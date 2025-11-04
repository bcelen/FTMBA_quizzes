# Weekly Quiz Results Dashboard (FTMBA)

This interactive Streamlit app helps students visualize and understand the weekly quiz marks and how they are adjusted to meet grading policy requirements. It is designed for the FTMBA program at Melbourne Business School.

The app reads raw quiz data (CSV files) from this GitHub repository and dynamically:
- Calculates **adjusted marks** based on a target mean and maximum proportion of top marks (H1),
- Visualizes **raw vs adjusted distributions**,
- Lets students **look up their own adjusted marks and rank**, and
- Offers detailed control via sliders for instructors or students to explore different policy outcomes.

---

## 🔧 Features

- 📁 Weekly dropdown menu to load quiz CSVs (e.g., `week1.csv`, `week2.csv`, ...)
- 🎯 Sliders to set:
  - Adjusted mean (range: `3.70 – 3.80`)
  - Max % of adjusted marks ≥ 4 (range: `20% – 30%`)
- 📈 Graph: Distribution of Original vs Adjusted Marks
- 📋 Summary Table: Mean and Std. Dev for both
- 🔍 Student Tool:
  - Enter your original quiz mark
  - See your adjusted mark
  - See your class rank
  - Highlights your marks on the graph

---

## 📁 File Structure
FTMBA_quizzes/
│
├── week1.csv
├── week2.csv
├── …
├── app.py              # Streamlit app
└── README.md           # This file
CSV files must contain **only one column** of raw quiz marks (e.g., values between 0 and 5). Non-numeric values are ignored.

