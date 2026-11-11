import { CodeJar } from 'codejar';
import hljs from 'highlight.js/lib/core';

export default function () {
    const liveMode = document.querySelector('.js-config-live-mode');
    const form = document.querySelector('.js-config-form');
    const editor = document.querySelector('.js-config-editor');
    const mount = document.querySelector('.js-config-mount');
    const actions = document.querySelector('.js-config-actions');
    const iframe = document.querySelector('.js-iframe');
    let jar;
    let timeout;

    const highlight = (el) => {
        el.innerHTML = hljs.highlight(el.textContent, {
            language: 'yaml',
            ignoreIllegals: true,
        }).value;
    };
    const show = (code) => {
        mount.textContent = code;
        highlight(mount);
    };
    show(editor.value);

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
        mount.setAttribute('aria-readonly', !on);
        actions.hidden = !on;
        if (on) {
            // YAML forbids tab indentation, and auto-closed quotes don't type over
            jar = CodeJar(mount, highlight, {
                tab: '  ',
                indentOn: /:$/,
                addClosing: false,
            });
            mount.style.outline = ''; // CodeJar hides the focus ring
            jar.onUpdate((code) => {
                // Also fires on keys that don't edit, like arrows
                if (code === editor.value) {
                    return;
                }
                editor.value = code;
                clearTimeout(timeout);
                timeout = setTimeout(() => form.requestSubmit(), 500);
            });
            mount.focus();
        } else {
            jar.destroy();
            mount.removeAttribute('contenteditable');
            form.reset();
        }
    });

    // Esc then Tab leaves the editor instead of indenting
    mount.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            jar?.updateOptions({ catchTab: false });
        }
    });
    mount.addEventListener('focus', () => {
        jar?.updateOptions({ catchTab: true });
    });

    // Fresh about:blank per render: document.open() keeps the old window, so
    // page scripts would re-run in one scope. replace() skips history entries
    let pendingHtml;
    iframe.addEventListener('load', () => {
        const html = pendingHtml;
        pendingHtml = undefined;
        if (html === undefined) {
            return;
        }
        const doc = iframe.contentDocument;
        doc.open();
        doc.write(html);
        doc.close();
    });

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        fetch(form.action, { method: 'POST', body: new FormData(form) })
            .then((response) => response.text())
            .then((html) => {
                pendingHtml = html;
                iframe.contentWindow.location.replace('about:blank');
            })
            .catch(() => {});
    });

    form.addEventListener('reset', () => {
        clearTimeout(timeout);
        iframe.contentWindow.location.replace(iframe.src);
        show(editor.defaultValue);
    });
}
