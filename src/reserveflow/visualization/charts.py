"""
Chart creation functions for ReserveFlow simulation results
"""

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List


# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


def create_exchange_rate_chart(results_df: pd.DataFrame, currencies: Optional[List[str]] = None) -> go.Figure:
    """Create interactive exchange rate chart"""
    if currencies is None:
        currencies = ["EUR", "GBP", "JPY", "CNY"]
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=tuple(f"{curr}/USD" for curr in currencies),
        specs=[[{"secondary_y": True}, {"secondary_y": True}],
               [{"secondary_y": True}, {"secondary_y": True}]]
    )
    
    for i, currency in enumerate(currencies[:4]):
        row = i // 2 + 1
        col = i % 2 + 1
        
        # Extract exchange rates for this currency
        if 'exchange_rates' in results_df.columns:
            rates = []
            for idx, row_data in results_df.iterrows():
                if isinstance(row_data['exchange_rates'], dict):
                    rates.append(row_data['exchange_rates'].get(currency, np.nan))
                else:
                    rates.append(np.nan)
            
            # Plot exchange rate
            fig.add_trace(
                go.Scatter(
                    x=results_df.index,
                    y=rates,
                    name=f"{currency}/USD",
                    line=dict(width=2)
                ),
                row=row, col=col
            )
    
    fig.update_layout(
        title="Exchange Rate Evolution",
        height=600,
        showlegend=True
    )
    
    return fig


def create_precious_metals_chart(results_df: pd.DataFrame) -> go.Figure:
    """Create precious metals price chart"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Gold Price (USD/oz)", "Silver Price (USD/oz)", 
                       "Gold/Silver Ratio", "Central Bank Gold Demand"),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Gold price
    if 'gold_price' in results_df.columns:
        fig.add_trace(
            go.Scatter(
                x=results_df.index,
                y=results_df['gold_price'],
                name="Gold Price",
                line=dict(color='gold', width=2)
            ),
            row=1, col=1
        )
    
    # Silver price
    if 'silver_price' in results_df.columns:
        fig.add_trace(
            go.Scatter(
                x=results_df.index,
                y=results_df['silver_price'],
                name="Silver Price",
                line=dict(color='silver', width=2)
            ),
            row=1, col=2
        )
    
    # Gold/Silver ratio
    if 'gold_silver_ratio' in results_df.columns:
        fig.add_trace(
            go.Scatter(
                x=results_df.index,
                y=results_df['gold_silver_ratio'],
                name="Gold/Silver Ratio",
                line=dict(color='orange', width=2)
            ),
            row=2, col=1
        )
    
    # Central bank gold demand
    if 'cb_gold_demand' in results_df.columns:
        fig.add_trace(
            go.Scatter(
                x=results_df.index,
                y=results_df['cb_gold_demand'],
                name="CB Gold Demand",
                line=dict(color='darkred', width=2)
            ),
            row=2, col=2
        )
    
    fig.update_layout(
        title="Precious Metals Market Dynamics",
        height=600,
        showlegend=True
    )
    
    return fig


def create_risk_dashboard(results_df: pd.DataFrame) -> go.Figure:
    """Create risk metrics dashboard"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Geopolitical Risk", "Market Stress", 
                       "Currency Volatility", "Risk Events Timeline"),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Geopolitical risk
    if 'geopolitical_risk' in results_df.columns:
        fig.add_trace(
            go.Scatter(
                x=results_df.index,
                y=results_df['geopolitical_risk'],
                name="Geopolitical Risk",
                line=dict(color='red', width=2),
                fill='tonexty'
            ),
            row=1, col=1
        )
    
    # Market stress
    if 'market_stress' in results_df.columns:
        fig.add_trace(
            go.Scatter(
                x=results_df.index,
                y=results_df['market_stress'],
                name="Market Stress",
                line=dict(color='orange', width=2)
            ),
            row=1, col=2
        )
    
    # Currency volatility (if available)
    if 'volatilities' in results_df.columns:
        # Extract average volatility
        avg_vol = []
        for idx, row_data in results_df.iterrows():
            if isinstance(row_data['volatilities'], dict):
                vols = [v for k, v in row_data['volatilities'].items() if k != 'USD']
                avg_vol.append(np.mean(vols) if vols else 0)
            else:
                avg_vol.append(0)
        
        fig.add_trace(
            go.Scatter(
                x=results_df.index,
                y=avg_vol,
                name="Avg Currency Vol",
                line=dict(color='blue', width=2)
            ),
            row=2, col=1
        )
    
    fig.update_layout(
        title="Risk Metrics Dashboard",
        height=600,
        showlegend=True
    )
    
    return fig


