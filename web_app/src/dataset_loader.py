"""
Module: dataset_loader.py
Mục đích: Quản lý nạp dữ liệu lai ghép (Hybrid Dataset) đa kịch bản (Live, Syn, Print, Replay)
theo nguyên tắc phân chia độc lập đối tượng (Subject-Independent Split).
"""

import os
import glob
import random
import cv2
import numpy as np
import torch
from torch.utils.data import Dataset
from torchvision import transforms

from src.roi_extractor import extract_annular_iris_roi
from src.spoof_generator import simulate_print_attack, simulate_replay_attack


class IrisPADHybridDataset(Dataset):
    """
    Dataset lai ghép chuẩn cho Iris PAD:
    - Loại 1: Live (Bona Fide)
    - Loại 2: Synthetic Spoof
    - Loại 3: Simulated Print Attack (tạo động từ Live)
    - Loại 4: Simulated Replay Attack (tạo động từ Live)
    """

    def __init__(self, records, transform=None):
        self.records = records
        self.transform = transform

    def __len__(self):
        return len(self.records)

    def __getitem__(self, idx):
        path, label, attack_type = self.records[idx]
        img_gray = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img_gray is None:
            img_gray = np.zeros((280, 320), dtype=np.uint8)

        if attack_type == "print":
            img_gray = simulate_print_attack(img_gray, seed=idx)
        elif attack_type == "replay":
            img_gray = simulate_replay_attack(img_gray, seed=idx)

        roi, _ = extract_annular_iris_roi(img_gray, target_size=(224, 224))
        roi_rgb = cv2.cvtColor(roi, cv2.COLOR_GRAY2RGB)

        if self.transform is not None:
            tensor = self.transform(roi_rgb)
        else:
            tensor = torch.from_numpy(roi_rgb.transpose(2, 0, 1)).float() / 255.0

        return tensor, torch.tensor(label, dtype=torch.float32), attack_type


def get_default_transform():
    return transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

