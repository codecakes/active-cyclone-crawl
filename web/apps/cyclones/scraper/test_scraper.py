"""Scraper unit tests."""

import datetime as dt
import os
from unittest import mock

from apps.cyclones.scraper import scraper
from django.test import TestCase

CUR_DIR = os.path.abspath(os.path.dirname(__file__))
HTML_FILE = os.path.join(CUR_DIR, "data.html")
MULTIPLE_BASINS_HTML_FILE = os.path.join(CUR_DIR, "basin_storms.html")

TEXT = [
    "TEST1",
    "TEST2",
    "TEST3",
    "TEST4",
    "TEST5",
    "TEST6",
    "TEST7",
    "TEST8",
]
HEADERS = ("c1", "c2")

FORECAST_TRACK = [
    {
        "forecast_hr": "0",
        "lat": "24.5",
        "lng": "275.8",
        "intensity": "60",
    },
    {
        "forecast_hr": "12",
        "lat": "26.4",
        "lng": "276.1",
        "intensity": "65",
    },
]
HISTORY_TRACK = [
    {
        "synoptic_time": "2020-11-11 12:00",
        "lat": "25.8",
        "lng": "-83.8",
        "intensity": "65",
    },
    {
        "synoptic_time": "2020-11-11 06:00",
        "lat": "24.5",
        "lng": "-84.2",
        "intensity": "60",
    },
]


def string_slice_generator(text):
    for line in text:
        yield line


class MockPatcherTestCase(TestCase):
    def _mock_patch_cleanup(
        self, mock_object: object, module: str, **kwargs
    ) -> mock.Mock:
        """DRY mock patcher with cleanup."""
        patcher = mock.patch.object(mock_object, module, autospec=True, **kwargs)
        mock_obj = patcher.start()
        self.addCleanup(patcher.stop)
        return mock_obj


class ScraperSlicedTblTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.TEXT = TEXT
        cls.HEADERS = HEADERS

    def setUp(self):
        self.stripped_string = string_slice_generator(ScraperSlicedTblTest.TEXT)
        self.start = 0
        self.steps = 2
        self.iterable_length = 4
        self.header = ScraperSlicedTblTest.HEADERS

    def testTbltoSlicedDicts(self):
        result = list(
            scraper.tbl_to_sliced_dicts(
                self.stripped_string,
                self.start,
                self.steps,
                self.iterable_length,
                self.header,
            )
        )
        expected = [
            {
                "c1": "TEST1",
                "c2": "TEST2",
            },
            {
                "c1": "TEST3",
                "c2": "TEST4",
            },
            {
                "c1": "TEST5",
                "c2": "TEST6",
            },
            {
                "c1": "TEST7",
                "c2": "TEST8",
            },
        ]
        self.assertEqual(
            expected, result, "Should be {} but is {}".format(expected, result)
        )


class ScrapeSingleDataTest(MockPatcherTestCase):
    def setUp(self):
        with open(HTML_FILE, encoding="utf-8") as html_f:
            html_body = html_f.read()
            self.mock_scraperwiki = self._mock_patch_cleanup(scraper, "scraperwiki")
            self.mock_scraperwiki.scrape.side_effect = lambda _: html_body
        self.mock_tag = mock.MagicMock(name="bs4_tag")
        self.img_dct = {"src": "some_img_src"}
        self.mock_tag.__getitem__.side_effect = self.img_dct.__getitem__
        self.href_dct = {"href": "some_href"}
        self.mock_tag.parent.__getitem__.side_effect = self.href_dct.__getitem__
        self.mock_tag.parent.parent.parent.parent.h3.get_text.return_value = (
            "REGION"
        )
        self.mock_tag.parent.get_text.return_value = "AL292020 - Tropical Storm ETA\n \n"
        self.forecast_track = FORECAST_TRACK
        self.history_track = HISTORY_TRACK

    def _helper_assert_test_scrape_data(self, result):
        self.assertIsInstance(result, dict)
        self.assertEqual(
            result["img_src"], "https://rammb-data.cira.colostate.edu/some_img_src"
        )
        self.assertIsInstance(
            result["forecast_time"],
            dt.datetime,
            "Should be datetime format buit is {}".format(result["forecast_time"]),
        )
        self.assertEqual(
            result["forecast_track"],
            self.forecast_track,
            "Should be {} got {}".format(self.forecast_track, result["forecast_track"]),
        )
        self.assertEqual(
            result["history_track"],
            self.history_track,
            "Should be {} got {}".format(self.history_track, result["history_track"]),
        )

    def test_scrape_data(self):
        scraper.scrape_data(self.mock_tag, self._helper_assert_test_scrape_data)
        self.mock_tag.__getitem__.assert_called_once_with("src")
        self.mock_tag.parent.parent.parent.parent.h3.get_text.assert_called_once()
        self.mock_tag.parent.__getitem__.assert_called_once_with("href")
        self.mock_scraperwiki.scrape.assert_called_once()


