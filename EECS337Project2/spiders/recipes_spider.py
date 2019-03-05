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
    urlCount = 0
    if RUN_MODE == 1:
        with open("data/" + targetCategory + "_urls.txt", "r") as file:
            urls = [line for line in file.read().split("\n") if len(line.strip()) != 0]
            urlCount = len(urls)
            start_urls = urls

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
