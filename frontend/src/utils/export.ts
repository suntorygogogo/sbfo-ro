import * as XLSX from 'xlsx';
import type { Entry, ChildImpact } from '@/types';

export interface ExportColVisible {
  ibpStep: boolean;
  subChannel: boolean;
  account: boolean;
  brandFamily: boolean;
  description: boolean;
  nsvAud: boolean;
  nsvNzd: boolean;
  volumeLitres: boolean;
  impactPeriod: boolean;
  creator: boolean;
}

export interface ExportPhasedCol {
  key: string;
  label: string;
  year: string;
  periods: string[];
}

function n(val?: string | null): number {
  const v = parseFloat(val ?? '');
  return isNaN(v) ? 0 : v;
}

function childSum(entry: Entry, field: 'nsvAud' | 'nsvNzd' | 'volumeLitres'): number {
  if (!entry.childImpacts?.length) return n(entry[field]);
  return entry.childImpacts.reduce((s, c) => s + n(c[field]), 0);
}

const PERIOD_ORDER = ['F01','F02','F03','F04','F05','F06','F07','F08','F09','F10','F11','F12'];

function periodRange(entry: Entry): string {
  const children = entry.childImpacts ?? [];
  if (!children.length) {
    if (entry.impactPeriod && entry.impactYear) return `${entry.impactPeriod} ${entry.impactYear}`;
    return entry.impactPeriod || entry.impactYear || '';
  }
  const items = children
    .filter(c => c.impactPeriod && c.impactYear)
    .map(c => ({ period: c.impactPeriod!, year: c.impactYear!, idx: PERIOD_ORDER.indexOf(c.impactPeriod!) }));
  items.sort((a, b) => a.year !== b.year ? a.year.localeCompare(b.year) : a.idx - b.idx);
  const seen = new Set<string>();
  const uniq = items.filter(i => { const k = `${i.period}|${i.year}`; if (seen.has(k)) return false; seen.add(k); return true; });
  if (!uniq.length) return '';
  const groups: typeof uniq[number][][] = [];
  let cur = [uniq[0]];
  for (let i = 1; i < uniq.length; i++) {
    const prev = cur[cur.length - 1], curr = uniq[i];
    const isConsec = prev.year === curr.year
      ? curr.idx === prev.idx + 1
      : prev.idx === 11 && curr.idx === 0 && +curr.year === +prev.year + 1;
    if (isConsec) cur.push(curr);
    else { groups.push(cur); cur = [curr]; }
  }
  groups.push(cur);
  return groups.map(g =>
    g.length === 1 ? `${g[0].period} ${g[0].year}` : `${g[0].period} ${g[0].year} - ${g[g.length-1].period} ${g[g.length-1].year}`
  ).join(', ');
}

function phasedTotal(entry: Entry, col: ExportPhasedCol): number {
  const field = entry.country === 'New Zealand' ? 'nsvNzd' : 'nsvAud';
  return (entry.childImpacts ?? []).reduce((acc, ci) => {
    if (String(ci.impactYear) === col.year && col.periods.includes(ci.impactPeriod ?? ''))
      return acc + n(ci[field as keyof ChildImpact] as string | undefined);
    return acc;
  }, 0);
}

