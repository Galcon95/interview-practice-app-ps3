# Page: Prompt Lab (developer mode only, see config.ini and app.py).
# Compares the 5 prompt techniques of the Role Q&A question generator. The test cases
# come from prompt_lab/test_cases.ini (editable, read on every page load). One test case
# (role, level) and the model are the same for every technique, so only the prompt changes.
# Each result is measured automatically, scored by the developer with a rubric, and
# optionally scored by an AI judge (LLM-as-judge) with the same rubric. The scores are
# saved to prompt_lab/scores.csv; the page compares the techniques, and you with the judge.
# The customer pages always use the default technique; only this page tries the others.
#
# What the page remembers (st.session_state):
#   "lab_results"     the last run: {"run_id", "case", "model", "results": {technique: {...}},
#                     "judge_model", "judgments": {technique: verdict or {"error"}}, "saved"}
#   "lab_saved_note"  a short-lived note after saving
#   "score_<run_id>_<technique>_<criterion>"  the star widgets (0 to 4 = 1 to 5 stars)

import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import pandas as pd
import streamlit as st

import api_client
from components.section_header import section_header

FEATURE = "role_qa"


def run_technique(technique, role, level, settings):
    """Run one technique for the test case and measure the time (runs in a worker thread).

    No Streamlit calls in here: worker threads can't draw on the page.

    Args:
        technique: a key of api_client.get_prompt_techniques(FEATURE).
        role: the IT role of the test case.
        level: the level of the test case.
        settings: the LLM settings from the sidebar.

    Returns:
        A dict {"questions", "reasoning", "seconds", "error"}; "error" is the
        error message (str) if the call failed, otherwise None.
    """
    start = time.perf_counter()
    try:
        result = api_client.generate_questions_with_technique(role, level, settings, technique)
        return {**result, "seconds": time.perf_counter() - start, "error": None}
    except Exception as error:
        return {"questions": [], "reasoning": None, "seconds": time.perf_counter() - start, "error": str(error)}


def judge_technique(case, questions, model):
    """Let the AI judge score one technique's questions (runs in a worker thread).

    Args:
        case: the test case dict.
        questions: the technique's questions.
        model: the judge's model ID.

    Returns:
        The verdict {criterion: {"score", "reason"}}, or {"error": message} if it failed.
    """
    try:
        return api_client.judge_questions(case, questions, model)
    except Exception as error:
        return {"error": str(error)}


def judge_all(lab, model):
    """Let the AI judge score every successful result of a run, all at the same time.

    Args:
        lab: the run from st.session_state["lab_results"]; its "judgments" and
            "judge_model" are filled in.
        model: the judge's model ID.
    """
    to_judge = [key for key, result in lab["results"].items() if not result["error"]]
    if not to_judge:
        return
    with ThreadPoolExecutor(max_workers=len(to_judge)) as pool:
        verdicts = pool.map(lambda key: judge_technique(lab["case"], lab["results"][key]["questions"], model), to_judge)
        lab["judgments"] = dict(zip(to_judge, verdicts))
    lab["judge_model"] = model


def score_key(run_id, technique, criterion):
    """Build the session_state key of one star widget.

    Args:
        run_id: the id of the run, so a new run gets fresh, empty stars.
        technique: the technique key.
        criterion: the rubric key, e.g. "clarity".

    Returns:
        The key (str).
    """
    return f"score_{run_id}_{technique}_{criterion}"


