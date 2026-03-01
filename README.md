# Smart System for Academic Progression Analysis and Graduation Delay Prediction

This project predicts graduation delay risk for university students based on structured, category-wise credit completion within a credit-based academic framework.

The system functions as an academic decision-support tool that analyzes progression patterns and estimates the probability of delayed graduation using traditional machine learning models. It enables early risk identification beyond deterministic eligibility checks.

---

## Project Objectives

- Assess whether a student is currently on track for graduation  
- Estimate the probability of graduation delay  
- Categorize risk levels (Low, Medium, High)  
- Provide early warnings based on academic progression patterns  
- Support students and administrators with data-driven insights  

---

## System Overview

The project follows a modular, production-oriented machine learning workflow:

- Synthetic academic data generation  
- SQLite-based structured data storage  
- Data preprocessing and model training pipelines  
- Evaluation and comparison of traditional ML models  
- Version-controlled model storage and metadata tracking  
- FastAPI-based prediction and retraining endpoints  
- React-based interactive dashboard for analysis and predictions  
- Full frontend–backend integration  

The system emphasizes maintainability, lifecycle management, and structured deployment practices.

---

## Machine Learning Models

The following traditional models were implemented and evaluated:

- Logistic Regression  
- Decision Tree  
- Random Forest  
- Gradient Boosting  
- XGBoost  

Models are evaluated using:

- Accuracy  
- Precision  
- Recall  
- F1-score  

The best-performing model is automatically selected for deployment within the prediction pipeline.

---

## Dashboard Features

The interactive frontend allows users to:

- View category-wise credit completion summaries  
- Analyze internship and course failure indicators  
- Compare model performance metrics  
- Generate graduation delay predictions  
- View probability-based risk levels (Low / Medium / High)  
- Monitor model version information  

The system distinguishes between rule-based eligibility checks and predictive risk estimation.

---

## Technology Stack

### Backend
- Python  
- FastAPI  
- Scikit-learn  
- XGBoost  
- SQLite  

### Frontend
- React (Vite + TypeScript)  
- Tailwind CSS  
- Recharts  

### Development
- Git & GitHub  
- Modular project structure  
- Version-controlled model lifecycle  

---

## Running the Project Locally

### Backend

```bash
cd Backend
pip install -r requirements.txt
uvicorn main:app --reload
