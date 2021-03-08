# routes.py
from flask import *
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/4k')
def key4():
    difficulty = {"nihilism": "veryhard", "round3": "normal", "revelation": "hard"}
    level = {"nihilism": 19, "round3": 16, "revelation": 16}
    return render_template('table.html', result=difficulty, level=level)

if __name__ == '__main__':
	app.run()