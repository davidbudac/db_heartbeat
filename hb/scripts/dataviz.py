import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import base64

def generate_report_plotly(df, filename="database_performance_report_plotly.html"):
    """Generates an HTML report with interactive Plotly visualizations."""

    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Database Performance Report (Plotly)</title>
        <style>
            body { font-family: sans-serif; }
            h1, h2 { color: navy; }
            .figure-container {
                margin-bottom: 20px;
                border: 1px solid #ddd;
                padding: 10px;
                border-radius: 5px;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin-top: 20px;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
            }
        </style>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script> 
    </head>
    <body>
        <h1>Database Performance Report (Plotly)</h1>
    """

    # --- Overall Duration Distribution ---
    fig1 = px.histogram(df, x='duration_ms', nbins=50, marginal="box",
                        title='Distribution of Operation Durations (ms)')
    fig1.update_layout(xaxis_title='Duration (ms)', yaxis_title='Frequency')
    html_content += f"<div class='figure-container'><h2>Overall Duration Distribution</h2>{fig1.to_html(full_html=False, include_plotlyjs=False)}</div>"  # Use to_html

    # --- Boxplot of Duration by Operation ---
    fig2 = px.box(df, x='operation', y='duration_ms', title='Operation Duration by Operation Type',
                  color='operation',  # Add color for better distinction
                  log_y=True)  # Log scale
    fig2.update_layout(xaxis_title='Operation', yaxis_title='Duration (ms)')
    html_content += f"<div class='figure-container'><h2>Duration by Operation</h2>{fig2.to_html(full_html=False, include_plotlyjs=False)}</div>"

    # --- Boxplot of Duration by Database ---
    fig3 = px.box(df, x='database', y='duration_ms', title='Operation Duration by Database',
                  color='database', log_y=True)
    fig3.update_layout(xaxis_title='Database', yaxis_title='Duration (ms)')
    html_content += f"<div class='figure-container'><h2>Duration by Database</h2>{fig3.to_html(full_html=False, include_plotlyjs=False)}</div>"

    # --- Boxplot of Duration by Database and Operation ---
    fig4 = px.box(df, x='database', y='duration_ms', color='operation',
                  title='Operation Duration by Database and Operation', log_y=True)
    fig4.update_layout(xaxis_title='Database', yaxis_title='Duration (ms)')
    html_content += f"<div class='figure-container'><h2>Duration by Database and Operation</h2>{fig4.to_html(full_html=False, include_plotlyjs=False)}</div>"

    # --- Time Series Plot of Durations (with custom rolling average)---
    df['rolling_duration'] = df['duration_ms'].rolling(window=50).mean()
    fig5 = px.line(df, x='timestamp', y='rolling_duration', title='Operation Duration Over Time (Rolling Average)')
    fig5.update_layout(xaxis_title='Timestamp', yaxis_title='Duration (ms) - Rolling Avg')
    html_content += f"<div class='figure-container'><h2>Duration Over Time</h2>{fig5.to_html(full_html=False, include_plotlyjs=False)}</div>"

   # --- Time Series of operation count per minute ---
    df_resampled = df.set_index('timestamp').resample('1T').count().reset_index()  # Reset index
    fig6 = px.line(df_resampled, x='timestamp', y='operation', title='Number of Database Operations per Minute')
    fig6.update_layout(xaxis_title='Timestamp', yaxis_title='Count')
    html_content += f"<div class='figure-container'><h2>Operations per Minute</h2>{fig6.to_html(full_html=False, include_plotlyjs=False)}</div>"

    # --- Time between operations
    fig7 = px.histogram(df, x='time_between_ms', nbins=50, marginal="box", title='Distribution of Time Between Operations (ms)')
    fig7.update_layout(xaxis_title='Time Between (ms)', yaxis_title='Frequency')
    html_content += f"<div class='figure-container'><h2>Time Between Operations</h2>{fig7.to_html(full_html=False, include_plotlyjs=False)}</div>"
    
    # --- Connect operation durations
    connect_df = df[df['operation'] == 'connect']
    fig8 = px.box(connect_df, x='database', y='duration_ms', color='database', title='Connect Operation Duration by Database')
    fig8.update_layout(xaxis_title='Database', yaxis_title='Duration (ms)')
    html_content += f"<div class='figure-container'><h2>Connect Operation Duration</h2>{fig8.to_html(full_html=False, include_plotlyjs=False)}</div>"

    # --- Visualize Concurrency (Custom Plotly Graph) ---
    df['count'] = 1
    pivot_df = df.pivot_table(index='timestamp', columns='database', values='count', aggfunc='sum')
    pivot_df = pivot_df.resample('100ms').sum()
    pivot_df = pivot_df.fillna(0)
    pivot_df['concurrency'] = pivot_df.sum(axis=1)
    fig9 = px.line(pivot_df, x=pivot_df.index, y='concurrency', title='Database Concurrency Over Time')  # Use px.line
    fig9.update_layout(xaxis_title='Timestamp', yaxis_title='Concurrent Operations')
    html_content += f"<div class='figure-container'><h2>Database Concurrency</h2>{fig9.to_html(full_html=False, include_plotlyjs=False)}</div>"



      # --- Enhanced time series
    connect_df = df[df['operation'] == 'connect'].copy()
    other_ops_df = df[df['operation'] != 'connect'].copy()
    connect_df['rolling_duration'] = connect_df['duration_ms'].rolling(window=50).mean()
    other_ops_df['rolling_duration'] = other_ops_df['duration_ms'].rolling(window=50).mean()

    fig10 = go.Figure()  # Create a figure object
    fig10.add_trace(go.Scatter(x=other_ops_df['timestamp'], y=other_ops_df['rolling_duration'], mode='lines', name='Other Operations')) #Add traces separately
    fig10.add_trace(go.Scatter(x=connect_df['timestamp'], y=connect_df['rolling_duration'], mode='lines', name='Connect Operations'))

    fig10.update_layout(title='Operation Duration Over Time (Rolling Average)',
                    xaxis_title='Timestamp',
                    yaxis_title='Duration (ms) - Rolling Average')

    html_content += f"<div class='figure-container'><h2>Operation Duration Over Time</h2>{fig10.to_html(full_html=False, include_plotlyjs=False)}</div>"

    # --- Identify and display the slowest operations ---
    slowest_operations = df.nlargest(10, 'duration_ms')
    html_content += f"""
        <div class='figure-container'>
            <h2>Slowest Operations</h2>
            {slowest_operations.to_html(index=False)}
        </div>
    """

    html_content += """
    </body>
    </html>
    """

    with open(filename, "w") as f:
        f.write(html_content)

if __name__ == '__main__':
    # Load the data
    df = pd.read_csv("../logs/log.csv")

    # Convert timestamp to datetime objects
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    generate_report_plotly(df, "../reports/database_performance_report_plotly.html")
    print("Report generated: reports/database_performance_report_plotly.html")