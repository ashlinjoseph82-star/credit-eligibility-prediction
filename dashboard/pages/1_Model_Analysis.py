import streamlit as st
import pandas as pd
import os
import sys

# --------------------------------------------------
# Ensure src imports work inside Streamlit
# --------------------------------------------------
sys.path.append(os.path.abspath("."))

# 👉 EDA MODULE IMPORT
from ml.eda import show_eda
from src.evaluate_model import evaluate_all_models

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
    evaluated on unseen test data before selecting a final model for deployment.
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
# TRAINED MODEL FILES
# ==================================================
st.subheader("🧠 Trained Models Available")

MODEL_DIR = "models"

if not os.path.exists(MODEL_DIR):
    st.error("Models directory not found.")
else:
    model_files = [f for f in os.listdir(MODEL_DIR) if f.endswith(".pkl")]

    if not model_files:
        st.warning("No trained model files found.")
    else:
        model_df = pd.DataFrame({
            "Model File": model_files,
            "Status": ["Ready for inference"] * len(model_files)
        })
        st.dataframe(model_df, use_container_width=True)

st.caption(
    "All trained models are stored persistently and can be reused for inference."
)

st.divider()

# ==================================================
# MODEL PERFORMANCE COMPARISON (REAL METRICS)
# ==================================================
st.subheader("📊 Model Performance Comparison")

try:
    results = evaluate_all_models()
    performance_df = pd.DataFrame(results)

    st.dataframe(
        performance_df.style.highlight_max(
            subset=["accuracy", "precision", "recall"],
            color="#d4edda"
        ),
        use_container_width=True
    )

    best_model = performance_df.sort_values(
        by="accuracy", ascending=False
    ).iloc[0]

    st.caption(
        f"**{best_model['model']}** achieved the best overall test-set performance."
    )

except Exception as e:
    st.error("Failed to evaluate models.")
    st.code(str(e))
    st.stop()

st.divider()

# ==================================================
# MODEL SELECTION DECISION
# ==================================================
st.subheader("✅ Model Selected for Deployment")

st.success(
    f"""
    **{best_model['model']}** was selected as the deployed model due to
    superior test-set accuracy and a balanced precision–recall tradeoff.
    """
)

st.write(
    """
    Logistic Regression provided interpretability, and Decision Trees captured
    non-linear academic relationships. However, the Random Forest ensemble
    demonstrated stronger generalization by aggregating multiple decision trees.
    """
)

st.divider()

# ==================================================
# DEPLOYED MODEL METRICS (REAL)
# ==================================================
st.subheader("🚀 Deployed Model Performance")

c1, c2, c3 = st.columns(3)
c1.metric("Accuracy", f"{best_model['accuracy']:.2f}")
c2.metric("Precision", f"{best_model['precision']:.2f}")
c3.metric("Recall", f"{best_model['recall']:.2f}")

st.divider()

# ==================================================
# EXPLORATORY DATA ANALYSIS (EDA)
# ==================================================
st.subheader("📊 Exploratory Data Analysis")

st.caption(
    "This section provides insights into the dataset used for training the models, "
    "supporting feature selection and model design decisions."
)

try:
    show_eda()
except Exception as e:
    st.warning("EDA could not be loaded.")
    st.code(str(e))

st.divider()

# ==================================================
# DISCLAIMER
# ==================================================
st.subheader("⚠️ Important Note")

st.info(
    """
    Machine learning predictions are **advisory in nature** and are designed
    to complement official academic audits. This system functions as an
    early-warning tool to help students identify potential graduation risks
    well in advance.
    """
)
