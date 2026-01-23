
(function(){
  const year = document.querySelector('[data-year]');
  if(year){ year.textContent = new Date().getFullYear(); }
  const navToggle = document.querySelector('[data-nav-toggle]');
  const navLinks = document.querySelector('.nav-links');
  if(navToggle && navLinks){ navToggle.addEventListener('click', ()=> navLinks.classList.toggle('open')); }
  const isLevelPage = /\/level\/\d+\/?$/.test(window.location.pathname);
  if (isLevelPage) {
    document.body.classList.add('level-page');
  }
  const playlist = window.CLUES_PLAYLIST || [];
  const maxLevel = playlist.reduce((m,e)=> Math.max(m, e.levelEnd||0), 0) || 135;
  function syncMaxInputs() {
    const inputs = document.querySelectorAll('[data-nav-jump-input], [data-level-search-input]');
    inputs.forEach((input) => {
      input.max = maxLevel;
      if (input.placeholder) {
        input.placeholder = input.placeholder.replace(/1-\d+/, `1-${maxLevel}`);
      }
    });
  }
  syncMaxInputs();
  // Ensure contact link exists in nav across pages
  if (navLinks && !navLinks.querySelector('a[href="/contact.html"]')) {
    const link = document.createElement('a');
    link.href = '/contact.html';
    link.textContent = 'Contact';
    navLinks.appendChild(link);
  }
  const friendLinks = [
    { label: '🐦 Twitter', url: 'https://twitter.com' },
    { label: '▶ YouTube', url: 'https://youtube.com' },
    { label: '✨ showmysites', url: 'https://showmysites.com' },
    { label: 'tikflash', url: 'https://tikflash.com' },
    { label: 'playcolorblockjam', url: 'https://playcolorblockjam.com' },
    { label: 'geckoout', url: 'https://geckoout.com' },
    { label: 'dropthecat', url: 'https://dropthecat.com' },
    { label: 'Reddit', url: 'https://www.reddit.com' },
    { label: 'dropawaylevel', url: 'https://dropawaylevel.com' },
    { label: 'aistorygenerator', url: 'https://aistorygenerator.com' },
    { label: 'lettergenie', url: 'https://lettergenie.com' },
    { label: 'you2mp4', url: 'https://you2mp4.com' },
    { label: 'monumentvalley 3', url: 'https://monumentvalley3.com' },
    { label: 'All in AI Tools', url: 'https://allinaitools.com' },
    { label: 'hexa away', url: 'https://hexaaway.com' },
    { label: 'Okei AI Tools', url: 'https://okeiaitools.com' },
    { label: 'evernote', url: 'https://evernote.com' },
    { label: 'Startup Fame', url: 'https://startupfame.com' },
    { label: 'ShowMySites Badge', url: 'https://showmysites.com/badge' },
    { label: 'DeepLaunch.io', url: 'https://deeplaunch.io' }
  ];

  function injectFooterLinks() {
    const grid = document.querySelector('.footer-grid');
    if (!grid || grid.querySelector('[data-friend-links]')) return;
    const col = document.createElement('div');
    col.setAttribute('data-friend-links','');
    const list = friendLinks.map(link => `<a href="${link.url}" target="_blank" rel="noopener">${link.label}</a>`).join('<br>');
    col.innerHTML = `<strong>Friend Links</strong><p>${list}</p>`;
    grid.appendChild(col);
  }

  function injectAnalytics() {
    if (document.querySelector('[data-analytics-gtag]')) return;
    const wrap = document.createElement('div');
    wrap.style.display = 'none';
    wrap.setAttribute('data-analytics-gtag', 'true');
    const scriptAsync = document.createElement('script');
    scriptAsync.async = true;
    scriptAsync.src = 'https://www.googletagmanager.com/gtag/js?id=G-99Y6YPMSV8';
    const scriptInline = document.createElement('script');
    scriptInline.textContent = `
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-99Y6YPMSV8');
    `;
    wrap.appendChild(scriptAsync);
    wrap.appendChild(scriptInline);
    document.body.appendChild(wrap);
  }

  function scheduleAnalytics() {
    const load = () => injectAnalytics();
    if ('requestIdleCallback' in window) {
      requestIdleCallback(load, { timeout: 4000 });
    } else {
      setTimeout(load, 2000);
    }
  }

  function injectPreconnects() {
    const head = document.head;
    if (!head) return;
    const origins = [
      'https://fonts.googleapis.com',
      'https://fonts.gstatic.com',
      'https://i.ytimg.com',
      'https://www.youtube.com',
      'https://www.youtube-nocookie.com'
    ];
    origins.forEach((href) => {
      if (head.querySelector(`link[rel=\"preconnect\"][href=\"${href}\"]`)) return;
      const link = document.createElement('link');
      link.rel = 'preconnect';
      link.href = href;
      if (href.includes('gstatic')) link.crossOrigin = 'anonymous';
      head.appendChild(link);
    });
  }

  function addJsonLd(obj){
    const script = document.createElement('script');
    script.type = 'application/ld+json';
    script.textContent = JSON.stringify(obj);
    document.head.appendChild(script);
  }

  function injectStructuredData() {
    addJsonLd({
      "@context": "https://schema.org",
      "@type": "WebSite",
      "name": "CluesBySam.org",
      "url": "https://cluesbysam.net/",
      "potentialAction": {
        "@type": "SearchAction",
        "target": "https://cluesbysam.net/level/{search_term_string}/",
        "query-input": "required name=search_term_string"
      }
    });

    const levelMatch = window.location.pathname.match(/level\/(\d+)/);
    if (levelMatch && window.CLUES_PLAYLIST) {
      const lvl = parseInt(levelMatch[1], 10);
      const entry = window.CLUES_PLAYLIST.find(e => lvl >= e.levelStart && lvl <= e.levelEnd);
      if (entry && entry.videoId) {
        const thumb = `https://i.ytimg.com/vi/${entry.videoId}/hqdefault.jpg`;
        addJsonLd({
          "@context": "https://schema.org",
          "@type": "BreadcrumbList",
          "itemListElement": [
            { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://cluesbysam.net/" },
            { "@type": "ListItem", "position": 2, "name": "Levels", "item": "https://cluesbysam.net/levels.html" },
            { "@type": "ListItem", "position": 3, "name": `Level ${lvl}`, "item": `https://cluesbysam.net/level/${lvl}/` }
          ]
        });
        addJsonLd({
          "@context": "https://schema.org",
          "@type": "VideoObject",
          "name": entry.title || `Clues by Sam Level ${lvl} Walkthrough`,
          "description": entry.subtitle || `Walkthrough for Clues by Sam level ${lvl}.`,
          "thumbnailUrl": [thumb],
          "contentUrl": entry.href || `https://www.youtube.com/watch?v=${entry.videoId}`,
          "embedUrl": `https://www.youtube-nocookie.com/embed/${entry.videoId}`,
          "publisher": { "@type": "Organization", "name": "CluesBySam.org" }
        });
      }
    }
  }

  // Replace YouTube iframes with poster + click-to-play to avoid black player
  const PLACEHOLDER_IMG = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="480" height="270" viewBox="0 0 480 270" fill="none"><rect width="480" height="270" rx="16" fill="%23f3fbfa" stroke="%23cbe7e2" stroke-width="4"/><path d="M205 95l80 40-80 40V95z" fill="%23d6246a"/></svg>';

  function setupVideoPosters() {
    document.querySelectorAll('.video-frame').forEach((frame) => {
      let videoId = frame.dataset.videoId || '';
      let title = frame.dataset.title || '';
      const existingIframe = frame.querySelector('iframe');
      if (!videoId && existingIframe) {
        const src = existingIframe.getAttribute('src') || '';
        const match = src.match(/embed\/([\w-]+)/);
        if (match && match[1]) videoId = match[1];
        title = title || existingIframe.getAttribute('title') || '';
        existingIframe.remove();
      }
      if (!videoId) return;
      const posterUrl = `https://i.ytimg.com/vi/${videoId}/hqdefault.jpg`;
      const poster = document.createElement('div');
      poster.className = 'video-poster';
      const img = document.createElement('img');
      img.src = posterUrl;
      img.loading = 'lazy';
      img.alt = title ? `${title} thumbnail` : 'Video preview';
      if (frame.dataset.priority === 'high') {
        img.setAttribute('fetchpriority', 'high');
      }
      const play = document.createElement('div');
      play.className = 'play-btn';
      play.innerHTML = '<span>Play</span>';
      poster.appendChild(img);
      poster.appendChild(play);
      frame.innerHTML = '';
      frame.appendChild(poster);
      poster.addEventListener('click', () => {
        const player = document.createElement('iframe');
        const base = frame.dataset.embedUrl || `https://www.youtube-nocookie.com/embed/${videoId}`;
        const url = base.includes('?') ? `${base}&autoplay=1` : `${base}?autoplay=1`;
        player.setAttribute('src', url);
        player.setAttribute('allow', 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture');
        player.setAttribute('allowfullscreen', 'true');
        player.setAttribute('loading', 'lazy');
        player.referrerPolicy = 'strict-origin-when-cross-origin';
        player.style.width = '100%';
        player.style.height = '100%';
        frame.innerHTML = '';
        frame.appendChild(player);
      });
    });
  }

  function setupLevelNavThumbnails() {
    const nav = document.querySelector('.level-nav');
    if (!nav || !window.CLUES_PLAYLIST) return;

    const playlist = window.CLUES_PLAYLIST;
    const path = window.location.pathname || '';
    let currentLevel = parseInt((path.match(/level\/(\d+)/) || [])[1], 10);
    if (Number.isNaN(currentLevel)) {
      const badgeText = (document.querySelector('.badge') || {}).textContent || '';
      currentLevel = parseInt((badgeText.match(/(\d+)/) || [])[1], 10);
    }
    if (!currentLevel || Number.isNaN(currentLevel)) return;

    const levelMap = new Map(playlist.flatMap(item => {
      const entries = [];
      for(let i=item.levelStart; i<=item.levelEnd; i++){ entries.push([i, item]); }
      return entries;
    }));
    const maxLevel = Math.max(...playlist.map(item => item.levelEnd));

    const thumbUrl = (levelNum) => {
      const data = levelMap.get(levelNum);
      const youtubeThumb = data && data.videoId ? `https://i.ytimg.com/vi/${data.videoId}/hqdefault.jpg` : PLACEHOLDER_IMG;
      return { fallback: youtubeThumb };
    };

    const createCard = (type, levelNum, label, href) => {
      const el = document.createElement('a');
      el.className = `nav-card ${type}`;
      if (href) el.href = href;
      const img = document.createElement('img');
      img.alt = `Clues by Sam Level ${levelNum} thumbnail`;
      img.loading = 'lazy';
      const urls = thumbUrl(levelNum);
      img.src = urls.fallback;
      img.onerror = () => { img.src = PLACEHOLDER_IMG; };
      const span = document.createElement('span');
      span.className = 'label';
      span.textContent = label;
      el.appendChild(img);
      el.appendChild(span);
      return el;
    };

    const prevLevel = currentLevel > 1 ? currentLevel - 1 : null;
    const nextLevel = currentLevel < maxLevel ? currentLevel + 1 : null;

    const grid = document.createElement('div');
    grid.className = 'level-nav-grid';
    const header = document.createElement('div');
    header.className = 'level-nav-header';
    const title = document.createElement('h3');
    title.textContent = 'Related Levels';
    const allLink = document.createElement('a');
    allLink.href = '/levels.html';
    allLink.className = 'level-nav-all';
    allLink.textContent = 'All Levels →';
    header.appendChild(title);
    header.appendChild(allLink);

    if (prevLevel) {
      grid.appendChild(createCard('prev', prevLevel, `← Level ${prevLevel}`, `/level/${prevLevel}/`));
    } else {
      const placeholder = document.createElement('div');
      placeholder.className = 'nav-card disabled';
      placeholder.innerHTML = '<div class="spacer-thumb"></div><span class="label">Start</span>';
      grid.appendChild(placeholder);
    }

    if (nextLevel) {
      grid.appendChild(createCard('next', nextLevel, `Level ${nextLevel} →`, `/level/${nextLevel}/`));
    } else {
      const placeholder = document.createElement('div');
      placeholder.className = 'nav-card disabled';
      placeholder.innerHTML = '<div class="spacer-thumb"></div><span class="label">End</span>';
      grid.appendChild(placeholder);
    }

    nav.innerHTML = '';
    nav.appendChild(header);
    nav.appendChild(grid);
  }

  function openSharePopup(url, title) {
    const w = 760;
    const h = 640;
    const left = (window.screen.width - w) / 2;
    const top = (window.screen.height - h) / 2;
    const win = window.open(url, title || 'Share', `width=${w},height=${h},top=${top},left=${left},noopener=yes`);
    if (!win || win.closed || typeof win.closed === 'undefined') {
      console.warn('Popup blocked. Please allow popups to share.');
    } else {
      try { win.focus(); } catch(e) {/* ignore */ }
    }
    return win;
  }

  function bindShareBox(box) {
    const canonical = document.querySelector('link[rel=canonical]');
    const url = (canonical && canonical.href) || window.location.href;
    const title = (document.querySelector('h1') || {}).textContent || 'Clues by Sam level guide';
    box.querySelectorAll('[data-share]').forEach((btn) => {
      btn.addEventListener('click', async () => {
        const type = btn.dataset.share;
        if (type === 'copy') {
          try {
            await navigator.clipboard.writeText(url);
            btn.textContent = 'Copied!';
            setTimeout(() => { btn.textContent = 'Copy Link'; }, 1600);
          } catch (err) {
            window.prompt('Copy this link', url);
          }
          return;
        }
        let shareUrl = '';
        if (type === 'facebook') shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`;
        if (type === 'twitter') shareUrl = `https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(title)}`;
        if (type === 'reddit') shareUrl = `https://www.reddit.com/submit?url=${encodeURIComponent(url)}&title=${encodeURIComponent(title)}`;
        if (type === 'whatsapp') shareUrl = `https://api.whatsapp.com/send?text=${encodeURIComponent(title + ' ' + url)}`;
        if (shareUrl) {
          openSharePopup(shareUrl, `Share ${title}`);
        }
      });
    });
  }

  function injectShareBox() {
    const path = window.location.pathname || '';
    if (!/\/level\/\d+(\/index\.html)?\/?$/.test(path)) return;
    const existing = Array.from(document.querySelectorAll('.share-box'));
    if (existing.length) {
      existing.forEach(bindShareBox);
      return;
    }
    const frame = document.querySelector('.video-frame');
    if (!frame) return;
    const share = document.createElement('div');
    share.className = 'share-box';
    share.innerHTML = `
      <h3>Share This Level Guide</h3>
      <p>Help other players by sharing this walkthrough guide.</p>
      <div class="share-actions">
        <button type="button" class="share-btn share-facebook" data-share="facebook">Facebook</button>
        <button type="button" class="share-btn share-twitter" data-share="twitter">Twitter</button>
        <button type="button" class="share-btn share-reddit" data-share="reddit">Reddit</button>
        <button type="button" class="share-btn share-whatsapp" data-share="whatsapp">WhatsApp</button>
        <button type="button" class="share-btn share-copy" data-share="copy">Copy Link</button>
      </div>
    `;
    bindShareBox(share);
    frame.insertAdjacentElement('afterend', share);
  }

  function init() {
    setupVideoPosters();
    setupLevelNavThumbnails();
    injectFooterLinks();
    injectStructuredData();
    injectPreconnects();
    scheduleAnalytics();
    injectShareBox();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
