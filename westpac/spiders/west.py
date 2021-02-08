import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from westpac.items import Article


class WestSpider(scrapy.Spider):
    name = 'west'
    start_urls = ['https://www.westpac.com.au/news/']

    def parse(self, response):
        with open('response.html', 'wb') as f:
            f.write(response.body)

        links = response.xpath('//h2[@class="article-title"]/a/@href').getall()
        yield from response.follow_all(links, self.parse_for_new)

    def parse_for_new(self, response):
        yield response.follow(response.url, self.parse_article, dont_filter=True)
        new_articles = response.xpath('//h3[@class="article-title"]/a/@href').getall()
        yield from response.follow_all(new_articles, self.parse_for_new)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get().strip()
        date = " ".join(response.xpath('//div[@class="time-detail"]/span/text()').get().strip().split()[-3:])
        date = datetime.strptime(date, '%B %d %Y')
        date = date.strftime('%Y/%m/%d')
        content = response.xpath('//div[@class="bodycopy"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()
        author = response.xpath('//div[@class="article-author-name "]/a/text()').get()
        tags = ",".join(response.xpath('//div[@class="tag-list"]//li/a/text()').getall())

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)
        item.add_value('author', author)
        item.add_value('tags', tags)

        return item.load_item()


