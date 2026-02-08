import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==================================================
# DATABASE CONNECTION
# ==================================================
DB_PATH = "students.db"

def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM students", conn)
    conn.close()
    return df

# ==================================================
# MAIN EDA FUNCTION
# ==================================================
def show_eda():
    st.subheader("📊 Exploratory Data Analysis (EDA)")

    df = load_data()

    if df.empty:
        st.warning("No data found in the database.")
        return

    # ==================================================
    # DATA OVERVIEW
    # ==================================================
    st.markdown("### 📄 Dataset Overview")
    st.dataframe(df.head(), use_container_width=True)

    st.markdown(
        f"""
        **Total Records:** {len(df)}  
        **Total Features:** {df.shape[1]}
        """
    )

    st.divider()

    # ==================================================
    # TARGET DISTRIBUTION
    # ==================================================
    if "graduation_risk" in df.columns:
        st.markdown("### 🎯 Graduation Risk Distribution")

        fig, ax = plt.subplots()
        sns.countplot(
            data=df,
            x="graduation_risk",
            palette="Reds",
            ax=ax
        )
        ax.set_xlabel("Risk Category")
        ax.set_ylabel("Number of Students")

        st.pyplot(fig)

        st.info(
            "This plot shows how students are distributed across risk categories. "
            "Class imbalance is important when evaluating model performance."
        )

        st.divider()

    # ==================================================
    # CREDIT DISTRIBUTION
    # ==================================================
    credit_cols = [
        "core_credits",
        "ge_credits",
        "sip_credits",
        "iip_credits",
        "ri_credits"
    ]

    available_cols = [c for c in credit_cols if c in df.columns]

    if available_cols:
        st.markdown("### 📚 Credit Distribution")

        fig, ax = plt.subplots(figsize=(8, 4))
        df[available_cols].boxplot(ax=ax)
        ax.set_ylabel("Credits")
        ax.set_title("Credit Spread Across Categories")

        st.pyplot(fig)

        st.info(
            "Boxplots help identify credit imbalance and outliers, "
            "which may strongly influence graduation risk."
        )

        st.divider()

    # ==================================================
    # CORRELATION HEATMAP
    # ==================================================
    st.markdown("### 🔗 Feature Correlation")

    numeric_df = df.select_dtypes(include=["int64", "float64"])

    if numeric_df.shape[1] > 1:
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.heatmap(
            numeric_df.corr(),
            annot=True,
            cmap="coolwarm",
            fmt=".2f",
            ax=ax
        )
        ax.set_title("Correlation Between Numeric Features")

        st.pyplot(fig)

        st.info(
            "Correlation analysis helps understand which academic factors "
            "are most related to graduation risk."
        )

    # ==================================================
    # EDA SUMMARY
    # ==================================================
    st.success(
        """
        ✅ **EDA Summary**
        - Identified risk distribution across students  
        - Observed credit imbalances and variability  
        - Analysed feature correlations for model relevance  
        
        These insights justify feature selection and model choice.
        """
    )
