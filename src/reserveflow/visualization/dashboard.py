"""
Interactive Dashboard for ReserveFlow using Dash
"""

import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

from ..simulation import ReserveFlowSimulation
from ..config import DefaultConfig
from .charts import create_exchange_rate_chart, create_precious_metals_chart, create_risk_dashboard


class ReserveFlowDashboard:
    """Interactive dashboard for ReserveFlow simulation monitoring"""
    
    def __init__(self, port: int = 8050):
        """Initialize the dashboard"""
        self.app = dash.Dash(__name__)
        self.port = port
        self.simulation = None
        self.current_results = None
        
        # Setup layout
        self._setup_layout()
        self._setup_callbacks()
    
    def _setup_layout(self):
        """Setup the dashboard layout"""
        self.app.layout = html.Div([
            # Header
            html.Div([
                html.H1("ReserveFlow Simulation Dashboard", className="header-title"),
                html.P("Real-time monitoring of international currency reserves and precious metal dynamics", 
                       className="header-subtitle"),
            ], className="header"),
            
            # Control Panel
            html.Div([
                html.Div([
                    html.H3("Simulation Controls"),
                    
                    html.Label("Scenario:"),
                    dcc.Dropdown(
                        id='scenario-dropdown',
                        options=[
                            {'label': 'Baseline', 'value': 'baseline'},
                            {'label': 'Crisis', 'value': 'crisis'},
                            {'label': 'De-dollarization', 'value': 'dedollarization'},
                            {'label': 'Inflation Surge', 'value': 'inflation_surge'}
                        ],
                        value='baseline'
                    ),
                    
                    html.Label("Duration (months):"),
                    dcc.Slider(
                        id='duration-slider',
                        min=6,
                        max=60,
                        value=24,
                        marks={i: str(i) for i in range(6, 61, 6)},
                        step=1
                    ),
                    
                    html.Button('Run Simulation', id='run-button', n_clicks=0),
                    
                ], className="control-panel"),
            ], className="controls"),
            
            # Status and Progress
            html.Div([
                html.Div(id="status-output"),
                dcc.Interval(id='interval-component', interval=1000, n_intervals=0),
            ], className="status-bar"),
            
            # Main Charts
            html.Div([
                # Top row
                html.Div([
                    dcc.Graph(id='precious-metals-chart'),
                    dcc.Graph(id='exchange-rates-chart'),
                ], className="chart-row"),
                
                # Bottom row
                html.Div([
                    dcc.Graph(id='risk-dashboard'),
                    dcc.Graph(id='allocation-chart'),
                ], className="chart-row"),
            ], className="charts-container"),
            
            # Summary Statistics
            html.Div([
                html.H3("Summary Statistics"),
                html.Div(id="summary-stats"),
            ], className="summary-section"),
            
        ], className="dashboard-container")
    
    def _setup_callbacks(self):
        """Setup dashboard callbacks"""
        
        @self.app.callback(
            [Output('status-output', 'children'),
             Output('precious-metals-chart', 'figure'),
             Output('exchange-rates-chart', 'figure'),
             Output('risk-dashboard', 'figure'),
             Output('allocation-chart', 'figure'),
             Output('summary-stats', 'children')],
            [Input('run-button', 'n_clicks')],
            [dash.dependencies.State('scenario-dropdown', 'value'),
             dash.dependencies.State('duration-slider', 'value')]
        )
        def update_dashboard(n_clicks, scenario, duration):
            """Update dashboard when simulation is run"""
            if n_clicks == 0:
                # Initial state
                empty_fig = go.Figure()
                return ("Ready to run simulation", empty_fig, empty_fig, empty_fig, empty_fig, "No simulation data")
            
            try:
                # Run simulation
                status = f"Running {scenario} scenario for {duration} months..."
                
                config = self._get_scenario_config(scenario)
                sim = ReserveFlowSimulation(config)
                results = sim.run_scenario(scenario, duration_months=duration)
                
                self.current_results = results
                
                # Create charts
                pm_chart = create_precious_metals_chart(results)
                fx_chart = create_exchange_rate_chart(results)
                risk_chart = create_risk_dashboard(results)
                allocation_chart = self._create_allocation_chart(results)
                
                # Generate summary
                summary = self._generate_summary_stats(results)
                
                status = f"✓ Simulation completed: {len(results)} data points generated"
                
                return (status, pm_chart, fx_chart, risk_chart, allocation_chart, summary)
                
            except Exception as e:
                error_fig = go.Figure().add_annotation(text=f"Error: {str(e)}")
                return (f"❌ Error: {str(e)}", error_fig, error_fig, error_fig, error_fig, "Error in simulation")
    
    def _get_scenario_config(self, scenario: str):
        """Get configuration for scenario"""
        from ..config import CrisisConfig, DepollarizationConfig, InflationSurgeConfig
        
        configs = {
            'baseline': DefaultConfig(),
            'crisis': CrisisConfig(),
            'dedollarization': DepollarizationConfig(),
            'inflation_surge': InflationSurgeConfig()
        }
        return configs.get(scenario, DefaultConfig())
    
    def _create_allocation_chart(self, results: pd.DataFrame) -> go.Figure:
        """Create reserve allocation chart"""
        fig = go.Figure()
        
        if 'current_allocation' in results.columns:
            # Extract allocation data
            allocation_data = {}
            for idx, row_data in results.iterrows():
                if isinstance(row_data['current_allocation'], dict):
                    for asset, allocation in row_data['current_allocation'].items():
                        if asset not in allocation_data:
                            allocation_data[asset] = []
                        allocation_data[asset].append(allocation * 100)
            
            # Create stacked area chart
            for asset in allocation_data:
                fig.add_trace(go.Scatter(
                    x=results.index,
                    y=allocation_data[asset],
                    name=asset.upper(),
                    stackgroup='one',
                    mode='lines'
                ))
        
        fig.update_layout(
            title="Reserve Allocation Evolution",
            xaxis_title="Date",
            yaxis_title="Allocation (%)",
            yaxis=dict(range=[0, 100])
        )
        
        return fig
    
    def _generate_summary_stats(self, results: pd.DataFrame) -> html.Div:
        """Generate summary statistics"""
        stats = []
        
        # Gold statistics
        if 'gold_price' in results.columns:
            initial_gold = results['gold_price'].iloc[0]
            final_gold = results['gold_price'].iloc[-1]
            gold_return = (final_gold / initial_gold - 1) * 100
            
            stats.append(html.Div([
                html.H4("Gold Performance"),
                html.P(f"Price: ${initial_gold:.0f} → ${final_gold:.0f}"),
                html.P(f"Return: {gold_return:+.1f}%", 
                       style={'color': 'green' if gold_return > 0 else 'red'})
            ], className="stat-box"))
        
        # Risk metrics
        if 'geopolitical_risk' in results.columns:
            avg_risk = results['geopolitical_risk'].mean()
            max_risk = results['geopolitical_risk'].max()
            
            stats.append(html.Div([
                html.H4("Risk Metrics"),
                html.P(f"Avg Geopolitical Risk: {avg_risk:.3f}"),
                html.P(f"Max Risk Level: {max_risk:.3f}")
            ], className="stat-box"))
        
        # Market stress
        if 'market_stress' in results.columns:
            avg_stress = results['market_stress'].mean()
            crisis_days = (results['market_stress'] > 0.7).sum()
            
            stats.append(html.Div([
                html.H4("Market Stress"),
                html.P(f"Average: {avg_stress:.3f}"),
                html.P(f"Crisis Days: {crisis_days}")
            ], className="stat-box"))
        
        return html.Div(stats, className="stats-grid")
    
    def run_server(self, debug: bool = True):
        """Run the dashboard server"""
        print(f"Starting ReserveFlow Dashboard on http://localhost:{self.port}")
        self.app.run_server(debug=debug, port=self.port)


# CSS Styling
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

def create_dashboard_css():
    """Create custom CSS for the dashboard"""
    return """
    .dashboard-container {
        font-family: Arial, sans-serif;
        margin: 20px;
    }
    
    .header {
        text-align: center;
        background-color: #2E86AB;
        color: white;
        padding: 20px;
        margin-bottom: 20px;
        border-radius: 10px;
    }
    
    .header-title {
        margin: 0;
        font-size: 2.5em;
    }
    
    .header-subtitle {
        margin: 10px 0 0 0;
        font-size: 1.2em;
        opacity: 0.9;
    }
    
    .controls {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    
    .control-panel {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 20px;
        align-items: end;
    }
    
    .status-bar {
        background-color: #e9ecef;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 20px;
        text-align: center;
    }
    
    .charts-container {
        margin-bottom: 20px;
    }
    
    .chart-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        margin-bottom: 20px;
    }
    
    .summary-section {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
        margin-top: 15px;
    }
    
    .stat-box {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .stat-box h4 {
        margin: 0 0 10px 0;
        color: #2E86AB;
    }
    
    .stat-box p {
        margin: 5px 0;
    }
    """


if __name__ == "__main__":
    # Example usage
    dashboard = ReserveFlowDashboard()
    dashboard.run_server() 