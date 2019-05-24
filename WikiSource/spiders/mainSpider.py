
import scrapy
from WikiSource.items import Entry
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider

#author Selector - (response.css('span#header_section_text::text').getall())
#book title Selector - (response.css('span#header_title_text a::text').getall()

class WikiSource(scrapy.Spider):
    name = 'wikisource'
    allowed_domains = ["wikisource.com"]
    start_urls = ['https://en.wikisource.org/wiki/Author:John_Abercromby']
    author_selectors = ['','span#header_author_text *::text','span#header_section_text::text']
    title_selectors = ['span#header_title_text a::text']
    year_selectors = []
    text_selectors = ['div.prp-pages-output > p::text']
    
    def parse(self,response):
        #entry['author'] = response.css('td.gen_header_title > b::text').get()
        text_urls = response.css('div.mw-parser-output > ul> li >a::attr("href")').getall()
        print(text_urls)
        for url in text_urls:
            print(response.urljoin(url))
            yield response.follow(response.urljoin(url), callback=self.get_texts)

    def get_texts(self, response):
        pass
        
        
       