import os
import sys

from backend.color_segmentation.color_segmentation import ImageColorSegmentation

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def process_image_in_background(content_image_path: str, color_count: int, task_id: str, logger, redis_client):
    try:
        color_segmentation = ImageColorSegmentation(task_id, color_count)
        color_segmentation.load_image(content_image_path)
        color_segmentation.process_image()

        logger.info(f"Processing image for task {task_id} with color count {color_count}...")

        redis_client.set(task_id, 'Finished')
        logger.info(f"Task {task_id} completed.")

    except Exception as e:
        redis_client.set(task_id, 'Failed')
        logger.error(f"Task {task_id} failed with error: {e}")
    finally:
        if redis_client:
            redis_client.close()
