
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

    if (backs.length > 0) {
      var back_page = get_page('back');
      var back_container = get_container('back');
      back_container.append(back_page);
    }

    for (var i=0; i<fronts.length; i++) {
      var front = fronts[i];
      var back = undefined;
      if (backs.length > 0) {
        back = backs[i];
      }

      // set card as previous card's back if needed
      if ($(front).find('.placement').attr('placement') == 'back') {
        var last_back = $(backs[i - 1]);
        last_back.replaceWith(front);
        back.remove();
        continue;
      }

      current_page.append(front);
      format_card(front);
      if (back) {
        add_back(back, back_page, front);
      }

      if (current_page.height() > current_container.height()) {
        front.remove();
        if (back) {
          back.remove();
        }

        current_container = get_container('front');
        current_page = get_page('front');
        current_page.append(front)
        current_container.append(current_page);

        if (backs.length > 0) {
          var back_container = get_container('back');
          var back_page = get_page('back');
          back_page.append(back);
          back_container.append(back_page);
        }
      }
    }
  }

  function add_back(back, page, front) {
    var back_text = $.trim($(back).text());
    if (back_text != 'SAME AS FRONT') {
      page.append(back);
      format_card(back);
      return;
    }

    page.append($(front).clone());
    back.remove();
  }

});
