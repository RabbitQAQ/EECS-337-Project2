# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

# Hard coded quantities, tools and actions
import json
import os
import nltk
import copy
from gensim.models import word2vec
from nltk.tokenize import TweetTokenizer
from EECS337Project2.items import Ingredient
from EECS337Project2.items import Step
from EECS337Project2.items import Recipe
from EECS337Project2.spiders import recipes_spider
import spacy

ingreDict = {}
tools = []
methodToTools = {
    'chop': 'knife',
    'cut': 'knife',
    'julienne': 'knife',
    'mince': 'knife',
    'dice': 'knife',
    'slice': 'knife',
    'stir': 'spoon',
    'fold': 'spoon',
    'glaze': 'spoon',
    'drizzle': 'spoon',
    'heated': 'oven',
    'fry': 'pan',
    'baste': 'baster',
    'sift': 'colander',
    'cream': 'hand mixer',
    'grate': 'grater',
    'whisk': 'whisk',
    'marinate': 'bowl',
    'shred': 'food processor',
    'peel': 'peeler',
    'mix' : 'cooker',
    'cover' : 'lid'
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
nlp = spacy.load('en')
cooking_verbs = {'arrange', 'baste', 'beat', 'blend', 'brown', 'build', 'bury', 'carve', 'check', 'chop', 'close', 'cool', 'correct', 'cover', 'crumple', 'cut', 'decorate', 'discard', 'divide', 'drape', 'drop', 'dry', 'film', 'fold', 'follow', 'form', 'force', 'glaze', 'insert', 'lay', 'leave', 'lift', 'make', 'melt', 'mince', 'mix', 'moisten', 'mound', 'open', 'pack', 'paint', 'pierce', 'pour', 'prepare', 'press', 'prick', 'pull', 'puree', 'push', 'quarter', 'raise', 'reduce', 'refresh', 'reheat', 'replace', 'return', 'ring', 'roast', 'roll', 'salt', 'saute', 'scatter', 'scoop', 'scrape', 'scrub', 'season', 'separate', 'set', 'settle', 'shave', 'simmer', 'skim', 'slice', 'slide', 'slip', 'slit', 'smear', 'soak', 'spoon', 'spread', 'sprinkle', 'stir', 'strain', 'strew', 'stuff', 'surround', 'taste', 'thin', 'tie', 'tilt', 'tip', 'top', 'toss', 'trim', 'turn', 'twist', 'warm', 'wilt', 'wind', 'wrap'}
time_noun = ['time', 'time','while', 'minute','seconds','hour']

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

def isTimeNounChunk(text):
    for noun in time_noun:
        if noun in text.lower():
            return True

def preprocess(direction):
    direction = direction.replace('season ', 'seasoning ').replace('cover ', 'covering ')
    return direction

# Pipelines that process raw direction data into structural object
class DirectionProcessPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, Recipe):
            try:
                item['steps'] = []
                directionList = item['rawDirectionList']
                # for direction in directionList:
                #     sentences = nltk.sent_tokenize(direction)
                #     for i in range(0, len(sentences)):
                #         item['steps'].append(sentences[i])

                for direction in directionList:

                    sentences = nlp(preprocess(direction.lower()))

                    for step_sentence in sentences.sents:
                        # item['steps'].append(sentences[i])
                        tmp_step = Step()
                        # ingredient | tools | methods
                        # posIngre = nltk.pos_tag(twTokenizer.tokenize(step_sentence))
                        step_doc = nlp(step_sentence.text)
                        currIngredients = []
                        currTools = []
                        currMethods = []
                        currTime = []

                        for ent in step_doc.ents:
                            if (ent.label_ == 'TIME'):
                                currTime.append(ent.text)

                        for token in step_doc:
                            if (token.pos_ == 'VERB'):
                                if (token.lemma_ in cooking_verbs):
                                    currMethods.append(token.lemma_)
                                    currTools.append(methodToTools.get(token.lemma_))

                        for chunk in step_doc.noun_chunks:
                            if (chunk.root.text.lower() not in methodToTools.values()):
                                if (not isTimeNounChunk(
                                        chunk.text.lower()) and not chunk.text.lower() in cooking_verbs):
                                    currIngredients.append(chunk.text)
                            else:
                                if (chunk.root.text.lower() not in currTools):
                                    currTools.append(chunk.text)

                        tmp_step['ingredient'] = currIngredients
                        tmp_step['tools'] = currTools
                        tmp_step['methods'] = currMethods
                        tmp_step['stepTime'] = currTime

                        item['steps'].append(tmp_step)
                return item
            except:
                return item
        else:
            return item


