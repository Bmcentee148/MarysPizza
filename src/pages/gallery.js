// Gallery page: All / Food / Restaurant filters and a full-screen photo viewer.
// Each tile is a plain link to the image, so without JS it still opens the photo.
(function(){
  var grid = document.getElementById('gGrid');
  var box = document.getElementById('lightbox');
  if(!grid || !box) return;
  var items = Array.prototype.slice.call(grid.querySelectorAll('.g-item'));
  var buttons = document.querySelectorAll('.g-filter');
  var img = document.getElementById('lbImg'), cap = document.getElementById('lbCap'), count = document.getElementById('lbCount');
  var visible = items, current = 0, lastFocus = null;

  function setFilter(cat){
    buttons.forEach(function(b){ b.setAttribute('aria-pressed', String(b.dataset.filter === cat)); });
    items.forEach(function(it){ it.hidden = !(cat === 'all' || it.dataset.cat === cat); });
    visible = items.filter(function(it){ return !it.hidden; });
  }
  buttons.forEach(function(b){ b.addEventListener('click', function(){ setFilter(b.dataset.filter); }); });

  function show(i){
    current = (i + visible.length) % visible.length;
    var tile = visible[current], thumb = tile.querySelector('img');
    img.src = tile.getAttribute('href');
    img.alt = thumb.alt;
    cap.textContent = thumb.alt;
    count.textContent = (current + 1) + ' / ' + visible.length;
  }
  function open(i){
    lastFocus = document.activeElement;
    show(i);
    box.hidden = false;
    document.body.classList.add('lb-open');
    document.getElementById('lbClose').focus();
  }
  function close(){
    box.hidden = true;
    document.body.classList.remove('lb-open');
    if(lastFocus) lastFocus.focus();
  }

  items.forEach(function(it){
    it.addEventListener('click', function(e){
      if(e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return; // let "open in new tab" work
      e.preventDefault();
      open(visible.indexOf(it));
    });
  });
  document.getElementById('lbClose').addEventListener('click', close);
  document.getElementById('lbPrev').addEventListener('click', function(){ show(current - 1); });
  document.getElementById('lbNext').addEventListener('click', function(){ show(current + 1); });
  box.addEventListener('click', function(e){ if(e.target === box) close(); });

  document.addEventListener('keydown', function(e){
    if(box.hidden) return;
    if(e.key === 'Escape') close();
    else if(e.key === 'ArrowLeft') show(current - 1);
    else if(e.key === 'ArrowRight') show(current + 1);
    else if(e.key === 'Tab'){ // keep focus inside the viewer
      var f = box.querySelectorAll('button'), first = f[0], last = f[f.length - 1];
      if(e.shiftKey && document.activeElement === first){ e.preventDefault(); last.focus(); }
      else if(!e.shiftKey && document.activeElement === last){ e.preventDefault(); first.focus(); }
    }
  });

  // swipe left/right on phones
  var startX = null, startY = null;
  box.addEventListener('touchstart', function(e){ startX = e.touches[0].clientX; startY = e.touches[0].clientY; }, {passive:true});
  box.addEventListener('touchend', function(e){
    if(startX === null) return;
    var dx = e.changedTouches[0].clientX - startX, dy = e.changedTouches[0].clientY - startY;
    if(Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) show(current + (dx < 0 ? 1 : -1));
    startX = null;
  });
})();
