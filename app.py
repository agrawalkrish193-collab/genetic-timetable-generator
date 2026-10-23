"""
app.py
------
Modern Streamlit front-end for:
    AI-Based College Timetable Generator Using Genetic Algorithm

NO FREE PERIOD: every class gets a lecture in every period of every day.

Run with:   python -m streamlit run app.py

Layout
    Sidebar : evolution settings + the big "Generate" button
    Tab 1   : Setup      (your data + live pre-flight checks)
    Tab 2   : Timetable  (coloured grids by class / by teacher + download)
    Tab 3   : Insights   (fitness graphs, penalty breakdown, before/after)
"""

import time

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from data.sample_data import ALL_DAYS, get_sample_problem
from ga.genetic_algorithm import run_genetic_algorithm
from ga.fitness import (PENALTY_WEIGHTS, HARD_RULES, RULE_NAMES, count_violations,
                        count_hard_conflicts, count_satisfied_constraints,
                        describe_conflicts, get_unavailable_set)
from ga.mutation import find_conflicting_genes
from utils.timetable import (subject_colors, class_grid_html, teacher_grid_html,
                             chromosome_to_long_dataframe)

st.set_page_config(page_title="GA Timetable Generator", page_icon="🧬", layout="wide")

sample = get_sample_problem()

# ======================================================================
# STYLE  (all the "modern look" lives here)
# ======================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], .stMarkdown, button, input, textarea { font-family: 'Inter', sans-serif; }
.block-container { padding-top: 3.6rem; max-width: 1250px; }
footer, #MainMenu { visibility: hidden; }

