"""
Module: spoof_generator.py
Mục đích: Giả lập các cuộc tấn công vật lý Print Attack (in ấn) và Replay Attack (màn hình)
dựa trên các mô hình quang học và biến dạng vật lý thực tế.
"""

import cv2
import numpy as np


def simulate_print_attack(img_gray: np.ndarray, seed: int = None) -> np.ndarray:
    """
    Giả lập tấn công in ấn (Print Attack):
    - Làm mờ biên cạnh do tán xạ quang học trên giấy (Gaussian blur).
    - Giảm dải tương phản động (Dynamic range compression).
    - Thêm nhiễu hạt in ấn (Halftone print grain noise).
    """
    if seed is not None:
        np.random.seed(seed)
    
    # 1. Làm mờ nhẹ
    ksize = np.random.choice([3, 5])
    blurred = cv2.GaussianBlur(img_gray, (ksize, ksize), 0.8)
    
    # 2. Giảm tương phản động
    low_bound = np.random.randint(15, 30)
    high_bound = np.random.randint(220, 240)
    compressed = np.clip((blurred.astype(np.float32) / 255.0) * (high_bound - low_bound) + low_bound, 0, 255)
    
    # 3. Thêm nhiễu hạt in
    noise = np.random.normal(0, 4.5, compressed.shape)
    printed = np.clip(compressed + noise, 0, 255).astype(np.uint8)
    
    return printed


def simulate_replay_attack(img_gray: np.ndarray, seed: int = None) -> np.ndarray:
    """
    Giả lập tấn công phát lại qua màn hình (Replay Attack):
    - Nhiễu sọc tần số cao (Moiré pattern) từ ma trận pixel màn hình.
    - Vệt lóa phản xạ gương phẳng (Specular glare reflection).
    - Méo gamma màn hình hiển thị.
    """
    if seed is not None:
        np.random.seed(seed)
        
    h, w = img_gray.shape
    float_img = img_gray.astype(np.float32)
    
    # 1. Méo Gamma
    gamma = np.random.uniform(1.2, 1.45)
    screen_img = 255.0 * np.power(float_img / 255.0, gamma)
    
    # 2. Tạo sọc giao thoa chu kỳ Moiré
    freq_x = np.random.uniform(0.12, 0.25)
    freq_y = np.random.uniform(0.08, 0.18)
    x_idx, y_idx = np.meshgrid(np.arange(w), np.arange(h))
    moire = 6.0 * np.sin(2 * np.pi * freq_x * x_idx + 2 * np.pi * freq_y * y_idx)
    screen_img = np.clip(screen_img + moire, 0, 255)
    
    # 3. Vệt lóa phản xạ màn hình
    glare_cx = np.random.randint(int(w * 0.25), int(w * 0.75))
    glare_cy = np.random.randint(int(h * 0.25), int(h * 0.75))
    dist_sq = (x_idx - glare_cx) ** 2 + (y_idx - glare_cy) ** 2
    glare_r = np.random.randint(18, 35)
    glare = 50.0 * np.exp(-dist_sq / (2.0 * (glare_r ** 2)))
    screen_img = np.clip(screen_img + glare, 0, 255).astype(np.uint8)
    
    return screen_img

