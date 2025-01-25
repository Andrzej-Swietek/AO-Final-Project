from flask import Flask, send_from_directory, jsonify, request, Response
from flask_cors import CORS, cross_origin
from uuid import uuid4
import redis
import os
import sys
import json
import time
import logging
from rq import Queue

from utils import send_file_with_attachment, encode_image
from worker.image_worker import process_image_in_background

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

app = Flask(__name__, static_folder="static")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000  # 16MB
CORS(app)
OUTPUT_FOLDER = "./output/"

# Set up redis
redisHost = os.getenv("REDIS_HOST", "127.0.0.1")
redis_client = redis.Redis(host=redisHost, port=6379, db=0)
queue = Queue(connection=redis_client)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
@cross_origin()
def serve_frontend(path):
    if path and path.startswith("static"):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api", methods=["GET"])
@cross_origin()
def hello():
    return jsonify({"message": "Hello from Flask!"})


@app.route("/api/process", methods=["POST"])
@cross_origin()
def process_image():
    try:
        content_image = request.files['image']
        difficulty = request.form.get('difficulty', 50)
        logger.info(content_image)
        if not content_image:
            return jsonify({'error': 'Image is required'}), 400

        task_id = str(uuid4())  

        task_folder = os.path.join(OUTPUT_FOLDER, task_id)
        os.makedirs(task_folder, exist_ok=True)

        image_path = os.path.join(task_folder, content_image.filename)
        content_image.save(image_path)
        if not redis_client:
            return jsonify({ "status": "no redis" }),500
        redis_client.set(task_id, 'In Progress') 
        # job = queue.enqueue(process_image_in_background, content_image, difficulty, task_id)
        logger.info(f"Task {task_id} started.")
        process_image_in_background(image_path, difficulty, task_id, logger, redis_client)

        return jsonify({"status": "processing", "task_id": task_id})
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return jsonify({'error': 'Failed to process image'}), 500


@app.route('/api/task_status/<task_id>', methods=['GET'])
@cross_origin()
def task_status(task_id):
    status = redis_client.get(task_id)
    if status is None:
        return jsonify({'task_id': task_id, 'status': 'Unknown'}), 404
    return jsonify({'task_id': task_id, 'status': status.decode('utf-8')})


@app.route('/api/download/<task_id>', methods=['GET'])
@cross_origin()
def download(task_id):
    task = redis_client.get(task_id)
    task_status_str = task.decode('utf-8')
    if task is None:
        return jsonify({'task_id': task_id, 'status': 'Unknown'}), 404

    if task_status_str in ['Finished', 'Completed']:
        output_path = f"./output/{task_id}/result.jpg"
        if os.path.exists(output_path):
            return send_file_with_attachment(output_path, 'result.jpg')
        else:
            return jsonify({
                'task_id': task_id,
                'status': 'Output file not found'
            }), 404
    else:
        return jsonify({'task_id': task_id, 'status': f'In Progress: [{task_status_str}]'}), 404


@app.route('/api/download-filled-image/<task_id>', methods=['GET'])
@cross_origin()
def download(task_id):
    task = redis_client.get(task_id)
    task_status_str = task.decode('utf-8')
    if task is None:
        return jsonify({'task_id': task_id, 'status': 'Unknown'}), 404

    if task_status_str in ['Finished', 'Completed']:
        output_path = f"../output/{task_id}/final_image.jpg"
        if os.path.exists(output_path):
            return send_file_with_attachment(output_path, 'result.jpg')
        else:
            return jsonify({
                'task_id': task_id,
                'status': 'Output file not found'
            }), 404
    else:
        return jsonify({'task_id': task_id, 'status': f'In Progress: [{task_status_str}]'}), 404


@app.route("/api/task_status_stream/<task_id>", methods=["GET"])
def task_status_stream(task_id):
    def generate():
        while True:
            status = redis_client.get(task_id)
            if status is None:
                yield f"data: {json.dumps({'status': 'Unknown'})}\n\n"
                break
            status = status.decode('utf-8')
            yield f"data: {json.dumps({'status': status})}\n\n"
            
            if status in ['Finished', 'Failed']:
                break

            time.sleep(1)

    return Response(generate(), content_type='text/event-stream')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
