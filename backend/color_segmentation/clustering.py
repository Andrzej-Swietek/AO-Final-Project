from dataclasses import dataclass

import cv2
import cv2 as cv
import numpy as np


@dataclass
class KMeansResult:
    segmented_image: np.ndarray[np.uint8]  # shape (H, W, 3)
    labels: np.ndarray[np.int32]  # shape (H*W,)
    centers: np.ndarray[np.uint8]  # shape (K, 3)


def find_optimal_k(
        image: np.ndarray[np.uint8],
        k_min: int = 3,
        k_max: int = 10
) -> int:
    """
    Znajduje optymalną liczbę klastrów 'k' dla obrazu
    metodą łokcia, testując kolejne wartości w przedziale [k_min, k_max].
    """
    # Spłaszczamy i konwertujemy piksele na float32 (tak samo jak w kmeans_image_segmentation)
    pixels = image.reshape((-1, 3))
    pixels = np.float32(pixels)

    # Kryteria k-meansa (możesz dostosować np. liczbę iteracji)
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 10, 1.0)

    compactness_values = []
    k_values = list(range(k_min, k_max + 1))

    for k in k_values:
        compactness, _, _ = cv.kmeans(
            data=pixels,
            K=k,
            bestLabels=None,
            criteria=criteria,
            attempts=10,
            flags=cv.KMEANS_RANDOM_CENTERS
        )
        compactness_values.append(compactness)

    # Metoda łokcia: proste wykrywanie "załamania" w wykresie
    # ------------------------------------------------------
    # 1) Możemy znaleźć punkt, dla którego względny spadek 'compactness'
    #    między k i k+1 jest najmniejszy (lub największy).
    # 2) Możemy użyć bardziej zaawansowanej metody, np. liczenia odległości
    #    punktu od prostej łączącej pierwszą i ostatnią wartość.
    #
    # Poniżej - podstawowa metoda "różnicy przyrostów":

    # Liczymy różnice przyrostowe: delta(i) = compactness(i) - compactness(i+1)
    # Potem jeszcze patrzymy jak szybko ta różnica spada.

    # Przykładowe podejście: szukamy "maksimum drugiej różnicy"
    # (czyli moment, w którym spadek inertii zaczyna gwałtownie wyhamowywać).

    deltas = np.diff(compactness_values)  # różnice pomiędzy kolejnymi compactness
    # Druga różnica (różnica różnic)
    second_deltas = np.diff(deltas)

    # Ponieważ second_deltas jest krótsze o 1 niż deltas,
    # bierzemy indeks, który powoduje największą dodatnią "drugą różnicę".
    # Indeks w second_deltas odnosi się do k_values[i + 1].
    if len(second_deltas) > 0:
        best_idx = np.argmax(second_deltas)
        best_k = k_values[best_idx + 1]
    else:
        # Jeśli z jakichś powodów nie da się policzyć (np. k_min == k_max),
        # to weźmy minimalną wartość compactness
        best_idx = np.argmin(compactness_values)
        best_k = k_values[best_idx]

    return best_k


def kmeans_image_segmentation(image: np.ndarray[np.uint8], k: int) -> KMeansResult:

    pixels = image.reshape((-1, 3))

    pixels = np.float32(pixels)

    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 10, 1.0)

    _, labels, centers = cv.kmeans(
        pixels, k, None, criteria, 10, cv.KMEANS_RANDOM_CENTERS
    )

    centers = np.uint8(centers)

    segmented_pixels = centers[labels.flatten()]

    segmented_image = segmented_pixels.reshape(image.shape)

    return KMeansResult(segmented_image=segmented_image, labels=labels, centers=centers)


def get_color_masks(result: KMeansResult) -> list[np.ndarray[np.uint8]]:
    h, w = result.segmented_image.shape[:2]
    labels = result.labels.reshape((h, w))
    masks: list[np.ndarray[np.uint8]] = []
    for cluster_idx in range(len(result.centers)):
        mask = (labels == cluster_idx).astype(np.uint8) * 255
        masks.append(mask)

    return masks


