import streamlit as st
import pandas as pd

st.set_page_config(page_title="Military MWR Usage Dashboard", layout="wide")

# --- Load Data ---
branch_df = pd.read_csv("data_ai/mwr_by_branch.csv")
activity_df = pd.read_csv("data_ai/mwr_by_activity.csv")
trend_df = pd.read_csv("data_ai/mwr_usage_trend.csv")
rank_df = pd.read_csv("data_ai/mwr_by_rank.csv")
bases_df = pd.read_csv("data_ai/mwr_top_bases.csv")

# --- Header ---
st.title("Military MWR Usage Dashboard")
st.markdown("**Morale, Welfare, and Recreation (MWR)** programs support the quality of life for U.S. military service members and their families. This dashboard shows estimated usage across branches, activities, and time.")
st.divider()

# --- Top KPI Metrics ---
total_users = branch_df["MWR_Users"].sum()
total_strength = branch_df["Total_Strength"].sum()
overall_rate = round(total_users / total_strength * 100, 1)
top_branch = branch_df.loc[branch_df["Usage_Percentage"].idxmax(), "Branch"]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total MWR Users", f"{total_users:,}")
col2.metric("Total Military Strength", f"{total_strength:,}")
col3.metric("Overall Usage Rate", f"{overall_rate}%")
col4.metric("Highest Usage Branch", top_branch)

st.divider()

# --- Row 1: Branch usage ---
st.subheader("MWR Usage by Military Branch")
col_left, col_right = st.columns([3, 2])

with col_left:
    st.bar_chart(
        branch_df.set_index("Branch")[["Total_Strength", "MWR_Users"]],
        use_container_width=True,
        color=["#b0c4de", "#1f77b4"],
    )
    st.caption("Blue = MWR Users  |  Light Blue = Total Strength")

with col_right:
    display_branch = branch_df[["Branch", "MWR_Users", "Usage_Percentage"]].copy()
    display_branch.columns = ["Branch", "MWR Users", "Usage Rate (%)"]
    display_branch = display_branch.sort_values("Usage Rate (%)", ascending=False).reset_index(drop=True)
    st.dataframe(display_branch, use_container_width=True, hide_index=True)

st.divider()

# --- Row 2: Trend over time ---
st.subheader("MWR Participation Trend (2019-2024)")
col_t1, col_t2 = st.columns([3, 2])

with col_t1:
    st.line_chart(
        trend_df.set_index("Year")["Total_Users_Millions"],
        use_container_width=True,
    )
    st.caption("Users in millions. 2020 dip reflects COVID-19 facility closures.")

with col_t2:
    display_trend = trend_df.copy()
    display_trend["YoY_Change_Pct"] = display_trend["YoY_Change_Pct"].apply(
        lambda x: f"{x:+.1f}%" if pd.notna(x) else "-"
    )
    display_trend.columns = ["Year", "Users (Millions)", "Year-over-Year Change"]
    st.dataframe(display_trend, use_container_width=True, hide_index=True)

st.divider()

# --- Row 3: Activities & Rank ---
col_act, col_rank = st.columns(2)

with col_act:
    st.subheader("Monthly Users by MWR Activity")
    activity_sorted = activity_df.sort_values("Monthly_Users", ascending=True)
    st.bar_chart(
        activity_sorted.set_index("Activity")["Monthly_Users"],
        use_container_width=True,
        horizontal=True,
    )

with col_rank:
    st.subheader("MWR Usage Rate by Rank Category")
    rank_sorted = rank_df.sort_values("Usage_Rate_Pct", ascending=False).reset_index(drop=True)
    display_rank = rank_sorted[["Rank_Category", "Estimated_Users", "Usage_Rate_Pct"]].copy()
    display_rank.columns = ["Rank Category", "Estimated Users", "Usage Rate (%)"]
    st.dataframe(display_rank, use_container_width=True, hide_index=True)

    st.markdown("**Usage Rate by Rank**")
    for _, row in rank_sorted.iterrows():
        st.progress(int(row["Usage_Rate_Pct"]), text=f"{row['Rank_Category']}: {row['Usage_Rate_Pct']}%")

st.divider()

