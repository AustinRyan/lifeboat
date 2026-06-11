import { getCollection } from 'astro:content';

function esc(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

export async function GET(context) {
  const site = context.site?.href ?? 'http://localhost:4321/';
  const events = (await getCollection('events')).sort((a, b) =>
    b.data.announced.localeCompare(a.data.announced),
  );
  const items = events
    .map(
      (e) => `    <item>
      <title>${esc(`${e.data.product} is shutting down — survival guide`)}</title>
      <link>${site}shutdowns/${e.id}</link>
      <guid>${site}shutdowns/${e.id}</guid>
      <pubDate>${new Date(e.data.announced + 'T00:00:00Z').toUTCString()}</pubDate>
      <description>${esc(e.data.tagline)}</description>
    </item>`,
    )
    .join('\n');

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Lifeboat — survival guides for sinking software</title>
    <link>${site}</link>
    <description>SaaS shutdown deadlines, export steps, and migration guides.</description>
${items}
  </channel>
</rss>`;
  return new Response(xml, { headers: { 'Content-Type': 'application/rss+xml' } });
}
