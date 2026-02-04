import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

fte = "Gonzalez Yamileth"
current_FTEs = ["Gonzalez Yamileth",
                 "VND Guzman Agustin",
                 "VND Reinoza  Osmel",
                 "VND Nunez Angela",
                 "VND Pizarro Nicol",
                 "VND Fuentealba Erick",
                 "VND Abrams Shannon",
                 "VND Olavarria Isabella",
                 "VND Rivadeneira Gabriela",
                 "VND Marchetti Vinicius",
                 "GRO"]


# ------------------------
# Month filter helper
# ------------------------

def year_month_range_filter(
    df: pd.DataFrame,
    year_col: str = "Year",
    month_num_col: str = "Month_#",
    month_name_col: str = "Month",
    label: str = "Select year-month range:",
    select_all_label: str = "Select All",
):
    """
    Sidebar year-month range selector with Select All checkbox.
    - Sorting/filtering is done chronologically by (Year, Month_#)
    - Display is done using "YYYY - MonthName"

    Returns:
        start_year, start_month_name, start_month_num,
        end_year, end_month_name, end_month_num,
        filtered_df
    """

    # Select All toggle
    select_all = st.sidebar.checkbox(select_all_label, value=False)

    # Keep unique chronological (Year, Month_#) combos
    ym_df = (
        df[[year_col, month_num_col, month_name_col]]
        .drop_duplicates()
        .sort_values([year_col, month_num_col])
    )

    if ym_df.empty:
        st.sidebar.warning("No year-month values available for filtering.")
        return None, None, None, None, None, None, df.copy()

    # Create ordered options as tuples (Year, Month_#)
    options = list(zip(ym_df[year_col], ym_df[month_num_col]))

    # Map tuple -> month name for formatting
    ym_to_name = {(y, m): n for y, m, n in zip(
        ym_df[year_col], ym_df[month_num_col], ym_df[month_name_col]
    )}

    # Default range is full range
    start_ym_default = options[0]
    end_ym_default = options[-1]

    # If Select All is checked, skip filtering and return full df
    if select_all:
        start_year, start_month_num = start_ym_default
        end_year, end_month_num = end_ym_default

        return (
            start_year,
            ym_to_name[start_ym_default],
            start_month_num,
            end_year,
            ym_to_name[end_ym_default],
            end_month_num,
            df.copy(),
        )

    # Slider returns (start_tuple, end_tuple)
    start_ym, end_ym = st.sidebar.select_slider(
        label,
        options=options,
        value=(start_ym_default, end_ym_default),
        format_func=lambda ym: f"{ym[0]} - {ym_to_name.get(ym, 'Unknown')}",
        disabled=select_all,  # stays enabled unless Select All is checked
    )

    start_year, start_month_num = start_ym
    end_year, end_month_num = end_ym

    start_month_name = ym_to_name[start_ym]
    end_month_name = ym_to_name[end_ym]

    # Filter chronologically using tuple comparison
    ym_series = list(zip(df[year_col], df[month_num_col]))
    mask = [(start_ym <= ym <= end_ym) for ym in ym_series]

    filtered_df = df.loc[mask].copy()

    return (
        start_year,
        start_month_name,
        start_month_num,
        end_year,
        end_month_name,
        end_month_num,
        filtered_df,
    )

# ------------------------
# Data loading (cached)
# ------------------------
@st.cache_data
def load_data():
    ftes = pd.read_excel("fte_data.xlsx")
    return ftes


# ------------------------
# 1. Page config
# ------------------------
st.set_page_config(
    page_title="FTE Dashboard",
    page_icon="📊",
    layout="wide",
)


st.markdown(
    """
    <style>
    /* Outermost app wrapper */
    .stApp {
      background-color: rgba(0,0,0,0);
      }

    /* Main area wrapper (everything except sidebar) */
    div[data-testid="stAppViewContainer"] {
      background-color: rgba(0,0,0,0);
      }

    /* Main content area */
    main[data-testid="stMain"] {
      background-color: rgba(0,0,0,0);
      }

    /* Center content container (controls padding/width area) */
    div.block-container {
      background-color: rgba(0,0,0,0);
      }

    /* Top header bar */
    div[data-testid="stHeader"] {
      background: rgba(0,0,0,0);
      }

    /* Sidebar */
    section[data-testid="stSidebar"] {
      background-color: #43224D;
      }
    section[data-testid="stSidebar"] > div {
      background-color: #43224D;
      }
</style>
""", 
unsafe_allow_html=True)


