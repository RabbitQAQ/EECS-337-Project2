# Instruction

### About the project
* The project is based on **Scrapy**, **NLTK**, **Spacy** and **Word2Vec**, you may need to download them if you don't have
* For the spacy, you may need to use `python -m spacy download en` in order to have its english model
* The data in data folder is crawled by ourselves using **category_spider.py**
* The **recipes_spider.py** is what actually crawls the recipe page and run the whole project
* We **don't use any hardcoded** in the **transformation part**. The ingredient we may replace and its alternative is **totally** based on our data (but we do use some hard code when parsing the quantity and measurement)
* Since there is no hardcoded, some results may look a little bit strange, like we may not replace "skinless boneless chicken breast" to any thing (or just to "chicken breast"). But we still can replace "chicken breast"


### How to run the project
* Simply run `Python main.py` when you are in the EECS-337-Project2/EECS337Project2/
* Follow the instruction and input the URLs you want to query
* The output recipe is a little bit long, it contains **raw ingredients**, **parsed ingredients**, **raw directions**, **parsed directions** and **transformation functions**
* There are several transformation you can choose:
   * To / From Healthy
   * To / From Vegetarian
   * To Vegan
   * To Italian
   * To Chinese
* The git repo link is here: [Click Me](https://github.com/RabbitQAQ/EECS-337-Project2)
