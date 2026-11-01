"""D13: paper figures (vector PDF, plus PNG previews for the README) from the run records only. usage: python d13_figures.py RUN_ID"""
import json, sys
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from common import Run, D_ROOT

EXP = D_ROOT / "experiments"; FIG = D_ROOT / "paper" / "figures"; FIG.mkdir(parents=True, exist_ok=True)
SRC = {"eval": "d08_rq1/runs/d08_eval_20261101_03/run.json", "event": "d11_event/runs/d11_event_20261101_02/run.json"}
run = Run(sys.argv[1], __file__, {"sources": SRC})
BLUE, ORANGE, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42})
ev = json.loads((EXP / SRC["eval"]).read_text())["results"]
out = []

# Fig 1: dose-response (main T0)
d = pd.DataFrame(ev["main_T0"]["dose_s1"])
fig, ax = plt.subplots(figsize=(3.6, 2.6))
x = range(len(d)); r = d.rate * 100
ax.errorbar(x, r, yerr=[r - d.lo * 100, d.hi * 100 - r], fmt="o", color=BLUE, ms=5, lw=1.5, capsize=0)
ax.set_xticks(list(x)); ax.set_xticklabels([f"{a}\n" + (f"{n/1e6:.1f}M" if n >= 1e6 else f"{n/1e3:.0f}k" if n >= 1e4 else f"{n:,}") for a, n in zip(d.s1, d.n)], fontsize=7); ax.set_yscale("log"); ax.set_ylim(0.02, 2); ax.set_xlim(-0.5, len(d) - 0.5)
ax.set_xlabel("Retracted references, $S_1$ (candidates below)"); ax.set_ylabel("Retracted later (%)")
ax.grid(axis="y", color=GRID, lw=0.6); ax.set_axisbelow(True); fig.tight_layout()
fig.savefig(FIG / "fig1_dose.pdf", bbox_inches="tight", metadata={"CreationDate": None, "ModDate": None}); out.append("fig1_dose.pdf")
fig.savefig(FIG / "fig1_dose.png", bbox_inches="tight", dpi=200, metadata={"Software": None}); out.append("fig1_dose.png"); plt.close(fig)

# Fig 2: within-journal MH odds ratios, main T0 vs T0'
rows = [("s1_ge1|all", "Cites retracted: all"), ("s1_ge1|mill", "Cites retracted: paper-mill outcome"),
        ("s1_ge1|nonmill", "Cites retracted: other outcomes"), ("s3_ge1|all", "Cited by retracted: all"),
        ("s3_ge1|mill", "Cited by retracted: paper-mill outcome"), ("s3_ge1|nonmill", "Cited by retracted: other outcomes")]
fig, ax = plt.subplots(figsize=(5.2, 2.6))
for off, tag, col, lab in [(-0.15, "main_T0", BLUE, "$T_0$ = 31 Jan 2024 (main)"), (0.15, "sens_c_T0p", ORANGE, "$T_0'$ = 30 Sep 2023")]:
    m = ev[tag]["mh"]
    for i, (k, _) in enumerate(rows):
        v = m[k]; ax.plot([v["lo"], v["hi"]], [i + off] * 2, color=col, lw=2, solid_capstyle="round")
        ax.plot(v["or_mh"], i + off, "o", color=col, ms=5, label=lab if i == 0 else None)
ax.axvline(1, color=MUTED, lw=0.8, ls="--"); ax.set_xscale("log"); ax.set_xticks([1, 2, 3, 4, 6]); ax.set_xticklabels(["1", "2", "3", "4", "6"])
ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[1] for r in rows]); ax.invert_yaxis()
ax.set_xlabel("Odds ratio within journal × year (95% CI)"); ax.legend(frameon=False, fontsize=7, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2)
ax.grid(axis="x", color=GRID, lw=0.6); ax.set_axisbelow(True); fig.tight_layout()
fig.savefig(FIG / "fig2_mh.pdf", bbox_inches="tight", metadata={"CreationDate": None, "ModDate": None}); out.append("fig2_mh.pdf")
fig.savefig(FIG / "fig2_mh.png", bbox_inches="tight", dpi=200, metadata={"Software": None}); out.append("fig2_mh.png"); plt.close(fig)

# Fig 3: citations per paper around retraction
e = pd.DataFrame(json.loads((EXP / SRC["event"]).read_text())["results"]["per_paper_all"])
fig, ax = plt.subplots(figsize=(3.4, 2.4))
ax.plot(e.k, e.retracted, "-o", color=BLUE, lw=2, ms=4); ax.plot(e.k, e.control, "-o", color=ORANGE, lw=2, ms=4)
ax.annotate("Retracted", (e.k.iloc[-1], e.retracted.iloc[-1]), xytext=(4, 0), textcoords="offset points", color=INK, fontsize=8, va="center")
ax.annotate("Matched\ncontrols", (e.k.iloc[-1], e.control.iloc[-1]), xytext=(4, 0), textcoords="offset points", color=INK, fontsize=8, va="center")
ax.axvline(0, color=MUTED, lw=0.8, ls="--"); ax.set_xlabel("Year relative to retraction notice"); ax.set_ylabel("Citations per paper")
ax.set_xlim(-5.4, 3.6); ax.grid(axis="y", color=GRID, lw=0.6); ax.set_axisbelow(True); fig.tight_layout()
fig.savefig(FIG / "fig3_event.pdf", bbox_inches="tight", metadata={"CreationDate": None, "ModDate": None}); out.append("fig3_event.pdf")
fig.savefig(FIG / "fig3_event.png", bbox_inches="tight", dpi=200, metadata={"Software": None}); out.append("fig3_event.png"); plt.close(fig)
for f in out:
    (run.dir / f).write_bytes((FIG / f).read_bytes())
run.log("figures", out)
run.finish()
