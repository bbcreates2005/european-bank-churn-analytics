import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="European Banking Churn Analytics",
    page_icon="🏦",
    layout="wide"
)

@st.cache_data
def load_data():
    return pd.read_csv("cleaned_bank_churn.csv")

df = load_data()

# Sidebar Segment Filters
st.sidebar.header("🔍 Segment Filters")

selected_geo = st.sidebar.multiselect(
    "Geography (Country)",
    options=df["Geography"].unique().tolist(),
    default=df["Geography"].unique().tolist()
)

selected_age = st.sidebar.multiselect(
    "Age Group",
    options=['<30', '30-45', '46-60', '60+'],
    default=['<30', '30-45', '46-60', '60+']
)

selected_balance = st.sidebar.multiselect(
    "Balance Segment",
    options=['Zero-balance', 'Low-balance', 'High-balance'],
    default=['Zero-balance', 'Low-balance', 'High-balance']
)

selected_activity = st.sidebar.multiselect(
    "Activity Status",
    options=['Active', 'Inactive'],
    default=['Active', 'Inactive']
)

# Apply Dynamic Filters
filtered_df = df[
    (df["Geography"].isin(selected_geo)) &
    (df["Age_Group"].isin(selected_age)) &
    (df["Balance_Segment"].isin(selected_balance)) &
    (df["Activity_Status"].isin(selected_activity))
]

st.title("🏦 Customer Segmentation & Churn Pattern Analytics in European Banking")
st.markdown("Interactive executive dashboard analyzing churn risk across European regions, customer demographics, and high-value accounts.")

if filtered_df.empty:
    st.warning("No customers match the selected filter combination. Please adjust your sidebar filters.")
    st.stop()

# MODULE 1: OVERALL CHURN SUMMARY (DYNAMIC KPIs)
st.subheader("📊 Module 1: Overall Churn Summary & Dynamic KPIs")

total_cust = len(filtered_df)
churned_cust = int(filtered_df["Exited"].sum())
overall_churn = (churned_cust / total_cust) * 100

hv_df = filtered_df[filtered_df["Balance_Segment"] == "High-balance"]
hv_churn = (hv_df["Exited"].mean() * 100) if len(hv_df) > 0 else 0.0

balance_at_risk = filtered_df[filtered_df["Exited"] == 1]["Balance"].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Filtered Customers", f"{total_cust:,}")
col2.metric("Overall Churn Rate", f"{overall_churn:.2f}%", f"{churned_cust:,} exited", delta_color="inverse")
col3.metric("High-Value Churn Ratio", f"{hv_churn:.2f}%", "Balance > $100k", delta_color="inverse")
col4.metric("Total Balance at Risk", f"${balance_at_risk:,.0f}", "Churned accounts", delta_color="inverse")

st.divider()

# MODULE 2: GEOGRAPHY-WISE CHURN VISUALIZATION
st.subheader("🌍 Module 2: Geography-Wise Churn & Engagement Risk")
c1, c2 = st.columns(2)

with c1:
    geo_df = filtered_df.groupby("Geography", observed=False).agg(
        Total=("Exited", "count"),
        Churned=("Exited", "sum"),
        Churn_Rate=("Exited", lambda x: round(x.mean() * 100, 2))
    ).reset_index()
    fig_geo = px.bar(
        geo_df, x="Geography", y="Churn_Rate", text="Churn_Rate",
        color="Geography", title="Churn Rate (%) by Country",
        labels={"Churn_Rate": "Churn Rate (%)"}
    )
    fig_geo.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig_geo, use_container_width=True)

with c2:
    act_df = filtered_df.groupby(["Geography", "Activity_Status"], observed=False)["Exited"].mean().mul(100).reset_index()
    act_df.rename(columns={"Exited": "Churn_Rate"}, inplace=True)
    fig_act = px.bar(
        act_df, x="Geography", y="Churn_Rate", color="Activity_Status", barmode="group",
        title="Engagement Drop Indicator: Active vs. Inactive Churn (%)",
        labels={"Churn_Rate": "Churn Rate (%)"}
    )
    st.plotly_chart(fig_act, use_container_width=True)

st.divider()

# MODULE 3: AGE & TENURE CHURN COMPARISON
st.subheader("👥 Module 3: Age & Tenure Churn Comparison")
c3, c4 = st.columns(2)

with c3:
    age_df = filtered_df.groupby("Age_Group", observed=False)["Exited"].mean().mul(100).reset_index()
    age_df.rename(columns={"Exited": "Churn_Rate"}, inplace=True)
    fig_age = px.bar(
        age_df, x="Age_Group", y="Churn_Rate", text="Churn_Rate",
        title="Churn Rate (%) by Age Group", color_discrete_sequence=["#6366F1"]
    )
    fig_age.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig_age, use_container_width=True)

with c4:
    tenure_df = filtered_df.groupby("Tenure_Group", observed=False)["Exited"].mean().mul(100).reset_index()
    tenure_df.rename(columns={"Exited": "Churn_Rate"}, inplace=True)
    fig_tenure = px.bar(
        tenure_df, x="Tenure_Group", y="Churn_Rate", text="Churn_Rate",
        title="Churn Rate (%) by Tenure Group", color_discrete_sequence=["#0EA5E9"]
    )
    fig_tenure.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig_tenure, use_container_width=True)

st.divider()

# MODULE 4: HIGH-VALUE CUSTOMER CHURN EXPLORER
st.subheader("💎 Module 4: High-Value Customer Churn Explorer & Drill-Down")
c5, c6 = st.columns([2, 1])

with c5:
    sample_plot = filtered_df.sample(n=min(1500, len(filtered_df)), random_state=42)
    fig_scatter = px.scatter(
        sample_plot, x="Balance", y="EstimatedSalary", color="Churn_Status",
        color_discrete_map={"Retained": "#94A3B8", "Churned": "#EF4444"},
        title="Salary vs. Account Balance Distribution (Churned vs. Retained)",
        hover_data=["Geography", "Age", "CreditScore", "NumOfProducts"]
    )
    fig_scatter.add_vline(x=100000, line_dash="dash", line_color="black", annotation_text="High-Balance ($100k)")
    st.plotly_chart(fig_scatter, use_container_width=True)

with c6:
    bal_summary = filtered_df.groupby("Balance_Segment", observed=False).agg(
        Customers=("Exited", "count"),
        Churned=("Exited", "sum"),
        Churn_Rate_Pct=("Exited", lambda x: round(x.mean() * 100, 2)),
        Total_Balance=("Balance", lambda x: f"${x.sum():,.0f}")
    ).reset_index()
    st.markdown("**Balance Segment Breakdown**")
    st.dataframe(bal_summary, use_container_width=True, hide_index=True)

with st.expander("🔎 Drill-Down View: Inspect High-Value Churned Customer Records"):
    high_risk_records = filtered_df[(filtered_df["Exited"] == 1) & (filtered_df["Balance"] > 100000)].sort_values(by="Balance", ascending=False)
    st.write(f"Showing {len(high_risk_records)} churned high-balance customers matching current filters:")
    st.dataframe(high_risk_records.head(100), use_container_width=True, hide_index=True)
