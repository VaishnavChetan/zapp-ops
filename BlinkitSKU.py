import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="ZAPP Operations & Dark Store Tracker",
    page_icon="⚡",
    layout="wide"
)

# Custom header
st.title("Zapp Ops: Inventory, Dark Stores & SLA Tracker")
st.caption("Live monitoring for Blinkit, Swiggy Instamart, and expansion hub health.")

# 3 Focused tabs
tab_overview, tab_stores, tab_inventory = st.tabs([
    "📊 Performance & SLA", 
    "🏬 Dark Store Health", 
    "📦 SKU Stock Monitor"
])

# ----------------- BASE DATA -----------------
# Matches Blinkit Expansion Level 2 view
store_data = [
    {"City": "Manipal", "Darkstores_Live": 1, "Avg_Daily_Units": 0.500, "Daily_Sales_INR": 45.0, "Availability_Pct": 21.7, "Status": "Passing"},
    {"City": "Bengaluru", "Darkstores_Live": 52, "Avg_Daily_Units": 0.090, "Daily_Sales_INR": 8.12, "Availability_Pct": 67.2, "Status": "At Risk"},
    {"City": "Hyderabad", "Darkstores_Live": 28, "Avg_Daily_Units": 0.059, "Daily_Sales_INR": 5.27, "Availability_Pct": 99.7, "Status": "At Risk"},
    {"City": "Chennai", "Darkstores_Live": 17, "Avg_Daily_Units": 0.047, "Daily_Sales_INR": 4.23, "Availability_Pct": 66.4, "Status": "At Risk"},
    {"City": "Mumbai", "Darkstores_Live": 0, "Avg_Daily_Units": 0.000, "Daily_Sales_INR": 0.0, "Availability_Pct": 0.0, "Status": "Expansion Pending"},
]

# SKU Stock across channels
stock_data = [
    {"Channel": "Swiggy Instamart", "SKU": "ZAPP Lime (57ml)", "Sellable": 308, "Reserved": 0, "Daily_Run_Rate": 14, "Days_Cover": 22.0},
    {"Channel": "Swiggy Instamart", "SKU": "ZAPP Berry (57ml)", "Sellable": 0, "Reserved": 6, "Daily_Run_Rate": 20, "Days_Cover": 0.0},
    {"Channel": "Blinkit", "SKU": "ZAPP Lime (57ml)", "Sellable": 0, "Reserved": 0, "Daily_Run_Rate": 4, "Days_Cover": 0.0},
    {"Channel": "Blinkit", "SKU": "ZAPP Berry (57ml)", "Sellable": 0, "Reserved": 0, "Daily_Run_Rate": 6, "Days_Cover": 0.0},
]

df_stores = pd.DataFrame(store_data)
df_stock = pd.DataFrame(stock_data)

# ----------------- TAB 1: OVERVIEW & SLA -----------------
with tab_overview:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Live Dark Stores", "98", "+4 from last cycle")
    col2.metric("Target Threshold", "0.200 units/store/day", "Blinkit L2 Target")
    col3.metric("Critical Out-of-Stock SKUs", "3 / 4 Channels", "-High Priority", delta_color="inverse")
    col4.metric("Active Hub Assessment", "27th Sep 2026", "Days Remaining: 4")

    st.divider()
    
    st.subheader("Blinkit Level 2 Store Performance vs SLA")
    fig = px.bar(
        df_stores[df_stores["Darkstores_Live"] > 0],
        x="City",
        y="Avg_Daily_Units",
        color="Status",
        color_discrete_map={"Passing": "#2ecc71", "At Risk": "#e74c3c"},
        text="Avg_Daily_Units",
        title="Avg Units / Store / Day (Target: 0.200)"
    )
    fig.add_hline(y=0.200, line_dash="dash", line_color="yellow", annotation_text="0.200 Target Line")
    st.plotly_chart(fig, use_container_width=True)

# ----------------- TAB 2: DARK STORE HEALTH -----------------
with tab_stores:
    st.subheader("City-Wise Dark Store Network")
    
    st.dataframe(
        df_stores,
        column_config={
            "City": "City Name",
            "Darkstores_Live": st.column_config.NumberColumn("Live Dark Stores", format="%d"),
            "Avg_Daily_Units": st.column_config.ProgressColumn(
                "Avg Units / Store / Day",
                help="SLA target is 0.200 units/store/day",
                format="%.3f",
                min_value=0.0,
                max_value=0.5,
            ),
            "Daily_Sales_INR": st.column_config.NumberColumn("Avg Daily Sales (INR)", format="₹%.2f"),
            "Availability_Pct": st.column_config.NumberColumn("Stock Availability", format="%.1f%%"),
            "Status": st.column_config.SelectboxColumn(
                "Evaluation Status",
                options=["Passing", "At Risk", "Expansion Pending"],
                help="Status under Blinkit Level 2 Assessment"
            ),
        },
        hide_index=True,
        use_container_width=True
    )
    
    st.warning("⚠️ **Assessment Deadline (27 Sep 2026):** Stores in Bengaluru, Hyderabad, and Chennai must achieve ≥ 0.200 units/day (₹19/day) to prevent automated de-listing and store exits.")

# ----------------- TAB 3: SKU STOCK MONITOR -----------------
with tab_inventory:
    st.subheader("Cross-Platform Stock & Days of Cover")
    
    for _, row in df_stock.iterrows():
        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        c1.write(f"**{row['Channel']}** — {row['SKU']}")
        c2.write(f"Sellable: `{row['Sellable']}`")
        c3.write(f"Days Cover: `{row['Days_Cover']} days`")
        if row["Sellable"] == 0:
            c4.error("CRITICAL OOS")
        elif row["Days_Cover"] < 7:
            c4.warning("LOW STOCK")
        else:
            c4.success("HEALTHY")