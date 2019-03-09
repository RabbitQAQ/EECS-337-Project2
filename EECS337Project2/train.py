import re
import os
import string

import nltk
import json
import numpy as np
from gensim.models import word2vec
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

from nltk.tokenize import TweetTokenizer
from gensim.models.phrases import Phrases, Phraser
from nltk.corpus import stopwords

def clean_sentence(sentence):
    sentence = sentence.lower().strip()
    sentence = re.sub("[^a-zA-Z0-9- ]", "", sentence)
    return sentence

def build_phrases(sentences):
    phrases = Phrases(sentences,
                      min_count=2,
                      threshold=10,
                      )
    return Phraser(phrases)

file = open("./data/direction_corpus.txt")

lines = file.read().split("\n")
Tokenizer = TweetTokenizer()
wordtovec = []

processed = []

# for line in lines:
#     line = clean_sentence(line)
#     # if line[-1] == '.':
#     #     line.replace('.', '')
#     line = line.lower()
#     processed.append(line)
#
#
#
#     w = Tokenizer.tokenize(line)
#
#
#
#
# phrases = build_phrases(processed)
#
#
# sentence_stream = [li.split(" ") for li in processed]
# bigram = Phrases(sentence_stream, min_count=2, threshold=5)
# for lin in processed:
#     w = Tokenizer.tokenize(lin)
#     wordtovec.append(bigram[w])

# model = word2vec.Word2Vec(wordtovec, workers = 2, size = 300, min_count = 2, window = 5, sample = 0.001)
# model.save("model")
model = word2vec.Word2Vec.load("model")
y1 = model.most_similar("tie_pasta", topn=30)
y2 = model.most_similar("oil", topn=30)
y3 = model.most_similar("salt", topn=30)
y4 = model.most_similar("egg", topn=30)
print(y1)
print(y2)
print(y3)
print(y4)
