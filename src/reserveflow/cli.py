#!/usr/bin/env python3
"""
Command Line Interface for ReserveFlow
"""

import argparse
import sys
import os
from typing import Optional, Dict, Any
import logging

from .simulation import ReserveFlowSimulation
from .config import DefaultConfig, CrisisConfig, DepollarizationConfig, InflationSurgeConfig
from .visualization.charts import create_matplotlib_summary, save_charts_to_html
from .visualization.dashboard import ReserveFlowDashboard


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('reserveflow.log')
        ]
    )


def get_scenario_config(scenario: str):
    """Get configuration for a specific scenario"""
    configs = {
        'baseline': DefaultConfig(),
        'crisis': CrisisConfig(),
        'dedollarization': DepollarizationConfig(),
        'inflation_surge': InflationSurgeConfig()
    }
    
    if scenario not in configs:
        raise ValueError(f"Unknown scenario: {scenario}. Available: {list(configs.keys())}")
    
    return configs[scenario]


def run_simulation_command(args):
    """Run simulation command"""
    print(f"Running ReserveFlow simulation: {args.scenario}")
    print(f"Duration: {args.duration} months")
    print(f"Output directory: {args.output}")
    
    # Setup output directory
    os.makedirs(args.output, exist_ok=True)
    
    # Get configuration
    try:
        config = get_scenario_config(args.scenario)
        if args.seed:
            config.random_seed = args.seed
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    
    # Run simulation
    try:
        sim = ReserveFlowSimulation(config)
        results = sim.run_simulation(duration_months=args.duration)
        
        print(f"✓ Simulation completed: {len(results)} data points generated")
        
        # Save results
        results_file = os.path.join(args.output, f"{args.scenario}_results.csv")
        results.to_csv(results_file)
        print(f"✓ Results saved to {results_file}")
        
        # Generate summary statistics
        summary_stats = sim.get_summary_statistics(results)
        print("\nSimulation Summary:")
        print("-" * 20)
        for category, stats in summary_stats.items():
            print(f"\n{category.replace('_', ' ').title()}:")
            for metric, value in stats.items():
                if isinstance(value, float):
                    print(f"  {metric}: {value:.3f}")
                else:
                    print(f"  {metric}: {value}")
        
        # Generate visualizations if requested
        if args.charts:
            print("\nGenerating visualizations...")
            try:
                # Matplotlib summary
                create_matplotlib_summary(results)
                summary_file = os.path.join(args.output, f"{args.scenario}_summary.png")
                os.rename('reserveflow_summary.png', summary_file)
                print(f"✓ Summary chart saved to {summary_file}")
                
                # Interactive charts
                from .visualization.charts import (
                    create_exchange_rate_chart, 
                    create_precious_metals_chart,
                    create_risk_dashboard
                )
                
                charts = {
                    'exchange_rates': create_exchange_rate_chart(results),
                    'precious_metals': create_precious_metals_chart(results),
                    'risk_dashboard': create_risk_dashboard(results)
                }
                
                save_charts_to_html(charts, args.output)
                print(f"✓ Interactive charts saved to {args.output}/")
                
            except Exception as e:
                print(f"Warning: Could not generate all visualizations: {e}")
        
        print(f"\nSimulation completed successfully!")
        print(f"All outputs saved to: {args.output}")
        
        return 0
        
    except Exception as e:
        print(f"Error running simulation: {e}")
        return 1


def run_comparison_command(args):
    """Run scenario comparison command"""
    print("Running ReserveFlow scenario comparison")
    print(f"Scenarios: {', '.join(args.scenarios)}")
    print(f"Duration: {args.duration} months")
    
    # Setup output directory
    os.makedirs(args.output, exist_ok=True)
    
    # Run scenarios
    scenario_results = {}
    sim = ReserveFlowSimulation()
    
    for scenario in args.scenarios:
        print(f"\nRunning {scenario} scenario...")
        try:
            results = sim.run_scenario(scenario, duration_months=args.duration)
            scenario_results[scenario] = results
            print(f"✓ {scenario} completed ({len(results)} data points)")
        except Exception as e:
            print(f"✗ {scenario} failed: {e}")
            continue
    
    if not scenario_results:
        print("No scenarios completed successfully!")
        return 1
    
    # Generate comparison
    print(f"\nGenerating comparison for {len(scenario_results)} scenarios...")
    
    try:
        from .visualization.charts import create_scenario_comparison
        comparison_fig = create_scenario_comparison(scenario_results)
        
        # Save comparison chart
        save_charts_to_html({'scenario_comparison': comparison_fig}, args.output)
        print(f"✓ Comparison chart saved to {args.output}/scenario_comparison.html")
        
        # Save individual results
        for scenario_name, results in scenario_results.items():
            filename = os.path.join(args.output, f"{scenario_name}_results.csv")
            results.to_csv(filename)
            print(f"✓ {scenario_name} results saved to {filename}")
        
        print(f"\nComparison completed successfully!")
        return 0
        
    except Exception as e:
        print(f"Error generating comparison: {e}")
        return 1


def run_dashboard_command(args):
    """Run dashboard command"""
    print(f"Starting ReserveFlow Dashboard on port {args.port}")
    
    try:
        dashboard = ReserveFlowDashboard(port=args.port)
        dashboard.run_server(debug=args.debug)
        return 0
    except Exception as e:
        print(f"Error starting dashboard: {e}")
        return 1


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="ReserveFlow - International Currency Reserves Simulation Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  reserveflow simulate --scenario crisis --duration 12 --charts
  reserveflow compare --scenarios baseline crisis --duration 18
  reserveflow dashboard --port 8080
        """
    )
    
    # Global arguments
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--version', action='version', version='ReserveFlow 0.1.0')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Simulate command
    sim_parser = subparsers.add_parser('simulate', help='Run a single simulation scenario')
    sim_parser.add_argument('--scenario', '-s', default='baseline',
                           choices=['baseline', 'crisis', 'dedollarization', 'inflation_surge'],
                           help='Simulation scenario to run')
    sim_parser.add_argument('--duration', '-d', type=int, default=24,
                           help='Simulation duration in months')
    sim_parser.add_argument('--output', '-o', default='output',
                           help='Output directory for results')
    sim_parser.add_argument('--seed', type=int, help='Random seed for reproducibility')
    sim_parser.add_argument('--charts', action='store_true', help='Generate visualization charts')
    
    # Compare command
    comp_parser = subparsers.add_parser('compare', help='Compare multiple scenarios')
    comp_parser.add_argument('--scenarios', '-s', nargs='+', 
                            default=['baseline', 'crisis'],
                            choices=['baseline', 'crisis', 'dedollarization', 'inflation_surge'],
                            help='Scenarios to compare')
    comp_parser.add_argument('--duration', '-d', type=int, default=18,
                            help='Simulation duration in months')
    comp_parser.add_argument('--output', '-o', default='output',
                            help='Output directory for results')
    
    # Dashboard command
    dash_parser = subparsers.add_parser('dashboard', help='Start interactive dashboard')
    dash_parser.add_argument('--port', '-p', type=int, default=8050,
                            help='Port for dashboard server')
    dash_parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Execute command
    if args.command == 'simulate':
        return run_simulation_command(args)
    elif args.command == 'compare':
        return run_comparison_command(args)
    elif args.command == 'dashboard':
        return run_dashboard_command(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main()) 