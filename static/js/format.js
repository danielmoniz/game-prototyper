
$(function() {

  format_cards($('.fronts').children(), $('.backs').children());

  function get_div(class_text) {
    return jQuery('<div/>', {
      class: class_text,
    })
  }

  function get_container(side) {
    var container = get_div('page_container ' + side);
    var sub_container = get_div('max-page-size ' + side);
    container.append(sub_container);
    $('body').append(container);
    return sub_container;

  }

  function get_page(side) {
    return get_div('page ' + side);
  }

  function format_cards(fronts, backs) {
    var current_container = get_container('front');
    var current_page = get_page('front');
    current_page.appendTo(current_container);

    var last_width = undefined;
    var last_height = undefined;
    start_index = 0

    for (var i=0; i<fronts.length; i++) {
      var card = fronts[i];
      last_width = $(card).width();
      last_height = $(card).height();
      current_page.append(card);

      if (current_page.height() > current_container.height()) {
        card.remove();

        if (backs.length > 0) {
          var back_page = add_back_page(backs, start_index, i);
          var back_container = get_container('back');
          back_container.append(back_page);
          start_index = i;
        }

        current_container = get_container('front');
        current_page = get_page('front');
        current_page.append(card)
        current_container.append(current_page);
      }
    }

    if (backs.length > 0) {
      var back_page = add_back_page(backs, start_index, backs.length);
      var back_container = get_container('back');
      back_container.append(back_page);
    }
  }

  function add_back_page(backs, start, end) {
    var page = get_page('back');
    for (var i=start; i<end; i++) {
      page.append(backs[i]);
    }
    return page;
  }

});
