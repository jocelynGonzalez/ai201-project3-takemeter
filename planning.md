# Project Planning — Community Text Classifier

> Baseline planning document. Fill in each section before starting data collection.
> Keep this updated as decisions change — it is the source of truth for the project.

**Project:** ai201-project3-takemeter
**Last updated:** _YYYY-MM-DD_

---

## 1. Community

_Which online community is the source of your data, and why is it a good fit for a classification task?_

- **Community chosen:**
  - _r/Europetravel_
- **Why this community:**
  - _Access to a variety of data and type of posts._
- **Why it fits a classification task:**
  - Posts naturally fall into distinct intents of asking for itinerary feedback, asking a factual logistics question, asking for open-ended recommendations, or sharing experience/advice — so the categories are real and recurring rather than invented.
  - The categories are non-trivial because a simple keyword rule can't separate them: the same words appear across labels (a "train" post might be a logistics question, a recommendation request, or a trip report), questions are often phrased indirectly, and many posts mix two intents — so the model has to read intent from context, not surface terms.
- **Real problem this could help solve:**
  - A moderator or community tool could use the labels to **auto-route posts** — e.g., funnel repetitive `logistics_question` posts to a FAQ/megathread, surface `itinerary_feedback` posts in a weekly planning thread, and tag `trip_report` posts for a "trip reports" feed — reducing duplicate questions and helping members find the content they want.

---

## 2. Labels

_Four labels (intent-based). They split cleanly into three "asking" intents and one "sharing" intent, so every post is doing one primary thing: asking for plan feedback, asking a factual question, asking for ideas, or sharing knowledge._

> Guideline: labels are **mutually exclusive** — assign by the post's *primary intent*. A post with no question defaults to `trip_report`. Off-topic or non-travel posts are dropped during cleaning, not given a label.

### Label A — `itinerary_feedback`
- **Definition:** A post is labeled `itinerary_feedback` when the author presents a concrete travel plan (specific cities, dates, or a day-by-day route) and asks others to critique, validate, or refine it.
- **Example 1:** _"3 weeks in Italy: Rome (4d) → Florence (3d) → Venice (2d) → Amalfi (5d). Is this too rushed? What would you cut?"_
- **Example 2:** _"Planning France + Switzerland in October, 10 days total. Does this order make sense or am I backtracking too much?"_

### Label B — `logistics_question`
- **Definition:** A post is labeled `logistics_question` when the author asks a narrow, factual question about how some aspect of travel works, where there is a largely correct answer.
- **Example 1:** _"Do I need to validate my regional train ticket before boarding in Italy, or is the printed ticket enough?"_
- **Example 2:** _"How many days do US passport holders get in the Schengen area, and does a layover in Frankfurt count?"_

### Label C — `recommendation_request`
- **Definition:** A post is labeled `recommendation_request` when the author asks for open-ended suggestions or opinions (where to go, what to do, what to eat) without an existing concrete plan to evaluate.
- **Example 1:** _"Best European city for a solo trip in early December? Looking for walkable and not too touristy."_
- **Example 2:** _"Where should I eat in Lisbon for authentic seafood that isn't a tourist trap?"_

### Label D — `trip_report` _(experience / advice)_
- **Definition:** A post is labeled `trip_report` when the author shares their own travel experience or accumulated advice — a completed-trip recap, lessons learned, or general tips — without asking a question.
- **Example 1:** _"Just got back from 2 weeks in Portugal — here's what went well, what I'd skip, and a rough budget breakdown."_
- **Example 2:** _"These 11 mistakes are ruining your trip to Europe (overpacking, skipping reservations, only visiting capitals...)."_

---

## 3. Hard Edge Cases

_What posts will be genuinely ambiguous between two labels, and how will you resolve them consistently?_

- **Ambiguous pair(s):**
  - **`itinerary_feedback` vs. `recommendation_request`** — e.g., _"Here's my Italy plan, but should I swap Florence for Bologna?"_ — it both presents a plan and asks for an open-ended suggestion.
  - **`logistics_question` vs. `recommendation_request`** — e.g., _"Best way to get from Paris to Amsterdam?"_ — partly factual (how), partly preference (best).
  - **Advice listicle vs. `trip_report`** — e.g., _"These 11 mistakes are ruining your trip to Europe."_ — generalized tips rather than a first-person trip recap.
