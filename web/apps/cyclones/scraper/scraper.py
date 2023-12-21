"""Scraper function for active cyclones."""

import functools
import queue
import re
import threading
from typing import Callable, Dict, Tuple, Generator

import requests
import scraperwiki
from bs4 import BeautifulSoup, SoupStrainer
from dateutil import parser as dateparser
from dateutil.tz import gettz
from django.conf import settings

URL = "https://rammb-data.cira.colostate.edu/tc_realtime/index.asp"
SITE_URI, _ = requests.urllib3.util.parse_url(URL).url.rsplit("/", 1)
HOST_URI = requests.urllib3.util.parse_url(SITE_URI).url
join_site_url = functools.partial(requests.compat.urljoin, HOST_URI)

# RegExp to seperate region from cyclone title for each cyclone title
RGX_TITLE_SEP = "[^\\w+]([\\\\n]*)"
TZINFOS = {"CST": gettz("America/Chicago")}

# Two header columns for cyclone data tables
FORECAST_HEADER = ("forecast_hr", "lat", "lng", "intensity")
HISTORY_HEADER = ("synoptic_time", "lat", "lng", "intensity")


def worker(qthread: queue.Queue):
    """Thread safe worker queue.

    Args:
        qthread: queue.Queue, thread safe FIFO queue.
    """
    while thread := qthread.get():
        settings.LOGGER.info(f"**Running thread** {thread}")
        qthread.task_done()


def scrape_page(fetch_result_cb: Callable):
    """Multi-threaded scraper.

    Args:
        fetch_result_cb(Callable): A callback task scheduler.
    """
    page = scraperwiki.scrape(URL)
    qthread = queue.Queue(maxsize=20)
    soup = BeautifulSoup(
        page,
        features="lxml",
        parse_only=SoupStrainer("div", attrs={"class": "basin_storms"}),
    )

    t = threading.Thread(target=worker, args=(qthread,))
    t.start()

    for tag in soup.select("div>ul>li>a>img"):
        t = threading.Thread(
            target=scrape_data,
            args=(
                tag,
                fetch_result_cb,
            ),
        )
        qthread.put(t)
        t.start()
    qthread.join()


def scrape_data(bs4_tag: BeautifulSoup, fetch_result_cb: Callable):
    """Scraper to parse cyclone page.

    Args:
        bs4_tag(BeautifulSoup): BeautifulSoup DOM tag.
        fetch_result_cb(Callable): An async celery callback to proces data.
    """
    forecast_tbl = None
    track_history_tbl = None
    forecast_time = None

    img_src, cyclone_heading, region, cyclone_name, link = scrape_tag(bs4_tag)
    cyclone_page = scraperwiki.scrape(link)

    data_res = BeautifulSoup(
        cyclone_page,
        features="lxml",
        parse_only=SoupStrainer("div", attrs={"class": "text_product_wrapper"}),
    )
    tables = data_res.select("table")
    try:
        if (forecast_heading := data_res.find("h4")) is not None:
            forecast_time, _ = dateparser.parse(
                forecast_heading.get_text(),
                fuzzy_with_tokens=True,
                tzinfos=TZINFOS,
            )
            forecast_time = forecast_time.replace(tzinfo=TZINFOS["CST"])
    except AttributeError as e:
        settings.LOGGER.error(f"ERRORed on link {link}")
        raise (e)

    if tables and len(tables) == 2:
        forecast_tbl, track_history_tbl = tables
    elif tables and forecast_heading:
        [forecast_tbl] = tables
    elif tables and not forecast_heading:
        [track_history_tbl] = tables

    forecast_data = (
        list(
            tbl_to_sliced_dicts(
                forecast_tbl.stripped_strings,
                4,
                4,
                len(forecast_tbl.find_all("tr")),
                FORECAST_HEADER,
            )
        )
        if forecast_tbl
        else None
    )
    history_data = (
        list(
            tbl_to_sliced_dicts(
                track_history_tbl.stripped_strings,
                4,
                4,
                len(track_history_tbl.find_all("tr")),
                HISTORY_HEADER,
            )
        )
        if track_history_tbl
        else None
    )
    fetch_result_cb(
        {
            "region": region,
            "img_src": img_src,
            "cyclone_name": f"{cyclone_heading}-{cyclone_name}",
            "link": link,
            "forecast_time": forecast_time,
            "forecast_track": forecast_data,
            "history_track": history_data,
        }
    )


def scrape_tag(bs4_tag: BeautifulSoup) -> Tuple[str]:
    """Parse scarped tag attributes.

        Args:
            bs4_tag(BeautifulSoup): BeautifulSoup DOM tag.
        Returns:
            Tuple of parsed attributes.
    """
    img_src = join_site_url(bs4_tag["src"])
    region = bs4_tag.parent.parent.parent.parent.h3.get_text().strip()
    cyclone_name, cyclone_heading = [w.strip() for w in bs4_tag.parent.get_text().strip().split('-')]
    link = requests.urllib3.util.Url(host=SITE_URI, path=bs4_tag.parent["href"]).url
    return img_src, cyclone_heading, region, cyclone_name, link


def tbl_to_sliced_dicts(
    string_generator: Generator,
    start: int,
    steps: int,
    iterable_length: int,
    header: Tuple[str],
) -> Generator[Dict[str, str], None, None]:
    """Iterate slices of dictionary of given sequence range.

    Args:
        string_generator(Generator): A generator to traverse sanitized strings.
        start(int): Starting index.
        steps(int): Sequences to skip.
        iterable_length(int): How many indices to traverse per slice.
        header(Tuple[str]): Table column headers.
    Returns:
        A list of dictionary results.
    """
    total_elements = steps * iterable_length
    res: list = []
    ctr = 0
    for line in string_generator:
        # print(f"line is {line}")
        if ctr == total_elements:
            break
        if ((ctr % steps) + start == start):
            if res:
                yield dict(zip(header, res))
                res.clear()
        if ctr >= start:
            res += [line]
        ctr += 1
        # print(f"start={start} steps={steps} ctr={ctr} res={res}")
    if res:
        yield dict(zip(header, res))
        res.clear()
    return
