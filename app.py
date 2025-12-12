import streamlit as st
import pandas as pd
import plotly.express as px
import datetime


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
    page_title="GRO Governance",
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

current_month_num = datetime.datetime.now().month
last_month_num = 12 if current_month_num == 1 else current_month_num -1
last_month_name = overall_plot.loc[overall_plot['Month_#'] == last_month_num, 'Month'].iloc[0]

def get_metric_value(metric_name: str):
    return overall_plot.loc[(overall_plot['Month_#'] == last_month_num) & (overall_plot['Metric'] == metric_name), 'Value'].iloc[0]

col1, col2, col3 = st.columns(3)

with col1: st.metric(f"{last_month_name} Utilization", f"{get_metric_value("Utilization"):.1%}")
with col2: st.metric(f"{last_month_name} Billability", f"{get_metric_value("Billability"):.1%}")
with col3: st.metric(f"{last_month_name} Engagement", f"{get_metric_value("Engagement"):.1%}")


# ------------------------
# 6. Plotly line chart for UT, Engagement and Billability
# ------------------------

metrics = ['Billability', 'Utilization', 'Engagement']
months_filter = pa_plot_filtered['Month'].unique()
st.subheader("Metrics Evolution")

if pa_plot_filtered.empty:
    st.warning(
        "No data for the selected filters. "
        "Try adjusting the Practice Areas or months."
    )
else:
    fig = px.line(
        overall_plot.loc[(overall_plot['Metric'].isin(metrics)) & (overall_plot['Month'].isin(months_filter))],
        x="Month",
        y="Value",
        color="Metric",
        title="Metrics over time",
        markers=True,
        text='Value'
    )

    fig.update_traces(
    texttemplate="%{y:.1%}",
    textposition="top center"
    )

    fig.update_yaxes(
    tickformat=".0%"
    )
     

    st.plotly_chart(fig, use_container_width=True)

# ------------------------
# 7. Plotly area chart for research hours
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