export function exportEntriesToExcel(
  entries: Entry[],
  colVisible: ExportColVisible,
  phasedCols: ExportPhasedCol[],
  filename: string,
) {
  type ColDef = { header: string; get: (e: Entry) => string | number };

  const metaCols: ColDef[] = [
    { header: 'Division',      get: e => e.division },
    { header: 'Country',       get: e => e.country },
    { header: 'Channel',       get: e => e.channel },
    ...(colVisible.subChannel  ? [{ header: 'Sub-Channel',  get: (e: Entry) => e.subChannel }] : []),
    ...(colVisible.account     ? [{ header: 'Account',      get: (e: Entry) => e.account }] : []),
    { header: 'Brand',         get: e => e.brand },
    ...(colVisible.brandFamily ? [{ header: 'Brand Family', get: (e: Entry) => Array.isArray(e.brandFamily) ? e.brandFamily.join(', ') : (e.brandFamily ?? '') }] : []),
    ...(colVisible.ibpStep     ? [{ header: 'IBP Step',     get: (e: Entry) => e.ibpStep ?? '' }] : []),
    { header: 'R&O',           get: e => e.rAndO },
    { header: 'Priority',      get: e => e.probability },
    ...(colVisible.description ? [{ header: 'Description',  get: (e: Entry) => e.description ?? '' }] : []),
    { header: 'Category',      get: e => e.categorisation },
    { header: 'Impact Type',   get: e => e.impactType ?? '' },
  ];

  const tailCols: ColDef[] = [
    { header: 'Owner',         get: e => e.owner },
    ...(colVisible.creator     ? [{ header: 'Creator',      get: (e: Entry) => e.creator ?? '' }] : []),
    { header: 'Status',        get: e => e.status ?? '' },
    { header: 'Last Modified', get: e => e.lastModified ?? '' },
  ];

  // ── Sheet 1: Parents ─────────────────────────────────────────────────────
  const s1Impact: ColDef[] = [
    ...(colVisible.nsvAud      ? [{ header: 'Impact (AUD)',    get: (e: Entry) => childSum(e, 'nsvAud') || '' }] : []),
    ...(colVisible.nsvNzd      ? [{ header: 'Impact (NZD)',    get: (e: Entry) => childSum(e, 'nsvNzd') || '' }] : []),
    ...(colVisible.volumeLitres? [{ header: 'Volume (Cases)',  get: (e: Entry) => childSum(e, 'volumeLitres') || '' }] : []),
    ...(colVisible.impactPeriod? [{ header: 'Impact Period',   get: (e: Entry) => periodRange(e) }] : []),
    ...phasedCols.map(col => ({ header: col.label, get: (e: Entry) => phasedTotal(e, col) || '' as string | number })),
  ];

  const s1Cols = [...metaCols, ...s1Impact, ...tailCols];
  const ws1 = XLSX.utils.aoa_to_sheet([
    s1Cols.map(c => c.header),
    ...entries.map(e => s1Cols.map(c => c.get(e))),
  ]);

  // ── Sheet 2: Details ──────────────────────────────────────────────────────
  const s2Header = [
    ...metaCols.map(c => c.header),
    ...(colVisible.impactPeriod ? ['Impact Period'] : []),
    ...(colVisible.nsvAud       ? ['Impact (AUD)'] : []),
    ...(colVisible.nsvNzd       ? ['Impact (NZD)'] : []),
    ...(colVisible.volumeLitres ? ['Volume (Cases)'] : []),
    ...tailCols.map(c => c.header),
  ];

  const s2Rows: (string | number)[][] = [];
  for (const entry of entries) {
    const meta = metaCols.map(c => c.get(entry));
    const tail = tailCols.map(c => c.get(entry));
    const children = entry.childImpacts ?? [];

    const impactRow = (period: string, year: string, aud?: string, nzd?: string, vol?: string) => [
      ...meta,
      ...(colVisible.impactPeriod ? [period && year ? `${period} ${year}` : period] : []),
      ...(colVisible.nsvAud       ? [n(aud) || ''] : []),
      ...(colVisible.nsvNzd       ? [n(nzd) || ''] : []),
      ...(colVisible.volumeLitres ? [n(vol) || ''] : []),
      ...tail,
    ];

    if (children.length > 0) {
      for (const c of children)
        s2Rows.push(impactRow(c.impactPeriod ?? '', c.impactYear ?? '', c.nsvAud, c.nsvNzd, c.volumeLitres));
    } else {
      s2Rows.push(impactRow(entry.impactPeriod ?? '', entry.impactYear ?? '', entry.nsvAud, entry.nsvNzd, entry.volumeLitres));
    }
  }

  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws1, 'Parents');
  XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet([s2Header, ...s2Rows]), 'Details');
  XLSX.writeFile(wb, `${filename}.xlsx`);
}
