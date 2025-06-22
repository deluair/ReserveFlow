#!/usr/bin/env python3
"""
Basic ReserveFlow Simulation Example

This script demonstrates how to run a basic simulation and visualize results.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from reserveflow import ReserveFlowSimulation, DefaultConfig
from reserveflow.visualization.charts import (
    create_exchange_rate_chart, 
    create_precious_metals_chart,
    create_risk_dashboard,
    create_matplotlib_summary
)
import pandas as pd


def main():
    """Run basic simulation example"""
    print("ReserveFlow Basic Simulation Example")
    print("=" * 40)
    
    # Create simulation with default configuration
    config = DefaultConfig()
    config.random_seed = 42  # For reproducible results
    
    sim = ReserveFlowSimulation(config)
    
    # Run 12-month baseline simulation
    print("Running 12-month baseline simulation...")
    results = sim.run_simulation(duration_months=12)
    
    print(f"Simulation completed. Generated {len(results)} data points.")
    
    # Display basic statistics
    print("\nSimulation Summary:")
    print("-" * 20)
    
    # Gold price statistics
    if 'gold_price' in results.columns:
        initial_gold = results['gold_price'].iloc[0]
        final_gold = results['gold_price'].iloc[-1]
        gold_return = (final_gold / initial_gold - 1) * 100
        print(f"Gold Price: ${initial_gold:.2f} → ${final_gold:.2f} ({gold_return:+.1f}%)")
    
    # Geopolitical risk statistics
    if 'geopolitical_risk' in results.columns:
        avg_risk = results['geopolitical_risk'].mean()
        max_risk = results['geopolitical_risk'].max()
        print(f"Geopolitical Risk: Avg={avg_risk:.3f}, Max={max_risk:.3f}")
    
    # Market stress statistics
    if 'market_stress' in results.columns:
        avg_stress = results['market_stress'].mean()
        max_stress = results['market_stress'].max()
        print(f"Market Stress: Avg={avg_stress:.3f}, Max={max_stress:.3f}")
    
    # USD Index statistics
    if 'usd_index' in results.columns:
        initial_usd = results['usd_index'].iloc[0]
        final_usd = results['usd_index'].iloc[-1]
        usd_change = final_usd - initial_usd
        print(f"USD Index: {initial_usd:.2f} → {final_usd:.2f} ({usd_change:+.2f})")
    
    # Create and display visualizations
    print("\nGenerating visualizations...")
    
    try:
        # Create matplotlib summary
        create_matplotlib_summary(results)
        print("✓ Summary chart saved as 'reserveflow_summary.png'")
        
        # Create interactive charts
        charts = {}
        
        # Exchange rate chart
        charts['exchange_rates'] = create_exchange_rate_chart(results)
        print("✓ Exchange rate chart created")
        
        # Precious metals chart
        charts['precious_metals'] = create_precious_metals_chart(results)
        print("✓ Precious metals chart created")
        
        # Risk dashboard
        charts['risk_dashboard'] = create_risk_dashboard(results)
        print("✓ Risk dashboard created")
        
        # Save interactive charts to HTML
        from reserveflow.visualization.charts import save_charts_to_html
        save_charts_to_html(charts, "output")
        print("✓ Interactive charts saved to 'output/' directory")
        
    except Exception as e:
        print(f"Warning: Could not create all visualizations: {e}")
    
    # Save results to CSV
    results_file = "simulation_results.csv"
    results.to_csv(results_file)
    print(f"✓ Results saved to '{results_file}'")
    
    print("\nBasic simulation completed successfully!")
    print("Check the generated files for detailed results and visualizations.")


if __name__ == "__main__":
    main() 