"""Trim MSN article titles to <=60 chars (full <title> after the brand suffix
is dropped on article pages). Rule 1: drop the trailing parenthetical.
Rule 2 (49 titles): hand-written trims cutting the trailing benefit clause.
Verifies each CSV title matches the article frontmatter before rewriting.
"""
import csv
import re
import sys

CSV = '/home/hatch/workspace/user/files/page_titles_over_60_characters.csv'
BLOG = '/home/hatch/workspace/mysortednest/src/content/blog'
SUFFIX = ' | My Sorted Nest'

MANUAL = {
    "Minimalist Decluttering: Where to Start When You're Overwhelmed": "Minimalist Decluttering: Where to Start",
    "17 Small Desk Supply Organization Ideas for Tiny Home Offices": "17 Small Desk Supply Organization Ideas",
    "17 Closet Shelf Organization Ideas That Turn Dead Space Into Storage": "17 Closet Shelf Organization Ideas",
    "18 Small Freezer Organization Ideas That End the Frozen Mystery Bag Era": "18 Small Freezer Organization Ideas",
    "15 Small Bedroom Storage Ideas for Couples Sharing a Tiny Room": "15 Small Bedroom Storage Ideas for Couples",
    "21 Small Apartment Pantry Organization Ideas That Actually Work": "21 Small Apartment Pantry Organization Ideas",
    "16 Laundry Room Wall Organization Ideas for Small Laundry Spaces": "16 Laundry Room Wall Organization Ideas",
    "16 Small Apartment Storage Ideas for Kids' Backpacks and School Gear": "16 Small Apartment Storage Ideas for Kids' Backpacks",
    "15 Entryway Mail and Paper Organization Ideas for Small Homes": "15 Entryway Mail and Paper Organization Ideas",
    "16 Small Guest Room Storage Ideas That Make Visitors Feel at Home": "16 Small Guest Room Storage Ideas",
    "15 Small Apartment Move-In Organization Ideas for Your First Week": "15 Small Apartment Move-In Organization Ideas",
    "16 Small Closet Lighting Ideas That Make a Dark Closet Usable": "16 Small Closet Lighting Ideas for Dark Closets",
    "17 Small Kitchen Pot and Pan Storage Ideas That Free Your Cabinets": "17 Small Kitchen Pot and Pan Storage Ideas",
    "14 Small Living Room Corner Storage Ideas That Use Wasted Space": "14 Small Living Room Corner Storage Ideas",
    "18 Small Bathroom Storage Ideas That Make a Tiny Bathroom Work Harder": "18 Small Bathroom Storage Ideas",
    "18 Small Apartment Recycling Station Ideas That Don't Look Like Trash": "18 Small Apartment Recycling Station Ideas",
    "15 Small Bedroom Nightstand Organization Ideas That End the Clutter": "15 Small Bedroom Nightstand Organization Ideas",
    "16 Small Apartment Charger and Cable Organization Ideas That End the Tangle": "16 Small Apartment Charger and Cable Organization Ideas",
    "15 Small Apartment Media Storage Ideas for TVs, Consoles, and Cables": "15 Small Apartment Media Storage Ideas",
    "16 Small Bathroom Towel Storage Ideas That Keep Towels Dry and Handy": "16 Small Bathroom Towel Storage Ideas",
    "Studio Apartment Organization: How to Create Zones in One Room": "Studio Apartment Organization: How to Create Zones",
    "16 Window Seat and Under-Window Storage Ideas for Small Homes": "16 Window Seat & Under-Window Storage Ideas",
    "18 Small Reach-In Closet Organization Ideas That Double Your Space": "18 Small Reach-In Closet Organization Ideas",
    "16 Small Galley Kitchen Storage Ideas That Make a Narrow Kitchen Work": "16 Small Galley Kitchen Storage Ideas",
    "17 Small Apartment Storage Ideas Under $25 That Look Expensive": "17 Small Apartment Storage Ideas Under $25",
    "16 Small Entryway Bench Ideas With Hidden Storage for Tiny Halls": "16 Small Entryway Bench Ideas With Hidden Storage",
    "16 Blind Corner Kitchen Cabinet Storage Ideas That Waste Nothing": "16 Blind Corner Kitchen Cabinet Storage Ideas",
    "16 Entryway Coat Storage Ideas for Apartments Without a Closet": "16 Entryway Coat Storage Ideas Without a Closet",
    "15 Small Bedroom Nightstand Alternatives That Save Floor Space": "15 Small Bedroom Nightstand Alternatives",
    "15 Small Apartment Robot Vacuum Storage Ideas That Hide the Dock": "15 Small Apartment Robot Vacuum Storage Ideas",
    "16 Small Kitchen Open Shelving Storage Ideas That Actually Stay Tidy": "16 Small Kitchen Open Shelving Storage Ideas",
    "16 Small Kitchen Spice Organization Ideas That End the Jumbled Drawer": "16 Small Kitchen Spice Organization Ideas",
    "15 Small Bathroom Hair Tool Storage Ideas That End the Cord Tangle": "15 Small Bathroom Hair Tool Storage Ideas",
    "17 Small Laundry Room Organization Ideas for Stacked Machines": "17 Small Laundry Room Organization Ideas",
    "16 Small Makeup Organization Ideas for Tiny Vanities and Bathrooms": "16 Small Makeup Organization Ideas",
    "17 Small Bedroom Loft Bed Storage Ideas That Use Every Inch Underneath": "17 Small Bedroom Loft Bed Storage Ideas",
    "15 Small Kitchen Tea Station Organization Ideas for Tiny Kitchens": "15 Small Kitchen Tea Station Organization Ideas",
    "16 Small Kitchen Knife Storage Ideas That Keep Blades Safe and Counters Clear": "16 Small Kitchen Knife Storage Ideas",
    "16 Small Kitchen Dish Drying Rack Ideas That Don't Eat Your Counter": "16 Small Kitchen Dish Drying Rack Ideas",
    "18 Under-Bed Storage Ideas That Turn Dead Space Into a Dresser": "18 Under-Bed Storage Ideas for Small Bedrooms",
    "17 Small Bedroom Dresser Organization Ideas That Double Your Drawers": "17 Small Bedroom Dresser Organization Ideas",
    "15 Small Apartment Ideas to Hide Your Router and Tech Clutter": "15 Small Apartment Ideas to Hide Router Clutter",
    "15 Small Fridge Organization Ideas That End the 'What's in There' Game": "15 Small Fridge Organization Ideas",
    "15 Small Bedroom Storage Ideas for Sloped Ceilings and Attic Rooms": "15 Small Bedroom Storage Ideas for Sloped Ceilings",
    "18 Small Garage Organization Ideas That Reclaim Your Parking Spot": "18 Small Garage Organization Ideas",
    "Space-Saving 3D-Printed Organization Ideas for Small Apartments": "Space-Saving 3D-Printed Organization Ideas",
    "18 Small Kitchen Cabinet Organization Ideas That Maximize Every Shelf": "18 Small Kitchen Cabinet Organization Ideas",
    "15 Small Apartment Murphy Bed Storage Ideas That Hide the Whole Bedroom": "15 Small Apartment Murphy Bed Storage Ideas",
    "16 Small Medicine Cabinet Organization Ideas That Make Mornings Faster": "16 Small Medicine Cabinet Organization Ideas",
}


