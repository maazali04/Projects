# Student Grade Prediction Using Linear Regression

## Project Overview

**Project Type:** Supervised Regression  
**Model:** Linear Regression (scikit-learn)  
**Level:** Applied Machine Learning (Foundational)

The objective of this project is to predict a student’s **FinalGrade** based on academic, behavioral, and contextual features using a Linear Regression model. Beyond prediction, the project emphasizes correct data handling, modeling assumptions, and rigorous evaluation.

---

## Dataset Description

The dataset contains synthetic student performance data with the following characteristics:

* Academic indicators (previous grades, study hours)
* Behavioral factors (attendance, extracurricular activities)
* Contextual attributes (parental support, online classes)

⚠️ **Important Note:**  
The dataset is synthetic, intentionally noisy, and includes missing values and invalid entries. It is designed primarily for data cleaning and analysis practice rather than predictive performance.

### Target Variable

* **FinalGrade** (continuous numerical variable)

---

## Problem Framing

This task is formulated as a regression problem. Linear Regression is selected under the assumption that the target variable may be expressed as an approximately linear function of the input features. This choice allows for interpretability and clear evaluation of model assumptions.

---

## Data Preparation

### Data Cleaning

* Removed non-informative identifier columns (StudentID, Name)
* Dropped rows with missing target values
* Applied median imputation for numerical features
* Applied mode imputation for categorical features
* Corrected invalid values (negative study hours, attendance > 100%)

### Exploratory Data Analysis

* Descriptive statistics revealed impossible values and wide variance
* Boxplots confirmed the presence of extreme and invalid outliers
* Correlation analysis was restricted to numerical features only to avoid misleading interpretations

---

## Feature Engineering

* Categorical variables were encoded using one-hot encoding
* All features were converted to numerical format
* Feature scaling was applied **after** train–test split to prevent data leakage

---

## Model Training

The dataset was split into training and testing sets (80/20 split). A Linear Regression model from scikit-learn was trained on the scaled training data and evaluated on unseen test data.

---

## Model Evaluation

* **R² Score:** −0.0298  
* **Mean Squared Error (MSE):** 94.59

### Interpretation

The Actual vs. Predicted plot reveals clear underfitting. While actual grades span a wide range (approximately 60–95), the model’s predictions are tightly clustered around the mean (~80). This confirms that the available features lack sufficient predictive power to move the model’s estimates away from the average.

---

## Conclusion

Although the linear regression model was implemented and evaluated correctly, it performs poorly due to the nature of the dataset. The data is synthetic, intentionally noisy, and does not contain a meaningful linear relationship between the features and the target variable.

This project highlights a fundamental principle of machine learning:

> **Model performance is constrained by data quality and underlying structure.**

The project is therefore concluded at this stage. Further optimization on this dataset is not scientifically justified. The same modeling pipeline should be applied to a real-world dataset to meaningfully assess the effectiveness of Linear Regression.

---

## Key Takeaway

This project demonstrates not just how to build a regression model, but how to critically evaluate when modeling assumptions fail and why poor results can still represent a correct and valuable outcome.
