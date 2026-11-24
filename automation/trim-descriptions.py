"""Trim the 9 meta descriptions over 985px (Screaming Frog export) to <=150
chars and <=985px (Liberation Sans 14px, calibrated to SF within ~1%).
Descriptions are also the visible lead paragraph on article/category pages,
so trims keep complete sentences. Verifies each current text matches the
file before rewriting.
"""
import re
import sys
from PIL import ImageFont

FONT = ImageFont.truetype(
    '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf', 14)
BLOG = '/home/hatch/workspace/mysortednest/src/content/blog'
ROOT = '/home/hatch/workspace/mysortednest'

# (kind, locator, old, new)
FIXES = [
    ('md', 'small-apartment-blanket-storage-ideas',
     "Small apartment blanket storage ideas: baskets, ladders, ottomans, and under-bed systems that keep throws handy without the sofa pile taking over your home.",
     "Small apartment blanket storage ideas: baskets, ladders, ottomans, and under-bed systems that keep throws handy without the sofa pile."),
    ('md', 'small-apartment-storage-ideas-kids-backpacks-school-gear',
     "Small apartment storage ideas for kids' backpacks and school gear: entry hooks, cubbies, homework stations, and a nightly pack-the-bag routine in small homes.",
     "Small apartment storage ideas for kids' backpacks and school gear: entry hooks, cubbies, homework stations, and a nightly routine."),
    ('md', 'small-guest-room-storage-ideas',
     "Luggage space, closet zones, and thoughtful touches: small guest room storage ideas that make a tiny spare room feel welcoming and ready for overnight guests.",
     "Luggage space, closet zones, and thoughtful touches: small guest room storage ideas that make a tiny spare room feel welcoming."),
    ('homepage', None,
     "My Sorted Nest — practical home organization ideas for small apartments: pantry systems, closet organization, kitchen storage and clever hacks. New guides weekly.",
     "My Sorted Nest — practical home organization ideas for small apartments: pantry systems, closet organization, kitchen storage and clever hacks."),
    ('md', 'small-kitchen-cabinet-organization-ideas',
     "Small kitchen cabinet organization with 18 renter-friendly ideas: shelf risers, stackable bins, lazy Susans, lid storage, door racks, and zones that double every shelf.",
     "Small kitchen cabinet organization with 18 renter-friendly ideas: shelf risers, stackable bins, lazy Susans, lid storage, and door racks."),
    ('md', 'small-apartment-pantry-organization-ideas',
     "Small apartment pantry organization doesn't need a remodel. 21 renter-friendly ideas — door racks, shelf risers, decanting systems — that double what fits in a tiny pantry.",
     "Small apartment pantry organization doesn't need a remodel. 21 renter-friendly ideas — door racks, shelf risers, decanting systems."),
    ('md', 'studio-apartment-organization-zones',
     "Studio apartment organization starts with zoning: use rugs, shelving, and furniture placement to carve sleep, work, and living zones out of one room — no construction needed.",
     "Studio apartment organization starts with zoning: use rugs, shelving, and furniture placement to carve sleep, work, and living zones."),
    ('cat', 'kitchen',
     "Pantries, cabinets, drawers and countertops — precision systems that make even the tiniest kitchen cook like a bigger one. Renter-friendly, budget-conscious, and built for daily use.",
     "Pantries, cabinets, drawers and countertops — precision systems that make even the tiniest kitchen cook like a bigger one."),
    ('cat', 'small-spaces',
     "Living in a compact apartment, studio, or loft doesn't mean compromising on beauty or order. Explore editor-tested spatial layouts, multifunctional furniture guides, and intentional storage systems designed for smaller footprints.",
     "Living in a compact apartment, studio, or loft doesn't mean compromising on beauty or order. Explore editor-tested spatial layouts."),
]


def check(new):
    assert len(new) <= 150, f'{len(new)} chars: {new}'
    w = FONT.getlength(new)
    assert w <= 985, f'{round(w)}px: {new}'
    return round(w)


def main():
    changed = 0
    for kind, loc, old, new in FIXES:
        w = check(new)
        if kind == 'md':
            path = f'{BLOG}/{loc}.md'
            text = open(path, encoding='utf-8').read()
            m = re.search(r'^description: "(.*)"\s*$', text, re.M)
            assert m and m.group(1) == old, f'{loc}: frontmatter mismatch'
            text = text[:m.start(1)] + new + text[m.end(1):]
        elif kind == 'homepage':
            path = f'{ROOT}/src/pages/[...page].astro'
            text = open(path, encoding='utf-8').read()
            assert old in text, 'homepage description not found'
            text = text.replace(old, new, 1)
        else:  # category desc in CategoryArchive.astro
            path = f'{ROOT}/src/components/CategoryArchive.astro'
            text = open(path, encoding='utf-8').read()
            assert old in text, f'cat {loc} desc not found'
            text = text.replace(old, new, 1)
        open(path, 'w', encoding='utf-8').write(text)
        changed += 1
        print(f'  {len(old)}->{len(new)} chars, {w}px | {loc or "homepage"}')
    print(f'changed: {changed}/{len(FIXES)}')
    assert changed == len(FIXES)


if __name__ == '__main__':
    main()
