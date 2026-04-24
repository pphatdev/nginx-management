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
