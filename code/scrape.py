# -*- coding: UTF-8 -*-
import re
import numpy as np
import requests as rq
import os
import pandas as pd
import newspaper
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

def get_article(url, lang):
    """Get text of article from url and language"""
    a = newspaper.build_article(url, lang=lang)
    a.download()
    a.parse()
    return a

lang_dict = {
    "movies-danish - movies-danish.csv": "da",
    "movies-dutch - movies-dutch.csv": "nl",
    "movies-english - movies-english.csv": "en",
    "movies-finnish - movies-finnish.csv": "fi",
    "movies-norwegian - movies-norwegian.csv": "no",
    "movies-swedish - movies-swedish.csv": "sv",
    "music-danish - music-danish.csv": "da",
    "music-german - music-german.csv": "de",
    "music-norwegian - music-norwegian.csv": "no", 
    "music-polish - music-polish.csv": "en",
    "music-swedish - music-swedish.csv": "sv"
}

bad_domains = Counter()
ok_domains = Counter()

for f in os.listdir("../data/quotes"):

    if f == ".DS_Store":
        continue

    print "processing:", f
    print "... language", lang_dict[f]

    if f in os.listdir("../data/review_quotes"):
        print "... already processed"
        continue

    dat = pd.read_csv(
        "../data/quotes/%s" % f,
        names=["url", "quote", "score", "orig_score"])

    reviews = []
    for item in dat.iterrows():

        domain = re.findall(r".*\://(?:www.)?([^\/]+)", item[1]['url'])[0]

        print ".",

        if bad_domains[domain] > ok_domains[domain] and bad_domains[domain] > 5:
            continue

        a = get_article(item[1]['url'], lang_dict[f])
        cf_quote = "".join(re.findall(r"\w+", item[1]['quote'][3:-3]))  # 'compact
        cf_review = "".join(re.findall(r"\w+", a.text))                 # form'

        if cf_quote not in cf_review:
            print "Bad_domain", domain
            bad_domains.update(domain)

            reviews.append("")
            continue

        print "!"

        ok_domains.update(domain)
        reviews.append(a.text)

    dat.loc[:, 'review'] = pd.Series(reviews, index=dat.index)
    dat.to_csv("../data/review_quotes/%s" % f, encoding="utf-8")

    print "Successfully wrote", f, "to review_quotes"
