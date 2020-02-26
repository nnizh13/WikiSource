import scrapy
from WikiSource.items import Item
import csv
import random
import re


class ParseArticle(scrapy.Spider):
    name = 'parse_article'
    DOWNLOAD_DELAY = 0.1
    allowed_domains = ['wikisource.org']
    author_selectors = ['span#header_author_text *::text', 'span.fn a::text']
    title_selectors = ['span#header_title_text::text', 'span#header_title_text  a::text']
    year_selectors = ['div.gen_header_title::text']
    text_selectors = ['div.mw-parser-output p::text']
    urls = []
    regex = r"(?=(\d{4}))"

    def start_requests(self):
        with open('/Users/nikanizharadze/Desktop/WikiSource/WikiSource/WikiSource/total_work_urls.csv', "r") as f:
            reader = csv.reader(f, delimiter=",")
            data = list(reader)

        for i in range(1, len(data)):
            self.urls.append(data[i][0])
        for url in self.urls:
            if 'https://en.wikisource.org/wiki/Translation' not in url:
                yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        text_url = response.request.url
        header_text = " ".join(response.css('.gen_header_title *::text').getall())
        # header_urls = response.css('.gen_header_title a::attr("href")').getall()

        # Regex to catch everything between parenthesis.
        inside_parentheses = re.findall(r'\(([^)]+)', header_text)
        digits_inside_parentheses = []
        for item in inside_parentheses:
            year = ''
            for char in item:
                if char.isdigit() or char == '–':
                    year += char
                elif char == ' ' and year != '':
                    year += char
            if year != '':
                duplicate_spaces_removed = re.sub(' +', ' ', year)
                digits_inside_parentheses.append(duplicate_spaces_removed)

        year_tags = []
        category_tags = " ".join(response.css('div#mw-normal-catlinks *::text').getall())
        for tag in category_tags.split():
            if tag.isdigit() and len(tag) >= 4:
                year_tags.append(tag)

        date = 0
        if len(inside_parentheses) == 1:
            if len(inside_parentheses[0]) == 4:
                date = inside_parentheses[0]
        elif len(year_tags) == 1:
            if len(year_tags[0]) == 4:
                date = year_tags[0]

        text = " ".join(response.css('div.mw-parser-output p::text').getall())
        # if year_tag == header_year or year_tag in header_year:
        #     item['year'] = year_tag
        # elif year_tag != -1:
        #     item['year'] = year_tag
        # elif year_tag == -1 and len(header_year) != 0:
        #     item['year'] = header_year
        # else:
        #     header_year = re.findall(r"(?=(\d{4}))", header_text)
        #     # If there are no 4 consecutive digits.
        #     if len(header_year) == 0:
        #         # Find 3 consecutive digits
        #         header_year = re.findall(r"(?=(\d{3}))", header_text)
        #     item['year'] = header_year

        # Author URL
        author_url = response.xpath(
            '//div[contains(@class, "gen_header_title")]//a[contains(@href, "/wiki/Author:")]/@href').getall()

        if date != 0:
            yield {
                'text_url': text_url,
                'year': date,
                'text': text,
                'author_url ': author_url
            }


    #     item = Item()
    #     # Get the whole header for a page.
    #     header = response.css('.gen_header_title *::text').getall()
    #     item['author_url'] = response.request.url
    #     item['author'] = header[0]
    #     item['author_dob'] = header[1]
    #     ul = response.css('div.mw-parser-output > ul> li').getall()
    #     link_tag = 'href="'
    #     title_tag = 'title="'
    #     for li in ul:
    #         if li.find(link_tag) != -1:
    #             # Get year of the text.
    #
    #             year = li[li.find('(')+1:li.find(')')]
    #             item['year'] = year
    #             if year is None or len(year) == 0 or year.isdigit() is False:
    #                 matches = re.findall(self.regex, li)
    #                 item['year'] = list(set(matches))
    #
    #             # Get title of the text.
    #             title_start_index = li.find(title_tag) + len(title_tag)
    #             title_end_index = li.find('"', title_start_index)
    #             title = li[title_start_index:title_end_index]
    #             item['title'] = title
    #
    #             # Get URL of article.
    #             url_start_index = li.find(link_tag)+len(link_tag)
    #             url_end_index = li.find('"', url_start_index)
    #             url = li[url_start_index:url_end_index]
    #             item['text_url'] = response.urljoin(url)
    #             yield response.follow(url=response.urljoin(url), callback=self.parse_text, meta={'item': item})
    #
    # def parse_text(self, response):
    #     item = response.meta['item']
    #     item['text'] = response.css('div.mw-parser-output p::text').getall()
    #
    #     title_content = response.css('div.gen_header_title *::text').getall()
    #     for word in title_content:
    #         if word.isdigit():
    #             if word not in item['year']:
    #                 item['year'].append(word)
    #     yield item
    #

        # header_to_string = ','.join(map(str, header))
        # # Find year if it is inside () parenthesis.
        # if header_to_string.find("(") != -1 and header_to_string.find(")") != -1:
        #     inside_parenthesis = header_to_string[header_to_string.find("(") + 1:header_to_string.find(")")]
        #     # Extract only digits within ()
        #     year = ''.join(filter(lambda x: x.isdigit() or x == '-', inside_parenthesis))
        #     item['year'] = year
        # else:
        #     year = ''
        #     for char in header_to_string:
        #         if char.isdigit() or char == '-':
        #             year += char
        #         elif len(year) > 0:
        #             break
        #     item['year'] = year
        # if item['year'] is None or len(item.get('year')) == 0:
        #     with open("/Users/nikanizharadze/Desktop/WikiSource/WikiSource/WikiSource/no_authors.csv", "a") as f:
        #         url = response.request.url
        #         f.write(f"No year for :{url}\n")
        #
        # # Extract authors from header.
        # for selector in self.author_selectors:
        #     if len(response.css(selector).getall()) != 0:
        #         item['author'] = response.css(selector).getall()
        #         break
        # if item.get('author') is None or len(item.get('author')) == 0:
        #     with open("/Users/nikanizharadze/Desktop/WikiSource/WikiSource/WikiSource/no_authors.csv", "a") as f:
        #         url = response.request.url
        #         f.write(f"No author for :{url}\n")
        #
        # # Extract title from header.
        # for selector in self.title_selectors:
        #     if len(response.css(selector).getall()) != 0:
        #         item['title'] = response.css(selector).getall()
        #         break
        # if item.get('title') is None or len(item.get('title')) == 0:
        #     with open("/Users/nikanizharadze/Desktop/WikiSource/WikiSource/WikiSource/no_authors.csv", "a") as f:
        #         url = response.request.url
        #         f.write(f"No title for :{url}\n")
        #
        # # Extract text from URL.
        # for selector in self.text_selectors:
        #     if len(response.css(selector).getall()) != 0:
        #         item['text'] = response.css(selector).getall()
        #         break
        # if item.get('text') is None or len(item.get('text')) == 0:
        #     with open("/Users/nikanizharadze/Desktop/WikiSource/WikiSource/WikiSource/no_authors.csv", "a") as f:
        #         url = response.request.url
        #         f.write(f"No text for :{url}\n")
        # yield item

        # header = response.css('div.gen_header_title ::text').getall()
        # for tag in header:
        #     year = tag[tag.find("(") + 1:tag.find(")")]
        #     if year is not None:
        #         item['year'] = year
        #         break
        # if item['year'] is None or len(item.get('year')) == 0:
        #     with open("/Users/nikanizharadze/Desktop/WikiSource/WikiSource/WikiSource/no_authors.csv", "a") as f:
        #         url = response.request.url
        #         f.write(f"No year for :{url}\n")
        # # for tag in header:
        #
        # # for selector in self.year_selectors:
        # #     if len(response.css(selector).getall()) != 0:
        # #         item['year'] = response.css(selector).getall()
        # #         break
        # # if item.get('year') is None or len(item.get('year')) == 0:
        # #     with open("/Users/nikanizharadze/Desktop/WikiSource/WikiSource/WikiSource/no_authors.csv", "a") as f:
        # #         url = response.request.url
        # #         f.write(f"No year for :{url}\n")
        #

