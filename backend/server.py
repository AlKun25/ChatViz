from sentiment_analysis import sentiment_analysis
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

@app.route('/endpoint', methods=['GET'])
def get_endpoint():
    input_string = request.args.get('input_string', '')

    if input_string is None or input_string == '':
        return jsonify({'error': 'Input string is missing'}), 400

    # Process the input_string as needed
    result = str(sentiment_analysis(input_string))

    return result

if __name__ == '__main__':
    app.run(debug=True, port=8000)