class SwapProcessPipeline(object):
    def get_ingredient(self, old, database, cate):
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
                            if database[new]["count"] >= 8:
                                for category in database[new]["category"]:
                                    length = len(database[new]["category"])
                                    if (category == cate) and database[new]["category"][category] > database[new]["count"] / 7:
                                        return new


                except:
                    big1 = big[1]
                    try:

                        y1 = model.most_similar(big1, topn=100)
                        for temp in y1:
                            new = temp[0]
                            new = new.replace("_", " ")
                            if new in database:
                                if database[new]["count"] >= 5:
                                    for category in database[new]["category"]:
                                        length = len(database[new]["category"])
                                        if (category == cate) and database[new]["category"][category] > database[new][
                                            "count"] / 2 and length >= 5:
                                            return new


                    except:
                        pass


        else:
            try:

                y1 = model.most_similar(old, topn=100)

                for temp in y1:
                    new = temp[0]
                    new = new.replace("_", " ")
                    if new in database:
                        if database[new]["count"] >= 8:
                            for category in database[new]["category"]:
                                length = len(database[new]["category"])
                                if (category == cate) and database[new]["category"][category] > database[new]["count"] / 7:

                                    return new

            except:
                pass

        return old



    def get_ingredient_vegetarian(self, old, database):
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
                            if database[new]["count"] >= 9:

                                for category in database[new]["category"]:
                                    length = len(database[new]["category"])
                                    if (category == "vegetarian" or category == 'vegan') and database[new]["category"][category] >= database[new]["count"] / 8:

                                        return new


                except:
                    big1 = big[1]
                    try:

                        y1 = model.most_similar(big1, topn=100)
                        for temp in y1:
                            new = temp[0]
                            new = new.replace("_", " ")
                            if new in database:
                                if database[new]["count"] >= 5:
                                    for category in database[new]["category"]:
                                        length = len(database[new]["category"])
                                        if (category == "vegetarian" or category == 'vegan') and database[new]["category"][category] > database[new]["count"] / 2 and length >= 5:
                                            return new


                    except:
                        pass

        else:
            try:

                y1 = model.most_similar(old, topn=100)

                for temp in y1:
                    new = temp[0]
                    new = new.replace("_", " ")
                    if new in database:
                        if database[new]["count"] >= 9:
                            for category in database[new]["category"]:
                                length = len(database[new]["category"])
                                if (category == "vegetarian" or category == 'vegan') and database[new]["category"][category] >= database[new]["count"] / 8:

                                    return new

            except:
                pass

        return old

    def get_seasoning(self, old, database, cate, seasoning_list):
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
                            if database[new]["count"] >= 5:
                                for category in database[new]["category"]:
                                    length = len(database[new]["category"])
                                    if (category == cate) and database[new]["category"][category] > database[new]["count"] / 2 and length >= 5:
                                        if new in seasoning_list:
                                            continue
                                        return new


                except:
                    big1 = big[1]
                    try:

                        y1 = model.most_similar(big1, topn=100)
                        for temp in y1:
                            new = temp[0]
                            new = new.replace("_", " ")
                            if new in database:
                                if database[new]["count"] >= 5:
                                    for category in database[new]["category"]:
                                        length = len(database[new]["category"])
                                        if (category == cate) and database[new]["category"][category] > database[new]["count"] / 2 and length >= 5:
                                            if new in seasoning_list:
                                                continue
                                            return new


                    except:
                        pass



        else:
            try:

                y1 = model.most_similar(old, topn=100)

                for temp in y1:
                    new = temp[0]
                    new = new.replace("_", " ")
                    if new in database:
                        if database[new]["count"] >= 5:
                            for category in database[new]["category"]:
                                length = len(database[new]["category"])
                                if (category == cate) and database[new]["category"][category] > database[new]["count"] /2.5 and length >= 5:
                                    if new in seasoning_list:
                                        continue
                                    return new

            except:
                pass

        return old



    def tovegetarian(self, old_recipe, database):


        for i in range(len(old_recipe["ingredients"])):
            temp = old_recipe["ingredients"][i]['name'].lower()

            res = temp.split()
            if len(res) > 3:
                bigram = nltk.bigrams(res)
                for big in bigram:
                    temp = big[0] + ' ' + big[1]


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

                if flag == 0 and count <= 4:
                    new_ingredient = self.get_ingredient_vegetarian(temp, database)
                    old_recipe["ingredients"][i]["name"] = new_ingredient
                    for each in old_recipe["steps"]:
                        each.replace(old_recipe["ingredients"][i]["name"], new_ingredient)




    def tonew(self, old_recipe, database, cate):
        seasoning_list = []
        for i in range(len(old_recipe["ingredients"])):
            temp = old_recipe["ingredients"][i]['name'].lower()

            res = temp.split()
            if len(res) > 3:
                bigram = nltk.bigrams(res)
                for big in bigram:

                    temp = big[0] + ' ' + big[1]



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
                        if category == cate:
                            flag = 1

                if flag == 0 and count <= 5:
                    new_ingredient = self.get_ingredient(temp, database, cate)
                    old_recipe["ingredients"][i]["name"] = new_ingredient

                if (count == 5 and flag == 1) or count == 6:
                    if database[temp]["category"][category] / database[temp]["count"] < 0.25:
                        new_ingredient = self.get_seasoning(temp, database, cate,seasoning_list)
                        seasoning_list.append(new_ingredient)
                        old_recipe["ingredients"][i]["name"] = new_ingredient
                        for each in old_recipe["steps"]:
                            each.replace(old_recipe["ingredients"][i]["name"],new_ingredient)






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

            toChineseRecipe = copy.deepcopy(item)
            toItalianRecipe = copy.deepcopy(item)
            toHealthyRecipe = copy.deepcopy(item)
            toVegetarianRecipe = copy.deepcopy(item)
            toVeganRecipe = copy.deepcopy(item)
            self.tonew(toChineseRecipe, data, 'chinese')
            self.tonew(toItalianRecipe, data, 'italian')
            self.tonew(toHealthyRecipe, data, 'healthy')
            self.tovegetarian(toVegetarianRecipe, data)
            self.tonew(toVeganRecipe, data, 'vegan')
            item['toChinese'] = toChineseRecipe
            item['toItalian'] = toItalianRecipe
            item['toHealthy'] = toHealthyRecipe
            item['toVegetarian'] = toVegetarianRecipe
            item['toVegan'] = toVeganRecipe


            return item
        else:
            return item

