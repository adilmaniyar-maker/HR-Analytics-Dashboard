import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HR Analytics Dashboard",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1b2a 0%, #1b2a3b 100%);
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

.main { background-color: #f0f4f8; }

.dashboard-header {
    background: linear-gradient(135deg, #0d1b2a 0%, #1a56db 55%, #06b6d4 100%);
    padding: 2rem 2.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 24px rgba(13,27,42,0.2);
}
.dashboard-header h1 { color: white; font-size: 2rem; font-weight: 700; margin: 0; }
.dashboard-header p  { color: #bae6fd; margin: 0.3rem 0 0 0; font-size: 0.95rem; }

.kpi-card {
    background: white;
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    box-shadow: 0 2px 12px rgba(13,27,42,0.08);
    border-left: 4px solid;
    transition: transform 0.2s;
    height: 110px;
}
.kpi-card:hover { transform: translateY(-2px); }
.kpi-label {
    font-size: 0.75rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.08em;
    color: #64748b; margin-bottom: 0.4rem;
}
.kpi-value { font-size: 1.9rem; font-weight: 700; color: #0d1b2a; line-height: 1; }
.kpi-sub   { font-size: 0.8rem; margin-top: 0.4rem; font-weight: 500; }

.section-header {
    font-size: 1.05rem; font-weight: 700; color: #0d1b2a;
    margin: 1.5rem 0 1rem 0; padding-bottom: 0.5rem;
    border-bottom: 2px solid #e2e8f0;
}

.insight-box {
    background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
    border: 1px solid #bae6fd; border-radius: 12px;
    padding: 0.9rem 1.1rem; margin-bottom: 0.6rem;
    font-size: 0.87rem; color: #0c4a6e;
}

.attrition-badge {
    display: inline-block; padding: 0.25rem 0.75rem;
    border-radius: 999px; font-size: 0.78rem; font-weight: 600;
}

#MainMenu {visibility: hidden;}
footer    {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── Load Data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("HR_Analytics_Sample_Dataset.csv", parse_dates=["Joining_Date"])
    df["Joining_Year"]  = df["Joining_Date"].dt.year
    df["Joining_Month"] = df["Joining_Date"].dt.to_period("M").astype(str)
    df["Attrition_Num"] = (df["Attrition"] == "Yes").astype(int)
    return df

df = load_data()

# ── Sidebar Filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎛️ Filters")
    st.markdown("---")

    cities = sorted(df["City"].unique())
    sel_cities = st.multiselect("🏙️ City", cities, default=cities)

    departments = sorted(df["Department"].unique())
    sel_depts = st.multiselect("🏢 Department", departments, default=departments)

    job_roles = sorted(df["Job_Role"].unique())
    sel_roles = st.multiselect("💼 Job Role", job_roles, default=job_roles)

    genders = sorted(df["Gender"].unique())
    sel_genders = st.multiselect("👤 Gender", genders, default=genders)

    attrition_opts = ["All", "Active", "Left"]
    sel_attrition = st.radio("📉 Attrition Status", attrition_opts, horizontal=True)

    st.markdown("---")
    st.markdown("**👨‍💻 Author:** Adil Sujaoddin Maniyar")
    st.markdown("**📊 Dataset:** HR Analytics · 1,000 employees")

# ── Filter Data ───────────────────────────────────────────────────────────────
fdf = df[
    df["City"].isin(sel_cities) &
    df["Department"].isin(sel_depts) &
    df["Job_Role"].isin(sel_roles) &
    df["Gender"].isin(sel_genders)
]
if sel_attrition == "Active":
    fdf = fdf[fdf["Attrition"] == "No"]
elif sel_attrition == "Left":
    fdf = fdf[fdf["Attrition"] == "Yes"]

# ── Palette ───────────────────────────────────────────────────────────────────
DEPT_COLORS = {
    "HR": "#1a56db", "IT": "#0891b2", "Sales": "#8b5cf6",
    "Finance": "#10b981", "Marketing": "#f59e0b", "Operations": "#ef4444"
}
PALETTE = ["#1a56db", "#0891b2", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444"]

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="dashboard-header">
    <h1>👥 HR Analytics Dashboard</h1>
    <p>Workforce insights · Attrition · Salary · Performance · 2018 – 2025</p>
</div>
""", unsafe_allow_html=True)

# ── KPI Cards ─────────────────────────────────────────────────────────────────
total_emp     = len(fdf)
attrition_cnt = fdf["Attrition_Num"].sum()
attrition_rt  = (attrition_cnt / total_emp * 100) if total_emp > 0 else 0
avg_salary    = fdf["Salary"].mean()
avg_exp       = fdf["Experience_Years"].mean()
avg_perf      = fdf["Performance_Rating"].mean()

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(f"""<div class="kpi-card" style="border-color:#1a56db;">
        <div class="kpi-label">👥 Total Employees</div>
        <div class="kpi-value">{total_emp:,}</div>
        <div class="kpi-sub" style="color:#1a56db;">{fdf['Department'].nunique()} departments</div>
    </div>""", unsafe_allow_html=True)

with k2:
    color = "#ef4444" if attrition_rt > 20 else "#f59e0b" if attrition_rt > 10 else "#10b981"
    st.markdown(f"""<div class="kpi-card" style="border-color:{color};">
        <div class="kpi-label">📉 Attrition Rate</div>
        <div class="kpi-value">{attrition_rt:.1f}%</div>
        <div class="kpi-sub" style="color:{color};">{attrition_cnt} employees left</div>
    </div>""", unsafe_allow_html=True)

with k3:
    st.markdown(f"""<div class="kpi-card" style="border-color:#8b5cf6;">
        <div class="kpi-label">💰 Avg Salary</div>
        <div class="kpi-value">₹{avg_salary:,.0f}</div>
        <div class="kpi-sub" style="color:#8b5cf6;">per annum</div>
    </div>""", unsafe_allow_html=True)

with k4:
    st.markdown(f"""<div class="kpi-card" style="border-color:#10b981;">
        <div class="kpi-label">🎓 Avg Experience</div>
        <div class="kpi-value">{avg_exp:.1f} yrs</div>
        <div class="kpi-sub" style="color:#10b981;">across workforce</div>
    </div>""", unsafe_allow_html=True)

with k5:
    perf_color = "#10b981" if avg_perf >= 3 else "#f59e0b"
    st.markdown(f"""<div class="kpi-card" style="border-color:{perf_color};">
        <div class="kpi-label">⭐ Avg Performance</div>
        <div class="kpi-value">{avg_perf:.2f}/5</div>
        <div class="kpi-sub" style="color:{perf_color};">rating score</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Row 1: Hiring Trend + Department Split ────────────────────────────────────
st.markdown('<div class="section-header">📊 Workforce Overview</div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    yearly = fdf.groupby(["Joining_Year", "Department"]).size().reset_index(name="Count")
    fig_trend = px.bar(
        yearly, x="Joining_Year", y="Count", color="Department",
        color_discrete_map=DEPT_COLORS,
        title="Employee Hiring by Year & Department",
        labels={"Joining_Year": "Year", "Count": "Employees Hired"},
        barmode="stack",
    )
    fig_trend.update_layout(
        plot_bgcolor="white", paper_bgcolor="white", font_family="Inter",
        title_font_size=14, margin=dict(t=50, b=20, l=0, r=0),
        legend=dict(orientation="h", y=1.12, x=0),
        xaxis=dict(showgrid=False, dtick=1),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with col2:
    dept_counts = fdf["Department"].value_counts().reset_index()
    dept_counts.columns = ["Department", "Count"]
    fig_dept = px.pie(
        dept_counts, names="Department", values="Count",
        color="Department", color_discrete_map=DEPT_COLORS,
        title="Employees by Department", hole=0.45,
    )
    fig_dept.update_layout(
        plot_bgcolor="white", paper_bgcolor="white", font_family="Inter",
        title_font_size=14, margin=dict(t=50, b=10, l=0, r=0),
        legend=dict(orientation="h", y=-0.15),
    )
    fig_dept.update_traces(textposition="outside", textinfo="percent+label")
    st.plotly_chart(fig_dept, use_container_width=True)

# ── Row 2: Attrition by Department + Gender Distribution ─────────────────────
st.markdown('<div class="section-header">📉 Attrition Analysis</div>', unsafe_allow_html=True)

col3, col4, col5 = st.columns(3)

with col3:
    att_dept = fdf.groupby("Department").agg(
        Total=("Attrition_Num", "count"),
        Left=("Attrition_Num", "sum")
    ).reset_index()
    att_dept["Rate %"] = (att_dept["Left"] / att_dept["Total"] * 100).round(1)
    att_dept = att_dept.sort_values("Rate %", ascending=True)

    fig_att = go.Figure(go.Bar(
        x=att_dept["Rate %"], y=att_dept["Department"],
        orientation="h",
        marker=dict(color=att_dept["Rate %"],
                    colorscale=[[0,"#10b981"],[0.5,"#f59e0b"],[1,"#ef4444"]]),
        text=att_dept["Rate %"].apply(lambda x: f"{x}%"),
        textposition="outside",
    ))
    fig_att.update_layout(
        title="Attrition Rate by Department",
        plot_bgcolor="white", paper_bgcolor="white", font_family="Inter",
        title_font_size=14, margin=dict(t=50, b=20, l=0, r=40),
        xaxis=dict(showgrid=True, gridcolor="#f1f5f9", title="Attrition Rate (%)"),
        yaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig_att, use_container_width=True)

with col4:
    att_role = fdf.groupby("Job_Role").agg(
        Total=("Attrition_Num","count"), Left=("Attrition_Num","sum")
    ).reset_index()
    att_role["Rate %"] = (att_role["Left"] / att_role["Total"] * 100).round(1)
    att_role = att_role.sort_values("Rate %", ascending=False).head(8)

    fig_role = px.bar(
        att_role, x="Job_Role", y="Rate %",
        color="Rate %", color_continuous_scale="RdYlGn_r",
        title="Attrition Rate by Job Role",
        text="Rate %",
    )
    fig_role.update_traces(texttemplate="%{text}%", textposition="outside")
    fig_role.update_layout(
        plot_bgcolor="white", paper_bgcolor="white", font_family="Inter",
        title_font_size=14, margin=dict(t=50, b=60, l=0, r=0),
        xaxis=dict(showgrid=False, tickangle=-30),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_role, use_container_width=True)

with col5:
    gender_att = fdf.groupby(["Gender", "Attrition"]).size().reset_index(name="Count")
    fig_gen = px.bar(
        gender_att, x="Gender", y="Count", color="Attrition",
        color_discrete_map={"Yes": "#ef4444", "No": "#10b981"},
        title="Attrition by Gender",
        barmode="group", text="Count",
    )
    fig_gen.update_traces(textposition="outside")
    fig_gen.update_layout(
        plot_bgcolor="white", paper_bgcolor="white", font_family="Inter",
        title_font_size=14, margin=dict(t=50, b=20, l=0, r=0),
        legend=dict(title="Attrition", orientation="h", y=1.12),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
    )
    st.plotly_chart(fig_gen, use_container_width=True)

# ── Row 3: Salary Analysis ────────────────────────────────────────────────────
st.markdown('<div class="section-header">💰 Salary Analysis</div>', unsafe_allow_html=True)

col6, col7 = st.columns(2)

with col6:
    sal_dept = fdf.groupby("Department")["Salary"].mean().reset_index()
    sal_dept.columns = ["Department", "Avg Salary"]
    sal_dept = sal_dept.sort_values("Avg Salary", ascending=True)

    fig_sal = go.Figure(go.Bar(
        x=sal_dept["Avg Salary"], y=sal_dept["Department"],
        orientation="h",
        marker=dict(color=sal_dept["Avg Salary"],
                    colorscale="Blues"),
        text=sal_dept["Avg Salary"].apply(lambda x: f"₹{x:,.0f}"),
        textposition="outside",
    ))
    fig_sal.update_layout(
        title="Average Salary by Department",
        plot_bgcolor="white", paper_bgcolor="white", font_family="Inter",
        title_font_size=14, margin=dict(t=50, b=20, l=0, r=80),
        xaxis=dict(showgrid=True, gridcolor="#f1f5f9", title="Avg Salary (₹)"),
        yaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig_sal, use_container_width=True)

with col7:
    fig_box = px.box(
        fdf, x="Department", y="Salary", color="Department",
        color_discrete_map=DEPT_COLORS,
        title="Salary Distribution by Department",
        points="outliers",
    )
    fig_box.update_layout(
        plot_bgcolor="white", paper_bgcolor="white", font_family="Inter",
        title_font_size=14, margin=dict(t=50, b=20, l=0, r=0),
        showlegend=False,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9", title="Salary (₹)"),
    )
    st.plotly_chart(fig_box, use_container_width=True)

# ── Row 4: Experience & Performance ──────────────────────────────────────────
st.markdown('<div class="section-header">🎓 Experience & Performance</div>', unsafe_allow_html=True)

col8, col9, col10 = st.columns(3)

with col8:
    exp_att = fdf.groupby("Experience_Years")["Attrition_Num"].mean().reset_index()
    exp_att["Attrition Rate %"] = (exp_att["Attrition_Num"] * 100).round(1)
    fig_exp = px.line(
        exp_att, x="Experience_Years", y="Attrition Rate %",
        markers=True, title="Attrition Rate by Experience",
        color_discrete_sequence=["#1a56db"],
    )
    fig_exp.update_layout(
        plot_bgcolor="white", paper_bgcolor="white", font_family="Inter",
        title_font_size=14, margin=dict(t=50, b=20, l=0, r=0),
        xaxis=dict(showgrid=False, title="Years of Experience"),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
    )
    st.plotly_chart(fig_exp, use_container_width=True)

with col9:
    perf_dept = fdf.groupby("Department")["Performance_Rating"].mean().reset_index()
    perf_dept.columns = ["Department", "Avg Rating"]
    perf_dept = perf_dept.sort_values("Avg Rating", ascending=False)
    fig_perf = px.bar(
        perf_dept, x="Department", y="Avg Rating",
        color="Department", color_discrete_map=DEPT_COLORS,
        title="Avg Performance Rating by Department",
        text="Avg Rating",
    )
    fig_perf.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig_perf.update_layout(
        plot_bgcolor="white", paper_bgcolor="white", font_family="Inter",
        title_font_size=14, margin=dict(t=50, b=20, l=0, r=0),
        showlegend=False,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9", range=[0, 5.5]),
    )
    st.plotly_chart(fig_perf, use_container_width=True)

with col10:
    edu_counts = fdf.groupby(["Education", "Attrition"]).size().reset_index(name="Count")
    fig_edu = px.bar(
        edu_counts, x="Education", y="Count", color="Attrition",
        color_discrete_map={"Yes": "#ef4444", "No": "#10b981"},
        title="Attrition by Education Level",
        barmode="stack", text="Count",
    )
    fig_edu.update_traces(textposition="inside")
    fig_edu.update_layout(
        plot_bgcolor="white", paper_bgcolor="white", font_family="Inter",
        title_font_size=14, margin=dict(t=50, b=20, l=0, r=0),
        legend=dict(title="Attrition", orientation="h", y=1.12),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
    )
    st.plotly_chart(fig_edu, use_container_width=True)

# ── Row 5: City & Salary vs Experience ───────────────────────────────────────
st.markdown('<div class="section-header">🏙️ City & Compensation Insights</div>', unsafe_allow_html=True)

col11, col12 = st.columns(2)

with col11:
    city_data = fdf.groupby("City").agg(
        Employees=("Employee_ID", "count"),
        Avg_Salary=("Salary", "mean"),
        Attrition_Rate=("Attrition_Num", "mean")
    ).reset_index()
    city_data["Attrition_Rate %"] = (city_data["Attrition_Rate"] * 100).round(1)

    fig_city = go.Figure()
    fig_city.add_trace(go.Bar(
        x=city_data["City"], y=city_data["Employees"],
        name="Employees", marker_color="#1a56db", opacity=0.85, yaxis="y"
    ))
    fig_city.add_trace(go.Scatter(
        x=city_data["City"], y=city_data["Attrition_Rate %"],
        name="Attrition %", mode="lines+markers",
        marker=dict(color="#ef4444", size=9),
        line=dict(color="#ef4444", width=2), yaxis="y2"
    ))
    fig_city.update_layout(
        title="Employees & Attrition Rate by City",
        plot_bgcolor="white", paper_bgcolor="white", font_family="Inter",
        title_font_size=14, margin=dict(t=50, b=20, l=0, r=60),
        legend=dict(orientation="h", y=1.12),
        yaxis=dict(title="Employees", showgrid=True, gridcolor="#f1f5f9"),
        yaxis2=dict(title="Attrition %", overlaying="y", side="right", showgrid=False),
        xaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig_city, use_container_width=True)

with col12:
    sample = fdf.sample(min(500, len(fdf)), random_state=42)
    fig_scatter = px.scatter(
        sample, x="Experience_Years", y="Salary",
        color="Department", color_discrete_map=DEPT_COLORS,
        symbol="Attrition",
        symbol_map={"Yes": "x", "No": "circle"},
        title="Salary vs Experience (✕ = Left)",
        opacity=0.7,
        hover_data=["Job_Role", "City"],
    )
    fig_scatter.update_layout(
        plot_bgcolor="white", paper_bgcolor="white", font_family="Inter",
        title_font_size=14, margin=dict(t=50, b=20, l=0, r=0),
        xaxis=dict(showgrid=True, gridcolor="#f1f5f9", title="Experience (Years)"),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9", title="Salary (₹)"),
        legend=dict(orientation="v", x=1.02),
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# ── Key Insights ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">💡 Key HR Insights</div>', unsafe_allow_html=True)

highest_att_dept = fdf.groupby("Department")["Attrition_Num"].mean().idxmax()
highest_att_pct  = fdf.groupby("Department")["Attrition_Num"].mean().max() * 100
lowest_att_dept  = fdf.groupby("Department")["Attrition_Num"].mean().idxmin()
highest_sal_dept = fdf.groupby("Department")["Salary"].mean().idxmax()
highest_sal_val  = fdf.groupby("Department")["Salary"].mean().max()
top_city         = fdf["City"].value_counts().idxmax()
male_pct         = (fdf["Gender"] == "Male").mean() * 100
female_pct       = 100 - male_pct
high_perf_att    = fdf[fdf["Performance_Rating"] >= 4]["Attrition_Num"].mean() * 100
low_perf_att     = fdf[fdf["Performance_Rating"] <= 2]["Attrition_Num"].mean() * 100

insights = [
    f"⚠️ <b>{highest_att_dept}</b> has the highest attrition rate at <b>{highest_att_pct:.1f}%</b> — needs urgent HR attention.",
    f"✅ <b>{lowest_att_dept}</b> has the lowest attrition — benchmark their engagement practices.",
    f"💰 <b>{highest_sal_dept}</b> pays the highest average salary of <b>₹{highest_sal_val:,.0f}</b>.",
    f"🏙️ <b>{top_city}</b> has the largest workforce concentration across all departments.",
    f"👥 Workforce is <b>{male_pct:.0f}% Male</b> and <b>{female_pct:.0f}% Female</b> — consider diversity initiatives.",
    f"⭐ High performers (rating ≥4) have <b>{high_perf_att:.1f}%</b> attrition vs <b>{low_perf_att:.1f}%</b> for low performers.",
]

ic1, ic2 = st.columns(2)
for i, insight in enumerate(insights):
    col = ic1 if i % 2 == 0 else ic2
    with col:
        st.markdown(f'<div class="insight-box">💬 {insight}</div>', unsafe_allow_html=True)

# ── Raw Data Explorer ─────────────────────────────────────────────────────────
with st.expander("📋 View Employee Data"):
    st.dataframe(
        fdf[["Employee_ID", "Age", "Gender", "Department", "Job_Role",
             "City", "Education", "Experience_Years", "Salary",
             "Performance_Rating", "Attrition", "Joining_Date"]]
        .sort_values("Joining_Date", ascending=False)
        .reset_index(drop=True),
        use_container_width=True, height=350,
    )
    st.caption(f"Showing {len(fdf):,} employees based on current filters.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<center style='color:#94a3b8;font-size:0.82rem;'>"
    "HR Analytics Dashboard · Built with Streamlit & Plotly · "
    "👨‍💻 Adil Sujaoddin Maniyar</center>",
    unsafe_allow_html=True,
)
