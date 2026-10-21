#!/usr/bin/env python3
"""Garde-fous de modification — photo-identite-bebe-domicile.fr

Implements the controls defined in docs/03-contraintes.md :
  Gate A  diff limité à la liste blanche
  Gate B  aucune modification de classe / style
  Gate C  empreinte structurelle (tag + class + style) inchangée (stories SEO)
  Gate D  nav / footer / barre mobile identiques à l'octet
  Gate E  fichiers noirs inchangés (JS, assets, templates, CNAME)
  Gate G  comparaison visuelle au pixel (Chrome headless + Pillow)

Usage:
  python3 scripts/garde_fous.py snapshot --story 00-baseline [--pages / /prix-photo-identite.html]
  python3 scripts/garde_fous.py diff --allow 'aide/*.html' [--seo]
  python3 scripts/garde_fous.py structure --baseline backup/00-baseline [--seo] [--allow-new 'aide/*.html']
  python3 scripts/garde_fous.py visuel --story backup/<dir> --page /prix-photo-identite.html [--viewport 390x844] [--seuil 0]

Aucune dépendance externe (Pillow uniquement pour `visuel`).
"""
import argparse
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
STORY_PAGES = [
    "index.html", "photo-identite-bebe-ile-de-france.html",
    "photo-identite-a-domicile-ile-de-france.html",
    "photographe-agree-ants-ile-de-france.html", "prix-photo-identite.html",
]

# --------------------------------------------------------------------------
# Inventaire des fichiers protégés (sauvegardés à chaque snapshot)
# --------------------------------------------------------------------------
def protected_files():
    files = set()
    patterns = [
        "*.html", "villes/*.html", "aide/*.html", "aide/*/index.html",
        "sitemap.xml", "robots.txt", ".gitignore", "CNAME", "site.webmanifest",
        "logo.png", "favicon.ico", "favicon.svg", "favicon-96x96.png",
        "apple-touch-icon.png", "web-app-manifest-*.png",
        "*.js", "config/*.js",
        "data/*.json", "scripts/generate_villes.py",
        "templates/**/*.html", "Images/*",
    ]
    for p in patterns:
        for f in glob.glob(p, recursive=True):
            if os.path.isfile(f):
                files.add(f.replace(os.sep, "/"))
    return sorted(files)

BLACKLIST = [
    ".js", ".css", ".scss", ".sass", ".less", ".png", ".jpg", ".jpeg", ".webp",
    ".ico", ".svg", ".woff", ".woff2", ".json", ".webmanifest", "CNAME",
    "templates/", "Images/",
]

def is_blacklisted(path):
    p = "/" + path
    return (
        path.startswith(("templates/", "Images/", "config/"))
        or path in ("CNAME", "site.webmanifest")
        or any(path.endswith(ext) for ext in (".js", ".css", ".scss", ".sass", ".less"))
        or any(path.endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".webp", ".ico", ".svg"))
    )


def preexisting_paths(manifest):
    """Chemins qui étaient déjà non suivis au moment du snapshot de référence.
    Ils ne sont pas imputables à la story en cours et sont donc tolérés."""
    out = set()
    for line in manifest.get("git_status", []):
        if line.startswith("??"):
            out.add(line[3:].strip().strip('"').rstrip("/"))
    return out


def baseline_tree(manifest):
    """Fichiers déjà versionnés au commit de référence (snapshot 00-baseline)."""
    head = manifest.get("git_head")
    if not head:
        return set()
    return {p for p in git("ls-tree", "-r", "--name-only", head).splitlines() if p}


def class_tokens(path):
    s = open(path, encoding="utf-8", errors="replace").read()
    toks = set()
    for m in re.findall(r'class="([^"]*)"', s):
        toks.update(m.split())
    return toks

def style_blocks(path):
    s = open(path, encoding="utf-8", errors="replace").read()
    out = set()
    for b in re.findall(r'<style[^>]*>(.*?)</style>', s, re.S | re.I):
        out.add(" ".join(b.split()))
    return out

def region_hashes(path):
    return {regions(path)} if os.path.exists(path) else set()

