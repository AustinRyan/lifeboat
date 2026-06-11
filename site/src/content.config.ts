import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const events = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/events' }),
  schema: z.object({
    product: z.string(),
    tagline: z.string(),
    status: z.enum(['sinking', 'sunk']),
    announced: z.string(), // ISO date the shutdown was announced
    deadline: z.string().optional(), // ISO date service goes dark
    sourceUrl: z.string().url(), // primary-source announcement
    exportUrl: z.string().url().optional(), // where users export their data
    alternatives: z.array(
      z.object({
        name: z.string(),
        url: z.string().url(),
        pitch: z.string(),
        affiliateKey: z.string().optional(),
      }),
    ),
  }),
});

export const collections = { events };
