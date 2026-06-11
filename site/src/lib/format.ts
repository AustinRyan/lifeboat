const FMT = new Intl.DateTimeFormat('en-US', {
  year: 'numeric',
  month: 'short',
  day: 'numeric',
  timeZone: 'UTC',
});

export function fmtDate(iso?: string): string {
  if (!iso) return 'unannounced';
  return FMT.format(new Date(iso + 'T00:00:00Z'));
}

/** Whole days from today (UTC) until the ISO date; negative if past. */
export function daysUntil(iso: string): number {
  const now = new Date();
  const today = Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate());
  return Math.round((Date.parse(iso + 'T00:00:00Z') - today) / 86_400_000);
}
