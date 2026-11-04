/**
 * reIris PAD Web Application - Client-Side Controller
 * Xử lý tương tác giao diện thời gian thực, gọi API FastAPI và cập nhật 4 chức năng cốt lõi.
 */

// Global State
let currentAnalysisData = null;
let currentCustomImageB64 = null;
let lossChart = null;
let accChart = null;

// =============================================================================
// 1. ĐIỀU HƯỚNG TRANG & BREADCRUMBS
// =============================================================================
function switchPage(pageId) {
    // Ẩn tất cả các trang
    document.getElementById('page-overview').classList.add('hidden');
    document.getElementById('page-quickstart').classList.add('hidden');
    document.getElementById('page-research').classList.add('hidden');

    // Bỏ active tất cả nav items
    document.getElementById('nav-overview').classList.remove('active');
    document.getElementById('nav-quickstart').classList.remove('active');
    document.getElementById('nav-research').classList.remove('active');

    // Cập nhật breadcrumb và hiển thị trang được chọn
    const breadcrumb = document.getElementById('breadcrumb-page');

    if (pageId === 'overview') {
        document.getElementById('page-overview').classList.remove('hidden');
        document.getElementById('nav-overview').classList.add('active');
        breadcrumb.innerText = 'Tổng quan';
    } else if (pageId === 'quickstart') {
        document.getElementById('page-quickstart').classList.remove('hidden');
        document.getElementById('nav-quickstart').classList.add('active');
        breadcrumb.innerText = 'Hướng Dẫn Nhanh';
    } else if (pageId === 'research') {
        document.getElementById('page-research').classList.remove('hidden');
        document.getElementById('nav-research').classList.add('active');
        breadcrumb.innerText = 'Nghiên cứu Mô Hình';
        
        // Nếu chưa có dữ liệu phân tích thì kích hoạt ngay lần đầu
        if (!currentAnalysisData) {
            triggerAnalysis();
        }
    }

    // Scroll to top mượt mà
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// =============================================================================
// 2. CHUYỂN ĐỔI SUB-TABS TRONG MỤC "NGHIÊN CỨU MÔ HÌNH"
// =============================================================================
function switchSubTab(subTabId) {
    document.getElementById('subtab-infer').classList.add('hidden');
    document.getElementById('subtab-bench').classList.add('hidden');
    document.getElementById('subtab-compare').classList.add('hidden');

    document.getElementById('subtab-btn-infer').classList.remove('active');
    document.getElementById('subtab-btn-bench').classList.remove('active');
    document.getElementById('subtab-btn-compare').classList.remove('active');

    if (subTabId === 'infer') {
        document.getElementById('subtab-infer').classList.remove('hidden');
        document.getElementById('subtab-btn-infer').classList.add('active');
    } else if (subTabId === 'bench') {
        document.getElementById('subtab-bench').classList.remove('hidden');
        document.getElementById('subtab-btn-bench').classList.add('active');
        renderBenchmarkCharts();
    } else if (subTabId === 'compare') {
        document.getElementById('subtab-compare').classList.remove('hidden');
        document.getElementById('subtab-btn-compare').classList.add('active');
        renderComparisonTable();
    }
}

// =============================================================================
// 3. TƯƠNG TÁC CHỌN ẢNH & UPLOAD
// =============================================================================
function onSampleChange() {
    currentCustomImageB64 = null;
    document.getElementById('file-uploader').value = '';
    triggerAnalysis();
}

function onFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(e) {
        currentCustomImageB64 = e.target.result;
        triggerAnalysis();
    };
    reader.readAsDataURL(file);
}

function onAttackModeChange() {
    triggerAnalysis();
}

// =============================================================================
// 4. CHỨC NĂNG 4: THANH TRƯỢT HÀNG RÀO AN NINH ĐỘNG (DYNAMIC ISO GATE)
// =============================================================================
function setQuickTau(val) {
    const slider = document.getElementById('tau-slider');
    slider.value = val;
    onTauSliderInput(val);
}

function onTauSliderInput(val) {
    const tau = parseFloat(val);
    document.getElementById('slider-val-display').innerText = tau.toFixed(4);

    // Cập nhật phán quyết thời gian thực ngay trên giao diện nếu đã có điểm số
    if (currentAnalysisData) {
        updateVerdictsLocally(tau);
    }
}

