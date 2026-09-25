"""Standalone HTML report for a run. No server needed: open the file."""

import html

from .pipeline import ROOT

CSS = """
:root{--bg:#fbfbfa;--fg:#1d1d1b;--muted:#6b6b66;--card:#fff;--line:#e4e3de;--ok:#1f7a4d;--okbg:#e5f4ec;
--bad:#b3261e;--badbg:#fbe9e7;--warn:#8a5a00;--warnbg:#fff4d6;--code:#f3f2ee}
@media (prefers-color-scheme:dark){:root{--bg:#161615;--fg:#ecebe6;--muted:#a09f99;--card:#1f1f1d;--line:#34332f;
--ok:#6fd3a0;--okbg:#17332a;--bad:#ff8a80;--badbg:#3a1d1b;--warn:#f5c35b;--warnbg:#3a2f14;--code:#262624}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:980px;margin:0 auto;padding:32px 16px 64px}h1{font-size:26px;margin:0 0 4px}h2{font-size:19px;margin:36px 0 12px}
.sub{color:var(--muted);margin:0 0 20px}.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin:12px 0}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}.stat b{display:block;font-size:26px}
.stat span{color:var(--muted);font-size:13px}.badge{display:inline-block;padding:2px 10px;border-radius:999px;font-weight:600;font-size:13px}
.VERIFIED{background:var(--okbg);color:var(--ok)}.BLOCKED{background:var(--badbg);color:var(--bad)}.NOT{background:var(--warnbg);color:var(--warn)}
.banner{background:var(--warnbg);color:var(--warn);border-radius:10px;padding:10px 14px;margin:12px 0;font-weight:600}
table{width:100%;border-collapse:collapse;font-size:14px}td,th{text-align:left;padding:7px 8px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--muted);font-weight:600}code,pre{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12.5px}
pre{background:var(--code);padding:12px;border-radius:8px;overflow-x:auto;max-height:480px}.add{color:var(--ok)}.del{color:var(--bad)}
.k{color:var(--ok);font-weight:600}.s{color:var(--bad);font-weight:600}summary{cursor:pointer;color:var(--muted)}a{color:inherit}
"""


def _e(s):
    return html.escape(str(s))


def _diff_html(diff):
    out = []
    for line in diff.splitlines():
        cls = "add" if line.startswith("+") and not line.startswith("+++") else \
              "del" if line.startswith("-") and not line.startswith("---") else ""
        out.append(f'<span class="{cls}">{_e(line)}</span>' if cls else _e(line))
    return "\n".join(out)


def _mutation_table(score):
    rows = "".join(
        f"<tr><td><code>{_e(m['id'])}</code></td><td>{_e(m['quirk'])}</td>"
        f"<td class=\"{'k' if m['killed'] else 's'}\">{'caught' if m['killed'] else 'missed'}</td>"
        f"<td>{_e(', '.join(m['by']))}</td></tr>" for m in score["mutants"])
    return f"<table><tr><th>Mutant</th><th>Legacy quirk it breaks</th><th>Result</th><th>Caught by</th></tr>{rows}</table>"


def render(state) -> str:
    char = state.get("characterization") or {}
    base = char.get("baseline") or {}
    mut = char.get("mutation")
    ctrl = char.get("control_mutation")
    mods = state.get("modernizations", [])
    modes = state.get("modes", [])

    banner = ""
    if "fixture" in modes:
        banner = '<div class="banner">Fixture mode: responses are hand-written test data, NOT Bob output.</div>'
    elif "replay" in modes:
        banner = '<div class="banner">Replay: Bob responses replayed from recorded sessions in bob_sessions/.</div>'

    stats = f"""<div class="stats">
<div class="card stat"><b>{base.get('tests', 0)}</b><span>characterization tests written by Bob</span></div>
<div class="card stat"><b>{'pass' if base.get('compiled') and not base.get('failures') and not base.get('errors') else 'fail'}</b><span>on the untouched legacy code</span></div>
<div class="card stat"><b>{f"{mut['killed']}/{mut['total']}" if mut else 'n/a'}</b><span>behaviour mutants caught (hand-written controls: {f"{ctrl['killed']}/{ctrl['total']}" if ctrl else 'n/a'})</span></div>
<div class="card stat"><b>{sum(m['verdict'] == 'VERIFIED' for m in mods)} / {sum(m['verdict'] == 'BLOCKED' for m in mods)}</b><span>modernizations verified / blocked</span></div>
</div>"""

    char_html = ""
    if char:
        fixes = f" Bob corrected its own suite in {char['fix_rounds']} round(s) after it failed on the original." if char.get("fix_rounds") else ""
        links = " ".join(f'<a href="../../{_e(t)}">{_e(t.split("/")[-1])}</a>' for t in char.get("transcripts", []))
        char_html = f"""<h2>1. Characterization tests</h2><div class="card">
<p>Bob read the legacy file and wrote <code>{_e(char['test_class'])}</code> to pin down what it does today.{fixes}
Each mutant below breaks one known legacy quirk; a good safety net must catch every one.</p>
{_mutation_table(mut) if mut else '<p>Suite did not pass on the original, so it was not scored.</p>'}
<p class="sub">Transcripts: {links}</p></div>"""

    mod_html = ""
    for i, m in enumerate(mods, 2):
        v = m["verdict"]
        cls = "NOT" if v == "NOT ATTEMPTED" else v
        body = ""
        if "result" in m:
            r = m["result"]
            failed = "".join(f"<tr><td><code>{_e(f['name'])}</code></td><td>{_e(f['message'])}</td></tr>" for f in r["failed"])
            status = (f"{r['tests'] - r['failures'] - r['errors']}/{r['tests']} characterization tests pass"
                      if r["compiled"] else "does not compile")
            outcome = (f"Applied to <code>{_e(m['applied_to'])}</code>." if m.get("applied_to")
                       else "Not applied: the legacy file is unchanged.")
            body = f"""<p><b>{status}.</b> {outcome}</p>
{'<table><tr><th>Failing test</th><th>What changed</th></tr>' + failed + '</table>' if failed else ''}
<details><summary>Diff (legacy → Bob)</summary><pre>{_diff_html(m['diff'])}</pre></details>"""
        else:
            body = f"<p>{_e(m.get('reason', ''))}</p>"
        mod_html += f"""<h2>{i}. Modernization: <span class="badge {cls}">{_e(v)}</span></h2><div class="card">
<p><b>Request:</b> {_e(m['goal'])}</p>{body}
<p class="sub">Transcript: <a href="../../{_e(m['transcript'])}">{_e(m['transcript'].split('/')[-1])}</a></p></div>"""

    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Legacy Bridge report</title>
<style>{CSS}</style></head><body><main>
<h1>Legacy Bridge report</h1>
<p class="sub">Run {_e(state['id'])} · <code>{_e(state['source_file'])}</code> · Bob modernizes; Bob's own characterization tests decide what ships.</p>
{banner}{stats}{char_html}{mod_html}
</main></body></html>"""


def write(run) -> str:
    path = run.dir / "report.html"
    path.write_text(render(run.state), encoding="utf-8")
    return str(path.relative_to(ROOT))
