from CoreEngine.EventBus import command_line
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

@app.route('/task/<int:uuid>', methods=['POST'])
def execute_tasks(uuid):
    task_list = request.json['TaskList']
    multi_thread = request.json['MultiThread']
    response = command_line(uuid, task_list, multi_thread)
    print("jiarui", response)

    if response is None:
        abort(400, 'Bad Request. Please check log for further information')

    return jsonify(response)


@app.route('/health/', methods=['POST', 'GET'])
def health_check():
    response = ["status: success"]

    if response is None:
        abort(400, 'Bad Request.')

    return jsonify(response)

@app.route('/', methods=['POST', 'GET'])
def load_balance_check():
    response = ["status: balance checking success"]

    if response is None:
        abort(400, 'Bad Request.')

    return jsonify(response)

if __name__ == '__main__':
    app.run(threaded=True, port=5000)
