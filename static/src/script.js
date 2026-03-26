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
