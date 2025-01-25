import unittest
from unittest.mock import patch, MagicMock, call
import os
import numpy as np
import cv2
from backend.color_segmentation.clustering import kmeans_image_segmentation, get_color_masks
from backend.color_segmentation.color_segmentation import ImageColorSegmentation


class TestImageColorSegmentation(unittest.TestCase):

    def test_development(self):
        image_color_segmentation = ImageColorSegmentation(task_id="test_task")
        image_color_segmentation.load_image("../example_images/img.jpg")



if __name__ == "__main__":
    unittest.main()
