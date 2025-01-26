import json
import logging
import os
import sys
import time
from uuid import uuid4

from flask import send_from_directory, Response, send_file
from flask_cors import CORS, cross_origin

from backend.utils import send_file_with_attachment
from backend.worker.image_worker import process_image_in_background

import sqlite3
from flask import Flask, request, jsonify

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

DB_FILE = "map_storage.db"


def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS map (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        conn.commit()


# Funkcje pomocnicze do obsługi bazy danych
def set_task_status(key: str, value: str):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("REPLACE INTO map (key, value) VALUES (?, ?)", (key, value))
        conn.commit()


def get_task_status(key: str):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM map WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row[0] if row else None


def delete_task_status(key: str):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM map WHERE key = ?", (key,))
        conn.commit()


def get_all_statuses():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM map")
        return dict(cursor.fetchall())


init_db()
app = Flask(__name__, static_folder="../frontend/dist")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000  # 16MB
CORS(app)
OUTPUT_FOLDER = "./output/"

IN_PROGRESS: str = "In Progress"
FINISHED: str = "Finished"
FAILED: str = "Failed"

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@app.route('/', methods=['GET'])
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route("/<path:path>", methods=['GET'])
def serve_angular(path):
    try:
        return send_from_directory(app.static_folder, path)
    except:
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
        # difficulty = request.form.get('difficulty', 50)
        color_count = request.form.get('color_count', 3)
        logger.info(color_count)
        logger.info(content_image)
        if not content_image:
            return jsonify({'error': 'Image is required'}), 400

        task_id = str(uuid4())

        task_folder = os.path.join(OUTPUT_FOLDER, task_id)
        os.makedirs(task_folder, exist_ok=True)

        image_path = os.path.join(task_folder, content_image.filename)
        content_image.save(image_path)
        set_task_status(task_id, IN_PROGRESS)
        logger.info(f"Task {task_id} started.")
        process_image_in_background(image_path, color_count, task_id, logger)

        return jsonify({"status": "processing", "task_id": task_id})
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return jsonify({'error': 'Failed to process image'}), 500


@app.route('/api/task_status/<task_id>', methods=['GET'])
@cross_origin()
def task_status(task_id):
    status = get_task_status(task_id)
    if status is None:
        return jsonify({'task_id': task_id, 'status': 'Unknown'}), 404
    return jsonify({'task_id': task_id, 'status': str(status)})


@app.route('/api/download/<task_id>', methods=['GET'])
@cross_origin()
def download(task_id):
    status = get_task_status(task_id)
    if status is None:
        return jsonify({'task_id': task_id, 'status': 'Unknown'}), 404

    if status == FINISHED:
        output_path = f"./output/{task_id}/result.jpg"
        if os.path.exists(output_path):
            return send_file_with_attachment(output_path, 'result.jpg')
        else:
            return jsonify({
                'task_id': task_id,
                'status': 'Output file not found'
            }), 404
    else:
        return jsonify({'task_id': task_id, 'status': f'In Progress: [{status}]'}), 404


@app.route('/api/view/<task_id>', methods=['GET'])
@cross_origin()
def view_image(task_id):
    status = get_task_status(task_id)
    if status is None or status != FINISHED:
        return jsonify({'task_id': task_id, 'status': 'Image not available'}), 404

    output_path = f"./output/{task_id}/result.jpg"
    if os.path.exists(output_path):
        return send_file(output_path, mimetype='image/jpeg')
    else:
        return jsonify({'task_id': task_id, 'status': 'Image file not found'}), 404


@app.route('/api/view/<task_id>/final-image', methods=['GET'])
@cross_origin()
def view_final_image(task_id):
    status = get_task_status(task_id)

    if status is None or status != FINISHED:
        return jsonify({'task_id': task_id, 'status': 'Image not available'}), 404

    output_path = f"./output/{task_id}/final_image.bmp"
    if os.path.exists(output_path):
        return send_file(output_path, mimetype='image/jpeg')
    else:
        return jsonify({'task_id': task_id, 'status': 'Image file not found'}), 404


@app.route('/api/filled-image/<task_id>', methods=['GET'])
@cross_origin()
def download_filled_image(task_id):
    status = get_task_status(task_id)
    if status is None:
        return jsonify({'task_id': task_id, 'status': 'Unknown'}), 404

    if status != FINISHED:
        output_path = f"./output/{task_id}/final_image.jpg"
        if os.path.exists(output_path):
            return send_file_with_attachment(output_path, 'result.jpg')
        else:
            return jsonify({
                'task_id': task_id,
                'status': 'Output file not found'
            }), 404
    else:
        return jsonify({'task_id': task_id, 'status': f'In Progress: [{status}]'}), 404


@app.route("/api/task_status_stream/<task_id>", methods=["GET"])
@cross_origin()
def task_status_stream(task_id):
    def generate():
        while True:
            status = get_task_status(task_id)
            if status is None:
                yield f"data: {json.dumps({'status': 'Unknown'})}\n\n"
                break
            yield f"data: {json.dumps({'status': status})}\n\n"

            if status in ['Finished', 'Failed']:
                break

            time.sleep(1)

    return Response(generate(), content_type='text/event-stream')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