function updateVerdictsLocally(tau) {
    if (!currentAnalysisData) return;

    const scoreRes = currentAnalysisData.resnet50.score;
    const scoreSvm = currentAnalysisData.lbp_svm.score;

    const isLiveRes = (scoreRes >= tau);
    const isLiveSvm = (scoreSvm >= tau);

    // Cập nhật thẻ ResNet-50
    const resBox = document.getElementById('res-verdict-box');
    const resText = document.getElementById('res-verdict-text');
    if (isLiveRes) {
        resBox.className = 'py-3 px-4 rounded-lg my-3 text-center transition bg-emerald-950/40 border border-emerald-500/50 text-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.2)]';
        resText.innerText = `CHẤP THUẬN LIVE (${(scoreRes * 100).toFixed(1)}%)`;
    } else {
        resBox.className = 'py-3 px-4 rounded-lg my-3 text-center transition bg-red-950/40 border border-red-500/50 text-red-400 shadow-[0_0_15px_rgba(239,68,68,0.2)]';
        resText.innerText = `TỪ CHỐI SPOOF (${(scoreRes * 100).toFixed(1)}%)`;
    }

    // Cập nhật thẻ LBP+SVM
    const svmBox = document.getElementById('svm-verdict-box');
    const svmText = document.getElementById('svm-verdict-text');
    if (isLiveSvm) {
        svmBox.className = 'py-3 px-4 rounded-lg my-3 text-center transition bg-emerald-950/40 border border-emerald-500/50 text-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.2)]';
        svmText.innerText = `CHẤP THUẬN LIVE (${(scoreSvm * 100).toFixed(1)}%)`;
    } else {
        svmBox.className = 'py-3 px-4 rounded-lg my-3 text-center transition bg-red-950/40 border border-red-500/50 text-red-400 shadow-[0_0_15px_rgba(239,68,68,0.2)]';
        svmText.innerText = `TỪ CHỐI SPOOF (${(scoreSvm * 100).toFixed(1)}%)`;
    }

    // Cập nhật đối đầu & Nhận xét
    const consensusBadge = document.getElementById('duel-consensus-badge');
    const commentaryText = document.getElementById('duel-commentary-text');

    if (isLiveRes === isLiveSvm) {
        consensusBadge.className = 'px-3 py-1 rounded-full text-xs font-bold bg-emerald-950/40 border border-emerald-500/50 text-emerald-400';
        consensusBadge.innerText = 'ĐỒNG THUẬN QUYẾT ĐỊNH';
        if (isLiveRes) {
            commentaryText.innerText = `Cả hai mô hình đều đồng thuận chấp nhận mẫu mống mắt là LIVE (Người thật) tại ngưỡng an ninh τ = ${tau.toFixed(4)}.`;
        } else {
            commentaryText.innerText = `Cả hai mô hình đều đồng thuận phát hiện và chặn đứng cuộc tấn công giả mạo SPOOF tại ngưỡng an ninh τ = ${tau.toFixed(4)}.`;
        }
    } else {
        consensusBadge.className = 'px-3 py-1 rounded-full text-xs font-bold bg-red-950/40 border border-red-500/50 text-red-400';
        consensusBadge.innerText = 'BẤT ĐỒNG THUẬN MÔ HÌNH';
        if (isLiveRes && !isLiveSvm) {
            commentaryText.innerText = `Mô hình kinh điển LBP+SVM nghi ngờ có vi hạt nhân tạo và từ chối, nhưng Deep ResNet-50 xác định đây là mắt thật nhờ cấu trúc phân cấp sâu.`;
        } else {
            commentaryText.innerText = `Mô hình kinh điển LBP+SVM bị đánh lừa bởi chất lượng in ấn/màn hình vi mô, nhưng Deep ResNet-50 đã ngăn chặn thành công nhờ trích xuất 2048 đặc trưng ngữ nghĩa cao.`;
        }
    }
}

