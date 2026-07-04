#!/usr/bin/env python3
"""
Deliverables gate for the daily-tribute pipeline.

Born from operator feedback on the 2026-07-03 ECC run, where three failures
shipped that no gate measured:

  1. The X caption was engagement-metrics-only (stars + thread views) with
     zero capability facts — nothing about what the project actually does.
  2. The video's "product" beat typed a terminal command no one had verified
     exists. Fact-check only traces NUMERALS, so an invented command passed
     every gate.
  3. The Gmail shipped the first-reply mechanics NOTE ("repo link belongs in
     the first reply") without the LINK itself — the user had nothing to paste.

Per pipeline principle 3 (gates, not vibes), each is now a measured check.

Usage:
    deliverables_check.py reports/deliverables-DATE.json
        [--spec reports/scene-spec-DATE.json --repo-study reports/repo-study-DATE.json]
        [--gmail reports/gmail-DATE.html]
    deliverables_check.py --selftest

deliverables-DATE.json schema:
    {"date": "...", "project_url": "https://github.com/owner/repo",
     "creator_handle": "@handle",
     "caption": "...",             # the X post, ready to paste
     "capability_fact": "...",     # the caption clause that says what the thing DOES
     "first_reply": "...",         # MUST contain project_url; paste-ready
     "why_this_one": "...",        # second thread reply
     "track_license": "CC BY 4.0",
     "attribution_reply": "Music. <title> by <artist> (<source>), licensed under CC BY 4.0."}

repo-study-DATE.json schema (written by the Repo Study step):
    {"date": "...", "project_url": "...",
     "components": ["real subsystem/agent/skill names"],
     "commands":  [{"text": "exact documented invocation", "source": "https://..."}],
     "outputs":   [{"text": "documented output line",      "source": "https://..."}],
     "architecture_facts": ["one clause each"],
     "surprising_detail": "..."}

Exit codes: 0 all green, 1 any FAIL, 2 usage/input error.
"""

import argparse
import json
import re
import sys
from pathlib import Path

URL_RE = re.compile(r"https?://\S+")

# Engagement metrics: a number + an audience-reaction noun, or "trending".
# These prove people CARE; they say nothing about what the project DOES.
ENGAGEMENT_NOUNS = r"(?:github\s+)?(?:stars?|views?|forks?|downloads?|likes?|bookmarks?|followers?|watchers?)"
CAPTION_METRIC_RE = re.compile(
    r"\b\d[\d,.]*\s*[kKmM]?\s*\+?\s*" + ENGAGEMENT_NOUNS + r"\b|\btrending\b", re.I)
# Scene-level growth language is broader: a star chart labeled "climbing"
# is a growth beat even without a numeral next to the noun.
GROWTH_SCENE_RE = re.compile(
    CAPTION_METRIC_RE.pattern + r"|\bclimbing\b|\bblowing up\b|\bviral\b|\bstar count\b|\bstargazers\b", re.I)

FORBIDDEN_CHARS = {"em dash": "—", "en dash": "–", "semicolon": ";"}
SMART_QUOTES = set("‘’“”")

# ---- LinkedIn caption (v9) ------------------------------------------------
# Same video, second surface. The operator's voice: chill, specific, human.
# Hard rules from the operator: no em/en dash, no colon, no semicolon, few
# commas, NO AI tells, 3-5 hashtags. The tell list is the AI "fingerprint"
# (delve/leverage/robust/seamless/tapestry/moreover/"in today's fast-paced
# world"...) that readers register as machine-written even when they can't say
# why -- researched, not guessed. "delve" is the single strongest signal.
LINKEDIN_FORBIDDEN = {"em dash": "—", "en dash": "–", "semicolon": ";", "colon": ":"}
LINKEDIN_AI_TELLS = [
    "delve", "delving", "delved", "leverage", "leverages", "leveraging",
    "utilize", "utilizes", "utilizing", "harness", "harnessing", "streamline",
    "streamlines", "streamlining", "underscore", "underscores", "elevate",
    "elevates", "elevating", "revolutionize", "revolutionizes", "revolutionary",
    "supercharge", "supercharges", "spearhead", "robust", "seamless",
    "seamlessly", "innovative", "cutting-edge", "pivotal", "bespoke",
    "unparalleled", "world-class", "next-level", "game-changer", "game changer",
    "game-changing", "tapestry", "realm", "synergy", "testament", "moreover",
    "furthermore", "consequently", "notably", "boasts", "boasting",
    "meticulous", "meticulously", "paradigm", "in today's", "fast-paced world",
    "digital age", "worth noting", "important to note", "dive into", "deep dive",
    "delve into", "embark on", "embark upon", "navigate the", "in the realm of",
    "unlock the", "at the end of the day", "look no further", "a testament to",
]


