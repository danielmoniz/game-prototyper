
$(function() {

  format_cards($('.fronts').children(), $('.backs').children());
  hide_cards();

  function hide_cards() {
    var card_sides = $('#info-div div#card_sides').text().toLowerCase();
    if (card_sides == 'fronts') {
      $('.page_container.back').hide();
    }
    if (card_sides == 'backs') {
      $('.page_container.front').hide();
    }
  }

  function get_div(class_text) {
    return jQuery('<div/>', {
      class: class_text,
    })
  }

  function get_container(side) {
    var size = $('#page_size').text();
    var container = get_div('page_container ' + side + ' ' + size);
    var sub_container = get_div('max-page-size ' + side + ' ' + size);
    container.append(sub_container);
    $('body').append(container);
    return sub_container;

  }

  function get_page(side) {
    return get_div('page ' + side);
  }

  function shrink_elements(element) {
    $(window).load(function() {
      var reduced = 0;
      while (element.scrollHeight > $(element).outerHeight() || element.scrollWidth > $(element).outerWidth()) {
        if ($(element).hasClass('shrinkable-font')) {
          var font_size = parseInt($(element).css('font-size'));
          if (font_size == 1) {
            break;
          }
          $(element).css('font-size', font_size - 1);
          reduced += 1;

          if (reduced % 2 == 0) {
            var elements = $(element).find('.text-item');
            var margin_bottom = parseInt(elements.first().css('margin-bottom'));
            elements.css('margin-bottom', margin_bottom - 1);
          }
        }

        if ($(element).hasClass('shrinkable-icons')) {
          var icons = $(element).find('.icon');
          var move_on = false;
          icons.each(function(i, icon) {
            var icon_width = $(icon).width();
            var icon_height = $(icon).height();
            if (icon_width <= 8 || icon_height <= 8) {
              move_on = true;
              /*return false;*/
            }

            var old_width = $(icon).width();
            $(icon).width(icon_width - 1);
            var new_width = $(icon).width();
            $(icon).height(icon_height - 1);
          });
          if (move_on) break;
        }
      }
    });
  }

  function format_card(card) {
    var elements = $(card).find('.shrinkable-icons');
    elements = elements.add($(card).find('.shrinkable-font'));
    elements.each(function(i, element) {
      shrink_elements(element);
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
      $(front).attr('card_number', i);
      var back = undefined;
      if (backs.length > 0) {
        back = backs[i];
        $(back).attr('card_number', i);
      }

      // set card as previous card's back if needed
      if (back && $(front).find('.placement').attr('placement') == 'back') {

        var last_back = undefined;
        for (var j=1; j<i+1; j++) {
          last_back = $(backs[i - j]);
          if ($(last_back).find('.placement').attr('placement') != 'replaced') {
            break;
          }
        }

        // add 'replaced' tag to ensure those cards are not replaced twice
        $(last_back).find('.placement').attr('placement', 'replaced');
        last_back.replaceWith(front);
        $(front).find('.placement').attr('placement', 'replaced');
        $(back).find('.placement').attr('placement', 'replaced');
        back.remove();
        continue;
      }

      current_page.append(front);
      format_card(front);
      if (back) {
        back = add_back(back, back_page, front);
      }

      if (current_page.height() > current_container.height()) {
        $(front).detach();
        if (back) {
          $(back).detach();
        }

        current_container = get_container('front');
        current_page = get_page('front');
        //current_page.append(front)
        current_container.append(current_page);

        if (backs.length > 0) {
          var back_container = get_container('back');
          var back_page = get_page('back');
          //back_page.append(back);
          //add_back(back, back_page, front);
          back_container.append(back_page);
        }
        i--;
      }
    }
  }

  function add_back(back, page, front) {
    var back_text = $.trim($(back).text());
    if (back_text != 'SAME AS FRONT') {
      page.append(back);
      format_card(back);
      return back;
    }

    $(back).remove();
    var new_back = $(front).clone().appendTo(page);
    format_card(new_back);

    return new_back;
  }

});
