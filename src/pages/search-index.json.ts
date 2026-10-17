import { getCollection } from 'astro:content';

export async function GET() {
  const posts = await getCollection('blog');
  const index = posts.map((p) => ({
    title: p.data.title,
    description: p.data.description,
    url: '/blog/' + p.id.replace(/\.md$/, '') + '/',
    category: p.data.category,
    image: p.data.image,
    date: p.data.pubDate,
    body: p.body.slice(0, 4000),
  }));
  return new Response(JSON.stringify(index), {
    headers: { 'Content-Type': 'application/json' },
  });
}
