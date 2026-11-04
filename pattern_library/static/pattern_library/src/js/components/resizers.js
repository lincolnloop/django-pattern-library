const root = document.documentElement;
const handles = {};
const limits = {
    '--sidebar-width': () => [150, window.innerWidth / 2],
    '--iframe-height': () => [100, Infinity],
};

function setSize(name, size) {
    const [min, max] = limits[name]();
    const px = Math.round(Math.min(Math.max(size, min), max));
    root.style.setProperty(name, `${px}px`);
    localStorage.setItem(`pattern-library${name}`, px);
    handles[name]?.setAttribute('aria-valuenow', px);
}

// Runs before the body is parsed, so pages load at the saved sizes
export function restoreSizes() {
    for (const name of Object.keys(limits)) {
        const saved = localStorage.getItem(`pattern-library${name}`);
        if (saved) {
            setSize(name, Number(saved));
        }
    }
}

function resizable(handle, name, axis, measure) {
    handles[name] = handle;
    // The sidebar width animates, so prefer the last size set over measuring
    const getSize = () =>
        parseFloat(root.style.getPropertyValue(name)) || measure();
    handle.setAttribute('aria-valuenow', Math.round(getSize()));

    handle.addEventListener('pointerdown', (e) => {
        const offset = e[axis] - getSize();
        const move = (e) => setSize(name, e[axis] - offset);
        handle.setPointerCapture(e.pointerId);
        handle.classList.add('is-active');
        document.body.classList.add('is-resizing');
        handle.addEventListener('pointermove', move);
        handle.addEventListener(
            'lostpointercapture',
            () => {
                handle.removeEventListener('pointermove', move);
                handle.classList.remove('is-active');
                document.body.classList.remove('is-resizing');
            },
            { once: true },
        );
    });

    handle.addEventListener('keydown', (e) => {
        const step = {
            ArrowLeft: -20,
            ArrowUp: -20,
            ArrowRight: 20,
            ArrowDown: 20,
        }[e.key];
        if (step) {
            e.preventDefault();
            setSize(name, getSize() + step);
        }
    });
}

export default function () {
    const sidebar = document.querySelector('.sidebar');
    const iframe = document.querySelector('.js-iframe');
    resizable(
        document.querySelector('.js-resize-sidebar'),
        '--sidebar-width',
        'clientX',
        () => sidebar.offsetWidth,
    );
    resizable(
        document.querySelector('.js-resize-preview'),
        '--iframe-height',
        'clientY',
        () => iframe.clientHeight,
    );
}
