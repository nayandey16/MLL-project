import streamlit as st
import pandas as pd
import joblib

# -------------------------
# 💠 Background (Same)
# -------------------------
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(90deg, rgb(199,114,21), rgb(29,52,97));
        background-size: cover;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: white;'>🏦 Loan Approval Prediction</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: white;'>An Intelligent System to Check Loan Eligibility</h4>", unsafe_allow_html=True)

# Load model & scaler (kept but not used for forced condition)
model = joblib.load("model.pkl")
scaler = joblib.load("scaler.pkl")

# -------------------------
# LAYOUT
# -------------------------
left, right = st.columns(2)

with left:
    Gender = st.selectbox("Gender", ["Male", "Female"])
    Marriage = st.selectbox("Marital Status", ["Married", "Not Married"])
    no_of_dep = st.slider("Number of Dependents", 0, 3)
    grad = st.selectbox("Education Level", ["Graduated", "Not Graduated"])

with right:
    self_emp = st.selectbox("Self Employed?", ["Yes", "No"])
    Loan_Amount = st.slider("Loan Amount (×1000 TK)", 0, 80)  # max 80k
    Property_Area = st.selectbox("Property Area", ["Urban", "Semiurban", "Rural"])
    Total_Income = st.slider("Total Income (×1000 TK)", 0, 10)  # max 10k

# -------------------------
# Custom Approval Logic
# -------------------------
if st.button("🔍 Predict Loan Status"):

    # -------------------------
    # Dependents scoring
    # -------------------------
    dep_score = {0: 3, 1: 2, 2: 1, 3: 0}[no_of_dep]  # higher better

    # -------------------------
    # Education & Self Employed
    # -------------------------
    edu_score = 2 if grad == "Graduated" else 1
    emp_score = 2 if self_emp == "Yes" else 1

    # -------------------------
    # Marital & Property
    # -------------------------
    marriage_score = 2 if Marriage == "Married" else 1
    prop_score = {"Urban": 2, "Semiurban": 1, "Rural": 0}[Property_Area]

    # -------------------------
    # Income vs Loan check
    # -------------------------
    loan_amount_real = Loan_Amount * 1000  # convert to TK
    total_income_real = Total_Income * 1000
    income_condition = total_income_real >= 0.4 * loan_amount_real  # 40% rule

    # -------------------------
    # Total score
    # -------------------------
    total_score = dep_score + edu_score + emp_score + marriage_score + prop_score

    # Approval thresholds
    if total_score >= 8 and income_condition and loan_amount_real <= 80000:
        st.success("✅ Congratulations! Your Loan is Approved.")
    else:
        st.error("❌ Sorry! Your Loan is Rejected.")

    # -------------------------
    # Optional: Show details
    # -------------------------
    st.markdown(f"**Score Details:** Dependents({dep_score}) + Education({edu_score}) + Self Employed({emp_score}) + Marriage({marriage_score}) + Property({prop_score}) = **{total_score}**")
    st.markdown(f"**Income vs Loan Check:** Total Income = {total_income_real} TK, Loan = {loan_amount_real} TK, Condition Met? {'✅' if income_condition else '❌'}")
