__author__ = 'Yu Chen'

from random import randint
import re
import collections
import sqlite3

class Dict:
    src = None
    count = 0
    def __init__(self, src, count):
        self.src = src
        self.count = count

class Result:
    Empty = 'the word cannot be empty'
    Duplicate = 'duplicate answers'
    Correct = 'correct'
    SameWord = ' is the same as source word '
    LengthLessThan3 = 'length of word "%s" less than 3'
    AlphabetWrong = ' is reused or not in the word '
    InDict = 'in dict'
    NotInDict = ' is not in dictionary'

class Words:
    @staticmethod
    def rand_word(_dict):
        word = None
        src = _dict.src
        count = _dict.count
        ri = randint(1, count)
        fp = open(src)
        for i, line in enumerate(fp):
            if i == ri:
                word = fp.readline().rstrip()
                break
        fp.close()
        return word

    @staticmethod
    def check(_answer, _word, _dicts):
        result = Words.check_word(_answer, _word)
        if result != Result.Correct:
            return result
        for dict in _dicts:
            result = Words.check_dict(_answer, dict)
            if result == Result.InDict:
                return result
        return '"%s"' % _answer + Result.NotInDict

    @staticmethod
    def check_word(_answer, _word):
        answer = _answer.lower()
        word = _word.lower()

        if answer == word:
            return '"%s"' % answer + Result.SameWord + '"%s"' % word

        if len(answer) < 3:
            return Result.LengthLessThan3 % answer

        for a in answer:
            if a in word:
                word = re.sub(a, "", word, 1)
            else:
                return '"%s"' % a + Result.AlphabetWrong + '"%s"' % _word
        return Result.Correct

    @staticmethod
    def check_dict(_answer, _dict):
        answer = _answer.lower()
        src = _dict.src

        with open(src) as f:
            for word in f:
                if answer == word.rstrip().lower():
                    return Result.InDict

        return Result.NotInDict

    @staticmethod
    def duplicate(_answers):
        return [x for x, y in collections.Counter(_answers).items() if y > 1]


class Score:
    id = None
    player = None
    time = None
    def __init__(self, player, time):
        self.player = player
        self.time = time

    def save_to(self, _database):
        conn = sqlite3.connect(_database)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO score (player, time) VALUES (?, ?)',
                       (self.player, self.time));
        self.id = cursor.lastrowid
        conn.commit()
        conn.close()

    def rank(self, _database):
        conn = sqlite3.connect(_database)
        cursor = conn.cursor()
        rows = cursor.execute("SELECT id from score ORDER BY time")
        count = 1
        for row in rows:
            if self.id == row[0]:
                break
            count += 1
        return count

    @staticmethod
    def get_top_10_from(_database):
        conn = sqlite3.connect(_database)
        cursor = conn.cursor()
        rows = cursor.execute("SELECT id, player, time from score ORDER BY time limit 10")
        scores = []
        for row in rows:
            scores.append(Score(player = row[1],
                                time = row[2]))
        conn.close()
        return scores


