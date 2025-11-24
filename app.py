import streamlit as st
import numpy as np
import pickle

# Load model & scaler
model = pickle.load(open('model.pkl', 'rb'))
scaler = pickle.load(open('scaler.pkl', 'rb'))

st.title("🏦 Loan Approval Prediction System")

st.write("Fill the details below to check whether your loan will be approved.")

# ----- INPUT FORM -----
gender = st.selectbox("Gender", ("Male", "Female"))
married = st.selectbox("Married", ("Yes", "No"))
dependents = st.selectbox("Dependents", (0, 1, 2, 3))
education = st.selectbox("Education", ("Graduate", "Not Graduate"))
self_emp = st.selectbox("Self Employed", ("Yes", "No"))

loan_amount = st.number_input("Loan Amount", min_value=10, max_value=500, step=1)
property_area = st.selectbox("Property Area", ("Urban", "Semiurban", "Rural"))

applicant_income = st.number_input("Applicant Income", min_value=0, step=100)
coapplicant_income = st.number_input("Co-Applicant Income", min_value=0, step=100)

# Total Income feature
total_income = applicant_income + coapplicant_income

# ----- ENCODING -----
gender = 1 if gender == "Male" else 0
married = 1 if married == "Yes" else 0
education = 1 if education == "Graduate" else 0
self_emp = 1 if self_emp == "Yes" else 0

property_mapping = {"Urban": 2, "Semiurban": 1, "Rural": 0}
property_area = property_mapping[property_area]

# Prepare input data array
input_data = np.array([[gender, married, dependents, education, self_emp,
                        loan_amount, property_area, total_income]])

# Scale the input
scaled_data = scaler.transform(input_data)

# ----- PREDICT -----
if st.button("Check Loan Approval"):
    prediction = model.predict(scaled_data)[0]

    if prediction == 1:
        st.success("🎉 **Loan Approved!**")
    else:
        st.error("❌ **Loan Rejected.**")