def effective_len(text):
    """X counts every URL as 23 chars (t.co)."""
    return len(URL_RE.sub("x" * 23, text))


def norm(text):
    """Lowercase, strip punctuation that doesn't change identity, collapse ws."""
    text = text.lower().strip()
    text = re.sub(r"^\$\s*", "", text)          # leading shell prompt
    text = re.sub(r"[^\w\s$+./-]", " ", text)   # keep word chars, $, +, ., /, -
    return re.sub(r"\s+", " ", text).strip()


def ngrams(text, n=4):
    words = norm(text).split()
    return {tuple(words[i:i + n]) for i in range(len(words) - n + 1)}


def check_copy_rules(field, text, fails, allow_final_question=False):
    for label, ch in FORBIDDEN_CHARS.items():
        if ch in text:
            fails.append(f"{field}: {label} present")
    if re.search(r"#\w", text):
        fails.append(f"{field}: hashtag present")
    for ch in text:
        if ord(ch) > 127 and ch not in SMART_QUOTES:
            fails.append(f"{field}: non-ASCII char {ch!r} (emoji/symbols banned)")
            break
    qs = text.count("?")
    if qs:
        if not allow_final_question or qs > 1 or not text.rstrip().endswith("?"):
            fails.append(f"{field}: question mark only allowed as the caption's final char")


def check_deliverables(d, fails):
    """Every check that CAN run does run — one pass surfaces every problem."""
    required = ["date", "project_url", "creator_handle", "caption",
                "capability_fact", "first_reply", "why_this_one", "track_license",
                "linkedin_caption", "linkedin_hashtags"]
    missing = [k for k in required if not d.get(k)]
    if missing:
        fails.append(f"deliverables: missing fields {missing}")

    caption, why = d.get("caption", ""), d.get("why_this_one", "")

    if caption:
        if d.get("creator_handle") and not caption.startswith(d["creator_handle"]):
            fails.append(f"caption: must open with {d['creator_handle']}")
        if effective_len(caption) > 280:
            fails.append(f"caption: {effective_len(caption)} effective chars > 280")
        check_copy_rules("caption", caption, fails, allow_final_question=True)
        hits = CAPTION_METRIC_RE.findall(caption)
        if len(hits) > 1:
            fails.append(f"caption: {len(hits)} engagement metrics ({hits}); max 1 — "
                         "the lead. The second fact must be a CAPABILITY fact.")

    fact = d.get("capability_fact", "")
    if fact:
        if len(fact.split()) < 4:
            fails.append("capability_fact: under 4 words — name a real capability clause")
        if CAPTION_METRIC_RE.search(fact):
            fails.append("capability_fact: is itself an engagement metric — must say what the project DOES")
        if caption and norm(fact) not in norm(caption):
            fails.append("capability_fact: not present in the caption (normalized substring)")

    if d.get("first_reply"):
        if d.get("project_url") and d["project_url"] not in d["first_reply"]:
            fails.append("first_reply: does NOT contain the project URL — the repo link "
                         "is paste-ready copy, not a mechanics note")
        if effective_len(d["first_reply"]) > 280:
            fails.append(f"first_reply: {effective_len(d['first_reply'])} effective chars > 280")

    if why:
        if effective_len(why) > 280:
            fails.append(f"why_this_one: {effective_len(why)} effective chars > 280")
        check_copy_rules("why_this_one", why, fails)
        shared = ngrams(caption) & ngrams(why) if caption else set()
        if shared:
            fails.append(f"why_this_one: shares 4-gram(s) with caption: {sorted(shared)[:2]}")

    if d.get("track_license", "").startswith("CC BY"):
        attr = d.get("attribution_reply", "")
        if not re.match(r"^Music\. .+ by .+, licensed under CC BY", attr):
            fails.append("attribution_reply: CC BY track requires verbatim "
                         "'Music. <title> by <artist> (<source>), licensed under CC BY ...'")


