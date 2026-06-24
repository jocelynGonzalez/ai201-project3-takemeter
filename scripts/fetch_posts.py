"""
Fetch public posts from r/Europetravel via Reddit's .json endpoint (no auth, no API key).

Produces posts.csv with columns: text, label, notes, flair_hint, url
  - text:       title + body, pre-filled  -> you label these
  - label:      BLANK on purpose          -> fill in one of the 4 labels
  - notes:      BLANK                      -> edge-case notes / tie-break rule used
  - flair_hint: the post's flair (helps labeling; delete before the notebook if it complains)
  - url:        permalink (so you can open the original)

Usage:
    python scripts/fetch_posts.py

Then label the `label` column in a spreadsheet and save as posts.csv in the repo root.
"""

import csv
import json
import time
import urllib.request

SUBREDDIT = "Europetravel"
TARGET = 250          # collect a bit over 200 so you can drop low-content rows
PER_PAGE = 100        # Reddit max per request
OUT = "posts.csv"

# A few listings to pull from so you get a varied mix (not just one sort order).
# Search queries bias toward the rarer intents so labels come out more balanced.
ENDPOINTS = [
    "https://www.reddit.com/r/{sub}/top.json?t=year&limit={n}",
    "https://www.reddit.com/r/{sub}/search.json?q=itinerary&restrict_sr=1&sort=top&t=year&limit={n}",
    "https://www.reddit.com/r/{sub}/search.json?q=train+OR+schengen+OR+visa&restrict_sr=1&sort=top&t=year&limit={n}",
    "https://www.reddit.com/r/{sub}/search.json?q=recommendations+OR+%22where+should%22&restrict_sr=1&sort=top&t=year&limit={n}",
    "https://www.reddit.com/r/{sub}/search.json?q=flair%3A%22Trip+Report%22&restrict_sr=1&sort=top&t=year&limit={n}",
]

HEADERS = {"User-Agent": "takemeter-data-collection/0.1 (educational project)"}


def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def collect():
    seen = {}
    for tmpl in ENDPOINTS:
        after = None
        # paginate up to ~2 pages per endpoint
        for _ in range(2):
            url = tmpl.format(sub=SUBREDDIT, n=PER_PAGE)
            if after:
                url += f"&after={after}"
            try:
                data = fetch(url)
            except Exception as e:
                print(f"  ! skipped {url[:60]}... ({e})")
                break

            children = data.get("data", {}).get("children", [])
            for c in children:
                p = c.get("data", {})
                if p.get("stickied"):
                    continue
                pid = p.get("id")
                if not pid or pid in seen:
                    continue
                title = (p.get("title") or "").strip()
                body = (p.get("selftext") or "").strip()
                text = f"{title}\n\n{body}".strip()
                if len(text) < 15:   # skip empty/low-content
                    continue
                seen[pid] = {
                    "text": text,
                    "label": "",
                    "notes": "",
                    "flair_hint": p.get("link_flair_text") or "",
                    "url": "https://www.reddit.com" + p.get("permalink", ""),
                }
            after = data.get("data", {}).get("after")
            time.sleep(2)   # be polite to Reddit
            if not after or len(seen) >= TARGET:
                break
        if len(seen) >= TARGET:
            break
    return list(seen.values())


def main():
    rows = collect()
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["text", "label", "notes", "flair_hint", "url"])
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} posts to {OUT}")
    if len(rows) < 200:
        print("WARNING: fewer than 200 rows. Re-run, raise TARGET, or add search queries.")


if __name__ == "__main__":
    main()
