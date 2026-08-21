import pyautogui, mss
import cv2
import numpy as np
import os
import time

print("pyautogui:", pyautogui.size())  # (width, height)



def custom_nms(boxes, overlap_thresh=0.3):
    """
    Pure NumPy implementation of Non-Maximum Suppression.
    Collapses multiple overlapping boxes down into single distinct predictions.
    """
    if len(boxes) == 0:
        return []

    boxes = np.array(boxes, dtype=float)
    pick = []

    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]
    scores = boxes[:, 4]  # Match confidence scores

    area = (x2 - x1) * (y2 - y1)
    idxs = np.argsort(scores)  # Sort by confidence score (lowest to highest)

    while len(idxs) > 0:
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)

        # Find the intersection coordinates
        xx1 = np.maximum(x1[i], x1[idxs[:last]])
        yy1 = np.maximum(y1[i], y1[idxs[:last]])
        xx2 = np.minimum(x2[i], x2[idxs[:last]])
        yy2 = np.minimum(y2[i], y2[idxs[:last]])

        # Calculate width and height of the intersection box
        w = np.maximum(0, xx2 - xx1)
        h = np.maximum(0, yy2 - yy1)

        # Compute the ratio of overlap
        overlap = (w * h) / area[idxs[:last]]

        # Delete all indexes that have a high overlap with the box we just picked
        idxs = np.delete(idxs, np.concatenate(([last], np.where(overlap > overlap_thresh)[0])))

    return boxes[pick].tolist()


def read_numbers_via_edge_matching(current_frame, templates_dir="images", match_threshold=0.3):
    """
    Finds and reads a sequence of digits inside a larger image using edge-based template matching.
    
    :param big_img_path: Path to the main image containing the numbers.
    :param templates_dir: Directory containing '0.png', '1.png', etc.
    :param match_threshold: Minimum confidence score to accept an edge match.
    :return: The read number string.
    """
    # 1. Load the big image and convert to grayscale
    # big_gray = cv2.cvtColor(big_img, cv2.COLOR_BGR2GRAY)
    big_gray = current_frame
    
    # 2. Extract edge map of the big image (strips background fills/colors)
    big_edges = cv2.Canny(big_gray, 50, 150)
    
    all_detections = []
    
    # 3. Loop through digit templates 0 to 9
    for digit in range(10):
        template_path = os.path.join(templates_dir, f"{digit}.png")
        
        # Skip if the file doesn't exist in the directory
        if not os.path.exists(template_path):
            continue
            
        template_img = cv2.imread(template_path)
        template_gray = cv2.cvtColor(template_img, cv2.COLOR_BGR2GRAY)
        
        # scaling number images
        scale_factor = 1
        h, w = template_gray.shape[:2]
        new_size = (int(w * scale_factor), int(h * scale_factor))
        
        # Use INTER_CUBIC if scaling up, INTER_AREA if scaling down
        interp = cv2.INTER_CUBIC if scale_factor > 1.0 else cv2.INTER_AREA
        template_gray = cv2.resize(template_gray, new_size, interpolation=interp)

        # Get edge map of the specific digit template
        template_edges = cv2.Canny(template_gray, 50, 150)
        h, w = template_edges.shape[:2]
        
        # Run template matching on the edge outlines
        result_matrix = cv2.matchTemplate(big_edges, template_edges, cv2.TM_CCOEFF_NORMED)
        
        # Find all coordinates crossing our confidence threshold
        y_coords, x_coords = np.where(result_matrix >= match_threshold)
        
        for (x, y) in zip(x_coords, y_coords):
            score = result_matrix[y, x]
            # Store box coordinates along with confidence score and the actual digit value
            all_detections.append([x, y, x + w, y + h, score, digit])
            
    # 4. Filter out duplicate ghost boxes using Non-Maximum Suppression
    final_digits = custom_nms(all_detections, overlap_thresh=0.3)
    
    # 5. Crucial Step: Sort the discovered digits from Left to Right (by their X1 coordinate)
    final_digits.sort(key=lambda box: box[0])
    
    # 6. Extract the digit values and join them into a final string
    detected_number_string = "".join([str(int(box[5])) for box in final_digits])
    
    return detected_number_string





with mss.mss() as sct:
    
    frame = np.array(sct.grab(sct.monitors[1]))
    print("current_frame:", frame.shape[1], frame.shape[0])  # width, height
    capture_interval = 3
    monitor = sct.monitors[1]
    counter = 0
    last_capture = 0

    while True:
        now = time.time()
        if now - last_capture >= capture_interval:
            current_frame = cv2.cvtColor(np.array(sct.grab(monitor)), cv2.COLOR_BGRA2BGR)
            last_capture = now
            current_frame_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)

            # storage gold
            x1, y1 = (2802, 415)
            x2, y2 = (3040, 456)
            big_gray = current_frame_gray[y1:y2, x1:x2]
            result_string = read_numbers_via_edge_matching(big_gray)
            print(result_string)

            # # storage elixir
            x1, y1 = (2802, 520)
            x2, y2 = (3040, 567)
            big_gray = current_frame_gray[y1:y2, x1:x2]
            result_string = read_numbers_via_edge_matching(big_gray)
            print(result_string)

            # # storage dark elixir
            x1, y1 = (2875, 628)
            x2, y2 = (3040, 674)
            big_gray = current_frame_gray[y1:y2, x1:x2]
            result_string = read_numbers_via_edge_matching(big_gray)
            print(result_string)


            print(counter)
            counter += 1
        time.sleep(0.5)
            