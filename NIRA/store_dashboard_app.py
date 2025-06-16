import streamlit as st
import pandas as pd
from datetime import datetime

# Load data
payments = pd.read_csv("payments_cleaned.csv", parse_dates=['Date'])
maintenance = pd.read_csv("maintenance_cleaned.csv", parse_dates=['ReportedDate'])
utilities = pd.read_csv("utilities_cleaned.csv", parse_dates=['Date'])

st.set_page_config(page_title="Store Dashboard", layout="wide")
st.title("🏢 Water Store Operations Dashboard")

# Sidebar
view_option = st.sidebar.radio("Select View", ["Overview", "Maintenance Alerts", "Store Details"])

# Overview Section
if view_option == "Overview":
    st.subheader("🗓️ Revenue Summary")
    period = st.selectbox("Select Timeframe", ["Daily", "Weekly", "Monthly"])

    if period == "Daily":
        summary = payments.groupby(['Date', 'StoreID'])['Amount'].sum().reset_index()
    elif period == "Weekly":
        payments['Week'] = payments['Date'].dt.to_period('W').apply(lambda r: r.start_time)
        summary = payments.groupby(['Week', 'StoreID'])['Amount'].sum().reset_index().rename(columns={'Week': 'Date'})
    else:  # Monthly
        payments['Month'] = payments['Date'].dt.to_period('M').apply(lambda r: r.start_time)
        summary = payments.groupby(['Month', 'StoreID'])['Amount'].sum().reset_index().rename(columns={'Month': 'Date'})

    pivot = summary.pivot(index='Date', columns='StoreID', values='Amount').fillna(0)
    st.line_chart(pivot)

    st.subheader("🍽️ Product Market Share by Store")
    product_columns = [col for col in payments.columns if 'Shop' in col]
    store_choice = st.selectbox("Select Store", ["ShopA", "ShopB", "ShopC"])
    store_products = [col for col in product_columns if store_choice in col]

    product_sums = payments[store_products].sum().rename(lambda x: x.replace(f" {store_choice}", ""))
    st.plotly_chart(product_sums.plot.pie(autopct='%1.1f%%', title=f"{store_choice} Product Shares").get_figure())

# Maintenance Alerts
elif view_option == "Maintenance Alerts":
    st.subheader("⚠️ Stores Requiring Attention")
    pending = maintenance[maintenance['Status'] == 'Pending']
    if pending.empty:
        st.success("No pending issues. All systems good!")
    else:
        for idx, row in pending.iterrows():
            with st.expander(f"{row['StoreID']} - {row['MachineType']} ({row['Issue']}) on {row['ReportedDate'].date()}"):
                if st.button("Mark as Done", key=str(idx)):
                    maintenance.at[idx, 'Status'] = 'Done'
                    maintenance.at[idx, 'ResolvedDate'] = datetime.today().date()
                    st.success("Marked as done!")

# Store Details
elif view_option == "Store Details":
    st.subheader("🏠 Store Revenue & Usage")
    selected_store = st.selectbox("Choose a Store", ["ShopA", "ShopB", "ShopC"])
    store_data = payments[payments['StoreID'] == selected_store]
    st.write("### Revenue Records", store_data[['Date', 'Amount']].groupby('Date').sum())

    st.write("### Utility Usage")
    store_util = utilities[utilities['StoreID'] == selected_store]
    st.line_chart(store_util.set_index('Date')[['ElectricityUsed', 'WaterUsed']])

# Save updated maintenance data
maintenance.to_csv("maintenance_cleaned.csv", index=False)
