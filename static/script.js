/* ============================================
   CV Studio – Shared Utilities (script.js)
   Toast · API Calls · Blob Helpers · Download
   ============================================ */

/**
 * Base URL for the API. Change this if the backend is on a different host/port.
 * When serving the frontend from the same origin as the FastAPI backend,
 * an empty string works fine.
 */
const API_BASE = '';

/* ---------- Toast Notifications ---------- */

const TOAST_ICONS = {
  success: 'fa-circle-check',
  error: 'fa-circle-xmark',
  info: 'fa-circle-info',
};

const TOAST_DURATION = 3500;

/**
 * Show a toast notification.
 * @param {string} message  – The message text to display.
 * @param {'success'|'error'|'info'} type – Toast type (default 'info').
 */
function showToast(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast--${type}`;
  toast.innerHTML = `
    <i class="fa-solid ${TOAST_ICONS[type] || TOAST_ICONS.info}"></i>
    <span>${escapeHtml(message)}</span>
  `;
  container.appendChild(toast);

  // Auto-dismiss
  const timer = setTimeout(() => dismissToast(toast), TOAST_DURATION);
  toast.addEventListener('mouseenter', () => clearTimeout(timer));
  toast.addEventListener('mouseleave', () => {
    setTimeout(() => dismissToast(toast), 1500);
  });
}

function dismissToast(toast) {
  if (!toast.parentNode) return;
  toast.classList.add('exiting');
  toast.addEventListener('animationend', () => toast.remove());
}

/* ---------- API Call ---------- */

/**
 * Send a multipart/form-data POST request to the backend.
 * @param {string}   endpoint  – e.g. '/api/blur'
 * @param {FormData} formData  – the form data to send
 * @returns {Promise<{blob: Blob|null, json: Object|null, contentType: string}>}
 */
async function apiCall(endpoint, formData) {
  const url = `${API_BASE}${endpoint}`;
  const response = await fetch(url, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    let detail;
    try {
      const errBody = await response.json();
      detail = errBody.detail || errBody.message || `HTTP ${response.status}`;
    } catch {
      detail = `HTTP ${response.status}: ${response.statusText}`;
    }
    throw new Error(detail);
  }

  const contentType = response.headers.get('content-type') || '';
  const isJson = contentType.includes('application/json');

  if (isJson) {
    const json = await response.json();
    return { blob: null, json, contentType };
  }

  const blob = await response.blob();
  return { blob, json: null, contentType };
}

/* ---------- Blob → Image ---------- */

/**
 * Create an object URL from a Blob and set it as the src of an <img> element.
 * @param {Blob}       blob
 * @param {HTMLImageElement} imgElement
 */
function blobToImage(blob, imgElement) {
  if (imgElement._objectUrl) {
    URL.revokeObjectURL(imgElement._objectUrl);
  }
  const url = URL.createObjectURL(blob);
  imgElement._objectUrl = url;
  imgElement.src = url;
}

/* ---------- Download ---------- */

/**
 * Trigger a browser download for a Blob.
 * @param {Blob}   blob
 * @param {string} filename – e.g. 'result.png'
 */
function downloadImage(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => {
    URL.revokeObjectURL(url);
    a.remove();
  }, 100);
}

/* ---------- Helpers ---------- */

/** Escape HTML entities to prevent XSS in dynamic content. */
function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

/** Format bytes into a human-readable string. */
function formatFileSize(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

/**
 * Enforce an odd value for a slider (used for kernel sizes).
 * If the value is even, adds 1.
 * @param {number} value
 * @returns {number}
 */
function enforceOdd(value) {
  const n = Math.round(value);
  return n % 2 === 0 ? n + 1 : n;
}

/* ---------- Navbar scroll effect ---------- */

document.addEventListener('DOMContentLoaded', () => {
  const navbar = document.querySelector('.navbar');
  if (!navbar) return;

  const onScroll = () => {
    navbar.classList.toggle('scrolled', window.scrollY > 30);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
});

/* ---------- Intersection Observer for fade-in elements ---------- */

document.addEventListener('DOMContentLoaded', () => {
  const fadeEls = document.querySelectorAll('.fade-in');
  if (!fadeEls.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15 }
  );

  fadeEls.forEach((el) => observer.observe(el));
});