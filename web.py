import base64

from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap

from datetime import datetime

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
<<<<<<< HEAD:server.py
    storm_recurrence = form['storm_recurrence']
    start_date = datetime.strptime(start_date, '%d.%m.%Y')
    end_date = datetime.strptime(end_date, '%d.%m.%Y')
    load_weather_data(station_id, start_date, end_date)
    data = WindIndicator.query.filter(WindIndicator.weather_station_id == station_id,
                                      WindIndicator.local_date < end_date, WindIndicator.local_date > start_date).all()
    # TODO сделать проверку, чтобы всегда storm_recurrence > 0
    storm_recurrence = float(storm_recurrence)
    velocity, _, image_buf = get_calculation_results(data, storm_recurrence, start_date, end_date)

    filter(
        WindIndicator.local_date

        )


    velocity, result_direction_speed, image_buf = get_calculation_results(data)
>>>>>>> refs/remotes/origin/develop:web.py
    image_encoded = base64.b64encode(image_buf.getvalue()).decode('utf-8')

    return render_template(
        'calculate.html',
        velocity_table=velocity,
        image=str(image_encoded),
        result_direction_speed=result_direction_speed
    )


if __name__ == '__main__':
    create_db()
    app.run(port=8080, debug=True)