class MockThreads(mock.MagicMock):
    """A mock for Thread class in ScrapeDataHomePageTest."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._instance = None
        self._mock_thread(*args, **kwargs)

    def _mock_thread(self, instance: object, target=None, args=None):
        self._instance = instance
        instance._thread_calls += 1
        if target and args and len(args) == 2 and (tag := args[0]):
            instance._thread_tags += [tag]

    def start(self):
        if self._instance:
            self._instance._start_thread_calls += 1
        return mock.MagicMock()


class ScrapeDataHomePageTest(MockPatcherTestCase):
    def setUp(self):
        with open(MULTIPLE_BASINS_HTML_FILE, encoding="utf-8") as html_f:
            html_body = html_f.read()
            self.mock_scraperwiki = self._mock_patch_cleanup(scraper, "scraperwiki")
            self.mock_scraperwiki.scrape.side_effect = lambda _: html_body
        self.mock_queue = self._mock_patch_cleanup(scraper, "queue")
        self.mock_qthread_instance = mock.MagicMock
        self.mock_queue.Queue = mock.MagicMock(side_effect=self.mock_qthread_instance)

        self.mock_threading = self._mock_patch_cleanup(scraper, "threading")
        self._thread_tags = []
        self._thread_calls = 0
        self._start_thread_calls = 0
        self.mock_threading.Thread.side_effect = lambda target, args: MockThreads(
            self, target=target, args=args
        )

    def tearDown(self) -> None:
        self._thread_tags.clear()
        self._thread_calls = 0
        self._start_thread_calls = 0

    def test_scrape_data_regional_multiple_cyclones(self):
        scraper.scrape_page(lambda _: _)
        expected_qthread_put_calls = 3
        expected_thread_calls = 4
        expected_thread_start_calls = 4
        expected_thread_tags_len = 3
        expected = [
            ('Atlantic', 'Tropical Storm ETA', 'AL292020'),
            ('Atlantic', 'Tropical Storm THETA', 'AL302020'),
            ('Atlantic', 'INVEST', 'AL982020'),
        ]
        self.mock_scraperwiki.scrape.assert_called_once()
        self.mock_queue.Queue.assert_called_once_with(maxsize=20)
        self.assertEqual(
            expected_thread_calls,
            self._thread_calls,
            "Expected %d but got %d" % (expected_thread_calls, self._thread_calls),
        )
        self.assertEqual(
            expected_thread_start_calls,
            self._start_thread_calls,
            "Expected %d but got %d"
            % (expected_thread_start_calls, self._start_thread_calls),
        )
        thread_tags_len = len(self._thread_tags)
        self.assertEqual(
            expected_thread_tags_len,
            thread_tags_len,
            "Expected %d but got %d" % (expected_thread_tags_len, thread_tags_len),
        )
        result = [
            (region, heading, name)
            for _, heading, region, name, _ in map(
                scraper.scrape_tag, self._thread_tags
            )
        ]
        self.assertListEqual(expected, result, "Expected {} Got {}".format(
            expected, result
        ))
