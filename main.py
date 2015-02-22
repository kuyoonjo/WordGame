from flask import Flask, session, render_template, request, redirect, url_for
import os.path
import html
import time
import re
import WordGame

app = Flask(__name__)
app.secret_key = os.urandom(24)


class Config:
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    APP_STATIC = os.path.join(APP_ROOT, 'static')
    Dict7ToMore = WordGame.Dict(src=os.path.join(APP_ROOT,
                                                 "dicts/7-more.dict"),
                                count=201044)
    Dict3To6 = WordGame.Dict(src=os.path.join(APP_ROOT,
                                              "dicts/3-6.dict"),
                             count=34628)
    Database = os.path.join(APP_ROOT, 'WordGame.db')

class Strings:
    Title = "Word Game"
    Rule = 'Fill seven three-or-more letter words made up from the letters contained within '
    Note = 'Note: case insensitive and white space will be removed automatically'


@app.route('/')
def start():
    word = WordGame.Words.rand_word(Config.Dict7ToMore)
    session[word] = {
        'word': word,
        'time': None,
        'started': False,
        'finished': False,
        'success': False
    }
    return redirect(url_for('new_game', word=word))
@app.route('/game/<word>')
def new_game(word=None):
    if not word or word not in session:
        return redirect(url_for('start'))
    if session[word]['started']:
        del session[word]
        return redirect(url_for('start'))
    session[word]['started'] = True
    session[word]['time'] = time.time()
    return render_template("game.html",
                           title=Strings.Title,
                           word=word,
                           rule=Strings.Rule,
                           note=Strings.Note,
                           answers=range(1, 8),
                           action=url_for('get_result', word=word),
                           )

@app.route('/game/<word>/result', methods=['POST'])
def get_result(word):
    if not word or word not in session:
        return redirect(url_for('start'))
    if session[word]['finished']:
        del session[word]
        return redirect(url_for('start'))
    session[word]['finished'] = True
    dicts = [Config.Dict3To6, Config.Dict7ToMore]
    answers = request.form.getlist('answer')
    answers = [re.sub("\s+", "", html.escape(x)) for x in answers]
    answers = [x.lower() for x in answers]
    duplicates = WordGame.Words.duplicate(answers)
    duplicated = []
    results = []
    success = True
    for answer in answers:
        if answer == "":
            answer = '(empty)'
            result = WordGame.Result.Empty
        elif answer in duplicated:
            result = WordGame.Result.Duplicate + ' "%s"' % answer
        else:
            if answer in duplicates:
                duplicated.append(answer)
            result = WordGame.Words.check(answer, word, dicts)
        results.append({'answer': answer,
                        'result': result})
        if result != WordGame.Result.InDict:
            success = False
    if success:
        session[word]['time'] = time.time() - session[word]['time']
        session[word]['success'] = True
    return render_template("result.html",
                           title=Strings.Title,
                           rule=Strings.Rule,
                           note=Strings.Note,
                           word=word,
                           results=results,
                           time=session[word]['time'],
                           success=success,
                           action=url_for('get_score', word=word))

@app.route('/game/<word>/score', methods=['POST'])
def get_score(word):
    if not word or word not in session:
        return redirect(url_for('start'))
    if not session[word]['success']:
        del session[word]
        return redirect(url_for('start'))
    player = request.form.get('player')
    if player:
        player = html.escape(player)
    else:
        player = 'Anonymous'

    score = WordGame.Score(player, session[word]['time'])
    score.save_to(Config.Database)
    top10 = WordGame.Score.get_top_10_from(Config.Database)
    rank = score.rank(Config.Database)
    return render_template("score.html",
                           title='Word Game',
                           top10=top10,
                           rank=rank,
                           player=player)

@app.route('/top10')
def show_top10():
    top10 = WordGame.Score.get_top_10_from(Config.Database)
    return render_template("top10.html",
                           title=Strings.Title,
                           rule=Strings.Rule,
                           top10=top10)

if __name__ == '__main__':
    app.run(debug=True)