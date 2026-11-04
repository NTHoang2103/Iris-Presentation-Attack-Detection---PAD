"""
Module: roi_extractor.py
Mục đích: Bóc tách vùng vành khăn mống mắt (Annular Iris ROI Masking) và triệt tiêu
hoàn toàn hiện tượng Học tắt (Shortcut Learning) do đốm sáng phản xạ đồng tử.
"""

import cv2
import numpy as np


def detect_pupil_and_iris(gray: np.ndarray):
    """
    Tự động phát hiện tâm và bán kính đồng tử (pupil), ước lượng bán kính mống mắt (iris).
    """
    h, w = gray.shape
    blurred = cv2.medianBlur(gray, 9)
    min_r = int(min(h, w) * 0.08)
    max_r = int(min(h, w) * 0.25)

    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=min_r * 2,
        param1=100,
        param2=30,
        minRadius=min_r,
        maxRadius=max_r,
    )

    if circles is not None and len(circles) > 0:
        circles = np.uint16(np.around(circles))
        cx, cy, r_pupil = int(circles[0, 0][0]), int(circles[0, 0][1]), int(circles[0, 0][2])
    else:
        thresh_val = np.percentile(blurred, 5)
        _, mask = cv2.threshold(blurred, thresh_val, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            c = max(contours, key=cv2.contourArea)
            (cx, cy), r_pupil = cv2.minEnclosingCircle(c)
            cx, cy, r_pupil = int(cx), int(cy), int(r_pupil)
        else:
            cx, cy, r_pupil = w // 2, h // 2, int(min(h, w) * 0.15)

    r_iris = int(r_pupil * 2.20)
    return cx, cy, r_pupil, r_iris


def extract_annular_iris_roi(gray: np.ndarray, target_size=(224, 224)):
    """
    Bóc tách vành khăn mống mắt:
    1. Tô đen 100% vùng đồng tử (r <= 1.10 * r_pupil) -> Xóa sạch phản xạ đèn LED NIR.
    2. Cắt giới hạn vành mống mắt ngoài (r <= 2.70 * r_pupil).
    3. Che bớt vùng lông mi/mí mắt trên dưới.
    4. Tăng cường tương phản cục bộ thích nghi CLAHE.
    """
    h, w = gray.shape
    cx, cy, r_pupil, r_iris = detect_pupil_and_iris(gray)

    # Tạo lưới tọa độ
    y_coords, x_coords = np.ogrid[:h, :w]
    dist_sq = (x_coords - cx) ** 2 + (y_coords - cy) ** 2

    r_inner = int(r_pupil * 1.10)
    r_outer = int(r_pupil * 2.70)

    # Mặt nạ vành khăn
    annular_mask = (dist_sq >= r_inner ** 2) & (dist_sq <= r_outer ** 2)

    # Che mi mắt trên & dưới
    eyelid_mask = np.ones((h, w), dtype=bool)
    y_upper = int(cy - 0.85 * r_iris)
    y_lower = int(cy + 0.90 * r_iris)
    if y_upper > 0:
        eyelid_mask[:y_upper, :] = False
    if y_lower < h:
        eyelid_mask[y_lower:, :] = False

    combined_mask = annular_mask & eyelid_mask

    masked_img = np.zeros_like(gray)
    masked_img[combined_mask] = gray[combined_mask]

    # Crop vùng bounding box quanh mống mắt
    margin = int(r_outer * 1.05)
    x1 = max(0, cx - margin)
    y1 = max(0, cy - margin)
    x2 = min(w, cx + margin)
    y2 = min(h, cy + margin)

    roi_crop = masked_img[y1:y2, x1:x2]
    if roi_crop.size == 0 or roi_crop.shape[0] < 10 or roi_crop.shape[1] < 10:
        roi_crop = masked_img

    roi_resized = cv2.resize(roi_crop, target_size, interpolation=cv2.INTER_CUBIC)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    roi_clahe = clahe.apply(roi_resized)

    return roi_clahe, {
        "cx": cx,
        "cy": cy,
        "r_pupil": r_pupil,
        "r_iris": r_iris,
        "bbox": (x1, y1, x2, y2),
        "r_inner": r_inner,
        "r_outer": r_outer,
    }

