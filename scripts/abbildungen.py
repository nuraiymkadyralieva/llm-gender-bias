"""Abbildungen für Kapitel 5 (PNG, 300 dpi). Farben: Studienwahl blau, Beruf orange,
zusätzlich unterschiedliche Marker (Kreis/Quadrat), damit die Zuordnung nicht nur über Farbe erfolgt."""
from pathlib import Path
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
MODELLE = [("openai", "GPT-6.1"), ("anthropic", "Claude Sonnet 5.5"), ("google", "Gemini 4")]
SZ = {"studienwahl": ("Studienwahl", "#2a78d6", "o"), "beruf": ("Beruf", "#eb6834", "s")}
INK, MUTED, GRID = "#1f1f1e", "#6b6a64", "#e4e3dd"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False})
rng = np.random.default_rng(1)

def abb_delta_f():
    pv = pd.read_csv(ROOT / "results/tables/kennzahlen_profil_variante.csv")
    w = pv.pivot_table(index=["model_key", "scenario", "profile_id"], columns="variant", values="F").reset_index()
    w["d"] = (w["w"] - w["m"]) * 100
    tests = pd.read_csv(ROOT / "results/tables/tests.csv")
    fig, ax = plt.subplots(figsize=(6.3, 2.9))
    ax.axvline(0, color=MUTED, lw=1, zorder=1)
    for i, (mk, name) in enumerate(MODELLE):
        y0 = len(MODELLE) - 1 - i
        for sc, (lab, col, mar) in SZ.items():
            d = w[(w.model_key == mk) & (w.scenario == sc)]["d"]
            off = 0.13 if sc == "studienwahl" else -0.13
            ax.scatter(d, y0 + off + rng.uniform(-0.05, 0.05, len(d)), s=22, color=col, marker=mar,
                       edgecolor="white", linewidth=0.8, zorder=3, label=lab if i == 0 else None)
        t = tests[(tests.modell == name) & (tests.szenario == "beide") & (tests.kennzahl == "ΔF") & (tests.vergleich == "w-m")].iloc[0]
        ax.plot([t.ki_unten * 100, t.ki_oben * 100], [y0 - 0.32] * 2, color=INK, lw=2, solid_capstyle="round", zorder=4)
        ax.scatter([t["median"] * 100], [y0 - 0.32], s=30, color=INK, zorder=5)
        ax.text(6.4, y0, f"Median {(t['median']*100 if abs(t['median']*100)>=0.05 else 0.0):+.1f} pp\np = {t.p_wilcoxon:.3f}",
                va="center", ha="left", fontsize=8, color=MUTED)
    ax.set_yticks(range(len(MODELLE))); ax.set_yticklabels([n for _, n in MODELLE][::-1])
    ax.set_xlim(-4, 6.2); ax.set_ylim(-0.6, 2.5)
    ax.set_xlabel("ΔF = F(weiblich) − F(männlich) in Prozentpunkten")
    ax.grid(axis="x", color=GRID, lw=0.8); ax.set_axisbelow(True)
    ax.legend(loc="upper left", frameon=False, fontsize=8, ncol=2, bbox_to_anchor=(0, 1.12))
    fig.tight_layout(); fig.subplots_adjust(right=0.8)
    fig.savefig(ROOT / "results/figures/abb_delta_f.png", dpi=300)

def abb_jaccard():
    jz = pd.read_csv(ROOT / "results/tables/jaccard.csv")
    jz = jz[(jz.ebene == "fein") & (jz.paar == "w-m")]
    fig, ax = plt.subplots(figsize=(6.3, 2.6))
    x = 0; ticks = []; labels = []
    for mk, name in MODELLE:
        for sc, (lab, col, mar) in SZ.items():
            s = jz[(jz.model_key == mk) & (jz.scenario == sc)]
            a, b = s.J_innerhalb.mean(), s.J_zwischen.mean()
            ax.plot([x, x], [a, b], color=col, lw=2, zorder=2)
            ax.scatter([x], [a], s=36, facecolor="white", edgecolor=col, linewidth=1.8, marker=mar, zorder=3)
            ax.scatter([x], [b], s=36, color=col, marker=mar, edgecolor="white", linewidth=0.8, zorder=3)
            x += 1
        ticks.append(x - 1.5); labels.append(name); x += 0.8
    ax.set_xticks(ticks); ax.set_xticklabels(labels)
    ax.set_ylim(0.6, 0.85); ax.set_ylabel("mittlere Jaccard-Überschneidung")
    ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True)
    from matplotlib.lines import Line2D
    h = [Line2D([], [], marker="o", ls="", markerfacecolor="white", markeredgecolor=MUTED, label="innerhalb einer Variante (Wiederholungen)"),
         Line2D([], [], marker="o", ls="", color=MUTED, label="zwischen weiblich und männlich"),
         Line2D([], [], marker="o", ls="", color=SZ["studienwahl"][1], label="Studienwahl"),
         Line2D([], [], marker="s", ls="", color=SZ["beruf"][1], label="Beruf")]
    ax.legend(handles=h, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(ROOT / "results/figures/abb_jaccard.png", dpi=300)

if __name__ == "__main__":
    abb_delta_f(); abb_jaccard(); print("ok")
