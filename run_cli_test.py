#!/usr/bin/env python3
"""
CLI Test Script for ReserveFlow
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from reserveflow import ReserveFlowSimulation
from reserveflow.config import CrisisConfig, DepollarizationConfig, InflationSurgeConfig
from reserveflow.visualization.charts import create_scenario_comparison, save_charts_to_html

def simulate_crisis_scenario():
    """Run crisis scenario simulation"""
    print("Running Crisis Scenario Simulation")
    print("=" * 35)
    
    # Create crisis simulation
    config = CrisisConfig()
    config.random_seed = 42
    
    sim = ReserveFlowSimulation(config)
    results = sim.run_simulation(duration_months=12)
    
    print(f"Crisis simulation completed: {len(results)} data points")
    
    # Key crisis metrics
    if 'gold_price' in results.columns:
        gold_return = (results['gold_price'].iloc[-1] / results['gold_price'].iloc[0] - 1) * 100
        print(f"Gold price performance: {gold_return:+.1f}%")
    
    if 'market_stress' in results.columns:
        crisis_days = (results['market_stress'] > 0.7).sum()
        avg_stress = float(results['market_stress'].mean())
        print(f"Market stress: Avg={avg_stress:.3f}, Crisis days={crisis_days}")
    
    # Save results
    results.to_csv('crisis_scenario_results.csv')
    print("✓ Crisis results saved to 'crisis_scenario_results.csv'")
    
    return results

def compare_extreme_scenarios():
    """Compare extreme scenarios (crisis vs inflation surge)"""
    print("\nComparing Extreme Scenarios")
    print("=" * 28)
    
    scenarios = {
        'crisis': CrisisConfig(),
        'inflation_surge': InflationSurgeConfig()
    }
    
    results = {}
    for name, config in scenarios.items():
        config.random_seed = 42
        sim = ReserveFlowSimulation(config)
        results[name] = sim.run_simulation(duration_months=6)
        print(f"✓ {name} scenario completed")
    
    # Create comparison chart
    try:
        comparison_fig = create_scenario_comparison(results)
        save_charts_to_html({'extreme_scenarios': comparison_fig}, "output")
        print("✓ Extreme scenario comparison saved to 'output/extreme_scenarios.html'")
    except Exception as e:
        print(f"Warning: Could not create comparison chart: {e}")
    
    # Compare key metrics
    print("\nExtreme Scenario Comparison:")
    print("-" * 30)
    
    for name, df in results.items():
        if 'gold_price' in df.columns:
            gold_return = (df['gold_price'].iloc[-1] / df['gold_price'].iloc[0] - 1) * 100
            print(f"{name}: Gold return = {gold_return:+.1f}%")

if __name__ == "__main__":
    # Run crisis scenario
    crisis_results = simulate_crisis_scenario()
    
    # Compare extreme scenarios
    compare_extreme_scenarios()
    
    print("\nCLI test completed successfully!")
    print("Generated files:")
    print("- crisis_scenario_results.csv")
    print("- output/extreme_scenarios.html") 