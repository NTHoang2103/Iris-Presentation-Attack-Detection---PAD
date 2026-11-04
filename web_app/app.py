"""
reIris Biometric PAD Lab - Standalone Web App (FastAPI)
Được tối ưu hoá để chạy độc lập hoặc triển khai lên Hugging Face Spaces (Docker).
Đầy đủ 4 chức năng cốt lõi:
1. Mô phỏng tấn công vật lý (Print Attack, Replay Attack).
2. So sánh 2 mô hình: Machine Learning kinh điển (LBP+SVM) vs Deep Learning (ResNet-50).
3. Kính hiển vi soi tư duy AI (Grad-CAM & 2D-FFT).
4. Thanh trượt hàng rào an ninh động chuẩn ISO/IEC 30107-3.
"""

import os
import sys
import io
import time
import glob
import base64
import random
import cv2
import numpy as np
from PIL import Image
from typing import Optional

# Cấu hình UTF-8 cho Windows console
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Thiết lập đường dẫn thư mục hiện tại và cha
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)

if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

import torch
import torch.nn.functional as F
import joblib
from skimage.feature import local_binary_pattern

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import module nội bộ (từ web_app/src hoặc src/)
from src.roi_extractor import extract_annular_iris_roi
from src.spoof_generator import simulate_print_attack, simulate_replay_attack
from src.models import load_pad_model
from src.explainability import GradCAM, overlay_heatmap_on_roi
from src.dataset_loader import get_default_transform