def show_result(technique, info, result, lab, rubric):
    """Draw one technique's result as a card: questions, measurements, your stars and the judge's scores.

    Args:
        technique: the technique key.
        info: the technique's {"label", "description", "default"}.
        result: the dict from run_technique().
        lab: the whole run from st.session_state["lab_results"].
        rubric: the criteria from api_client.get_rubric().
    """
    with st.container(border=True):
        st.markdown(f"**{info['label']}**" + ("  :green-badge[App]" if info["default"] else ""))
        if result["error"]:
            st.error(result["error"])
            return
        questions = result["questions"]
        for number, question in enumerate(questions, start=1):
            st.markdown(f"**Q{number}.** {question}")
        if result["reasoning"]:
            with st.expander("The model's planning / corrections"):
                st.text(result["reasoning"])

        # Measured automatically (keyword heuristics for behavioral and topics: estimates).
        measured = api_client.measure_questions(questions, lab["case"]["expected_topics"])
        expected = len(lab["case"]["expected_topics"])
        line = (
            f"{measured['avg_words']:.0f} words/question · {measured['multi_part']} packed · "
            f"{measured['behavioral']} behavioral · {result['seconds']:.0f} s"
        )
        if expected:
            line += f" · topics {len(measured['topics_covered'])}/{expected}"
        st.caption(line)
        if measured["topics_missing"]:
            st.caption("Missing topics: " + ", ".join(measured["topics_missing"]))

        # Scored by the developer with the rubric.
        st.markdown("<small><b>Your scores</b></small>", unsafe_allow_html=True)
        for criterion in rubric:
            col_label, col_stars = st.columns([2, 3], vertical_alignment="center")
            col_label.markdown(f"<small>{criterion['label']}</small>", unsafe_allow_html=True)
            with col_stars:
                st.feedback("stars", key=score_key(lab["run_id"], technique, criterion["key"]), disabled=lab["saved"])

        # Scored by the AI judge with the same rubric.
        verdict = lab["judgments"].get(technique)
        if verdict and "error" in verdict:
            st.caption(f"AI judge failed: {verdict['error']}")
        elif verdict:
            total = sum(verdict[c["key"]]["score"] for c in rubric)
            scores = " · ".join(f"{c['label']} {verdict[c['key']]['score']}" for c in rubric)
            st.markdown(f"<small><b>AI judge:</b> {scores} · <b>{total}/{5 * len(rubric)}</b></small>", unsafe_allow_html=True)
            with st.expander("The judge's reasons"):
                for c in rubric:
                    st.markdown(f"**{c['label']} ({verdict[c['key']]['score']}):** {verdict[c['key']]['reason']}")


def collect_scores(lab, rubric):
    """Collect the stars the developer gave, for the techniques that are fully scored.

    Args:
        lab: the whole run from st.session_state["lab_results"].
        rubric: the criteria from api_client.get_rubric().

    Returns:
        A tuple (scores, incomplete): scores is {technique: {criterion: 1 to 5}} for every
        technique with all criteria scored; incomplete lists the labels of techniques that
        are partly scored (their stars are not saved).
    """
    scores, incomplete = {}, []
    for technique, result in lab["results"].items():
        if result["error"]:
            continue
        values = {c["key"]: st.session_state.get(score_key(lab["run_id"], technique, c["key"])) for c in rubric}
        given = [value for value in values.values() if value is not None]
        if len(given) == len(rubric):
            scores[technique] = {key: value + 1 for key, value in values.items()}  # 0-4 -> 1-5 stars
        elif given:
            incomplete.append(techniques[technique]["label"])
    return scores, incomplete


