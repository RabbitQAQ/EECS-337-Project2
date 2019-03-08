# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

# Hard coded quantities, tools and actions
import json
import os
import nltk
from gensim.models import word2vec
from nltk.tokenize import TweetTokenizer
from EECS337Project2.items import Ingredient
from EECS337Project2.items import Recipe
from EECS337Project2.spiders import recipes_spider
ingreDict = {}
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

punctuation = ['(', ')', ',', '.', ';', '?', '-']
prepPunct = [',', '.', ';', '-']
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
        if isinstance(item, Recipe):
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
                # Find the last punct and regard it as preparation
                indexRange = -1
                hasPrep = False
                textOnly = [k[0] for k in posIngre]
                for punct in prepPunct:
                    tmpIndex = -1
                    if punct in textOnly:
                        tmpIndex = textOnly.index(punct)
                    if tmpIndex != -1 and tmpIndex > indexRange:
                        indexRange = tmpIndex
                        hasPrep = True
                if indexRange == -1:
                    indexRange = len(posIngre)
                # find name / method
                adjs = []
                for i in range(bkpoint, indexRange):
                    wordtag = posIngre[i]
                    if wordtag[0] in punctuation:
                        bkpoint = i + 1
                        continue
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
                    for i in range(indexRange + 1, len(posIngre)):
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
        else:
            return item

# Pipelines that process raw direction data into structural object
class DirectionProcessPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, Recipe):
            with open("data/direction_corpus.txt", "a+") as file:
                directionList = item['rawDirectionList']
                for direction in directionList:
                    sentences = nltk.sent_tokenize(direction)
                    for sentence in sentences:
                        file.write(sentence + "\n")
                return item
        else:
            return item


class SwapProcessPipeline(object):
    def get_ingredient(self, old, database, cate, count, co):
        model = word2vec.Word2Vec.load("model")
        res = old.split()
        if len(res) >= 2:
            bigram = nltk.bigrams(res)

            for big in bigram:
                big1 = big[0] + '_' + big[1]
                try:

                    y1 = model.most_similar(big1, topn=100)

                    for temp in y1:
                        new = temp[0]
                        new = new.replace("_", " ")
                        if new in database:
                            if database[new]["count"] >= 2:

                                for category in database[new]["category"]:
                                    length = len(database[new]["category"])
                                    if (category == "vegetarian" or category =='vegan') and database[new]["category"][category] >= database[new]["count"] / 8:
                                        co += 1
                                        return new

                    return old

                except:
                    pass



        else:
            try:

                y1 = model.most_similar(old, topn=100)

                for temp in y1:
                    new = temp[0]
                    new = new.replace("_", " ")
                    if new in database:
                        if database[new]["count"] >= 2:


                            for category in database[new]["category"]:
                                length = len(database[new]["category"])
                                if (category == "vegetarian" or category == 'vegan') and database[new]["category"][category] >= database[new]["count"] / 8:
                                    co +=1
                                    return new

                return old

            except:
                pass

        return old


    def tovegetarian(self, old_recipe, database):
        co = 0
        for i in range(len(old_recipe["ingredients"])):
            temp = old_recipe["ingredients"][i]['name'].lower()

            res = temp.split()
            if temp not in database and len(res) > 1:
                length = len(res)
                for j in range(0, length):
                    if res[length - j - 1] in database:
                        temp = res[length - j - 1]
                        break

            if temp in database:
                flag = 0
                count = 0
                for category in database[temp]["category"]:
                    if database[temp]["category"][category] >= 3:
                        count += 1
                        if category == 'vegetarian' or category == 'vegan':
                            flag = 1

                if flag == 0 and count < 4:
                    new_ingredient = self.get_ingredient(temp,database,'vegetarian', count,co)
                    old_recipe["ingredients"][i]["name"] = new_ingredient

        print (co)


    def process_item(self, item, spider):
        if isinstance(item, Recipe):
            directionList = item['rawDirectionList']
            for direction in directionList:
                pass
            #
            # datapath = os.path.abspath(os.path.dirname(os.getcwd())) + '/data'
            with open("./data/final_formatted.json") as json_data:
                data = json.load(json_data)
            pass

            # if transferto == 'vegetarain':
            new_recipe = self.tovegetarian(item, data)

            return item
        else:
            return item










class StatisticPipeline(object):
    count = recipes_spider.RecipesSpider.startCount
    categoryCount = 0
    indexDict = recipes_spider.RecipesSpider.indexDict
    categoryList = recipes_spider.RecipesSpider.categoryList
    currCategory = categoryList[0]
    maxIter = 500
    def process_item(self, item, spider):
        if isinstance(item, Recipe):
            # Print progress
            print("Progress: " + str(self.count) + " / " + str(recipes_spider.RecipesSpider.maxUrlCount))
            # Change category
            if self.categoryCount == self.indexDict[self.currCategory]:
                nextIndex = self.categoryList.index(self.currCategory) + 1
                if nextIndex < len(self.categoryList):
                    self.currCategory = self.categoryList[nextIndex]
                    self.categoryCount = 0
            else:
                self.categoryCount += 1
            # Do dict count
            for i in item['ingredients']:
                if i['name'] == '':
                    continue
                if i['name'] in ingreDict:
                    ingreDict[i['name']]['count'] += 1
                    if self.currCategory not in ingreDict[i['name']]['category']:
                        ingreDict[i['name']]['category'].append(self.currCategory)
                else:
                    ingreDict[i['name']] = {}
                    ingreDict[i['name']]['count'] = 1
                    ingreDict[i['name']]['category'] = []
                    ingreDict[i['name']]['category'].append(self.currCategory)

            # If it reaches the max count
            self.count += 1
            if self.count >= recipes_spider.RecipesSpider.maxUrlCount:
                # Delete most frequent ones
                # for k, v in list(ingreDict.items()):
                #     if len(v['category']) >= 3:
                #         del ingreDict[k]
                # Sort dict
                sortedIngreDict = sorted(ingreDict.items(), key=lambda entry: entry[1]['count'], reverse=True)
                jsonFormat = {}
                self.maxIter = len(sortedIngreDict)
                # if self.maxIter > len(sortedIngreDict):
                #     self.maxIter = len(sortedIngreDict)
                # else:
                #     self.maxIter = 500
                for i in range(0, self.maxIter):
                    currName = sortedIngreDict[i][0].lower()
                    jsonFormat[currName] = {}
                    jsonFormat[currName]['count'] = sortedIngreDict[i][1]['count']
                    jsonFormat[currName]['category'] = []
                    for category in sortedIngreDict[i][1]['category']:
                        jsonFormat[currName]['category'].append(category)
                    jsonFormat[currName]['styles'] = []
                    jsonFormat[currName]['substitutions'] = {}
                    jsonFormat[currName]['substitutions']['to healthy'] = ""
                    jsonFormat[currName]['substitutions']['to italian'] = ""
                    jsonFormat[currName]['substitutions']['to meaty'] = ""
                    jsonFormat[currName]['substitutions']['to vegan'] = ""
                    jsonFormat[currName]['substitutions']['to vegetarian'] = ""
                trueJson = json.dumps(jsonFormat)
                with open("data/final_formatted.json", "w") as file:
                    file.write(trueJson)
                # Parse to json
            return item
        else:
            return item