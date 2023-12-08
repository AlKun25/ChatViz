from flask import Flask, request, jsonify
from sentiment_analysis import sentiment_analysis

app = Flask(__name__)

@app.route('/endpoint', methods=['GET'])
def get_endpoint():
    input_string = request.args.get('input_string', '')

    if input_string is None:
        return jsonify({'error': 'Input string is missing'}), 400

    # Process the input_string as needed
    result = str(sentiment_analysis(input_string))

    return result

if __name__ == '__main__':
    app.run(debug=True, port=8000)
