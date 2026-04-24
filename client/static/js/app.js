// ── Toast notification ─────────────────────────
let toastTimer = null;

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const msgEl = document.getElementById('toast-msg');
    const iconEl = document.getElementById('toast-icon');

    const iconMap = {
        success: { cls: 'fa-circle-check', color: 'text-emerald-400' },
        error: { cls: 'fa-circle-xmark', color: 'text-red-400' },
        info: { cls: 'fa-circle-info', color: 'text-blue-400' },
    };

    const { cls, color } = iconMap[type] || iconMap.success;
    iconEl.className = `fa-solid ${cls} ${color}`;
    msgEl.textContent = message;

    toast.classList.remove('hidden');
    toast.classList.add('show');

    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
        toast.classList.remove('show');
        toast.classList.add('hidden');
    }, 3000);
}

// ── Nginx reload ───────────────────────────────
async function reloadNginx() {
    try {
        const res = await fetch('/api/nginx/reload', { method: 'POST' });
        const data = await res.json();
        showToast(data.message, 'success');

        const el = document.getElementById('last-reload');
        if (el) el.textContent = 'Reloaded just now';
    } catch {
        showToast('Reload failed', 'error');
    }
}

// ── Helper utility functions ────────────────

// Format bytes to human readable format
function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Format date to locale string
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// Format date short
function formatDateShort(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// Get status badge HTML
function getStatusBadge(status) {
    const statusColors = {
        active: { bg: 'bg-emerald-500/10', text: 'text-emerald-400', dot: 'bg-emerald-400' },
        inactive: { bg: 'bg-gray-500/10', text: 'text-gray-400', dot: 'bg-gray-400' },
        error: { bg: 'bg-red-500/10', text: 'text-red-400', dot: 'bg-red-400' },
        up: { bg: 'bg-emerald-500/10', text: 'text-emerald-400', dot: 'bg-emerald-400' },
        down: { bg: 'bg-red-500/10', text: 'text-red-400', dot: 'bg-red-400' },
        configured: { bg: 'bg-blue-500/10', text: 'text-blue-400', dot: 'bg-blue-400' },
        pending: { bg: 'bg-yellow-500/10', text: 'text-yellow-400', dot: 'bg-yellow-400' },
        failed: { bg: 'bg-red-500/10', text: 'text-red-400', dot: 'bg-red-400' },
        draining: { bg: 'bg-yellow-500/10', text: 'text-yellow-400', dot: 'bg-yellow-400' }
    };
    
    const { bg, text, dot } = statusColors[status] || statusColors.inactive;
    return `<span class="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full ${bg} ${text}">
        <span class="w-1.5 h-1.5 rounded-full ${dot}"></span> ${status}
    </span>`;
}

// API request helper
async function apiRequest(method, endpoint, data = null) {
    const options = {
        method,
        headers: { 'Content-Type': 'application/json' }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    const res = await fetch(`/api${endpoint}`, options);
    
    if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(error.detail || `HTTP ${res.status}`);
    }
    
    return res.json();
}

// Debounce function for search/filter inputs
function debounce(func, delay) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func(...args), delay);
    };
}
