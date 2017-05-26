
/*
 * Determines if an element's content is greater than its height or width.
 */
function contentTooLarge(element) {
  var scrollHeightOverlapAllowance = 2; // hopefully offsets unnecessary final margin
  return element.scrollHeight > $(element).outerHeight() + scrollHeightOverlapAllowance
    || element.scrollWidth > $(element).outerWidth();
}

function shrinkElements(element) {
  $(window).load(function() {

    (function(contentTooLarge){
      // console.log('Window loaded for', $(element).parents('.card').find('.title').text())
      contentTooLarge = contentTooLarge.bind(null, element);
      var reduced = 0;

      var reduceAmount = 0.5;
      while (contentTooLarge()) {
        if (!shrinkText(element, reduceAmount)) break;
        reduced += 1;

        if (reduced % (Math.ceil(2 / reduceAmount)) == 0 && contentTooLarge()) {
          reduceMargin(element);
        }

        var iconsCanBeShrunk = true,
            frequency = 2;
        if (iconsCanBeShrunk && contentTooLarge() && (reduced % frequency == 0)) {
          iconsCanBeShrunk = shrinkIcons(element);
        }
      }
    })(contentTooLarge);
  });
}

/*
 * If applicable, finds and shrinks text within an element.
 */
function shrinkText(element, reduceAmount) {
  if ($(element).hasClass('shrinkable-font')) {
    var font_size = parseFloat($(element).css('font-size'));
    if (font_size == 1) {
      return false;
    }

    $(element).css('font-size', font_size - reduceAmount);
    // console.log($(element).parents('.card').find('.title').text(), 'reduced:', reduced)
  }
  return true;
}

// reduce margins on text-items within element if needed
function reduceMargin(element) {
  if ($(element).hasClass('shrinkable-font')) {
    var elements = $(element).find('.text-item');
    var margin_bottom = parseInt(elements.first().css('margin-bottom'));
    elements.css('margin-bottom', margin_bottom - 1);
  }
}

/*
 * If applicable, finds and shrinks icons within an element.
 */
function shrinkIcons(element) {
  if ($(element).hasClass('shrinkable-icons')) {
    var icons = $(element).find('.icon');
    icons.each(function(i, icon) {
      var icon_width = $(icon).width();
      var icon_height = $(icon).height();
      if (icon_width <= 8 || icon_height <= 8) {
        return false; // stop shrinking icons as soon as one icon is too small
      }

      $(icon).width(icon_width - 1);
      $(icon).height(icon_height - 1);
    });
  }
  return true;
}

$(function() {

  var body = document.querySelector('body');
  body.innerHTML = TextTemplater.runTemplating(body.innerHTML);
  format_cards($('.fronts').children(), $('.backs').children());
  hide_cards();
  rotatePages();

  function rotatePages() {
    if ($('#page_orientation').data("page-orientation") == 'landscape') {
      $('div.page_container').each(function(index, page) {
        page = $(page);
        var width = page.css('width');
        page.css('width', page.css('height'));
        page.css('height', width);
      });
    }
  }

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



  function format_card(card) {
    var elements = $(card).find('.shrinkable-icons');
    elements = elements.add($(card).find('.shrinkable-font'));
    elements.each(function(i, element) {
      shrinkElements(element);
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
