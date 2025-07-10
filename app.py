import requests
from flask import Flask

app = Flask(__name__)

@app.route('/next_buses/<stop_code>')
def next_buses(stop_code):
    url = f'https://api.tfl.gov.uk/StopPoint/{stop_code}/Arrivals'

    try:
        response = requests.get(url)
        response.raise_for_status()
        arrivals = response.json()

        buses = []
        for bus in arrivals:
            buses.append({
                'lineName': bus.get('lineName'),
                'destinationName': bus.get('destinationName'),
                'timeToStation_sec': bus.get('timeToStation'),  # seconds until arrival
                'expectedArrival': bus.get('expectedArrival'),
            })

        buses.sort(key=lambda x: x['timeToStation_sec'])
        return buses[:5]

    except requests.exceptions.RequestException as e:
        return {'error': 'Failed to fetch data from TfL API', 'details': str(e)}, 500

@app.route('/')
def index():
    return 'Hello, Flask!'

if __name__ == '__main__':
    app.run()