def core_title(full):
    return full[:-len(SUFFIX)] if full.endswith(SUFFIX) else full


def new_title(core):
    # Strip the trailing parenthetical first, then check manual trims on the
    # stripped form (some manual entries had a paren in the CSV original).
    stripped = re.sub(r'\s*\([^)]*\)\s*$', '', core).strip()
    if stripped in MANUAL:
        return MANUAL[stripped]
    return stripped


def main():
    rows = list(csv.DictReader(open(CSV, encoding='utf-8-sig')))
    plan = []  # (slug, old, new)
    skipped = []
    for r in rows:
        url = r['Address'].rstrip('/')
        slug = url.split('/blog/')[-1]
        old = core_title(r['Title 1'])
        new = new_title(old)
        assert '"' not in new, f'double quote in new title: {new}'
        assert len(new) <= 60, f'still >60: {len(new)} | {new}'
        if len(old) <= 60:
            continue  # suffix removal alone fixes it; no frontmatter change
        plan.append((slug, old, new))
    print(f'plan: {len(plan)} frontmatter rewrites')
    changed, mismatched, missing = 0, [], []
    for slug, old, new in plan:
        path = f'{BLOG}/{slug}.md'
        try:
            text = open(path, encoding='utf-8').read()
        except FileNotFoundError:
            missing.append(slug)
            continue
        m = re.search(r'^title: "(.*)"\s*$', text, re.M)
        if not m:
            mismatched.append((slug, 'no title line'))
            continue
        if m.group(1) == new:
            changed += 1  # already applied in an earlier run
            continue
        if m.group(1) != old:
            mismatched.append((slug, f'frontmatter={m.group(1)!r} csv={old!r}'))
            continue
        esc = new.replace('\\', '\\\\').replace('"', '\\"')
        text = text[:m.start(1)] + esc + text[m.end(1):]
        open(path, 'w', encoding='utf-8').write(text)
        changed += 1
    print(f'changed: {changed}, missing files: {missing}, mismatches: {len(mismatched)}')
    for s, why in mismatched:
        print('  MISMATCH', s, why)
    if missing or mismatched:
        sys.exit(1)
    print('sample:')
    for slug, old, new in plan[:5]:
        print(f'  {len(old)}->{len(new)} | {old}  =>  {new}')


if __name__ == '__main__':
    main()
