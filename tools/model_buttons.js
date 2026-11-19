<script id="model-buttons-js">
/* model page: Product Enquiry, Generate Quote Excel, Online Data Sheet, Generate Data Sheet, Specification sheet - all offline, Simple branded */
(function () {
  function txt(e) { return e ? e.textContent.replace(/\s+/g, ' ').trim() : ''; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function abs(u) { try { return new URL(u, location.href).href; } catch (e) { return u; } }
  function data() {
    var model = txt(document.querySelector('.select-right .title, .select-right h1, .select-right h2, .select-right p')) || 'K-CL38E-207R-R2W';
    model = model.split(' ')[0];
    var crumbs = [].map.call(document.querySelectorAll('.el-breadcrumb__inner'), txt);
    var series = crumbs.length > 1 ? crumbs[crumbs.length - 2] : '';
    var main = document.querySelector('.product-select .select-left img');
    var groups = [].map.call(document.querySelectorAll('.table-right > .general'), function (g) {
      return { name: txt(g.querySelector('.h1')), rows: [].map.call(g.querySelectorAll('.item'), function (it) {
        var t = txt(it.querySelector('.title')), all = txt(it);
        var v = all.indexOf(t) === 0 ? all.slice(t.length) : all;
        return [t.replace(/:\s*$/, ''), v.replace(/^\s*:\s*/, '').trim()];
      }) };
    });
    var acc = [].map.call(document.querySelectorAll('.table-right .el-table__body tr'), function (tr) { return [].map.call(tr.querySelectorAll('td'), txt); });
    // drop columns that are empty in every row (the live table has a blank leading column)
    if (acc.length) {
      var keep = acc[0].map(function (_, c) { return acc.some(function (r) { return r[c]; }); });
      acc = acc.map(function (r) { return r.filter(function (_, c) { return keep[c]; }); });
    }
    var thumbs = [].map.call(document.querySelectorAll('.my-carousel .prodect-item img'), function (i) { return abs(i.getAttribute('src')); });
    return { model: model, series: series, img: main ? abs(main.getAttribute('src')) : '', groups: groups, acc: acc, thumbs: thumbs };
  }
  var LOGO = '<svg width="150" height="46" viewBox="0 0 260 80" xmlns="http://www.w3.org/2000/svg"><text x="0" y="50" font-family="Manrope,Arial,sans-serif" font-size="52" font-weight="300" textLength="214" lengthAdjust="spacingAndGlyphs" fill="#111">simple</text><circle cx="232" cy="45" r="6" fill="#d7262e"/><text x="2" y="74" font-family="Manrope,Arial,sans-serif" font-size="13" textLength="210" lengthAdjust="spacing" fill="#111">LIGHTING</text></svg>';

  function sheet(mode) {
    var d = data(), w = window.open('', '_blank');
    if (!w) { alert('Please allow pop-ups for this page to open the data sheet.'); return; }
    var groups = d.groups.map(function (g) {
      return '<section><h3>' + esc(g.name) + '</h3><table>' + g.rows.map(function (r) { return '<tr><th>' + esc(r[0]) + '</th><td>' + esc(r[1] || '/') + '</td></tr>'; }).join('') + '</table></section>';
    }).join('');
    var acc = d.acc.length ? '<section class="wide"><h3>Accessories</h3><table class="acc"><tr><th>Name</th><th>Size</th><th>Type</th><th>Material</th></tr>' +
      d.acc.map(function (r) { return '<tr>' + r.map(function (c) { return '<td>' + esc(c) + '</td>'; }).join('') + '</tr>'; }).join('') + '</table></section>' : '';
    var thumbs = d.thumbs.slice(0, 3).map(function (s) { return '<img src="' + s + '">'; }).join('');
    var editable = mode === 'online';
    w.document.write('<!doctype html><html><head><meta charset="utf-8"><title>' + esc(d.model) + ' - Data Sheet - Simple Lighting</title><style>' +
      '@page{size:A4;margin:12mm}*{box-sizing:border-box}body{font-family:Manrope,Arial,sans-serif;color:#222;margin:0;background:#eee}' +
      '.bar{position:sticky;top:0;background:#111;color:#fff;padding:10px 20px;display:flex;gap:10px;align-items:center;font-size:14px}.bar button{background:#d7262e;color:#fff;border:0;padding:8px 16px;border-radius:4px;cursor:pointer;font-size:14px}.bar span{opacity:.75;margin-left:auto}' +
      '.page{width:210mm;min-height:297mm;margin:20px auto;background:#fff;padding:14mm;box-shadow:0 2px 12px rgba(0,0,0,.15)}' +
      'header{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:3px solid #d7262e;padding-bottom:8px;margin-bottom:14px}header .m{text-align:right}header .m b{font-size:22px;display:block}header .m small{color:#777}' +
      '.top{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:14px}.hero{border:1px solid #eee;display:flex;align-items:center;justify-content:center;height:70mm}.hero img{max-width:100%;max-height:100%}' +
      '.thumbs{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-top:6px}.thumbs img{width:100%;height:22mm;object-fit:contain;border:1px solid #eee}' +
      '.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}section.wide{grid-column:1/-1}h3{font-size:13px;text-transform:uppercase;letter-spacing:.06em;background:#f4f4f4;margin:0 0 4px;padding:5px 8px;border-left:3px solid #d7262e}' +
      'table{width:100%;border-collapse:collapse;font-size:11px}th,td{padding:3px 8px;border-bottom:1px solid #eee;text-align:left;vertical-align:top}th{color:#666;font-weight:600;width:45%}.acc th{width:auto}' +
      'footer{margin-top:16px;border-top:1px solid #ddd;padding-top:8px;font-size:10px;color:#777;display:flex;justify-content:space-between}' +
      '[contenteditable=true]:hover{outline:1px dashed #d7262e}' +
      '@media print{.bar{display:none}body{background:#fff}.page{margin:0;box-shadow:none;width:auto;min-height:0;padding:0}}' +
      '</style></head><body><div class="bar"><button onclick="print()">Download PDF / Print</button>' +
      (editable ? '<span>Online Data Sheet: click any text to edit it before printing</span>' : '<span>Choose “Save as PDF” in the print window to download</span>') +
      '</div><div class="page"' + (editable ? ' contenteditable="true"' : '') + '><header>' + LOGO + '<div class="m"><b>' + esc(d.model) + '</b><small>' + esc(d.series) + ' · Product Data Sheet</small></div></header>' +
      '<div class="top"><div><div class="hero">' + (d.img ? '<img src="' + d.img + '">' : '') + '</div><div class="thumbs">' + thumbs + '</div></div><div>' + groups.split('</section>')[0] + '</section></div></div>' +
      '<div class="grid">' + d.groups.slice(1).map(function (g) { return '<section><h3>' + esc(g.name) + '</h3><table>' + g.rows.map(function (r) { return '<tr><th>' + esc(r[0]) + '</th><td>' + esc(r[1] || '/') + '</td></tr>'; }).join('') + '</table></section>'; }).join('') + acc + '</div>' +
      '<footer><span>Simple Lighting Co. (H.K.) Limited · sales@simpleled.com · www.simpleled.com</span><span>Specifications subject to change without notice.</span></footer></div>' +
      (mode === 'print' ? '<script>window.onload=function(){setTimeout(function(){print()},400)}<\/script>' : '') + '</body></html>');
    w.document.close();
  }

  function quote() {
    var d = data();
    var rows = [['Simple Lighting Co. (H.K.) Limited - Quotation'], ['sales@simpleled.com', 'www.simpleled.com'], ['Date', new Date().toLocaleDateString()], [],
      ['Model', 'Series', 'Quantity', 'Unit price (USD)', 'Total (USD)'], [d.model, d.series, '1', '', ''], [], ['Specifications']];
    d.groups.forEach(function (g) { rows.push([g.name]); g.rows.forEach(function (r) { rows.push(['', r[0], r[1]]); }); });
    var csv = '﻿' + rows.map(function (r) { return r.map(function (c) { c = String(c == null ? '' : c); return /[",\n]/.test(c) ? '"' + c.replace(/"/g, '""') + '"' : c; }).join(','); }).join('\r\n');
    var a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    a.download = 'Simple-Quote-' + d.model.replace(/[^\w.-]+/g, '_') + '.csv';
    document.body.appendChild(a); a.click(); setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
  }

  document.addEventListener('click', function (e) {
    var t = e.target, b;
    if ((b = t.closest('.btn-select .enquiry'))) {
      e.preventDefault(); e.stopPropagation();
      var box = document.querySelector('.enquiry-box') || document.getElementById('bottom');
      if (box) box.scrollIntoView({ behavior: 'smooth', block: 'start' });
      var first = box && box.querySelector('input'); if (first) setTimeout(function () { first.focus({ preventScroll: true }); }, 600);
      return;
    }
    if (t.closest('.btn-select .quote-generator')) { e.preventDefault(); return quote(); }
    if (t.closest('.btn-select .editing')) { e.preventDefault(); return sheet('online'); }
    if (t.closest('.btn-select .generator')) { e.preventDefault(); return sheet('print'); }
    if (t.closest('.product-download .btn-list span')) { e.preventDefault(); return sheet('view'); }
    if ((b = t.closest('.enquiry-submit button, .enquiry-submit'))) {
      e.preventDefault();
      alert('Thank you. In this offline preview the enquiry is not sent.');
    }
  }, true);
  var css = document.createElement('style');
  css.textContent = '.product-download .btn-list span{cursor:pointer}';
  document.head.appendChild(css);
})();
</script>