# --- Activity Satisfaction Explorer ---
st.subheader("MWR Activity Satisfaction Scores")
st.markdown("Average satisfaction rating (out of 5.0) reported by service members.")

sat_sorted = activity_df.sort_values("Avg_Satisfaction", ascending=False).reset_index(drop=True)
cols = st.columns(5)
for i, row in sat_sorted.iterrows():
    with cols[i % 5]:
        st.metric(label=row["Activity"], value=f"{row['Avg_Satisfaction']} / 5.0")

st.divider()

# --- Activity Deep Dive: What Are Members Using & Top Bases ---
st.subheader("What Service Members Are Using — Activity Breakdown & Top Bases")
st.markdown("Select an activity to see what it offers and which installations have the highest participation.")

activities_list = bases_df["Activity"].unique().tolist()
selected_activity = st.selectbox("Choose an MWR Activity", activities_list)

activity_info = bases_df[bases_df["Activity"] == selected_activity].iloc[0]
top_bases = bases_df[bases_df["Activity"] == selected_activity].sort_values("Rank")

col_desc, col_bases = st.columns([2, 3])

with col_desc:
    st.markdown(f"### {selected_activity}")
    st.info(activity_info["Description"])
    monthly_total = activity_df.loc[activity_df["Activity"] == selected_activity, "Monthly_Users"].values[0]
    satisfaction = activity_df.loc[activity_df["Activity"] == selected_activity, "Avg_Satisfaction"].values[0]
    st.metric("Estimated Monthly Users (DoD-wide)", f"{monthly_total:,}")
    st.metric("Avg. Satisfaction Score", f"{satisfaction} / 5.0")

with col_bases:
    st.markdown("**Top 3 Installations by Monthly Participation**")
    medals = ["Gold", "Silver", "Bronze"]
    medal_colors = ["#FFD700", "#C0C0C0", "#CD7F32"]
    for _, row in top_bases.iterrows():
        rank_idx = int(row["Rank"]) - 1
        pct_of_total = round(row["Monthly_Users"] / monthly_total * 100, 1)
        st.markdown(
            f"""
            <div style="background-color:#1e2a3a; border-left: 5px solid {medal_colors[rank_idx]};
                        padding: 12px 16px; border-radius: 6px; margin-bottom: 10px;">
                <span style="color:{medal_colors[rank_idx]}; font-weight:bold; font-size:15px;">
                    #{row['Rank']} {medals[rank_idx]}
                </span>
                &nbsp;&nbsp;
                <span style="color:white; font-size:15px;">{row['Base']}</span><br>
                <span style="color:#aac8e8; font-size:13px;">
                    {row['Monthly_Users']:,} monthly users &nbsp;|&nbsp; {pct_of_total}% of DoD-wide total
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.divider()

# --- All Activities Summary Table ---
st.subheader("Full Activity & Top Base Summary")
st.markdown("Overview of every MWR activity with its top installation at a glance.")

top1_bases = (
    bases_df[bases_df["Rank"] == 1]
    .merge(activity_df[["Activity", "Monthly_Users", "Avg_Satisfaction"]], on="Activity")
    .rename(columns={
        "Monthly_Users_y": "DoD Monthly Users",
        "Monthly_Users_x": "Top Base Monthly Users",
        "Avg_Satisfaction": "Satisfaction (/ 5.0)",
        "Base": "Top Installation",
    })
)[["Activity", "Description", "DoD Monthly Users", "Top Installation", "Top Base Monthly Users", "Satisfaction (/ 5.0)"]]

st.dataframe(
    top1_bases.reset_index(drop=True),
    use_container_width=True,
    hide_index=True,
    column_config={
        "Description": st.column_config.TextColumn("What It Offers", width="large"),
        "DoD Monthly Users": st.column_config.NumberColumn(format="%d"),
        "Top Base Monthly Users": st.column_config.NumberColumn(format="%d"),
        "Satisfaction (/ 5.0)": st.column_config.ProgressColumn(
            min_value=0, max_value=5, format="%.1f"
        ),
    },
)

st.divider()
st.caption("Data is based on publicly available DoD MWR reports and program estimates. Dashboard built for educational and research purposes.")
