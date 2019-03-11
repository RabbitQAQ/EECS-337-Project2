# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Recipe(scrapy.Item):
    # recipe name, string
    recipeName = scrapy.Field()
    # recipe ingredient list, list of raw ingredient data
    rawIngredientList = scrapy.Field()
    # recipe direction list, list of raw direction data
    rawDirectionList = scrapy.Field()
    # ingredient list after processing, supposed to be a list of Ingredient (defined below)
    ingredients = scrapy.Field()
    # steps that each consist of ingredients, tools, methods, and times; list of Step (defined below)
    steps = scrapy.Field()

    toChinese = scrapy.Field()
    toItalian = scrapy.Field()
    toVegetarian = scrapy.Field()
    toVegan = scrapy.Field()
    toHealthy = scrapy.Field()
    fromHealthy = scrapy.Field()
    fromVegetarian = scrapy.Field()

class Ingredient(scrapy.Item):
    name = scrapy.Field()
    quantityAndMeasurement = scrapy.Field()
    descriptor = scrapy.Field()
    preparation = scrapy.Field()
    method = scrapy.Field()
    tool = scrapy.Field()

class Step(scrapy.Item):
    # ingredient used in this recipe, no need to be a Ingredient Object, just list of string(or a single string) is fine
    ingredient = scrapy.Field()
    # tools used in this recipe, a list of string
    tools = scrapy.Field()
    # methods used in this recipe, a list of string
    methods = scrapy.Field()
    # time for this step, a string
    stepTime = scrapy.Field()

