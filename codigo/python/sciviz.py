"""sciviz — publication-grade figure primitives for matplotlib.

Why this module exists
----------------------
Hand-positioning text in absolute coordinates is the single most common cause of
rejected figures: labels collide with tick marks, annotations overrun panels, and
nothing is caught until a human squints at the render. This module removes the
whole class of error by (a) forcing physical sizing in millimetres, (b) using
matplotlib's constrained layout so the solver places text, and (c) measuring every
Text artist against the real renderer before export.

Typical use
-----------
    import sciviz

    sciviz.apply_style()
    fig, ax = sciviz.new_figure(width="single", height_mm=70)
    ...
    sciviz.finalize(
        fig,
        outdir="02_final/figuras",
        stem="figura_01_serie_clase70",
        contract="F01",
        source="04_extraccion_series/.../serie_indicadores_acr_1985_2024.csv",
        note="Clasificación cartográfica anual; no demuestra condición ecológica.",
    )

`finalize` raises SciVizError on a hard violation (overlapping text, font below the
floor, missing provenance). That is deliberate: a figure that fails these checks
should never reach a reviewer.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import warnings
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Iterable, Sequence

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.text import Text

__all__ = [
    "pt",
    "unit",
    "SUPERSCRIPT",
    "SciVizError",
    "MM",
    "WIDTHS",
    "apply_style",
    "new_figure",
    "new_panel_grid",
    "finalize",
    "check_layout",
    "OKABE_ITO",
    "palette",
    "sequential",
    "diverging",
    "add_scalebar",
    "add_north_arrow",
    "add_locator_inset",
    "declare_n",
    "booktabs_latex",
]


class SciVizError(RuntimeError):
    """Raised when a figure violates a non-negotiable publication rule."""


# --------------------------------------------------------------------------
# Physical sizing
# --------------------------------------------------------------------------

MM = 1.0 / 25.4  # millimetres -> inches

#: Common journal text-block widths in mm. Override with an explicit number when
#: the target journal publishes its own value — most do, in the author guide.
WIDTHS = {
    "single": 85.0,    # single column (Elsevier 90, Springer 84, PNAS 87 — 85 is safe)
    "onehalf": 120.0,  # 1.5 column
    "double": 180.0,   # full text width / double column
    "a4text": 160.0,   # A4 portrait with 25 mm margins (thesis body)
    "a4land": 257.0,   # A4 landscape with 20 mm margins
    "a3land": 400.0,   # A3 landscape map sheet with 10 mm margins
    "poster": 300.0,   # one column of a typical A0 scientific poster
}

#: Absolute floor for rendered text. Below ~6 pt, print is unreadable and most
#: publishers reject outright. 7 pt is the practical minimum for figure text.
MIN_FONT_PT = 7.0
PREFERRED_FONT_PT = 8.0


def pt(frac: float = 1.0) -> float:
    """Font size as a fraction of the current base size, never below the floor.

    Use this instead of hard-coding sizes: it keeps secondary text subordinate
    while guaranteeing it is still legible in print.
    """
    return max(MIN_FONT_PT, mpl.rcParams["font.size"] * frac)


# --------------------------------------------------------------------------
# Units
# --------------------------------------------------------------------------

SUPERSCRIPT = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")


def unit(*factors: str, sep: str = "·") -> str:
    """Compose an unambiguous compound unit.

    `unit("g", "m-2")` -> "g·m⁻²"   `unit("m3", "s-1")` -> "m³·s⁻¹"

    The middle dot matters. Written as "g m-2" a reader has to infer whether the
    two symbols are multiplied or divided, and a bare hyphen reads as a minus
    sign rather than a negative exponent. Either write the product explicitly
    with a dot, or use the solidus form ("g/m²") — but pick one convention and
    hold it across every figure and table in the document.

    Each factor is "<symbol><exponent>" with the exponent optional and signed:
    "g", "m-2", "s-1", "ha", "1000ha-1".
    """
    out = []
    for f in factors:
        f = f.strip()
        m = re.match(r"^(.+?)(-?\d+)$", f)   # only a *trailing* signed integer is an exponent
        if not m:
            out.append(f)
            continue
        sym, exp = m.group(1), m.group(2)
        out.append(sym if exp == "1" else sym + exp.translate(SUPERSCRIPT))
    return sep.join(out)


def _resolve_width(width) -> float:
    if isinstance(width, str):
        try:
            return WIDTHS[width]
        except KeyError:
            raise SciVizError(
                f"Unknown width alias {width!r}. Use one of {sorted(WIDTHS)} or a number in mm."
            )
    return float(width)


# --------------------------------------------------------------------------
# Style
# --------------------------------------------------------------------------

def apply_style(base_pt: float = 8.0, family: str = "sans-serif") -> None:
    """Install a neutral, journal-safe rcParam set.

    Deliberately plain: no seaborn grid washes, no coloured backgrounds, no
    top/right spines. Anything decorative competes with the data for the
    reader's attention, and reviewers read that as noise.
    """
    if base_pt < MIN_FONT_PT:
        raise SciVizError(f"base_pt={base_pt} is below the {MIN_FONT_PT} pt floor.")

    mpl.rcParams.update({
        "figure.dpi": 150,
        "savefig.dpi": 600,
        "savefig.bbox": None,          # constrained layout already handles margins
        "savefig.transparent": False,
        "savefig.facecolor": "white",
        "figure.facecolor": "white",
        "axes.facecolor": "white",

        "font.family": family,
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "Liberation Sans"],
        "font.serif": ["Times New Roman", "DejaVu Serif", "Liberation Serif"],
        "font.size": base_pt,
        "axes.titlesize": base_pt * 1.05,
        "axes.labelsize": base_pt,
        "xtick.labelsize": max(MIN_FONT_PT, base_pt * 0.9),
        "ytick.labelsize": max(MIN_FONT_PT, base_pt * 0.9),
        "legend.fontsize": max(MIN_FONT_PT, base_pt * 0.9),
        "figure.titlesize": base_pt * 1.2,

        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.titlepad": 4.0,
        "axes.labelpad": 3.0,

        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.6,
        "axes.axisbelow": True,

        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.major.size": 2.5,
        "ytick.major.size": 2.5,

        "grid.color": "#D9D9D9",
        "grid.linewidth": 0.4,
        "grid.alpha": 1.0,

        "lines.linewidth": 1.2,
        "lines.markersize": 3.5,
        "lines.solid_capstyle": "round",

        "legend.frameon": False,
        "legend.handlelength": 1.6,
        "legend.columnspacing": 1.2,
        "legend.borderaxespad": 0.3,

        # Vector output must stay editable: keep text as text, never as paths.
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "pdf.compression": 6,

        "axes.prop_cycle": mpl.cycler(color=list(OKABE_ITO_CYCLE)),
    })


# --------------------------------------------------------------------------
# Colour
# --------------------------------------------------------------------------

#: Okabe & Ito (2008) qualitative set — the reference palette for colour-vision
#: deficiency. Distinguishable under deuteranopia, protanopia and tritanopia.
OKABE_ITO = {
    "black":      "#000000",
    "orange":     "#E69F00",
    "sky":        "#56B4E9",
    "green":      "#009E73",
    "yellow":     "#F0E442",
    "blue":       "#0072B2",
    "vermillion": "#D55E00",
    "purple":     "#CC79A7",
}

OKABE_ITO_CYCLE = (
    "#0072B2", "#D55E00", "#009E73", "#CC79A7",
    "#E69F00", "#56B4E9", "#000000", "#F0E442",
)


def palette(n: int, kind: str = "qualitative") -> list[str]:
    """Return `n` colours that survive greyscale printing and CVD.

    Refuses to hand back more than 8 qualitative colours. Beyond that, readers
    cannot match swatch to line reliably — the right fix is to facet, to direct-
    label, or to grey out everything except the two or three series that carry
    the message.
    """
    if kind == "qualitative":
        if n > 8:
            raise SciVizError(
                f"{n} qualitative colours is past the point of legibility. "
                "Facet into small multiples, direct-label the series, or grey out "
                "the context and colour only what the message needs."
            )
        return list(OKABE_ITO_CYCLE[:n])
    if kind == "sequential":
        return [mpl.colormaps["viridis"](i / max(n - 1, 1)) for i in range(n)]
    if kind == "diverging":
        return [mpl.colormaps["RdBu_r"](i / max(n - 1, 1)) for i in range(n)]
    raise SciVizError(f"Unknown palette kind {kind!r}.")


def sequential(name: str = "viridis"):
    """Perceptually uniform sequential maps. Never `jet`, `rainbow` or `hsv`:
    they invent banding that readers mistake for structure in the data."""
    allowed = {"viridis", "cividis", "magma", "inferno", "plasma", "mako", "rocket",
               "Blues", "Greens", "Oranges", "Purples", "Greys", "YlGnBu", "YlOrBr"}
    if name not in allowed:
        raise SciVizError(f"{name!r} is not a perceptually uniform sequential map. Use one of {sorted(allowed)}.")
    return mpl.colormaps[name]


def diverging(name: str = "RdBu_r", vcenter: float = 0.0):
    """Diverging maps require a meaningful zero. Returns (cmap, TwoSlopeNorm-ready centre)."""
    allowed = {"RdBu_r", "RdBu", "BrBG", "PuOr", "PiYG", "coolwarm", "vlag"}
    if name not in allowed:
        raise SciVizError(f"{name!r} is not an accepted diverging map. Use one of {sorted(allowed)}.")
    return mpl.colormaps[name], vcenter


# --------------------------------------------------------------------------
# Figure construction
# --------------------------------------------------------------------------

def new_figure(width="single", height_mm: float | None = None, aspect: float = 0.62, **kw):
    """Create a correctly sized figure with constrained layout enabled.

    `aspect` is height/width; 0.62 (golden-ish) reads well for a single panel.
    Give `height_mm` explicitly when panels must align across figures.
    """
    w_mm = _resolve_width(width)
    h_mm = height_mm if height_mm is not None else w_mm * aspect
    fig, ax = plt.subplots(
        figsize=(w_mm * MM, h_mm * MM),
        layout="constrained",
        **kw,
    )
    fig.get_layout_engine().set(w_pad=1.5 * MM, h_pad=1.5 * MM, hspace=0.02, wspace=0.02)
    return fig, ax


def new_panel_grid(nrows: int, ncols: int, width="double", panel_h_mm: float = 40.0,
                   sharex: bool = True, sharey: bool = True, **kw):
    """Small multiples. Shared axes by default — that is the point of the form:
    panels are only comparable if the scale is identical, so opting out should be
    a conscious act, not the default."""
    w_mm = _resolve_width(width)
    fig, axes = plt.subplots(
        nrows, ncols,
        figsize=(w_mm * MM, (panel_h_mm * nrows + 12) * MM),
        layout="constrained",
        sharex=sharex, sharey=sharey,
        **kw,
    )
    fig.get_layout_engine().set(w_pad=1.5 * MM, h_pad=1.5 * MM, hspace=0.04, wspace=0.04)
    return fig, axes


# --------------------------------------------------------------------------
# Layout verification — the part that catches what humans catch by squinting
# --------------------------------------------------------------------------

@dataclass
class LayoutReport:
    overlaps: list[tuple[str, str]] = field(default_factory=list)
    small_text: list[tuple[str, float]] = field(default_factory=list)
    clipped: list[str] = field(default_factory=list)
    size_mm: tuple[float, float] = (0.0, 0.0)

    @property
    def ok(self) -> bool:
        return not (self.overlaps or self.small_text or self.clipped)

    def as_dict(self) -> dict:
        return {
            "size_mm": [round(self.size_mm[0], 1), round(self.size_mm[1], 1)],
            "overlapping_text_pairs": [list(p) for p in self.overlaps],
            "text_below_font_floor": [[t, round(s, 2)] for t, s in self.small_text],
            "text_outside_canvas": self.clipped,
            "passed": self.ok,
        }


def _visible_texts(fig: Figure) -> list[Text]:
    out = []
    for t in fig.findobj(Text):
        if not t.get_visible():
            continue
        s = t.get_text().strip()
        if not s:
            continue
        out.append(t)
    return out


def _overlap_area(a, b) -> float:
    dx = min(a.x1, b.x1) - max(a.x0, b.x0)
    dy = min(a.y1, b.y1) - max(a.y0, b.y0)
    return dx * dy if (dx > 0 and dy > 0) else 0.0


def check_layout(fig: Figure, min_font_pt: float = MIN_FONT_PT,
                 tolerance: float = 0.12) -> LayoutReport:
    """Measure every rendered Text against the real renderer.

    This is what a human does when they open the PNG and squint — done
    numerically, so it happens every time instead of when someone remembers.
    `tolerance` is the fraction of the smaller box that may overlap before it
    counts as a collision (kerning-level touching is not a defect).

    **Known limitation, and the reason the visual step is not optional:** this
    compares text against text. It does not see a label sitting on top of data
    marks, a legend covering a line, or an annotation landing inside a dense
    cloud of points. Those are only caught by opening the render and looking at
    it. When an annotation has to live near the data, reserve space for it by
    extending the axis limit rather than trusting it to land in a gap.
    """
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    texts = _visible_texts(fig)

    report = LayoutReport()
    w_in, h_in = fig.get_size_inches()
    report.size_mm = (w_in / MM, h_in / MM)
    canvas = fig.bbox

    boxes = []
    for t in texts:
        try:
            bb = t.get_window_extent(renderer=renderer)
        except Exception:
            continue
        if bb.width <= 0 or bb.height <= 0:
            continue
        label = t.get_text().strip()

        # Matplotlib keeps tick-label artists for ticks that fall outside the
        # current view. They never render, so they are not defects — skip them.
        fully_outside = (bb.x1 < canvas.x0 or bb.x0 > canvas.x1
                         or bb.y1 < canvas.y0 or bb.y0 > canvas.y1)
        if fully_outside:
            continue

        boxes.append((label, bb, t))

        size_pt = t.get_fontsize()
        if size_pt < min_font_pt - 1e-9:
            report.small_text.append((label[:40], size_pt))

        # Partially outside means genuinely cut off at the edge of the canvas.
        if (bb.x0 < canvas.x0 - 1 or bb.x1 > canvas.x1 + 1
                or bb.y0 < canvas.y0 - 1 or bb.y1 > canvas.y1 + 1):
            report.clipped.append(label[:40])

    for i in range(len(boxes)):
        li, bi, ti = boxes[i]
        for j in range(i + 1, len(boxes)):
            lj, bj, tj = boxes[j]
            # Texts inside the same legend or the same annotation are laid out
            # together on purpose; only flag cross-artist collisions.
            if ti.get_figure() is not tj.get_figure():
                continue
            area = _overlap_area(bi, bj)
            if area <= 0:
                continue
            smaller = min(bi.width * bi.height, bj.width * bj.height)
            if smaller > 0 and area / smaller > tolerance:
                report.overlaps.append((li[:30], lj[:30]))

    return report


# --------------------------------------------------------------------------
# Annotations that carry scientific obligations
# --------------------------------------------------------------------------

def declare_n(ax, n, where: str = "upper right", prefix: str = "n = ", **kw):
    """State the sample size on the figure itself.

    A reader should never have to hunt the caption to learn how many
    observations a bar rests on. When groups differ, pass a dict and it is
    written per group.
    """
    if isinstance(n, dict):
        txt = "  ".join(f"{k}: {prefix}{v}" for k, v in n.items())
    else:
        txt = f"{prefix}{n}"
    loc = {"upper right": (0.98, 0.98, "right", "top"),
           "upper left": (0.02, 0.98, "left", "top"),
           "lower right": (0.98, 0.02, "right", "bottom"),
           "lower left": (0.02, 0.02, "left", "bottom")}[where]
    x, y, ha, va = loc
    return ax.text(x, y, txt, transform=ax.transAxes, ha=ha, va=va,
                   fontsize=pt(0.85), color="#444444", **kw)


def add_scalebar(ax, length_m: float, label: str | None = None,
                 location=(0.06, 0.06), height_frac: float = 0.012,
                 color: str = "black", segments: int = 2, fontsize: float | None = None):
    """Draw a graphic (bar) scale in projected map units.

    Only a graphic scale survives reproduction. A printed "1:50 000" becomes a
    lie the moment the page is resized for a poster, a slide or a two-column
    reflow; a bar rescales with the image. Requires `ax` to be in a projected
    CRS whose units are metres — a bar over degrees is meaningless.
    """
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    span_x, span_y = x1 - x0, y1 - y0
    bx = x0 + location[0] * span_x
    by = y0 + location[1] * span_y
    seg = length_m / segments
    h = height_frac * span_y
    fs = fontsize or pt(0.8)

    for k in range(segments):
        ax.add_patch(mpl.patches.Rectangle(
            (bx + k * seg, by), seg, h,
            facecolor=color if k % 2 == 0 else "white",
            edgecolor=color, linewidth=0.5, zorder=50, clip_on=False))

    if label is None:
        label = f"{length_m / 1000:g} km" if length_m >= 1000 else f"{length_m:g} m"
    for k in range(segments + 1):
        v = k * seg
        s = f"{v / 1000:g}" if length_m >= 1000 else f"{v:g}"
        ax.text(bx + v, by + h * 1.4, s, ha="center", va="bottom",
                fontsize=fs, zorder=51)
    ax.text(bx + length_m + span_x * 0.012, by + h * 0.5, label,
            ha="left", va="center", fontsize=fs, zorder=51)
    return ax


def add_north_arrow(ax, location=(0.94, 0.90), size_frac: float = 0.055,
                    color: str = "black", fontsize: float | None = None):
    """A plain north arrow. Ornamental compass roses steal ink from the map."""
    fs = fontsize or pt(0.9)
    ax.annotate(
        "N",
        xy=location, xytext=(location[0], location[1] - size_frac),
        xycoords="axes fraction", textcoords="axes fraction",
        ha="center", va="center", fontsize=fs, fontweight="bold", color=color,
        arrowprops=dict(arrowstyle="-|>", color=color, linewidth=0.9,
                        shrinkA=0, shrinkB=0),
        zorder=60,
    )
    return ax


def add_locator_inset(fig, parent_ax, rect=(0.70, 0.02, 0.28, 0.28)):
    """Add an empty locator axes positioned relative to `parent_ax`.

    Plot the country/region outline and an extent marker into the returned axes.
    A reader outside your region cannot place the study area without it.
    """
    bb = parent_ax.get_position()
    ax = fig.add_axes([
        bb.x0 + rect[0] * bb.width,
        bb.y0 + rect[1] * bb.height,
        rect[2] * bb.width,
        rect[3] * bb.height,
    ])
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_linewidth(0.5)
    ax.set_facecolor("white")
    return ax


# --------------------------------------------------------------------------
# Tables
# --------------------------------------------------------------------------

def booktabs_latex(df, caption: str, label: str, units: dict[str, str] | None = None,
                   decimals: dict[str, int] | None = None, notes: Sequence[str] = ()) -> str:
    """Render a DataFrame as a booktabs table: three rules, no vertical lines.

    Units belong in the column header, not repeated in every cell — repeating
    them costs the reader a re-read on every row. Significant figures are fixed
    per column so the table does not advertise precision the measurement never had.
    """
    units = units or {}
    decimals = decimals or {}
    cols = list(df.columns)

    def tex_safe(s: str) -> str:
        """Unicode superscripts break plain pdflatex; emit real maths instead."""
        sup = {"⁻": "-", "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4",
               "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9"}
        return re.sub(
            r"[⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+",
            lambda m: "$^{" + "".join(sup[c] for c in m.group(0)) + "}$",
            str(s),
        )

    aligns = "".join(
        "S" if str(df[c].dtype).startswith(("int", "float")) else "l" for c in cols
    ).replace("S", "r")  # plain LaTeX fallback; use siunitx S column if available

    header = " & ".join(
        tex_safe(f"{c}" + (f" ({units[c]})" if c in units else "")) for c in cols
    )

    rows = []
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if c in decimals and isinstance(v, (int, float)) and not isinstance(v, bool):
                cells.append(f"{v:.{decimals[c]}f}")
            else:
                cells.append(str(v))
        rows.append(" & ".join(cells) + r" \\")

    note_block = ""
    if notes:
        items = r" \\ ".join(tex_safe(n) for n in notes)
        note_block = "\n" + r"\multicolumn{%d}{l}{\footnotesize %s}\\" % (len(cols), items)

    return "\n".join([
        r"\begin{table}[htbp]",
        r"\centering",
        rf"\caption{{{caption}}}",
        rf"\label{{{label}}}",
        rf"\begin{{tabular}}{{{aligns}}}",
        r"\toprule",
        header + r" \\",
        r"\midrule",
        *rows,
        r"\bottomrule" + note_block,
        r"\end{tabular}",
        r"\end{table}",
    ])


# --------------------------------------------------------------------------
# Export + provenance
# --------------------------------------------------------------------------

def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _detect_embedded_prose(fig: Figure) -> list[str]:
    """Find title/caption/source prose baked into the canvas.

    The image should carry the graphic and the labels the graphic needs to be
    read — axis labels, tick labels, legend entries, panel letters, units, n.
    The title, the interpretive note and the source line are manuscript text:
    the journal typesets them, the copy-editor corrects them, and a translator
    translates them. Burned into a PNG they can do none of that, and they get
    duplicated when the typesetter adds the real caption underneath.
    """
    found = []
    if getattr(fig, "_suptitle", None) is not None and fig._suptitle.get_text().strip():
        found.append(f"suptitle: {fig._suptitle.get_text().strip()[:60]}")
    for attr in ("_supxlabel", "_supylabel"):
        art = getattr(fig, attr, None)
        if art is not None and art.get_text().strip():
            found.append(f"{attr[1:]}: {art.get_text().strip()[:60]}")
    for t in _visible_texts(fig):
        s = t.get_text().strip()
        # Long sentences and provenance keywords are prose, not labels.
        if len(s) > 90 or re.search(
                r"\b(fuente|source|elaboraci[oó]n propia|nota|note:|accessed|"
                r"consulta|acceso:|no demuestra|does not (prove|show))\b", s, re.I):
            found.append(f"text: {s[:60]}")
    return found


def finalize(fig: Figure, outdir, stem: str, *, contract: str, source,
             caption: str | None = None, note: str | None = None,
             source_note: str | None = None, lang: str = "es",
             formats: Iterable[str] = ("pdf", "svg", "png"),
             png_dpi: int = 600, min_font_pt: float = MIN_FONT_PT,
             embed_prose: bool = False, strict: bool = True,
             extra: dict | None = None) -> dict:
    """Verify, export in every required format, and write the sidecars.

    Three sidecars are written next to the figure:

      <stem>.manifest.json  provenance — contract id, source paths and their
                            SHA-256, physical size, layout-check result
      <stem>.caption.md     the text block to paste into the manuscript:
                            caption, interpretive note, source
      <stem>.caption.txt    the same as plain text

    `caption`, `note` and `source_note` are *not* drawn on the canvas. By
    default `embed_prose=False` and `finalize` refuses to export if it finds a
    figure title, a source line or a full sentence inside the image, because
    that text belongs to the document, not to the graphic. Set
    `embed_prose=True` only for a standalone sheet that will be read outside a
    document — a poster panel, an annex map, a slide.

    `lang` records the language of the text drawn in the figure, so a document
    never mixes a Spanish axis with an English caption.

    Set `strict=False` only to inspect a work in progress; never for a
    deliverable.
    """
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    if not embed_prose:
        prose = _detect_embedded_prose(fig)
        if prose:
            msg = ("Prose found inside the image: " + "; ".join(prose[:5]) +
                   "\nTitles, notes and source lines belong in the manuscript, not on "
                   "the canvas — pass them as caption=/note=/source_note= and they will "
                   "be written to <stem>.caption.md for you to paste into the document. "
                   "Keep on the canvas only what the graphic needs to be read: axis "
                   "labels with units, tick labels, legend entries, panel letters, n. "
                   "If this really is a standalone sheet, pass embed_prose=True.")
            if strict:
                raise SciVizError(msg)
            warnings.warn(msg)

    report = check_layout(fig, min_font_pt=min_font_pt)
    if not report.ok:
        msg_parts = []
        if report.overlaps:
            msg_parts.append("overlapping text: " + "; ".join(f"{a!r}~{b!r}" for a, b in report.overlaps[:6]))
        if report.small_text:
            msg_parts.append("text below %.1f pt: %s" % (min_font_pt, report.small_text[:6]))
        if report.clipped:
            msg_parts.append("text outside canvas: " + ", ".join(report.clipped[:6]))
        msg = ("Layout check failed — " + " | ".join(msg_parts) +
               "\nFix the layout rather than shrinking the text: enlarge the figure, "
               "rotate or shorten labels, direct-label instead of using a legend, "
               "or split into panels.")
        if strict:
            raise SciVizError(msg)
        warnings.warn(msg)

    sources = [source] if isinstance(source, (str, Path)) else list(source)
    src_records = []
    for s in sources:
        p = Path(s)
        rec = {"path": str(s)}
        if p.exists() and p.is_file():
            rec["sha256"] = _sha256(p)
            rec["bytes"] = p.stat().st_size
        else:
            rec["sha256"] = None
            rec["warning"] = "source path not resolvable from this working directory"
        src_records.append(rec)

    written = {}
    for fmt in formats:
        path = outdir / f"{stem}.{fmt}"
        kw = {"dpi": png_dpi} if fmt in ("png", "tif", "tiff", "jpg") else {}
        fig.savefig(path, format=fmt, **kw)
        written[fmt] = {"path": str(path), "sha256": _sha256(path)}

    # ---- caption block for the manuscript -------------------------------
    label = {"es": ("Figura", "Nota", "Fuente"),
             "en": ("Figure", "Note", "Source")}.get(lang, ("Figure", "Note", "Source"))
    lines = []
    if caption:
        lines.append(f"**{label[0]} N.** {caption.strip()}")
    if note:
        lines.append(f"*{label[1]}:* {note.strip()}")
    if source_note:
        lines.append(f"*{label[2]}:* {source_note.strip()}")
    if not lines:
        lines.append(
            f"<!-- {label[0]} N. Sin caption. Pasa caption=, note= y source_note= "
            f"a finalize(): el pie es parte del producto, no un añadido. -->")
    caption_md = "\n\n".join(lines) + "\n"
    (outdir / f"{stem}.caption.md").write_text(caption_md, encoding="utf-8")
    (outdir / f"{stem}.caption.txt").write_text(
        re.sub(r"[*_]", "", caption_md), encoding="utf-8")

    manifest = {
        "contract": contract,
        "stem": stem,
        "generated": date.today().isoformat(),
        "lang": lang,
        "figure_size_mm": [round(report.size_mm[0], 1), round(report.size_mm[1], 1)],
        "png_dpi": png_dpi,
        "layout_check": report.as_dict(),
        "prose_embedded_in_image": bool(embed_prose),
        "sources": src_records,
        "caption": caption,
        "note": note,
        "source_note": source_note,
        "outputs": written,
        "matplotlib": mpl.__version__,
    }
    if extra:
        manifest.update(extra)

    (outdir / f"{stem}.manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    return manifest
