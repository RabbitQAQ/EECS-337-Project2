# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

# Hard coded quantities, tools and actions
import re
import nltk

from nltk.tokenize import TweetTokenizer
from EECS337Project2.items import Ingredient

tools = []
methodToTools = {
    'chopped': 'knife',
    'cut': 'knife',
    'julienne': 'knife',
    'minced': 'knife',
    'diced': 'knife',
    'sliced': 'knife',
    'stir': 'spoon',
    'fold': 'spoon',
    'glazed': 'spoon',
    'drizzled': 'spoon',
    'heated': 'oven',
    'fry': 'pan',
    'baste': 'baster',
    'sift': 'colander',
    'cream': 'hand mixer',
    'grate': 'grater',
    'whisk': 'whisk',
    'marinate': 'bowl',
    'shred': 'food processor',
    'peeled': 'peeler',
}
quantity = {
    'tsp': 'teaspoon',
    'c': 'cup',
    'ml': 'milliliter',
    'tbsp': 'tablespoon',
    'pt': 'pint',
    'l': 'liter',
    'oz': 'ounce',
    'qt': 'quart',
    'g': 'gram',
    'fl oz': 'fluid ounce',
    'gal': 'gallon',
    'lb': 'pound',
    'package': 'package'
}

punctuation = ['(', ')', ',', '.', ';', '?']
easyToTaggedWrongWords = ['can']
acceptableAdjs = ['JJ']
acceptableVerbs = ['VB', 'VBD']
acceptableNouns = ['NN', 'NNP', 'NNS', 'IN']

# Tokenizer
twTokenizer = TweetTokenizer()

# Initial variables that may use in other pipelines
class InitPipeline(object):
    def process_item(self, item, spider):
        global tools
        global quantity
        global quantityRegex
        with open('data/tools.txt') as file:
            tools = file.read().split('\n')
        with open('data/quantity.txt') as file:
            for q in file.read().split('\n'):
                quantity[q] = q

        return item


# Pipelines that process raw ingredient data into structural object
class IngredientProcessPipeline(object):
    def process_item(self, item, spider):
        item['ingredients'] = []
        ingredientList = item['rawIngredientList']
        for ingredient in ingredientList:
            tmpIngredient = Ingredient()
            # name | quantity | measurement | descriptor | preparation
            posIngre = nltk.pos_tag(twTokenizer.tokenize(ingredient))
            currName = ''
            currQuent = ''
            currDescriptor = ''
            currPreparation = ''
            currTool = []
            currMethod = []
            # find quantity using stack
            stack = []
            bkpoint = 0
            comment = False
            for wordtag in posIngre:
                if wordtag[1] == 'CD':
                    stack.append(wordtag)
                    bkpoint += 1
                elif wordtag[1] == 'NN' or wordtag[1] == 'NNS' or wordtag[0] in easyToTaggedWrongWords:
                    if len(stack) != 0:
                        if wordtag[0] in quantity:
                            if not comment:
                                currQuent = currQuent + " ".join([w[0] for w in stack]) + ' ' + wordtag[0] + '| '
                                bkpoint += 1
                                stack = []
                                break
                            else:
                                currQuent = currQuent + stack.pop()[0] + ' ' + wordtag[0] + '| '
                                bkpoint += 1
                        else:
                            currQuent = currQuent + stack.pop()[0] + '| '
                            bkpoint += 1
                    else:
                        break
                elif wordtag[0] in punctuation:
                    comment = True
                    bkpoint += 1
                else:
                    break
            if len(stack) != 0:
                for wordtag in stack:
                    currQuent = currQuent + wordtag[0] + '| '
            currQuent = currQuent.strip()
            # find name / method
            print("fuck")
            hasPrep = False
            adjs = []
            for i in range(bkpoint, len(posIngre)):
                wordtag = posIngre[i]
                if wordtag[0] in punctuation:
                    bkpoint = i + 1
                    hasPrep = True
                    break
                if wordtag[1] in acceptableAdjs:
                    adjs.append(wordtag[0])
                if wordtag[1] in acceptableVerbs:
                    currMethod.append((' '.join(adjs) + ' ' + wordtag[0]).strip())
                    adjs = []
                if wordtag[1] in acceptableNouns:
                    currName += wordtag[0] + ' '
                    currDescriptor += ' '.join(adjs) + ' '
                    adjs = []
            if currName == "" and len(adjs) != 0:
                currName = " ".join(adjs)
                adjs = []

            currName = currName.strip()
            currDescriptor = currDescriptor.strip()

            # find preparation
            if hasPrep:
                for i in range(bkpoint, len(posIngre)):
                    currPreparation += posIngre[i][0] + ' '

            # find tools
            for method in currMethod:
                for knownMethod in methodToTools.keys():
                    if method in knownMethod:
                        if methodToTools[knownMethod] not in currTool:
                            currTool.append(methodToTools[knownMethod])

            # build ingredient object
            tmpIngredient['name'] = currName
            tmpIngredient['quantityAndMeasurement'] = currQuent
            tmpIngredient['descriptor'] = currDescriptor
            tmpIngredient['preparation'] = currPreparation
            tmpIngredient['method'] = currMethod
            tmpIngredient['tool'] = currTool

            # add to item field
            item['ingredients'].append(tmpIngredient)

        return item

# Pipelines that process raw direction data into structural object
class DirectionProcessPipeline(object):
    def process_item(self, item, spider):
        directionList = item['rawDirectionList']
        for direction in directionList:
            pass
        return item
