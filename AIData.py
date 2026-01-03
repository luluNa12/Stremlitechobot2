import streamlit as st
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import mean_squared_error, accuracy_score

st.title("Upload Data → Train Model → Show Results")

uploaded = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded is not None:
    df = pd.read_csv(uploaded)
    st.write("Preview of your data:")
    st.dataframe(df.head())

    st.write("Pick your target column (the column you want to predict):")
    target_col = st.selectbox("Target column", df.columns)

    # Basic cleaning: keep only numeric columns for a simple starter model
    numeric_df = df.select_dtypes(include=["number"]).dropna()

    if target_col not in numeric_df.columns:
        st.error("For this simple demo, the target column must be numeric and have no missing values.")
    else:
        X = numeric_df.drop(columns=[target_col])
        y = numeric_df[target_col]

        if X.shape[1] == 0:
            st.error("You need at least one numeric feature column besides the target.")
        else:
            test_size = st.slider("Test set size", 0.1, 0.5, 0.2, 0.05)
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )

            st.write("Choose model type:")
            model_type = st.selectbox("Model", ["Linear Regression (numeric target)", "Logistic Regression (binary 0/1 target)"])

            if model_type.startswith("Linear"):
                model = LinearRegression()
                model.fit(X_train, y_train)
                preds = model.predict(X_test)
                mse = mean_squared_error(y_test, preds)

                st.write("Model trained.")
                st.write("Mean Squared Error (MSE):", mse)
                results = pd.DataFrame({"Actual": y_test.values, "Predicted": preds})
                st.write("Sample predictions:")
                st.dataframe(results.head(10))

            else:
                # Logistic regression needs binary 0/1 target
                unique_vals = sorted(y.unique())
                if unique_vals != [0, 1]:
                    st.error("Logistic Regression demo requires the target to be binary with values 0 and 1.")
                else:
                    model = LogisticRegression(max_iter=1000)
                    model.fit(X_train, y_train)
                    preds = model.predict(X_test)
                    acc = accuracy_score(y_test, preds)

                    st.write("Model trained.")
                    st.write("Accuracy:", acc)
                    results = pd.DataFrame({"Actual": y_test.values, "Predicted": preds})
                    st.write("Sample predictions:")
                    st.dataframe(results.head(10))
