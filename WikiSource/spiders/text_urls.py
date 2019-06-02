import scrapy
from WikiSource.items import WorkUrl


class TextUrls(scrapy.Spider):
    name = 'get_text_urls'
    start_urls = ['https://en.wikisource.org/wiki/Category:Works_by_era',
                  'https://en.wikisource.org/wiki/Category:Works_by_type',
                  'https://en.wikisource.org/wiki/Category:Works_by_genre',
                  'https://en.wikisource.org/wiki/Category:Works_by_subject']
    works_url = []

    def parse(self, response):
        """Send requests for every Work's subcategories."""
        for category_url in response.css('a.CategoryTreeLabelCategory::attr("href")').getall():
            yield response.follow(response.urljoin(category_url), callback=self.parse_works)

    def parse_works(self, response):
        """Parse responses for each request."""
        works = response.css('div#mw-pages > div.mw-content-ltr > '
                             ' div.mw-category > div.mw-category-group ul li a::attr("href")').getall()
        for work in works:
            work_url = response.urljoin(work)
            if work_url not in self.works_url:
                self.works_url.append(work_url)
                w_url = WorkUrl()
                w_url['url'] = work_url
                yield w_url
        # Crawls next page if it exists
        try:
            next_page = response.css('div#mw-pages > a::attr("href")').getall()[1]
            if next_page is not None:
                next_page_url = response.urljoin(next_page)
                yield scrapy.Request(response.urljoin(next_page_url), callback=self.parse_works)
        except IndexError:
            pass
        # Crawls subcategories
        subcategories = response.css('div.CategoryTreeItem a::attr("href")').getall()
        for cat in subcategories:
            yield scrapy.Request(response.urljoin(cat), callback=self.parse_works)

    # def save_as_csv(self, works, path):
    #     """write the list to csv file"""
    #     with open(path, "w") as outfile:
    #         for entries in works:
    #             outfile.write(entries)
    #             outfile.write("\n")
