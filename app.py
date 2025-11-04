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
    target_mean = st.slider("🎯 Adjusted Average", min_value=3.7, max_value=3.8, value=3.75, step=0.01,
                             help="Set the target average of adjusted marks")

with col3:
    target_pct_above_4 = st.slider("🔝 Maximum percentage of adjusted marks above 4", min_value=20, max_value=30,
                                    value=30, step=1,
                                    help="Maximum allowed percentage of adjusted marks ≥ 4") / 100

# --- Policy Description ---
st.markdown("""
MBS grade policy requires that the mean of the final marks (over 100) be between 74 and 76 (3.70 and 3.80 out of 5) and that the scores corresponding to H1 (4 out of 5) do not exceed 30%.  
The adjustment takes these criteria into account and adjusts marks while preserving the original z-scores.  

⚠️ *Please note that although these distributions are indicative, they may change at the end of the subject because there are some zero marks which may change after the consensus date.*
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
    " ": ["Original", "Adjusted"],
    "Mean": [f"{mean_orig:.2f}", f"{np.mean(adjusted_marks):.2f}"],
    "Std. Dev": [f"{np.std(original_marks):.2f}", f"{np.std(adjusted_marks):.2f}"],
})

# --- Layout: Summary + Student Lookup ---
col_summ, col_rank = st.columns(2)

with col_summ:
    st.markdown("### 📋 Summary")
    st.markdown(
        f"""
        <div style='width:100%; overflow-x:auto;'>
            {summary_df.to_html(index=False, justify='center')}
        </div>
        """,
        unsafe_allow_html=True
    )

with col_rank:
    st.markdown("### 🔍 Find Your Adjusted Mark and Rank")
    student_mark = st.number_input("Enter your original quiz mark", min_value=0.0, max_value=5.0, step=0.01)
    show_lookup = student_mark != 0.0  # or however you'd like to trigger it

    if show_lookup:
        z = (student_mark - mean_orig) / std_orig
        adjusted_student_mark = round(z * target_std + target_mean, 2)
        student_rank = int(np.sum(adjusted_marks > adjusted_student_mark) + 1)
        st.write(f"**Your adjusted mark is:** {adjusted_student_mark:.2f}")
        st.write(f"**Your rank is:** {student_rank} out of {len(adjusted_marks)}")

# --- Visualization ---
sorted_indices = np.argsort(original_marks)
sorted_original = original_marks.iloc[sorted_indices].reset_index(drop=True)
sorted_adjusted = adjusted_marks[sorted_indices]

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(sorted_original, label="Original Marks", marker='o', linestyle='-', color='#2c7bb6')
ax.plot(sorted_adjusted, label="Adjusted Marks", marker='o', linestyle='--', color='#fdae61')

if show_lookup:
    # Horizontal lines for user marks
    ax.axhline(student_mark, color='#2c7bb6', linestyle=':', linewidth=2, label="Your Original Mark")
    ax.axhline(adjusted_student_mark, color='#fdae61', linestyle=':', linewidth=2, label="Your Adjusted Mark")

ax.set_ylabel("Mark (0–5)")
ax.set_xlabel("Student Index")
ax.set_title("Distribution of Marks (Original vs Adjusted)")
ax.legend()
st.pyplot(fig)