// =============================================================================
// 5. GỬI YÊU CẦU PHÂN TÍCH TOÀN DIỆN ĐẾN BACKEND FASTAPI
// =============================================================================
async function triggerAnalysis() {
    const sampleSelect = document.getElementById('sample-select');
    const sampleId = sampleSelect ? sampleSelect.value : 'live_01';
    
    // Lấy attack mode từ radio buttons
    const attackRadios = document.getElementsByName('attack-mode');
    let attackMode = 'none';
    for (const r of attackRadios) {
        if (r.checked) {
            attackMode = r.value;
            break;
        }
    }

    const tauSlider = document.getElementById('tau-slider');
    const tau = tauSlider ? parseFloat(tauSlider.value) : 0.9109;

    const payload = {
        sample_id: sampleId,
        attack_mode: attackMode,
        tau: tau,
        custom_image_b64: currentCustomImageB64
    };

    try {
        const resp = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!resp.ok) {
            const err = await resp.json();
            console.error('Lỗi API analyze:', err);
            return;
        }

        const data = await resp.json();
        currentAnalysisData = data;

        // Cập nhật 4 ảnh Kính hiển vi (Chức năng 3)
        if (data.images) {
            document.getElementById('img-view-raw').src = data.images.raw;
            document.getElementById('img-view-roi').src = data.images.roi;
            document.getElementById('img-view-cam').src = data.images.gradcam;
            document.getElementById('img-view-fft').src = data.images.fft;
        }

        // Cập nhật thanh tiến trình và thông số LBP+SVM (Chức năng 2)
        document.getElementById('svm-score-num').innerText = data.lbp_svm.score.toFixed(4);
        document.getElementById('svm-progress-bar').style.width = `${data.lbp_svm.percentage}%`;
        document.getElementById('svm-lat-display').innerText = `~${data.lbp_svm.latency_ms.toFixed(1)} ms`;

        // Cập nhật thanh tiến trình và thông số ResNet-50 (Chức năng 2)
        document.getElementById('res-score-num').innerText = data.resnet50.score.toFixed(4);
        document.getElementById('res-progress-bar').style.width = `${data.resnet50.percentage}%`;
        document.getElementById('res-lat-display').innerText = `~${data.resnet50.latency_ms.toFixed(1)} ms`;

        // Cập nhật phán quyết theo tau (Chức năng 4)
        updateVerdictsLocally(tau);

    } catch (e) {
        console.error('Không thể kết nối đến backend reIris:', e);
    }
}

// =============================================================================
// 6. BIỂU ĐỒ BENCHMARK & BẢNG SO SÁNH
// =============================================================================
async function renderBenchmarkCharts() {
    try {
        const resp = await fetch('/api/benchmark-data');
        const data = await resp.json();

        // Biểu đồ Loss
        const ctxLoss = document.getElementById('chart-loss').getContext('2d');
        if (lossChart) lossChart.destroy();
        lossChart = new Chart(ctxLoss, {
            type: 'line',
            data: {
                labels: data.epochs.map(e => `Epoch ${e}`),
                datasets: [{
                    label: 'Focal Loss (Train)',
                    data: data.train_loss,
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.15)',
                    tension: 0.3,
                    fill: true,
                    pointBackgroundColor: '#ef4444',
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                    y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } }
                },
                plugins: {
                    legend: { labels: { color: '#f8fafc', font: { size: 11 } } }
                }
            }
        });

        // Biểu đồ Accuracy
        const ctxAcc = document.getElementById('chart-acc').getContext('2d');
        if (accChart) accChart.destroy();
        accChart = new Chart(ctxAcc, {
            type: 'line',
            data: {
                labels: data.epochs.map(e => `Epoch ${e}`),
                datasets: [{
                    label: 'Validation Accuracy (%)',
                    data: data.val_acc,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.15)',
                    tension: 0.2,
                    fill: true,
                    pointBackgroundColor: '#10b981',
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                    y: { min: 99.0, max: 100.1, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } }
                },
                plugins: {
                    legend: { labels: { color: '#f8fafc', font: { size: 11 } } }
                }
            }
        });

    } catch (e) {
        console.error('Lỗi nạp benchmark data:', e);
    }
}

async function renderComparisonTable() {
    try {
        const resp = await fetch('/api/benchmark-data');
        const data = await resp.json();
        const tbody = document.getElementById('comparison-table-body');
        tbody.innerHTML = '';

        data.comparison_table.forEach((row, idx) => {
            const tr = document.createElement('tr');
            tr.className = (idx % 2 === 0) ? 'bg-[#0a0f1d]' : 'bg-[#0d1424]';
            tr.innerHTML = `
                <td class="p-3 font-medium text-slate-200 border-r border-[#172238]">${row.criterion}</td>
                <td class="p-3 font-mono text-slate-400 border-r border-[#172238]">${row.lbp}</td>
                <td class="p-3 font-mono text-cyan-400 font-semibold">${row.resnet}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        console.error('Lỗi nạp bảng so sánh:', e);
    }
}

// Khởi chạy khi tài liệu nạp xong
document.addEventListener('DOMContentLoaded', () => {
    // Tải thông số hệ thống
    fetch('/api/system-status')
        .then(r => r.json())
        .then(d => {
            const devEl = document.getElementById('spec-device');
            if (devEl) devEl.innerText = `${d.device} / ${d.gpu_name.split(' ')[0]}`;
        })
        .catch(err => console.log('Status fetch error:', err));
});

