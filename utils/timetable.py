"""
utils/timetable.py
------------------
Convert a chromosome (list of genes) into things the UI can show:

  * chromosome_to_dataframe()  -> plain Pandas Day x Period table (one class)
  * class_grid_html()          -> coloured timetable grid for ONE class
  * teacher_grid_html()        -> coloured timetable grid for ONE teacher
  * chromosome_to_long_dataframe() -> one row per lecture (for CSV download)
"""

import html
import pandas as pd

# Soft pastel background + stronger accent colour, one pair per subject
PALETTE = [
    ("#E0E7FF", "#6366F1"), ("#FCE7F3", "#EC4899"), ("#DCFCE7", "#22C55E"),
    ("#FEF3C7", "#F59E0B"), ("#E0F2FE", "#0EA5E9"), ("#F3E8FF", "#A855F7"),
    ("#FFE4E6", "#F43F5E"), ("#CCFBF1", "#14B8A6"), ("#FFEDD5", "#F97316"),
    ("#ECFCCB", "#84CC16"),
]


def subject_colors(problem):
    """{subject or activity name: (background, accent)} - same colour everywhere."""
    names = [s["name"] for s in problem["subjects"]] + list(problem.get("activities", []))
    return {name: PALETTE[i % len(PALETTE)] for i, name in enumerate(names)}


def _esc(text):
    return html.escape(str(text))


# ----------------------------------------------------------------------
# Plain tables
# ----------------------------------------------------------------------
def chromosome_to_dataframe(chromosome, problem, class_name):
    """Build a Day x Period table for ONE class. Cell = Subject (Teacher, Room)."""
    days = problem["days"]
    num_periods = problem["num_periods"]

    slots = {}
    for gene in chromosome:
        if gene["class"] == class_name:
            if gene.get("activity"):
                text = f"{gene['subject']} (Activity)"
            else:
                text = f"{gene['subject']} ({gene['teacher']}, {gene['room']})"
            slots.setdefault((gene["day"], gene["period"]), []).append(text)

    rows = []
    for d in range(len(days)):
        row = []
        for p in range(num_periods):
            items = slots.get((d, p))
            if not items:
                row.append("Free")
            elif len(items) == 1:
                row.append(items[0])
            else:                                   # clash: two lectures in one slot
                row.append("⚠ " + " / ".join(items))
        rows.append(row)

    table = pd.DataFrame(rows, index=days,
                         columns=[f"Period {i + 1}" for i in range(num_periods)])
    table.index.name = "Day"
    return table


def chromosome_to_long_dataframe(chromosome, problem):
    """One row per lecture, sorted by class / day / period. Used for CSV export."""
    rows = []
    for g in chromosome:
        rows.append({
            "Class": g["class"],
            "Day": problem["days"][g["day"]],
            "Period": g["period"] + 1,
            "Subject": g["subject"],
            "Teacher": g["teacher"] or "-",
            "Room": g["room"],
        })
    df = pd.DataFrame(rows)
    day_order = {d: i for i, d in enumerate(problem["days"])}
    df["_d"] = df["Day"].map(day_order)
    return df.sort_values(["Class", "_d", "Period"]).drop(columns="_d").reset_index(drop=True)


# ----------------------------------------------------------------------
# HTML grids (rendered with st.markdown(..., unsafe_allow_html=True))
# NOTE: built as ONE line without indentation, otherwise Markdown would turn
# indented lines into code blocks.
# ----------------------------------------------------------------------
def _grid(problem, cell_function):
    parts = ['<div class="tt-wrap"><table class="tt"><thead><tr><th class="tt-corner">Day</th>']
    for p in range(problem["num_periods"]):
        parts.append(f"<th>Period {p + 1}</th>")
    parts.append("</tr></thead><tbody>")
    for d, day in enumerate(problem["days"]):
        parts.append(f'<tr><th class="tt-day">{_esc(day)}</th>')
        for p in range(problem["num_periods"]):
            parts.append(f"<td>{cell_function(d, p)}</td>")
        parts.append("</tr>")
    parts.append("</tbody></table></div>")
    return "".join(parts)


def _lecture_card(gene, colors, line2, flagged, show_clash_tag=True):
    bg, accent = colors.get(gene["subject"], ("#EEE", "#999"))
    cls = "tt-cell tt-flag" if flagged else "tt-cell"
    tag = '<span class="tt-warn">⚠ clash</span>' if (flagged and show_clash_tag) else ""
    return (f'<div class="{cls}" style="background:{bg};border-left:4px solid {accent}">'
            f'<b>{_esc(gene["subject"])}</b>{tag}{line2}</div>')


def class_grid_html(chromosome, problem, class_name, colors, flagged=None):
    """Coloured Day x Period grid for one class. `flagged` = set of clashing gene indexes."""
    flagged = flagged or set()
    slots = {}
    for index, gene in enumerate(chromosome):
        if gene["class"] == class_name:
            slots.setdefault((gene["day"], gene["period"]), []).append((index, gene))

    def cell(d, p):
        items = slots.get((d, p))
        if not items:
            return '<div class="tt-cell tt-free">Free period</div>'
        out = []
        for index, gene in items:
            if gene.get("activity"):
                line2 = '<span class="tt-sub">Activity period</span>'
            else:
                line2 = (f'<span class="tt-sub">{_esc(gene["teacher"])}</span>'
                         f'<span class="tt-room">{_esc(gene["room"])}</span>')
            out.append(_lecture_card(gene, colors, line2, index in flagged or len(items) > 1))
        return "".join(out)

    return _grid(problem, cell)


def teacher_grid_html(chromosome, problem, teacher, colors, flagged=None):
    """Coloured Day x Period grid for one teacher (a teacher may have real free time)."""
    flagged = flagged or set()
    slots = {}
    for index, gene in enumerate(chromosome):
        if gene["teacher"] == teacher and not gene.get("activity"):
            slots.setdefault((gene["day"], gene["period"]), []).append((index, gene))

    def cell(d, p):
        items = slots.get((d, p))
        if not items:
            return '<div class="tt-cell tt-empty">-</div>'
        out = []
        for index, gene in items:
            line2 = (f'<span class="tt-sub">Class {_esc(gene["class"])}</span>'
                     f'<span class="tt-room">{_esc(gene["room"])}</span>')
            out.append(_lecture_card(gene, colors, line2, index in flagged or len(items) > 1))
        return "".join(out)

    return _grid(problem, cell)


def style_timetable(table, subject_names):
    """(kept for compatibility) Colour a Pandas timetable by subject."""
    colors = {name: PALETTE[i % len(PALETTE)][0] for i, name in enumerate(subject_names)}

    def color_cell(value):
        if value == "Free":
            return "color: #9aa0a6; background-color: #f7f7f7"
        if value.startswith("⚠"):
            return "background-color: #ffb3b3; color: #1f2937"
        for name, color in colors.items():
            if value.startswith(name + " ("):
                return f"background-color: {color}; color: #1f2937"
        return ""

    styler = table.style
    return styler.map(color_cell) if hasattr(styler, "map") else styler.applymap(color_cell)
