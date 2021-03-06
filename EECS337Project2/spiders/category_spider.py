from scrapy import Spider
import scrapy

baseUrlDict = {
    "vegetarian": "https://www.allrecipes.com/recipes/87/everyday-cooking/vegetarian/?page=",
    "healthy": "https://www.allrecipes.com/recipes/84/healthy-recipes/?page=",
    "italian": "https://www.allrecipes.com/recipes/723/world-cuisine/european/italian/?page=",
    "vegan": "https://www.allrecipes.com/recipes/1227/everyday-cooking/vegan/?page="
}
targetCategory = "italian"

class CategorySpider(Spider):
    pageCount = 1
    maxCount = 25
    isFirstTime = True

    name = 'category_spider'
    start_urls = [baseUrlDict[targetCategory] + str(pageCount)]

    def parse(self, response):
        # clean the file
        if self.isFirstTime:
            open("data/" + targetCategory + "_urls_1000.txt", "w+").close()
            self.isFirstTime = False
        if (self.pageCount > self.maxCount):
            return
        recipesLinkList = response.xpath('//article[@class="fixed-recipe-card"]/div[@class="grid-card-image-container"]/a[contains(@href, "www.allrecipes.com/recipe")]/@href').extract()
        # write the file
        with open("data/" + targetCategory + "_urls_1000.txt", "a") as file:
            for i in recipesLinkList:
                file.write(i + "\n")
        self.pageCount += 1
        yield scrapy.Request(baseUrlDict[targetCategory] + str(self.pageCount))