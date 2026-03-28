// static/src/script.js

/**
 * Wrapper global para fetch que detecta sesión cerrada/expirada y recarga
 * la página automáticamente. Úsalo en lugar de fetch() directo en todas las
 * llamadas a las APIs internas.
 *
 * @param {string} url           URL a consultar
 * @param {RequestInit} options  Opciones de fetch (method, body, headers…)
 * @returns {Promise<any|null>}  JSON parseado, o null si hubo error de sesión
 *
 * Uso:
 *   const json = await apiFetch('/api/explosion/validar?...');
 *   if (!json) return;  // sesión expirada → ya se recargó la página
 */
async function apiFetch(url, options = {}) {
    try {
        const res = await fetch(url, options);

        // Intentar parsear siempre como JSON
        let data;
        try {
            data = await res.json();
        } catch {
            // Respuesta no-JSON (p.ej. redirect a login en HTML): recargar
            window.location.reload();
            return null;
        }

        // Detectar mensajes de sesión cerrada o expirada
        if (
            data?.error === "No autenticado" ||
            data?.error === "Sesión expirada"
        ) {
            window.location.reload();
            return null;
        }

        // Otros errores HTTP: loguear y devolver null
        if (!res.ok) {
            console.error(`[apiFetch] ${res.status} en ${url}`, data);
            return null;
        }

        return data;
    } catch (err) {
        // Error de red (sin conexión, CORS, etc.)
        console.error('[apiFetch] Error de red:', err);
        return null;
    }
}

// ─────────────────────────────────────────────────────────────────────────────

function validarCantidad(valor, max) {
    if (!valor || valor <= 0) {
        return {
            ok: false,
            mensaje: "Ingresa una cantidad válida"
        };
    }

    if (valor > max) {
        return {
            ok: false,
            mensaje: `No puedes producir más de ${max}`
        };
    }

    return { ok: true };
}

function aplicarEstadoValidacion({ ok, mensaje }, input, btn, error) {

    // Reset visual
    error.classList.add('hidden');
    input.classList.remove('border-red-400');

    if (!ok) {
        btn.disabled = true;
        btn.classList.add('opacity-50', 'cursor-not-allowed');

        error.textContent = mensaje;
        error.classList.remove('hidden');

        input.classList.add('border-red-400');
        return;
    }

    // OK
    btn.disabled = false;
    btn.classList.remove('opacity-50', 'cursor-not-allowed');
}

function abrirModal(idModal) {
    const modal = document.getElementById(idModal);
    if (!modal) return;

    modal.classList.remove('hidden');
    modal.classList.add('flex');
}

function cerrarModal(idModal) {
    const modal = document.getElementById(idModal);
    if (!modal) return;

    modal.classList.add('hidden');
    modal.classList.remove('flex');
}