app = FastAPI(title="reIris Biometric PAD Lab", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Xác định đường dẫn weights & samples độc lập
WEIGHTS_DIR = os.path.join(CURRENT_DIR, "weights")
if not os.path.exists(os.path.join(WEIGHTS_DIR, "best_model_resnet50_v2.pth")):
    WEIGHTS_DIR = os.path.join(PARENT_DIR, "weights")

SAMPLES_DIR = os.path.join(CURRENT_DIR, "samples")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[INIT] Device detected: {device}")

# 1. Nạp mô hình ResNet-50
pth_path = os.path.join(WEIGHTS_DIR, "best_model_resnet50_v2.pth")
if not os.path.exists(pth_path):
    pth_path = os.path.join(WEIGHTS_DIR, "best_model_resnet50_v2.zip")

model_res = None
gradcam = None
if os.path.exists(pth_path):
    try:
        model_res = load_pad_model(pth_path, device=device)
        model_res.eval()
        gradcam = GradCAM(model_res, target_layer=model_res.layer4[-1])
        print(f"[OK] ResNet-50 loaded successfully on {device} ({os.path.getsize(pth_path)/(1024*1024):.1f} MB)")
    except Exception as e:
        print(f"[ERR] Error loading ResNet-50: {e}")
else:
    print(f"[WARN] ResNet-50 weights not found at: {pth_path}")

# 2. Nạp mô hình LBP + SVM
svm_path = os.path.join(WEIGHTS_DIR, "model_lbp_svm.joblib")
svm_model = None
scaler_lbp = None
if os.path.exists(svm_path):
    try:
        data = joblib.load(svm_path)
        svm_model = data["model"]
        scaler_lbp = data["scaler"]
        print(f"[OK] LBP+SVM loaded successfully (0.29 MB)")
    except Exception as e:
        print(f"[ERR] Error loading LBP+SVM: {e}")
else:
    print(f"[WARN] LBP+SVM weights not found at: {svm_path}")

transform = get_default_transform()


def compute_2d_fft(gray_img: np.ndarray) -> np.ndarray:
    """Tính phổ biên độ tần số 2D Fourier (2D-FFT)."""
    dft = np.fft.fft2(gray_img)
    dft_shift = np.fft.fftshift(dft)
    mag = 20 * np.log(np.abs(dft_shift) + 1e-8)
    norm = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return norm


def extract_spatial_lbp_160(roi_gray):
    """Trích xuất 160 đặc trưng Spatial Uniform LBP từ vành khăn mống mắt."""
    lbp = local_binary_pattern(roi_gray, 8, 1, method='uniform')
    h, w = roi_gray.shape
    features = []
    for r in range(4):
        for c in range(4):
            cell = lbp[r*h//4:(r+1)*h//4, c*w//4:(c+1)*w//4]
            hist, _ = np.histogram(cell.ravel(), bins=10, range=(0, 10))
            hist = hist.astype(np.float32) / (hist.sum() + 1e-7)
            features.extend(hist)
    return np.array(features, dtype=np.float32)


def img_to_base64_png(img_bgr_or_gray):
    """Mã hóa ảnh OpenCV sang Base64 Data URI PNG."""
    ret, buf = cv2.imencode(".png", img_bgr_or_gray)
    if not ret:
        return ""
    b64 = base64.b64encode(buf.tobytes()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


@app.get("/api/samples")
def get_sample_list():
    """Trả về danh sách 6 ca mẫu lâm sàng đối chuẩn."""
    return [
        {
            "id": "live_01",
            "name": "[Live 01] CASIA-Interval Mắt Trái (Oculus Sinister - S1001L01)",
            "type": "live",
            "desc": "Mắt thật người sống, độ phân giải cao, đốm phản xạ đèn LED NIR được khoét đen tự động."
        },
        {
            "id": "live_02",
            "name": "[Live 02] CASIA-Interval Mắt Phải (Oculus Dexter - S1001R01)",
            "type": "live",
            "desc": "Mắt thật bên phải, vân collagen sắc nét, biên giới đồng tử - mống mắt rõ rệt."
        },
        {
            "id": "live_03",
            "name": "[Live 03] CASIA-Interval Đối Tượng Mới (S1002L01)",
            "type": "live",
            "desc": "Mẫu kiểm thử mù độc lập từ đối tượng chưa từng xuất hiện trong tập train."
        },
        {
            "id": "spoof_syn_01",
            "name": "[Spoof 01] CASIA-Syn Mắt Nhân Tạo Tổng Hợp (Syn-000_1)",
            "type": "spoof",
            "desc": "Mống mắt sinh học nhân tạo sinh bởi thuật toán Markov Random Field, thiếu vi mạch tự nhiên."
        },
        {
            "id": "spoof_print_01",
            "name": "[Spoof 02] Print Attack (Tấn Công In Ấn Giấy Ảnh)",
            "type": "spoof",
            "desc": "Mô phỏng ảnh in màu/trắng đen độ phân giải cao với vi hạt tán xạ halftone và độ nhòe thấu kính."
        },
        {
            "id": "spoof_replay_01",
            "name": "[Spoof 03] Replay Attack (Tấn Công Phát Lại Màn Hình)",
            "type": "spoof",
            "desc": "Mô phỏng phát lại video/ảnh trên iPad/Smartphone với sọc lưới quét Moiré và vệt lóa phản xạ."
        }
    ]


@app.get("/api/system-status")
def get_system_status():
    """Trả về thông số phần cứng và trạng thái bảo mật của hệ thống."""
    return {
        "device": str(device).upper(),
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU Active (x86_64 AVX2)",
        "iso_standard": "ISO/IEC 30107-3:2017 & ISO/IEC 19794-6",
        "default_eer_tau": 0.9109,
        "models": {
            "resnet50": {
                "name": "Deep ResNet-50 + Focal Loss",
                "status": "Loaded" if model_res is not None else "Error",
                "size_mb": 94.3,
                "params": "23.5 Million",
                "worst_acer": "0.00%",
                "roc_auc": "100.00%"
            },
            "lbp_svm": {
                "name": "Spatial Uniform LBP + SVM RBF",
                "status": "Loaded" if svm_model is not None else "Error",
                "size_mb": 0.29,
                "params": "160-dim histogram",
                "worst_acer": "0.23%",
                "roc_auc": "99.96%"
            }
        }
    }


class AnalysisRequest(BaseModel):
    sample_id: Optional[str] = "live_01"
    attack_mode: Optional[str] = "none"  # "none", "print", "replay"
    tau: Optional[float] = 0.9109
    custom_image_b64: Optional[str] = None


@app.post("/api/analyze")
async def analyze_iris(req: AnalysisRequest):
    """
    Tiến hành kiểm định an ninh sinh trắc học mống mắt thời gian thực.
    Thực thi 4 chức năng cốt lõi:
    - Chức năng 1: Mô phỏng tấn công vật lý (Print, Replay, None).
    - Chức năng 2: So sánh 2 mô hình: ResNet-50 vs LBP+SVM.
    - Chức năng 3: Sinh bản đồ nhiệt Grad-CAM & Phổ tần số 2D-FFT.
    - Chức năng 4: Áp dụng thanh trượt ngưỡng an ninh động τ.
    """
    t_start_total = time.time()
    
    # 1. Thu nhận ảnh đầu vào
    raw_img = None
    source_name = "Mẫu không xác định"

    if req.custom_image_b64 and len(req.custom_image_b64) > 100:
        try:
            b64_clean = req.custom_image_b64.split(",")[-1]
            img_data = base64.b64decode(b64_clean)
            nparr = np.frombuffer(img_data, np.uint8)
            raw_img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
            source_name = "Ảnh người dùng tải lên"
        except Exception as e:
            return JSONResponse(status_code=400, content={"error": f"Lỗi giải mã ảnh: {str(e)}"})
    else:
        sample_id = req.sample_id or "live_01"
        sample_file = os.path.join(SAMPLES_DIR, f"{sample_id}.jpg")
        
        # Đọc trực tiếp từ thư mục samples độc lập
        if os.path.exists(sample_file):
            raw_img = cv2.imread(sample_file, cv2.IMREAD_GRAYSCALE)
            desc_map = {
                "live_01": "CASIA-Interval Mắt Trái S1001L01",
                "live_02": "CASIA-Interval Mắt Phải S1001R01",
                "live_03": "CASIA-Interval Đối Tượng Mới S1002L01",
                "spoof_syn_01": "CASIA-Syn Mắt Nhân Tạo Syn-000_1",
                "spoof_print_01": "Print Attack (Ảnh in halftone giả mạo)",
                "spoof_replay_01": "Replay Attack (Phát lại qua màn hình)"
            }
            source_name = desc_map.get(sample_id, sample_id)
        else:
            # Fallback nếu chưa có file
            raw_img = np.zeros((280, 320), dtype=np.uint8)
            source_name = "Ảnh giả lập"

    if raw_img is None:
        return JSONResponse(status_code=400, content={"error": "Không thể nạp ảnh mống mắt."})

    # =========================================================================
    # CHỨC NĂNG 1: MÔ PHỎNG TẤN CÔNG VẬT LÝ TRỰC TIẾP (PHYSICAL ATTACK SIMULATION)
    # =========================================================================
    processed_img = raw_img.copy()
    attack_applied = "Không có (Nguyên bản)"
    
    if req.attack_mode == "print":
        processed_img = simulate_print_attack(processed_img, seed=int(time.time()) % 1000)
        attack_applied = "Print Attack (Vi hạt mực in Halftone + Nhòe quang học)"
    elif req.attack_mode == "replay":
        processed_img = simulate_replay_attack(processed_img, seed=int(time.time()) % 1000)
        attack_applied = "Replay Attack (Sọc quét Moiré + Vệt phản xạ màn hình)"

    # =========================================================================
    # TIỀN XỬ LÝ: MẶT NẠ VÀNH KHĂN ANNULAR MASKING (KHOÉT ĐEN 100% ĐỒNG TỬ)
    # =========================================================================
    t_roi_start = time.time()
    roi_annular, meta = extract_annular_iris_roi(processed_img, target_size=(224, 224))
    roi_lat_ms = (time.time() - t_roi_start) * 1000.0

    # =========================================================================
    # CHỨC NĂNG 2: SO SÁNH 2 MÔ HÌNH (LBP+SVM VS RESNET-50)
    # =========================================================================
    # 1. Động cơ Học Sâu (Deep ResNet-50 + Focal Loss)
    prob_res = 0.5
    lat_res_ms = 0.0
    cam_overlay = None

    if model_res is not None:
        roi_rgb = cv2.cvtColor(roi_annular, cv2.COLOR_GRAY2RGB)
        tensor_res = transform(roi_rgb).unsqueeze(0).to(device)
        t_res_start = time.time()
        with torch.no_grad():
            out_res = model_res(tensor_res)
            prob_res = F.softmax(out_res, dim=1)[0, 1].item()
        lat_res_ms = (time.time() - t_res_start) * 1000.0

        # CHỨC NĂNG 3: Grad-CAM
        try:
            hm = gradcam.generate_heatmap(tensor_res, class_idx=1)
            cam_overlay = overlay_heatmap_on_roi(roi_annular, hm, alpha=0.55)
        except Exception as e:
            print(f"[GradCAM Err]: {e}")
            cam_overlay = cv2.cvtColor(roi_annular, cv2.COLOR_GRAY2BGR)
    else:
        cam_overlay = cv2.cvtColor(roi_annular, cv2.COLOR_GRAY2BGR)

    # 2. Động cơ Kinh điển (Spatial LBP 160D + SVM RBF)
    prob_svm = 0.5
    lat_svm_ms = 0.0

    if svm_model is not None and scaler_lbp is not None:
        t_svm_start = time.time()
        feat_lbp = extract_spatial_lbp_160(roi_annular).reshape(1, -1)
        feat_scaled = scaler_lbp.transform(feat_lbp)
        prob_svm = float(svm_model.predict_proba(feat_scaled)[0, 1])
        lat_svm_ms = (time.time() - t_svm_start) * 1000.0

    # =========================================================================
    # CHỨC NĂNG 3: KÍNH HIỂN VI SOI TƯ DUY AI (2D-FFT SPECTRUM)
    # =========================================================================
    fft_spectrum = compute_2d_fft(roi_annular)
    fft_colored = cv2.applyColorMap(fft_spectrum, cv2.COLORMAP_MAGMA)

    # =========================================================================
    # CHỨC NĂNG 4: ÁP DỤNG NGƯỠNG AN NINH ĐỘNG (τ) CHUẨN ISO/IEC 30107-3
    # =========================================================================
    tau = req.tau if req.tau is not None else 0.9109
    verdict_res = "LIVE" if prob_res >= tau else "SPOOF"
    verdict_svm = "LIVE" if prob_svm >= tau else "SPOOF"
    consensus = (verdict_res == verdict_svm)

    total_time_ms = (time.time() - t_start_total) * 1000.0

    # Phản hồi JSON chi tiết
    return {
        "success": True,
        "input_metadata": {
            "source_name": source_name,
            "attack_mode": req.attack_mode,
            "attack_applied": attack_applied,
            "threshold_tau": tau,
            "total_latency_ms": round(total_time_ms, 1)
        },
        "deep_learning": {
            "model_name": "Deep ResNet-50 + Focal Loss",
            "score": round(prob_res, 4),
            "score_percent": f"{prob_res * 100:.1f}%",
            "verdict": verdict_res,
            "latency_ms": round(lat_res_ms, 1),
            "weights_size_mb": 94.3,
            "params": "23.5M",
            "details": "Kiến trúc 50 tầng học sâu với cơ chế Residual Skip Connection"
        },
        "classical_cv": {
            "model_name": "Spatial LBP + SVM (RBF)",
            "score": round(prob_svm, 4),
            "score_percent": f"{prob_svm * 100:.1f}%",
            "verdict": verdict_svm,
            "latency_ms": round(lat_svm_ms, 1),
            "weights_size_mb": 0.29,
            "params": "160 Uniform LBP Features",
            "details": "Trích xuất vi kết cấu bề mặt cục bộ 4x4 ô lưới"
        },
        "consensus": {
            "agreed": consensus,
            "status_text": "ĐỒNG THUẬN QUYẾT ĐỊNH" if consensus else "BẤT ĐỒNG QUYẾT ĐỊNH",
            "commentary": (
                f"Cả hai mô hình đều đồng thuận chấp nhận mẫu mống mắt là {verdict_res} tại ngưỡng an ninh τ = {tau:.4f}."
                if consensus else
                f"Cảnh báo: Mô hình ResNet-50 đưa ra kết luận {verdict_res} ({prob_res*100:.1f}%), trong khi LBP+SVM kết luận {verdict_svm} ({prob_svm*100:.1f}%)."
            )
        },
        "visualizations": {
            "raw_input": img_to_base64_png(processed_img),
            "annular_roi": img_to_base64_png(roi_annular),
            "gradcam": img_to_base64_png(cam_overlay if cam_overlay is not None else roi_annular),
            "fft_spectrum": img_to_base64_png(fft_colored)
        },
        "confusion_matrix_svm": {
            "matrix": [[2279, 3], [1, 390]],
            "labels": ["Spoof", "Live"],
            "acer": "0.23%",
            "errors": 4
        },
        "confusion_matrix_resnet": {
            "matrix": [[2282, 0], [0, 391]],
            "labels": ["Spoof", "Live"],
            "acer": "0.00%",
            "errors": 0
        },
        "comparison_table": [
            {"criterion": "Kiến trúc mô hình", "lbp": "Spatial Uniform LBP (P=8, R=1) + RBF SVM", "resnet": "Deep ResNet-50 + Focal Loss (γ=2.0)"},
            {"criterion": "Kích thước tập tin trọng số", "lbp": "0.29 MB (Siêu nhỏ gọn)", "resnet": "94.3 MB (Gấp ~325 lần)"},
            {"criterion": "Số lượng tham số", "lbp": "160 đặc trưng vi kết cấu", "resnet": "23.5 Triệu trọng số tích chập"},
            {"criterion": "Độ trễ suy luận (CPU / GPU)", "lbp": "~12.4 ms / N/A", "resnet": "~26.8 ms / ~6.2 ms"},
            {"criterion": "Độ chính xác Test (Accuracy)", "lbp": "99.85%", "resnet": "100.00% (Hoàn hảo)"},
            {"criterion": "Chỉ số ACER (Worst-case)", "lbp": "0.23% (Sai 4 mẫu vi hạt)", "resnet": "0.00% (Không sai sót)"},
            {"criterion": "Chỉ số ROC-AUC", "lbp": "99.96%", "resnet": "100.00%"},
            {"criterion": "Khả năng kháng Print Attack", "lbp": "Khá (Dễ bị lừa bởi in phân giải cao)", "resnet": "Tuyệt đối (Bắt trọn vi hạt halftone)"},
            {"criterion": "Khả năng kháng Replay Attack", "lbp": "Khá (Dễ sai lệch khi có ánh sáng chói)", "resnet": "Tuyệt đối (Bắt trọn sọc quét Moiré)"},
            {"criterion": "Giải thích được (XAI)", "lbp": "Phổ Histogram phân bố 160D", "resnet": "Bản đồ nhiệt Grad-CAM + Phổ 2D-FFT"}
        ]
    }


# Gắn thư mục tĩnh static
STATIC_DIR = os.path.join(CURRENT_DIR, "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", response_class=HTMLResponse)
def serve_index():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>reIris PAD Web App Loading...</h1>"


if __name__ == "__main__":
    import uvicorn
    # Hugging Face Spaces cung cấp biến môi trường PORT (mặc định 7860), còn local dùng 8000
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    print(f"[START] Khởi động reIris Biometric PAD Lab trên {host}:{port} ...")
    uvicorn.run(app, host=host, port=port)

