import requests
import urllib.parse

URL_CHANNEL_ID = "https://api.avgle.com/v1/categories"
URL_RECOMMENDATION = "https://api.avgle.com/v1/videos/{}?limit={}"
URL_CATEGORY_RECOMMENDATION = "https://api.avgle.com/v1/videos/{}?c={}&limit={}"
URL_SEARCH = "https://api.avgle.com/v1/search/{}/{}?limit={}"
RESPONSE_MODEL = '''
<figure class="video_container">
  <iframe src="{}" frameborder="0" allowfullscreen="true"> </iframe>
</figure>
'''
REQUEST_HEADER = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0",
    "Connection": "keep-alive"
}


def _output_videos(resp):
    ret = []
    if resp['success']:
        videos = resp['response']['videos']
        for video in videos:
            ret.append(FetchedVideo(video))
    return ret


class AVSearcher:
    def __init__(self, proxies=None):
        self._proxies = proxies

    def fetch_categories(self):
        resp = requests.get(URL_CHANNEL_ID,
                                       headers=REQUEST_HEADER, proxies=self._proxies);
        channel_id_resp = resp.json()
        categories = {}
        if channel_id_resp['success']:
            for category in channel_id_resp['response']['categories']:
                categories[category['name']] = category['CHID']
        return categories

    def fetch_recommendation(self, page=0, limit=5):
        resp = requests.get(URL_RECOMMENDATION.format(page, limit),
                            headers=REQUEST_HEADER, proxies=self._proxies).json()
        return _output_videos(resp)

    def fetch_category_recommendation(self, ch_id, page=0, limit=5):
        resp = requests.get(URL_CATEGORY_RECOMMENDATION.format(page, ch_id, limit),
                            headers=REQUEST_HEADER, proxies=self._proxies).json()
        return _output_videos(resp)

    def fetch(self, keywords, page=0, limit=5):
        resp = requests.get(URL_SEARCH.format(urllib.parse.quote_plus(keywords), page, limit),
                            headers=REQUEST_HEADER, proxies=self._proxies).json()
        return _output_videos(resp)


class FetchedVideo:
    def __init__(self, video_resp):
        self._title = video_resp['title']
        self._url = video_resp['video_url']
        self._embedded_url = video_resp['embedded_url']

    def get_title(self):
        return self._title

    def get_url(self):
        return self._url

    def get_embedded_url(self):
        return self._embedded_url

    def get_response(self):
        return RESPONSE_MODEL.format(self._embedded_url)

    def __repr__(self):
        return self._title

    def __str__(self):
        return self._title
