import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import os

# --------------------- CONFIG ---------------------
st.set_page_config(page_title="MIJI ROMC Dashboard", layout="wide")

# --------------------- STYLE ---------------------
st.markdown("""
    <style>
        body {
            color: #E1E1E1;
            background-color: #121212;
        }
        .stTabs [role="tablist"] > div {
            font-weight: bold;
            font-size: 16px;
        }
    </style>
""", unsafe_allow_html=True)

# --------------------- LOGO ---------------------
st.image("logo.png", width=120)
st.title("🏆 MIJI ROMC - Tournament Performance Dashboard")

# --------------------- DATA ---------------------
df = pd.read_excel("MIJITOUR.xlsx", sheet_name="Sheet1")

# --------------------- FILTER PANEL ---------------------
st.sidebar.header("📊 Filter Panel")
selected_enemy = st.sidebar.selectbox("Enemy", df["Enemy"].unique())

st.sidebar.markdown("### Class")
all_classes = sorted(df["Class"].unique())

if "class_states" not in st.session_state:
    st.session_state.class_states = {cls: True for cls in all_classes}

def update_all(val):
    for cls in all_classes:
        st.session_state.class_states[cls] = val

select_all = st.sidebar.checkbox("✅ Select All Classes", value=True, on_change=update_all, args=(True,))
if not select_all:
    update_all(False)

selected_classes = []
for cls in all_classes:
    filename = cls.lower().replace(" ", "-") + ".png"
    image_path = os.path.join("classes-logo", filename)

    cols = st.sidebar.columns([0.25, 1.0])
    with cols[0]:
        try:
            st.image(image_path, width=50)
        except:
            st.write("")
    with cols[1]:
        checked = st.checkbox(label=cls, key=f"class_{cls}", value=st.session_state.class_states[cls])
        st.session_state.class_states[cls] = checked
        if checked:
            selected_classes.append(cls)

filtered_df = df[(df["Enemy"] == selected_enemy) & (df["Class"].isin(selected_classes))]

# --------------------- TABLE STYLER ---------------------
def styled_table(df, subset=None):
    styler = df.style.set_properties(**{"text-align": "center"})
    styler.set_table_styles([{
        "selector": "th",
        "props": [("text-align", "center"), ("font-weight", "bold")]
    }])
    if subset:
        styler.set_properties(subset=subset, **{"text-align": "left"})
    return styler

# --------------------- TABS ---------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "⚔️ Attacker",
    "💖 Assist x Resurrect",
    "🧠 Assist x Expel",
    "📊 Class Summary",
    "🔮 Advanced Insights",
    "🔍 Player Details by Class"
])


with tab1:
    st.subheader("⚔️ Kill x Damage (M)")
    fig1 = px.scatter(filtered_df, x="Damage (M)", y="Kill", color="Class",
                      hover_name="Name", text="Name", size="Kill", title="Kill vs Damage",
                      labels={"Damage (M)": "Damage (Million)", "Kill": "Kills"})
    fig1.update_traces(textposition="top center")
    st.plotly_chart(fig1, use_container_width=True)

    attacker_df = filtered_df[["Name", "Class", "Kill", "Damage (M)", "Death", "Expel"]].sort_values(by="Kill", ascending=False)
    st.dataframe(styled_table(attacker_df, subset=["Name", "Class"]), use_container_width=True)

with tab2:
    st.subheader("💖 Assist x Resurrect")
    fig2 = px.scatter(filtered_df, x="Assist", y="Resurrect", color="Class",
                      hover_name="Name", text="Name", size="Resurrect", title="Assist vs Resurrect")
    fig2.update_traces(textposition="top center")
    st.plotly_chart(fig2, use_container_width=True)

    heal_df = filtered_df[["Name", "Assist", "Heal (M)", "Resurrect", "Death", "Expel"]].sort_values(by="Resurrect", ascending=False)
    st.dataframe(styled_table(heal_df, subset=["Name"]), use_container_width=True)

with tab3:
    st.subheader("🧠 Assist x Expel")
    fig3 = px.scatter(filtered_df, x="Assist", y="Expel", color="Class",
                      hover_name="Name", text="Name", size="Expel", title="Assist vs Expel")
    fig3.update_traces(textposition="top center")
    st.plotly_chart(fig3, use_container_width=True)

    assist_df = filtered_df[["Name", "Assist", "Expel", "Death"]].sort_values(by="Assist", ascending=False)
    st.dataframe(styled_table(assist_df, subset=["Name"]), use_container_width=True)
    
