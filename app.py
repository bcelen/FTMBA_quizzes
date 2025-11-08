import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("📊 Weekly Quiz Results Dashboard")

# --- UI Controls ---
col1, col2, col3 = st.columns([2, 2, 2])

with col1:
    week_option = st.selectbox("Select Week", [f"Week {i} Quiz Results" for i in range(1, 8)])
    week_file = f"week{week_option.split()[1]}.csv"

with col2:
    target_mean = st.slider(
        "🎯 Adjusted Average",
        min_value=3.7, max_value=3.8, value=3.75, step=0.01,
        help="Set the target average of adjusted marks"
    )

with col3:
    target_pct_above_4 = st.slider(
        "🔝 Maximum percentage of adjusted marks above 4",
        min_value=20, max_value=30, value=30, step=1,
        help="Maximum allowed percentage of adjusted marks ≥ 4"
    ) / 100

# --- Policy Description ---
st.markdown("""
MBS grade policy requires that the mean of the final marks (over 100) be between 74 and 76 (3.70 and 3.80 out of 5) and that the scores corresponding to H1 (4 out of 5) do not exceed 30%.  
The adjustment takes these criteria into account and adjusts marks while preserving the original z-scores.  

⚠️ *Please note that although these distributions are indicative, they may change at the end of the subject because there are some zero marks which may change after the census date.*
""")

# --- Load Data from GitHub ---
@st.cache_data
def load_data(file):
    try:
        url = f"https://raw.githubusercontent.com/bcelen/FTMBA_quizzes/main/{file}"
        df = pd.read_csv(url)
        return df
    except:
        return None

quiz_df = load_data(week_file)

if quiz_df is None:
    st.warning("📄 Quiz marks are not available yet.")
    st.stop()

# --- Clean and Extract Marks ---
original_marks = quiz_df.iloc[:, 0].astype(str).str.replace(',', '.').astype(float)

mean_orig = np.mean(original_marks)
std_orig = np.std(original_marks)
z_scores = (original_marks - mean_orig) / std_orig

z_cutoff = norm.ppf(1 - target_pct_above_4)
target_std = (4 - target_mean) / z_cutoff if z_cutoff != 0 else 1
adjusted_marks = np.clip((z_scores * target_std + target_mean), 0, 5)

# --- Summary Table ---
summary_df = pd.DataFrame({
    " ": ["Original Marks", "Adjusted Marks"],
    "Mean": [f"{mean_orig:.2f}", f"{np.mean(adjusted_marks):.2f}"],
    "Std. Dev": [f"{np.std(original_marks):.2f}", f"{np.std(adjusted_marks):.2f}"],
})

# --- Layout: Summary + Student Lookup ---
col_summ, col_rank = st.columns(2)

with col_summ:
    st.subheader("📋 Summary")
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

show_marker = False
user_adjusted = None
rank = None
total = len(adjusted_marks)

with col_rank:
    st.subheader("🔍 Find Your Adjusted Mark and Rank")
    with st.form("lookup_form"):
        input_col, result_col = st.columns(2)
        with input_col:
            student_mark = st.number_input(
                "Enter your original quiz mark (0–5):",
                min_value=0.0, max_value=5.0, step=0.01
            )
        submitted = st.form_submit_button("Find My Adjusted Mark")

    if submitted:
        student_z = (student_mark - mean_orig) / std_orig
        adjusted_student_mark = np.clip(student_z * target_std + target_mean, 0, 5)

        # --- Precision-safe rank calculation ---
        higher_count = np.sum(adjusted_marks > adjusted_student_mark)
        tie_count = np.sum(np.isclose(adjusted_marks, adjusted_student_mark, rtol=1e-5, atol=1e-8))
        student_rank = higher_count + 1  # all tied top marks share the same rank (1)

        with result_col:
            st.markdown(f"""
            **Your adjusted mark is:** `{adjusted_student_mark:.2f}`  
            **Your rank is:** `{student_rank}` out of `{len(adjusted_marks)}` students.
            """)
        show_marker = True
    else:
        show_marker = False

# --- Visualization ---
sorted_indices = np.argsort(original_marks)
sorted_original = original_marks.iloc[sorted_indices].reset_index(drop=True)
sorted_adjusted = adjusted_marks[sorted_indices]

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(sorted_original, label="Original Marks", marker='o', linestyle='-', color='#FF6B6B')
ax.plot(sorted_adjusted, label="Adjusted Marks", marker='o', linestyle='--', color='#4D96FF')

if show_marker:
    ax.axhline(student_mark, color='#FF6B6B', linestyle=':', linewidth=2, label="Your Original Mark")
    ax.axhline(adjusted_student_mark, color='#4D96FF', linestyle=':', linewidth=2, label="Your Adjusted Mark")

ax.set_ylabel("Mark (0–5)")
ax.set_xlabel("Student Index")
ax.set_title("Distribution of Marks (Original vs Adjusted)")
ax.legend()
st.pyplot(fig)