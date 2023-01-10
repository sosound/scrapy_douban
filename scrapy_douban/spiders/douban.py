import scrapy
from scrapy import Selector, Request

from scrapy_douban.items import MovieItem

"""
    该方法可以获取pagination组件进行翻页从而爬取多个页面。存在的问题是必须
限定爬取页面的数量，当然，可以设置大于实际存在的数量。
"""


class DoubanSpider(scrapy.Spider):
    name = 'douban'
    allowed_domains = ['movie.douban.com']
    start_urls = ['https://movie.douban.com/top250/']

    def start_requests(self):
        for page in range(3):
            yield Request(url=f'https://movie.douban.com/top250?start={page*25}&filter=')

    def parse(self, response, **kwargs):
        sel = Selector(response)
        list_items = sel.css('#content > div > div.article > ol > li')
        for list_item in list_items:
            detail_url = list_item.css('div.info > div.hd > a::attr(href)').extract_first()
            movie_item = MovieItem()
            movie_item['title'] = list_item.css('span.title::text').extract_first()
            movie_item['rank'] = list_item.css('span.rating_num::text').extract_first()
            movie_item['subject'] = list_item.css('span.inq::text').extract_first()
            yield Request(
                url=detail_url, callback=self.parse_detail,
                cb_kwargs={'item': movie_item}
            )

    def parse_detail(self, response, **kwargs):
        sel = Selector(response)
        movie_item = kwargs['item']
        movie_item['duration'] = sel.css('span[property="v:runtime"]::attr(content)').extract()
        movie_item['intro'] = sel.css('span[property="v:summary"]::text').extract_first()
        yield movie_item
