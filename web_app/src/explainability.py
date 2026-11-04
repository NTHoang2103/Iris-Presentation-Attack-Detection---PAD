"""
Module: explainability.py
Mục đích: Trích xuất bản đồ nhiệt Grad-CAM (Gradient-weighted Class Activation Mapping)
giải thích vùng mạng ResNet-50 tập trung chú ý khi ra quyết định Liveness.
"""

import cv2
import numpy as np
import torch
import torch.nn.functional as F


class GradCAM:
    """
    Grad-CAM cho mô hình phân loại mống mắt ResNet-50.
    Target layer mặc định: model.layer4[-1] (tầng tích chập sâu nhất).
    """

    def __init__(self, model: torch.nn.Module, target_layer: torch.nn.Module = None):
        self.model = model
        self.target_layer = target_layer if target_layer is not None else model.layer4[-1]
        self.gradient = None
        self.activation = None

        self.target_layer.register_forward_hook(self._save_activation)
        self.target_layer.register_full_backward_hook(self._save_gradient)

    def _save_activation(self, module, input, output):
        self.activation = output.detach()

    def _save_gradient(self, module, grad_input, grad_output):
        self.gradient = grad_output[0].detach()

    def generate_heatmap(self, input_tensor: torch.Tensor, class_idx: int = 1) -> np.ndarray:
        """
        Sinh bản đồ nhiệt chuẩn hóa từ [0, 1] cho ảnh đầu vào.
        class_idx: 1 (Live), 0 (Spoof)
        """
        self.model.eval()
        self.model.zero_grad()

        output = self.model(input_tensor)
        if output.shape[1] > 1:
            score = output[0, class_idx]
        else:
            score = output[0, 0]

        score.backward(retain_graph=True)

        gradients = self.gradient
        activations = self.activation

        weights = torch.mean(gradients, dim=(2, 3), keepdim=True)
        cam = torch.sum(weights * activations, dim=1, keepdim=True)
        cam = F.relu(cam)

        cam = cam.squeeze().cpu().numpy()
        cam_min, cam_max = np.min(cam), np.max(cam)
        if cam_max > cam_min:
            cam = (cam - cam_min) / (cam_max - cam_min)
        else:
            cam = np.zeros_like(cam)

        return cam


def overlay_heatmap_on_roi(roi_gray: np.ndarray, heatmap: np.ndarray, alpha: float = 0.5) -> np.ndarray:
    """
    Chồng bản đồ nhiệt màu JET lên ảnh ROI mống mắt.
    """
    h, w = roi_gray.shape[:2]
    heatmap_resized = cv2.resize(heatmap, (w, h), interpolation=cv2.INTER_LINEAR)
    heatmap_colored = cv2.applyColorMap(np.uint8(255 * heatmap_resized), cv2.COLORMAP_JET)

    if len(roi_gray.shape) == 2:
        roi_rgb = cv2.cvtColor(roi_gray, cv2.COLOR_GRAY2RGB)
    else:
        roi_rgb = roi_gray

    overlay = cv2.addWeighted(roi_rgb, 1.0 - alpha, heatmap_colored, alpha, 0)
    return overlay

