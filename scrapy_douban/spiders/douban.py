import scrapy
from scrapy import Selector, Request

from scrapy_douban.items import MovieItem

"""
    该方法可以获取pagination按钮进行多个页面的爬取，但是存在问题。第一页会重复爬取
一遍。原因是页面切换第一页之外的页面后，第一页的索引Url发生了改变。
    调整下方start_urls的链接并不能解决问题，原因不明。
"""


class DoubanSpider(scrapy.Spider):
    name = 'douban'
    allowed_domains = ['movie.douban.com']
    start_urls = ['https://movie.douban.com/top250/']

    def parse(self, response, **kwargs):
        sel = Selector(response)
        list_items = sel.css('#content > div > div.article > ol > li')
        for list_item in list_items:
            movie_item = MovieItem()
            movie_item['title'] = list_item.css('span.title::text').extract_first()
            movie_item['rank'] = list_item.css('span.rating_num::text').extract_first()
            movie_item['subject'] = list_item.css('span.inq::text').extract_first()
            yield movie_item

        hrefs_list = sel.css('#content > div > div.article > div.paginator > a::attr(href)')
        for href in hrefs_list:
            url = response.urljoin(href.extract())
            yield Request(url=url)
