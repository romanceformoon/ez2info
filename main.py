from flask import *
from flask_cors import CORS
import sqlite3
from werkzeug.utils import secure_filename
import os
import ocr
import random
import string
import json
from difflib import SequenceMatcher

app = Flask(__name__)
CORS(app)


@app.errorhandler(400)
def error_400(error):
    return "400 Error"


@app.errorhandler(401)
def error_401(error):
    return "401 Error"


@app.errorhandler(403)
def error_403(error):
    return "403 Error"


@app.errorhandler(404)
def error_404(error):
    return "404 Error"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/detail', methods=['GET'])
def detail():
    if request.method == 'GET':
        song = request.args['song']
        key = request.args['key']

        conn = sqlite3.connect("ranking.db")
        c = conn.cursor()

        c.execute("SELECT * FROM ranking WHERE song='" + song +
                  "' AND key=" + key + " ORDER BY score DESC")
        rows = c.fetchall()

        c.execute("SELECT name, video, pattern FROM difficulty WHERE song='" + song +
                  "' AND key=" + key + " LIMIT 1")
        temp_rows = c.fetchall()
        song_name = temp_rows[0][0]
        youtube_link = temp_rows[0][1]
        pattern = temp_rows[0][2]

        conn.close()

        mix = ""
        if song[-1] == "1":
            mix = "EASY MIX"
        elif song[-1] == "2":
            mix = "NORMAL MIX"
        elif song[-1] == "3":
            mix = "HARD MIX"
        elif song[-1] == "4":
            mix = "SUPER HARD MIX"

        ranking = {}
        rank = 1
        already_list = []

        for row in rows:
            kool = row[3]
            cool = row[4]
            good = row[5]
            miss = row[6]
            fail = row[7]
            score = row[8]
            acc = row[9]
            combo = row[10]
            nickname = row[11]
            key = row[0]
            filename = row[15]
            notes = row[2]

            if rank == 11:
                break
            temp = nickname
            if temp not in already_list:
                ranking[rank] = [kool, cool, good, miss, fail,
                                 score, acc, combo, nickname, notes, key, filename]
                already_list.append(nickname)
                rank += 1

        return render_template('detail.html', song=song, whatKey=key, ranking=ranking, link=youtube_link, name=song_name, key=key, dif=mix, pattern=pattern)


@app.route('/ranking', methods=['GET'])
def ranking():
    if request.method == 'GET':
        song = request.args['song']
        key = request.args['key']

        conn = sqlite3.connect("ranking.db")
        c = conn.cursor()

        c.execute("SELECT * FROM ranking WHERE song='" + song +
                  "' AND key=" + key + " ORDER BY score DESC")
        rows = c.fetchall()

        c.execute("SELECT name FROM difficulty WHERE song='" +
                  song + "' LIMIT 1")
        temp_rows = c.fetchall()
        song_name = temp_rows[0][0]

        conn.close()

        mix = ""
        if song[-1] == "1":
            mix = "EASY MIX"
        elif song[-1] == "2":
            mix = "NORMAL MIX"
        elif song[-1] == "3":
            mix = "HARD MIX"
        elif song[-1] == "4":
            mix = "SUPER HARD MIX"

        ranking = {}
        rank = 1
        already_list = []

        for row in rows:
            kool = row[3]
            cool = row[4]
            good = row[5]
            miss = row[6]
            fail = row[7]
            score = row[8]
            acc = row[9]
            combo = row[10]
            nickname = row[11]
            key = row[0]
            filename = row[15]
            notes = row[2]

            temp = nickname
            if temp not in already_list:
                ranking[rank] = [kool, cool, good, miss, fail,
                                 score, acc, combo, nickname, notes, key, filename]
                already_list.append(nickname)
                rank += 1

        return render_template('ranking.html', ranking=ranking, name=song_name, key=key, dif=mix)


@app.route('/table', methods=['GET'])
def table():
    if request.method == 'GET':
        key = request.args['key']

        conn = sqlite3.connect("ranking.db")
        c = conn.cursor()

        c.execute("SELECT * FROM difficulty WHERE key=" + key)
        rows = c.fetchall()
        conn.close()

        difficulty = {}
        level = {}

        for row in rows:
            difficulty[row[2]] = row[4]
        for row in rows:
            level[row[2]] = row[3]

        return render_template('table.html', result=difficulty, level=level, whatKey=key)