def harvest_strings(scene):
    out = []
    for k, v in scene.items():
        if k in ("template", "camera"):
            continue
        if isinstance(v, str):
            out.append(v)
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, str):
                    out.append(item)
                elif isinstance(item, dict):
                    out.extend(str(x) for x in item.values() if isinstance(x, str))
        elif isinstance(v, dict):
            out.extend(str(x) for x in v.values() if isinstance(x, str))
    return out


def study_pool(study):
    pool = set()
    for c in study.get("components", []):
        pool.add(norm(c))
    for entry in study.get("commands", []) + study.get("outputs", []):
        pool.add(norm(entry["text"]))
    for f in study.get("architecture_facts", []):
        pool.add(norm(f))
    return pool


def matches_study(s, pool):
    n = norm(s)
    if len(n) < 4:
        return False
    return any(n == p or n in p or p in n for p in pool)


def check_substance(spec, study, fails):
    for i, entry in enumerate(study.get("commands", []) + study.get("outputs", [])):
        if not str(entry.get("source", "")).startswith("https://"):
            fails.append(f"repo-study: entry {i} ({entry.get('text', '')!r}) has no https source URL")

    commands = {norm(e["text"]) for e in study.get("commands", [])}
    outputs = {norm(e["text"]) for e in study.get("outputs", [])}
    pool = study_pool(study)

    growth_scenes, backed_scenes = [], []
    for idx, sc in enumerate(spec.get("scenes", [])):
        tpl = sc.get("template")
        strings = harvest_strings(sc)

        # Test the scene's text as one blob: templates like big_number split
        # the numeral and the noun ("225k" / "github stars") across fields.
        if GROWTH_SCENE_RE.search(" ".join(strings)):
            growth_scenes.append(idx)

        if tpl == "terminal":
            ok = True
            for line in sc.get("lines", []):
                text = line["text"] if isinstance(line, dict) else line
                is_prompt = line.get("prompt", True) if isinstance(line, dict) else True
                target, kind = (commands, "commands") if is_prompt else (outputs, "outputs")
                if norm(text) not in target:
                    fails.append(f"scene {idx} (terminal): line {text!r} not in repo-study "
                                 f"{kind}[] — invented terminal content is unshippable")
                    ok = False
            if ok and sc.get("lines"):
                backed_scenes.append(idx)
        elif tpl == "diagram":
            labels = [n.get("label", "") for n in sc.get("nodes", [])]
            matched = sum(1 for lb in labels if matches_study(lb, pool))
            if labels and matched >= max(1, len(labels) - 1):
                backed_scenes.append(idx)
        elif tpl in ("mono_block", "panes", "wire_dispatch", "split", "stack", "quote"):
            if any(matches_study(s, pool) for s in strings):
                backed_scenes.append(idx)

    if len(growth_scenes) > 2:
        fails.append(f"spec: {len(growth_scenes)} growth-metric scenes {growth_scenes}; "
                     "max 2 — the scoreboard is the hook, not the story")
    if len(backed_scenes) < 2:
        fails.append(f"spec: only {len(backed_scenes)} repo-study-backed product scenes "
                     f"{backed_scenes}; need >= 2 (terminal with verified lines, diagram of "
                     "real components, or copy quoting the study)")


