import streamlit as st
import pandas as pd

# ==============================
# LOAD DATA
# ==============================

FILE_PATH = r"D:\Agentic_AI\data\dummy_sales_data.xlsx"

df = pd.read_excel(FILE_PATH)
df['order_date'] = pd.to_datetime(df['order_date'])
df['month'] = df['order_date'].dt.to_period('M').astype(str)

# ==============================
# PAGE CONFIG
# ==============================

st.set_page_config(page_title="Sales Dashboard", layout="wide")
st.title("📊 Sales AI Dashboard")

# ==============================
# RESET BUTTON
# ==============================

if st.sidebar.button("🔄 Reset Filters"):
    st.session_state.clear()

# ==============================
# FILTERS
# ==============================

sales_rep = st.sidebar.multiselect(
    "Sales Rep",
    options=df['sales_rep'].unique(),
    default=df['sales_rep'].unique()
)

month = st.sidebar.multiselect(
    "Month",
    options=sorted(df['month'].unique()),
    default=sorted(df['month'].unique())
)

product = st.sidebar.multiselect(
    "Product",
    options=df['product'].unique(),
    default=df['product'].unique()
)

category = st.sidebar.multiselect(
    "Category",
    options=df['category'].unique(),
    default=df['category'].unique()
)

# ==============================
# TOP N FILTER
# ==============================

top_n = st.sidebar.slider("Top N Products", min_value=3, max_value=20, value=5)

# ==============================
# APPLY FILTER
# ==============================

filtered_df = df[
    (df['sales_rep'].isin(sales_rep)) &
    (df['month'].isin(month)) &
    (df['product'].isin(product)) &
    (df['category'].isin(category))
]

# ==============================
# KPI
# ==============================

total_sales = filtered_df['total_sales'].sum()
total_orders = filtered_df['order_id'].nunique()
avg_order = filtered_df['total_sales'].mean()
max_sales = filtered_df['total_sales'].max()

k1, k2, k3, k4 = st.columns(4)

k1.metric("💰 Total Sales", f"₹{total_sales:,.0f}")
k2.metric("📦 Orders", total_orders)
k3.metric("📊 Avg Order", f"₹{avg_order:,.0f}")
k4.metric("🔥 Max Sale", f"₹{max_sales:,.0f}")

st.markdown("---")

# ==============================
# PRODUCT (TOP N)
# ==============================

st.subheader("📦 Top Products")

product_sales = (
    filtered_df.groupby('product')['total_sales']
    .sum()
    .sort_values(ascending=False)
    .head(top_n)
)

st.bar_chart(product_sales)

# ==============================
# DRILL DOWN (PRODUCT LEVEL)
# ==============================

selected_product = st.selectbox("🔍 Drill Down by Product", ["All"] + list(df['product'].unique()))

if selected_product != "All":
    drill_df = filtered_df[filtered_df['product'] == selected_product]
    st.write(f"### Details for {selected_product}")
    st.dataframe(drill_df)
else:
    drill_df = filtered_df

# ==============================
# MONTHLY TREND
# ==============================

c1, c2 = st.columns(2)

with c1:
    st.subheader("📅 Monthly Sales")
    month_sales = drill_df.groupby('month')['total_sales'].sum()
    st.line_chart(month_sales)

with c2:
    st.subheader("👨‍💼 Sales Rep Performance")
    rep_sales = drill_df.groupby('sales_rep')['total_sales'].sum()
    st.bar_chart(rep_sales)

# ==============================
# DELIVERY STATUS
# ==============================

st.subheader("🚚 Delivery Status")

delivery_summary = drill_df.groupby('delivery_status').agg(
    order_count=('order_id', 'count'),
    total_sales=('total_sales', 'sum')
)

st.dataframe(delivery_summary)

# ==============================
# GROWTH TREND
# ==============================

st.subheader("📈 Sales Rep Growth Trend")

rep_month = drill_df.groupby(['month', 'sales_rep'])['total_sales'].sum().reset_index()
pivot = rep_month.pivot(index='month', columns='sales_rep', values='total_sales').fillna(0)

st.line_chart(pivot)

st.markdown("---")
st.subheader("🧠 AI Insights")

if not filtered_df.empty:

    # Top Product
    top_product = (
        filtered_df.groupby('product')['total_sales']
        .sum()
        .sort_values(ascending=False)
        .index[0]
    )

    # Top Sales Rep
    top_rep = (
        filtered_df.groupby('sales_rep')['total_sales']
        .sum()
        .sort_values(ascending=False)
        .index[0]
    )

    # Best Month
    top_month = (
        filtered_df.groupby('month')['total_sales']
        .sum()
        .sort_values(ascending=False)
        .index[0]
    )

    # Delivery Issue
    delayed_orders = filtered_df[filtered_df['days_to_deliver'] > 5].shape[0]

    # Discount Risk
    high_discount = filtered_df[filtered_df['discount_pct'] > 10].shape[0]

    # ==============================
    # DISPLAY INSIGHTS
    # ==============================

    c1, c2 = st.columns(2)

    with c1:
        st.info(f"""
📌 Top Product: **{top_product}**

👨‍💼 Top Sales Rep: **{top_rep}**

📅 Highest Sales Month: **{top_month}**
""")

    with c2:
        st.warning(f"""
🚚 Delayed Orders (>5 days): **{delayed_orders}**

💸 High Discount Orders (>10%): **{high_discount}**
""")

    # Final Observation
    st.success(f"""
📊 **Observation:**
Sales performance is driven by **{top_product}** and **{top_rep}**. 
Focus required on delivery delays and discount control.
""")

else:
    st.warning("No data available for selected filters")

import io

st.markdown("---")
st.subheader("📥 Download Data")

# Convert dataframe to Excel in memory
def convert_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Filtered_Data')
    return output.getvalue()

excel_data = convert_to_excel(filtered_df)

st.download_button(
    label="⬇️ Download Filtered Data (Excel)",
    data=excel_data,
    file_name="sales_filtered_data.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.markdown("---")
st.subheader("💬 Ask Questions (AI Query)")

query = st.text_input("Type your question:")

if query:

    q = query.lower()

    if "total sales" in q:
        result = filtered_df['total_sales'].sum()
        st.success(f"Total Sales: ₹{result:,.0f}")

    elif "top product" in q:
        result = (
            filtered_df.groupby('product')['total_sales']
            .sum()
            .sort_values(ascending=False)
            .index[0]
        )
        st.success(f"Top Product: {result}")

    elif "top sales rep" in q:
        result = (
            filtered_df.groupby('sales_rep')['total_sales']
            .sum()
            .sort_values(ascending=False)
            .index[0]
        )
        st.success(f"Top Sales Rep: {result}")

    elif "monthly sales" in q:
        result = filtered_df.groupby('month')['total_sales'].sum()
        st.write(result)

    elif "delivery status" in q:
        result = filtered_df.groupby('delivery_status')['total_sales'].sum()
        st.write(result)

    else:
        st.warning("Try questions like: total sales, top product, top sales rep")