# ------------------------
# 2. Title & description
# ------------------------
st.title("📊 GRO Dashboard")
st.write(
    "Check GRO performance as a team or by FTE. "
    "Use the controls on the left to filter the data."
)

# ------------------------
# 3. Load data
# ------------------------
fte_plot = load_data()

# ------------------------
# 4. Sidebar filters
# ------------------------
st.sidebar.header("FTE Filters")

fte_filter = st.sidebar.multiselect(
    "Select data to show:",
    options = [fte,"GRO"],
    default=[fte,"GRO"]
)

st.sidebar.header("Metrics Filters")

metric_filter = st.sidebar.multiselect(
    "Select metrics to show:",
    options=['Utilization', 'Billability', 'Engagement', 'Adj. Ack. SLA', 'Due to DRS SLA'],
    default=['Utilization']
)

# Apply FTE and metric filters first
fte_plot2 = fte_plot[
    (fte_plot["FTE"].isin(fte_filter)) &
    (fte_plot["Metric"].isin(metric_filter))
].copy()

# Apply Year-Month range filter (new multi-year filter)
(
    start_year,
    start_month_name,
    start_month_num,
    end_year,
    end_month_name,
    end_month_num,
    fte_plot_filtered,
) = year_month_range_filter(
    fte_plot2,
    year_col="Year",
    month_num_col="Month_#",
    month_name_col="Month",
    label="Select year-month range:",
    select_all_label="Select All"
)

# Display selected range (only if filter returned a valid range)
if start_year is not None and end_year is not None:
    st.write(
        f"Showing data from **{start_month_name} {start_year}** "
        f"to **{end_month_name} {end_year}**"
    )

# ------------------------
# 5. Summary metrics (last month)
# ------------------------

# current_month_num = datetime.datetime.now().month
# last_month_num = 12 if current_month_num == 1 else current_month_num -1
# last_month_name = fte_plot.loc[fte_plot['Month_#'] == last_month_num, 'Month'].iloc[0]

# def get_metric_value(metric_name: str):
#     return fte_plot.loc[(fte_plot['Month_#'] == last_month_num)
#                         &(fte_plot['Metric'] == metric_name)
#                         &(fte_plot["FTE"] == fte), 'Value'].iloc[0]

# col1, col2, col3 = st.columns(3)

# with col1: st.metric(f"{last_month_name} Utilization", f"{get_metric_value("Utilization"):.1%}")
# with col2: st.metric(f"{last_month_name} Billability", f"{get_metric_value("Billability"):.1%}")
# with col3: st.metric(f"{last_month_name} Engagement", f"{get_metric_value("Engagement"):.1%}")


# ------------------------
# 6. Plotly line chart for UT, Billability and Engagement
# ------------------------

metrics = ['Utilization', 'Billability', 'Engagement', 'Adj. Ack. SLA', 'Due to DRS SLA']
st.subheader("Metrics Evolution")

if fte_plot_filtered.empty:
    st.warning(
        "No data for the selected filters. "
        "Try adjusting the FTEs, metrics or months."
    )
else:
    # Build a proper chronological Year-Month datetime
    fte_plot_filtered = fte_plot_filtered.copy()
    fte_plot_filtered["YearMonth"] = pd.to_datetime(
        fte_plot_filtered["Year"].astype(str) + "-" + fte_plot_filtered["Month_#"].astype(str).str.zfill(2) + "-01"
    )

    # Optional: readable label for the x-axis
    fte_plot_filtered["YearMonth_Label"] = fte_plot_filtered["YearMonth"].dt.strftime("%Y-%b")

    # Ensure chronological order
    fte_plot_filtered = fte_plot_filtered.sort_values("YearMonth")

    # (Optional) filter only the metrics you care about
    fte_plot_filtered = fte_plot_filtered[fte_plot_filtered["Metric"].isin(metrics)]

    fig = px.line(
        fte_plot_filtered,
        x="YearMonth",
        y="Value",
        color="Metric",
        line_dash="FTE",
        title="Metrics over time",
        markers=True
    )

    # Make x-axis show friendly labels
    fig.update_xaxes(
        tickformat="%Y-%b",
        title_text="Year-Month"
    )

    fig.update_yaxes(
        tickformat=".1%")

    #fig.update_layout(
    #paper_bgcolor="#776EA9",  # outside plot (transparent)
    #plot_bgcolor="rgba(0,0,0,0)",   # inside axes (transparent)
    #)

    st.plotly_chart(fig, use_container_width=True)

# ------------------------
# 7. Show raw data (optional)
# ------------------------
with st.expander("Show raw data"):
    st.dataframe(fte_plot_filtered)
