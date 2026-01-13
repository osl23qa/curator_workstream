import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Team Application Usage Dashboard", layout="wide")
st.title("Team Application Usage Dashboard")

# File uploader
uploaded_file = st.file_uploader("Upload App Usage CSV", type=["csv"])

if uploaded_file:
    alerts = []
    df = pd.read_csv(uploaded_file)
    # Clean and parse dates
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df['WrittenAt'] = pd.to_datetime(df['WrittenAt'], errors='coerce')
    df = df.dropna(subset=['Date'])

    # Sidebar filters
    st.sidebar.header("Filters")
    unique_dates = sorted(df['Date'].dt.date.unique())
    unique_hosts = sorted(df['Host'].unique())
    unique_users = sorted(df['User'].unique())
    unique_apps = sorted(df['Application'].unique())

    st.sidebar.markdown("""
        <style>
        .modern-filter-label {
            color: #0d47a1;
            font-weight: 600;
            font-size: 15px;
            margin-bottom: 4px;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar.expander("🔎 Filter Data", expanded=True):
        st.markdown('<div class="modern-filter-label">Date Range</div>', unsafe_allow_html=True)
        min_date, max_date = min(unique_dates), max(unique_dates)
        date_range = st.date_input("Select date range", value=(min_date, max_date), min_value=min_date, max_value=max_date, key="date_range")

        st.markdown('<div class="modern-filter-label">Host</div>', unsafe_allow_html=True)
        selected_host = st.selectbox("Select a host", options=["All"] + unique_hosts, key="host_select")

        # Custom pill-style checkboxes for users
        st.markdown('<div class="modern-filter-label">User(s)</div>', unsafe_allow_html=True)
        st.markdown("""
        <style>
        .pill-checkbox {
            display: inline-block;
            margin: 2px 6px 2px 0;
            padding: 6px 16px;
            border-radius: 20px;
            background: #e3f2fd;
            color: #1565c0;
            font-weight: 500;
            border: 2px solid #90caf9;
            cursor: pointer;
            transition: background 0.2s, color 0.2s;
        }
        .pill-checkbox.selected {
            background: #1565c0;
            color: #fff;
            border: 2px solid #1565c0;
        }
        </style>
        """, unsafe_allow_html=True)
        user_cols = st.columns(2)
        user_states = {}
        for i, user in enumerate(unique_users):
            with user_cols[i % 2]:
                checked = st.checkbox(user, value=True, key=f"user_pill_{user}")
                user_states[user] = checked
        selected_users = [u for u, v in user_states.items() if v]

        # Custom pill-style checkboxes for applications
        st.markdown('<div class="modern-filter-label">Application(s)</div>', unsafe_allow_html=True)
        app_cols = st.columns(2)
        app_states = {}
        for i, app in enumerate(unique_apps):
            with app_cols[i % 2]:
                checked = st.checkbox(app, value=True, key=f"app_pill_{app}")
                app_states[app] = checked
        selected_apps = [a for a, v in app_states.items() if v]

    # Apply new filter logic
    filtered_df = df.copy()
    # Date range filter
    if isinstance(date_range, tuple) and len(date_range) == 2:
        filtered_df = filtered_df[(filtered_df['Date'].dt.date >= date_range[0]) & (filtered_df['Date'].dt.date <= date_range[1])]
    # Host filter
    if selected_host != "All":
        filtered_df = filtered_df[filtered_df['Host'] == selected_host]
    # User filter
    if selected_users:
        filtered_df = filtered_df[filtered_df['User'].isin(selected_users)]
    # Application filter
    if selected_apps:
        filtered_df = filtered_df[filtered_df['Application'].isin(selected_apps)]

    st.subheader("Summary Statistics (Filtered)")
    import pandas as pd
    stats_dict = {
        "Total Records": len(filtered_df),
        "Unique Users": filtered_df['User'].nunique(),
        "Unique Applications": filtered_df['Application'].nunique(),
        "Unique Hosts": filtered_df['Host'].nunique()
    }
    stats_df = pd.DataFrame([stats_dict])
    # Gradient for each cell
    from matplotlib import colors
    minv, maxv = stats_df.min(axis=1)[0], stats_df.max(axis=1)[0]
    # Custom HTML/CSS for a wide, appealing summary table
    gradient_colors = ["#e3f2fd", "#64b5f6", "#1976d2", "#1565c0"]
    values = list(stats_dict.values())
    metrics = list(stats_dict.keys())
    n = len(values)
    tds = ""
    for i, (metric, value) in enumerate(zip(metrics, values)):
        color = gradient_colors[i % len(gradient_colors)]
        font_color = '#222' if i < 2 else '#fff'
        tds += f'<td style="background:{color};color:{font_color};padding:24px 0;font-size:2em;font-weight:bold;text-align:center;border-radius:12px 12px 0 0;">{value}<div style="font-size:0.6em;font-weight:normal;margin-top:8px;letter-spacing:1px;">{metric}</div></td>'
    html = f'''
    <div style="width:100%;display:flex;justify-content:center;margin-bottom:24px;">
        <table style="width:100%;border-collapse:separate;border-spacing:16px 0;table-layout:fixed;">
            <tr>{tds}</tr>
        </table>
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)

    # Application usage summary (filtered)
    app_usage = filtered_df.groupby('Application')['Total_Active_Time_Minutes'].sum().sort_values(ascending=False)
    st.subheader("Application Usage Overview (Filtered)")
    colA, colB = st.columns(2)
    with colA:
        st.markdown("**Most Used Applications (Bar Chart)**")
        app_bar = go.Figure(go.Bar(
            x=app_usage.index,
            y=app_usage.values,
            marker_color=px.colors.qualitative.Set2,
            text=app_usage.values,
            textposition='auto'))
        app_bar.update_layout(
            height=350,
            margin=dict(t=30, b=30, l=0, r=0),
            xaxis_title='Application',
            yaxis_title='Total Minutes',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(app_bar, use_container_width=True, key="app_bar_chart")
    with colB:
        st.markdown("**Application Usage Distribution (Pie Chart)**")
        pie_fig = px.pie(
            app_usage.reset_index(),
            names='Application',
            values='Total_Active_Time_Minutes',
            title='Application Usage Distribution',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        pie_fig.update_traces(
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Minutes: %{value}<br>Percent: %{percent}<extra></extra>',
            hole=0.45, # donut style
            marker=dict(line=dict(color='#fff', width=2)),
            textfont_size=16
        )
        pie_fig.update_layout(
            showlegend=True,
            legend_title_text='Application',
            legend=dict(font=dict(size=14)),
            title_font_size=22,
            margin=dict(t=60, b=20, l=0, r=0),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(pie_fig, use_container_width=True, key="pie_chart")

    # User activity summary (filtered)
    user_usage = filtered_df.groupby('User')['Total_Active_Time_Minutes'].sum().sort_values(ascending=False)
    st.subheader("User Activity (Total Minutes, Filtered)")
    user_bar = go.Figure(go.Bar(
        x=user_usage.index,
        y=user_usage.values,
        marker_color=px.colors.qualitative.Set3,
        text=user_usage.values,
        textposition='auto'))
    user_bar.update_layout(
        height=350,
        margin=dict(t=30, b=30, l=0, r=0),
        xaxis_title='User',
        yaxis_title='Total Minutes',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(user_bar, use_container_width=True)

    # Top User Activity Progress and Work Pattern by Hour side by side
    colE, colF = st.columns(2)
    with colE:
        st.subheader("Top User Activity Progress (Filtered)")
        if not user_usage.empty:
            top_user = user_usage.index[0]
            top_minutes = user_usage.iloc[0]
            max_minutes = user_usage.max()
            percent = min(int(top_minutes / max_minutes * 100), 100) if max_minutes > 0 else 0
            st.markdown(f"**Top user:** {top_user}")
            # Horizontal bar chart for top user
            import plotly.graph_objects as go
            bar_fig = go.Figure(go.Bar(
                x=[top_minutes],
                y=[top_user],
                orientation='h',
                marker_color='#1976d2',
                text=[f"{top_minutes} min"],
                textposition='auto',
                width=[0.5]
            ))
            bar_fig.update_layout(
                xaxis=dict(range=[0, max(max_minutes, top_minutes + 10)], title='Active Minutes'),
                yaxis=dict(title=''),
                height=200,
                margin=dict(t=30, b=30, l=0, r=0),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(bar_fig, use_container_width=True, key="top_user_bar")
    with colF:
        st.subheader("Work Pattern by Hour (Filtered)")
        filtered_df['Hour'] = filtered_df['WrittenAt'].dt.hour
        hour_usage = filtered_df.groupby('Hour')['Total_Active_Time_Minutes'].sum()
        import plotly.graph_objects as go
        hour_fig = go.Figure()
        hour_labels = [f"{v} min" for v in hour_usage.values]
        hour_fig.add_trace(go.Scatter(
            x=hour_usage.index,
            y=hour_usage.values,
            mode='lines+markers+text',
            text=hour_labels,
            textposition='top center',
            line=dict(color='#43a047', width=3),
            marker=dict(size=8, color='#43a047'),
            name='Active Minutes'
        ))
        hour_fig.update_layout(
            xaxis_title='Hour of Day',
            yaxis_title='Total Active Minutes',
            height=350,
            margin=dict(t=30, b=30, l=0, r=0),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(hour_fig, use_container_width=True, key="hour_line_chart")

    # User activity and Host usage bar charts side by side
    user_usage = filtered_df.groupby('User')['Total_Active_Time_Minutes'].sum().sort_values(ascending=False)
    host_usage = filtered_df.groupby('Host')['Total_Active_Time_Minutes'].sum().sort_values(ascending=False)
    colC, colD = st.columns(2)
    with colC:
        st.subheader("User Activity (Total Minutes, Filtered)")
        user_bar = go.Figure(go.Bar(
            x=user_usage.index,
            y=user_usage.values,
            marker_color=px.colors.qualitative.Set3,
            text=user_usage.values,
            textposition='auto'))
        user_bar.update_layout(
            height=350,
            margin=dict(t=30, b=30, l=0, r=0),
            xaxis_title='User',
            yaxis_title='Total Minutes',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(user_bar, use_container_width=True, key="user_bar_chart")
    with colD:
        st.subheader("Host Usage (Total Minutes, Filtered)")
        host_bar = go.Figure(go.Bar(
            x=host_usage.index,
            y=host_usage.values,
            marker_color=px.colors.qualitative.Pastel,
            text=host_usage.values,
            textposition='auto'))
        host_bar.update_layout(
            height=350,
            margin=dict(t=30, b=30, l=0, r=0),
            xaxis_title='Host',
            yaxis_title='Total Minutes',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(host_bar, use_container_width=True, key="host_bar_chart")
    if alerts:
        for alert in alerts:
            st.warning(alert)
    else:
        st.success("No alerts detected.")
else:
    st.info("Please upload a CSV file to view the dashboard.")
