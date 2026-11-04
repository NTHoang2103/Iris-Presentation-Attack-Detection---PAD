"""
reIris Biometric PAD Lab - Server Entrypoint
Chuyển tiếp trực tiếp từ app.py để đảm bảo tính độc lập và tương thích ngược 100%.
"""

import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)

if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

# Import ứng dụng FastAPI chính thức
from app import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    host = "127.0.0.1"
    uvicorn.run(app, host=host, port=port)
