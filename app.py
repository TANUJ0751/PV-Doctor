import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime

# Load CSV
csv_file = "final_data.csv"
df = pd.read_csv(csv_file)

# Convert 'Date' to datetime
df['Date'] = pd.to_datetime(df['Date'], dayfirst=False)

#Date Filters
st.title("Performance Ration Evalutation")

start_date = st.date_input("Start Date", df['Date'].min().date())
end_date = st.date_input("End Date", df['Date'].max().date())




def show_graph(start_date,end_date):

    #Load CSV
    df = pd.read_csv(csv_file)

    # Convert 'Date' to datetime
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=False)    

    # Filter data
    df = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))].copy()

    # Sort data
    df = df.sort_values('Date').reset_index(drop=True)

    # 30-day PR moving average
    df['PR_30MA'] = df['PR'].rolling(window=30, min_periods=1).mean()

    # Budget PR Decay Logic
    initial_budget = 73.9
    annual_decay = 0.008
    budget_dict = {}

    current_year = 2019
    budget_value = initial_budget

    while pd.Timestamp(f'{current_year + 1}-06-30') <= df['Date'].max() + pd.Timedelta(days=365):
        start = pd.Timestamp(f'{current_year}-07-01')
        end = pd.Timestamp(f'{current_year + 1}-06-30')
        budget_dict[(start, end)] = budget_value
        budget_value *= (1 - annual_decay)
        current_year += 1

    def get_budget_pr(date):
        for (start, end), val in budget_dict.items():
            if start <= date <= end:
                return val
        return budget_value

    df['Budget_PR'] = df['Date'].apply(get_budget_pr)
    total_points=df['PR'].count()
    points_above_budget = (df['PR'] > df['Budget_PR']).sum()
    # GHI color coding
    def ghi_color(val):
        if val < 2:
            return 'navy'
        elif 2 <= val <= 4:
            return 'lightblue'
        elif 4 < val <= 6:
            return 'orange'
        else:
            return 'brown'

    df['Color'] = df['GHI'].apply(ghi_color)

    # Plotly Figure
    fig = go.Figure()

    # Scatter plot (PR)
    fig.add_trace(go.Scatter(
        x=df['Date'], y=df['PR'], mode='markers',
        marker=dict(color=df['Color'], size=4, line=dict(width=1, color='black')),
        name='Daily PR'
    ))

    # 30-day Moving Avg (Red Line)
    fig.add_trace(go.Scatter(
        x=df['Date'], y=df['PR_30MA'], mode='lines',
        line=dict(color='red', width=2),
        name='30-Day PR Moving Avg'
    ))
    # Add GHI legend entries (dummy traces for legend)
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=10, color='navy'),
        name='GHI < 2'
    ))
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=10, color='lightblue'),
        name='GHI 2–4'
    ))
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=10, color='orange'),
        name='GHI 4–6'
    ))
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=10, color='brown'),
        name='GHI > 6'
    ))

    # Budget PR (Green Line)
    fig.add_trace(go.Scatter(
        x=df['Date'], y=df['Budget_PR'], mode='lines',
        line=dict(color='darkgreen', width=2),
        name='Budget PR'
    ))

    # Add average PR text
    avg7 = df['PR'].tail(7).mean()
    avg30 = df['PR'].tail(30).mean()
    avg60 = df['PR'].tail(60).mean()
    avg90= df['PR'].tail(90).mean()
    avg365=df['PR'].tail(365).mean()
    avgLife=df['PR'].mean()

    fig.add_annotation(
        text=f"<b>Points above Target Budget PR : {points_above_budget}/{total_points} : {points_above_budget/(total_points*0.01):.2f}%</b><br>Average PR last 7-days: {avg7:.2f}<br>Average PR last 30-days: {avg30:.2f}<br>Average PR last 60-days: {avg60:.2f} <br>Average PR last 90-days: {avg90:.2f} <br>Average PR last 365-days: {avg365:.2f}<br> <b>Average PR Lifetime: {avgLife:.2f}</b>",
        xref="paper", yref="paper", x=0.99, y=0.01, showarrow=False,
        font=dict(size=12, color="black"), align="right",
        bordercolor="black", borderwidth=1, borderpad=4, bgcolor="white", opacity=0.8
    )
    background_color = "#dbe0ef"
    paper_color = "#181818"
    # Layout
    fig.update_layout(
        title=f"Performance Ratio (PR) Visualization (From {start_date} to {end_date} )",
        xaxis_title="Date", yaxis_title="PR",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            font=dict(color="white")
        ),
        plot_bgcolor=background_color,
        paper_bgcolor=paper_color,
        font=dict(color="white"),
        hovermode="x unified",
        xaxis=dict(
            gridcolor='rgba(255,255,255,0.2)',
            zerolinecolor='rgba(255,255,255,0.4)'
        ),
        yaxis=dict(
            range=[0,90],
            gridcolor='rgba(255,255,255,0.2)',
            zerolinecolor='rgba(255,255,255,0.4)'
        ),
    )

    # Show Plotly Graph 
    st.plotly_chart(fig, use_container_width=True)

if st.button("Generate PR Graph"): # Displays Graph on button Click
    show_graph(start_date, end_date)
st.write("------")
st.subheader("Author")
st.write("This project is made by **Tanuj Jain** for assignment submission for **PV Doctor Private Limited**.")
st.write("------")
st.subheader("Description")
st.write('''This project processes and visualizes Performance Ratio (PR) and Global Horizontal Irradiance (GHI) data for a Photovoltaic (PV) plant.
It includes the following features:

**✅ Data Processing:**
- Combines multiple CSV files containing daily PR and GHI data into a single dataset.
- Calculates the 30-day moving average of PR.
- Dynamically computes the annual Budget PR decay based on a 0.8% yearly reduction starting from July 2019.

**✅ Interactive Visualization:**
- Generates an interactive scatter plot using Plotly, with PR values as points and GHI values represented by color.
- Highlights the 30-day moving average and Budget PR decay line.
         
Color codes the PR points based on GHI ranges:
- **Navy Blue:** GHI < 2
- **Light Blue:** GHI 2–4
- **Orange:** GHI 4–6
- **Brown:** GHI > 6

**✅ Dynamic Features:**
- Displays the total number of days where the PR exceeded the Budget PR.
- Allows users to filter data by custom date ranges.
- Shows average PR values for the last 7, 30, and 60 days.

**✅ Interactive Web App:**
- Built with Streamlit and Plotly, the app provides an interactive dashboard that is user-friendly and responsive.

''')
st.write("-------")
