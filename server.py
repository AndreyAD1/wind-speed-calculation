import base64

from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap

from databases import create_db, load_weather_data, WindIndicator
from calculations import get_calculation_results

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
    data = WindIndicator.query.filter(WindIndicator.weather_station_id==station_id).all()
    velocity, _, image_buf = get_calculation_results(data)
    image_encoded = base64.b64encode(image_buf.getvalue()).decode('utf-8')
    return render_template(
        'calculate.html',
        velocity_table=velocity,
        image=str(image_encoded),
    )


if __name__ == '__main__':
    create_db()
    app.run(port=8080, debug=True)
