import streamlit as st
import pandas as pd
import joblib

# -------------------------
# 💠 Background (Same Dark Orange + Blue Mix)
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

# Load model & scaler
model = joblib.load("model.pkl")
scaler = joblib.load("scaler.pkl")

# Mappings
gender_map = {"Male": 1, "Female": 0}
married_map = {"Married": 1, "Not Married": 0}
edu_map = {"Graduated": 1, "Not Graduated": 0}
emp_map = {"Yes": 1, "No": 0}
prop_map = {"Urban": 2, "Semiurban": 1, "Rural": 0}

# -------------------------
# LAYOUT (Left 4 – Right 4)
# -------------------------
left, right = st.columns(2)

with left:
    Gender = st.selectbox("Gender", ["Male", "Female"])
    Marriage = st.selectbox("Marital Status", ["Married", "Not Married"])
    no_of_dep = st.slider("Number of Dependents", 0, 3)
    grad = st.selectbox("Education Level", ["Graduated", "Not Graduated"])

with right:
    self_emp = st.selectbox("Self Employed?", ["Yes", "No"])
    Loan_Amount = st.slider("Loan Amount", 0, 1000)
    Property_Area = st.selectbox("Property Area", ["Urban", "Semiurban", "Rural"])
    Total_Income = st.slider("Total Income", 0, 10000)

# -------------------------
# Prediction Button
# -------------------------
if st.button("🔍 Predict Loan Status"):

    data = [[
        gender_map[Gender],
        married_map[Marriage],
        no_of_dep,
        edu_map[grad],
        emp_map[self_emp],
        Loan_Amount,
        prop_map[Property_Area],
        Total_Income,
    ]]

    df_input = pd.DataFrame(data, columns=[
        "Gender", "Married", "Dependents", "Education",
        "Self_Employed", "LoanAmount", "Property_Area", "Total_Income"
    ])

    df_scaled = scaler.transform(df_input)
    prediction = model.predict(df_scaled)[0]

    if prediction == 1:
        st.success("✅ Congratulations! Your Loan is Approved.")
    else:
        st.error("❌ Sorry! Your Loan is Rejected.")