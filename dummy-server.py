from flask import Flask, jsonify
import pandas as pd

app = Flask(__name__)
data = pd.read_csv('weatherHistory.csv')
current_index = 0

@app.route('/')
def get_next_row():
    global current_index
    if current_index < len(data):
        row = data.iloc[current_index].to_dict()
        current_index += 1
        return jsonify(row)
    else:
        return jsonify(error='No more data available'), 404

if __name__ == '__main__':
    app.run(debug=True)