class UIPipeline(object):
    def printRecipe(self, item):
        print("++++++++++++++ Recipes +++++++++++++++")
        print("======== Ingredients =======")
        for i in range(0, len(item['ingredients'])):
            currIngredient = item['ingredients'][i]
            print(str(i) + ". " + currIngredient['descriptor'] + ' ' + currIngredient['name'])
            print("Quantity and Measurement: " + currIngredient["quantityAndMeasurement"])
            print("Preparation: " + currIngredient["preparation"])
            print("Method: " + str(currIngredient["method"]))
            print("Tool: " + str(currIngredient["tool"]))
        print("======== Steps =======")
        for i in range(0, len(item['steps'])):
            print(str(i) + ". " + item['steps'][i])
        print("========== End ==========")
    def process_item(self, item, spider):
        if isinstance(item, Recipe):
            # Show Origin Recipe
            self.printRecipe(item)
            while True:
                print("Select the transformation you wanna do:")
                print("0. To Vegetarian")
                print("1. To Vegan")
                print("2. To Healthy")
                print("3. To Chinese")
                print("4. To Italian")
                print("q. quit")
                selection = input("Your choice: ")
                if selection == '0':
                    self.printRecipe(item["toVegetarian"])
                elif selection == '1':
                    self.printRecipe(item["toVegan"])
                elif selection == '2':
                    self.printRecipe(item["toHealthy"])
                elif selection == '3':
                    self.printRecipe(item["toChinese"])
                elif selection == '4':
                    self.printRecipe(item["toItalian"])
                elif selection == 'q':
                    break
                else:
                    print("Invalid Input. Try Again.")

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