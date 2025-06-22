#!/usr/bin/env python3
"""
ReserveFlow - Main Entry Point

Quick start script for running ReserveFlow simulations
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from reserveflow import ReserveFlowSimulation, DefaultConfig
from reserveflow.visualization.charts import create_matplotlib_summary


def main():
    """Run a quick demonstration of ReserveFlow"""
    print("ReserveFlow - International Currency Reserves Simulation")
    print("=" * 55)
    
    print("Running baseline scenario for 12 months...")
    
    # Create and run simulation
    config = DefaultConfig()
    config.random_seed = 42  # For reproducible results
    
    sim = ReserveFlowSimulation(config)
    results = sim.run_simulation(duration_months=12)
    
    print(f"✓ Simulation completed: {len(results)} data points")
    
    # Display key results
    print("\nKey Results:")
    print("-" * 12)
    
    if 'gold_price' in results.columns:
        initial_gold = results['gold_price'].iloc[0]
        final_gold = results['gold_price'].iloc[-1]
        gold_return = (final_gold / initial_gold - 1) * 100
        print(f"Gold: ${initial_gold:.0f} → ${final_gold:.0f} ({gold_return:+.1f}%)")
    
    if 'geopolitical_risk' in results.columns:
        avg_risk = results['geopolitical_risk'].mean()
        max_risk = results['geopolitical_risk'].max()
        # Ensure avg_risk and max_risk are scalars before formatting
        if hasattr(avg_risk, 'mean'):
            avg_risk = avg_risk.mean()
        if hasattr(max_risk, 'max'):
            max_risk = max_risk.max()
        print(f"Geopolitical Risk: Avg={avg_risk:.3f}, Max={max_risk:.3f}")
    
    if 'market_stress' in results.columns:
        avg_stress = results['market_stress'].mean()
        crisis_days = (results['market_stress'] > 0.7).sum()
        if hasattr(avg_stress, 'mean'):
            avg_stress = avg_stress.mean()
        print(f"Market Stress: Avg={avg_stress:.3f}, Crisis Days={crisis_days}")
    
    # Save results
    results.to_csv('quick_simulation_results.csv')
    print("\n✓ Results saved to 'quick_simulation_results.csv'")
    
    # Create summary chart
    try:
        create_matplotlib_summary(results)
        print("✓ Summary chart saved as 'reserveflow_summary.png'")
    except Exception as e:
        print(f"Could not create chart: {e}")
    
    print("\nTo explore more:")
    print("- Run 'python examples/basic_simulation.py' for detailed example")
    print("- Run 'python examples/scenario_comparison.py' for scenario comparison")
    print("- Use 'python -m reserveflow.cli --help' for full CLI options")


if __name__ == "__main__":
    main() 