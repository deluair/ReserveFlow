#!/usr/bin/env python3
"""
ReserveFlow Scenario Comparison Example

This script runs multiple scenarios and compares their outcomes.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from reserveflow import ReserveFlowSimulation, DefaultConfig
from reserveflow.visualization.charts import create_scenario_comparison, save_charts_to_html
import pandas as pd
import matplotlib.pyplot as plt


def main():
    """Run scenario comparison example"""
    print("ReserveFlow Scenario Comparison Example")
    print("=" * 45)
    
    # Initialize simulation
    sim = ReserveFlowSimulation(DefaultConfig())
    
    # Define scenarios to run
    scenarios = ['baseline', 'crisis', 'dedollarization', 'inflation_surge']
    duration_months = 18
    
    # Store results for each scenario
    scenario_results = {}
    
    print(f"Running {len(scenarios)} scenarios for {duration_months} months each...\n")
    
    # Run each scenario
    for i, scenario in enumerate(scenarios, 1):
        print(f"Running scenario {i}/{len(scenarios)}: {scenario}")
        try:
            results = sim.run_scenario(scenario, duration_months=duration_months)
            scenario_results[scenario] = results
            print(f"✓ {scenario} completed ({len(results)} data points)")
        except Exception as e:
            print(f"✗ {scenario} failed: {e}")
            continue
    
    if not scenario_results:
        print("No scenarios completed successfully!")
        return
    
    print(f"\nCompleted {len(scenario_results)} scenarios. Analyzing results...")
    
    # Compare key metrics across scenarios
    print("\nScenario Comparison Summary:")
    print("-" * 30)
    
    comparison_data = []
    
    for scenario_name, results in scenario_results.items():
        metrics = {}
        metrics['Scenario'] = scenario_name
        
        # Gold price performance
        if 'gold_price' in results.columns:
            initial_gold = results['gold_price'].iloc[0]
            final_gold = results['gold_price'].iloc[-1]
            metrics['Gold Return (%)'] = (final_gold / initial_gold - 1) * 100
            metrics['Gold Volatility (%)'] = results['gold_price'].pct_change().std() * 100
        
        # Geopolitical risk metrics
        if 'geopolitical_risk' in results.columns:
            metrics['Avg Geo Risk'] = results['geopolitical_risk'].mean()
            metrics['Max Geo Risk'] = results['geopolitical_risk'].max()
        
        # Market stress metrics
        if 'market_stress' in results.columns:
            metrics['Avg Market Stress'] = results['market_stress'].mean()
            metrics['Crisis Days'] = (results['market_stress'] > 0.7).sum()
        
        # USD strength
        if 'usd_index' in results.columns:
            initial_usd = results['usd_index'].iloc[0]
            final_usd = results['usd_index'].iloc[-1]
            metrics['USD Change'] = final_usd - initial_usd
        
        comparison_data.append(metrics)
    
    # Create comparison DataFrame
    comparison_df = pd.DataFrame(comparison_data)
    print(comparison_df.to_string(index=False, float_format='%.2f'))
    
    # Create visualizations
    print("\nGenerating comparison visualizations...")
    
    try:
        # Create scenario comparison chart
        comparison_fig = create_scenario_comparison(scenario_results)
        
        # Save to HTML
        save_charts_to_html({'scenario_comparison': comparison_fig}, "output")
        print("✓ Scenario comparison chart saved to 'output/scenario_comparison.html'")
        
        # Create summary statistics chart
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Scenario Comparison Summary', fontsize=16)
        
        # Gold return comparison
        scenarios_list = list(scenario_results.keys())
        gold_returns = [comparison_data[i].get('Gold Return (%)', 0) for i in range(len(scenarios_list))]
        
        axes[0, 0].bar(scenarios_list, gold_returns, color=['blue', 'red', 'green', 'orange'][:len(scenarios_list)])
        axes[0, 0].set_title('Gold Price Returns by Scenario')
        axes[0, 0].set_ylabel('Return (%)')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Average geopolitical risk
        geo_risks = [comparison_data[i].get('Avg Geo Risk', 0) for i in range(len(scenarios_list))]
        
        axes[0, 1].bar(scenarios_list, geo_risks, color=['blue', 'red', 'green', 'orange'][:len(scenarios_list)])
        axes[0, 1].set_title('Average Geopolitical Risk')
        axes[0, 1].set_ylabel('Risk Level')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Crisis days
        crisis_days = [comparison_data[i].get('Crisis Days', 0) for i in range(len(scenarios_list))]
        
        axes[1, 0].bar(scenarios_list, crisis_days, color=['blue', 'red', 'green', 'orange'][:len(scenarios_list)])
        axes[1, 0].set_title('Crisis Days (Market Stress > 0.7)')
        axes[1, 0].set_ylabel('Number of Days')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # USD strength change
        usd_changes = [comparison_data[i].get('USD Change', 0) for i in range(len(scenarios_list))]
        
        axes[1, 1].bar(scenarios_list, usd_changes, color=['blue', 'red', 'green', 'orange'][:len(scenarios_list)])
        axes[1, 1].set_title('USD Index Change')
        axes[1, 1].set_ylabel('Index Points')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig('scenario_comparison_summary.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("✓ Summary comparison chart saved as 'scenario_comparison_summary.png'")
        
    except Exception as e:
        print(f"Warning: Could not create all visualizations: {e}")
    
    # Save comparison data
    comparison_df.to_csv('scenario_comparison.csv', index=False)
    print("✓ Comparison data saved to 'scenario_comparison.csv'")
    
    # Save individual scenario results
    for scenario_name, results in scenario_results.items():
        filename = f"scenario_{scenario_name}_results.csv"
        results.to_csv(filename)
        print(f"✓ {scenario_name} results saved to '{filename}'")
    
    print("\nScenario comparison completed successfully!")
    print("Key insights:")
    print("- Check 'scenario_comparison.html' for interactive comparison charts")
    print("- Review individual scenario CSV files for detailed analysis")
    print("- Summary charts show comparative performance across scenarios")


if __name__ == "__main__":
    main() 