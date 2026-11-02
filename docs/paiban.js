/**
 * paiban 排版引擎（浏览器 / Node 通用）
 *
 * 这是 src/paiban/core.py 的逐条移植，规则与行为一一对应：
 * 只做「读起来更舒服、且几乎不可能出错」的改动，
 * 代码块、行内代码、URL 与 Markdown 链接地址一律原样保留。
 *
 * 浏览器里挂在 window.paiban，Node 里通过 require 加载。
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) {
    module.exports = factory();
  } else {
    root.paiban = factory();
  }
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  // 汉字、假名、谚文等「全角文字」的码位范围（与 core.py 一致）
  var CJK_CLASS =
    "\u3040-\u30ff" + // 平假名 / 片假名
    "\u3400-\u4dbf" + // 汉字扩展 A
    "\u4e00-\u9fff" + // 汉字基本区
    "\uf900-\ufaff" + // 兼容汉字
    "\uac00-\ud7af"; // 谚文音节
  var CJK = "[" + CJK_CLASS + "]";

  // 全角闭合标点：前面不该有空格。注意不含间隔号 ·（它是分隔符）
  var CLOSERS = "，。！？；：、）》」』】〕〉”’…";
  // 全角开启标点：后面不该有空格
  var OPENERS = "（《「『【〔〈“‘";

  function esc(s) {
    return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  var RE = {
    spaceBeforeCloser: new RegExp("[ \\t]+(?=[" + esc(CLOSERS) + "])", "g"),
    spaceAfterOpener: new RegExp("(?<=[" + esc(OPENERS) + "])[ \\t]+", "g"),
    spacesBetweenCjk: new RegExp("(?<=" + CJK + ")[ \\t]+(?=" + CJK + ")", "g"),
    cjkThenAlnum: new RegExp("(?<=" + CJK + ")(?=[A-Za-z0-9])", "g"),
    alnumThenCjk: new RegExp("(?<=[A-Za-z0-9])(?=" + CJK + ")", "g"),
    cjkThenAlpha: new RegExp("(?<=" + CJK + ")(?=[A-Za-z])", "g"),
    alphaThenCjk: new RegExp("(?<=[A-Za-z])(?=" + CJK + ")", "g"),
    trailingEol: /[ \t]+(?=\r?\n)/g,
    trailingTail: /[ \t]+$/,
    // 围栏代码块；未闭合时一直保护到文末
    fenced:
      /^[ \t]{0,3}(`{3,}|~{3,})[^\n]*\n[\s\S]*?(?:^[ \t]{0,3}\1[^\n]*(?=\r?\n|(?![\s\S]))|(?![\s\S]))/gms,
    inlineCode: /`[^`\n]*`/g,
    autolink: /<https?:\/\/[^>\s]+>/g,
    url: /https?:\/\/[^\s<>`"']+/g,
    linkDest: /\]\([^)\n]*\)/g
  };

  var PROTECTORS = [RE.fenced, RE.inlineCode, RE.autolink, RE.url, RE.linkDest];

  function protectedSpans(text) {
    var spans = [];
    for (var i = 0; i < PROTECTORS.length; i++) {
      var re = PROTECTORS[i];
      var m;
      while ((m = re.exec(text)) !== null) {
        spans.push([m.index, m.index + m[0].length]);
        if (m[0].length === 0) re.lastIndex++;
      }
    }
    if (!spans.length) return [];
    spans.sort(function (a, b) {
      return a[0] - b[0] || a[1] - b[1];
    });
    var merged = [spans[0].slice()];
    for (var k = 1; k < spans.length; k++) {
      var s = spans[k][0];
      var e = spans[k][1];
      var last = merged[merged.length - 1];
      if (s <= last[1]) {
        if (e > last[1]) last[1] = e;
      } else {
        merged.push([s, e]);
      }
    }
    return merged;
  }

  function apply(segment, opts, atLineEnd) {
    if (!segment) return segment;
    var t = segment;

    if (opts.space) {
      if (opts.digits) {
        t = t.replace(RE.cjkThenAlnum, " ").replace(RE.alnumThenCjk, " ");
      } else {
        t = t.replace(RE.cjkThenAlpha, " ").replace(RE.alphaThenCjk, " ");
      }
    }
    if (opts.cjkSpaces) {
      t = t.replace(RE.spacesBetweenCjk, "");
    }
    if (opts.punctuation) {
      t = t.replace(RE.spaceBeforeCloser, "").replace(RE.spaceAfterOpener, "");
    }
    if (opts.trailing) {
      t = t.replace(RE.trailingEol, "");
      if (atLineEnd) t = t.replace(RE.trailingTail, "");
    }
    return t;
  }

  /**
   * 修正一段文本的中文排版，选项与 Python 版 fix() 对应：
   * space / digits / cjkSpaces / punctuation / trailing / protect，默认全开。
   * 函数是幂等的：fix(fix(s)) === fix(s)。
   */
  function fix(text, options) {
    var opts = Object.assign(
      {
        space: true,
        digits: true,
        cjkSpaces: true,
        punctuation: true,
        trailing: true,
        protect: true
      },
      options || {}
    );
    if (!text) return text;

    if (!opts.protect) return apply(text, opts, true);

    var spans = protectedSpans(text);
    if (!spans.length) return apply(text, opts, true);

    var parts = [];
    var cursor = 0;
    for (var i = 0; i < spans.length; i++) {
      var start = spans[i][0];
      var end = spans[i][1];
      if (start > cursor) {
        // 只有保护区正好从行首开始时，前一段的末尾空白才算「行尾空白」
        var ch = text[start];
        var atLineEnd = start >= text.length || ch === "\r" || ch === "\n";
        parts.push(apply(text.slice(cursor, start), opts, atLineEnd));
      }
      parts.push(text.slice(start, end));
      cursor = end;
    }
    if (cursor < text.length) parts.push(apply(text.slice(cursor), opts, true));
    return parts.join("");
  }

  return { fix: fix, CJK_CLASS: CJK_CLASS };
});
