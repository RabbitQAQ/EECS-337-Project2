from scrapy.cmdline import execute


if __name__ == '__main__':
    url = input("Please Input Recipe URL:")
    execute(("scrapy crawl recipes_spider -a url=" + url).split())
    #execute("scrapy crawl category_spider".split())