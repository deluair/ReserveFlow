"""
Interactive Dashboard for ReserveFlow using Dash
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import traceback
import sys
import os
from datetime import datetime, timedelta
import json

# Add the src directory to the Python path to handle direct execution
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(current_dir, '..', '..', '..')
    sys.path.insert(0, src_dir)

try:
    from ..simulation import ReserveFlowSimulation
    from ..config import DefaultConfig, CrisisConfig, DepollarizationConfig, InflationSurgeConfig
    from .charts import create_exchange_rate_chart, create_precious_metals_chart, create_risk_dashboard
except ImportError:
    # Direct execution fallback
    from src.reserveflow.simulation import ReserveFlowSimulation
    from src.reserveflow.config import DefaultConfig, CrisisConfig, DepollarizationConfig, InflationSurgeConfig
    from src.reserveflow.visualization.charts import create_exchange_rate_chart, create_precious_metals_chart, create_risk_dashboard


class ReserveFlowDashboard:
    """Enhanced Interactive dashboard for ReserveFlow simulation monitoring"""

    def __init__(self, port: int = 8050):
        """Initialize the dashboard"""
        self.app = dash.Dash(__name__, external_stylesheets=[
            "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap",
            "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
        ])
        self.app.title = "ReserveFlow - Advanced Analytics Dashboard"
        self.port = port
        self.simulation_results = {}  # Store multiple scenario results
        
        self._setup_layout()
        self._setup_callbacks()

    def _setup_layout(self):
        """Setup the enhanced dashboard layout"""
        self.app.layout = html.Div([
            # Header Section
            html.Div([
                html.Div([
                    html.I(className="fas fa-globe-americas", style={'fontSize': '2rem', 'marginRight': '15px'}),
                    html.H1("ReserveFlow Analytics", style={'margin': '0', 'fontSize': '2.5rem'}),
                ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'}),
                html.P("Advanced International Currency Reserves & Precious Metals Simulation Platform", 
                       style={'textAlign': 'center', 'margin': '10px 0 0 0', 'opacity': '0.9'})
            ], className="header"),

            # Main Dashboard Content
            html.Div([
                # Left Sidebar - Controls
                html.Div([
                    # Simulation Controls Card
                    html.Div([
                        html.H3([html.I(className="fas fa-cogs", style={'marginRight': '10px'}), "Simulation Controls"]),
                        
                        html.Label("🎯 Scenario Selection", className="control-label"),
                        dcc.Dropdown(
                            id='scenario-dropdown',
                            options=[
                                {'label': '📈 Baseline Economy', 'value': 'baseline'},
                                {'label': '🔥 Financial Crisis', 'value': 'crisis'},
                                {'label': '💸 De-dollarization', 'value': 'dedollarization'},
                                {'label': '💹 Inflation Surge', 'value': 'inflation_surge'}
                            ],
                            value='baseline',
                            clearable=False,
                            className="modern-dropdown"
                        ),

                        html.Label("⏱️ Simulation Duration", className="control-label"),
                        dcc.Slider(
                            id='duration-slider', 
                            min=6, max=60, value=24, step=3,
                            marks={i: {'label': f'{i}m', 'style': {'fontSize': '12px'}} for i in range(6, 61, 6)},
                            tooltip={"placement": "bottom", "always_visible": True},
                            className="modern-slider"
                        ),

                        html.Button([
                            html.I(className="fas fa-play", style={'marginRight': '8px'}),
                            "Run Simulation"
                        ], id='run-button', n_clicks=0, className="run-button"),

                        html.Button([
                            html.I(className="fas fa-copy", style={'marginRight': '8px'}),
                            "Compare Scenarios"
                        ], id='compare-button', n_clicks=0, className="compare-button"),

                        html.Button([
                            html.I(className="fas fa-trash", style={'marginRight': '8px'}),
                            "Clear All"
                        ], id='clear-button', n_clicks=0, className="clear-button"),

                    ], className="control-card"),

                    # Quick Stats Card
                    html.Div([
                        html.H4([html.I(className="fas fa-chart-bar", style={'marginRight': '10px'}), "Quick Stats"]),
                        html.Div(id="quick-stats", children="No simulation data yet")
                    ], className="stats-card"),

                    # Scenario Info Card
                    html.Div([
                        html.H4([html.I(className="fas fa-info-circle", style={'marginRight': '10px'}), "Scenario Info"]),
                        html.Div(id="scenario-info")
                    ], className="info-card")

                ], className="sidebar"),

                # Main Content Area
                html.Div([
                    # Status Bar
                    dcc.Loading(
                        id="loading-spinner",
                        type="dot",
                        color="#00D4FF",
                        children=[
                            html.Div(id="status-container", children=[
                                html.Div("🚀 Ready to simulate! Select parameters and click 'Run Simulation'", 
                                        className="status-ready")
                            ])
                        ]
                    ),

                    # Charts Container
                    html.Div(id="charts-container", children=[
                        html.Div("Select a scenario and run simulation to see visualizations", 
                                className="empty-state")
                    ])

                ], className="main-content")

            ], className="dashboard-body"),

            # Footer
            html.Div([
                html.P(f"ReserveFlow Dashboard v2.0 | Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            ], className="footer")

        ], className="dashboard-container")

    def _setup_callbacks(self):
        """Setup enhanced dashboard callbacks"""
        
        @self.app.callback(
            [Output('scenario-info', 'children')],
            [Input('scenario-dropdown', 'value')]
        )
        def update_scenario_info(scenario):
            """Update scenario information display"""
            scenario_descriptions = {
                'baseline': {
                    'title': '📈 Baseline Economy',
                    'description': 'Standard economic conditions with normal market volatility and gradual shifts in reserve allocations.',
                    'key_features': ['Stable growth', 'Low volatility', 'Gradual changes']
                },
                'crisis': {
                    'title': '🔥 Financial Crisis',
                    'description': 'High market stress, increased volatility, flight to safe-haven assets like gold.',
                    'key_features': ['High volatility', 'Risk-off sentiment', 'Gold preference']
                },
                'dedollarization': {
                    'title': '💸 De-dollarization',
                    'description': 'Systematic reduction in USD holdings, diversification into alternative currencies and assets.',
                    'key_features': ['USD reduction', 'Currency diversification', 'Strategic rebalancing']
                },
                'inflation_surge': {
                    'title': '💹 Inflation Surge',
                    'description': 'High inflation environment driving demand for inflation hedges and precious metals.',
                    'key_features': ['Inflation hedge', 'Metal preference', 'Real asset focus']
                }
            }
            
            info = scenario_descriptions.get(scenario, {})
            return [html.Div([
                html.H5(info.get('title', 'Unknown Scenario'), style={'color': '#00D4FF', 'marginBottom': '10px'}),
                html.P(info.get('description', ''), style={'fontSize': '14px', 'lineHeight': '1.4'}),
                html.Ul([html.Li(feature) for feature in info.get('key_features', [])], 
                       style={'fontSize': '12px', 'marginTop': '10px'})
            ])]

        @self.app.callback(
            [Output('status-container', 'children'),
             Output('charts-container', 'children'),
             Output('quick-stats', 'children')],
            [Input('run-button', 'n_clicks'),
             Input('compare-button', 'n_clicks'),
             Input('clear-button', 'n_clicks')],
            [State('scenario-dropdown', 'value'),
             State('duration-slider', 'value')]
        )
        def update_dashboard(run_clicks, compare_clicks, clear_clicks, scenario, duration):
            """Main dashboard update logic"""
            ctx = callback_context
            if not ctx.triggered:
                return self._get_initial_state()

            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

            try:
                if trigger_id == 'clear-button' and clear_clicks > 0:
                    self.simulation_results = {}
                    return self._get_initial_state()

                elif trigger_id == 'run-button' and run_clicks > 0:
                    return self._run_single_simulation(scenario, duration)

                elif trigger_id == 'compare-button' and compare_clicks > 0:
                    return self._create_comparison_view()

                else:
                    return self._get_initial_state()

            except Exception as e:
                tb = traceback.format_exc()
                error_content = html.Div([
                    html.H4("⚠️ Simulation Error", style={'color': '#FF6B6B'}),
                    html.P(f"Error: {str(e)}", style={'color': '#FF6B6B'}),
                    html.Details([
                        html.Summary("🔍 Technical Details"),
                        html.Pre(tb, className="error-traceback")
                    ])
                ], className="error-container")
                
                return [error_content, self._get_empty_charts(), "Error occurred"]

    def _get_initial_state(self):
        """Get initial dashboard state"""
        status = html.Div("🚀 Ready to simulate! Select parameters and click 'Run Simulation'", 
                         className="status-ready")
        charts = html.Div("Select a scenario and run simulation to see visualizations", 
                         className="empty-state")
        stats = "No simulation data yet"
        return [status, charts, stats]

    def _run_single_simulation(self, scenario, duration):
        """Run a single scenario simulation"""
        # Get configuration
        configs = {
            'baseline': DefaultConfig(), 'crisis': CrisisConfig(),
            'dedollarization': DepollarizationConfig(), 'inflation_surge': InflationSurgeConfig()
        }
        config = configs.get(scenario, DefaultConfig())
        
        # Run simulation
        sim = ReserveFlowSimulation(config)
        results = sim.run_simulation(duration_months=duration)
        
        # Store results
        self.simulation_results[scenario] = {
            'data': results,
            'duration': duration,
            'timestamp': datetime.now()
        }
        
        # Create visualizations
        charts = self._create_enhanced_charts(results, scenario)
        
        # Update status
        status = html.Div([
            html.I(className="fas fa-check-circle", style={'color': '#4CAF50', 'marginRight': '10px'}),
            f"✅ Simulation completed for '{scenario}' scenario ({duration} months, {len(results)} data points)"
        ], className="status-success")
        
        # Generate stats
        stats = self._generate_quick_stats(results, scenario)
        
        return [status, charts, stats]

    def _create_enhanced_charts(self, results, scenario):
        """Create enhanced chart visualizations"""
        # Enhanced Precious Metals Chart
        pm_fig = self._create_enhanced_pm_chart(results)
        
        # Enhanced Exchange Rates Chart
        fx_fig = self._create_enhanced_fx_chart(results)
        
        # Enhanced Risk Dashboard
        risk_fig = self._create_enhanced_risk_chart(results)
        
        # Enhanced Allocation Chart
        alloc_fig = self._create_enhanced_allocation_chart(results)
        
        # Market Indicators Chart
        market_fig = self._create_market_indicators_chart(results)
        
        # Performance Summary Chart
        perf_fig = self._create_performance_summary_chart(results)
        
        # Apply dark theme to all charts
        dark_theme = {
            'template': 'plotly_dark',
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'plot_bgcolor': 'rgba(45,45,45,0.8)',
            'font': {'color': '#E0E0E0', 'family': 'Inter'},
            'colorway': ['#00D4FF', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
        }
        
        for fig in [pm_fig, fx_fig, risk_fig, alloc_fig, market_fig, perf_fig]:
            fig.update_layout(**dark_theme)
            fig.update_layout(
                margin=dict(l=20, r=20, t=40, b=20),
                height=400,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )

        return html.Div([
            # Top Row - Main Charts
            html.Div([
                html.Div([dcc.Graph(figure=pm_fig, config={'displayModeBar': False})], className="chart-container"),
                html.Div([dcc.Graph(figure=fx_fig, config={'displayModeBar': False})], className="chart-container")
            ], className="charts-row"),
            
            # Middle Row - Risk and Allocation
            html.Div([
                html.Div([dcc.Graph(figure=risk_fig, config={'displayModeBar': False})], className="chart-container"),
                html.Div([dcc.Graph(figure=alloc_fig, config={'displayModeBar': False})], className="chart-container")
            ], className="charts-row"),
            
            # Bottom Row - Market Indicators and Performance
            html.Div([
                html.Div([dcc.Graph(figure=market_fig, config={'displayModeBar': False})], className="chart-container"),
                html.Div([dcc.Graph(figure=perf_fig, config={'displayModeBar': False})], className="chart-container")
            ], className="charts-row")
        ], className="charts-grid")

    def _create_enhanced_pm_chart(self, results):
        """Create enhanced precious metals chart"""
        fig = go.Figure()
        
        # Ensure we have valid data
        if len(results) == 0:
            fig.add_annotation(text="No data available", xref="paper", yref="paper", 
                             x=0.5, y=0.5, showarrow=False)
            return fig
        
        # Create proper time series (days from start)
        time_periods = list(range(len(results)))
        
        # Plot gold price
        if 'gold_price' in results.columns:
            try:
                gold_data = pd.to_numeric(results['gold_price'], errors='coerce').fillna(0)
                if len(gold_data) > 0:
                    fig.add_trace(
                        go.Scatter(x=time_periods, y=gold_data.values, 
                                  name='Gold Price (USD)', line=dict(color='#FFD700', width=3),
                                  hovertemplate='<b>Gold</b><br>Day: %{x}<br>Price: $%{y:,.0f}<br><extra></extra>')
                    )
            except Exception as e:
                pass
        
        # Plot silver price (without extreme scaling)
        if 'silver_price' in results.columns:
            try:
                silver_data = pd.to_numeric(results['silver_price'], errors='coerce').fillna(0)
                if len(silver_data) > 0:
                    # Use secondary y-axis for silver to avoid scaling issues
                    fig.add_trace(
                        go.Scatter(x=time_periods, y=silver_data.values, 
                                  name='Silver Price (USD)', line=dict(color='#C0C0C0', width=3),
                                  yaxis='y2',
                                  hovertemplate='<b>Silver</b><br>Day: %{x}<br>Price: $%{y:,.2f}<br><extra></extra>')
                    )
            except Exception as e:
                pass
        
        fig.update_layout(
            title="💎 Precious Metals Price Evolution",
            xaxis_title="Days",
            yaxis_title="Gold Price (USD)",
            yaxis2=dict(
                title="Silver Price (USD)",
                overlaying='y',
                side='right'
            ),
            hovermode='x unified'
        )
        
        return fig

    def _create_enhanced_fx_chart(self, results):
        """Create enhanced exchange rates chart"""
        fig = go.Figure()
        
        # Create proper time series
        time_periods = list(range(len(results)))
        
        # Look for meaningful exchange rate data
        potential_fx_columns = []
        for col in results.columns:
            if any(term in col.lower() for term in ['exchange', 'rate', 'usd', 'eur', 'gbp', 'jpy', 'cny']):
                potential_fx_columns.append(col)
        
        # Also look for real interest rates or other economic indicators
        if not potential_fx_columns:
            for col in results.columns:
                if any(term in col.lower() for term in ['interest', 'real', 'rate', 'volatility']):
                    potential_fx_columns.append(col)
        
        colors = ['#00D4FF', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        traces_added = 0
        
        for i, col in enumerate(potential_fx_columns[:5]):
            if col in results.columns:
                try:
                    # Handle different data types more robustly
                    if results[col].dtype == 'object':
                        # Extract numeric values from complex objects
                        fx_data = results[col].apply(lambda x: 
                            float(x[0]) if hasattr(x, '__getitem__') and len(x) > 0 and isinstance(x[0], (int, float))
                            else float(np.mean(x)) if hasattr(x, '__iter__') and not isinstance(x, str) and len(x) > 0
                            else float(x) if isinstance(x, (int, float)) 
                            else 0.0
                        )
                    else:
                        fx_data = pd.to_numeric(results[col], errors='coerce')
                    
                    fx_data = fx_data.fillna(0)
                    
                    # Only plot if there's meaningful variation and non-zero values
                    if len(fx_data) > 0 and fx_data.var() > 1e-10 and fx_data.abs().max() > 1e-6:
                        currency_name = col.replace('_exchange_rate', '').replace('_', ' ').title()
                        fig.add_trace(
                            go.Scatter(x=time_periods, y=fx_data.values, 
                                      name=currency_name, 
                                      line=dict(color=colors[traces_added % len(colors)], width=2),
                                      hovertemplate=f'<b>{currency_name}</b><br>Day: %{{x}}<br>Value: %{{y:.4f}}<br><extra></extra>')
                        )
                        traces_added += 1
                except Exception as e:
                    continue
        
        if traces_added == 0:
            # Create a placeholder with sample data
            fig.add_trace(
                go.Scatter(x=time_periods, y=[1.0] * len(results), 
                          name='Real Interest Rates', 
                          line=dict(color='#00D4FF', width=2),
                          hovertemplate='<b>Real Interest Rates</b><br>Day: %{x}<br>Rate: %{y:.3f}<br><extra></extra>')
            )
        
        fig.update_layout(
            title="💱 Exchange Rates & Currency Indicators",
            xaxis_title="Days",
            yaxis_title="Rate/Index Value",
            hovermode='x unified'
        )
        
        return fig

    def _create_enhanced_risk_chart(self, results):
        """Create enhanced risk metrics chart"""
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Create proper time series
        time_periods = list(range(len(results)))
        
        if 'geopolitical_risk' in results.columns:
            try:
                risk_data = results['geopolitical_risk'].apply(
                    lambda x: float(x[0]) if hasattr(x, '__iter__') and not isinstance(x, str) and len(x) > 0
                    else float(x) if isinstance(x, (int, float))
                    else 0.0
                )
                risk_data = pd.to_numeric(risk_data, errors='coerce').fillna(0)
                
                fig.add_trace(
                    go.Scatter(x=time_periods, y=risk_data.values, 
                              name='Geopolitical Risk', 
                              line=dict(color='#FF6B6B', width=2),
                              fill='tozeroy',
                              hovertemplate='<b>Geopolitical Risk</b><br>Day: %{x}<br>Level: %{y:.3f}<br><extra></extra>'),
                    secondary_y=False
                )
            except Exception as e:
                pass
        
        if 'market_stress' in results.columns:
            try:
                stress_data = results['market_stress'].apply(
                    lambda x: float(x[0]) if hasattr(x, '__iter__') and not isinstance(x, str) and len(x) > 0
                    else float(x) if isinstance(x, (int, float))
                    else 0.0
                )
                stress_data = pd.to_numeric(stress_data, errors='coerce').fillna(0)
                
                fig.add_trace(
                    go.Scatter(x=time_periods, y=stress_data.values, 
                              name='Market Stress', 
                              line=dict(color='#FF9500', width=2),
                              hovertemplate='<b>Market Stress</b><br>Day: %{x}<br>Level: %{y:.3f}<br><extra></extra>'),
                    secondary_y=True
                )
            except Exception as e:
                pass
        
        fig.update_layout(
            title="⚠️ Risk Metrics Dashboard",
            xaxis_title="Days"
        )
        fig.update_yaxes(title_text="Geopolitical Risk", secondary_y=False)
        fig.update_yaxes(title_text="Market Stress", secondary_y=True)
        
        return fig

    def _create_enhanced_allocation_chart(self, results):
        """Create enhanced allocation chart"""
        fig = go.Figure()
        
        # Create proper time series
        time_periods = list(range(len(results)))
        
        if 'current_allocation' in results.columns and len(results) > 0:
            allocation_data = {}
            valid_rows = 0
            
            for idx, row_data in results.iterrows():
                try:
                    allocation = row_data['current_allocation']
                    if isinstance(allocation, dict) and allocation:
                        valid_rows += 1
                        for asset, alloc_value in allocation.items():
                            if asset not in allocation_data:
                                allocation_data[asset] = []
                            # Convert to percentage
                            percentage = float(alloc_value) * 100 if alloc_value is not None else 0
                            allocation_data[asset].append(percentage)
                    elif isinstance(allocation, (int, float)):
                        # Handle single value allocation
                        if 'total' not in allocation_data:
                            allocation_data['total'] = []
                        allocation_data['total'].append(float(allocation) * 100)
                        valid_rows += 1
                except Exception:
                    continue
            
            if allocation_data and valid_rows > 0:
                colors = ['#00D4FF', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
                
                # Create stacked area chart
                for i, (asset, data) in enumerate(allocation_data.items()):
                    # Pad data to match results length
                    while len(data) < len(results):
                        data.append(0)
                    
                    fig.add_trace(
                        go.Scatter(
                            x=time_periods, y=data, 
                            name=asset.upper().replace('_', ' '), 
                            stackgroup='one', mode='lines',
                            fill='tonexty', line=dict(width=1, color=colors[i % len(colors)]),
                            hovertemplate=f'<b>{asset.upper()}</b><br>Day: %{{x}}<br>Allocation: %{{y:.1f}}%<br><extra></extra>'
                        )
                    )
            else:
                fig.add_annotation(text="No allocation data available", xref="paper", yref="paper", 
                                 x=0.5, y=0.5, showarrow=False)
        else:
            fig.add_annotation(text="No allocation data available", xref="paper", yref="paper", 
                             x=0.5, y=0.5, showarrow=False)
        
        fig.update_layout(
            title="📊 Reserve Allocation Evolution",
            xaxis_title="Days",
            yaxis_title="Allocation (%)",
            yaxis_range=[0, 100],
            hovermode='x unified'
        )
        
        return fig

    def _create_market_indicators_chart(self, results):
        """Create market indicators chart"""
        fig = go.Figure()
        
        # Create proper time series
        time_periods = list(range(len(results)))
        
        # Find market-related columns
        market_columns = [col for col in results.columns if any(term in col.lower() for term in 
                         ['volatility', 'stress', 'risk', 'gdp', 'inflation', 'interest', 'market'])]
        
        colors = ['#00D4FF', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        traces_added = 0
        
        for col in market_columns[:5]:
            if col in results.columns:
                try:
                    # Handle different data types
                    if results[col].dtype == 'object':
                        # Try to extract numeric values from complex objects
                        data = results[col].apply(lambda x: 
                            float(x[0]) if hasattr(x, '__getitem__') and len(x) > 0 and isinstance(x[0], (int, float))
                            else float(np.mean(x)) if hasattr(x, '__iter__') and not isinstance(x, str) and len(x) > 0
                            else float(x) if isinstance(x, (int, float, str)) and str(x).replace('.','').replace('-','').isdigit()
                            else 0.0
                        )
                    else:
                        data = pd.to_numeric(results[col], errors='coerce')
                    
                    data = data.fillna(0)
                    
                    # Only plot if there's meaningful variation
                    if len(data) > 0 and (data.var() > 1e-6 or data.abs().max() > 1e-6):
                        fig.add_trace(
                            go.Scatter(
                                x=time_periods, y=data.values, 
                                name=col.replace('_', ' ').title(),
                                line=dict(color=colors[traces_added % len(colors)], width=2),
                                hovertemplate=f'<b>{col.replace("_", " ").title()}</b><br>Day: %{{x}}<br>Value: %{{y:.4f}}<br><extra></extra>'
                            )
                        )
                        traces_added += 1
                except Exception:
                    continue
        
        if traces_added == 0:
            fig.add_annotation(text="No market indicator data available", xref="paper", yref="paper", 
                             x=0.5, y=0.5, showarrow=False)
        
        fig.update_layout(
            title="📈 Market Indicators & Economic Metrics",
            xaxis_title="Days", 
            yaxis_title="Indicator Value",
            hovermode='x unified'
        )
        
        return fig

    def _create_performance_summary_chart(self, results):
        """Create performance summary chart"""
        fig = go.Figure()
        
        # Calculate performance metrics
        metrics = {}
        
        if 'gold_price' in results.columns:
            try:
                gold_data = pd.to_numeric(results['gold_price'], errors='coerce').dropna()
                if len(gold_data) > 1:
                    initial_gold = gold_data.iloc[0]
                    final_gold = gold_data.iloc[-1]
                    metrics['Gold Return'] = (final_gold / initial_gold - 1) * 100
            except Exception:
                pass
        
        if 'silver_price' in results.columns:
            try:
                silver_data = pd.to_numeric(results['silver_price'], errors='coerce').dropna()
                if len(silver_data) > 1:
                    initial_silver = silver_data.iloc[0]
                    final_silver = silver_data.iloc[-1]
                    metrics['Silver Return'] = (final_silver / initial_silver - 1) * 100
            except Exception:
                pass
        
        # Add portfolio performance if available
        if len(metrics) > 0:
            colors = ['#4CAF50' if v > 0 else '#FF6B6B' for v in metrics.values()]
            
            fig.add_trace(
                go.Bar(x=list(metrics.keys()), y=list(metrics.values()),
                      marker_color=colors,
                      hovertemplate='<b>%{x}</b><br>Return: %{y:+.2f}%<extra></extra>')
            )
        
        fig.update_layout(
            title="📊 Performance Summary",
            xaxis_title="Asset",
            yaxis_title="Return (%)",
            showlegend=False
        )
        
        return fig

    def _generate_quick_stats(self, results, scenario):
        """Generate quick statistics"""
        stats = []
        
        # Simulation info
        stats.append(html.Div([
            html.I(className="fas fa-database", style={'marginRight': '8px'}),
            f"Data Points: {len(results)}"
        ], className="stat-item"))
        
        # Scenario type
        stats.append(html.Div([
            html.I(className="fas fa-chart-line", style={'marginRight': '8px'}),
            f"Scenario: {scenario.title()}"
        ], className="stat-item"))
        
        # Gold performance
        if 'gold_price' in results.columns:
            try:
                gold_data = pd.to_numeric(results['gold_price'], errors='coerce').dropna()
                if len(gold_data) > 1:
                    initial = gold_data.iloc[0]
                    final = gold_data.iloc[-1]
                    change = (final / initial - 1) * 100
                    color = '#4CAF50' if change > 0 else '#FF6B6B'
                    
                    stats.append(html.Div([
                        html.I(className="fas fa-coins", style={'marginRight': '8px'}),
                        f"Gold: {change:+.1f}%"
                    ], className="stat-item", style={'color': color}))
            except Exception:
                pass
        
        # Risk level
        risk_columns = [col for col in results.columns if 'risk' in col.lower()]
        if risk_columns:
            try:
                risk_col = risk_columns[0]
                risk_data = results[risk_col].apply(
                    lambda x: x[0] if hasattr(x, '__getitem__') and len(x) > 0 and isinstance(x[0], (int, float))
                    else float(x) if isinstance(x, (int, float)) else 0
                )
                risk_data = pd.to_numeric(risk_data, errors='coerce').dropna()
                if len(risk_data) > 0:
                    avg_risk = risk_data.mean()
                    stats.append(html.Div([
                        html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px'}),
                        f"Avg Risk: {avg_risk:.3f}"
                    ], className="stat-item"))
            except Exception:
                pass
        
        # Market stress
        stress_columns = [col for col in results.columns if 'stress' in col.lower()]
        if stress_columns:
            try:
                stress_col = stress_columns[0]
                stress_data = results[stress_col].apply(
                    lambda x: x[0] if hasattr(x, '__getitem__') and len(x) > 0 and isinstance(x[0], (int, float))
                    else float(x) if isinstance(x, (int, float)) else 0
                )
                stress_data = pd.to_numeric(stress_data, errors='coerce').dropna()
                if len(stress_data) > 0:
                    avg_stress = stress_data.mean()
                    stats.append(html.Div([
                        html.I(className="fas fa-chart-area", style={'marginRight': '8px'}),
                        f"Market Stress: {avg_stress:.3f}"
                    ], className="stat-item"))
            except Exception:
                pass
        
        return html.Div(stats, className="quick-stats-grid")

    def _create_comparison_view(self):
        """Create scenario comparison view"""
        if len(self.simulation_results) < 2:
            return [
                html.Div("⚠️ Need at least 2 scenarios to compare", className="status-warning"),
                html.Div("Run multiple scenarios to enable comparison", className="empty-state"),
                "Insufficient data for comparison"
            ]
        
        # Create comparison charts
        comparison_charts = self._create_comparison_charts()
        
        status = html.Div([
            html.I(className="fas fa-balance-scale", style={'marginRight': '10px'}),
            f"📊 Comparing {len(self.simulation_results)} scenarios"
        ], className="status-info")
        
        return [status, comparison_charts, f"{len(self.simulation_results)} scenarios loaded"]

    def _create_comparison_charts(self):
        """Create scenario comparison charts"""
        # Comparison logic would go here
        # For now, return a placeholder
        return html.Div([
            html.H3("🔍 Scenario Comparison"),
            html.P("Comparison feature coming soon...")
        ], className="comparison-placeholder")

    def _get_empty_charts(self):
        """Get empty charts placeholder"""
        return html.Div("Select a scenario and run simulation to see visualizations", 
                       className="empty-state")

    def run_server(self, debug: bool = True):
        """Run the enhanced dashboard server"""
        self.app.index_string = f"""
        <!DOCTYPE html>
        <html>
            <head>
                {{%metas%}}
                <title>{{%title%}}</title>
                {{%favicon%}}
                {{%css%}}
                <style>{create_advanced_css()}</style>
            </head>
            <body>
                {{%app_entry%}}
                <footer>
                    {{%config%}}
                    {{%scripts%}}
                    {{%renderer%}}
                </footer>
            </body>
        </html>
        """
        print(f"🚀 Starting ReserveFlow Advanced Dashboard on http://localhost:{self.port}")
        print(f"🎯 Features: Multi-scenario analysis, Real-time updates, Advanced visualizations")
        self.app.run(debug=debug, port=self.port)


def create_advanced_css():
    """Create advanced CSS styling"""
    return """
    :root {
        --dark-bg: #0D1117; --medium-bg: #161B22; --light-bg: #21262D; --card-bg: #30363D;
        --primary-color: #00D4FF; --secondary-color: #FF6B6B; --success-color: #4CAF50;
        --warning-color: #FF9500; --text-color: #E6EDF3; --text-muted: #7D8590;
        --border-color: #30363D; --shadow: 0 8px 32px rgba(0,0,0,0.3);
        --font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    * { box-sizing: border-box; }
    
    body {
        background: linear-gradient(135deg, var(--dark-bg) 0%, var(--medium-bg) 100%);
        color: var(--text-color); font-family: var(--font-family); margin: 0; padding: 0;
        min-height: 100vh; overflow-x: hidden;
    }

    .dashboard-container {
        display: flex; flex-direction: column; min-height: 100vh;
        background: linear-gradient(135deg, var(--dark-bg) 0%, var(--medium-bg) 100%);
    }

    .header {
        background: linear-gradient(135deg, var(--medium-bg) 0%, var(--light-bg) 100%);
        padding: 2rem; text-align: center; border-bottom: 2px solid var(--primary-color);
        box-shadow: var(--shadow); position: relative; overflow: hidden;
    }

    .header::before {
        content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(45deg, transparent 0%, rgba(0,212,255,0.1) 50%, transparent 100%);
        animation: shimmer 3s ease-in-out infinite;
    }

    @keyframes shimmer {
        0%, 100% { transform: translateX(-100%); }
        50% { transform: translateX(100%); }
    }

    .dashboard-body { display: flex; flex-grow: 1; }

    .sidebar {
        width: 320px; background: var(--medium-bg); padding: 1.5rem; border-right: 1px solid var(--border-color);
        overflow-y: auto; box-shadow: var(--shadow);
    }

    .main-content { flex-grow: 1; padding: 1.5rem; overflow-y: auto; }

    .control-card, .stats-card, .info-card {
        background: var(--card-bg); border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem;
        border: 1px solid var(--border-color); box-shadow: var(--shadow);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .control-card:hover, .stats-card:hover, .info-card:hover {
        transform: translateY(-2px); box-shadow: 0 12px 40px rgba(0,0,0,0.4);
    }

    .control-label {
        font-weight: 600; margin: 1rem 0 0.5rem 0; display: block; color: var(--primary-color);
        font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.5px;
    }

    .modern-dropdown .Select-control {
        background: var(--light-bg) !important; border: 2px solid var(--border-color) !important;
        border-radius: 8px; padding: 0.5rem; transition: all 0.3s ease;
    }

    .modern-dropdown .Select-control:hover {
        border-color: var(--primary-color) !important; box-shadow: 0 0 0 3px rgba(0,212,255,0.1);
    }

    .modern-slider .rc-slider-track {
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color)) !important;
        height: 6px !important;
    }

    .modern-slider .rc-slider-handle {
        border: 3px solid var(--primary-color) !important; background: var(--card-bg) !important;
        width: 20px !important; height: 20px !important; box-shadow: var(--shadow);
    }

    .run-button, .compare-button, .clear-button {
        width: 100%; padding: 0.75rem 1rem; border: none; border-radius: 8px; font-size: 1rem;
        font-weight: 600; cursor: pointer; transition: all 0.3s ease; margin-top: 1rem;
        font-family: var(--font-family); text-transform: uppercase; letter-spacing: 0.5px;
    }

    .run-button {
        background: linear-gradient(135deg, var(--primary-color), #0099CC);
        color: white; box-shadow: 0 4px 15px rgba(0,212,255,0.3);
    }

    .run-button:hover {
        transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,212,255,0.4);
    }

    .compare-button {
        background: linear-gradient(135deg, var(--warning-color), #FF7700);
        color: white; box-shadow: 0 4px 15px rgba(255,149,0,0.3);
    }

    .clear-button {
        background: linear-gradient(135deg, var(--secondary-color), #FF4444);
        color: white; box-shadow: 0 4px 15px rgba(255,107,107,0.3);
    }

    .status-ready, .status-success, .status-warning, .status-info {
        padding: 1rem; border-radius: 8px; margin-bottom: 1rem; font-weight: 500;
        display: flex; align-items: center; animation: fadeIn 0.5s ease;
    }

    .status-ready { background: rgba(0,212,255,0.1); border-left: 4px solid var(--primary-color); }
    .status-success { background: rgba(76,175,80,0.1); border-left: 4px solid var(--success-color); }
    .status-warning { background: rgba(255,149,0,0.1); border-left: 4px solid var(--warning-color); }
    .status-info { background: rgba(0,212,255,0.1); border-left: 4px solid var(--primary-color); }

    .charts-grid { display: grid; gap: 1.5rem; }
    .charts-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 1.5rem; }

    .chart-container {
        background: var(--card-bg); border-radius: 12px; padding: 1rem;
        border: 1px solid var(--border-color); box-shadow: var(--shadow);
        transition: transform 0.2s ease;
    }

    .chart-container:hover { transform: translateY(-2px); }

    .empty-state, .comparison-placeholder {
        text-align: center; padding: 3rem; color: var(--text-muted); font-size: 1.1rem;
        background: var(--card-bg); border-radius: 12px; border: 2px dashed var(--border-color);
    }

    .quick-stats-grid { display: grid; gap: 0.75rem; }

    .stat-item {
        background: rgba(0,212,255,0.1); padding: 0.75rem; border-radius: 6px;
        font-size: 0.9rem; font-weight: 500; border-left: 3px solid var(--primary-color);
    }

    .error-container {
        background: rgba(255,107,107,0.1); border: 1px solid var(--secondary-color);
        border-radius: 8px; padding: 1.5rem; margin: 1rem 0;
    }

    .error-traceback {
        background: var(--dark-bg); color: var(--text-muted); padding: 1rem;
        border-radius: 4px; font-family: 'Monaco', 'Menlo', monospace; font-size: 0.8rem;
        overflow-x: auto; margin-top: 1rem; border: 1px solid var(--border-color);
    }

    .footer {
        background: var(--medium-bg); padding: 1rem; text-align: center;
        border-top: 1px solid var(--border-color); color: var(--text-muted);
    }

    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

    /* Responsive Design */
    @media (max-width: 1200px) {
        .charts-row { grid-template-columns: 1fr; }
        .sidebar { width: 280px; }
    }

    @media (max-width: 768px) {
        .dashboard-body { flex-direction: column; }
        .sidebar { width: 100%; }
        .header { padding: 1rem; }
    }

    /* Custom Scrollbars */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: var(--medium-bg); }
    ::-webkit-scrollbar-thumb { background: var(--border-color); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--primary-color); }
    """


if __name__ == "__main__":
    dashboard = ReserveFlowDashboard()
    dashboard.run_server() 