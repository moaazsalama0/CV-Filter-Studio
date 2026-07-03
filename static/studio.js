/* ============================================
   CV Studio – Studio Logic (studio.js)
   Upload · Tabs · Params · Apply · Histogram
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {
  /* ---------- DOM References ---------- */
  const uploadArea       = document.getElementById('upload-area');
  const fileInput        = document.getElementById('file-input');
  const uploadPreview    = document.getElementById('upload-preview');
  const uploadThumb      = document.getElementById('upload-thumb');
  const uploadName       = document.getElementById('upload-name');
  const uploadSize       = document.getElementById('upload-size');
  const clearBtn         = document.getElementById('clear-btn');

  const tabs             = document.querySelectorAll('.filter-tab');
  const paramSections    = document.querySelectorAll('.param-section');

  const applyBtn         = document.getElementById('apply-btn');
  const applySpinner     = applyBtn ? applyBtn.querySelector('.spinner') : null;
  const downloadBtn      = document.getElementById('download-btn');

  const originalImg      = document.getElementById('original-image');
  const resultImg        = document.getElementById('result-image');
  const resultPlaceholder = document.getElementById('result-placeholder');
  const loadingOverlay   = document.getElementById('loading-overlay');

  const originalPlaceholder = document.getElementById('original-placeholder');

  const comparisonCard    = document.getElementById('comparison-card');
  const comparisonWrap    = document.getElementById('comparison-container');
  const comparisonFullImg = comparisonWrap ? comparisonWrap.querySelector('img:not(.comparison-overlay img)') : null;
  const comparisonOverlay = comparisonWrap ? comparisonWrap.querySelector('.comparison-overlay') : null;
  const comparisonOverlayImg = comparisonOverlay ? comparisonOverlay.querySelector('img') : null;
  const comparisonHandle  = comparisonWrap ? comparisonWrap.querySelector('.comparison-handle') : null;

  const histogramCard     = document.getElementById('histogram-card');
  const histCanvasWrap    = document.getElementById('histogram-canvas-wrap');
  const histCanvas        = document.getElementById('histogram-canvas');

  /* ---------- State ---------- */
  let currentFile = null;        // the uploaded File object
  let resultBlob  = null;        // last result Blob
  let currentFilter = 'blur';    // active filter tab
  let isApplying = false;

  /* ========================================
     1. IMAGE UPLOAD
     ======================================== */

  if (uploadArea && fileInput) {
    // Click to browse
    uploadArea.addEventListener('click', (e) => {
      if (e.target.closest('.upload-preview__clear')) return;
      fileInput.click();
    });

    // File selected via input
    fileInput.addEventListener('change', () => {
      if (fileInput.files.length) handleFile(fileInput.files[0]);
    });

    // Drag & drop
    uploadArea.addEventListener('dragover', (e) => {
      e.preventDefault();
      uploadArea.classList.add('drag-over');
    });

    uploadArea.addEventListener('dragleave', () => {
      uploadArea.classList.remove('drag-over');
    });

    uploadArea.addEventListener('drop', (e) => {
      e.preventDefault();
      uploadArea.classList.remove('drag-over');
      const files = e.dataTransfer.files;
      if (files.length && files[0].type.startsWith('image/')) {
        handleFile(files[0]);
      } else {
        showToast('Please drop a valid image file.', 'error');
      }
    });
  }

  function handleFile(file) {
    if (!file.type.startsWith('image/')) {
      showToast('Unsupported file type. Please select an image.', 'error');
      return;
    }
    currentFile = file;

    // Show thumbnail & original preview
    const reader = new FileReader();
    reader.onload = (e) => {
      const dataUrl = e.target.result;
      uploadThumb.src = dataUrl;
      originalImg.src = dataUrl;
      originalImg.style.display = '';
      if (originalPlaceholder) originalPlaceholder.style.display = 'none';
    };
    reader.readAsDataURL(file);

    uploadName.textContent = file.name;
    uploadSize.textContent = formatFileSize(file.size);
    uploadPreview.classList.add('active');

    // Clear previous result
    clearResult();
    showToast('Image loaded successfully.', 'success');
  }

  if (clearBtn) {
    clearBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      currentFile = null;
      fileInput.value = '';
      uploadPreview.classList.remove('active');
      uploadThumb.src = '';
      originalImg.src = '';
      clearResult();
    });
  }

  function clearResult() {
    resultBlob = null;
    resultImg.src = '';
    resultImg.style.display = 'none';
    if (resultImg._objectUrl) URL.revokeObjectURL(resultImg._objectUrl);
    resultPlaceholder.style.display = '';
    if (loadingOverlay) loadingOverlay.classList.remove('active');
    if (downloadBtn) downloadBtn.classList.remove('visible');
    if (histCanvasWrap) histCanvasWrap.classList.remove('visible');
    if (histogramCard) histogramCard.style.display = 'none';
    if (comparisonCard) comparisonCard.style.display = 'none';
    if (comparisonWrap) comparisonWrap.style.display = 'none';
    if (comparisonOverlay) comparisonOverlay.style.width = '50%';
    if (comparisonHandle) comparisonHandle.style.left = '50%';
  }

  /* ========================================
     2. FILTER TAB SWITCHING
     ======================================== */

  tabs.forEach((tab) => {
    tab.addEventListener('click', () => {
      const filter = tab.dataset.filter;
      if (!filter) return;

      currentFilter = filter;

      // Activate tab
      tabs.forEach((t) => t.classList.remove('active'));
      tab.classList.add('active');

      // Show corresponding params
      paramSections.forEach((s) => s.classList.remove('active'));
      const target = document.getElementById(`params-${filter}`);
      if (target) target.classList.add('active');

      // Clear previous result (keep uploaded image)
      clearResult();
    });
  });

  /* ========================================
     3. SLIDER VALUE DISPLAYS
     ======================================== */

  document.querySelectorAll('.param-slider').forEach((slider) => {
    const display = document.getElementById(slider.id + '-val');
    if (!display) return;

    const update = () => {
      let val = Number(slider.value);

      // Enforce odd for kernel-like sliders
      if (slider.dataset.odd === 'true') {
        val = enforceOdd(val);
        slider.value = val;
      }

      display.textContent = slider.dataset.float === 'true' ? val.toFixed(1) : val;
    };

    slider.addEventListener('input', update);
    update();
  });

  /* ========================================
     4. CONDITIONAL PARAM VISIBILITY
     ======================================== */

  // Blur – show sigma only for gaussian, bilateral params only for bilateral, etc.
  const blurKernelSelect = document.getElementById('blur-kernel-type');
  if (blurKernelSelect) {
    const showBlurParams = () => {
      const type = blurKernelSelect.value;
      toggleParam('blur-sigma-x-group', type === 'gaussian');
      toggleParam('blur-bilateral-group', type === 'bilateral');
    };
    blurKernelSelect.addEventListener('change', showBlurParams);
    showBlurParams();
  }

  // Threshold – show adaptive params only for adaptive, hide value for otsu/adaptive
  const threshTypeSelect = document.getElementById('threshold-type');
  if (threshTypeSelect) {
    const showThreshParams = () => {
      const type = threshTypeSelect.value;
      toggleParam('threshold-value-group', type === 'binary');
      toggleParam('threshold-adaptive-group', type === 'adaptive');
    };
    threshTypeSelect.addEventListener('change', showThreshParams);
    showThreshParams();
  }

  // Edge – show method-specific params
  const edgeMethodSelect = document.getElementById('edge-method');
  if (edgeMethodSelect) {
    const showEdgeParams = () => {
      const method = edgeMethodSelect.value;
      toggleParam('edge-canny-group', method === 'canny');
      toggleParam('edge-sobel-group', method === 'sobel' || method === 'scharr');
      toggleParam('edge-laplacian-group', method === 'laplacian');
    };
    edgeMethodSelect.addEventListener('change', showEdgeParams);
    showEdgeParams();
  }

  function toggleParam(id, show) {
    const el = document.getElementById(id);
    if (el) el.style.display = show ? '' : 'none';
  }

  /* ========================================
     5. OUTPUT FORMAT (PNG / JPEG)
     ======================================== */

  // Radio buttons for format – handled during apply

  /* ========================================
     6. APPLY FILTER
     ======================================== */

  if (applyBtn) {
    applyBtn.addEventListener('click', applyFilter);
  }

  async function applyFilter() {
    if (!currentFile) {
      showToast('Please upload an image first.', 'error');
      return;
    }
    if (isApplying) return;
    isApplying = true;

    // UI: loading state
    applyBtn.classList.add('loading');
    if (applyBtn.querySelector('.btn-text')) applyBtn.querySelector('.btn-text').textContent = 'Processing…';
    if (loadingOverlay) loadingOverlay.classList.add('active');
    if (downloadBtn) downloadBtn.classList.remove('visible');
    if (histCanvasWrap) histCanvasWrap.classList.remove('visible');

    try {
      const formData = new FormData();
      formData.append('image', currentFile);

      // Get output format (PNG / JPEG)
      const formatRadio = document.querySelector('input[name="output-format"]:checked');
      if (formatRadio) formData.append('format', formatRadio.value);

      // Append filter-specific params
      appendFilterParams(formData);

      // Determine endpoint
      const endpoint = getEndpoint();
      if (!endpoint) throw new Error('Unknown filter type.');

      const result = await apiCall(endpoint, formData);

      if (result.json) {
        // Histogram JSON response → draw chart
        drawHistogram(result.json);
      } else if (result.blob) {
        // Image response
        blobToImage(result.blob, resultImg);
        resultBlob = result.blob;
        resultImg.style.display = '';
        resultPlaceholder.style.display = 'none';

        // Enable download
        if (downloadBtn) {
          downloadBtn.classList.add('visible');
          const ext = result.contentType.includes('jpeg') || result.contentType.includes('jpg') ? 'jpg' : 'png';
          downloadBtn.onclick = () => downloadImage(result.blob, `cv-studio-${currentFilter}.${ext}`);
        }

        // Show comparison slider
        setupComparison();
        showToast('Filter applied successfully!', 'success');
      }
    } catch (err) {
      showToast(err.message || 'An error occurred while processing the image.', 'error');
    } finally {
      isApplying = false;
      applyBtn.classList.remove('loading');
      if (applyBtn.querySelector('.btn-text')) applyBtn.querySelector('.btn-text').textContent = 'Apply Filter';
      if (loadingOverlay) loadingOverlay.classList.remove('active');
    }
  }

  function getEndpoint() {
    const map = {
      blur: '/api/blur',
      threshold: '/api/threshold',
      edge: '/api/edge-detection',
      histogram: '/api/histogram',
    };
    return map[currentFilter] || null;
  }

  function appendFilterParams(formData) {
    switch (currentFilter) {
      case 'blur':
        formData.append('kernel_type', getVal('blur-kernel-type', 'gaussian'));
        formData.append('size', getVal('blur-size', '5'));
        if (getVal('blur-kernel-type') === 'gaussian') {
          formData.append('sigma_x', getVal('blur-sigma-x', '1.0'));
        }
        if (getVal('blur-kernel-type') === 'bilateral') {
          formData.append('diameter', getVal('blur-diameter', '9'));
          formData.append('sigma_color', getVal('blur-sigma-color', '75'));
          formData.append('sigma_space', getVal('blur-sigma-space', '75'));
        }
        break;

      case 'threshold':
        formData.append('type', getVal('threshold-type', 'binary'));
        formData.append('value', getVal('threshold-value', '127'));
        formData.append('max_value', getVal('threshold-max-value', '255'));
        formData.append('invert', isChecked('threshold-invert') ? 'true' : 'false');
        if (getVal('threshold-type') === 'adaptive') {
          formData.append('block_size', getVal('threshold-block-size', '11'));
          formData.append('C', getVal('threshold-C', '5'));
          formData.append('adaptive_method', getVal('threshold-adaptive-method', 'mean'));
        }
        break;

      case 'edge':
        formData.append('method', getVal('edge-method', 'canny'));
        if (getVal('edge-method') === 'canny') {
          formData.append('low_threshold', getVal('edge-low-threshold', '50'));
          formData.append('high_threshold', getVal('edge-high-threshold', '150'));
        }
        if (['sobel', 'scharr'].includes(getVal('edge-method'))) {
          formData.append('dx', getVal('edge-dx', '1'));
          formData.append('dy', getVal('edge-dy', '0'));
        }
        if (getVal('edge-method') === 'laplacian') {
          formData.append('kernel_size', getVal('edge-kernel-size', '3'));
        }
        break;

      case 'histogram': {
        const histFormat = document.querySelector('input[name="hist-format"]:checked');
        if (histFormat) formData.append('format', histFormat.value);
        formData.append('color', isChecked('histogram-color') ? 'true' : 'false');
        break;
      }
    }
  }

  /* ---------- Value Helpers ---------- */

  function getVal(id, fallback) {
    const el = document.getElementById(id);
    if (!el) return fallback || '';
    return el.value;
  }

  function isChecked(id) {
    const el = document.getElementById(id);
    return el ? el.checked : false;
  }

  /* ========================================
     7. HISTOGRAM CHART (Canvas)
     ======================================== */

  function drawHistogram(data) {
    if (!histCanvas) return;
    if (histogramCard) histogramCard.style.display = '';
    histCanvasWrap.classList.add('visible');
    resultPlaceholder.style.display = 'none';

    const ctx = histCanvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    const displayWidth = histCanvas.parentElement.clientWidth - 32; // padding
    const displayHeight = 280;

    histCanvas.width = displayWidth * dpr;
    histCanvas.height = displayHeight * dpr;
    histCanvas.style.width = displayWidth + 'px';
    histCanvas.style.height = displayHeight + 'px';
    ctx.scale(dpr, dpr);

    // Clear
    ctx.clearRect(0, 0, displayWidth, displayHeight);

    const padding = { top: 20, right: 16, bottom: 36, left: 48 };
    const chartW = displayWidth - padding.left - padding.right;
    const chartH = displayHeight - padding.top - padding.bottom;

    // Determine channels
    let channels = [];
    if (data.b && data.g && data.r) {
      channels = [
        { label: 'Blue', data: data.b, color: 'rgba(59,130,246,0.7)', fill: 'rgba(59,130,246,0.15)' },
        { label: 'Green', data: data.g, color: 'rgba(34,197,94,0.7)', fill: 'rgba(34,197,94,0.15)' },
        { label: 'Red', data: data.r, color: 'rgba(239,68,68,0.7)', fill: 'rgba(239,68,68,0.15)' },
      ];
    } else if (data.hist) {
      channels = [
        { label: 'Intensity', data: data.hist, color: 'rgba(168,139,250,0.8)', fill: 'rgba(168,139,250,0.2)' },
      ];
    } else {
      showToast('Unexpected histogram data format.', 'error');
      return;
    }

    // Find max across all channels
    let maxVal = 0;
    channels.forEach((ch) => {
      const m = Math.max(...ch.data);
      if (m > maxVal) maxVal = m;
    });
    if (maxVal === 0) maxVal = 1;

    const numBins = channels[0].data.length;
    const barW = chartW / numBins;

    // Draw grid lines
    ctx.strokeStyle = 'rgba(255,255,255,0.06)';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
      const y = padding.top + (chartH / 4) * i;
      ctx.beginPath();
      ctx.moveTo(padding.left, y);
      ctx.lineTo(padding.left + chartW, y);
      ctx.stroke();

      // Y-axis labels
      const val = Math.round(maxVal * (1 - i / 4));
      ctx.fillStyle = 'rgba(255,255,255,0.35)';
      ctx.font = '10px Inter, sans-serif';
      ctx.textAlign = 'right';
      ctx.textBaseline = 'middle';
      ctx.fillText(val, padding.left - 6, y);
    }

    // Draw each channel
    channels.forEach((ch) => {
      // Filled area
      ctx.beginPath();
      ctx.moveTo(padding.left, padding.top + chartH);
      ch.data.forEach((val, i) => {
        const x = padding.left + i * barW;
        const h = (val / maxVal) * chartH;
        ctx.lineTo(x, padding.top + chartH - h);
      });
      ctx.lineTo(padding.left + (numBins - 1) * barW, padding.top + chartH);
      ctx.closePath();
      ctx.fillStyle = ch.fill;
      ctx.fill();

      // Line on top
      ctx.beginPath();
      ch.data.forEach((val, i) => {
        const x = padding.left + i * barW;
        const h = (val / maxVal) * chartH;
        if (i === 0) ctx.moveTo(x, padding.top + chartH - h);
        else ctx.lineTo(x, padding.top + chartH - h);
      });
      ctx.strokeStyle = ch.color;
      ctx.lineWidth = 1.5;
      ctx.stroke();
    });

    // X-axis labels
    ctx.fillStyle = 'rgba(255,255,255,0.35)';
    ctx.font = '10px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    const labelStep = Math.ceil(numBins / 8);
    for (let i = 0; i < numBins; i += labelStep) {
      const x = padding.left + i * barW;
      ctx.fillText(i, x, padding.top + chartH + 8);
    }
    // Last label
    ctx.fillText(numBins - 1, padding.left + (numBins - 1) * barW, padding.top + chartH + 8);

    // X-axis title
    ctx.fillStyle = 'rgba(255,255,255,0.4)';
    ctx.font = '11px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Pixel Value', padding.left + chartW / 2, displayHeight - 6);

    // Legend
    const legendX = padding.left + 8;
    let legendY = padding.top + 8;
    channels.forEach((ch) => {
      ctx.fillStyle = ch.color;
      ctx.fillRect(legendX, legendY, 12, 3);
      ctx.fillStyle = 'rgba(255,255,255,0.6)';
      ctx.font = '10px Inter, sans-serif';
      ctx.textAlign = 'left';
      ctx.textBaseline = 'middle';
      ctx.fillText(ch.label, legendX + 18, legendY + 1.5);
      legendY += 16;
    });

    showToast('Histogram generated.', 'info');
  }

  /* ========================================
     8. COMPARISON SLIDER
     ======================================== */

  function setupComparison() {
    if (!comparisonWrap || !comparisonOverlay || !comparisonHandle || !comparisonOverlayImg) return;

    // Only show comparison if we have both images
    if (!originalImg.src || !resultImg.src) return;

    // Use the result image as the full-width background, and original as the overlay
    if (comparisonCard) comparisonCard.style.display = '';
    comparisonWrap.style.display = 'block';
    if (comparisonFullImg) comparisonFullImg.src = resultImg.src;
    if (comparisonOverlayImg) comparisonOverlayImg.src = originalImg.src;

    // Reset position
    updateComparison(0.5);

    // Drag handling
    let isDragging = false;

    const getPosition = (e) => {
      const rect = comparisonWrap.getBoundingClientRect();
      const clientX = e.touches ? e.touches[0].clientX : e.clientX;
      return Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
    };

    comparisonWrap.addEventListener('mousedown', (e) => { isDragging = true; updateComparison(getPosition(e)); });
    comparisonWrap.addEventListener('touchstart', (e) => { isDragging = true; updateComparison(getPosition(e)); }, { passive: true });

    window.addEventListener('mousemove', (e) => { if (isDragging) updateComparison(getPosition(e)); });
    window.addEventListener('touchmove', (e) => { if (isDragging) updateComparison(getPosition(e)); }, { passive: true });

    window.addEventListener('mouseup', () => { isDragging = false; });
    window.addEventListener('touchend', () => { isDragging = false; });
  }

  function updateComparison(ratio) {
    if (!comparisonOverlay || !comparisonHandle) return;
    const pct = ratio * 100;
    comparisonOverlay.style.width = pct + '%';
    comparisonHandle.style.left = pct + '%';
  }

  /* ========================================
     9. KEYBOARD SHORTCUT (Enter to apply)
     ======================================== */

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.target.matches('input, select, textarea')) {
      applyBtn && applyBtn.click();
    }
  });
});