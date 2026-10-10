import re
import io
import csv
from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ---------------------------------------------------------------------
# SkillMap — a practical, local-first career skills planner
# ---------------------------------------------------------------------

st.set_page_config(
    page_title="SkillMap | Career Skills Planner",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS: restrained typography, clear hierarchy, no emoji decorations.
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {
        --page: #0b1020;
        --panel: #111a2e;
        --panel-soft: #16223a;
        --border: #263550;
        --text: #edf2fb;
        --muted: #9aabc5;
        --accent: #75a7ff;
        --accent-strong: #3979ef;
        --green: #5bd0a0;
        --amber: #f5c26b;
        --red: #f18b92;
    }

    html, body, [class*="css"], .stApp {
        font-family: 'DM Sans', sans-serif;
    }
    .stApp {
        background:
          radial-gradient(ellipse at 85% 0%, rgba(57,121,239,.12), transparent 32%),
          var(--page);
        color: var(--text);
    }
    [data-testid="stHeader"] { background: rgba(11,16,32,.85); }
    [data-testid="stSidebar"] {
        background: #0e1729;
        border-right: 1px solid var(--border);
    }
    [data-testid="stSidebar"] > div:first-child { padding-top: 1.25rem; }
    h1, h2, h3 {
        font-family: 'Manrope', sans-serif !important;
        letter-spacing: -0.035em;
        color: var(--text) !important;
    }
    h1 { font-size: clamp(2rem, 3vw, 2.8rem) !important; font-weight: 800 !important; }
    h2 { font-size: 1.55rem !important; font-weight: 750 !important; }
    h3 { font-size: 1.12rem !important; font-weight: 700 !important; }
    p, label, li { color: #d7e0ef; }
    .muted { color: var(--muted); }
    .brand {
        font-family: 'Manrope', sans-serif;
        font-size: 1.5rem;
        font-weight: 800;
        letter-spacing: -.06em;
        color: var(--text);
        margin-bottom: .15rem;
    }
    .brand-mark {
        display:inline-block; width:9px; height:27px; border-radius:5px;
        background: linear-gradient(180deg, #91bcff, #3979ef);
        margin-right:10px; vertical-align:-5px;
    }
    .eyebrow {
        color: #8db7ff; font-size: .76rem; font-weight: 700;
        letter-spacing: .15em; text-transform: uppercase;
    }
    .hero {
        padding: 1.8rem 1.9rem;
        border: 1px solid var(--border);
        border-radius: 20px;
        background: linear-gradient(115deg, rgba(24,39,66,.96), rgba(17,26,46,.92));
        margin: .4rem 0 1.4rem 0;
    }
    .hero p { color: #b6c5dc; max-width: 760px; margin-bottom: 0; font-size: 1.02rem; }
    .hero h1 { margin: .4rem 0 .55rem 0; }
    .panel {
        background: rgba(17,26,46,.92);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1.1rem 1.25rem;
    }
    .metric-label { color: var(--muted); font-size: .82rem; margin-bottom: .35rem; }
    .metric-value { font-family: 'Manrope', sans-serif; font-size: 1.9rem; font-weight: 800; line-height: 1.2; }
    .metric-note { color: var(--muted); font-size: .78rem; margin-top: .35rem; }
    .tag {
        display: inline-block; border: 1px solid var(--border); background: #17243b;
        color: #dbe8fb; border-radius: 999px; padding: .28rem .62rem;
        margin: .16rem .2rem .16rem 0; font-size: .82rem;
    }
    .skill-row {
        display:flex; align-items:center; justify-content:space-between; gap:1rem;
        border-bottom: 1px solid rgba(38,53,80,.7); padding: .7rem 0;
    }
    .skill-row:last-child { border-bottom: 0; }
    .skill-name { color: var(--text); font-weight: 600; }
    .skill-meta { color: var(--muted); font-size: .82rem; }
    .status {
        display:inline-block; border-radius:999px; padding:.2rem .55rem;
        font-size:.75rem; font-weight:700;
    }
    .status-good { color:#91e6c2; background:rgba(35,143,101,.16); }
    .status-mid { color:#ffda8d; background:rgba(193,132,26,.16); }
    .status-low { color:#ffb0b4; background:rgba(190,69,80,.16); }
    div[data-testid="stMetric"] {
        background: var(--panel); border: 1px solid var(--border);
        padding: 1rem 1.1rem; border-radius: 14px;
    }
    div[data-testid="stMetric"] label { color: var(--muted) !important; }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-family: 'Manrope', sans-serif; color: var(--text);
    }
    .stButton > button, .stDownloadButton > button {
        border-radius: 10px; border: 1px solid #3a5279;
        background: #1b2a45; color: #f3f7ff; font-weight: 700;
        min-height: 2.7rem; transition: all .15s ease;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background: #263d62; border-color: #75a7ff; color: white;
    }
    .stButton > button[kind="primary"] {
        background: var(--accent-strong); border-color: var(--accent-strong);
    }
    .stButton > button[kind="primary"]:hover { background: #2c67d3; }
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div {
        background: #101a2d; border-color: #344765; border-radius: 10px;
    }
    input, textarea { color: var(--text) !important; }
    [data-testid="stTabs"] button { font-weight: 700; }
    [data-testid="stAlert"] { border-radius: 12px; }
    hr { border-color: var(--border); }
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Role templates are transparent, editable starter references—not live job-market data.
ROLE_SKILLS = {
    "Data Analyst": {
        "Python": 3, "SQL": 3, "Excel": 2, "Data visualization": 3,
        "Statistics": 3, "Pandas": 2, "Problem solving": 2, "Communication": 1,
    },
    "Python Developer": {
        "Python": 3, "Git": 2, "SQL": 2, "Object-oriented programming": 3,
        "Debugging": 2, "APIs": 2, "Testing": 2, "Problem solving": 2,
    },
    "AI / ML Engineer": {
        "Python": 3, "Machine learning": 3, "Statistics": 3, "Pandas": 2,
        "NumPy": 2, "Data preprocessing": 3, "Model evaluation": 3,
        "Git": 1, "SQL": 1,
    },
    "Frontend Developer": {
        "HTML": 2, "CSS": 3, "JavaScript": 3, "Responsive design": 2,
        "Git": 2, "Accessibility": 1, "Debugging": 2, "APIs": 1,
    },
    "Full-Stack Developer": {
        "HTML": 1, "CSS": 2, "JavaScript": 3, "Python": 2,
        "SQL": 2, "APIs": 3, "Git": 2, "Testing": 2,
    },
    "Data Scientist": {
        "Python": 3, "Statistics": 3, "Machine learning": 3, "SQL": 2,
        "Pandas": 3, "NumPy": 2, "Data visualization": 2,
        "Data preprocessing": 3, "Model evaluation": 3,
    },
    "Product / Business Analyst": {
        "Excel": 3, "SQL": 2, "Data visualization": 2, "Communication": 3,
        "Problem solving": 3, "Requirements analysis": 3, "Presentation": 2,
        "Statistics": 1,
    },
    "QA / Test Engineer": {
        "Testing": 3, "Test case design": 3, "Debugging": 2, "SQL": 1,
        "Git": 1, "APIs": 2, "Problem solving": 2, "Communication": 1,
    },
}

SKILL_CATALOG = sorted({
    skill for role in ROLE_SKILLS.values() for skill in role
} | {
    "C", "C++", "Java", "R", "Power BI", "Tableau", "Deep learning",
    "Natural language processing", "Computer vision", "PyTorch",
    "TensorFlow", "Cloud basics", "Linux", "Docker", "Figma",
    "Writing", "Research", "Project management", "Teamwork",
    "Presentation", "Requirements analysis", "Test case design",
    "Accessibility", "Responsive design", "Data preprocessing",
    "Model evaluation", "Object-oriented programming", "Debugging",
    "APIs", "Testing", "Git", "NumPy", "Pandas", "Statistics",
    "Data visualization", "Problem solving", "Communication",
})

# Keywords map common variants to the canonical skills used by the app.
ALIASES = {
    "python": "Python", "py": "Python",
    "sql": "SQL", "structured query language": "SQL",
    "excel": "Excel", "microsoft excel": "Excel",
    "power bi": "Power BI", "tableau": "Tableau",
    "data visualization": "Data visualization", "data visualisation": "Data visualization",
    "statistics": "Statistics", "statistical analysis": "Statistics",
    "machine learning": "Machine learning", "ml": "Machine learning",
    "deep learning": "Deep learning", "nlp": "Natural language processing",
    "natural language processing": "Natural language processing",
    "computer vision": "Computer vision", "pytorch": "PyTorch",
    "tensorflow": "TensorFlow", "pandas": "Pandas", "numpy": "NumPy",
    "javascript": "JavaScript", "js": "JavaScript", "html": "HTML",
    "css": "CSS", "responsive design": "Responsive design",
    "git": "Git", "github": "Git", "api": "APIs", "apis": "APIs",
    "rest api": "APIs", "rest apis": "APIs",
    "object oriented programming": "Object-oriented programming",
    "oop": "Object-oriented programming", "debugging": "Debugging",
    "testing": "Testing", "unit testing": "Testing",
    "test case design": "Test case design", "problem solving": "Problem solving",
    "communication": "Communication", "presentation": "Presentation",
    "linux": "Linux", "docker": "Docker", "cloud": "Cloud basics",
    "cloud computing": "Cloud basics", "c++": "C++", "java": "Java",
    "programming in c": "C", "c programming": "C", "powerpoint": "Presentation",
    "project management": "Project management", "teamwork": "Teamwork",
    "requirements analysis": "Requirements analysis",
    "data preprocessing": "Data preprocessing", "model evaluation": "Model evaluation",
    "writing": "Writing", "research": "Research", "figma": "Figma",
}

LEARNING_GUIDES = {
    "Python": ("Write small scripts, practise functions and collections, then build a command-line tool.", "Build a CSV cleaner or file organiser."),
    "SQL": ("Practise SELECT, filtering, joins, grouping and subqueries on a small dataset.", "Answer 10 business questions from a sample database."),
    "Excel": ("Practise formulas, lookup functions, pivot tables and clean chart design.", "Turn a messy spreadsheet into a one-page report."),
    "Data visualization": ("Learn chart choice, labels, colour restraint and how to explain a finding.", "Create a dashboard with three useful charts."),
    "Statistics": ("Review distributions, averages, variance, probability and correlation.", "Analyse a dataset and write five observations."),
    "Pandas": ("Load data, handle missing values, filter rows, group results and export files.", "Create a reusable data-cleaning notebook."),
    "NumPy": ("Practise arrays, shapes, indexing and vectorised calculations.", "Compare a loop-based calculation with a NumPy version."),
    "Machine learning": ("Start with train/test splits, baselines, overfitting and a simple model.", "Train and evaluate a small classifier."),
    "Data preprocessing": ("Practise missing values, duplicates, encoding and scaling without data leakage.", "Document a repeatable preprocessing pipeline."),
    "Model evaluation": ("Learn appropriate metrics and why accuracy can be misleading.", "Compare two models and justify the metric used."),
    "Git": ("Practise commits, branches, diffs and a clear README.", "Publish one small project with a meaningful commit history."),
    "JavaScript": ("Practise variables, functions, arrays, objects and DOM events.", "Build a small interactive form."),
    "HTML": ("Learn semantic structure, forms, links and accessible labels.", "Create a clean single-page project profile."),
    "CSS": ("Practise layout, spacing, responsive design and reusable styles.", "Rebuild one page at desktop and mobile widths."),
    "APIs": ("Learn HTTP methods, status codes, JSON and basic error handling.", "Consume a public API and show the returned data."),
    "Testing": ("Write tests for normal cases, edge cases and invalid inputs.", "Add a small test suite to an existing project."),
    "Debugging": ("Reproduce issues, inspect values and isolate the smallest failing case.", "Write down and fix three bugs in a project."),
    "Object-oriented programming": ("Practise classes, methods, composition and clear responsibilities.", "Model a simple library or inventory system."),
    "Communication": ("Explain your approach, trade-offs and result in plain language.", "Write a short project case study for a non-technical reader."),
    "Problem solving": ("Break tasks into inputs, outputs, constraints and small testable steps.", "Solve a set of small problems and record the reasoning."),
}

def canonicalise(text):
    key = re.sub(r"[^a-z0-9+# ]+", " ", text.lower())
    key = re.sub(r"\s+", " ", key).strip()
    if key in ALIASES:
        return ALIASES[key]
    for alias, canonical in sorted(ALIASES.items(), key=lambda item: len(item[0]), reverse=True):
        if re.search(r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])", key):
            return canonical
    return None


def extract_skills(text):
    found = []
    lower = text.lower()
    for alias, canonical in sorted(ALIASES.items(), key=lambda item: len(item[0]), reverse=True):
        pattern = r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])"
        if re.search(pattern, lower) and canonical not in found:
            found.append(canonical)
    return found


def build_roadmap(missing, weeks, hours_per_week):
    if not missing:
        return pd.DataFrame(columns=["Week", "Focus skill", "Practice task", "Suggested effort"])
    total_hours = max(1, int(weeks) * int(hours_per_week))
    # Keep a modest plan; more than one skill can be revisited in a week.
    skill_count = min(len(missing), weeks * 2)
    selected = missing[:skill_count]
    rows = []
    for i, skill in enumerate(selected):
        week = min(weeks, (i // 2) + 1)
        guide, project = LEARNING_GUIDES.get(
            skill,
            (f"Learn the core concepts of {skill} and practise with a small guided exercise.",
             f"Build a small project that demonstrates {skill}."),
        )
        rows.append({
            "Week": f"Week {week}",
            "Focus skill": skill,
            "Practice task": project,
            "Suggested effort": f"{max(1, total_hours // max(1, skill_count))} hours",
        })
    return pd.DataFrame(rows)


def make_report(role, score, matched, missing, current_levels, source_name, roadmap):
    lines = [
        "# SkillMap — Skills Review",
        "",
        f"Created: {date.today().isoformat()}",
        f"Target role: {role}",
        f"Analysis source: {source_name}",
        "",
        "## Summary",
        f"- Skills matched: {len(matched)}",
        f"- Skills to develop: {len(missing)}",
        f"- Coverage score: {score}%",
        "",
        "This is a planning aid based on the skills selected or detected. It is not a hiring prediction.",
        "",
        "## Skills already selected",
    ]
    lines += [f"- {skill}: {current_levels.get(skill, 'Not rated')}" for skill in matched] or ["- No matching skills found."]
    lines += ["", "## Skills to develop"]
    lines += [f"- {skill}" for skill in missing] or ["- No gaps found in the selected comparison."]
    lines += ["", "## Suggested learning plan"]
    if not roadmap.empty:
        for _, row in roadmap.iterrows():
            lines.append(f"- {row['Week']} — {row['Focus skill']}: {row['Practice task']} ({row['Suggested effort']})")
    else:
        lines.append("- No learning plan needed for the current comparison.")
    lines += ["", "## Notes", "- Role skill lists are editable starter references, not live labour-market data."]
    return "\n".join(lines)


# ------------------------------- Sidebar -------------------------------
with st.sidebar:
    st.markdown('<div class="brand"><span class="brand-mark"></span>SkillMap</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted" style="font-size:.88rem;">Career skills workspace</div>', unsafe_allow_html=True)
    st.divider()

    page = st.radio(
        "Workspace",
        ["Overview", "Job description", "Learning plan", "About this project"],
        label_visibility="visible",
    )
    st.divider()
    st.markdown("**Your goal**")
    target_role = st.selectbox("Target role", list(ROLE_SKILLS.keys()), key="target_role")
    st.caption("Role templates are starting points. A real job description gives a more specific comparison.")
    st.divider()
    st.markdown("**Planning preferences**")
    weeks = st.slider("Plan length (weeks)", min_value=2, max_value=12, value=4)
    hours_per_week = st.slider("Hours available per week", min_value=1, max_value=15, value=4)
    st.caption("Your plan is a guide, not a deadline.")

# State setup
if "selected_skills" not in st.session_state:
    st.session_state.selected_skills = ["Python", "HTML", "Excel"]
if "skill_levels" not in st.session_state:
    st.session_state.skill_levels = {}
if "job_text" not in st.session_state:
    st.session_state.job_text = ""
if "custom_skills" not in st.session_state:
    st.session_state.custom_skills = []
if "analysis_source" not in st.session_state:
    st.session_state.analysis_source = "Role template"
if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = None

# Header
st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">CAREER DEVELOPMENT WORKSPACE</div>
      <h1>Make your next skill move count.</h1>
      <p>Compare what you know with what a role asks for, then turn the gaps into a realistic plan you can work through.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if page == "About this project":
    st.markdown("## A practical tool, not a hiring score")
    st.write(
        "SkillMap compares a skill profile with a role template or the skills it can recognise in a pasted job description. "
        "It helps organise learning priorities; it does not predict whether someone will get hired."
    )
    a, b = st.columns(2)
    with a:
        st.markdown('<div class="panel"><h3>What it does</h3><p>Tracks selected skills, compares them with role requirements, displays coverage, and creates a week-by-week practice plan.</p></div>', unsafe_allow_html=True)
    with b:
        st.markdown('<div class="panel"><h3>What it does not do</h3><p>It does not contact employers, verify skill levels, browse live job listings, or use a trained AI model. Job-description matching is keyword-based.</p></div>', unsafe_allow_html=True)
    st.info("For a portfolio project, describe the current version honestly as a Python/Streamlit skills analysis tool with keyword-based job-description parsing.")
    st.stop()

if page == "Job description":
    st.markdown("## Analyse a job description")
    st.write("Paste the responsibilities or requirements section from a job advert. SkillMap will look for skills in its built-in vocabulary.")
    st.session_state.job_text = st.text_area(
        "Job description",
        value=st.session_state.job_text,
        height=240,
        placeholder="Example: We are looking for a junior data analyst with Python, SQL, Excel and data visualization experience...",
        help="You can remove company names and personal information before pasting.",
    )
    left, right = st.columns([1, 2])
    with left:
        if st.button("Find skills in this text", type="primary", use_container_width=True):
            detected = extract_skills(st.session_state.job_text)
            if detected:
                st.session_state.custom_skills = detected
                st.session_state.analysis_source = "Pasted job description"
                st.session_state.last_analysis = None
                st.success(f"Found {len(detected)} recognised skills.")
            else:
                st.warning("No recognised skills were found. Try pasting the requirements section or use the role template.")
    with right:
        if st.session_state.custom_skills:
            st.markdown("**Recognised skills**")
            st.markdown("".join(f'<span class="tag">{s}</span>' for s in st.session_state.custom_skills), unsafe_allow_html=True)
            st.caption("Keyword matches only. The tool may miss synonyms or skills outside its vocabulary.")
    st.divider()
    st.markdown("### Your current skill profile")
    st.write("Update your selected skills on the Overview page, then return here to compare them with the detected requirements.")
    st.stop()

if page == "Learning plan":
    st.markdown("## Learning plan")
    st.write("Your plan is based on the most recent comparison. Analyse your skills on the Overview page to refresh it.")
    if st.session_state.last_analysis:
        data = st.session_state.last_analysis
        roadmap = build_roadmap(data["missing"], weeks, hours_per_week)
        if roadmap.empty:
            st.success("No missing skills were found in this comparison. You can deepen your existing skills or choose another role.")
        else:
            st.dataframe(roadmap, use_container_width=True, hide_index=True)
            st.markdown("### How to use the plan")
            st.write("Work on one task at a time. Keep a small note of what you built, what failed, and what you would improve next.")
    else:
        st.info("No comparison saved in this session yet. Open Overview and select **Analyse my profile**.")
    st.stop()

# ------------------------------- Overview -------------------------------
st.markdown("## Your skills profile")
st.markdown('<div class="muted">Select skills you can currently use. Rate your confidence honestly; you can update it as you practise.</div>', unsafe_allow_html=True)
st.write("")

profile_col, level_col = st.columns([1.1, 1])

with profile_col:
    selected = st.multiselect(
        "Skills you have worked with",
        options=SKILL_CATALOG,
        default=[s for s in st.session_state.selected_skills if s in SKILL_CATALOG],
        key="skills_picker",
        help="Choose skills you can explain or demonstrate—not skills you only recognise by name.",
    )
    st.session_state.selected_skills = selected
    custom_skill = st.text_input("Add another skill", placeholder="e.g. OpenCV, FastAPI")
    if st.button("Add skill", use_container_width=False):
        new_skill = custom_skill.strip()
        if new_skill and new_skill not in st.session_state.selected_skills:
            st.session_state.selected_skills.append(new_skill)
            st.session_state.custom_skills.append(new_skill)
            st.rerun()
        elif new_skill:
            st.info("That skill is already in your profile.")

with level_col:
    st.markdown("### Confidence check")
    st.caption("These ratings are for your own planning. They do not change the coverage calculation.")
    current = st.session_state.selected_skills
    if current:
        for skill in current[:8]:
            st.session_state.skill_levels[skill] = st.select_slider(
                skill,
                options=["Learning", "Beginner", "Comfortable", "Confident"],
                value=st.session_state.skill_levels.get(skill, "Beginner"),
                key=f"level_{skill}",
            )
        if len(current) > 8:
            st.caption(f"Showing the first 8 of {len(current)} selected skills. The rest are still included in the comparison.")
    else:
        st.write("Choose at least one skill to start your profile.")

st.divider()

source_options = ["Use role template"]
if st.session_state.custom_skills:
    source_options.append("Use skills detected from job description")
source_choice = st.radio(
    "Compare your profile against",
    source_options,
    horizontal=True,
    index=1 if st.session_state.analysis_source == "Pasted job description" and len(source_options) > 1 else 0,
)
if source_choice == "Use skills detected from job description" and st.session_state.custom_skills:
    requirements = {s: 2 for s in st.session_state.custom_skills}
    comparison_name = "Pasted job description"
else:
    requirements = ROLE_SKILLS[target_role]
    comparison_name = target_role

# Include custom profile skills in the selectable comparison if users typed one in.
current_set = set(st.session_state.selected_skills)
matched = [skill for skill in requirements if skill.lower() in {s.lower() for s in current_set}]
missing = [skill for skill in requirements if skill.lower() not in {s.lower() for s in current_set}]
score = round(100 * len(matched) / len(requirements)) if requirements else 0

run_col, note_col = st.columns([1, 2])
with run_col:
    analyse = st.button("Analyse my profile", type="primary", use_container_width=True)
with note_col:
    st.markdown('<div class="muted" style="padding:.7rem 0;">The result reflects selected skills only. It is not a measure of job readiness.</div>', unsafe_allow_html=True)

if analyse:
    st.session_state.last_analysis = {
        "role": comparison_name,
        "score": score,
        "matched": matched,
        "missing": missing,
        "requirements": list(requirements),
        "source": comparison_name,
        "levels": dict(st.session_state.skill_levels),
    }

# Display current comparison immediately, and persist it when analysed.
data = st.session_state.last_analysis
if data and data["role"] == comparison_name and data["requirements"] == list(requirements):
    shown_matched, shown_missing, shown_score = data["matched"], data["missing"], data["score"]
else:
    shown_matched, shown_missing, shown_score = matched, missing, score

st.divider()
st.markdown("## Snapshot")
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Skills selected", len(st.session_state.selected_skills))
with m2:
    st.metric("Requirements compared", len(requirements))
with m3:
    st.metric("Skills matched", len(shown_matched))
with m4:
    st.metric("Coverage", f"{shown_score}%")

progress_col, text_col = st.columns([1.5, 1])
with progress_col:
    st.markdown("### Coverage at a glance")
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=shown_score,
        number={"suffix": "%", "font": {"size": 42, "color": "#edf2fb"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#9aabc5", "tickfont": {"color": "#9aabc5"}},
            "bar": {"color": "#75a7ff", "thickness": .25},
            "bgcolor": "#111a2e",
            "bordercolor": "#263550",
            "steps": [
                {"range": [0, 40], "color": "#252033"},
                {"range": [40, 70], "color": "#202c42"},
                {"range": [70, 100], "color": "#1b3540"},
            ],
            "threshold": {"line": {"color": "#5bd0a0", "width": 3}, "thickness": .8, "value": 70},
        },
    ))
    fig.update_layout(
        height=270, margin=dict(l=15, r=15, t=25, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "DM Sans", "color": "#edf2fb"},
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
with text_col:
    st.markdown("### What this means")
    if shown_score >= 75:
        status, status_class = "Strong overlap", "status-good"
        advice = "Your selected skills cover much of this comparison. Review the gaps and build evidence through a small project."
    elif shown_score >= 45:
        status, status_class = "Some overlap", "status-mid"
        advice = "You have a starting point. Choose one important missing skill and practise it in a project before adding more topics."
    else:
        status, status_class = "Early-stage match", "status-low"
        advice = "Treat this as a starting map, not a judgement. Pick one foundational skill and work through a focused exercise."
    st.markdown(f'<span class="status {status_class}">{status}</span>', unsafe_allow_html=True)
    st.write(advice)
    st.markdown(f'<div class="panel"><div class="metric-label">Comparison source</div><div style="font-size:1.1rem;font-weight:700;">{comparison_name}</div><div class="metric-note">Role templates are starter references; job descriptions are keyword-matched.</div></div>', unsafe_allow_html=True)

tab_match, tab_gap, tab_plan = st.tabs(["Skills you selected", "Skills to work on", "Suggested plan"])

with tab_match:
    if shown_matched:
        st.markdown("Skills in your profile that also appear in this comparison.")
        for skill in shown_matched:
            level = st.session_state.skill_levels.get(skill, "Not rated")
            st.markdown(
                f'<div class="skill-row"><div><div class="skill-name">{skill}</div>'
                f'<div class="skill-meta">Confidence: {level}</div></div>'
                f'<span class="status status-good">Matched</span></div>',
                unsafe_allow_html=True,
            )
    else:
        st.info("No selected skills overlap with this comparison yet. That is useful information for choosing your first learning task.")

with tab_gap:
    if shown_missing:
        st.markdown("These are the skills in the comparison that are not yet in your selected profile.")
        for i, skill in enumerate(shown_missing):
            guide, project = LEARNING_GUIDES.get(
                skill,
                (f"Learn the main concepts of {skill} and practise with short exercises.",
                 f"Build a small project that demonstrates {skill}."),
            )
            with st.expander(f"{i + 1:02d}  {skill}", expanded=(i == 0)):
                st.write(guide)
                st.markdown(f"**Try this:** {project}")
    else:
        st.success("No skill gaps were found in this comparison. You can select another role or use a job description for a more specific check.")

with tab_plan:
    roadmap = build_roadmap(shown_missing, weeks, hours_per_week)
    if roadmap.empty:
        st.write("There are no gaps in this comparison to turn into a learning plan.")
    else:
        st.caption(f"Planned around {hours_per_week} hours per week for {weeks} weeks. The first skills are listed first; adjust the pace to suit your schedule.")
        st.dataframe(roadmap, use_container_width=True, hide_index=True)
        if st.button("Open full learning plan"):
            st.session_state["open_learning_plan"] = True
            st.info("Choose Learning plan in the left sidebar to view the plan separately.")

st.divider()
st.markdown("## Take your results with you")
st.write("Download a copy for your own records or to use as a project-planning checklist.")
report = make_report(
    comparison_name,
    shown_score,
    shown_matched,
    shown_missing,
    st.session_state.skill_levels,
    comparison_name,
    build_roadmap(shown_missing, weeks, hours_per_week),
)
csv_buffer = io.StringIO()
writer = csv.writer(csv_buffer)
writer.writerow(["Skill", "Status", "Confidence"])
for skill in requirements:
    status = "Matched" if skill in shown_matched else "To develop"
    writer.writerow([skill, status, st.session_state.skill_levels.get(skill, "Not rated")])
d1, d2, d3 = st.columns([1, 1, 2])
with d1:
    st.download_button(
        "Download review (.md)",
        data=report,
        file_name="skillmap_review.md",
        mime="text/markdown",
        use_container_width=True,
    )
with d2:
    st.download_button(
        "Download skills (.csv)",
        data=csv_buffer.getvalue(),
        file_name="skillmap_skills.csv",
        mime="text/csv",
        use_container_width=True,
    )
with d3:
    st.caption("Keep the report honest: it records your selections and a rule-based comparison, not independently verified proficiency.")

st.divider()
st.markdown(
    '<div class="muted" style="font-size:.8rem;">SkillMap · Built with Python, Streamlit, Pandas and Plotly · '
    'Your inputs stay in this local app session unless you choose to download them.</div>',
    unsafe_allow_html=True,
)
