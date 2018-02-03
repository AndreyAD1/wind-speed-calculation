import base64
from datetime import datetime

from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap

from databases import load_weather_data, WindIndicator
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
    storm_recurrence = form['storm_recurrence']
    start_date = datetime.strptime(start_date, '%d.%m.%Y')
    end_date = datetime.strptime(end_date, '%d.%m.%Y')
    load_weather_data(station_id, start_date, end_date)

    data = WindIndicator.query.filter(WindIndicator.weather_station_id == station_id,
                                      WindIndicator.local_date <= end_date,
                                      WindIndicator.local_date >= start_date).all()

    # TODO сделать проверку, чтобы всегда storm_recurrence > 0
    storm_recurrence = float(storm_recurrence)

    velocity, result_direction_speed, image_buf, legend_decoding_dict = get_calculation_results(
        data, storm_recurrence, start_date, end_date
    )
    image_encoded = base64.b64encode(image_buf.getvalue()).decode('utf-8')

    return render_template(
        'calculate.html',
        station_id=station_id,
        start_date=start_date,
        end_date=end_date,
        velocity_table=velocity,
        image=str(image_encoded),
        result_direction_speed=result_direction_speed,
        legend_decoding_dict=legend_decoding_dict,
        storm_recurrence = storm_recurrence
    )


if __name__ == '__main__':
    app.run(port=8080, debug=True)