with tab4:
    st.subheader("📊 Summary by Class")

    class_summary = (
        filtered_df
        .groupby("Class")
        .agg({
            "Kill": "sum",
            "Damage (M)": "sum",
            "Assist": "sum",
            "Heal (M)": "sum",
            "Resurrect": "sum",
            "Expel": "sum",
            "Death": "sum"
        })
        .reset_index()
        .sort_values(by="Kill", ascending=False)
    )

    # Show full styled table
    st.dataframe(
        styled_table(class_summary, subset=["Class"]),
        use_container_width=True
    )

    # Charts per metric
    metrics = ["Kill", "Damage (M)", "Assist", "Heal (M)", "Resurrect", "Expel", "Death"]
    for metric in metrics:
        st.markdown(f"### 🔹 {metric} by Class")
        fig = px.bar(class_summary, x="Class", y=metric, color="Class", text_auto=True)
        fig.update_layout(yaxis_title=metric)
        st.plotly_chart(fig, use_container_width=True)

with tab5:
    st.subheader("🔮 Advanced Insights by Class")

    # Prepare summary base
    advanced_summary = (
        filtered_df
        .groupby("Class")
        .agg({
            "Kill": "sum",
            "Damage (M)": "sum",
            "Assist": "sum",
            "Heal (M)": "sum",
            "Resurrect": "sum",
            "Expel": "sum",
            "Death": "sum"
        })
        .reset_index()
    )

    # --- Calculated Insights ---
    advanced_summary["Kill per Death"] = (advanced_summary["Kill"] / advanced_summary["Death"]).replace([float("inf"), -float("inf")], 0).round(2)
    advanced_summary["Heal per Resurrect"] = (advanced_summary["Heal (M)"] / advanced_summary["Resurrect"]).replace([float("inf"), -float("inf")], 0).round(2)
    advanced_summary["Expel per Death"] = (advanced_summary["Expel"] / advanced_summary["Death"]).replace([float("inf"), -float("inf")], 0).round(2)
    advanced_summary["Impact Score"] = (
        advanced_summary["Kill"] * 2 +
        advanced_summary["Assist"] +
        advanced_summary["Heal (M)"] * 0.5 +
        advanced_summary["Resurrect"] * 2 +
        advanced_summary["Expel"] * 1.5 -
        advanced_summary["Death"]
    ).round(2)

    # --- Table ---
    show_cols = [
        "Class", "Kill", "Death", "Kill per Death",
        "Heal (M)", "Resurrect", "Heal per Resurrect",
        "Expel", "Expel per Death", "Impact Score"
    ]

    st.dataframe(styled_table(advanced_summary[show_cols], subset=["Class"]), use_container_width=True)

    # --- Charts ---
    metric_charts = [
        "Kill per Death",
        "Heal per Resurrect",
        "Expel per Death",
        "Impact Score"
    ]

    for metric in metric_charts:
        st.markdown(f"### 🔹 {metric}")
        
        if metric == "Impact Score":
            with st.expander("💡 How is Impact Score calculated?"):
                st.markdown("**Formula:** `Kill × 2 + Assist + Heal(M) × 0.5 + Resurrect × 2 + Expel × 1.5 − Death`")

        fig = px.bar(advanced_summary, x="Class", y=metric, color="Class", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)

with tab6:
    st.subheader("🔍 Player Performance by Class")

    available_classes = sorted(filtered_df["Class"].unique())

    if not available_classes:
        st.warning("No data available for selected enemy and class filters.")
    else:
        selected_class = st.selectbox("Select a Class", available_classes)

        class_df = filtered_df[filtered_df["Class"] == selected_class]

        st.markdown(f"### 👥 Players in **{selected_class}** ({len(class_df)} total)")

        st.dataframe(
            styled_table(
                class_df[["Name", "Kill", "Assist", "Heal (M)", "Resurrect", "Expel", "Damage (M)", "Death"]],
                subset=["Name"]
            ),
            use_container_width=True
        )

        # Chart: Toggle metric to visualize
        metric_options = ["Kill", "Assist", "Heal (M)", "Resurrect", "Expel", "Damage (M)", "Death"]
        selected_metric = st.selectbox("📊 Select a metric to visualize", metric_options, index=0)

        st.markdown(f"### 📌 {selected_metric} by Player in {selected_class}")
        fig = px.bar(
            class_df.sort_values(selected_metric, ascending=False),
            x="Name", y=selected_metric, text_auto=True, color="Name"
        )
        fig.update_layout(yaxis_title=selected_metric)
        st.plotly_chart(fig, use_container_width=True)
