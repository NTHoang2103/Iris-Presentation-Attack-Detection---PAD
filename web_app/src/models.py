"""
Module: models.py
Mục đích: Định nghĩa kiến trúc mạng ResNet-50 cho bài toán Phát hiện Tấn công Giả mạo Mống mắt (Iris PAD).
Khớp chính xác với cấu trúc trọng số huấn luyện từ iris-pad_2.ipynb:
- model.fc = nn.Sequential(nn.Dropout(0.5), nn.Linear(2048, 2))
- 2 Classes: 0: Spoof, 1: Live
"""

import os
import torch
import torch.nn as nn
from torchvision import models


def build_resnet50_pad(pretrained: bool = False, num_classes: int = 2) -> nn.Module:
    """
    Xây dựng kiến trúc ResNet-50 khớp với checkpoint V2:
    - Backbone: ResNet-50
    - Head: Dropout(0.5) -> Linear(2048, 2)
    """
    weights = models.ResNet50_Weights.DEFAULT if pretrained else None
    model = models.resnet50(weights=weights)

    in_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(p=0.5),
        nn.Linear(in_features, num_classes),
    )
    return model


def load_pad_model(weights_path: str, device: torch.device = None) -> nn.Module:
    """
    Nạp trọng số đã huấn luyện từ file .pth hoặc .zip.
    """
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = build_resnet50_pad(pretrained=False, num_classes=2)

    if not os.path.exists(weights_path):
        raise FileNotFoundError(f"Không tìm thấy file trọng số tại: {weights_path}")

    state_dict = torch.load(weights_path, map_location=device)
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()
    return model

