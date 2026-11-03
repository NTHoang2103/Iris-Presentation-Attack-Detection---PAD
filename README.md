# XÂY DỰNG HỆ THỐNG NHẬN DIỆN MỐNG MẮT THẬT VÀ GIẢ BẰNG HỌC SÂU
**(Deep Learning-based Iris Presentation Attack Detection)**

---

## 1. MÔ TẢ CHI TIẾT VỀ BỘ DỮ LIỆU (DATASETS)

Dự án sử dụng hai tập dữ liệu chuẩn quốc tế thuộc hệ sinh thái **CASIA-IrisV4**, được thu thập và phát triển bởi Trung tâm Nghiên cứu Sinh trắc học và Bảo mật (Center for Biometrics and Security Research - CBSR), thuộc Viện Tự động hóa, Viện Hàn lâm Khoa học Trung Quốc (CASIA).

*   **Trang thông tin học thuật gốc (CBSR):** [http://www.cbsr.ia.ac.cn/english/IrisDatabase.asp](http://www.cbsr.ia.ac.cn/english/IrisDatabase.asp)
*   **Nguồn dữ liệu Mắt thật (CASIA-Iris-Interval):** [https://www.kaggle.com/datasets/swoyam2609/casia-iris-interval](https://www.kaggle.com/datasets/swoyam2609/casia-iris-interval)
*   **Nguồn dữ liệu Mắt giả tổng hợp (CASIA-Iris-Syn):** [https://www.kaggle.com/datasets/monareyhanii/casia-iris-syn](https://www.kaggle.com/datasets/monareyhanii/casia-iris-syn)

### 1.1. Tập dữ liệu CASIA-Iris-Interval (Dữ liệu Mắt thật - Live / Bona Fide)
*   **Vai trò trong đề tài:** Đóng vai trò là tập dữ liệu chuẩn mang nhãn **Mắt thật (Live - Nhãn 1)**. Đồng thời, đây là nguồn dữ liệu gốc chất lượng cao được sử dụng để chế tác các mẫu giả lập tấn công vật lý (in giấy và phát lại qua màn hình).
*   **Quy mô dữ liệu:** Bao gồm **2.639 ảnh** mống mắt được thu thập từ **249 người tham gia** (subjects), tạo thành **395 lớp** (classes - mỗi mắt trái hoặc phải của một người được tính là một lớp độc lập).
*   **Định dạng và độ phân giải:** Ảnh đa cấp xám 8-bit (8-bit Grayscale), định dạng `.jpg`, độ phân giải cố định **320 x 280 pixels**.
*   **Điều kiện thu thập và đặc tính kỹ thuật:** 
    *   Ảnh được chụp trong môi trường phòng thí nghiệm kiểm soát chặt chẽ qua hai phiên (two sessions) bằng camera chụp mống mắt cận cảnh chuyên dụng do CASIA tự thiết kế.
    *   Thiết bị sử dụng một vòng đèn LED hồng ngoại gần (Near-Infrared - NIR) bố trí đồng tâm, cung cấp thông lượng sáng tối ưu cho vùng mống mắt.
    *   Hình ảnh thu được có độ sắc nét cực cao, thể hiện rõ ràng các chi tiết vi cấu trúc (micro-textures) như các nếp gấp, rãnh, hốc mống mắt và xuất hiện một vòng chấm sáng trắng nhỏ phản xạ từ dàn đèn LED nằm gọn bên trong vùng đồng tử đen.
*   **Cấu trúc lưu trữ và quy tắc đặt tên file:**
    ```text
    CASIA-Iris-Interval/YYY/L/S1YYYENN.jpg (hoặc CASIA-Iris-Interval/YYY/S1YYYENN.jpg)
    ```
    Trong đó:
    *   `S1`: Ký hiệu định danh của tập con thứ nhất (Interval).
    *   `YYY`: Mã định danh của đối tượng (Subject ID).
    *   `E`: Ký hiệu vị trí mắt, bao gồm `L` (Left - mắt trái) và `R` (Right - mắt phải).
    *   `NN`: Số thứ tự của bức ảnh trong lớp tương ứng.

### 1.2. Tập dữ liệu CASIA-Iris-Syn (Dữ liệu Mắt giả nhân tạo - Spoof / Synthetic Attack)
*   **Vai trò trong đề tài:** Đóng vai trò là tập dữ liệu mang nhãn **Mắt giả (Spoof - Nhãn 0)**, đại diện cho hình thức tấn công sinh trắc học bằng dữ liệu tổng hợp từ máy tính và thuật toán nhân tạo.
*   **Quy mô dữ liệu:** Bao gồm **10.000 ảnh** mống mắt nhân tạo, được phân bổ đều vào **1.000 lớp** (mỗi lớp gồm 10 ảnh biến thể).
*   **Định dạng và độ phân giải:** Ảnh đa cấp xám 8-bit (8-bit Grayscale), định dạng `.jpg`, độ phân giải cố định **640 x 480 pixels**.
*   **Phương pháp tổng hợp và đặc tính kỹ thuật:**
    *   Dữ liệu không được chụp từ người thật mà được sinh tự động bằng thuật toán dựa trên việc lấy mẫu các mảng kết cấu (texture patches) từ cơ sở dữ liệu CASIA-IrisV1, kết hợp với phương pháp Phân tích thành phần chính (PCA) và kỹ thuật siêu phân giải (Super-Resolution).
    *   Sau khi tổng hợp vân mống mắt gốc, hệ thống áp dụng các biến dạng nội lớp (intra-class variations) bao gồm biến dạng đàn hồi, làm mờ nhẹ, thêm nhiễu nền và xoay góc để mô phỏng điều kiện thu nhận thực tế.
    *   Về mặt thị giác thông thường, ảnh trong tập `CASIA-Iris-Syn` rất giống mắt người thật. Tuy nhiên, khi phân tích ở cấp độ điểm ảnh và miền tần số, dữ liệu này thiếu các đặc trưng sinh học tự nhiên ở dải tần số cao và có sự phân bố ánh sáng nền khác biệt so với ảnh chụp từ cảm biến NIR thực tế.
*   **Cấu trúc lưu trữ và quy tắc đặt tên file:**
    ```text
    CASIA-Iris-Syn/YYY/S6YYYENN.jpg
    ```
    Trong đó `YYY` là mã lớp tổng hợp (từ `000` đến `999`) và `NN` là chỉ số ảnh biến thể trong lớp đó.

### 1.3. Bảng tổng hợp đối sánh và Thách thức dữ liệu cần xử lý

| Tiêu chí kỹ thuật | CASIA-Iris-Interval | CASIA-Iris-Syn | Thách thức đặt ra cho hệ thống |
| :--- | :--- | :--- | :--- |
| **Nhãn phân loại** | `Live` (Mắt thật - `1`) | `Spoof` (Mắt giả - `0`) | Phân loại nhị phân (Binary Classification). |
| **Số lượng mẫu** | 2.639 ảnh | 10.000 ảnh | **Mất cân bằng dữ liệu (Class Imbalance)** tỷ lệ xấp xỉ 1 : 3.8 nghiêng về lớp giả mạo. |
| **Độ phân giải gốc** | 320 x 280 pixels | 640 x 480 pixels | **Lệch miền độ phân giải (Resolution Shift):** Nếu resize trực tiếp toàn ảnh, mô hình sẽ học vẹt dấu vết nội suy pixel thay vì học cấu trúc mống mắt. |
| **Bản chất môi trường** | Ảnh chụp phòng thí nghiệm rất sạch | Ảnh tổng hợp bằng thuật toán | **Thiếu mẫu tấn công vật lý:** Cần bổ sung thêm các mẫu giả lập in giấy (Print) và chụp qua màn hình (Replay) để mô hình không bị học vẹt (Overfitting). |

---

## 2. CÁC CÔNG VIỆC THỰC HIỆN VÀ KẾT QUẢ MONG MUỐN SAU CÙNG

### 2.1. Các công việc và quy trình thực hiện trong đề tài (Project Workflow & Pipeline)

Để giải quyết triệt để bài toán nhận diện mống mắt thật và giả cũng như khắc phục các thách thức từ dữ liệu gốc, đề tài triển khai một luồng xử lý khép kín gồm 6 công đoạn kỹ thuật:

```text
[Dữ liệu gốc: CASIA-Iris-Interval (Live) & CASIA-Iris-Syn (Spoof)]
        |
        v
[Công đoạn 1: Khảo sát & Trực quan hóa dữ liệu (EDA)]
        |
        v
[Công đoạn 2: Phân chia tập dữ liệu độc lập theo đối tượng (Train / Val / Test)]
        |
        v
[Công đoạn 3: Định vị, phân vùng cắt lấy mống mắt (ROI) & Đồng nhất kích thước 224x224]
        |
        +---> Nhánh Live (1): Ảnh ROI thật + Tăng cường dữ liệu hình học cơ bản
        |
        +---> Nhánh Spoof (0): Ảnh ROI từ CASIA-Syn + Ảnh ROI giả lập Print & Replay Attack
        |
        v
[Công đoạn 4: Huấn luyện mô hình Học sâu (ResNet-50 / MobileNetV3 + Focal Loss)]
        |
        v
[Công đoạn 5: Đánh giá theo chuẩn bảo mật ISO/IEC 30107-3 & Giải thích bằng Grad-CAM]
        |
        v
[Công đoạn 6: Đóng gói mô hình và xây dựng ứng dụng Web Demo bằng Streamlit]
```

#### Công đoạn 1: Khảo sát và Trực quan hóa dữ liệu (Exploratory Data Analysis - EDA)
*   Kiểm tra tính toàn vẹn của toàn bộ tệp ảnh trong hai bộ dữ liệu, loại bỏ các tệp bị hỏng định dạng (nếu có).
*   Thống kê và vẽ biểu đồ phân phối số lượng mẫu theo từng lớp và số lượng ảnh trên mỗi đối tượng.
*   Vẽ biểu đồ phân bố cường độ mức xám (Pixel Intensity Histogram) để đối chiếu dải tương phản động giữa ảnh chụp hồng ngoại thật và ảnh nhân tạo.
*   Thực hiện biến đổi Fourier nhanh hai chiều (2D Fast Fourier Transform - FFT) để chuyển ảnh từ miền không gian sang miền tần số, trực quan hóa sự suy giảm tần số cao và các nhiễu tuần hoàn trên ảnh giả mạo.

#### Công đoạn 2: Tiền xử lý dữ liệu và Phân vùng mống mắt (Preprocessing & Iris Segmentation)
*   **Phân chia dữ liệu độc lập theo đối tượng (Subject-Independent Split):** Tiến hành chia dữ liệu thành 3 tập Train (70%), Validation (15%) và Test (15%) dựa theo thư mục mã người dùng (`Subject ID`). Nguyên tắc bắt buộc là toàn bộ ảnh của cùng một cá nhân chỉ được xuất hiện ở một tập duy nhất nhằm ngăn chặn hoàn toàn hiện tượng rò rỉ dữ liệu (Data Leakage).
*   **Định vị và tách vùng quan tâm (Iris Localization & Segmentation):** Áp dụng mạng phân vùng **U-Net** kết hợp với phép biến đổi **Hough Circle Transform** để xác định biên trong (đồng tử) và biên ngoài (mống mắt). Thực hiện cắt (crop) khung hình vuông bao trọn vùng mống mắt (Region of Interest - ROI), loại bỏ các thành phần gây nhiễu bên ngoài như lông mi, mi mắt và vùng da.
*   **Chuẩn hóa kích thước và mức xám:** Đưa toàn bộ ảnh vùng ROI đã cắt từ cả hai bộ dữ liệu về cùng một kích thước chuẩn **224 x 224 pixels**, cân bằng biểu đồ xám cục bộ (CLAHE) và chuẩn hóa giá trị pixel theo phân phối chuẩn để triệt tiêu sự chênh lệch độ phân giải gốc (`320x280` và `640x480`).

#### Công đoạn 3: Tăng cường dữ liệu và Chế tác mẫu giả mạo lai (Data Augmentation & Hybrid Spoof Generation)
Sử dụng thư viện `OpenCV` và `Albumentations` để xử lý hai luồng dữ liệu:
*   **Luồng tăng cường dữ liệu chuẩn (trên tập Train):** Áp dụng phép lật ngang ngẫu nhiên (Horizontal Flip), xoay góc nhỏ ($\pm 15^\circ$), thay đổi nhẹ độ sáng và độ tương phản để tăng khả năng tổng quát hóa.
*   **Luồng sinh dữ liệu giả mạo vật lý (Hybrid Spoof Generation):** Trích xuất một phần ảnh từ tập `CASIA-Iris-Interval` trong từng tập tương ứng để biến đổi thành các mẫu tấn công giả lập, gán nhãn `Spoof (0)`:
    *   *Giả lập tấn công in giấy (Simulated Print Attack):* Áp dụng bộ lọc làm mờ quang học (`GaussianBlur`, `MotionBlur`), chèn nhiễu hạt mô phỏng hạt mực in (`MultiplicativeNoise`, `ISO Noise`) và giảm độ sâu bit màu (`Posterize`).
    *   *Giả lập tấn công phát lại qua màn hình (Simulated Replay Attack):* Chèn các vệt lóa sáng phản xạ gương (`Specular Glare`), phủ lớp lưới giao thoa mô phỏng tần số quét màn hình điện thoại (`Moiré Pattern`) và nén giảm chất lượng ảnh (`JPEG Compression`).

#### Công đoạn 4: Xây dựng và Huấn luyện mô hình Học sâu (Model Training & Optimization)
*   **Thiết kế kiến trúc mạng phân loại:** Sử dụng phương pháp Học chuyển giao (Transfer Learning) với hai kiến trúc mạng nơ-ron tích chập (CNN) để thực nghiệm và đối sánh:
    *   **ResNet-50:** Mô hình chủ lực tận dụng các kết nối tắt (Residual Connections) giúp bảo toàn thông tin đặc trưng vi cấu trúc bề mặt mống mắt qua nhiều tầng tích chập sâu.
    *   **MobileNetV3-Large:** Mô hình gọn nhẹ sử dụng tích chập tách chiều sâu (Depthwise Separable Convolution), phục vụ bài toán tối ưu hóa tốc độ suy luận thời gian thực.
*   **Hàm mất mát và Thuật toán tối ưu:** Sử dụng **Focal Loss** (hoặc Weighted Binary Cross-Entropy) để xử lý sự mất cân bằng số lượng mẫu giữa lớp Thật và Giả, đồng thời buộc mô hình tập trung học các mẫu giả mạo khó phân biệt. Kết hợp bộ tối ưu hóa `AdamW`, lịch trình điều chỉnh tốc độ học `CosineAnnealingLR` và cơ chế dừng sớm (`Early Stopping`) để chống học vẹt.

#### Công đoạn 5: Đánh giá theo tiêu chuẩn bảo mật quốc tế và Giải thích mô hình
*   **Đo lường theo tiêu chuẩn ISO/IEC 30107-3:** Đánh giá hiệu năng hệ thống thông qua các chỉ số chuyên ngành sinh trắc học:
    *   **APCER (Attack Presentation Classification Error Rate):** Tỷ lệ mẫu giả mạo bị hệ thống nhận nhầm là mắt thật.
    *   **BPCER (Bona Fide Presentation Classification Error Rate):** Tỷ lệ mắt người thật bị hệ thống từ chối nhầm là giả mạo.
    *   **ACER (Average Classification Error Rate):** Trung bình cộng của APCER và BPCER.
    *   Các chỉ số bổ trợ: Accuracy, Precision, Recall, F1-Score, Ma trận nhầm lẫn (Confusion Matrix), đường cong ROC-AUC và EER (Equal Error Rate).
*   **Giải thích quyết định của AI (Explainable AI):** Áp dụng thuật toán **Grad-CAM** tạo bản đồ nhiệt (Heatmap) chồng lên ảnh đầu vào để kiểm chứng xem mô hình thực sự nhìn vào vùng vân mống mắt hay đang học vẹt các chi tiết thừa ở viền ảnh.

#### Công đoạn 6: Xây dựng ứng dụng Web Demo (System Deployment)
*   Sử dụng framework **Streamlit** để đóng gói toàn bộ quy trình tiền xử lý, khoanh vùng mống mắt, mô hình phân loại và trích xuất Grad-CAM thành một giao diện ứng dụng Web tương tác trực tiếp.

---

### 2.2. Kết quả mong muốn sau cùng (Expected Final Deliverables)

Sau khi hoàn thành toàn bộ các công đoạn trên, đề tài hướng tới 4 kết quả đầu ra cụ thể và có thể kiểm chứng:

1.  **Bộ dữ liệu PAD hoàn chỉnh và Bộ mã nguồn Tiền xử lý tự động:**
    *   Một tập dữ liệu đã được làm sạch, cắt chuẩn vùng ROI mống mắt (`224 x 224`), phân chia nghiêm ngặt theo đối tượng (`train/val/test`) và bao phủ đầy đủ 3 kịch bản tấn công: Ảnh tổng hợp AI (`CASIA-Iris-Syn`), Ảnh giả lập in ấn (`Print Attack`) và Ảnh giả lập màn hình (`Replay Attack`).
    *   Bộ script Python tự động hóa hoàn toàn từ khâu đọc dữ liệu thô, phân vùng mống mắt cho đến bước sinh nhiễu giả lập.

2.  **Mô hình Học sâu có độ chính xác cao và khả năng tổng quát hóa vững chắc:**
    *   Tệp trọng số mô hình đã huấn luyện hoàn chỉnh (`.pth`) của kiến trúc **ResNet-50** và **MobileNetV3** đạt tỷ lệ lỗi trung bình **ACER ở mức thấp nhất**, đảm bảo cân bằng giữa tính an ninh (APCER thấp) và tính tiện dụng (BPCER thấp).
    *   Mô hình chứng minh được khả năng kháng nhiễu, không bị học vẹt vào độ phân giải ảnh gốc và tập trung chính xác vào vùng cấu trúc vành khăn mống mắt thông qua kết quả kiểm chứng trên bản đồ nhiệt **Grad-CAM**.

3.  **Hệ thống báo cáo thực nghiệm và Phân tích định lượng đầy đủ:**
    *   Hệ thống biểu đồ phân tích dữ liệu trực quan (phân bố lớp, biểu đồ mức xám Histogram, phổ tần số 2D-FFT).
    *   Bảng số liệu đối sánh thực nghiệm (Ablation Study) chi tiết giữa ResNet-50 và MobileNetV3 về độ chính xác, các chỉ số chuẩn ISO/IEC 30107-3 (APCER, BPCER, ACER, ROC-AUC) và tốc độ xử lý trung bình trên mỗi bức ảnh.

4.  **Ứng dụng phần mềm Web Demo hoạt động theo thời gian thực (Streamlit App):**
    *   Giao diện người dùng trực quan cho phép tải ảnh kiểm thử bất kỳ từ máy tính hoặc chọn nhanh từ **Kho ảnh mẫu (Sample Gallery)** tích hợp sẵn.
    *   Hiển thị minh bạch từng bước trong luồng xử lý của AI trên cùng một màn hình: `Ảnh gốc đầu vào` -> `Ảnh khoanh vùng và cắt mống mắt (ROI)` -> `Bản đồ nhiệt vùng chú ý Grad-CAM`.
    *   Trả về kết luận phân loại rõ ràng (**Mắt thật - Live** hoặc **Mắt giả - Spoof**) đi kèm thanh biểu diễn tỷ lệ phần trăm độ tin cậy (Confidence Score) và bảng thống kê các chỉ số đánh giá mô hình.

---

## 3. HƯỚNG DẪN SỬ DỤNG HỆ THỐNG (SYSTEM USAGE GUIDE)

Dự án tập trung vào hai thành phần thực thi chính: Notebook thực nghiệm huấn luyện và Giao diện ứng dụng Web Demo trực quan.

### 3.1. Hướng dẫn chạy Notebook Huấn luyện và Thực nghiệm (iris-pad_3.ipynb)

Notebook `iris-pad_3.ipynb` được thiết kế tự động hóa khép kín (End-to-End Pipeline) từ khâu nạp dữ liệu thô, tiền xử lý, huấn luyện mô hình cho đến đánh giá theo chuẩn quốc tế ISO/IEC 30107-3. Khuyến nghị thực thi trên nền tảng Kaggle GPU (miễn phí) để đạt tốc độ tối ưu:

1.  **Chuẩn bị môi trường trên Kaggle:**
    *   Tạo một Notebook mới trên Kaggle và kích hoạt phần cứng hỗ trợ: **GPU T4 x2** (hoặc GPU P100).
    *   Đính kèm hai bộ dữ liệu chuẩn vào Notebook bằng cách chọn `Add Input` và tìm kiếm:
        *   `swoyam2609/casia-iris-interval` (Mắt thật - Live)
        *   `monareyhanii/casia-iris-syn` (Mắt nhân tạo - Spoof)

2.  **Nạp và thực thi Notebook:**
    *   Chọn `File` -> `Upload Notebook` và nạp tệp `iris-pad_3.ipynb`.
    *   Nhấn `Run All` để thực thi tuần tự toàn bộ các cell code:
        *   *Cell 1 - 5 (Thiết lập & Khảo sát EDA):* Cài đặt thư viện, kiểm tra toàn vẹn tệp ảnh, phân tích biểu đồ mức xám Histogram và phổ Fourier 2D-FFT.
        *   *Cell 6 - 9 (Tiền xử lý & Mô phỏng tấn công):* Bóc tách mặt nạ vành khăn Annular Iris Masking (khoét đen 100% vùng đồng tử để triệt tiêu lỗi học vẹt đèn LED), chế tác dữ liệu tấn công in giấy (Print Attack) và phát lại màn hình (Replay Attack).
        *   *Cell 10 - 13 (Phân chia dữ liệu):* Xây dựng bộ dữ liệu True Hybrid PAD và phân chia độc lập người dùng (Subject-Independent: 199 đối tượng Train, 25 đối tượng Val, 25 đối tượng Test).
        *   *Cell 14 - 15 (Mô hình kinh điển):* Trích xuất đặc trưng Spatial Uniform LBP (160 chiều) và huấn luyện bộ phân loại SVM RBF (thời gian khoảng 4.5 phút trên CPU).
        *   *Cell 16 - 20 (Mô hình học sâu):* Huấn luyện mạng Deep ResNet-50 kết hợp hàm mất mát Focal Loss và tối ưu hóa nửa độ chính xác FP16 qua 10 Epochs (thời gian khoảng 20 phút trên GPU).
        *   *Cell 21 - 25 (Đánh giá & Minh bạch hóa XAI):* Xuất ma trận nhầm lẫn đối sánh, đường cong ROC theo chuẩn ISO/IEC 30107-3, bản đồ nhiệt Grad-CAM và phân tích các ca nhận dạng sai.

3.  **Lưu trữ tệp trọng số đầu ra:**
    *   Sau khi chạy xong, hai tệp trọng số mô hình tối ưu được tạo ra trong thư mục output:
        *   `best_model_resnet50_v2.pth` (Trọng số ResNet-50)
        *   `model_lbp_svm.joblib` (Trọng số LBP + SVM)
    *   Tải hai tệp này về máy tính cá nhân và đặt vào thư mục `weights/` của dự án để phục vụ giao diện Demo.

---

### 3.2. Hướng dẫn khởi chạy và sử dụng Giao diện Web Demo (Streamlit App)

Giao diện Web Demo đóng gói toàn bộ mô hình và thuật toán thành một ứng dụng tương tác trực quan, cho phép kiểm tra và chẩn đoán ảnh mống mắt theo thời gian thực.

1.  **Cài đặt thư viện cần thiết:**
    Mở cửa sổ dòng lệnh (Terminal / PowerShell) tại thư mục gốc của dự án và cài đặt các thư viện cần thiết:
    ```bash
    pip install streamlit torch torchvision opencv-python scikit-learn albumentations matplotlib pandas numpy
    ```

2.  **Khởi chạy ứng dụng Web Demo:**
    Thực hiện lệnh sau từ thư mục gốc của dự án:
    ```bash
    streamlit run app/app_streamlit.py
    ```
    Hệ thống sẽ khởi tạo máy chủ cục bộ và tự động mở trình duyệt tại địa chỉ:
    ```text
    http://localhost:8501
    ```

3.  **Hướng dẫn thao tác trên giao diện:**
    Giao diện làm việc gồm thanh điều hướng bên trái và khu vực hiển thị nội dung chính với 3 mục chức năng:

    *   **Mục 1 - Tổng quan:** 
        Cung cấp tài liệu tra cứu lý thuyết về bài toán chống tấn công giả mạo mống mắt (Iris PAD), cơ chế hoạt động của mạng Deep ResNet-50, mô hình kinh điển Spatial LBP + SVM, và tiêu chuẩn an ninh quốc tế ISO/IEC 30107-3.

    *   **Mục 2 - Hướng dẫn nhanh:**
        Tài liệu tóm tắt quy trình chuẩn (SOP) 3 bước vận hành hệ thống kiểm định từ tiếp nhận ảnh hồng ngoại NIR, bóc tách mặt nạ vành khăn mống mắt đến phân tích cảnh báo an ninh.

    *   **Mục 3 - Nghiên cứu mô hình (Khu vực thử nghiệm chính):**
        Bao gồm 3 tab làm việc:
        *   *Tab "Thử nghiệm":*
            *   Bước 1: Chọn một ảnh từ "Thư viện mẫu" (gồm đủ 4 kịch bản: Mắt thật Live, Mắt nhân tạo Syn, Tấn công in giấy Print, Tấn công màn hình Replay) hoặc bấm "Browse files" để tải ảnh bất kỳ từ máy tính cá nhân.
            *   Bước 2: Hệ thống tự động tiền xử lý (khoét đen đồng tử) và hiển thị kết quả suy luận ngay lập tức: Điểm tin cậy độ sống (Liveness Score), Kết luận nhị phân (`LIVE - XÁC THỰC THÀNH CÔNG` hoặc `SPOOF - CẢNH BÁO GIẢ MẠO`), và Khuyến nghị an ninh kiểm soát cửa SmartGate.
            *   Bước 3: Quan sát bản đồ nhiệt Grad-CAM để kiểm tra vùng mô sợi mống mắt mà AI tập trung phân tích, kết hợp phổ tần số không gian 2D-FFT để nhận diện dấu vết nhiễu vi mô nhân tạo.
        *   *Tab "Biểu đồ Benchmark":*
            Xem biểu đồ đường cong suy giảm hàm mất mát Focal Loss, biểu đồ độ chính xác kiểm định Validation qua 10 Epochs, ma trận nhầm lẫn (Confusion Matrix) và đường cong ROC đạt AUC tuyệt đối 100%.
        *   *Tab "So sánh mô hình":*
            Bảng đối sánh trực tiếp các chỉ số hiệu năng giữa hai mô hình: LBP + SVM (nhẹ 0.29 MB, thời gian huấn luyện 4.5 phút) và Deep ResNet-50 (độ chính xác tuyệt đối ACER = 0.00%, tốc độ suy luận 6.5 ms/ảnh).

---

## 4. THÔNG TIN HỌC PHẦN (PROJECT CREDITS)

*   **Học phần:** Nhận dạng mẫu (Pattern Recognition)
*   **Đơn vị đào tạo:** Khoa Công nghệ Thông tin - Phân hiệu Trường Đại học Thủy Lợi
*   **Giảng viên hướng dẫn:** Cô: Nguyễn Thị Hồng Tú
