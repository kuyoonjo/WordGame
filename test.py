__author__ = 'yuchen'

import WordGame
import os
import sqlite3

class Config:
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    APP_STATIC = os.path.join(APP_ROOT, 'static')
    Dict7ToMore = WordGame.Dict(src = os.path.join(APP_ROOT, "dicts/7-more.dict"),
                                count = 201044)
    Dict3To6 = WordGame.Dict(src = "dicts/3-6.dict",
                             count = 34628)

s = WordGame.Words.check_word('intelligent', 'intelligent');
print(s)
s = WordGame.Words.check_dict('tell', Config.Dict3To6);
print(s)
s = WordGame.Words.check_dict('tell', Config.Dict7ToMore);
print(s)
score = WordGame.Score("A", 100)
score.save_to('WordGame.db')