def show_comparisons(rows, rubric):
    """Draw the comparisons over all saved runs: the techniques, and you vs. the AI judge.

    Args:
        rows: the saved rows from api_client.load_lab_scores().
        rubric: the criteria from api_client.get_rubric().
    """
    table = pd.DataFrame(rows)
    keys = [c["key"] for c in rubric]
    for column in [*keys, "total", *[f"judge_{k}" for k in keys], "judge_total", "topics_covered", "topics_expected"]:
        table[column] = pd.to_numeric(table[column], errors="coerce")  # empty = not scored
    table["topics %"] = 100 * table["topics_covered"] / table["topics_expected"].where(table["topics_expected"] > 0)
    label = lambda key: techniques.get(key, {"label": key})["label"]  # noqa: E731
    max_total = 5 * len(rubric)

    # a) Which technique works best: your and the judge's average total, plus the measurements.
    st.markdown("**Techniques**")
    summary = (
        table.groupby("technique")
        .agg(
            runs=("technique", "size"),
            you=("total", "mean"),
            ai=("judge_total", "mean"),
            words=("avg_words", "mean"),
            packed=("multi_part", "mean"),
            behavioral=("behavioral", "mean"),
            topics=("topics %", "mean"),
            seconds=("seconds", "mean"),
        )
        .round(1)
    )
    summary = summary.sort_values(["you", "ai"], ascending=False)
    summary.index = [label(key) for key in summary.index]
    # "–" instead of an empty cell where nobody scored (st.dataframe would show "None").
    for column in ("you", "ai"):
        summary[column] = summary[column].map(lambda value: "–" if pd.isna(value) else f"{value:.1f}")
    st.dataframe(summary, column_config={
        "you": st.column_config.TextColumn(f"you (of {max_total})"),
        "ai": st.column_config.TextColumn(f"AI judge (of {max_total})"),
        "topics": st.column_config.NumberColumn("topics %"),
    })

    # b) The same per criterion, "you / AI judge".
    st.markdown("**Per criterion (you / AI judge, average of 1 to 5)**")
    per_criterion = pd.DataFrame(index=sorted(table["technique"].unique(), key=lambda k: list(techniques).index(k) if k in techniques else 99))
    for c in rubric:
        you = table.groupby("technique")[c["key"]].mean()
        ai = table.groupby("technique")[f"judge_{c['key']}"].mean()
        per_criterion[c["label"]] = [
            f"{you.get(k, float('nan')):.1f} / {ai.get(k, float('nan')):.1f}".replace("nan", "–")
            for k in per_criterion.index
        ]
    per_criterion.index = [label(key) for key in per_criterion.index]
    st.dataframe(per_criterion)

    # c) How well you and the judge agree, on the rows both scored.
    both = table.dropna(subset=["total", "judge_total"])
    st.markdown("**You vs. the AI judge**")
    if both.empty:
        st.caption("No technique is scored by both you and the AI judge yet.")
    else:
        agreement = pd.DataFrame([
            {
                "criterion": c["label"],
                "you": both[c["key"]].mean(),
                "AI judge": both[f"judge_{c['key']}"].mean(),
                "AI − you": (both[f"judge_{c['key']}"] - both[c["key"]]).mean(),
                "within 1 star %": 100 * ((both[f"judge_{c['key']}"] - both[c["key"]]).abs() <= 1).mean(),
            }
            for c in rubric
        ]).set_index("criterion").round(1)
        st.dataframe(agreement)
        best_you = both.groupby("technique")["total"].mean().idxmax()
        best_ai = both.groupby("technique")["judge_total"].mean().idxmax()
        verdict = "agree" if best_you == best_ai else "disagree"
        st.caption(
            f"Compared on {len(both)} scored results. Best technique by you: {label(best_you)}; "
            f"by the AI judge: {label(best_ai)} (you {verdict}). "
            "A positive 'AI − you' means the judge is more generous than you."
        )

    st.caption(
        f"{len(table)} saved results from {table['case'].nunique()} test case(s) and "
        f"{table['model'].nunique()} model(s). All rows: prompt_lab/scores.csv (opens in Excel)."
    )


section_header(
    "Prompt Lab",
    "Compare prompt techniques for the interview questions on one fixed test case.",
    pill="Developer mode",
)

techniques = api_client.get_prompt_techniques(FEATURE)
rubric = api_client.get_rubric()
models = api_client.get_models()
cases, problems = api_client.get_prompt_lab_test_cases()
settings = st.session_state.get("llm_settings") or api_client.get_default_settings()

# --- 1. Test case: the same for every technique ---
with st.container(border=True):
    st.markdown("#### 1. Test case")
    st.caption(
        "From prompt_lab/test_cases.ini: edit that file to add or change cases, then reload the page. "
        "The same test case and model go to every technique, so only the prompt changes."
    )
    for problem in problems:
        st.warning(problem, icon=":material/warning:")
    if not cases:
        st.stop()  # nothing to run; the warning above says why
    names = [case["name"] for case in cases]
    name = st.selectbox("Test case", names, key="lab_case")
    case = cases[names.index(name)]
    st.markdown(f'<span class="mono">Input for every technique: Role: {case["role"]} · Level: {case["level"]}</span>', unsafe_allow_html=True)
    if case["note"]:
        st.caption(case["note"])
    if case["expected_topics"]:
        st.markdown("Expected topics: " + " ".join(f":gray-badge[{topic}]" for topic in case["expected_topics"]))
    chosen = st.pills(
        "Techniques",
        list(techniques),
        selection_mode="multi",
        default=list(techniques),
        format_func=lambda key: techniques[key]["label"],
        key="lab_techniques",
    )
    col_judge, col_judge_model = st.columns([1, 2], vertical_alignment="bottom")
    use_judge = col_judge.toggle("AI judge scores too", value=True, key="lab_use_judge")
    model_ids = list(models)
    judge_model = col_judge_model.selectbox(
        "Judge model",
        model_ids,
        index=model_ids.index(api_client.get_judge_default_model()),
        format_func=lambda model_id: models[model_id]["label"],
        disabled=not use_judge,
        key="lab_judge_model",
        help="Best from another model family than the one that writes the questions: "
        "models tend to rate their own text higher.",
    )
    calls = len(chosen) * (2 if use_judge else 1)
    st.markdown(
        f'<span class="mono">Writer: {settings["model"]} (from the sidebar) · '
        f"{calls} AI calls (at most 10 per minute)</span>",
        unsafe_allow_html=True,
    )
    if st.button("Run", type="primary", icon=":material/play_arrow:", disabled=not chosen):
        with st.spinner(f"Running {len(chosen)} techniques..."):
            with ThreadPoolExecutor(max_workers=len(chosen)) as pool:
                runs = pool.map(lambda key: run_technique(key, case["role"], case["level"], settings), chosen)
                results = dict(zip(chosen, runs))
        lab = {
            "run_id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "case": case, "model": settings["model"], "results": results,
            "judge_model": "", "judgments": {}, "saved": False,
        }
        if use_judge:
            with st.spinner("The AI judge is scoring..."):
                judge_all(lab, judge_model)
        st.session_state["lab_results"] = lab

