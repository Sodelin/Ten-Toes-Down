/* Pure routing functions shared by the offline reader and its tests. */
(function (root) {
  'use strict';
  function integer(n, min, max, label) {
    if (!Number.isInteger(n) || n < min || n > max) throw new RangeError(label);
    return n;
  }
  function wrap(n) { return 1 + ((n - 1) % 40 + 40) % 40; }
  function route(department, row, emblem, dice = 0, snack = 0, bonus = 0) {
    integer(department, 1, 6, 'Department must be 1-6');
    integer(row, 1, 5, 'Mood must be 1-5');
    integer(emblem, 1, 8, 'Emblem must be 1-8');
    integer(dice, -4, 4, 'Four-dice total must be -4 to 4');
    integer(snack, 0, 2, 'Snack adjustment must be 0-2');
    if (bonus !== 0 && bonus !== 2) throw new RangeError('Stamp bonus must be zero or two');
    const base = 8 * (row - 1) + emblem;
    const local = wrap(base + dice + snack + bonus);
    return { department, row, emblem, base, local, dice, snack, bonus,
      id: 'P' + String(40 * (department - 1) + local).padStart(3, '0') };
  }
  function diceValue(die) { integer(die, 1, 6, 'Die must be 1-6'); return Math.floor((die - 1) / 2) - 1; }
  function fourDice(dice) {
    if (!Array.isArray(dice) || dice.length !== 4) throw new RangeError('Exactly four dice');
    return dice.reduce((sum, d) => sum + diceValue(d), 0);
  }
  function eligible(game, evidence, prefs) {
    const d = evidence?.developer_declarations || [];
    return (!prefs.untimed || d.includes('Playable without Timed Input')) &&
      (!prefs.camera || d.includes('Camera Comfort')) &&
      (!prefs.mouse || d.includes('Mouse Only Option')) &&
      (!prefs.waits || game.pace === 'waits') &&
      (!prefs.coop || game.native_coop === 'yes') &&
      (!prefs.memory || ['light', 'moderate'].includes(game.memory)) &&
      (!prefs.promising || game.fit_tier === 'promising');
  }
  function appeal(selection, direction, previousAppeals = 0) {
    if (previousAppeals !== 0 || selection.appeals) throw new RangeError('One appeal; then choose freely or stop');
    if (direction !== -1 && direction !== 1) throw new RangeError('Adjacent appeal must be -1 or +1');
    const local = wrap(selection.local + direction);
    return { ...selection, local, id: 'P' + String(40 * (selection.department - 1) + local).padStart(3, '0'), appeals: 1 };
  }
  function appealDepartment(selection, department, previousAppeals = 0) {
    if (previousAppeals !== 0 || selection.appeals) throw new RangeError('One appeal; then choose freely or stop');
    integer(department, 1, 6, 'Department must be 1-6');
    if (department === selection.department) throw new RangeError('Choose another department');
    return { ...selection, department, id: 'P' + String(40 * (department - 1) + selection.local).padStart(3, '0'), appeals: 1 };
  }
  root.Panorama = Object.freeze({ wrap, route, diceValue, fourDice, eligible, appeal, appealDepartment });
})(typeof globalThis !== 'undefined' ? globalThis : this);
