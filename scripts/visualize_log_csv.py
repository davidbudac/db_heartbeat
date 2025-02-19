import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import base64
import argparse
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, ALL

# Modify the generate_report_plotly function to create an interactive Dash app
def generate_report_plotly(df, filename="database_performance_report.html", port=8050):
    app = Dash(__name__)
    
    # Get unique values for filters
    databases = sorted(df['database'].unique())
    operations = sorted(df['operation'].unique())
    
    # Custom CSS for better styling
    app.layout = html.Div([
        # Header
        html.Div([
            html.H1('Database Performance Dashboard', 
                   style={'textAlign': 'center', 'color': '#2c3e50', 'margin': '20px 0'}),
            
            # Filter controls in a row
            html.Div([
                html.Div([
                    html.Label('Database Filter:', style={'fontWeight': 'bold', 'marginBottom': '10px', 'display': 'block'}),
                    dcc.Checklist(
                        id='database-filter',
                        options=[{'label': db, 'value': db} for db in databases],
                        value=databases,
                        inline=True,
                        labelStyle={'marginRight': '15px'}
                    )
                ], style={'width': '100%', 'marginBottom': '20px'}),
                
                html.Div([
                    html.Label('Operation Filter:', style={'fontWeight': 'bold', 'marginBottom': '10px', 'display': 'block'}),
                    dcc.Checklist(
                        id='operation-filter',
                        options=[{'label': op, 'value': op} for op in operations],
                        value=operations,
                        inline=True,
                        labelStyle={'marginRight': '15px'}
                    )
                ], style={'width': '100%'})
            ], style={'padding': '20px'}),
        ], style={'backgroundColor': '#f8f9fa', 'padding': '20px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),

        # Grid layout for graphs
        html.Div([
            # Row 1 - Raw duration time series
            html.Div([
                dcc.Graph(id='raw-duration-series')
            ], style={'marginBottom': '20px'}),

            # Row 2 - Raw time between operations
            html.Div([
                dcc.Graph(id='raw-time-between')
            ], style={'marginBottom': '20px'}),

            # Row 3 - Rolling average time series
            html.Div([
                dcc.Graph(id='time-series')
            ], style={'marginBottom': '20px'}),

            # Row 4 - Duration histogram and time between ops
            html.Div([
                html.Div([
                    dcc.Graph(id='duration-histogram')
                ], style={'width': '50%', 'display': 'inline-block'}),
                
                html.Div([
                    dcc.Graph(id='time-between-ops')
                ], style={'width': '50%', 'display': 'inline-block'}),
            ], style={'marginBottom': '20px'}),

            # Row 5 - Operation and database boxplots
            html.Div([
                html.Div([
                    dcc.Graph(id='operation-boxplot')
                ], style={'width': '50%', 'display': 'inline-block'}),
                
                html.Div([
                    dcc.Graph(id='database-boxplot')
                ], style={'width': '50%', 'display': 'inline-block'}),
            ]),
        ], style={'padding': '20px'}),
    ], style={'backgroundColor': '#ffffff', 'fontFamily': 'Arial, sans-serif'})

    @app.callback(
        [Output('raw-duration-series', 'figure'),
         Output('raw-time-between', 'figure'),
         Output('duration-histogram', 'figure'),
         Output('operation-boxplot', 'figure'),
         Output('database-boxplot', 'figure'),
         Output('time-series', 'figure'),
         Output('time-between-ops', 'figure')],
        [Input('database-filter', 'value'),
         Input('operation-filter', 'value')]
    )
    def update_graphs(selected_dbs, selected_ops):
        # Filter dataframe based on selections
        filtered_df = df[
            (df['database'].isin(selected_dbs)) &
            (df['operation'].isin(selected_ops))
        ]
        
        # Define symbols for different operations
        operation_symbols = {op: i for i, op in enumerate(operations)}
        
        # Raw duration time series with symbols
        fig_raw = go.Figure()
        for db in selected_dbs:
            db_data = filtered_df[filtered_df['database'] == db]
            for op in selected_ops:
                op_data = db_data[db_data['operation'] == op]
                fig_raw.add_trace(go.Scatter(
                    x=op_data['timestamp'],
                    y=op_data['duration_ms'],
                    name=f"{db} - {op}",
                    mode='markers',
                    marker=dict(
                        size=6,
                        symbol=operation_symbols[op],
                    ),
                    hovertemplate="<b>%{text}</b><br>" +
                                "Database: " + db + "<br>" +
                                "Operation: " + op + "<br>" +
                                "Time: %{x}<br>" +
                                "Duration: %{y:.2f} ms<br>" +
                                "<extra></extra>",
                    text=op_data['operation']
                ))

        fig_raw.update_layout(
            title='Raw Operation Duration Over Time',
            xaxis_title='Timestamp',
            yaxis_title='Duration (ms)',
            showlegend=True
        )

        # Raw time between operations with symbols
        fig_raw_between = go.Figure()
        for db in selected_dbs:
            db_data = filtered_df[filtered_df['database'] == db]
            for op in selected_ops:
                op_data = db_data[db_data['operation'] == op]
                fig_raw_between.add_trace(go.Scatter(
                    x=op_data['timestamp'],
                    y=op_data['time_between_ms'],
                    name=f"{db} - {op}",
                    mode='markers',
                    marker=dict(
                        size=6,
                        symbol=operation_symbols[op],
                    ),
                    hovertemplate="<b>%{text}</b><br>" +
                                "Database: " + db + "<br>" +
                                "Operation: " + op + "<br>" +
                                "Time: %{x}<br>" +
                                "Time Between: %{y:.2f} ms<br>" +
                                "<extra></extra>",
                    text=op_data['operation']
                ))
        
        fig_raw_between.update_layout(
            title='Raw Time Between Operations Over Time',
            xaxis_title='Timestamp',
            yaxis_title='Time Between (ms)',
            showlegend=True
        )

        # Duration histogram
        fig1 = px.histogram(filtered_df, x='duration_ms', nbins=50, 
                          marginal="box",
                          title='Distribution of Operation Durations (ms)')
        
        # Operation boxplot
        fig2 = px.box(filtered_df, x='operation', y='duration_ms',
                     title='Operation Duration by Operation Type',
                     color='operation', log_y=True)
        
        # Database boxplot
        fig3 = px.box(filtered_df, x='database', y='duration_ms',
                     title='Operation Duration by Database',
                     color='database', log_y=True)
        
        # Rolling average time series with symbols
        fig4 = go.Figure()
        for db in selected_dbs:
            db_data = filtered_df[filtered_df['database'] == db]
            for op in selected_ops:
                op_data = db_data[db_data['operation'] == op]
                op_data['rolling_duration'] = op_data['duration_ms'].rolling(window=50).mean()
                fig4.add_trace(go.Scatter(
                    x=op_data['timestamp'],
                    y=op_data['rolling_duration'],
                    name=f"{db} - {op}",
                    mode='markers',
                    marker=dict(
                        size=8,
                        symbol=operation_symbols[op],
                    ),
                    hovertemplate="<b>%{text}</b><br>" +
                                "Database: " + db + "<br>" +
                                "Operation: " + op + "<br>" +
                                "Time: %{x}<br>" +
                                "Rolling Avg Duration: %{y:.2f} ms<br>" +
                                "<extra></extra>",
                    text=op_data['operation']
                ))
        
        fig4.update_layout(
            title='Operation Duration Over Time (Rolling Average)',
            xaxis_title='Timestamp',
            yaxis_title='Duration (ms)',
            showlegend=True
        )
        
        # Time between operations
        fig6 = px.histogram(filtered_df, x='time_between_ms', nbins=50,
                          marginal="box",
                          title='Distribution of Time Between Operations (ms)')
        
        # Update all figures with consistent styling
        template = 'plotly_white'
        height = 400

        figures = [fig_raw, fig_raw_between, fig1, fig2, fig3, fig4, fig6]

        for fig in figures:
            fig.update_layout(
                template=template,
                height=height,
                margin={'l': 40, 'r': 40, 't': 40, 'b': 40},
                legend={'orientation': 'h', 'y': -0.2},
                plot_bgcolor='white',
                paper_bgcolor='white',
                font={'family': 'Arial, sans-serif'},
                xaxis={'gridcolor': '#eee'},
                yaxis={'gridcolor': '#eee'}
            )

        return fig_raw, fig_raw_between, fig1, fig2, fig3, fig4, fig6

    print(f"\nDashboard is running at: http://localhost:{port}")
    print("Press Ctrl+C to quit")
    
    # Run the server
    app.run_server(debug=False, port=port)

def main():
    parser = argparse.ArgumentParser(description='Generate database performance visualization report')
    parser.add_argument('input_file', help='Input CSV log file to analyze')
    parser.add_argument('--port', type=int, default=8050,
                       help='Port to run the Dash server (default: 8050)')
    
    args = parser.parse_args()
    
    try:
        df = pd.read_csv(args.input_file)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        print(f"Starting visualization server on port {args.port}...")
        generate_report_plotly(df, port=args.port)
        
    except FileNotFoundError:
        print(f"Error: Input file '{args.input_file}' not found")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    main()