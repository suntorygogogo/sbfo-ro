export function formatDate(dateStr?: string): string {
  if (!dateStr) return "-";
  const d = new Date(dateStr);
  const dd  = String(d.getUTCDate()).padStart(2, "0");
  const mm  = String(d.getUTCMonth() + 1).padStart(2, "0");
  const yyyy = d.getUTCFullYear();
  const h24 = String(d.getUTCHours()).padStart(2, "0");
  const min = String(d.getUTCMinutes()).padStart(2, "0");
  return `${dd}/${mm}/${yyyy}, ${h24}:${min}`;
}

export function formatMoney(val?: string): string {
  if (!val) return "-";
  const num = parseFloat(val);
  return isNaN(num) ? val : num.toLocaleString();
}

export function formatVol(val?: string): string {
  if (!val) return "-";
  const num = parseFloat(val);
  return isNaN(num) ? val : num.toLocaleString();
}
