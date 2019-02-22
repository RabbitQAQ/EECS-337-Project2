from scrapy import Spider

from EECS337Project2.items import Recipe


class RecipesSpider(Spider):
    name = 'recipes_spider'
    start_urls = ["https://www.allrecipes.com/recipe/269944/shrimp-and-smoked-sausage-jambalaya/",
        "https://www.allrecipes.com/recipe/269941/tex-mex-smoked-sausage-baked-beans/"]

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
