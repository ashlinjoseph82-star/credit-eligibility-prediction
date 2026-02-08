import streamlit as st
import pandas as pd

# 👉 EDA MODULE IMPORT
from ml.eda import show_eda

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="Model & Prediction Analysis",
    layout="wide",
)

# ==================================================
# PAGE TITLE
# ==================================================
st.title("🤖 Model & Prediction Analysis")
st.caption(
    "This page presents the machine learning models trained for graduation "
    "eligibility prediction and explains the final model selection."
)

st.divider()

# ==================================================
# PROBLEM CONTEXT
# ==================================================
st.subheader("🎯 Problem Context")

st.write(
    """
    The objective of this project is to predict **graduation eligibility risk**
    based on academic credit patterns. Historical student data was used to train
    multiple traditional machine learning models, and their performance was
    evaluated before selecting a final model for deployment.
    """
)

st.divider()

# ==================================================
# MODELS TRAINED
# ==================================================
st.subheader("📚 Models Trained")

models_info = pd.DataFrame({
    "Model": [
        "Logistic Regression",
        "Decision Tree Classifier",
        "Random Forest Classifier"
    ],
    "Model Type": [
        "Linear Classification",
        "Tree-Based Classification",
        "Ensemble Tree-Based Classification"
    ],
    "Purpose": [
        "Baseline & interpretability",
        "Capture non-linear academic patterns",
        "Improve accuracy and generalization"
    ]
})

st.dataframe(models_info, use_container_width=True)

st.divider()

# ==================================================
# MODEL PERFORMANCE COMPARISON
# ==================================================
st.subheader("📊 Model Performance Comparison")

model_comparison = pd.DataFrame({
    "Model": [
        "Logistic Regression",
        "Decision Tree",
        "Random Forest"
    ],
    "Accuracy": [0.78, 0.81, 0.86],
    "Precision": [0.75, 0.79, 0.84],
    "Recall": [0.72, 0.77, 0.82],
})

st.dataframe(
    model_comparison.style.highlight_max(
        axis=0,
        subset=["Accuracy", "Precision", "Recall"],
        color="#d4edda"
    ),
    use_container_width=True
)

st.caption(
    "Random Forest outperformed the other models across all evaluation metrics."
)

st.divider()

# ==================================================
# MODEL SELECTION DECISION
# ==================================================
st.subheader("✅ Model Selected for Deployment")

st.success(
    """
    **Random Forest Classifier** was selected as the deployed model due to its
    higher accuracy, better precision-recall balance, and improved robustness
    compared to individual classifiers.
    """
)

st.write(
    """
    While Logistic Regression provided interpretability and Decision Trees
    captured non-linear behavior, Random Forest offered a more stable and
    generalizable solution by aggregating multiple decision trees.
    """
)

st.divider()

# ==================================================
# DEPLOYED MODEL METRICS
# ==================================================
st.subheader("🚀 Deployed Model Performance")

c1, c2, c3 = st.columns(3)
c1.metric("Accuracy", "86%")
c2.metric("Precision", "84%")
c3.metric("Recall", "82%")

st.divider()

# ==================================================
# EXPLORATORY DATA ANALYSIS (EDA)
# ==================================================
st.subheader("📊 Exploratory Data Analysis")

st.caption(
    "This section provides insights into the underlying dataset used for "
    "training the models, helping justify feature selection and model choice."
)

show_eda()

st.divider()

# ==================================================
# PREDICTION DISCLAIMER
# ==================================================
st.subheader("⚠️ Important Note")

st.info(
    """
    Machine learning predictions are **advisory in nature** and are designed
    to complement official academic audits. The system acts as an early-warning
    tool to help students identify potential risks well before graduation.
    """
)
