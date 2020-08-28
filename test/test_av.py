import unittest
import avgle
from pprint import pprint

PROXIES = {
    'http': 'http://127.0.0.1:8889',
    'https': 'http://127.0.0.1:8889'
}


class TestAV(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestAV, self).__init__(*args, **kwargs)
        self.av_searcher = avgle.AVSearcher(PROXIES)

    def test_category(self):
        pprint(self.av_searcher.fetch_categories())

    def test_recommendation(self):
        pprint(self.av_searcher.fetch_recommendation())

    def test_category_recommendation(self):
        pprint(self.av_searcher.fetch_category_recommendation("1"))

    def test_search(self):
        pprint(self.av_searcher.fetch("三上悠亚"))


if __name__ == '__main__':
    unittest.main()