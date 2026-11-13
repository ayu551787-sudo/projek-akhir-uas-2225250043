import assert from 'node:assert/strict';
import { test } from 'node:test';

import { formatAngka, formatMentah, parseAngka, teksPersamaan } from '../js/format.js';

test('parseAngka menerima format Indonesia', () => {
  assert.equal(parseAngka('19000'), 19000);
  assert.equal(parseAngka('19.000'), 19000);
  assert.equal(parseAngka('Rp19.000'), 19000);
  assert.equal(parseAngka('Rp 8.900.000'), 8900000);
  assert.equal(parseAngka('-10'), -10);
  assert.equal(parseAngka('−10'), -10);
  assert.equal(parseAngka('1,5'), 1.5);
});

test('parseAngka menolak format tidak dikenal', () => {
  for (const s of ['', 'abc', '19.00', '--5', '1e3', null]) assert.equal(parseAngka(s), null, String(s));
});

test('formatAngka & formatMentah', () => {
  assert.equal(formatAngka(8900000), '8.900.000');
  assert.equal(formatAngka(-10), '−10');
  assert.equal(formatMentah('-19000'), '−19.000');
  assert.equal(formatMentah('-'), '−');
  assert.equal(formatMentah(''), '');
});

test('teksPersamaan', () => {
  assert.equal(teksPersamaan([2, -1, 30], ['x', 'y']), '2x − y = 30');
  assert.equal(teksPersamaan([-1, 1, 70], ['x', 'y']), '−x + y = 70');
  assert.equal(teksPersamaan(['1', '-6', '-10'], ['x', 'y']), 'x − 6y = −10');
  assert.equal(teksPersamaan([1, 2, 130000], ['a', 'b']), 'a + 2b = 130.000');
});
