import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------
# 1. Page config
# ------------------------
st.set_page_config(
    page_title="Sample Dashboard",
    page_icon="📊",
    layout="wide"
)

# ------------------------
# 2. Title & description
# ------------------------
st.title("📊 Interactive GRO Dashboard")
st.write(
    "This is a simple demo for future dashboard + analysis. "
    "Use the controls on the left to filter the data."
)

# ------------------------
# 3. Create a sample dataset
#    (In a real app, you'll load from CSV / database)
# ------------------------
@st.cache_data
def load_data():
    # Date range
    dates = pd.date_range("2024-01-01", periods=60, freq="D")

    data = []
    categories = ["North", "South", "East", "West"]

    for cat in categories:
        for d in dates:
            data.append({
                "date": d,
                "region": cat,
                "sales": max(0, 1000 + hash((cat, d)) % 500 - 250),  # fake but consistent
            })

    return pd.DataFrame(data)

df = load_data()

# ------------------------
# 4. Sidebar filters
# ------------------------
st.sidebar.header("Filters")

# Region filter
regions = st.sidebar.multiselect(
    "Select region(s):",
    options=sorted(df["region"].unique()),
    default=sorted(df["region"].unique())
)

# Date filter
min_date = df["date"].min()
max_date = df["date"].max()

date_range = st.sidebar.date_input(
    "Select date range:",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

# Ensure date_range is a tuple (start, end)
if isinstance(date_range, tuple):
    start_date, end_date = date_range
else:
    start_date = date_range
    end_date = date_range

# Apply filters
filtered_df = df[
    (df["region"].isin(regions)) &
    (df["date"] >= pd.to_datetime(start_date)) &
    (df["date"] <= pd.to_datetime(end_date))
]

# ------------------------
# 5. Summary metrics
# ------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Sales", f"{filtered_df['sales'].sum():,.0f}")

with col2:
    st.metric("Average Daily Sales", f"{filtered_df.groupby('date')['sales'].sum().mean():,.0f}")

with col3:
    st.metric("Number of Records", f"{len(filtered_df):,}")

# ------------------------
# 6. Plotly chart
# ------------------------
st.subheader("Sales Over Time")

if filtered_df.empty:
    st.warning("No data for the selected filters. Try adjusting the region or date range.")
else:
    fig = px.line(
        filtered_df,
        x="date",
        y="sales",
        color="region",
        title="Sales by Region Over Time",
        markers=True
    )

    st.plotly_chart(fig, use_container_width=True)

# ------------------------
# 7. Show raw data (optional)
# ------------------------
with st.expander("Show raw data"):
    st.dataframe(filtered_df)
