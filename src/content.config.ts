import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/blog' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.string(),
    keywords: z.string().optional(),
    category: z.string().default('small-spaces'),
    image: z.string().default('/images/pantry-hero.jpg'),
  }),
});

export const collections = { blog };
