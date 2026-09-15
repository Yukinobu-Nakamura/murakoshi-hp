/* 村越じゅんた 公式サイト — 最小限のインタラクション */
(function () {
  'use strict';

  var header = document.getElementById('header');
  var menuBtn = document.getElementById('menuBtn');
  var nav = document.getElementById('nav');
  var totop = document.querySelector('.totop');

  /* ---------- header shrink + totop visibility ---------- */
  var ticking = false;
  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () {
      var y = window.scrollY || window.pageYOffset;
      header.classList.toggle('is-scrolled', y > 24);
      if (totop) totop.classList.toggle('is-visible', y > 600);
      ticking = false;
    });
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---------- mobile nav ---------- */
  function closeNav() {
    nav.classList.remove('is-open');
    menuBtn.setAttribute('aria-expanded', 'false');
    menuBtn.setAttribute('aria-label', 'メニューを開く');
    document.body.style.overflow = '';
  }
  if (menuBtn) {
    menuBtn.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      menuBtn.setAttribute('aria-expanded', String(open));
      menuBtn.setAttribute('aria-label', open ? 'メニューを閉じる' : 'メニューを開く');
      document.body.style.overflow = open ? 'hidden' : '';
    });
    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) closeNav();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('is-open')) closeNav();
    });
  }

  /* ---------- scroll reveal ---------- */
  var revealTargets = document.querySelectorAll(
    '.section__kicker, .section__title, .section__lead, .message__body p, ' +
    '.card, .work__text, .work__media, .sanpo__item, .sns-chip, ' +
    '.profile__side, .timeline__item, .reuse__box, .contact__sns, .activity__note'
  );
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!reduced && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          en.target.classList.add('is-on');
          io.unobserve(en.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
    revealTargets.forEach(function (el, i) {
      el.classList.add('reveal');
      el.style.transitionDelay = Math.min((i % 6) * 60, 240) + 'ms';
      io.observe(el);
    });
  }

  /* ---------- YouTube: サムネイル表示 → クリックで再生 ---------- */
  Array.prototype.forEach.call(document.querySelectorAll('.ytlite'), function (btn) {
    btn.addEventListener('click', function () {
      var id = btn.getAttribute('data-yt-id');
      if (!id) return;
      var frame = document.createElement('iframe');
      frame.src = 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(id) +
                  '?autoplay=1&rel=0';
      frame.title = btn.getAttribute('data-yt-title') || 'YouTube動画';
      frame.setAttribute('allow',
        'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share');
      frame.setAttribute('referrerpolicy', 'strict-origin-when-cross-origin');
      frame.setAttribute('allowfullscreen', '');
      btn.parentNode.replaceChild(frame, btn);
    });
  });

  /* ---------- ACTIVITY: Facebook 最新投稿3件を自動表示 ----------
     assets/data/facebook-latest.json を読み、取得できたら3枚のカードを差し替える。
     取得できない場合(オフライン / file:// で開いた場合など)はHTML側の既定カードを維持する。 */
  var fbCards = document.getElementById('fbCards');
  var fbSrc = fbCards && fbCards.getAttribute('data-fb-src');

  function fbIcon() {
    var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 24 24');
    svg.setAttribute('aria-hidden', 'true');
    var path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', 'M24 12a12 12 0 1 0-13.9 11.9v-8.4h-3V12h3V9.4c0-3 1.8-4.7 4.6-4.7 1.3 0 2.7.2 2.7.2v3h-1.5c-1.5 0-2 .9-2 1.9V12h3.3l-.5 3.5h-2.8v8.4A12 12 0 0 0 24 12z');
    svg.appendChild(path);
    return svg;
  }

  function formatDate(value) {
    if (!value) return '';
    var d = new Date(value);
    if (isNaN(d.getTime())) return '';
    return d.getFullYear() + '.' +
      ('0' + (d.getMonth() + 1)).slice(-2) + '.' +
      ('0' + d.getDate()).slice(-2);
  }

  function buildCard(post) {
    var article = document.createElement('article');
    article.className = 'card';

    var link = document.createElement('a');
    link.className = 'card__link';
    link.href = post.permalink || fbCards.getAttribute('data-fb-page') || '#';
    link.target = '_blank';
    link.rel = 'noopener';

    var figure = document.createElement('figure');
    figure.className = 'card__media';
    var img = document.createElement('img');
    img.src = post.image;
    img.loading = 'lazy';
    img.setAttribute('referrerpolicy', 'no-referrer');
    img.alt = post.alt || 'Facebookに投稿された村越じゅんたの活動写真';
    figure.appendChild(img);

    var body = document.createElement('div');
    body.className = 'card__body';

    var date = formatDate(post.date);
    if (date) {
      var meta = document.createElement('p');
      meta.className = 'card__meta';
      meta.appendChild(fbIcon());
      var dateEl = document.createElement('span');
      dateEl.textContent = date;
      meta.appendChild(dateEl);
      body.appendChild(meta);
    }

    if (post.title) {
      var title = document.createElement('h3');
      title.className = 'card__title';
      title.textContent = post.title;
      body.appendChild(title);
    }

    var text = document.createElement('p');
    text.className = 'card__text';
    text.textContent = post.text || '';
    body.appendChild(text);

    var more = document.createElement('p');
    more.className = 'card__more';
    more.textContent = 'Facebookで投稿を見る →';
    body.appendChild(more);

    link.appendChild(figure);
    link.appendChild(body);
    article.appendChild(link);
    return article;
  }

  if (fbCards && fbSrc && typeof window.fetch === 'function') {
    window.fetch(fbSrc, { cache: 'no-cache' })
      .then(function (res) {
        if (!res.ok) throw new Error('feed unavailable');
        return res.json();
      })
      .then(function (data) {
        var posts = (data && data.posts) || [];
        posts = posts.filter(function (p) { return p && p.image; }).slice(0, 3);
        if (!posts.length) return;
        fbCards.textContent = '';
        posts.forEach(function (p) { fbCards.appendChild(buildCard(p)); });
      })
      .catch(function () {
        /* 既定カードを維持する(表示は崩れない) */
      });
  }
})();
