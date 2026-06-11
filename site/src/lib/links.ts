import affiliates from '../data/affiliates.json';

export interface ResolvedLink {
  href: string;
  sponsored: boolean;
}

/** Affiliate URL when configured, otherwise the honest direct link. */
export function resolveLink(directUrl: string, affiliateKey?: string): ResolvedLink {
  if (affiliateKey && !affiliateKey.startsWith('_')) {
    const tracked = (affiliates as Record<string, string>)[affiliateKey];
    if (typeof tracked === 'string' && tracked.startsWith('http')) {
      return { href: tracked, sponsored: true };
    }
  }
  return { href: directUrl, sponsored: false };
}