# --- 2. Results side by side, with the rubric ---
lab = st.session_state.get("lab_results")
if lab and "judgments" in lab:  # missing in results from an older version of this page
    judged = f" · judged by {lab['judge_model']}" if lab["judgments"] else ""
    st.markdown(f"#### 2. Results: {lab['case']['name']} · {lab['model']}{judged}")
    with st.expander("How to score: the rubric (1 to 5 stars per criterion)"):
        for criterion in rubric:
            anchors = criterion["anchors"]
            st.markdown(
                f"**{criterion['label']}**: {criterion['question']}  \n"
                f"1 = {anchors[1]}  \n3 = {anchors[3]}  \n5 = {anchors[5]}"
            )
        st.caption(
            "Measured automatically: words per question, packed (more than one sentence, e.g. a question plus a task), "
            "behavioral (phrases like 'Tell me about a time'), topics covered. The last two are "
            "keyword estimates. The AI judge uses the same rubric and doesn't know which technique wrote the questions."
        )

    items = list(lab["results"].items())
    for row_start in range(0, len(items), 3):  # 3 cards per row
        row = items[row_start:row_start + 3]
        for column, (key, result) in zip(st.columns(3), row):
            with column:
                show_result(key, techniques[key], result, lab, rubric)

    if lab["saved"]:
        st.success(st.session_state.get("lab_saved_note", "Scores saved."), icon=":material/check:")
    else:
        col_save, col_judge_now = st.columns([1, 3])
        if not lab["judgments"] and col_judge_now.button("Let the AI judge score", icon=":material/gavel:"):
            with st.spinner("The AI judge is scoring..."):
                judge_all(lab, judge_model)
            st.rerun()
        if col_save.button("Save scores", icon=":material/save:"):
            scores, incomplete = collect_scores(lab, rubric)
            judgments = {key: verdict for key, verdict in lab["judgments"].items() if "error" not in verdict}
            if scores or judgments:
                count = api_client.save_lab_scores(
                    lab["case"], lab["model"], lab["results"], scores,
                    datetime.now().strftime("%Y-%m-%d %H:%M"), judgments, lab["judge_model"],
                )
                lab["saved"] = True
                note = f"{count} result{'s' if count != 1 else ''} saved to prompt_lab/scores.csv."
                if incomplete:  # a warning would disappear with the rerun, so it goes into the note
                    note += " Your stars not saved (not fully scored): " + ", ".join(incomplete) + "."
                st.session_state["lab_saved_note"] = note
                st.rerun()
            else:
                st.warning("Nothing to save yet: give every criterion 1 to 5 stars, or let the AI judge score.")

# --- 3. Scores so far: comparisons ---
st.markdown("#### 3. Scores so far")
saved_rows = api_client.load_lab_scores()
if saved_rows:
    show_comparisons(saved_rows, rubric)
else:
    st.info("No scores saved yet. Run a test case, score it (you and/or the AI judge), then click **Save scores**.")

# --- 4. The prompts ---
st.markdown("#### The 5 prompt techniques")
st.caption(
    "Each technique is one prompt file in server/prompts/qa_generator/. All five ask for the "
    "same JSON reply. The guardrail (scope rules) is added to the end of each prompt."
)
for key, info in techniques.items():
    prompt = api_client.get_prompt_text(FEATURE, key)
    # About 4 characters per token in English text: a rough idea of the cost per call.
    title = f"{info['label']} · about {len(prompt) // 4:,} tokens" + (" · used by the app" if info["default"] else "")
    with st.expander(title):
        st.markdown(info["description"])
        st.code(prompt, language="markdown", wrap_lines=True)
