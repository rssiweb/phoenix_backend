from flask import Flask, jsonify
import json

app = Flask(__name__)

@app.route('/')
def index():
	return jsonify(dict(content='Hello World'))

if __name__=='__main__':
	app.run(debug=True)
