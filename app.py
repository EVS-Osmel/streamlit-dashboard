import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime


# ------------------------
# Month filter helper
# ------------------------
def month_range_filter(
    df: pd.DataFrame,
    month_num_col: str = "Month_#",
    month_name_col: str = "Month",
    label: str = "Select month range:",
):
    """
    Show a month range selector in the sidebar using month NAMES,
    but sort/filter by month NUMBERS.

    Returns:
        start_month_name, end_month_name, start_month_num, end_month_num, filtered_df
    """
    months_df = (
        df[[month_num_col, month_name_col]]
        .drop_duplicates()
        .sort_values(month_num_col)
    )

    if months_df.empty:
        st.sidebar.warning("No months available for filtering.")
        return None, None, None, None, df.copy()

    month_numbers = months_df[month_num_col].tolist()
    month_names = months_df[month_name_col].tolist()
    name_to_num = dict(zip(month_names, month_numbers))

    start_month_name, end_month_name = st.sidebar.select_slider(
        label,
        options=month_names,
        value=(month_names[0], month_names[-1]),
    )

    start_month_num = name_to_num[start_month_name]
    end_month_num = name_to_num[end_month_name]

    mask = (
        (df[month_num_col] >= start_month_num)
        & (df[month_num_col] <= end_month_num)
    )
    filtered_df = df.loc[mask].copy()

    return (
        start_month_name,
        end_month_name,
        start_month_num,
        end_month_num,
        filtered_df,
    )


# ------------------------
# Data loading (cached)
# ------------------------
@st.cache_data
def load_data():
    overall = pd.read_excel("GRO_data.xlsx")
    pa = pd.read_excel("pa_data.xlsx")
    return overall, pa


# ------------------------
# 1. Page config
# ------------------------
st.set_page_config(
    page_title="Sample Dashboard",
    page_icon="📊",
    layout="wide",
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
# 3. Load data
# ------------------------
overall_plot, pa_plot = load_data()

# ------------------------
# 4. Sidebar filters
# ------------------------
st.sidebar.header("Filters")

practice_areas = st.sidebar.multiselect(
    "Select PA(s):",
    options=sorted(pa_plot["Practice area"].unique()),
    default=sorted(pa_plot["Practice area"].unique()),
)

# Apply practice area filter first
pa_plot = pa_plot[pa_plot["Practice area"].isin(practice_areas)]

(
    start_name,
    end_name,
    start_num,
    end_num,
    pa_plot_filtered,
) = month_range_filter(pa_plot)

if start_name is not None:
    st.write(f"Showing data from **{start_name}** to **{end_name}**")

# ------------------------
# 5. Summary metrics (last month)
# ------------------------
current_month_num = datetime.now().month
last_month_num = 12 if current_month_num == 1 else current_month_num - 1

mask_last_month_num = overall_plot["Month_#"] == last_month_num

if mask_last_month_num.any():
    last_month_name = overall_plot.loc[mask_last_month_num, "Month"].iloc[0]

    def get_metric_value(metric_name: str):
        mask_metric = (
            (overall_plot["Month"] == last_month_name)
            & (overall_plot["Metric"] == metric_name)
        )
        if mask_metric.any():
            return overall_plot.loc[mask_metric, "Value"].iloc[0]
        return None

    latest_UT = get_metric_value("Utilization")
    latest_billability = get_metric_value("Billability")
    latest_engagement = get_metric_value("Engagement")

    col1, col2, col3 = st.columns(3)

    with col1:
        if latest_UT is not None:
            st.metric(f"{last_month_name} Utilization", f"{latest_UT:.1%}")

    with col2:
        if latest_billability is not None:
            st.metric(f"{last_month_name} Billability", f"{latest_billability:.1%}")

    with col3:
        if latest_engagement is not None:
            st.metric(f"{last_month_name} Engagement", f"{latest_engagement:.1%}")
else:
    st.warning("No data found for last month in overall_plot.")

# ------------------------
# 6. Plotly chart
# ------------------------
st.subheader("Research Hours Over Time")

if pa_plot_filtered.empty:
    st.warning(
        "No data for the selected filters. "
        "Try adjusting the Practice Areas or months."
    )
else:
    fig = px.area(
        pa_plot_filtered,
        x="Month",
        y="Research hours",
        color="Practice area",
        title="Research hours over time",
        markers=True,
    )

    st.plotly_chart(fig, use_container_width=True)


# ------------------------
# 7. Show raw data (optional)
# ------------------------
# with st.expander("Show raw data"):
#     st.dataframe(filtered_df)
