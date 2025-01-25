import unittest
from unittest.mock import patch, MagicMock, call
import os
import numpy as np
import cv2
from backend.color_segmentation.clustering import kmeans_image_segmentation, get_color_masks
from backend.color_segmentation.color_segmentation import ImageColorSegmentation


class TestImageColorSegmentation(unittest.TestCase):
    @patch("cv2.imread")
    @patch("cv2.cvtColor")
    @patch("backend.color_segmentation.clustering.kmeans_image_segmentation")
    @patch("backend.color_segmentation.clustering.get_color_masks")
    def test_load_image(self, mock_get_color_masks, mock_kmeans, mock_cvtColor, mock_imread):
        # Arrange
        mock_imread.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_cvtColor.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_kmeans.return_value = "kmeans_result"
        mock_get_color_masks.return_value = [np.ones((100, 100), dtype=np.uint8)] * 8

        task_id = "test_task"
        image_path = "test_image.jpg"
        segmenter = ImageColorSegmentation(task_id)

        # Act
        segmenter.load_image(image_path)

        # Assert
        mock_imread.assert_called_once_with(image_path)
        mock_cvtColor.assert_called_once()
        mock_kmeans.assert_called_once_with(mock_cvtColor.return_value, 8)
        mock_get_color_masks.assert_called_once_with("kmeans_result")
        self.assertEqual(len(segmenter.color_masks), 8)

    @patch("os.makedirs")
    @patch("cv2.imwrite")
    def test_save_image(self, mock_imwrite, mock_makedirs):
        # Arrange
        task_id = "test_task"
        output_folder = "./output"
        image_name = "test_image.jpg"
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        segmenter = ImageColorSegmentation(task_id)
        segmenter.OUTPUT_FOLDER = output_folder

        # Act
        segmenter.save_image(image_name, image)

        # Assert
        expected_output_path = os.path.join(output_folder, task_id, image_name)
        mock_makedirs.assert_called_once_with(os.path.join(output_folder, task_id), exist_ok=True)
        mock_imwrite.assert_called_once_with(expected_output_path, image)

    @patch("cv2.erode")
    def test_get_edges(self, mock_erode):
        # Arrange
        mock_erode.return_value = np.zeros((100, 100), dtype=np.uint8)
        mask = np.ones((100, 100), dtype=np.uint8)
        segmenter = ImageColorSegmentation(task_id="test_task")

        # Act
        edges = segmenter.get_edges(mask)

        # Assert
        mock_erode.assert_called_once_with(mask, 3, iterations=1)
        np.testing.assert_array_equal(edges, mask - mock_erode.return_value)

    @patch("cv2.cvtColor")
    @patch("cv2.add")
    def test_process(self, mock_add, mock_cvtColor):
        # Arrange
        task_id = "test_task"
        segmenter = ImageColorSegmentation(task_id)
        segmenter.image = np.zeros((100, 100, 3), dtype=np.uint8)
        segmenter.images = [np.ones((100, 100), dtype=np.uint8)] * 2

        mock_cvtColor.side_effect = [np.zeros((100, 100, 3), dtype=np.uint8)] * 4
        mock_add.return_value = np.zeros((100, 100, 3), dtype=np.uint8)

        with patch.object(segmenter, "save_image") as mock_save_image:
            # Act
            segmenter.process()

            # Assert
            self.assertEqual(mock_cvtColor.call_count, 4)
            self.assertEqual(mock_add.call_count, 2)
            self.assertEqual(mock_save_image.call_count, 3)

    @patch("cv2.imread")
    def test_load_image_invalid_path(self, mock_imread):
        # Arrange
        mock_imread.return_value = None
        task_id = "test_task"
        segmenter = ImageColorSegmentation(task_id)

        # Act & Assert
        with self.assertRaises(Exception):
            segmenter.load_image("invalid_path.jpg")


    def development_test(self):
        image_color_segmentation = ImageColorSegmentation(task_id="test_task")
        image_color_segmentation.load_image("test_image.jpg")



        self.assertIsInstance(image_color_segmentation, ImageColorSegmentation)


if __name__ == "__main__":
    unittest.main()