def check_gmail(html, d, fails):
    if d["project_url"] not in html:
        fails.append("gmail: project repo URL not present anywhere — the first-reply "
                     "link is a REQUIRED paste-ready block")
    if not re.search(r"first\s+reply", html, re.I):
        fails.append("gmail: no 'First reply' section — the repo link must ship as its own block")
    date = d["date"]
    if not re.search(rf"https://\S+/reports/tribute-{date}\.mp4", html):
        fails.append(f"gmail: MP4 download URL for {date} missing")
    if not re.search(rf"https://\S+/reports/tribute-preview-{date}\.gif", html):
        fails.append(f"gmail: GIF preview URL for {date} missing")
    if "/home/" in html:
        fails.append("gmail: local filesystem path present — deliverables must be https URLs")
    if "<style" in html.lower():
        fails.append("gmail: <style> block present — inline styles only")
    if d["track_license"].startswith("CC BY") and "licensed under CC BY" not in html:
        fails.append("gmail: CC BY attribution line missing")
    # v9: the LinkedIn caption + hashtags must ship as their own copy-paste block
    if not re.search(r"linked\s*in", html, re.I):
        fails.append("gmail: no LinkedIn block -- the LinkedIn caption + hashtags must ship as one copy-paste block")
    li = (d.get("linkedin_caption", "") or "").strip()
    if li and li[:24] not in html:
        fails.append("gmail: LinkedIn caption text not found in the HTML block")
    tags = d.get("linkedin_hashtags", "")
    tags_str = tags if isinstance(tags, str) else " ".join(tags)
    first_tag = re.search(r"#\w+", tags_str)
    if first_tag and first_tag.group(0) not in html:
        fails.append("gmail: LinkedIn hashtags not found in the HTML block")


def check_linkedin(d, fails):
    """Editorial gate for the LinkedIn caption + hashtags (v9). The operator's
    voice: no em/en dash, no colon, no semicolon; commas kept low; no AI tells;
    a tight paragraph or two; 3-5 hashtags at the end. LinkedIn @-mentions can't
    be typed as plain text, so a linkedin_tag (name + profile URL) rides
    alongside in the deliverables for the operator to @-mention by hand."""
    cap = d.get("linkedin_caption", "")
    if not cap:
        return  # a missing caption is reported by the required-fields check
    low = cap.lower()

    for label, ch in LINKEDIN_FORBIDDEN.items():
        if ch in cap:
            fails.append(f"linkedin_caption: {label} ({ch!r}) present -- the operator forbids it")

    hits = sorted({t for t in LINKEDIN_AI_TELLS
                   if re.search(r"(?<!\w)" + re.escape(t) + r"(?!\w)", low)})
    if hits:
        fails.append(f"linkedin_caption: AI-tell word(s)/phrase(s) {hits[:8]} -- "
                     "rewrite plainer, in a real human voice (be specific, take a stance)")

    commas = cap.count(",")
    sentences = max(1, len(re.findall(r"[.!?]+", cap)))
    if commas > sentences + 1:
        fails.append(f"linkedin_caption: {commas} commas across ~{sentences} sentences -- too many; "
                     "keep the sentences short and clipped")

    n = len(cap.strip())
    if n < 200:
        fails.append(f"linkedin_caption: {n} chars -- too thin; say what it does and why it is cool")
    if n > 1300:
        fails.append(f"linkedin_caption: {n} chars -- too long; a tight paragraph or two, not an essay")

    tags = d.get("linkedin_hashtags", "")
    tags_str = tags if isinstance(tags, str) else " ".join(tags)
    hcount = len(re.findall(r"#\w+", tags_str))
    if not (3 <= hcount <= 5):
        fails.append(f"linkedin_hashtags: {hcount} hashtag(s) -- use 3 to 5 (6+ triggers a LinkedIn reach penalty)")


def run_checks(deliv_path, spec_path=None, study_path=None, gmail_path=None):
    fails = []
    d = json.loads(Path(deliv_path).read_text())
    check_deliverables(d, fails)
    check_linkedin(d, fails)

    if spec_path or study_path:
        if not (spec_path and study_path):
            fails.append("usage: --spec and --repo-study must be passed together")
        else:
            spec = json.loads(Path(spec_path).read_text())
            study = json.loads(Path(study_path).read_text())
            check_substance(spec, study, fails)

    if gmail_path:
        check_gmail(Path(gmail_path).read_text(), d, fails)

    return fails


# ---------------------------------------------------------------- selftest

