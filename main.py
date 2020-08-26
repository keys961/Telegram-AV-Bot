import time
import telepot
import yaml
from enum import Enum, unique
from telepot.loop import MessageLoop
from telepot.delegate import pave_event_space, per_chat_id, create_open
from telepot.namedtuple import ReplyKeyboardMarkup


# TODO: Implement the av recommendation
class WinneAVSearcher(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(WinneAVSearcher, self).__init__(*args, **kwargs)
        self.state = AVSearcherState.INIT

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        print(content_type, chat_type, chat_id)
        if content_type == 'text':
            if self.state == AVSearcherState.INIT:
                if msg['text'] == '/recommend':
                    self.handle_recommend(msg, chat_id)
                elif msg['text'] == '/category':
                    self.handle_category_recommend(msg, chat_id)
                elif msg['text'] == '/search':
                    self.handle_search(msg, chat_id)
            elif self.state == AVSearcherState.CATEGORY:
                self.category_recommend_callback(msg, chat_id)
            elif self.state == AVSearcherState.SEARCH:
                self.search_callback(msg, chat_id)
            else:
                bot.sendMessage(chat_id, "Fuck you! Fuck you! Fuck you!")
        else:
            bot.sendMessage(chat_id, "Fuck you! Fuck you! Fuck you!")

    def handle_recommend(self, msg, chat_id):
        bot.sendMessage(chat_id, 'fuck you asshole')

    def handle_category_recommend(self, msg, chat_id):
        self.state = AVSearcherState.CATEGORY
        keyboard = ReplyKeyboardMarkup(keyboard=[['Porn Star'], ['JAV'], ['Teen'], ['Anal']], one_time_keyboard=True)
        bot.sendMessage(chat_id, 'Please pick an AV category you love:',
                        reply_markup=keyboard)

    def category_recommend_callback(self, msg, chat_id):
        self.state = AVSearcherState.INIT
        bot.sendMessage(chat_id, text="XXX")

    def handle_search(self, msg, chat_id):
        self.state = AVSearcherState.SEARCH
        bot.sendMessage(chat_id, text="Please input the keyword of AV you want to search:")

    def search_callback(self, msg, chat_id):
        self.state = AVSearcherState.INIT
        bot.sendMessage(chat_id, text="Fuck you")


@unique
class AVSearcherState(Enum):
    INIT = 0,
    CATEGORY = 1,
    SEARCH = 2


with open("./config.yml") as f:
    data = f.read()
    config = yaml.full_load(data)
if config['proxy'] is not None:
    telepot.api.set_proxy(config['proxy'])
bot = telepot.DelegatorBot(config['token'], [pave_event_space()(per_chat_id(), create_open, WinneAVSearcher, timeout=20)])


def main():
    MessageLoop(bot).run_as_thread()


if __name__ == "__main__":
    main()
    print('Listening ...')
    while 1:
        time.sleep(10)
