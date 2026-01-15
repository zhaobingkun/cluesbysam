
(function(){
  const data = window.CLUES_PLAYLIST || [];
  const maxLevel = data.reduce((m,e)=> Math.max(m, e.levelEnd||0), 0) || 130;
  const PLACEHOLDER_IMG = 'data:image/svg+xml;utf8,<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"320\" height=\"180\" viewBox=\"0 0 320 180\" fill=\"none\"><rect width=\"320\" height=\"180\" rx=\"16\" fill=\"%23f3fbfa\" stroke=\"%23cbe7e2\" stroke-width=\"4\"/><path d=\"M135 70l70 40-70 40V70z\" fill=\"%23d6246a\"/></svg>';
  function buildHref(lvl){ return `/level/${lvl}/`; }
  function findEntry(level){ const n = Number(level); return data.find(e=>n>=e.levelStart && n<=e.levelEnd); }
  function showInlineError(scope, msg){
    let err = scope.querySelector('.jump-error');
    if(!err){
      err = document.createElement('p');
      err.className = 'search-error jump-error';
      err.style.margin = '0.3rem 0 0';
      scope.appendChild(err);
    }
    err.textContent = msg || '';
    err.style.display = msg ? 'block' : 'none';
  }
  function setupHomeGrid(){
    const grid = document.querySelector('[data-home-grid]');
    if(!grid) return;
    const filters = document.querySelector('[data-home-range]');
    const count = document.querySelector('[data-home-count]');
    const searchInput = document.querySelector('[data-home-search-input]');
    const searchBtn = document.querySelector('[data-home-search-btn]');
    const searchErr = document.querySelector('[data-home-search-error]');
    const ranges=[]; const step=40;
    for(let end=maxLevel; end>=1; end-=step){
      const start = Math.max(1, end-step+1);
      ranges.push({start, end});
    }
    let activeRange = ranges[0];
    function card(entry){
      const div=document.createElement('div');
      div.className='level-card';
      const img = document.createElement('img');
      img.className = 'card-thumb';
      img.loading = 'lazy';
      img.src = entry.videoId ? `https://img.youtube.com/vi/${entry.videoId}/hqdefault.jpg` : PLACEHOLDER_IMG;
      img.alt = `Clues by Sam Level ${entry.levelStart} thumbnail`;
      img.width = 320;
      img.height = 180;
      img.onerror = ()=>{ img.src = PLACEHOLDER_IMG; };
      const badge = document.createElement('span');
      badge.className = 'badge';
      badge.textContent = `Level ${entry.levelStart}`;
      const title = document.createElement('h3');
      title.textContent = entry.title;
      const meta = document.createElement('p');
      meta.className = 'small';
      meta.textContent = entry.subtitle;
      const link = document.createElement('a');
      link.className = 'btn btn-secondary';
      link.href = buildHref(entry.levelStart);
      link.textContent = 'Open guide';
      div.appendChild(badge);
      div.appendChild(img);
      div.appendChild(title);
      div.appendChild(meta);
      div.appendChild(link);
      return div;
    }
    function render(list){
      const limited = list.slice(0,24);
      grid.innerHTML='';
      limited.forEach(e=> grid.appendChild(card(e)));
      if(count) count.textContent = `Showing ${limited.length} of ${list.length} guides`;
    }
    function applyFilters(){
      let list = data.slice().sort((a,b)=> (b.levelStart||0) - (a.levelStart||0));
      if(activeRange){ list = list.filter(e=>e.levelStart>=activeRange.start && e.levelEnd<=activeRange.end); }
      const query = (searchInput && searchInput.value || '').trim();
      if(query){
        const num = Number(query);
        if(Number.isFinite(num)){
          list = list.filter(e=>num>=e.levelStart && num<=e.levelEnd);
        } else {
          const lower = query.toLowerCase();
          list = list.filter(e=> e.title.toLowerCase().includes(lower) || (e.subtitle||'').toLowerCase().includes(lower));
        }
      }
      render(list);
      if(searchErr) searchErr.style.display = list.length ? 'none' : 'block';
    }
    if(filters){
      filters.innerHTML='';
      ranges.forEach((r,idx)=>{
        const b=document.createElement('button');
        b.className='chip' + (idx===0 ? ' active' : '');
        b.textContent=`Level ${r.start}-${r.end}`;
        b.addEventListener('click', ()=>{
          filters.querySelectorAll('.chip').forEach(c=>c.classList.remove('active'));
          b.classList.add('active');
          activeRange = r;
          applyFilters();
        });
        filters.appendChild(b);
      });
    }
    if(searchBtn && searchInput){
      searchBtn.addEventListener('click', applyFilters);
      searchInput.addEventListener('keypress', (e)=>{ if(e.key==='Enter') applyFilters(); });
    }
    applyFilters();
  }
  function setupJump(){
    document.querySelectorAll('[data-nav-jump-btn]').forEach(btn=>{
      const scope = btn.parentElement || document;
      const input = scope.querySelector('[data-nav-jump-input]') || document.querySelector('[data-nav-jump-input]');
      if(!input) return;
      function go(){
        const n = Number(input.value);
        const entry = findEntry(n);
        if(!Number.isFinite(n) || n<1 || !entry || n>maxLevel){
          showInlineError(scope, 'Level not found.');
          return;
        }
        showInlineError(scope, '');
        window.location.href = buildHref(n);
      }
      btn.addEventListener('click', go);
      input.addEventListener('keypress', (e)=>{ if(e.key==='Enter') go(); });
    });
  }
  function setupGrid(){
    const grid = document.querySelector('[data-level-grid]');
    const filters = document.querySelector('[data-range-filters]');
    const count = document.querySelector('[data-level-count]');
    if(!grid||!filters) return;
    const ranges=[]; const step=50;
    for(let end=maxLevel; end>=1; end-=step){
      const start = Math.max(1, end-step+1);
      ranges.push({start, end});
    }
    function card(entry){
      const div=document.createElement('div');
      div.className='level-card';
      const img = document.createElement('img');
      img.className = 'card-thumb';
      img.loading = 'lazy';
      img.src = entry.videoId ? `https://img.youtube.com/vi/${entry.videoId}/hqdefault.jpg` : PLACEHOLDER_IMG;
      img.alt = `Clues by Sam Level ${entry.levelStart} thumbnail`;
      img.width = 320;
      img.height = 180;
      img.onerror = ()=>{ img.src = PLACEHOLDER_IMG; };
      const title = document.createElement('h3');
      title.textContent = entry.title;
      const meta = document.createElement('p');
      meta.className = 'small';
      meta.textContent = entry.subtitle;
      const link = document.createElement('a');
      link.className = 'btn btn-secondary';
      link.href = buildHref(entry.levelStart);
      link.textContent = 'Open guide';
      div.appendChild(img);
      div.appendChild(title);
      div.appendChild(meta);
      div.appendChild(link);
      return div;
    }
    function render(list){ grid.innerHTML=''; list.forEach(e=> grid.appendChild(card(e))); if(count) count.textContent=`${list.length} guides`; }
    filters.innerHTML='';
    const allBtn=document.createElement('button'); allBtn.className='chip active'; allBtn.textContent='All 1-'+maxLevel; filters.appendChild(allBtn);
    allBtn.addEventListener('click',()=>{ filters.querySelectorAll('.chip').forEach(c=>c.classList.remove('active')); allBtn.classList.add('active'); render(data); });
    ranges.forEach(r=>{ const b=document.createElement('button'); b.className='chip'; b.textContent=`${r.start}-${r.end}`; b.addEventListener('click',()=>{ filters.querySelectorAll('.chip').forEach(c=>c.classList.remove('active')); b.classList.add('active'); const list=data.filter(e=>e.levelStart>=r.start && e.levelEnd<=r.end); render(list); }); filters.appendChild(b); });
    render(data.slice().sort((a,b)=> (b.levelStart||0) - (a.levelStart||0)));
  }
  function setupSearch(){
    const input=document.querySelector('[data-level-search-input]');
    const btn=document.querySelector('[data-level-search-btn]');
    const err=document.querySelector('[data-level-search-error]');
    if(!input||!btn) return;
    function go(){
      const n=Number(input.value);
      const entry=findEntry(n);
      if(entry && n<=maxLevel){ if(err) err.style.display='none'; window.location.href=buildHref(n); return; }
      if(err){ err.textContent='Level not found.'; err.style.display='block'; }
    }
    btn.addEventListener('click', go);
    input.addEventListener('keypress',(e)=>{ if(e.key==='Enter') go(); });
  }
  setupJump(); setupGrid(); setupSearch(); setupHomeGrid();
})();