/* ---------- hero ---------- */
.hero { background: linear-gradient(120deg, #4f46e5 0%, #7c3aed 55%, #db2777 100%);
        border-radius: 20px; padding: 28px 34px; color: #fff; margin-bottom: 18px;
        box-shadow: 0 10px 30px rgba(99,102,241,.28); }
.hero h1 { color: #fff; font-size: 2rem; font-weight: 800; margin: 6px 0 6px 0; padding: 0; letter-spacing: -.5px; }
.hero p  { color: rgba(255,255,255,.92); margin: 0; font-size: 1.02rem; max-width: 820px; line-height: 1.55; }
.hero-badge { display: inline-block; background: rgba(255,255,255,.18); border-radius: 999px;
              padding: 4px 12px; font-size: .78rem; font-weight: 600; letter-spacing: .3px; }
.chips { margin-top: 16px; display: flex; gap: 10px; flex-wrap: wrap; }
.chip  { background: rgba(255,255,255,.16); border: 1px solid rgba(255,255,255,.28);
         border-radius: 12px; padding: 7px 13px; font-size: .84rem; }
.chip b { font-weight: 700; }

/* ---------- section headings ---------- */
.section-title { font-size: 1.12rem; font-weight: 700; margin: 8px 0 2px 0; }
.section-sub   { opacity: .7; font-size: .9rem; margin-bottom: 10px; }

/* ---------- status banners ---------- */
.banner { border-radius: 14px; padding: 14px 18px; margin: 6px 0 14px 0; display: flex; gap: 12px;
          align-items: flex-start; border: 1px solid; line-height: 1.45; }
.banner .ico { font-size: 1.4rem; line-height: 1.2; }
.banner b { font-weight: 700; }
.banner.ok   { background: rgba(34,197,94,.12);  border-color: rgba(34,197,94,.45); }
.banner.warn { background: rgba(245,158,11,.13); border-color: rgba(245,158,11,.5); }
.banner.bad  { background: rgba(239,68,68,.12);  border-color: rgba(239,68,68,.5); }
.banner.info { background: rgba(99,102,241,.11); border-color: rgba(99,102,241,.4); }
.banner ul { margin: 6px 0 0 18px; padding: 0; }

/* ---------- KPI cards ---------- */
.kpi-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(135px, 1fr)); gap: 12px; margin: 6px 0 16px 0; }
.kpi { background: var(--secondary-background-color, #f6f7fb); border: 1px solid rgba(128,128,128,.18);
       border-radius: 16px; padding: 14px 16px; }
.kpi-label { font-size: .74rem; text-transform: uppercase; letter-spacing: .6px; opacity: .65; font-weight: 600; }
.kpi-value { font-size: 1.65rem; font-weight: 800; margin-top: 2px; }
.kpi-sub   { font-size: .8rem; opacity: .7; }
.kpi.good .kpi-value { color: #16a34a; }
.kpi.bad  .kpi-value { color: #dc2626; }

/* ---------- timetable grid ---------- */
.tt-wrap { overflow-x: auto; border-radius: 16px; border: 1px solid rgba(128,128,128,.2); margin: 8px 0 12px 0; }
table.tt { border-collapse: separate; border-spacing: 6px; width: 100%; min-width: 760px; }
table.tt th { font-size: .78rem; text-transform: uppercase; letter-spacing: .5px; opacity: .75; font-weight: 700;
              padding: 8px 4px; text-align: center; background: transparent !important; border: none !important; }
table.tt th.tt-day { text-align: left; padding-left: 10px; white-space: nowrap; opacity: 1; font-size: .86rem;
                     text-transform: none; letter-spacing: 0; }
table.tt td { padding: 0 !important; vertical-align: top; border: none !important; background: transparent !important; }
.tt-cell { border-radius: 10px; padding: 9px 10px; min-height: 66px; color: #1f2937; display: flex;
           flex-direction: column; gap: 2px; font-size: .84rem; box-shadow: 0 1px 2px rgba(0,0,0,.06);
           margin-bottom: 3px; }
.tt-cell b { font-size: .92rem; font-weight: 700; }
.tt-sub  { font-size: .76rem; opacity: .85; }
.tt-room { font-size: .7rem; font-weight: 700; background: rgba(255,255,255,.7); border-radius: 6px;
           padding: 1px 7px; align-self: flex-start; margin-top: 2px; }
.tt-free  { background: #fee2e2 !important; color: #b91c1c; border: 2px dashed #ef4444; align-items: center;
            justify-content: center; font-weight: 700; }
.tt-empty { background: rgba(128,128,128,.10) !important; color: #9ca3af; align-items: center;
            justify-content: center; box-shadow: none; }
.tt-flag  { outline: 2px solid #ef4444; }
.tt-warn  { font-size: .68rem; font-weight: 700; color: #b91c1c; }
.legend { display: flex; gap: 8px; flex-wrap: wrap; margin: 4px 0 4px 0; }
.legend span { border-radius: 999px; padding: 4px 12px; font-size: .78rem; font-weight: 600; color: #1f2937; }

/* ---------- inputs & buttons ---------- */
.stButton > button { width: 100%; border-radius: 12px; font-weight: 700; padding: .65rem 1rem; }
.stButton > button[kind="primary"] { background: linear-gradient(120deg, #4f46e5, #7c3aed); border: none;
                                     box-shadow: 0 6px 18px rgba(99,102,241,.35); }
.stDownloadButton > button { border-radius: 12px; font-weight: 600; }
.stTabs [data-baseweb="tab-list"] { gap: 6px; }
.stTabs [data-baseweb="tab"] { border-radius: 10px 10px 0 0; padding: 10px 18px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


# ======================================================================
# Full-width buttons (works on old and new Streamlit versions)
# ======================================================================
def wide(widget, *args, **kwargs):
    """Call st.button / st.download_button stretched to the full column width."""
    try:
        return widget(*args, width="stretch", **kwargs)              # Streamlit >= 1.50
    except TypeError:
        return widget(*args, use_container_width=True, **kwargs)     # older versions


def scroll_to_top():
    """Smoothly scroll the page back to the top (used after clicking Generate)."""
    # The time stamp makes the script different on every run, so it always re-executes.
    components.html(
        f"""<script>/* {time.time()} */
        const doc = window.parent.document;
        const targets = [doc.querySelector('[data-testid="stMain"]'),
                         doc.querySelector('section.main'),
                         doc.querySelector('.main'),
                         doc.scrollingElement];
        targets.forEach(t => {{ if (t) t.scrollTo({{top: 0, behavior: 'smooth'}}); }});
        </script>""",
        height=0)


# ======================================================================
# Small HTML helpers
# ======================================================================
def banner(kind, icon, title, body="", items=None):
    """kind = ok | warn | bad | info"""
    lis = ""
    if items:
        lis = "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"
    st.markdown(f'<div class="banner {kind}"><div class="ico">{icon}</div>'
                f'<div><b>{title}</b>{"<br>" + body if body else ""}{lis}</div></div>',
                unsafe_allow_html=True)


def kpi_row(cards):
    """cards = [(label, value, sub, tone)]"""
    html = "".join(f'<div class="kpi {tone}"><div class="kpi-label">{label}</div>'
                   f'<div class="kpi-value">{value}</div><div class="kpi-sub">{sub}</div></div>'
                   for label, value, sub, tone in cards)
    st.markdown(f'<div class="kpi-row">{html}</div>', unsafe_allow_html=True)


def section(title, subtitle=""):
    st.markdown(f'<div class="section-title">{title}</div>'
                f'<div class="section-sub">{subtitle}</div>', unsafe_allow_html=True)


def legend(colors):
    chips = "".join(f'<span style="background:{bg};border:1px solid {accent}">{name}</span>'
                    for name, (bg, accent) in colors.items())
    st.markdown(f'<div class="legend">{chips}</div>', unsafe_allow_html=True)


# ======================================================================
# Turn the tables typed by the user into the `problem` dictionary
# ======================================================================
def clean_text(value):
    """Return a stripped string, or '' for empty/NaN cells."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return str(value).strip()


def build_problem(days, num_periods, subjects_df, classes_df, rooms_df, unavail_df, activities):
    """Validate the inputs. Returns (problem, list_of_errors, list_of_warnings)."""
    errors, warnings = [], []

    subjects = []
    for _, row in subjects_df.iterrows():
        name, teacher = clean_text(row["Subject"]), clean_text(row["Teacher"])
        if name and teacher and not pd.isna(row["Lectures per week"]):
            subjects.append({"name": name, "teacher": teacher,
                             "lectures": int(row["Lectures per week"])})

    classes = {}
    for _, row in classes_df.iterrows():
        name = clean_text(row["Class"])
        if name and not pd.isna(row["Strength"]):
            if name in classes:
                errors.append(f"Class name '{name}' is repeated.")
            classes[name] = int(row["Strength"])

    rooms = {}
    for _, row in rooms_df.iterrows():
        name = clean_text(row["Room"])
        if name and not pd.isna(row["Capacity"]):
            if name in rooms:
                errors.append(f"Room name '{name}' is repeated.")
            rooms[name] = int(row["Capacity"])

    unavailable = []
    for _, row in unavail_df.iterrows():
        teacher, day = clean_text(row["Teacher"]), clean_text(row["Day"])
        if teacher and day and not pd.isna(row["Period"]):
            unavailable.append((teacher, day, int(row["Period"])))

    if not subjects:
        errors.append("Add at least one subject (with teacher and lectures).")
    if not classes:
        errors.append("Add at least one class.")
    if not rooms:
        errors.append("Add at least one room.")

    names = [s["name"] for s in subjects]
    if len(names) != len(set(names)):
        errors.append("Subject names must be unique.")
    if activities and set(activities) & set(names):
        errors.append("An activity name is the same as a subject name. Use different names.")

    # ---------- NO FREE PERIOD: lectures must fill every slot ----------
    slots = len(days) * num_periods
    lectures_per_class = sum(s["lectures"] for s in subjects)
    if subjects:
        if lectures_per_class > slots:
            errors.append(f"Each class needs {lectures_per_class} lectures but a week has only "
                          f"{slots} slots. Remove {lectures_per_class - slots} lecture(s).")
        elif lectures_per_class < slots and not activities:
            errors.append(f"Each class has {lectures_per_class} lectures for {slots} slots, which would leave "
                          f"{slots - lectures_per_class} FREE period(s). Add {slots - lectures_per_class} more "
                          f"lecture(s), or switch on 'Fill leftover periods with activities'.")

    # ---------- feasibility checks (so the GA is never asked the impossible) ----------
    if classes and subjects:
        blocked = {}
        for t, d, p in set(unavailable):
            if d in days and 1 <= p <= num_periods:
                blocked[t] = blocked.get(t, 0) + 1
        load = {}
        for s in subjects:
            load[s["teacher"]] = load.get(s["teacher"], 0) + s["lectures"] * len(classes)
        for teacher, total in load.items():
            free_slots = slots - blocked.get(teacher, 0)
            if total > free_slots:
                errors.append(f"{teacher} must teach {total} lectures but is only available in "
                              f"{free_slots} slots - impossible without a clash.")
        if rooms and not activities and len(classes) > len(rooms):
            errors.append(f"{len(classes)} classes are in session at the same time (no free period) "
                          f"but there are only {len(rooms)} rooms.")
        for t, _, _ in unavailable:
            if t not in load:
                warnings.append(f"'{t}' in the availability table does not teach any subject.")
                break

    biggest_room = max(rooms.values()) if rooms else 0
    for class_name, strength in classes.items():
        if strength > biggest_room:
            warnings.append(f"No room is big enough for class {class_name} ({strength} students).")

    problem = {"days": days, "num_periods": num_periods, "classes": classes,
               "subjects": subjects, "rooms": rooms, "teacher_unavailable": unavailable,
               "activities": activities}
    return problem, errors, warnings


# ======================================================================
# SIDEBAR  - evolution settings + generate button
# ======================================================================
PRESETS = {
    "⚡ Fast preview":           {"pop": 60,  "gen": 200,  "text": "Quick check. May leave a clash on tightly packed data."},
    "⚖️ Balanced (recommended)": {"pop": 100, "gen": 500,  "text": "Good speed and quality for most inputs."},
    "🔬 Thorough":               {"pop": 200, "gen": 1000, "text": "Best chance on big or tightly packed inputs."},
    "🎛️ Custom":                 {"pop": 100, "gen": 500,  "text": "Choose the values yourself."},
}

with st.sidebar:
    st.markdown("## 🧬 Evolution settings")
    preset_name = st.selectbox("Quality preset", list(PRESETS.keys()), index=1)
    preset = PRESETS[preset_name]
    st.caption(preset["text"])

    if preset_name.endswith("Custom"):
        population_size = st.slider("Population size", 20, 300, 100, step=10,
                                    help="How many timetables exist in each generation")
        generations = st.slider("Generations", 10, 1000, 500, step=10,
                                help="How many times the population evolves")
    else:
        population_size, generations = preset["pop"], preset["gen"]
        st.markdown(f"**Population** {population_size} &nbsp;·&nbsp; **Generations** {generations}")

    with st.expander("Advanced"):
        elite_count = st.slider("Elitism (best kept unchanged)", 1, 10, 2)
        mutation_rate = st.slider("Mutation rate", 0.0, 0.5, 0.02, step=0.01,
                                  help="Chance that each lecture is randomly changed")
        crossover_rate = st.slider("Crossover rate", 0.0, 1.0, 0.8, step=0.05,
                                   help="Chance that two parents are mixed")
        seed = st.number_input("Random seed (0 = different every time)", 0, 99999, 42)

    st.divider()
    generate_clicked = wide(st.button, "🚀 Generate timetable", type="primary")
    st.caption("Tip: the same seed always gives the same timetable.")

# ======================================================================
# HERO
# ======================================================================
st.markdown("""
<div class="hero">
  <span class="hero-badge">🧬 AISC · Artificial Intelligence &amp; Soft Computing</span>
  <h1>AI College Timetable Generator</h1>
  <p>Enter your classes, subjects, teachers and rooms. A <b>Genetic Algorithm</b> evolves hundreds of
     timetables with selection, crossover and mutation until it finds one with <b>no clashes and no free period</b>.</p>
  <div class="chips">
    <div class="chip"><b>Chromosome</b> · one full timetable</div>
    <div class="chip"><b>Gene</b> · one lecture</div>
    <div class="chip"><b>Fitness</b> · 1 / (1 + penalty)</div>
    <div class="chip"><b>Guarantee</b> · every period filled</div>
  </div>
</div>
""", unsafe_allow_html=True)

progress_slot = st.container()          # progress bar / error messages appear here

tab_setup, tab_table, tab_insights = st.tabs(["📝  Setup", "🗓️  Timetable", "📈  Insights"])

# ======================================================================
# TAB 1 - SETUP
# ======================================================================
with tab_setup:
    section("Timetable size", "How many days and periods does a week have?")
    col_a, col_b = st.columns(2)
    num_days = col_a.slider("Working days", 1, 6, len(sample["days"]))
    num_periods = col_b.slider("Periods per day", 2, 8, sample["num_periods"])
    days = ALL_DAYS[:num_days]

    left, right = st.columns(2, gap="large")
    with left:
        section("👩‍🏫 Subjects & faculty", "Each class studies every subject below. Use + at the bottom to add rows.")
        subjects_df = st.data_editor(
            pd.DataFrame([{"Subject": s["name"], "Teacher": s["teacher"],
                           "Lectures per week": s["lectures"]} for s in sample["subjects"]]),
            num_rows="dynamic", key="subjects_table",
            column_config={"Lectures per week": st.column_config.NumberColumn(min_value=1, max_value=10, step=1)})
        section("🚫 Teacher availability", "Slots where a teacher can NOT teach.")
        unavail_df = st.data_editor(
            pd.DataFrame([{"Teacher": t, "Day": d, "Period": p}
                          for t, d, p in sample["teacher_unavailable"]]),
            num_rows="dynamic", key="unavail_table",
            column_config={"Day": st.column_config.SelectboxColumn(options=ALL_DAYS),
                           "Period": st.column_config.NumberColumn(min_value=1, max_value=8, step=1)})
    with right:
        section("🎓 Classes / sections", "Strength decides which rooms are big enough.")
        classes_df = st.data_editor(
            pd.DataFrame([{"Class": c, "Strength": n} for c, n in sample["classes"].items()]),
            num_rows="dynamic", key="classes_table",
            column_config={"Strength": st.column_config.NumberColumn(min_value=1, step=1)})
        section("🏫 Rooms & capacity", "A lecture needs a room that fits the whole class.")
        rooms_df = st.data_editor(
            pd.DataFrame([{"Room": r, "Capacity": c} for r, c in sample["rooms"].items()]),
            num_rows="dynamic", key="rooms_table",
            column_config={"Capacity": st.column_config.NumberColumn(min_value=1, step=1)})

    section("🧩 Leftover periods", "Only needed when your lectures do not add up to the full week.")
    use_activities = st.toggle("Fill leftover periods with activities (Library, Sports ...)", value=False,
                               help="Activity periods need no teacher and no room. "
                                    "Off = every period must be a real lecture.")
    activities = []
    if use_activities:
        raw = st.text_input("Activity names (comma separated)", "Library, Sports, Self Study, Mentoring")
        activities = [a.strip() for a in raw.split(",") if a.strip()] or ["Activity"]

    # ---------- live pre-flight checks ----------
    problem_draft, errors, warnings = build_problem(days, num_periods, subjects_df, classes_df,
                                                    rooms_df, unavail_df, activities)
    slots = num_days * num_periods
    lectures = sum(s["lectures"] for s in problem_draft["subjects"])

    st.divider()
    section("✅ Pre-flight check", "Is your data ready to become a timetable with no free period?")
    kpi_row([
        ("Slots per class", slots, f"{num_days} days × {num_periods} periods", ""),
        ("Lectures per class", lectures, "from the subjects table",
         "good" if lectures == slots else ("" if activities and lectures < slots else "bad")),
        ("Classes", len(problem_draft["classes"]), "sections", ""),
        ("Rooms", len(problem_draft["rooms"]), "available", ""),
    ])
    if errors:
        banner("bad", "⛔", "Fix these before generating:", items=errors)
    elif lectures == slots:
        banner("ok", "✅", "Perfect fit - no free period",
               f"{lectures} lectures fill all {slots} slots of every class.")
    else:
        banner("info", "🧩", f"{slots - lectures} leftover period(s) per class will be filled with activities",
               ", ".join(activities))
    if warnings:
        banner("warn", "⚠️", "Heads up:", items=warnings)

# ======================================================================
# GENERATE (runs after the Setup tab so it can read the tables above)
# ======================================================================
if generate_clicked:
    with progress_slot:
        scroll_to_top()                       # jump to the top so progress + result are visible
    if errors:
        with progress_slot:
            banner("bad", "⛔", "Cannot generate yet",
                   "Open the <b>Setup</b> tab and fix the problems listed in the pre-flight check.")
    else:
        with progress_slot:
            bar = st.progress(0.0, text="🧬 Evolving timetables...")

            def update_progress(gen, total, best_fitness):
                bar.progress(gen / total, text=f"🧬 Generation {gen}/{total}  ·  best fitness {best_fitness:.4f}")

            result = run_genetic_algorithm(problem_draft, population_size, generations, mutation_rate,
                                           crossover_rate, elite_count, seed=int(seed),
                                           progress_callback=update_progress)
            bar.empty()
        st.session_state["problem"] = problem_draft          # keep results when widgets change
        st.session_state["result"] = result
        st.toast("Timetable ready! Open the 🗓️ Timetable tab.", icon="✅")

# ======================================================================
# RESULTS
# ======================================================================
has_result = "result" in st.session_state

if has_result:
    problem = st.session_state["problem"]
    result = st.session_state["result"]
    best, first = result["best_chromosome"], result["initial_chromosome"]
    colors = subject_colors(problem)
    unavailable_set = get_unavailable_set(problem)
    flagged_best = find_conflicting_genes(best, problem, unavailable_set)
    flagged_first = find_conflicting_genes(first, problem, unavailable_set)

    final_counts = count_violations(best, problem)
    initial_counts = count_violations(first, problem)
    hard_conflicts = count_hard_conflicts(final_counts)
    satisfied, total_checks = count_satisfied_constraints(best, problem)

# ---------------------------------------------------------------- TAB 2
with tab_table:
    if not has_result:
        banner("info", "👋", "No timetable yet",
               "Check your data in the <b>Setup</b> tab, then press <b>🚀 Generate timetable</b> in the sidebar.")
    else:
        if hard_conflicts == 0:
            banner("ok", "✅", "Valid timetable - no clashes and no free period",
                   f"Found in {result['generations_run']} generations. "
                   f"Free periods: <b>{final_counts['free']}</b> · Hard conflicts: <b>0</b>.")
        else:
            banner("warn", "⚠️", f"{hard_conflicts} hard conflict(s) remain",
                   "Pick the 🔬 Thorough preset, raise the generations, or try another seed. "
                   "Clashing lectures are outlined in red below.")

        view = st.radio("View", ["🎓 By class", "👩‍🏫 By teacher"], horizontal=True, label_visibility="collapsed")
        legend(colors)

        if view.endswith("By class"):
            chosen_class = st.radio("Class", list(problem["classes"].keys()), horizontal=True,
                                    label_visibility="collapsed", key="class_pick")
            st.markdown(class_grid_html(best, problem, chosen_class, colors, flagged_best),
                        unsafe_allow_html=True)
            n_lect = sum(1 for g in best if g["class"] == chosen_class)
            st.caption(f"**{chosen_class}** · {problem['classes'][chosen_class]} students · "
                       f"{n_lect} lectures in {len(problem['days']) * problem['num_periods']} slots · "
                       f"{final_counts['free']} free period(s) in the whole timetable")
        else:
            teachers = sorted({s["teacher"] for s in problem["subjects"]})
            chosen_teacher = st.radio("Teacher", teachers, horizontal=True,
                                      label_visibility="collapsed", key="teacher_pick")
            st.markdown(teacher_grid_html(best, problem, chosen_teacher, colors, flagged_best),
                        unsafe_allow_html=True)
            n_lect = sum(1 for g in best if g["teacher"] == chosen_teacher)
            st.caption(f"**{chosen_teacher}** teaches {n_lect} lectures a week. "
                       "Grey cells are the teacher's own free time.")

        long_df = chromosome_to_long_dataframe(best, problem)
        d1, d2, _ = st.columns([1, 1, 2])
        wide(d1.download_button, "⬇️ Download all (CSV)", long_df.to_csv(index=False).encode("utf-8-sig"),
             file_name="timetable_all_classes.csv", mime="text/csv")
        if view.endswith("By class"):
            wide(d2.download_button, f"⬇️ Download {chosen_class} (CSV)",
                 long_df[long_df["Class"] == chosen_class].to_csv(index=False).encode("utf-8-sig"),
                 file_name=f"timetable_{chosen_class}.csv", mime="text/csv")

# ---------------------------------------------------------------- TAB 3
with tab_insights:
    if not has_result:
        banner("info", "📊", "Nothing to analyse yet", "Generate a timetable first.")
    else:
        kpi_row([
            ("Initial fitness", f"{result['initial_fitness']:.4f}", "best random timetable", ""),
            ("Final fitness", f"{result['best_fitness']:.4f}",
             f"{result['best_fitness'] - result['initial_fitness']:+.4f}",
             "good" if result["best_fitness"] == 1 else ""),
            ("Generations run", result["generations_run"], "stops early at penalty 0", ""),
            ("Hard conflicts", hard_conflicts, f"was {count_hard_conflicts(initial_counts)}",
             "good" if hard_conflicts == 0 else "bad"),
            ("Free periods", final_counts["free"], "every period filled",
             "good" if final_counts["free"] == 0 else "bad"),
            ("Constraints met", f"{satisfied}/{total_checks}", "hard-rule checks", ""),
        ])

        section("📈 Generation vs fitness", "Fitness rises and penalty falls as the population evolves.")
        g1, g2 = st.columns(2)
        with g1:
            st.caption("Fitness (higher is better)")
            st.line_chart(pd.DataFrame({"Best fitness": result["best_history"],
                                        "Average fitness": result["avg_history"]}),
                          color=["#6366F1", "#F59E0B"])
        with g2:
            st.caption("Total penalty of the best timetable (lower is better)")
            st.line_chart(pd.DataFrame({"Penalty": result["penalty_history"]}), color=["#EF4444"])

        section("🧮 Penalty breakdown", "Initial random timetable vs the final one.")
        rows = []
        for rule, weight in PENALTY_WEIGHTS.items():
            rows.append({"Rule": RULE_NAMES[rule],
                         "Type": "Hard" if rule in HARD_RULES else "Soft",
                         "Penalty weight": str(weight),
                         "Violations (initial)": initial_counts[rule],
                         "Violations (final)": final_counts[rule]})
        rows.append({"Rule": "TOTAL PENALTY", "Type": "-", "Penalty weight": "-",
                     "Violations (initial)": result["initial_penalty"],
                     "Violations (final)": result["best_penalty"]})
        st.dataframe(pd.DataFrame(rows), hide_index=True)

        section("🔄 Before vs after", "Red outlines mark lectures that clash.")
        chosen = st.radio("Class to compare", list(problem["classes"].keys()), horizontal=True,
                          key="compare_pick")
        cl, cr = st.columns(2)
        with cl:
            st.markdown("**Initial** (best of random generation 0)")
            st.markdown(class_grid_html(first, problem, chosen, colors, flagged_first), unsafe_allow_html=True)
        with cr:
            st.markdown("**Final** (after the Genetic Algorithm)")
            st.markdown(class_grid_html(best, problem, chosen, colors, flagged_best), unsafe_allow_html=True)

        remaining = describe_conflicts(best, problem)
        if remaining:
            with st.expander(f"Remaining conflicts ({len(remaining)})"):
                for message in remaining:
                    st.write("• " + message)

        with st.expander("💡 How is 'no free period' guaranteed?"):
            st.markdown(
                "- Every class gets exactly **days × periods** lectures.\n"
                "- Generation 0 gives each class a **random permutation of its slots**, so no slot is empty "
                "and no two lectures of a class share a slot.\n"
                "- **Crossover** swaps whole class timetables between parents.\n"
                "- **Mutation** only *swaps* two lectures of the same class (or changes a room).\n"
                "- So a free period can never appear. The GA only has to fix teacher and room clashes."
            )