def remove_distortions(binary_image: np.ndarray[np.uint8], power: int = 5) -> np.ndarray[np.uint8]:
    result = cv2.erode(binary_image, np.ones((power, power), np.uint8), iterations=1)
    result = cv2.dilate(result, np.ones((power, power), np.uint8), iterations=1)
    return result


def get_edges(mask: np.ndarray):
    return cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=1) - mask # cv2.erode(mask, np.ones((3, 3), np.uint8), iterations=1)


def combine_edges(edges: list[np.ndarray[np.uint8]]) -> np.ndarray[np.uint8]:

    combined = np.zeros_like(edges[0], dtype=np.uint8)
    for edge in edges:
        combined = cv.add(combined, edge)

    combined[combined > 255] = 255

    return combined


def shrink_to_points(binary_image: np.ndarray[np.uint8]) -> np.ndarray[np.uint8]:
    img = binary_image.copy()
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))

    while True:
        prev = img.copy()
        img = cv2.erode(img, kernel)
        if cv2.countNonZero(img ^ prev) == 0:
            break

    return prev


def combine_rgb_images(images: list[np.ndarray[np.uint8]]) -> np.ndarray[np.uint8]:

    combined = np.zeros_like(images[0], dtype=np.uint16)  # Use uint16 to avoid overflow during addition
    for image in images:
        combined += image  # Add pixel values

    combined = np.clip(combined, 0, 255).astype(np.uint8)  # Clip values to 0-255 and convert back to uint8
    return combined


def sharpen_image(image: np.ndarray[np.uint8], k: int = 3) -> np.ndarray[np.uint8]:
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened_image = cv2.filter2D(image, -1, kernel)
    # filter_matrix = make_filter_matrix(k)
    # filtered_image = cv2.filter2D(src=image, ddepth=-1, kernel=filter_matrix)
    return sharpened_image


def make_filter_matrix(k: int) -> np.ndarray[np.float32]:
    if k % 2 == 0:
        raise ValueError("Filter size 'k' must be odd.")
    filter_matrix = -1 * np.ones((k, k), dtype=np.float32)
    center = k // 2
    filter_matrix[center, center] = k**2 - 1
    return filter_matrix


def find_inner_points_for_objects(bin_image: np.ndarray[np.uint8]) -> list[tuple[int, int, int]]:
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(bin_image, connectivity=8)

    bin01 = (bin_image > 0).astype(np.uint8)
    dist_map = cv2.distanceTransform(bin01, cv2.DIST_L2, 3)

    points = []
    for label_idx in range(1, num_labels):
        masked_dist = dist_map.copy()
        masked_dist[labels != label_idx] = 0
        # Znajdź maksimum w "masked_dist"
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(masked_dist)
        # maxLoc jest (x, y) => (kolumna, wiersz)
        r, c = min(max(maxLoc[1], 5), bin_image.shape[0] - 5), min(max(maxLoc[0], 5), bin_image.shape[1] - 5)
        area = stats[label_idx, cv2.CC_STAT_AREA]
        points.append((r, c, area))

    return points


def scale_image(og_image: np.ndarray, size: int = 512) -> np.ndarray:
    original_height, original_width = og_image.shape[:2]

    if original_width > original_height:
        scale = size / original_width
        new_width = size
        new_height = int(original_height * scale)
    else:
        scale = size / original_height
        new_height = size
        new_width = int(original_width * scale)

    resized_image = cv2.resize(og_image, (new_width, new_height))
    return resized_image


def put_text_with_center_at(image: np.ndarray, text: str, x: int, y: int, color: tuple[int, int, int]):
    text = str(text)
    font_face = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.3
    thickness = 1
    (x, y) = (x, y)
    (text_width, text_height), baseline = cv2.getTextSize(text, font_face, font_scale, thickness)
    text_x = x - text_width // 2
    text_y = y + text_height // 2
    cv2.putText(image, text, (text_x, text_y), font_face, font_scale, color, thickness)