def selftest():
    """Regression cases mirroring the 2026-07-03 failures, plus green paths."""
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="deliv_selftest_"))

    def write(name, obj):
        p = tmp / name
        p.write_text(json.dumps(obj, indent=2) if isinstance(obj, dict) else obj)
        return p

    base = {
        "date": "2026-07-03",
        "project_url": "https://github.com/affaan-m/ECC",
        "creator_handle": "@affaanmustafa",
        "track_license": "CC BY 4.0",
        "attribution_reply": "Music. Beauty Flow by Kevin MacLeod (incompetech.com), licensed under CC BY 4.0.",
    }

    # Case 1: the caption that actually shipped — two engagement metrics,
    # no capability fact, no first reply. Must FAIL on all three.
    shipped = dict(base)
    shipped["caption"] = ("@affaanmustafa 225k+ GitHub stars and counting for ECC, the config layer "
                          "you built across Claude Code, Codex, Cursor, and OpenCode. Your launch "
                          "thread hit 900k views before the repo even went public.")
    shipped["capability_fact"] = ""
    shipped["first_reply"] = ""
    shipped["why_this_one"] = "x"
    f1 = run_checks(write("shipped.json", shipped))
    assert any("engagement metrics" in x for x in f1), f1
    assert any("missing fields" in x for x in f1), f1

    # Case 2: corrected deliverables — must PASS clean.
    good = dict(base)
    good["caption"] = ("@affaanmustafa 225k+ GitHub stars and counting for ECC. One config layer "
                       "that carries 60+ agents and 250+ skills across Claude Code, Codex, Cursor, "
                       "and OpenCode, with AgentShield security scanning built in.")
    good["capability_fact"] = ("One config layer that carries 60+ agents and 250+ skills across "
                               "Claude Code, Codex, Cursor, and OpenCode")
    good["first_reply"] = "https://github.com/affaan-m/ECC"
    good["why_this_one"] = ("He won the Anthropic x Forum Ventures hackathon in NYC by shipping "
                            "zenith.chat in 8 hours without typing a line, then open sourced the "
                            "whole setup once the guide thread crossed 900k views.")
    good["linkedin_caption"] = ("ECC is one config layer that carries a stack of agents and skills "
                                "across Claude Code, Codex, Cursor, and OpenCode. Affaan built it in a "
                                "weekend and open sourced the whole thing. The part that got me is the "
                                "security scan baked in so your agent setup gets checked before it ships. "
                                "If you run more than one coding agent this saves you from wiring the same "
                                "config five times over. Worth a look if you live in these tools all day.")
    good["linkedin_hashtags"] = "#AI #DevTools #OpenSource #CodingAgents"
    good["linkedin_tag"] = {"name": "Affaan Mustafa", "url": "https://www.linkedin.com/in/affaanmustafa"}
    good_p = write("good.json", good)
    f2 = run_checks(good_p)
    assert f2 == [], f2

    # Case 3: gmail missing the first-reply block / repo link — the exact
    # 2026-07-03 miss. Must FAIL on both counts.
    bad_html = ("<table><tr><td>repo link goes in the first comment, not the post body"
                "<a href='https://github.com/x/y/raw/main/reports/tribute-2026-07-03.mp4'>mp4</a>"
                "<a href='https://github.com/x/y/raw/main/reports/tribute-preview-2026-07-03.gif'>gif</a>"
                "licensed under CC BY 4.0</td></tr></table>")
    f3 = run_checks(good_p, gmail_path=write("bad.html", bad_html))
    assert any("repo URL not present" in x for x in f3), f3
    assert any("First reply" in x for x in f3), f3

    # Case 4: gmail with the first-reply block AND the LinkedIn copy-paste block — PASS.
    good_html = bad_html.replace(
        "repo link goes in the first comment, not the post body",
        "<b>First reply (paste right after posting)</b> https://github.com/affaan-m/ECC "
        "<b>Post to LinkedIn</b> " + good["linkedin_caption"] + " " + good["linkedin_hashtags"] + " ")
    f4 = run_checks(good_p, gmail_path=write("good.html", good_html))
    assert f4 == [], f4

    # Case 4b: LinkedIn caption with an em dash, AI tells, and too few hashtags — must FAIL.
    bad_li = dict(good)
    bad_li["linkedin_caption"] = ("This tool will revolutionize how you work — it is a robust and seamless "
                                  "way to leverage your agents. In today's fast-paced world you have to "
                                  "delve into it.")
    bad_li["linkedin_hashtags"] = "#AI #DevTools"
    f4b = run_checks(write("badli.json", bad_li))
    assert any("em dash" in x for x in f4b), f4b
    assert any("AI-tell" in x for x in f4b), f4b
    assert any("hashtag" in x for x in f4b), f4b

    # Case 5: terminal scene typing a command the repo study never verified —
    # the invented `ecc security-review` case. Must FAIL; and only 1 backed scene.
    spec = {"scenes": [
        {"template": "terminal", "lines": [
            {"text": "ecc security-review", "prompt": True},
            {"text": "0 criticals, 2 warnings", "prompt": False}]},
        {"template": "sparkline", "values": [1, 2, 3, 4, 5], "value_label": "225k+ stars",
         "caption": "still climbing every day"},
        {"template": "flash", "word": "still climbing"},
        {"template": "diagram", "nodes": [
            {"label": "ECC"}, {"label": "claude"}, {"label": "codex"},
            {"label": "cursor"}, {"label": "opencode"}]},
    ]}
    study_empty = {"components": ["ECC", "claude code adapter", "codex adapter",
                                  "cursor adapter", "opencode adapter"],
                   "commands": [], "outputs": [], "architecture_facts": []}
    f5 = run_checks(good_p, spec_path=write("spec.json", spec),
                    study_path=write("study0.json", study_empty))
    assert any("invented terminal content" in x for x in f5), f5

    # Case 6: same spec with the command properly studied and sourced — PASS,
    # growth scenes exactly at the cap (sparkline + flash), 2 backed scenes.
    study_full = {"components": study_empty["components"],
                  "commands": [{"text": "ecc security-review",
                                "source": "https://raw.githubusercontent.com/affaan-m/ECC/main/README.md"}],
                  "outputs": [{"text": "0 criticals, 2 warnings",
                               "source": "https://raw.githubusercontent.com/affaan-m/ECC/main/README.md"}],
                  "architecture_facts": []}
    f6 = run_checks(good_p, spec_path=write("spec.json", spec),
                    study_path=write("study1.json", study_full))
    assert f6 == [], f6

    # Case 7: three growth scenes — over the cap. Must FAIL.
    spec3 = {"scenes": spec["scenes"] + [
        {"template": "big_number", "numeral": "225k", "caption": "github stars today"}]}
    f7 = run_checks(good_p, spec_path=write("spec3.json", spec3),
                    study_path=write("study1.json", study_full))
    assert any("growth-metric scenes" in x for x in f7), f7

    print("SELFTEST PASSED (8 cases: shipped-caption FAIL, corrected PASS, "
          "linkless-gmail FAIL, linked-gmail PASS, linkedin-tells FAIL, "
          "invented-command FAIL, studied-command PASS, growth-cap FAIL)")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("deliverables", nargs="?", help="reports/deliverables-DATE.json")
    p.add_argument("--spec", help="reports/scene-spec-DATE.json")
    p.add_argument("--repo-study", dest="study", help="reports/repo-study-DATE.json")
    p.add_argument("--gmail", help="reports/gmail-DATE.html (the exact HTML to be sent)")
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args()

    if args.selftest:
        selftest()
        return

    if not args.deliverables:
        p.error("deliverables JSON path required (or --selftest)")

    fails = run_checks(args.deliverables, args.spec, args.study, args.gmail)
    if fails:
        print(f"DELIVERABLES CHECK FAILED ({len(fails)} issue(s)):")
        for f in fails:
            print(f"  FAIL: {f}")
        sys.exit(1)
    scope = ["copy"]
    if args.spec:
        scope.append("scene substance")
    if args.gmail:
        scope.append("gmail")
    print(f"DELIVERABLES CHECK PASSED ({' + '.join(scope)})")


if __name__ == "__main__":
    main()