@app.route('/submit_page', methods=['GET'])
def submit_page():
    if request.method == 'GET':
        song = request.args['song']
        key = request.args['key']

        conn = sqlite3.connect("ranking.db")
        c = conn.cursor()

        c.execute("SELECT * FROM ranking WHERE song='" + song +
                  "' AND key=" + key + " ORDER BY score DESC")
        rows = c.fetchall()

        c.execute("SELECT name FROM difficulty WHERE song='" +
                  song + "' LIMIT 1")
        temp_rows = c.fetchall()
        song_name = temp_rows[0][0]

        conn.close()

        mix = ""
        if song[-1] == "1":
            mix = "EASY MIX"
        elif song[-1] == "2":
            mix = "NORMAL MIX"
        elif song[-1] == "3":
            mix = "HARD MIX"
        elif song[-1] == "4":
            mix = "SUPER HARD MIX"

        return render_template('ranking_add.html', song=song, name=song_name, key=key, dif=mix)


@app.route('/add', methods=['POST'])
def ranking_add():
    if request.method == 'POST':
        data = request.get_json()
        song = data['song']
        key = data['key']
        kool = data['kool']
        cool = data['cool']
        good = data['good']
        miss = data['miss']
        fail = data['fail']
        score = data['score']
        acc = data['rate']
        combo = data['combo']
        nickname = data['nickname']
        filename = data['filename']
        notes = data['notes']
        conn = sqlite3.connect("ranking.db")
        c = conn.cursor()

        c.executemany(
            'INSERT INTO ranking VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            [
                (key, song, notes, kool, cool, good, miss, fail, score,
                 acc, combo, nickname, "", "", "", filename)
            ]
        )
        conn.commit()
        conn.close()

        return render_template('success.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        song = request.form['song']
        key = request.form['key']
        f = request.files['file']
        name, ext = os.path.splitext(f.filename)

        filename = ''.join(random.choice(string.ascii_uppercase + string.digits)
                           for _ in range(8)) + ext

        f.save(os.path.join('static/upload', filename))
        result = ocr.work(os.path.join('static/upload', filename))

        num_notes = result['notes']
        sum_notes = int(result['kool']) + int(result['cool']) + \
            int(result['good']) + int(result['miss']) + int(result['fail'])

        if int(num_notes) < int(sum_notes) and int(result['miss']) == 10:
            print("Change Miss 10 to 0")
            result['miss'] = "0"
            sum_notes = int(result['kool']) + int(result['cool']) + \
                int(result['good']) + int(result['miss']) + int(result['fail'])

        if int(num_notes) < int(sum_notes) and int(result['fail']) == 10:
            print("Change Fail 10 to 0")
            result['fail'] = "0"
            sum_notes = int(result['kool']) + int(result['cool']) + \
                int(result['good']) + int(result['miss']) + int(result['fail'])

        if int(num_notes) < int(sum_notes) and int(result['good']) == 10:
            print("Change Good 10 to 0")
            result['good'] = "0"
            sum_notes = int(result['kool']) + int(result['cool']) + \
                int(result['good']) + int(result['miss']) + int(result['fail'])

        if int(num_notes) < int(sum_notes) and int(result['cool']) == 10:
            print("Change Cool 10 to 0")
            result['miss'] = "0"
            sum_notes = int(result['kool']) + int(result['cool']) + \
                int(result['good']) + int(result['miss']) + int(result['fail'])

        result['rate'] = round(int(result['score']) /
                               (1100000 + int(num_notes)) * 100, 2)
        result['key'] = key
        result['filename'] = filename

        print(result['rate'])
        print(song.upper(), result['song'].upper())
        print(SequenceMatcher(None, song.upper(),
              result['song'].upper()).ratio())

        if SequenceMatcher(None, song.upper(), result['song'].upper()).ratio() > 0.6:
            # return render_template('data_check.html', result=result, filename=filename, song=song, key=key)
            result['song'] = song
            result['success'] = "success"
            return json.dumps(result)
        else:
            os.remove(os.path.join('static/upload', filename))
            print("곡명이 일치하지 않습니다.")
            result['success'] = "fail"
            return json.dumps(result)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
