from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap

from databases import create_db, load_weather_data

app = Flask(__name__)
Bootstrap(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/calculate', methods=['POST'])
def calculate():
    form = request.form
    station_id = form['station_id']
    start_date = form['from']
    end_date = form['to']
    load_weather_data(station_id, start_date, end_date)

    return 'Тут результат'


if __name__ == '__main__':
    create_db()
    app.run(port=8080, debug=True)
