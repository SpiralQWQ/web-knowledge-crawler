"""Coursera / edX / Khan Academy 课程站内搜索。"""
from urllib.parse import quote
from .playwright_search import PlaywrightSearcher
from .base import register


@register
class CourseraSearcher(PlaywrightSearcher):
    name = "coursera"
    domain = "coursera.org"
    search_url_template = "https://www.coursera.org/search?query={term}"
    item_selector = ".ProductCard"
    title_selector = ".ProductCard-title a"
    url_selector = ".ProductCard-title a"
    summary_selector = ".ProductCard-body"
    wait_timeout = 15000


@register
class EdxSearcher(PlaywrightSearcher):
    name = "edx"
    domain = "edx.org"
    search_url_template = "https://www.edx.org/search?q={term}"
    item_selector = ".course-item"
    title_selector = ".course-title a"
    url_selector = ".course-title a"
    summary_selector = ".course-description"
    wait_timeout = 15000


@register
class KhanAcademySearcher(PlaywrightSearcher):
    name = "khanacademy"
    domain = "khanacademy.org"
    search_url_template = "https://www.khanacademy.org/api/internal/search?q={term}&locale=zh-CN"
    item_selector = ".search-result-item"
    title_selector = ".result-title a"
    url_selector = ".result-title a"
    summary_selector = ".result-desc"
    wait_timeout = 10000
