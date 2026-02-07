import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Academic Self-Audit Dashboard",
    layout="wide",
)

# ==================================================
# DEGREE RULES (B.Tech AI)
# ==================================================
CREDIT_RULES = {
    "Core": {"required": 120, "unlock_sem": 1},
    "PEP": {"required": 20, "unlock_sem": 1, "lock_after": 3},   # first 1.5 years
    "GE (Total)": {"required": 32, "unlock_sem": 1},
    "Humanities": {"required": 18, "unlock_sem": 1},            # subset of GE
    "Effective Execution": {"required": 6, "unlock_sem": 1},
    "SIP": {"required": 12, "unlock_sem": 3},
    "Short IIP": {"required": 8, "unlock_sem": 5},
    "Long IIP": {"required": 16, "unlock_sem": 7},
}

TOTAL_CREDITS = 194

SEMESTER_EXPECTED = {
    1: 20,
    2: 40,
    3: 62,
    4: 86,
    5: 112,
    6: 140,
    7: 170,
    8: 194,
}

# ==================================================
# HEADER
# ==================================================
st.title("📘 Academic Self-Audit Dashboard")
st.caption(
    "Evaluate your degree progress based on your **current academic stage**, "
    "**earned credits**, and **future-locked requirements**."
)

st.divider()

# ==================================================
# ACADEMIC POSITION (MAIN CANVAS)
# ==================================================
st.subheader("🎓 Academic Position")

col_pos1, col_pos2 = st.columns(2)

with col_pos1:
    semester = st.selectbox("Current Semester", list(range(1, 9)), index=3)

with col_pos2:
    st.markdown(
        f"**Academic Phase:** "
        f"{'Final Phase' if semester >= 7 else 'Mid Phase' if semester >= 3 else 'Early Phase'}"
    )

st.divider()

# ==================================================
# CREDIT INPUTS (MAIN CANVAS)
# ==================================================
st.subheader("📥 Credits Earned So Far")

c1, c2, c3 = st.columns(3)

with c1:
    core = st.number_input("Core Credits", 0, 120, 75)
    pep = st.number_input("PEP Credits", 0, 20, 12)
    execution = st.number_input("Effective Execution Credits", 0, 6, 3)

with c2:
    humanities = st.number_input("Humanities Credits (GE)", 0, 18, 10)
    other_ge = st.number_input("Other GE Credits", 0, 32, 12)

with c3:
    sip = st.number_input("SIP Credits", 0, 12, 0)
    short_iip = st.number_input("Short IIP Credits", 0, 8, 6)
    long_iip = st.number_input("Long IIP Credits", 0, 16, 0)

ge_total = humanities + other_ge

earned_inputs = {
    "Core": core,
    "PEP": pep,
    "GE (Total)": ge_total,
    "Humanities": humanities,
    "Effective Execution": execution,
    "SIP": sip,
    "Short IIP": short_iip,
    "Long IIP": long_iip,
}

st.divider()

# ==================================================
# EVALUATION LOGIC
# ==================================================
rows = []
earned_total = 0
future_locked = 0
pending = 0
missing = []

for cat, rule in CREDIT_RULES.items():
    earned = earned_inputs[cat]
    required = rule["required"]

    # availability logic
    available = semester >= rule["unlock_sem"]
    if "lock_after" in rule and semester > rule["lock_after"]:
        available = False

    if available:
        # avoid double counting Humanities (already inside GE)
        if cat not in ["Humanities"]:
            earned_total += earned

        deficit = max(0, required - earned)
        if deficit > 0:
            missing.append(cat)
            pending += deficit

        status = "Completed" if earned >= required else "Pending"
        progress = int((earned / required) * 100)
        remaining = deficit
    else:
        future_locked += required
        remaining = "-"
        progress = "-"
        status = "Not Available 🔒"

    rows.append([
        cat,
        required,
        earned,
        remaining,
        progress,
        status,
    ])

expected_by_now = SEMESTER_EXPECTED[semester]
performance_ratio = earned_total / max(expected_by_now, 1)

if performance_ratio >= 1:
    academic_status = "Eligible / On Track"
    risk = "Low"
    status_color = "success"
elif performance_ratio >= 0.85:
    academic_status = "On Track (Pending)"
    risk = "Low"
    status_color = "info"
elif performance_ratio >= 0.7:
    academic_status = "Attention Needed"
    risk = "Medium"
    status_color = "warning"
else:
    academic_status = "At Risk"
    risk = "High"
    status_color = "error"

# ==================================================
# STATUS CARD (BOLT-LIKE)
# ==================================================
getattr(st, status_color)(
    f"**{academic_status}**  \n"
    f"Credits Earned (Available): {earned_total} / {expected_by_now}"
)

st.progress(min(earned_total / TOTAL_CREDITS, 1.0))

# ==================================================
# RISK INDICATOR
# ==================================================
st.subheader("📉 Graduation Risk")

risk_map = {
    "Low": "🟢 Low Risk",
    "Medium": "🟡 Medium Risk",
    "High": "🔴 High Risk",
}
st.markdown(f"### {risk_map[risk]}")

# ==================================================
# SUMMARY METRICS
# ==================================================
c1, c2, c3, c4 = st.columns(4)

c1.metric("Credits Earned", earned_total)
c2.metric("Expected by Now", expected_by_now)
c3.metric("Pending Credits", pending)
c4.metric("Future Locked", future_locked)

# ==================================================
# CREDIT BREAKDOWN TABLE
# ==================================================
st.subheader("📊 Credit Breakdown")

df = pd.DataFrame(
    rows,
    columns=["Category", "Required", "Earned", "Remaining", "Progress %", "Status"]
)

st.dataframe(df, use_container_width=True)

# ==================================================
# MISSING REQUIREMENTS
# ==================================================
if missing:
    st.warning("### Missing / Incomplete Requirements")
    for m in missing:
        st.write("•", m)

# ==================================================
# NOTES
# ==================================================
st.info("""
### Important Notes
• **PEP is only available in Sem 1–3**  
• **GE total includes Humanities credits**  
• **Effective Execution credits are mandatory for degree completion**  
• Locked credits are excluded from progress calculation  
• SIP unlocks after Semester 2  
• Short IIP unlocks after Semester 4  
• Long IIP unlocks in the final year  
• Evaluation is based only on credits available at the current stage
""")
