
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

  function shrink_font(element) {
    while (element.scrollHeight > $(element).outerHeight() || element.scrollWidth > $(element).outerWidth()) {
      var size = parseInt($(element).css('font-size'));
      if (size == 1) {
        break;
      }
      $(element).css('font-size', size - 1);
    }
  }

  function format_card(card) {
    var elements = $(card).find('.shrinkable-font');
    elements.each(function(i, element) {
      shrink_font(element);
    });
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
      format_card(card);
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
      var card = backs[i];
      var back_text = $.trim($(card).text());

      if (back_text == 'SAME AS FRONT') {
        var front_page = $('.page.front:last');
        var index = i % front_page.children().length + 1;
        var front_card = front_page.children().filter(':nth-child('+ index +')');
        page.append(front_card.clone());
        card.remove();
      } else {
        page.append(card);
      }
    }
    return page;
  }

});
