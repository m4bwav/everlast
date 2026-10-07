#!/usr/bin/env python3
"""Keep each skill's copies of the shared docs in step with their source.

Agent Skills linters (vally, used by github/awesome-copilot) reject a SKILL.md
link that leaves the skill folder, so a skill links `references/<dir>/<file>`
and this script copies `<dir>/<file>` from the plugin root there. The root
folder stays the one to edit. In a copy, a relative link to a file the skill
does not carry becomes a GitHub URL; links to files that do not exist (examples)
are left alone.

  python scripts/sync-skill-refs.py           write the copies, delete stale ones
  python scripts/sync-skill-refs.py --check   exit 1 if any copy is missing, stale or edited

Stdlib only, Python 3.9+.
"""
import pathlib
import re
import sys

SHARED_DIRS = ["protocol"]
BLOB = "https://github.com/m4bwav/everlast/blob/master/"

ROOT = pathlib.Path(__file__).resolve().parent.parent
LINK = re.compile(r"(\]\()([^)\s]+)(\))")
HEADER = "<!-- Copy of {src}, written by scripts/sync-skill-refs.py. Edit {src} and run the script. -->\n"


def wanted():
    """{copy path: source path} for every references/<dir>/<file> link in a SKILL.md."""
    out = {}
    for skill_md in sorted((ROOT / "skills").glob("*/SKILL.md")):
        text = skill_md.read_text(encoding="utf-8")
        for m in LINK.finditer(text):
            target = m.group(2).split("#")[0]
            parts = target.split("/")
            if len(parts) == 3 and parts[0] == "references" and parts[1] in SHARED_DIRS:
                src = ROOT / parts[1] / parts[2]
                if src.is_file():
                    out[skill_md.parent / target] = src
    return out


def render(src, copy, carried):
    def fix(m):
        target = m.group(2)
        if re.match(r"^[a-z][a-z0-9+.-]*:|^#|^/", target):
            return m.group(0)
        path, _, anchor = target.partition("#")
        resolved = (src.parent / path).resolve()
        if not resolved.exists():
            return m.group(0)
        if copy.parent / resolved.name in carried and resolved.parent == src.parent:
            return m.group(0)
        rel = resolved.relative_to(ROOT).as_posix()
        return m.group(1) + BLOB + rel + ("#" + anchor if anchor else "") + m.group(3)

    body = src.read_text(encoding="utf-8")
    return HEADER.format(src=src.relative_to(ROOT).as_posix()) + LINK.sub(fix, body)


def main(argv):
    check = "--check" in argv
    want = wanted()
    problems = []
    for copy, src in want.items():
        text = render(src, copy, want)
        current = copy.read_text(encoding="utf-8") if copy.exists() else None
        if current == text:
            continue
        if check:
            problems.append("%s: %s" % (copy.relative_to(ROOT).as_posix(), "missing" if current is None else "differs from " + src.relative_to(ROOT).as_posix()))
        else:
            copy.parent.mkdir(parents=True, exist_ok=True)
            copy.write_bytes(text.encode("utf-8"))
    for d in SHARED_DIRS:
        for stale in sorted((ROOT / "skills").glob("*/references/%s/*" % d)):
            if stale not in want:
                if check:
                    problems.append("%s: not linked from its SKILL.md" % stale.relative_to(ROOT).as_posix())
                else:
                    stale.unlink()
    for p in problems:
        print(p)
    if problems:
        print("run: python scripts/sync-skill-refs.py")
        return 1
    print("skill references in sync (%d copies)" % len(want))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