def create_reserve_allocation_chart(results_df: pd.DataFrame) -> go.Figure:
    """Create reserve allocation evolution chart"""
    fig = go.Figure()
    
    # Extract allocation data
    if 'current_allocation' in results_df.columns:
        allocation_data = {}
        
        for idx, row_data in results_df.iterrows():
            if isinstance(row_data['current_allocation'], dict):
                for asset, allocation in row_data['current_allocation'].items():
                    if asset not in allocation_data:
                        allocation_data[asset] = []
                    allocation_data[asset].append(allocation * 100)  # Convert to percentage
        
        # Create stacked area chart
        for asset in allocation_data:
            fig.add_trace(
                go.Scatter(
                    x=results_df.index,
                    y=allocation_data[asset],
                    name=asset.upper(),
                    stackgroup='one',
                    mode='lines'
                )
            )
    
    fig.update_layout(
        title="Reserve Allocation Evolution",
        xaxis_title="Date",
        yaxis_title="Allocation (%)",
        yaxis=dict(range=[0, 100]),
        height=500
    )
    
    return fig


def create_scenario_comparison(scenarios_results: Dict[str, pd.DataFrame]) -> go.Figure:
    """Compare multiple scenario results"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Gold Price Comparison", "USD Index Comparison",
                       "Geopolitical Risk", "Market Stress"),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    colors = ['blue', 'red', 'green', 'orange', 'purple']
    
    for i, (scenario_name, results) in enumerate(scenarios_results.items()):
        color = colors[i % len(colors)]
        
        # Gold price comparison
        if 'gold_price' in results.columns:
            fig.add_trace(
                go.Scatter(
                    x=results.index,
                    y=results['gold_price'],
                    name=f"{scenario_name} - Gold",
                    line=dict(color=color, width=2)
                ),
                row=1, col=1
            )
        
        # USD index comparison
        if 'usd_index' in results.columns:
            fig.add_trace(
                go.Scatter(
                    x=results.index,
                    y=results['usd_index'],
                    name=f"{scenario_name} - USD",
                    line=dict(color=color, width=2, dash='dash')
                ),
                row=1, col=2
            )
        
        # Geopolitical risk
        if 'geopolitical_risk' in results.columns:
            fig.add_trace(
                go.Scatter(
                    x=results.index,
                    y=results['geopolitical_risk'],
                    name=f"{scenario_name} - Geo Risk",
                    line=dict(color=color, width=2, dash='dot')
                ),
                row=2, col=1
            )
        
        # Market stress
        if 'market_stress' in results.columns:
            fig.add_trace(
                go.Scatter(
                    x=results.index,
                    y=results['market_stress'],
                    name=f"{scenario_name} - Stress",
                    line=dict(color=color, width=2, dash='dashdot')
                ),
                row=2, col=2
            )
    
    fig.update_layout(
        title="Scenario Comparison Dashboard",
        height=700,
        showlegend=True
    )
    
    return fig


def save_charts_to_html(figures: Dict[str, go.Figure], output_dir: str = "output") -> None:
    """Save all charts to HTML files"""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    for name, fig in figures.items():
        filepath = os.path.join(output_dir, f"{name}.html")
        fig.write_html(filepath)
        print(f"Saved {name} chart to {filepath}")


def create_matplotlib_summary(results_df: pd.DataFrame) -> None:
    """Create summary charts using matplotlib"""
    # Identify numeric columns for plotting
    numeric_cols = results_df.select_dtypes(include=np.number).columns.tolist()
    
    # Key columns to prioritize for plotting
    plot_candidates = [
        'gold_price', 'silver_price', 'geopolitical_risk', 
        'market_stress', 'usd_index', 'sdr_value_usd',
        'risk_sentiment', 'sdr_attractiveness'
    ]
    
    # Select up to 6 available numeric columns from candidates
    plot_cols = [col for col in plot_candidates if col in numeric_cols]
    if not plot_cols:
        print("No suitable numeric columns found for plotting.")
        return
        
    plot_cols = plot_cols[:6]
    
    num_plots = len(plot_cols)
    if num_plots == 0: return

    rows = (num_plots + 2) // 3
    fig, axes = plt.subplots(rows, 3, figsize=(18, 6 * rows))
    axes = axes.flatten()
    fig.suptitle('ReserveFlow Simulation Summary', fontsize=16)
    
    colors = plt.cm.viridis(np.linspace(0, 1, num_plots))
    
    for i, col_name in enumerate(plot_cols):
        ax = axes[i]
        ax.plot(results_df.index, results_df[col_name], color=colors[i], linewidth=2)
        ax.set_title(col_name.replace('_', ' ').title())
        ax.set_ylabel('Value')
        ax.grid(True)

    # Hide any unused subplots
    for i in range(num_plots, len(axes)):
        fig.delaxes(axes[i])
        
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig('reserveflow_summary.png', dpi=300, bbox_inches='tight')
    plt.show() 