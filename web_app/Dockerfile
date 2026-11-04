# Sử dụng Python 3.10 slim làm base image
FROM python:3.10-slim

# Thiết lập biến môi trường
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PORT=7860

# Cài đặt thư viện hệ thống cần thiết cho xử lý ảnh
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Tạo người dùng non-root (chuẩn an toàn của Hugging Face Spaces)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Cài đặt các thư viện Python
COPY --chown=user:user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn, trọng số và dữ liệu mẫu vào container
COPY --chown=user:user . .

# Hugging Face Spaces yêu cầu cổng 7860
EXPOSE 7860

# Khởi chạy ứng dụng FastAPI
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]

