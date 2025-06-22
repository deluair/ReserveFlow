# ReserveFlow User Guide

## Table of Contents
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Scenarios](#scenarios)
- [Configuration](#configuration)
- [Visualization](#visualization)
- [CLI Reference](#cli-reference)
- [API Reference](#api-reference)

## Quick Start

Get started with ReserveFlow in just a few commands:

```bash
# Clone and install
git clone <repository-url>
cd ReserveFlow
pip install -r requirements.txt
pip install -e .

# Run a quick simulation
python main.py

# Or run a detailed example
python examples/basic_simulation.py
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Install ReserveFlow
```bash
pip install -e .
```

## Basic Usage

### Python API

```python
from reserveflow import ReserveFlowSimulation, DefaultConfig

# Create simulation with default configuration
sim = ReserveFlowSimulation(DefaultConfig())

# Run baseline scenario for 24 months
results = sim.run_simulation(duration_months=24)

# Display summary statistics
stats = sim.get_summary_statistics(results)
print(stats)

# Save results
results.to_csv('simulation_results.csv')
```

### Command Line Interface

```bash
# Run a simulation
reserveflow simulate --scenario baseline --duration 12 --charts

# Compare multiple scenarios
reserveflow compare --scenarios baseline crisis --duration 18

# Start interactive dashboard
reserveflow dashboard
```

## Scenarios

ReserveFlow includes four predefined scenarios:

### 1. Baseline Scenario
- **Description**: Gradual reserve diversification with current trends
- **Key Features**:
  - USD dominance slowly declining (0.5% per year)
  - Moderate central bank gold purchases (1,000 tonnes/year)
  - Low geopolitical risk baseline
  - Standard market volatility

```python
from reserveflow.config import DefaultConfig
config = DefaultConfig()
sim = ReserveFlowSimulation(config)
results = sim.run_scenario('baseline', duration_months=24)
```

### 2. Crisis Scenario
- **Description**: Major currency disruption with heightened volatility
- **Key Features**:
  - Elevated currency volatility (2.5x normal)
  - Increased flight-to-safety behavior
  - Emergency liquidation events
  - High geopolitical risk

```python
results = sim.run_scenario('crisis', duration_months=18)
```

### 3. De-dollarization Scenario
- **Description**: Accelerated shift away from USD reserves
- **Key Features**:
  - Rapid USD dominance decline (2% per year)
  - Increased Yuan adoption
  - Enhanced central bank gold purchases (1,800 tonnes/year)
  - Alternative payment system adoption

```python
results = sim.run_scenario('dedollarization', duration_months=30)
```

### 4. Inflation Surge Scenario
- **Description**: High inflation driving precious metal rally
- **Key Features**:
  - Global inflation surge (8%)
  - Gold target price: $3,500/oz
  - Silver target price: $45/oz
  - Mining supply constraints

```python
results = sim.run_scenario('inflation_surge', duration_months=24)
```

## Configuration

### Custom Configuration

```python
from reserveflow.config import BaseConfig
from dataclasses import dataclass

@dataclass
class CustomConfig(BaseConfig):
    # Override specific parameters
    initial_gold_price: float = 2500.0
    gold_volatility: float = 0.30
    geopolitical_risk_baseline: float = 0.6
    
    # Custom currency list
    major_currencies: List[str] = field(default_factory=lambda: 
        ["USD", "EUR", "JPY", "GBP", "CNY", "CHF"])

# Use custom configuration
sim = ReserveFlowSimulation(CustomConfig())
```

### Key Configuration Parameters

- **Simulation Period**: `start_date`, `end_date`, `frequency`
- **Market Parameters**: `initial_exchange_rates`, `currency_volatility`
- **Precious Metals**: `initial_gold_price`, `initial_silver_price`, `gold_volatility`
- **Central Banks**: `num_central_banks`, `intervention_probability`
- **Risk Factors**: `geopolitical_risk_baseline`, `correlation_decay`

## Visualization

### Interactive Charts

```python
from reserveflow.visualization.charts import (
    create_exchange_rate_chart,
    create_precious_metals_chart,
    create_risk_dashboard
)

# Create interactive charts
fx_chart = create_exchange_rate_chart(results)
pm_chart = create_precious_metals_chart(results)
risk_chart = create_risk_dashboard(results)

# Save to HTML
charts = {
    'exchange_rates': fx_chart,
    'precious_metals': pm_chart,
    'risk_dashboard': risk_chart
}
save_charts_to_html(charts, "output")
```

### Dashboard

Start the interactive dashboard:

```bash
reserveflow dashboard --port 8050
```

Then navigate to `http://localhost:8050` to access the dashboard.

### Matplotlib Charts

```python
from reserveflow.visualization.charts import create_matplotlib_summary

# Create summary chart
create_matplotlib_summary(results)
# Saves as 'reserveflow_summary.png'
```

## CLI Reference

### Global Options
- `--verbose, -v`: Enable verbose output
- `--version`: Show version information

### Commands

#### simulate
Run a single simulation scenario.

```bash
reserveflow simulate [OPTIONS]
```

**Options:**
- `--scenario, -s`: Scenario to run (baseline, crisis, dedollarization, inflation_surge)
- `--duration, -d`: Duration in months (default: 24)
- `--output, -o`: Output directory (default: output)
- `--seed`: Random seed for reproducibility
- `--charts`: Generate visualization charts

**Examples:**
```bash
reserveflow simulate --scenario crisis --duration 12 --charts
reserveflow simulate --scenario baseline --duration 6 --seed 42
```

#### compare
Compare multiple scenarios.

```bash
reserveflow compare [OPTIONS]
```

**Options:**
- `--scenarios, -s`: Scenarios to compare (space-separated)
- `--duration, -d`: Duration in months (default: 18)
- `--output, -o`: Output directory (default: output)

**Examples:**
```bash
reserveflow compare --scenarios baseline crisis dedollarization
reserveflow compare --scenarios baseline inflation_surge --duration 24
```

#### dashboard
Start interactive dashboard.

```bash
reserveflow dashboard [OPTIONS]
```

**Options:**
- `--port, -p`: Port for dashboard server (default: 8050)
- `--debug`: Run in debug mode

**Examples:**
```bash
reserveflow dashboard
reserveflow dashboard --port 8080 --debug
```

## API Reference

### Core Classes

#### ReserveFlowSimulation
Main simulation class that orchestrates all engines.

**Methods:**
- `__init__(config)`: Initialize simulation
- `run_simulation(duration_months)`: Run complete simulation
- `run_scenario(scenario_name, duration_months)`: Run specific scenario
- `get_summary_statistics(results)`: Calculate summary statistics

#### Configuration Classes
- `BaseConfig`: Base configuration class
- `DefaultConfig`: Default baseline scenario
- `CrisisConfig`: Crisis scenario configuration
- `DepollarizationConfig`: De-dollarization scenario
- `InflationSurgeConfig`: Inflation surge scenario

### Engine Classes

#### ExchangeRateEngine
Models multi-currency exchange rate dynamics with stochastic volatility.

**Key Features:**
- Regime switching (calm/crisis)
- Correlation structure
- Central bank interventions

#### PreciousMetalsEngine
Simulates gold and silver markets with supply-demand fundamentals.

**Key Features:**
- Central bank purchasing
- Industrial demand
- Seasonal patterns
- Gold-silver ratio dynamics

#### GeopoliticalRiskEngine
Models geopolitical events and their market impact.

**Key Features:**
- Event-driven risk spikes
- Regional risk factors
- De-dollarization pressure
- Flight-to-safety effects

#### SDREngine
Models IMF Special Drawing Rights system.

**Key Features:**
- Basket currency dynamics
- Emergency allocations
- Transaction modeling
- Attractiveness metrics

#### ReserveManagementEngine
Models central bank reserve allocation decisions.

**Key Features:**
- Portfolio optimization
- Rebalancing triggers
- Risk management
- Intervention strategies

### Visualization Functions

- `create_exchange_rate_chart(results)`: Exchange rate evolution
- `create_precious_metals_chart(results)`: Gold/silver price dynamics
- `create_risk_dashboard(results)`: Risk metrics dashboard
- `create_scenario_comparison(scenarios)`: Multi-scenario comparison
- `create_matplotlib_summary(results)`: Static summary chart

## Examples

### Custom Scenario Analysis

```python
from reserveflow import ReserveFlowSimulation
from reserveflow.config import DefaultConfig

# Create custom high-volatility scenario
config = DefaultConfig()
config.currency_volatility = {c: v * 2 for c, v in config.currency_volatility.items()}
config.geopolitical_risk_baseline = 0.8
config.gold_central_bank_purchases = 2000.0

sim = ReserveFlowSimulation(config)
results = sim.run_simulation(duration_months=12)

# Analyze results
stats = sim.get_summary_statistics(results)
print("High Volatility Scenario Results:")
for category, metrics in stats.items():
    print(f"{category}: {metrics}")
```

### Batch Processing

```python
import pandas as pd

scenarios = ['baseline', 'crisis', 'dedollarization', 'inflation_surge']
all_results = {}

sim = ReserveFlowSimulation()

for scenario in scenarios:
    print(f"Running {scenario}...")
    results = sim.run_scenario(scenario, duration_months=18)
    all_results[scenario] = results
    
    # Save individual results
    results.to_csv(f"{scenario}_results.csv")

# Create comparison
from reserveflow.visualization.charts import create_scenario_comparison
comparison_chart = create_scenario_comparison(all_results)
comparison_chart.write_html("scenario_comparison.html")
```

## Tips and Best Practices

1. **Reproducibility**: Always set a random seed for reproducible results
2. **Performance**: For large simulations, consider reducing frequency or duration
3. **Memory**: Monitor memory usage for very long simulations
4. **Validation**: Compare results across different configurations to validate models
5. **Documentation**: Document custom configurations for future reference

## Troubleshooting

### Common Issues

**Import Errors**
```python
# Ensure proper installation
pip install -e .

# Check Python path
import sys
sys.path.append('path/to/reserveflow/src')
```

**Visualization Issues**
```python
# Install additional dependencies
pip install plotly dash matplotlib seaborn

# For Jupyter notebooks
pip install jupyter ipykernel
```

**Performance Issues**
- Reduce simulation duration for testing
- Use lower frequency (weekly instead of daily)
- Monitor system resources

For additional support, check the examples directory and run the provided scripts. 