
import scrapy
from WikiSource.items import Entry
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider
import csv

class Linkextractor(scrapy.Spider):
    name = 'linkextractor'
    start_urls = ["https://en.wikisource.org/wiki/Category:Authors_by_era"]
    authors_url = []
    my_dict = {}

    def parse(self,response):
        """Send requests for every category in Authors by Era"""
        for category_url in response.css('a.CategoryTreeLabelCategory::attr("href")').extract():
            yield response.follow(response.urljoin(category_url), callback=self.parse_authors)

    def parse_authors(self, response):
        """ """
        authors = response.css('div#mw-pages > div.mw-content-ltr >  div.mw-category > div.mw-category-group ul li a::attr("href")').getall()  
        for author in authors:
            author_url = response.urljoin(author)
            self.authors_url.append(author_url)
            yield response.follow(author_url,callback=self.get_works)
        next_page = response.css('div#mw-pages > a::attr("href")').getall()[1]
        if(next_page != None):
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(response.urljoin(next_page_url), callback=self.parse_authors)
        #self.save_as_csv(self.authors_url)

    def get_works(self,response):
        author = response.request.url
        works = response.css('div.mw-parser-output > ul> li >a::attr("href")').getall()
        for i in range(len(works)):
            works[i] = response.urljoin(works[i])
        self.my_dict[author] = works
        with open('test.csv', 'w') as f:
            for key in self.my_dict.keys():
                f.write("%s,%s\n"%(key,self.my_dict[key]))

    def save_as_csv(self,authors):
        """write the list to csv file"""
        with open("data/authors.csv", "w") as outfile:
            for entries in authors:
                outfile.write(entries)
                outfile.write("\n")
