// Promotions page: hide promos whose data-ends date (YYYY-MM-DD, last day shown) has passed.
(function(){
  var cards = document.querySelectorAll('.promo-card[data-ends]');
  var now = new Date(), shown = 0;
  cards.forEach(function(card){
    var p = card.dataset.ends.split('-').map(Number);
    var endsAfter = new Date(p[0], p[1] - 1, p[2] + 1); // midnight after the last day, visitor's time
    if(now >= endsAfter) card.hidden = true; else shown++;
  });
  var empty = document.getElementById('promoEmpty');
  if(empty && !shown) empty.hidden = false;
})();
