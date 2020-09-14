'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _postcss = require('postcss');

var _postcss2 = _interopRequireDefault(_postcss);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var shortRegExps = [/(#)([0-9ABCDEF]{1,2})(\b)/gi, /(rgba?\()(\d{1,3})(,?\s?[0-9\.]*\))/gi];

function transformColor(exp, value) {
  return value.replace(exp, function (str, prefix, match, postfix) {
    var joiner = prefix === '#' ? '' : ', ';
    return '' + prefix + match + joiner + match + joiner + match + postfix;
  });
}

function transformDecl(decl) {
  shortRegExps.forEach(function (exp) {
    /* eslint-disable no-param-reassign */
    if (exp.test(decl.value)) decl.value = transformColor(exp, decl.value);
  });
}

exports.default = _postcss2.default.plugin('postcss-color-short', function () {
  return function (style) {
    style.walkDecls(transformDecl);
  };
});
module.exports = exports['default'];
