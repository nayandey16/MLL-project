import streamlit as st
import pandas as pd
import joblib
import numpy as np

# -------------------------
# 💠 Background (Same Dark Orange + Blue Mix)
# -------------------------
st.set_page_config(page_title="Loan Approval Prediction", layout="centered")
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

# Try to load model & scaler if present (kept for future use)
try:
    model = joblib.load("model.pkl")
    scaler = joblib.load("scaler.pkl")
except Exception:
    model = None
    scaler = None

# Mappings (kept for consistency)
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
    Gender = st.selectbox("Gender", ["Male", "Female"], index=1)
    Marriage = st.selectbox("Marital Status", ["Married", "Not Married"], index=0)
    no_of_dep = st.slider("Number of Dependents", 0, 3, value=0)
    grad = st.selectbox("Education Level", ["Graduated", "Not Graduated"], index=1)

with right:
    self_emp = st.selectbox("Self Employed?", ["Yes", "No"], index=1)
    Loan_Amount = st.slider("Loan Amount (in thousand TK)", 0, 1000, value=0)
    Property_Area = st.selectbox("Property Area", ["Urban", "Semiurban", "Rural"], index=0)
    Total_Income = st.slider("Total Income (monthly, TK)", 0, 10000, value=0)  # highest = 10000 as requested

st.markdown("---")
st.markdown("**Bank-style decision logic used:** EMI estimated (5 years @10% p.a.), compute monthly EMI → DTI = EMI / Total_Income. Then score with other factors (married, property, education, employment, dependents).")

# -------------------------
# Bank-style helper functions
# -------------------------
def calculate_emi(principal_thousand, annual_rate=10.0, tenure_years=5):
    """
    principal_thousand: loan amount entered as 'thousand TK'
    returns EMI in TK/month
    """
    P = principal_thousand * 1000.0  # convert to TK
    r = annual_rate / 12.0 / 100.0
    n = tenure_years * 12
    if P <= 0:
        return 0.0
    emi = (P * r * (1 + r)**n) / ((1 + r)**n - 1)
    return emi

def decision_by_rules(emi, total_income, gender, married, dependents, education, self_emp, property_area):
    """
    Returns (approve_bool, score, details_dict)
    """
    details = {}
    # avoid division by zero
    if total_income <= 0:
        dti = float('inf')
    else:
        dti = emi / total_income

    details['EMI'] = round(emi, 2)
    details['DTI_percent'] = round(dti * 100, 2)

    # scoring
    score = 0

    # 1) DTI is the most important: prefer <= 40%
    if dti <= 0.40:
        score += 3
        details['DTI_flag'] = "Good (<=40%)"
    elif dti <= 0.50:
        score += 1
        details['DTI_flag'] = "Borderline (40-50%)"
    else:
        details['DTI_flag'] = "High (>50%)"

    # 2) Total income importance
    if total_income >= 7000:
        score += 2
        details['Income_flag'] = "Strong"
    elif total_income >= 4000:
        score += 1
        details['Income_flag'] = "Moderate"
    else:
        details['Income_flag'] = "Weak"

    # 3) Property area
    if property_area == "Urban":
        score += 1
        details['Property_flag'] = "Urban (Good collateral value)"
    elif property_area == "Semiurban":
        score += 0
        details['Property_flag'] = "Semiurban (Neutral)"
    else:
        score -= 1
        details['Property_flag'] = "Rural (Lower collateral value)"

    # 4) Marital status (slight positive)
    if married == "Married":
        score += 1
        details['Marriage_flag'] = "Married (Slight stability bonus)"
    else:
        details['Marriage_flag'] = "Not Married"

    # 5) Education
    if education == "Graduated":
        score += 1
        details['Education_flag'] = "Graduate (Slight bonus)"
    else:
        details['Education_flag'] = "Not Graduate"

    # 6) Employment type
    if self_emp == "No":
        score += 1
        details['Employment_flag'] = "Salaried (Stable income)"
    else:
        score -= 0  # neutral but could require docs
        details['Employment_flag'] = "Self Employed (Requires verification)"

    # 7) Dependents
    if dependents == 0:
        score += 1
        details['Dependents_flag'] = "0 (Lower household burden)"
    elif dependents == 1:
        score += 0
        details['Dependents_flag'] = "1 (Neutral)"
    else:
        score -= 1
        details['Dependents_flag'] = f"{dependents} (Higher burden)"

    details['score'] = score

    # Decision threshold:
    # score >= 4 => approve, score 2-3 => maybe review (we'll treat as reject but show explanation),
    # score <2 => reject
    approve = score >= 4 and dti != float('inf')

    return approve, score, details

# -------------------------
# Prediction Button
# -------------------------
if st.button("🔍 Predict Loan Status"):

    emi = calculate_emi(Loan_Amount, annual_rate=10.0, tenure_years=5)
    approve, score, details = decision_by_rules(
        emi=emi,
        total_income=Total_Income,
        gender=Gender,
        married=Marriage,
        dependents=no_of_dep,
        education=grad,
        self_emp=self_emp,
        property_area=Property_Area
    )

    # Show key diagnostics
    st.markdown("### 🔎 Diagnostic")
    col1, col2, col3 = st.columns(3)
    col1.metric("Estimated EMI (TK/month)", f"{details['EMI']:,}")
    col2.metric("DTI (%)", f"{details['DTI_percent']}%")
    col3.metric("Score", f"{details['score']} / 8")

    st.markdown("#### Details")
    st.write(pd.DataFrame({
        "Factor": [
            "DTI status", "Income status", "Property", "Marital", "Education", "Employment", "Dependents"
        ],
        "Evaluation": [
            details.get('DTI_flag',''),
            details.get('Income_flag',''),
            details.get('Property_flag',''),
            details.get('Marriage_flag',''),
            details.get('Education_flag',''),
            details.get('Employment_flag',''),
            details.get('Dependents_flag',''),
        ]
    }))

    st.markdown("---")
    if approve:
        st.success("✅ Congratulations! Your Loan is Approved.")
        st.info("Reason: DTI acceptable and combined score meets bank's minimum criteria.")
    else:
        # give constructive message
        if details['DTI_flag'].startswith("High"):
            st.error("❌ Sorry! Your Loan is Rejected due to high DTI (monthly EMI too high vs income).")
        else:
            st.error("❌ Sorry! Your Loan is Rejected based on the bank-rule evaluation.")
            st.warning("Tip: increase total income, reduce requested loan, choose better collateral (Urban), or reduce dependents.")

# Optional: show link to original notebook (local path)
st.markdown("---")
st.markdown("**Notebook source (local):** `/mnt/data/Loan_Approval_Prediction.ipynb`")
