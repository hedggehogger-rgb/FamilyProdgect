export const MONTH_NAMES = [
  'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
  'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
];

export const WEEK_DAYS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

export function formatMoney(val) {
  if (val === null || val === undefined || isNaN(val) || val === '') return '0';
  return Number(val).toLocaleString('ru-RU');
}

export function formatMoneyFixed(val, digits = 2) {
  if (val === null || val === undefined || isNaN(val) || val === '') return '0,00';
  return Number(val).toLocaleString('ru-RU', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits
  });
}

export function formatDate(isoStr) {
  if (!isoStr) return '';
  return new Date(isoStr).toLocaleDateString('ru-RU');
}

export function getExactDay(isoString) {
  if (!isoString) return 0;
  const d = isoString.split('T')[0].split(' ')[0].split('-');
  return parseInt(d[2], 10);
}

export function getExactMonth(isoString) {
  if (!isoString) return 0;
  const d = isoString.split('T')[0].split(' ')[0].split('-');
  return parseInt(d[1], 10);
}

export function getExactYear(isoString) {
  if (!isoString) return 0;
  const d = isoString.split('T')[0].split(' ')[0].split('-');
  return parseInt(d[0], 10);
}