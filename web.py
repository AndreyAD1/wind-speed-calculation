import base64
from datetime import datetime, timedelta

from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap

from databases import check_db, WindIndicator
from calculations import get_calculation_results
from constants import MONTH_LIST


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
    storm_probability = form['storm_recurrence']
    selected_months = []
    for month_number in MONTH_LIST:
        try:
            month_status = form[month_number]
        except:
            continue
        selected_months.append(month_number)
    start_date = datetime.strptime(start_date, '%d.%m.%Y')
    # включаем в запрос последний день в интервале
    end_date = datetime.strptime(end_date, '%d.%m.%Y') + timedelta(days=1)
    print(selected_months)

    # TODO сделать проверку, чтобы всегда storm_recurrence > 0
    # перехожу от обеспеченности в % к количеству лет
    storm_recurrence = 100/float(storm_probability)

    check_db(station_id, start_date, end_date)
# TODO надо добавить в фильтр нужные месяцы
    data = WindIndicator.query.filter(WindIndicator.weather_station_id == station_id,
                                      WindIndicator.local_date <= end_date,
                                      WindIndicator.local_date >= start_date).all()

    velocity, result_direction_speed, image_buf, legend_decoding_dict = get_calculation_results(
        data, storm_recurrence, start_date, end_date
    )
    image_encoded = base64.b64encode(image_buf.getvalue()).decode('utf-8')

    return render_template(
        'calculate.html',
        station_id=station_id,
        start_date=start_date,
        end_date=end_date - timedelta(days=1),
        velocity_table=velocity,
        image=str(image_encoded),
        result_direction_speed=result_direction_speed,
        legend_decoding_dict=legend_decoding_dict,
        storm_probability=storm_probability
    )


if __name__ == '__main__':
    app.run(port=8080, debug=True)
