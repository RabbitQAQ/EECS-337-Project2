from scrapy.cmdline import execute


if __name__ == '__main__':
    execute("scrapy crawl recipes_spider".split())
    #execute("scrapy crawl category_spider".split())