import time
import urllib.parse

import telepot
import yaml
from av import AVSearcher, URL_SEARCH
from enum import Enum, unique
from telepot.loop import MessageLoop
from telepot.delegate import pave_event_space, per_chat_id, create_open
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from ratelimit import limits, sleep_and_retry

bot = telepot.DelegatorBot
config = None


def get_protocol(proxy):
    return str(proxy)[:str(proxy).index("://")]


def get_proxies_dict(proxy):
    protocol = get_protocol(proxy)
    ret = {}
    if str(protocol).index("http") >= 0:
        ret['http'] = proxy
        ret['https'] = proxy
    else:
        ret[protocol] = proxy
    return ret


def output_video(chat_id, videos):
    if len(videos) > 0:
        cnt = 1
        for video in videos:
            # bot.sendVideo(chat_id, video.get_embedded_url())
            msg = str(cnt) + ". " + video.get_response()
            cnt += 1
            bot.sendMessage(chat_id, msg)
    else:
        bot.sendMessage(chat_id, "Nothing found.")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Next", callback_data="N"), InlineKeyboardButton(text="Finish", callback_data="F")]
    ])
    bot.sendMessage(chat_id, "What's next?", reply_markup=keyboard)


class WinneAVSearcher(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(WinneAVSearcher, self).__init__(*args, True, **kwargs)
        if config['proxy'] is not None:
            self.av_searcher = AVSearcher(get_proxies_dict(config['proxy']))
        else:
            self.av_searcher = AVSearcher()
        self.fetched_categories = self.av_searcher.fetch_categories()
        self.state = AVSearcherState.INIT
        self.page = 0
        self.param = None

    @limits(calls=10, period=1)
    @sleep_and_retry
    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        print(content_type, chat_type, chat_id)
        if content_type == 'text':
            if msg['text'] == '/recommend':
                self._reset_state()
                self._handle_recommend(chat_id)
            elif msg['text'] == '/category':
                self._reset_state()
                self._handle_category_recommend(chat_id)
            elif msg['text'] == '/search':
                self._reset_state()
                self._handle_search(chat_id)
            else:
                if self.state == AVSearcherState.INIT:
                    bot.sendMessage(chat_id, "Fuck you! Fuck you! Fuck you!")
                    self._reset_state()
                elif self.state == AVSearcherState.SEARCH:
                    self._do_search(msg, chat_id)
                else:
                    bot.sendMessage(chat_id, "Fuck you! Fuck you! Fuck you!")
                    self._reset_state()
        else:
            bot.sendMessage(chat_id, "Fuck you! Fuck you! Fuck you!")
            self._reset_state()

    @limits(calls=10, period=1)
    @sleep_and_retry
    def on_callback_query(self, msg):
        query_id, from_id, callback_data = telepot.glance(msg, flavor='callback_query')
        if self.state == AVSearcherState.RECOMMEND:
            if callback_data == 'N':
                self.page += 1
                videos = self.av_searcher.fetch_recommendation(self.page)
                output_video(from_id, videos)
            elif callback_data == 'F':
                self._reset_state()
                bot.sendMessage(from_id, "Thank you sir ♂")
        elif self.state == AVSearcherState.CATEGORY_RECOMMEND:
            if callback_data == 'N':
                self.page += 1
                videos = self.av_searcher.fetch_category_recommendation(self.param, self.page)
                output_video(from_id, videos)
            elif callback_data == 'F':
                self._reset_state()
                bot.sendMessage(from_id, "Thank you sir ♂")
            else:
                ch_id = self.fetched_categories[callback_data]
                self.page = 0
                self.param = ch_id
                videos = self.av_searcher.fetch_category_recommendation(self.param, self.page)
                output_video(from_id, videos)
        elif self.state == AVSearcherState.SEARCH:
            if callback_data == 'N':
                self.page += 1
                videos = self.av_searcher.fetch(self.param, self.page)
                output_video(from_id, videos)
            elif callback_data == 'F':
                self._reset_state()
                bot.sendMessage(from_id, "Thank you sir ♂")
        else:
            bot.sendMessage(from_id, "Fuck you! Fuck you! Fuck you!")

    def _handle_recommend(self, chat_id):
        self.state = AVSearcherState.RECOMMEND
        videos = self.av_searcher.fetch_recommendation()
        output_video(chat_id, videos)

    def _handle_category_recommend(self, chat_id):
        self.state = AVSearcherState.CATEGORY_RECOMMEND
        button_list = []
        row = []
        for category in self.fetched_categories.keys():
            row.append(InlineKeyboardButton(text=category, callback_data=category))
            if len(row) == 2:
                button_list.append(row)
                row = []
        if len(row) > 0:
            button_list.append(row)
        keyboard = InlineKeyboardMarkup(inline_keyboard=button_list)
        bot.sendMessage(chat_id, 'Please pick an AV category you love:',
                        reply_markup=keyboard)

    def _handle_search(self, chat_id):
        self.state = AVSearcherState.SEARCH
        bot.sendMessage(chat_id, text="Please input the keyword of AV you want to search:")

    def _do_search(self, msg, chat_id):
        self.state = AVSearcherState.SEARCH
        self.page = 0
        self.param = msg['text']
        videos = self.av_searcher.fetch(self.param, self.page)
        output_video(chat_id, videos)

    def _reset_state(self):
        self.state = AVSearcherState.INIT
        self.page = 0
        self.param = None


@unique
class AVSearcherState(Enum):
    INIT = 0,
    RECOMMEND = 1,
    CATEGORY_RECOMMEND = 2,
    SEARCH = 3


def main():
    global config, bot
    with open("./config.yml") as f:
        data = f.read()
        config = yaml.full_load(data)
    if config['proxy'] is not None:
        telepot.api.set_proxy(config['proxy'])
    bot = telepot.DelegatorBot(config['token'],
                               [pave_event_space()(per_chat_id(), create_open, WinneAVSearcher, timeout=120)])
    MessageLoop(bot).run_as_thread()
    print('Listening ...')
    while 1:
        time.sleep(20)


if __name__ == "__main__":
    main()