- **Why it's hard:**
  - These posts carry two intents at once, and the title alone often doesn't reveal which one is primary; the deciding signal is sometimes buried in the body.
- **Tie-breaking rule(s):**
  - **Existing concrete plan → `itinerary_feedback`.** If the author already has a specific route/dates and asks to refine it, label it feedback even if it also asks for ideas.
  - **Single correct answer → `logistics_question`.** If the core ask has a largely factual answer, label logistics; if it's mostly taste/opinion, label `recommendation_request`.
  - **No question → `trip_report`.** Generalized advice and tips listicles count as `trip_report` (experience/advice), since the author is telling, not asking.
  - **General rule:** assign by the *primary* intent expressed in the first sentence / title; if still tied, prefer the more specific "asking" label over the broader one.
- **Annotation hygiene:**
  - Keep a running **edge-case log** (post → chosen label → rule applied) so identical cases are labeled consistently.
  - Do a **second pass** over all borderline items once the dataset is complete to enforce consistency.
  - Engagement-bait / blogspam listicles linking to external sites are a **content-quality** issue — handle in data cleaning (drop), not as a label.

---

## 4. Data Collection Plan

_Where will the examples come from, how many, and what's the fallback for thin labels?_

- **Source(s):**
  - _Exact location(s): which subreddit/board/threads, scraping method or API, date range._
- **Target counts:**
  - _Total examples and target per label (e.g., ~50–100 per label, ~200 total)._
- **Sampling strategy:**
  - _Random vs. targeted? How will you avoid pulling near-duplicate or low-content posts?_
- **Underrepresented-label plan (after 200 examples):**
  - _If a label has too few examples: targeted search/keyword sampling, extend the date range, oversample in training, merge/redefine the label, or report it as a known class imbalance._
- **Cleaning & storage:**
  - _Dedup, PII removal, format (CSV/JSONL columns), where the dataset lives._

---

## 5. Evaluation Metrics

_Which metrics will you report, and why are they right for THIS task? (Accuracy alone is not enough.)_

- **Primary metrics:**
  - _e.g., per-class **precision, recall, F1** + **macro-F1** — because class imbalance makes plain accuracy misleading._
- **Why not accuracy alone:**
  - _Explain: if one label dominates, a model can score high accuracy while failing the minority classes that matter._
- **Diagnostics:**
  - _**Confusion matrix** to see which labels get mixed up (ties back to your edge cases)._
- **Validation method:**
  - _Train/test split or k-fold cross-validation; held-out test size; whether the split is stratified by label._
- **Baseline to beat:**
  - _Majority-class baseline and/or a simple keyword/logistic-regression baseline so improvements are meaningful._

---

## 6. Definition of Success

_What performance makes this classifier genuinely useful?_

- **Target performance:**
  - _Concrete threshold(s), e.g., "macro-F1 ≥ 0.X and no single label below recall 0.Y."_
- **"Good enough" for deployment:**
  - _What bar would let it run as a real community tool (e.g., a triage assistant that a human still reviews)?_
- **Cost of errors:**
  - _Which mistakes are tolerable vs. costly? Does the use case favor precision (avoid false flags) or recall (catch everything)?_
- **Human-in-the-loop:**
  - _Will the model auto-act, suggest, or only surface uncertain cases for review? How does that change the bar?_

---

## 7. AI Tool pLan

- **Label stress-testing:**
  - _I will give Claude the four labels and edge case description so that it can generate 5-10 posts that are a bit ambiguous to label. If it can come up with posts that can't be classified, I will have to update the labels._
- **Annotation assistance:**
  - _Will give LLM to pre-label batch of examples before reviewing them._
- **Failure analysis:**
  - _Will give my list of wrong predictions to Claude and ask it to identify patterns before writing up the evaluation. I will verify myself._


## Open Questions & Decisions Log

- _Track unresolved choices, label redefinitions, and dated decisions here._