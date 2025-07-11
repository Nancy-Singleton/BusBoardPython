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

@app.route('/next_buses_by_postcode/<postcode>')
def next_buses_by_postcode(postcode):
    postcode_url = f'https://api.postcodes.io/postcodes/{postcode}'

    try:
        postcode_response = requests.get(postcode_url)
        postcode_response.raise_for_status()
        postcode_data = postcode_response.json()

        if postcode_data['status'] != 200 or not postcode_data.get('result'):
            return {'error': 'Invalid postcode'}, 400

        lat = postcode_data['result']['latitude']
        lng = postcode_data['result']['longitude']

    except requests.exceptions.RequestException as e:
        return {'error': 'Failed to fetch location from Postcodes.io', 'details': str(e)}, 500

    tfl_url = (
        f'https://api.tfl.gov.uk/StopPoint'
        f'?lat={lat}&lon={lng}&stopTypes=NaptanPublicBusCoachTram&radius=300&modes=bus'
    )

    try:
        stop_response = requests.get(tfl_url)
        stop_response.raise_for_status()
        stop_data = stop_response.json()

        stop_points = stop_data.get('stopPoints', [])
        stop_points_sorted = sorted(stop_points, key=lambda s: s.get('distance', float('inf')))
        nearest = stop_points_sorted[:2]

        for idx, stop in enumerate(nearest):
            print(f"[{idx+1}] {stop.get('commonName')} - ID: {stop.get('naptanId')}")

    except requests.exceptions.RequestException as e:
        return {'error': 'Failed to fetch nearby stop points from TfL', 'details': str(e)}, 500

    all_buses = []
    for stop in nearest:
        buses = next_buses(stop.get('naptanId'))
        all_buses.extend(buses)

    all_buses.sort(key=lambda b: b['timeToStation_sec'])
    return all_buses[:5]

@app.route('/')
def index():
    return 'Hello, Flask!'

if __name__ == '__main__':
    app.run()