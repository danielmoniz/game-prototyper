
// This value should be dynamic.
var iconsPath = 'resource/';

var TextTemplater = {

  runTemplating: function(text) {
    // Eg. (( icon: wood, large ))
    text = TextTemplater.runReplaceFunction(text,
      TextTemplater.getReplacementOutputText, /\(\([,-\s\w:]+\)\)/g);
    // Eg. {{ effect| stuff goes here }}
    text = TextTemplater.runReplaceFunction(text,
      TextTemplater.getReplacementWrapperText, /{{.*?}}/g);
    return text;
  },

  runReplaceFunction: function(text, replaceFunction, pattern) {
    var match = pattern.exec(text);
    while (match != null) {
      text = replaceFunction.bind(this)(pattern, match);
      match = pattern.exec(text);
    }
    return text;
  },

  /*
   * Used for wrapping text with spans. Eg:
   * {{ effect|Some text here }}  --> <span class="effect">Some text here</span>
   */
  getReplacementWrapperText: function(pattern, match) {
    var pieces = this.separateMatchKeyFromValue(match, pattern, '|');
    var [key, value] = pieces;

    var newText = "<span class='tag " + key + "'>" + value + "</span>";
    var text = match.input;
    return text.slice(0, match.index) + newText + text.slice(pattern.lastIndex);
  },

  /*
   * Used for replacing text with content. Eg:
   * (( icon:wood,tiny ))  --> <img src='...wood.png' class='tiny'>
   * (( wood, large ))  // still counts as an icon by default
   */
  getReplacementOutputText: function(pattern, match) {
    var pieces = this.separateMatchKeyFromValue(match, pattern, ':');
    if (pieces.length === 1) {
      pieces = ['icon', pieces[0]]; // assume an icon if not specified
    }
    var [key, value] = pieces;
    var values = value.split(',');
    var keyword = values[0].trim();

    var newText = "";
    if (key === 'icon') {
      newText = this.makeIcon(keyword, values.slice(1));
    } else {
      newText = "[[" + key + " NOT SUPPORTED]]";
    }
    var text = match.input;
    return text.slice(0, match.index) + newText + text.slice(pattern.lastIndex);
  },

  /*
   * Parses templating code to get to the inner pieces.
   * Returns a key and a value as an array given a match, pattern, and separator.
   * The match and pattern are used to determine where the parts to replace
   * start and end.
   */
  separateMatchKeyFromValue: function(match, pattern, separator) {
    var text = match.input;
    var replaceMe = text.slice(match.index, pattern.lastIndex);
    // console.log(replaceMe);
    var innerContents = match[0].slice(2, -2);

    var pieces = innerContents.split(separator);
    // only separate on first separator. Should just be key and value.
    if (pieces.length > 1) {
      pieces[1] = pieces.slice(1).join(separator);
    }
    return pieces.map(function(piece) {
      return piece.trim();
    });
  },

  /*
   * Makes an icon given a type of icon and a list of classes.
   */
  makeIcon: function(type, classes) {
    var classesString = '';
    var sizes = ['tiny', 'small', 'medium', 'large', 'huge'];
    var defaultSizeClass = ' small';
    if (classes) {
      classes = classes.map(function(className) {
        if (sizes.indexOf(className.trim()) !== -1) {
          defaultSizeClass = "";
        }
        return className.trim();
      });
      classesString = classes.join(' '); }
    return "<img src='" + iconsPath + type.toLowerCase() + ".png' class='icon" + defaultSizeClass + " " + classesString + "' />";
  },

  // builds an array instead of a string
  runReplaceFunction2: function(text, replaceFunction, pattern) {
    var startIndex = 0;
    var result = [];
    var match = pattern.exec(text);
    while (match != null) {
      var templatedChunks = replaceFunction.call(this, pattern, match, startIndex);
      result = result.concat(templatedChunks);
      startIndex = pattern.lastIndex;
      match = pattern.exec(text);
    }
    result.push(text.slice(startIndex));
    return result.join("");
  },

  /*
   * Used for wrapping text with spans. Eg:
   * {{ effect|Some text here }}  --> <span class="effect">Some text here</span>
   */
  getReplacementWrapperText2: function(pattern, match, startIndex=0) {
    var pieces = this.separateMatchKeyFromValue(match, pattern, '|');
    var [key, value] = pieces;

    var newText = "<span class='tag " + key + "'>" + value + "</span>";
    var text = match.input;
    return [text.slice(startIndex, match.index), newText];
  },
};

// var text = "The following bit {{ loss | Is in a span and has an (( metal, large )) image. }} The ((icon:best)). Really.";
var text = "First tag: {{ tagname1|this is tag 1}}. Second tag: {{ tagname2|this is tag 2}}. Those are both tags."
console.log(text);
text = TextTemplater.runTemplating(text);