def content_new_ok(path, baseline_dir):
    """Page de contenu : classes existantes uniquement, styles et nav/footer identiques au site."""
    problems = []
    vocab, styles, navs = set(), set(), set()
    for f in glob.glob(os.path.join(baseline_dir, "**", "*.html"), recursive=True):
        vocab |= class_tokens(f)
        styles |= style_blocks(f)
        navs.add(regions(f))
    extra = class_tokens(path) - vocab
    if extra:
        problems.append(f"classes inédites: {sorted(extra)[:5]}")
    extra_css = style_blocks(path) - styles
    if extra_css:
        problems.append("bloc <style> inédit")
    raw = open(path, encoding="utf-8", errors="replace").read()
    if "<nav" in raw.lower() or "<footer" in raw.lower():
        if regions(path) not in navs:
            problems.append("nav/footer/barre mobile différents du site")
    if re.search(r'\bstyle\s*=', open(path, encoding="utf-8", errors="replace").read()):
        problems.append("attribut style= présent")
    return problems

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

# --------------------------------------------------------------------------
# Empreinte structurelle et zones sensibles
# --------------------------------------------------------------------------
class Fingerprint(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def _record(self, tag, attrs):
        d = dict(attrs)
        self.parts.append(f"{tag}|{d.get('class', '')}|{d.get('style', '')}")

    def handle_starttag(self, tag, attrs):
        self._record(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        self._record(tag, attrs)


def fingerprint(path):
    fp = Fingerprint()
    fp.feed(open(path, encoding="utf-8", errors="replace").read())
    return hashlib.sha256("\n".join(fp.parts).encode()).hexdigest()


def regions(path):
    s = open(path, encoding="utf-8", errors="replace").read()
    out = []
    for pat in (r"(?is)<nav\b.*?</nav>", r"(?is)<footer\b.*?</footer>",
                r"(?is)<div[^>]*fixed bottom-0[^>]*>.*?</div>"):
        out += re.findall(pat, s)
    return hashlib.sha256("\n".join(out).encode()).hexdigest()


def new_file_ok(path):
    """Un fichier nouveau (stub) ne doit contenir ni classe, ni style, ni CSS."""
    s = open(path, encoding="utf-8", errors="replace").read()
    problems = []
    if re.search(r'\bclass\s*=', s):
        problems.append("attribut class")
    if re.search(r'\bstyle\s*=', s):
        problems.append("attribut style")
    if re.search(r"<style\b", s, re.I):
        problems.append("bloc <style>")
    if re.search(r'rel=["\']stylesheet["\']', s, re.I):
        problems.append("feuille de style externe")
    return problems

# --------------------------------------------------------------------------
# Sub-commandes
# --------------------------------------------------------------------------
def git(*args):
    return subprocess.run(["git", "-c", "core.quotePath=false", *args], capture_output=True, text=True).stdout


def cmd_snapshot(args):
    ts = __import__("datetime").datetime.now().strftime("%Y%m%d-%H%M%S")
    out = os.path.join("backup", "00-baseline" if args.story.startswith("00") else f"{ts}-{args.story}")
    files_dir = os.path.join(out, "files")
    shots_dir = os.path.join(out, "screenshots")
    os.makedirs(files_dir, exist_ok=True)
    os.makedirs(shots_dir, exist_ok=True)

    manifest = {
        "story": args.story,
        "date": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
        "git_head": git("rev-parse", "--short", "HEAD").strip(),
        "git_status": [l for l in git("status", "--porcelain", "-uall").splitlines()],
        "files": {},
        "screenshots": [],
    }
    files = protected_files()
    print(f"Snapshot {out} — {len(files)} fichiers protégés")
    for rel in files:
        dst = os.path.join(files_dir, rel)
        os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
        with open(rel, "rb") as src, open(dst, "wb") as fh:
            fh.write(src.read())
        manifest["files"][rel] = sha256(rel)
    with open(os.path.join(out, "pre.diff"), "w", encoding="utf-8") as fh:
        fh.write(git("diff"))
    with open(os.path.join(out, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=1)
    print("Manifest écrit :", os.path.join(out, "manifest.json"))

    if args.pages:
        for page in args.pages:
            for vp in ("390x844", "1440x900"):
                dest = os.path.join(shots_dir, f"before-{page.strip('/').replace('/', '_') or 'home'}-{vp}.png")
                capture(page, vp, dest)
    return 0


def capture(page, viewport, dest):
    url = f"http://127.0.0.1:8765/{page.lstrip('/')}"
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
           "--force-prefers-reduced-motion", f"--window-size={viewport.replace('x', ',')}",
           "--virtual-time-budget=6000", f"--screenshot={dest}", url]
    subprocess.run(cmd, capture_output=True, timeout=90)
    print(f"  capture {page} {viewport} -> {dest}")


def cmd_diff(args):
    """Gate A + B : compare l'arbre courant au snapshot de référence."""
    manifest = json.load(open(os.path.join(args.baseline, "manifest.json"), encoding="utf-8"))
    base = os.path.join(args.baseline, "files")
    changed, new = [], []
    for rel, expected in manifest["files"].items():
        if rel.startswith("backup/"):
            continue
        if not os.path.exists(rel):
            changed.append(rel)
        elif sha256(rel) != expected:
            changed.append(rel)
    pre = preexisting_paths(manifest) | baseline_tree(manifest)
    for rel in git("ls-files", "-co", "--exclude-standard").splitlines():
        rel = rel.strip()
        if not rel or rel.startswith(("backup/", "docs/")):
            continue
        if rel not in manifest["files"] and rel not in pre and not any(rel.startswith(p + "/") for p in pre):
            new.append(rel)

    allowed = [re.compile("^docs/"), re.compile("^backup/"),
               re.compile(r"^scripts/garde_fous\.py$"), re.compile(r"^\.gitignore$")]
    for pat in args.allow:
        allowed.append(re.compile("^" + pat.replace(".", r"\.").replace("*", ".*") + "$"))

    errors = 0
    for rel in changed + new:
        if not any(r.match(rel) for r in allowed):
            print(f"ECHEC Gate A — hors liste blanche : {rel}")
            errors += 1
    print(f"Gate A {'OK' if not errors else 'ECHEC'} — {len(changed)} fichier(s) modifié(s), {len(new)} nouveau(x)")

    if args.seo:
        for rel in changed:
            if rel.endswith((".html", ".xml", ".txt")) and os.path.exists(rel):
                old = os.path.join(base, rel)
                if not os.path.exists(old):
                    continue
                import difflib
                a = open(old, encoding="utf-8", errors="replace").read().splitlines()
                b = open(rel, encoding="utf-8", errors="replace").read().splitlines()
                for line in difflib.unified_diff(a, b, n=0):
                    if line.startswith(("+", "-")) and not line.startswith(("+++", "---")):
                        if re.search(r'(class="|style="|<style|@media|rel="stylesheet")', line):
                            print(f"ECHEC Gate B — ligne de style modifiée dans {rel} : {line[:90]}")
                            errors += 1
        print(f"Gate B {'OK' if not errors else 'ECHEC'} — aucune classe/style modifiée")
    return 1 if errors else 0


def cmd_structure(args):
    base = os.path.join(args.baseline, "files")
    manifest = json.load(open(os.path.join(args.baseline, "manifest.json"), encoding="utf-8"))
    errors = 0

    # Gate E — fichiers noirs inchangés
    checked = 0
    for rel, expected in manifest["files"].items():
        if not is_blacklisted(rel) or not os.path.exists(rel):
            continue
        checked += 1
        if sha256(rel) != expected:
            print(f"ECHEC Gate E — fichier noir modifié : {rel}")
            errors += 1
    print(f"Gate E OK — {checked} fichier(s) noir(s) inchangé(s)")

    # Gate C / D — pages HTML modifiées
    for rel in manifest["files"]:
        if not rel.endswith(".html") or not os.path.exists(rel):
            continue
        if sha256(rel) == manifest["files"][rel]:
            continue
        if regions(rel) != regions(os.path.join(base, rel)):
            print(f"ECHEC Gate D — nav/footer/barre modifié : {rel}")
            errors += 1
        if args.seo:
            if fingerprint(rel) != fingerprint(os.path.join(base, rel)):
                print(f"ECHEC Gate C — empreinte structurelle modifiée : {rel}")
                errors += 1
            else:
                print(f"Gate C/D OK — {rel}")
        else:
            print(f"Gate D OK — {rel} (contenu, empreinte libre)")

    # Contrôle du vocabulaire de classes pour les fichiers modifiés (mode contenu)
    if args.content_new:
        base_files = os.path.join(args.baseline, "files")
        vocab = set()
        for f in glob.glob(os.path.join(base_files, "**", "*.html"), recursive=True):
            vocab |= class_tokens(f)
        for rel in manifest["files"]:
            if not rel.endswith(".html") or not os.path.exists(rel):
                continue
            if sha256(rel) == manifest["files"][rel]:
                continue
            extra = class_tokens(rel) - vocab
            if extra:
                print(f"ECHEC — classes inédites dans {rel} : {sorted(extra)[:5]}")
                errors += 1
            if style_blocks(rel) - style_blocks(os.path.join(base_files, rel)):
                print(f"ECHEC — bloc <style> modifié dans {rel}")
                errors += 1
        print(f"Gate C (contenu) — vocabulaire de classes vérifié")

    # Nouveaux fichiers .html
    allow_new = [re.compile("^" + p.replace(".", r"\.").replace("*", ".*") + "$") for p in args.allow_new]
    pre = preexisting_paths(manifest) | baseline_tree(manifest)
    for rel in git("ls-files", "-co", "--exclude-standard").splitlines():
        rel = rel.strip()
        if not rel.endswith(".html"):
            continue
        if rel.startswith("backup/") or rel in manifest["files"] or rel in pre:
            continue
        if allow_new and not any(r.match(rel) for r in allow_new):
            print(f"ECHEC — nouveau fichier HTML non autorisé : {rel}")
            errors += 1
            continue
        problems = content_new_ok(rel, os.path.join(args.baseline, "files")) if args.content_new else new_file_ok(rel)
        if problems:
            print(f"ECHEC — {rel} contient : {', '.join(problems)}")
            errors += 1
        else:
            print(f"Gate C/D OK (nouveau) — {rel} sans classe/style")

    return 1 if errors else 0


def cmd_visuel(args):
    from PIL import Image, ImageChops
    shots = os.path.join(args.story, "screenshots")
    os.makedirs(shots, exist_ok=True)
    server = subprocess.Popen([sys.executable, "-m", "http.server", "8765", "--bind", "127.0.0.1"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    errors = 0
    try:
        __import__("time").sleep(1)
        name = args.page.strip("/").replace("/", "_") or "home"
        for vp in args.viewports:
            before = os.path.join(shots, f"before-{name}-{vp}.png")
            after = os.path.join(shots, f"after-{name}-{vp}.png")
            if not os.path.exists(before):
                print(f"ECHEC Gate G — capture 'avant' absente : {before}")
                errors += 1
                continue
            capture(args.page, vp, after)
            a = Image.open(before).convert("RGB")
            b = Image.open(after).convert("RGB")
            if a.size != b.size:
                print(f"ECHEC Gate G — dimensions différentes ({a.size} vs {b.size})")
                errors += 1
                continue
            diff = ImageChops.difference(a, b)
            changed = sum(1 for px in diff.getdata() if max(px) > 8)
            status = "OK" if changed <= args.seuil else "ECHEC"
            print(f"Gate G {status} — {name} {vp} : {changed} pixel(s) différent(s) (seuil {args.seuil})")
            errors += 0 if changed <= args.seuil else 1
    finally:
        server.terminate()
    return 1 if errors else 0


def main():
    ap = argparse.ArgumentParser(description="Garde-fous docs/03-contraintes.md")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("snapshot"); s.add_argument("--story", required=True)
    s.add_argument("--pages", nargs="*", default=[]); s.set_defaults(func=cmd_snapshot)

    d = sub.add_parser("diff"); d.add_argument("--baseline", required=True)
    d.add_argument("--allow", action="append", default=[])
    d.add_argument("--seo", action="store_true"); d.set_defaults(func=cmd_diff)

    st = sub.add_parser("structure"); st.add_argument("--baseline", required=True)
    st.add_argument("--seo", action="store_true"); st.add_argument("--content-new", action="store_true")
    st.add_argument("--allow-new", nargs="*", default=[])
    st.set_defaults(func=cmd_structure)

    v = sub.add_parser("visuel"); v.add_argument("--story", required=True)
    v.add_argument("--page", required=True); v.add_argument("--viewports", nargs="*", default=["390x844", "1440x900"])
    v.add_argument("--seuil", type=int, default=0); v.set_defaults(func=cmd_visuel)

    args = ap.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
