export default function () {
    const liveMode = document.querySelector('.js-config-live-mode');
    const source = document.querySelector('.js-config-source');
    const form = document.querySelector('.js-config-form');
    const editor = document.querySelector('.js-config-editor');
    const actions = document.querySelector('.js-config-actions');
    const iframe = document.querySelector('.js-iframe');
    let timeout;

    fetch(form.action, { method: 'OPTIONS' })
        .then((response) => {
            liveMode.hidden = !response.headers.has(
                'X-Pattern-Library-Live-Edit',
            );
        })
        .catch(() => {});

    liveMode.addEventListener('click', () => {
        const on = liveMode.getAttribute('aria-pressed') !== 'true';
        liveMode.setAttribute('aria-pressed', on);
        source.hidden = on;
        form.hidden = !on;
        actions.hidden = !on;
        if (on) {
            editor.focus();
        } else {
            form.reset();
        }
    });

    editor.addEventListener('input', () => {
        clearTimeout(timeout);
        timeout = setTimeout(() => form.requestSubmit(), 500);
    });

    form.addEventListener('reset', () => {
        clearTimeout(timeout);
        iframe.src = iframe.src;
    });
}
