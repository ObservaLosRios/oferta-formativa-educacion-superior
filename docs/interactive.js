document.addEventListener('DOMContentLoaded', () => {
	const navLinks = document.querySelectorAll('.nav-link');
	const sections = document.querySelectorAll('.section');
	const iframeRegistry = new Map();

	const registerFrames = () => {
		document.querySelectorAll('.viz-frame[data-frame-id]').forEach((frame) => {
			const frameId = frame.dataset.frameId;
			if (!frameId) {
				return;
			}
			const fallback = Number(frame.dataset.minHeight) || 640;
			frame.style.minHeight = `${fallback}px`;
			if (!frame.style.height) {
				frame.style.height = `${fallback}px`;
			}
			iframeRegistry.set(frameId, frame);
		});
	};

	const applyIframeHeight = (frameId, payloadHeight) => {
		const iframe = iframeRegistry.get(frameId);
		if (!iframe) {
			return;
		}
		const requested = Number(payloadHeight);
		if (!Number.isFinite(requested) || requested <= 0) {
			return;
		}
		const padding = 24;
		const fallback = Number(iframe.dataset.minHeight) || 480;
		const finalHeight = Math.max(requested + padding, fallback);
		iframe.style.height = `${finalHeight}px`;
	};

	window.addEventListener('message', (event) => {
		const { data } = event;
		if (!data || data.source !== 'oferta-formativa' || !data.frameId) {
			return;
		}
		applyIframeHeight(data.frameId, data.height);
	});

	const activateSection = (sectionId) => {
		sections.forEach((section) => {
			section.classList.toggle('active', section.id === sectionId);
		});
		navLinks.forEach((link) => {
			link.classList.toggle('active', link.dataset.section === sectionId);
		});
	};

	const scrollToSection = (sectionId) => {
		const target = document.getElementById(sectionId);
		if (target) {
			target.scrollIntoView({ behavior: 'smooth', block: 'start' });
		}
	};

	navLinks.forEach((link) => {
		link.addEventListener('click', (event) => {
			event.preventDefault();
			const sectionId = link.dataset.section;
			if (!sectionId) {
				return;
			}
			activateSection(sectionId);
			scrollToSection(sectionId);
			history.replaceState(null, '', `#${sectionId}`);
		});
	});

	const initialSection = window.location.hash.replace('#', '') || 'vacantes-instituciones';
	if (document.getElementById(initialSection)) {
		activateSection(initialSection);
	} else {
		activateSection('vacantes-instituciones');
	}

	registerFrames();
});
