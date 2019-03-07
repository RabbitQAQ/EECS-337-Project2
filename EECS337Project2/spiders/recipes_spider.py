import scrapy
from scrapy import Spider

from EECS337Project2.items import Recipe

# RUN_MODE 0: test mode, add urls manually
# RUN_MODE 1: statistic mode, read urls from text, count the ingredients number
RUN_MODE = 1
targetCategory = "vegetarian"

class RecipesSpider(Spider):
    name = 'recipes_spider'
    start_urls = ["https://www.allrecipes.com/recipe/73634/colleens-slow-cooker-jambalaya/?internalSource=previously%20viewed&referringContentType=Homepage&clickId=cardslot%208"]
    startCount = 527
    maxUrlCount = 0
    urlCount = 0
    indexDict = {"vegetarian": 0, "healthy": 0, "italian": 0, "vegan": 0}
    categoryList = ["vegetarian", "healthy", "italian", "vegan"]
    currCategory = categoryList[0]
    if RUN_MODE == 1:
        start_urls = []
        for category in categoryList:
            with open("data/" + category + "_urls_1000.txt", "r") as file:
                urls = [line for line in file.read().split("\n") if len(line.strip()) != 0]
                maxUrlCount += len(urls)
                indexDict[category] = len(urls)
                start_urls.extend(urls)
        start_urls = start_urls[startCount:]

    def parse(self, response):
        recipeName = response.xpath('//h1[@id="recipe-main-content"]/text()').extract()[0]
        rawIngredientList = response.xpath('//li[@class="checkList__line"]/label/span/text()').extract()
        rawDirectionList = response.xpath('//li[@class="step"]/span/text()').extract()
        for ingredient in rawIngredientList[:]:
            if ingredient == 'Add all ingredients to list':
                rawIngredientList.remove(ingredient)
        recipe = Recipe()
        recipe['recipeName'] = recipeName
        recipe['rawIngredientList'] = rawIngredientList
        recipe['rawDirectionList'] = rawDirectionList

        yield recipe
