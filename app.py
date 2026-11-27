
import streamlit as st
import csv
from pathlib import Path
from datetime import date

st.set_page_config(page_title="FitLife", page_icon="💪", layout="wide")

FILE = Path("fitness_data.csv")

def load_data():
    if FILE.exists():
        with open(FILE, "r", newline="") as f:
            return list(csv.DictReader(f))
    return []

def save_data(record):
    file_exists = FILE.exists()

    with open(FILE, "a", newline="") as f:
        fields = [
            "Date", "Steps", "Heart Rate",
            "Sleep Hours", "Calories", "Active Minutes"
        ]
        writer = csv.DictWriter(f, fieldnames=fields)

        if not file_exists:
            writer.writeheader()

        writer.writerow(record)


def calculate_wellness(steps, sleep, active, heart):
    step_score = min(steps / 10000, 1) * 40
    sleep_score = max(0, 1 - abs(sleep - 8) / 8) * 30
    active_score = min(active / 60, 1) * 20
    heart_score = 10 if 60 <= heart <= 100 else 5

    total = step_score + sleep_score + active_score + heart_score
    return round(total)

df = load_data()

st.title("💪 FitLife")
st.subheader("Fitness & Lifestyle Wellness Analytics System")

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Choose a page",
    ["Home", "Fitness Tracker", "Analytics"]
)

if page == "Home":
    st.header("Welcome to FitLife!")
    st.write("Your personal fitness tracking dashboard.")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Records", len(df))

    total_steps = sum(int(r["Steps"]) for r in df)
    col2.metric("Total Steps", total_steps)

    avg_sleep = (
        sum(float(r["Sleep Hours"]) for r in df) / len(df)
        if df else 0
    )
    col3.metric("Average Sleep", f"{avg_sleep:.1f} hours")

    st.success("Start tracking your daily fitness!")

elif page == "Fitness Tracker":
    st.header("📝 Daily Fitness Tracker")

    with st.form("fitness_form"):
        record_date = st.date_input("Date", value=date.today())
        steps = st.number_input("Steps", min_value=0, step=500)
        heart = st.number_input("Heart Rate (BPM)", 1, 250, 75)
        sleep = st.number_input("Sleep Hours", 0.0, 24.0, 8.0, 0.5)
        calories = st.number_input("Calories Burned", min_value=0)
        active = st.number_input("Active Minutes", min_value=0)

        submit = st.form_submit_button("Save Fitness Data")

    if submit:
        record = {
            "Date": str(record_date),
            "Steps": steps,
            "Heart Rate": heart,
            "Sleep Hours": sleep,
            "Calories": calories,
            "Active Minutes": active
        }

        save_data(record)
        st.success("Fitness data saved successfully!")
        st.rerun()

    if df:
        st.subheader("Your Fitness Records")
        st.write(df)
  
elif page == "Analytics":

    st.header("📊 Fitness Analytics")
    if df:
        total_steps = sum(int(r["Steps"]) for r in df)
        total_calories = sum(int(r["Calories"]) for r in df)
        avg_heart = sum(int(r["Heart Rate"]) for r in df) / len(df)

        scores = [
            calculate_wellness(
                int(r["Steps"]),
                float(r["Sleep Hours"]),
                int(r["Active Minutes"]),
                int(r["Heart Rate"])
            )
            for r in df
        ]

        avg_score = sum(scores) / len(scores)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Steps", total_steps)
        col2.metric("Total Calories", total_calories)
        col3.metric("Average Heart Rate", f"{avg_heart:.0f} BPM")

        st.divider()

        st.subheader("🏆 Daily Wellness Score")

        st.metric("Average Wellness Score", f"{avg_score:.0f}/100")

        st.progress(avg_score / 100)

        for i, r in enumerate(df):
            st.write(
                f'{r["Date"]} — Wellness Score: {scores[i]}/100'
            )

        st.divider()

        st.subheader("Daily Steps")
        for r in df:
            st.write(r["Date"], "-", f'{r["Steps"]} steps')
            st.progress(min(int(r["Steps"]) / 10000, 1.0))

    else:
        st.warning("No fitness data available.")
