# -*- coding: utf-8 -*-
"""
Created on Fri Jun 11 15:42:20 2021

@author: Nandita
"""

from flask import Flask, render_template, request

#import yaml
from PIL import Image
import pytesseract
import re
import nltk
#import csv
#import pandas as pd
from nltk.corpus import stopwords    
#from nltk.stem.porter import PorterStemmer
#from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from collections import Counter

app = Flask(__name__)



@app.route('/')
def index():       
    return render_template('index.html')

@app.route('/')
def getKeywords():
    keywords = request.form['keywords']
    return keywords

@app.route('/')
def getAnswerSheet():
    imagee = request.form['answer_sheet']
    return imagee

@app.route('/',methods=['POST'])
def answer_evaluation():
    
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    answer_sheet = getAnswerSheet()
    file = Image.open(answer_sheet)
    answer = pytesseract.image_to_string(file, lang='eng')
    
    # Tokenizing sentences
    #sentences = nltk.sent_tokenize(answer)

    # Tokenizing words
    words = nltk.word_tokenize(answer)
    #Lematization
    #wordnet = WordNetLemmatizer()
    corpus = []
    for i in range(len(words)):
        review = re.sub('[^a-zA-Z]', ' ', words[i])
        review = review.lower()
        review = review.split()
        review = [word for word in review if not word in stopwords.words('english')]
        review = ' '.join(review)
        corpus.append(review)
    corpus = list(filter(None,corpus))
    keywords = list(map(str, getKeywords().strip().split()))
    
    corpus_synonyms = []
    for i in range(len(corpus)):
        for syn in wordnet.synsets(corpus[i]):
            for l in syn.lemmas():
                corpus_synonyms.append(l.name())
    
    common = set(keywords) & set(corpus_synonyms)
    
    # count word occurrences
    a_vals = Counter(common)
    b_vals = Counter(keywords)
    # convert to word-vectors
    words  = list(a_vals.keys() | b_vals.keys())
    a_vect = [a_vals.get(word, 0) for word in words]        # [0, 0, 1, 1, 2, 1]
    b_vect = [b_vals.get(word, 0) for word in words]        # [1, 1, 1, 0, 1, 0]
    # find cosine-similarity
    len_a  = sum(av*av for av in a_vect) ** 0.5             # sqrt(7)
    len_b  = sum(bv*bv for bv in b_vect) ** 0.5             # sqrt(4)
    dot    = sum(av*bv for av,bv in zip(a_vect, b_vect))    # 3
    cosine = dot / (len_a * len_b) 
    cosine = cosine*100
    
    if(cosine>=90):
        Marks = 10
        return render_template('pass.html', mark=Marks)
    elif(89.99>=cosine>=80):
        Marks = 9
        return render_template('pass.html', mark=Marks)
    elif(79.99>=cosine>=70):
        Marks = 8
        return render_template('pass.html', mark=Marks)
    elif(69.99>=cosine>=60):    
        Marks = 7
        return render_template('pass.html', mark=Marks)
    elif(59.99>=cosine>=50):
        Marks = 6
        return render_template('pass.html', mark=Marks)
    elif(49.99>=cosine>=40):
        Marks = 5
        return render_template('pass.html', mark=Marks)
    elif(39.99>=cosine>=30):
        Marks = 4
        return render_template('pass.html', mark=Marks)
    elif(29.99>=cosine>=20):
        Marks = 3
        return render_template('pass.html', mark=Marks)
    elif(19.99>=cosine>=10):
        Marks = 2
        return render_template('pass.html', mark=Marks)
    elif(9.99>=cosine>=1):
        Marks = 1
        return render_template('pass.html', mark=Marks)
    else:
        Marks = 0
        return render_template('pass.html', mark=Marks)
    


if __name__ == '__main__':
    app.run(debug=True)