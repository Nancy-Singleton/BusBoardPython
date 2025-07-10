from flask import Flask

app = Flask(__name__)

@app.route('/next_buses/<stop_code>')
def next_buses(stop_code):
    dummy_buses = ['1001', '1002', '1003']
    return dummy_buses

@app.route('/')
def index():
    return 'Hello, Flask!'

if __name__ == '__main__':
    app.run()