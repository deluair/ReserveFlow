# ReserveFlow

A comprehensive Python-based simulation framework that models the complex dynamics between international currency reserves, precious metal holdings, and exchange rate volatilities in the global financial system.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 🌍 Overview

ReserveFlow incorporates real-world policy decisions, geopolitical tensions, and market mechanisms that drive central bank reserve management strategies during periods of economic uncertainty. The simulation captures unprecedented dynamics in the global financial landscape, including the strategic shift toward non-traditional reserve currencies and the erosion of US dollar dominance from over 70% in 2000 to 59% in Q1 2024.

### Key Statistics Modeled
- China's $3.59 trillion foreign exchange reserves
- Japan's $1.3 trillion reserves  
- Record central bank gold purchases of 1,045 tonnes in 2024
- Global reserve diversification trends and de-dollarization pressures

## 🚀 Features

### Core Simulation Engines

- **🏦 Reserve Management Engine**: Models central bank decision-making for portfolio allocation across currencies, gold, SDRs, and securities
- **💱 Multi-Currency Exchange Rate System**: Stochastic volatility models with regime-switching for major reserve currencies
- **🥇 Precious Metal Market Dynamics**: Gold and silver price movements with supply-demand fundamentals and central bank buying patterns
- **🌐 Geopolitical Risk Framework**: Quantifies geopolitical tensions affecting reserve reallocation decisions
- **🏛️ Special Drawing Rights (SDR) Module**: IMF SDR system modeling with allocation mechanisms

### Advanced Features

- **📊 Liquidity Stress Testing**: Crisis scenarios with rapid reserve liquidations
- **🌊 Cross-Border Capital Flow Modeling**: Global capital flow tracking and monetary policy transmission
- **⚡ Policy Transmission Mechanisms**: Impact of major central bank policies on global reserves
- **🚫 Sanctions and Financial Weapon Dynamics**: Models asset freezing and alternative payment systems

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Quick Install

```bash
git clone https://github.com/deluair/ReserveFlow.git
cd ReserveFlow
pip install -r requirements.txt
pip install -e .
```

### Dependencies

The project uses the following key libraries:
- `numpy`, `pandas`, `scipy` for numerical computing
- `matplotlib`, `seaborn`, `plotly` for visualization
- `dash` for interactive dashboards
- `scikit-learn`, `statsmodels` for statistical modeling
- `yfinance`, `fredapi` for market data (optional)

## 🎯 Quick Start

### Basic Usage

```python
from reserveflow import ReserveFlowSimulation, DefaultConfig

# Create and run a 12-month baseline simulation
config = DefaultConfig()
sim = ReserveFlowSimulation(config)
results = sim.run_simulation(duration_months=12)

print(f"Gold price change: {results['gold_price'].iloc[-1] / results['gold_price'].iloc[0] - 1:.1%}")
```

### Command Line Interface

```bash
# Run a quick demonstration
python main.py

# Run detailed examples
python examples/basic_simulation.py
python examples/scenario_comparison.py

# Use CLI for advanced scenarios
python -m reserveflow.cli simulate --scenario crisis --duration 24
python -m reserveflow.cli compare --scenarios baseline crisis dedollarization
python -m reserveflow.cli dashboard  # Launch interactive dashboard
```

## 📈 Simulation Scenarios

### 1. Baseline Scenario
**Gradual Reserve Diversification**
- USD dominance declining 0.5% per year
- Moderate central bank gold purchases (1,000 tonnes/year)
- Stable geopolitical environment

### 2. Crisis Scenario  
**Major Currency Disruption**
- 2.5x increased volatility across all currencies
- Flight-to-safety dynamics with emergency liquidations
- Coordinated central bank interventions

### 3. De-dollarization Scenario
**Accelerated USD Decline**
- 2% annual USD dominance decline
- Alternative payment system adoption
- Increased bilateral currency arrangements
- Enhanced central bank gold purchases (1,800 tonnes/year)

### 4. Inflation Surge Scenario
**Precious Metal Rally**
- Global inflation surge (8%)
- Gold targeting $3,500/oz, Silver $45/oz
- Supply chain disruptions affecting mining
- Retail investor demand surge

## 📊 Results and Analytics

### Key Metrics Tracked

- **Exchange Rates**: Real-time multi-currency dynamics with correlations
- **Precious Metals**: Gold/silver prices with supply-demand analysis
- **Geopolitical Risk**: Quantified risk indices affecting market behavior
- **Reserve Allocations**: Central bank portfolio compositions
- **Market Stress**: Liquidity conditions and crisis indicators
- **SDR Dynamics**: Special Drawing Rights usage and attractiveness

### Visualization Options

- **Interactive Dashboards**: Real-time monitoring with Plotly/Dash
- **Static Charts**: Publication-ready matplotlib visualizations  
- **Scenario Comparisons**: Multi-scenario analysis and comparison
- **Risk Dashboards**: Comprehensive risk metric monitoring

## 🏗️ Project Structure

```
ReserveFlow/
├── src/reserveflow/           # Main package
│   ├── core/                  # Core simulation engines
│   │   ├── base_engine.py     # Base engine class
│   │   ├── exchange_rate_engine.py
│   │   ├── precious_metals_engine.py
│   │   ├── geopolitical_engine.py
│   │   ├── sdr_engine.py
│   │   └── reserve_engine.py
│   ├── visualization/         # Visualization components
│   │   ├── charts.py          # Chart creation functions
│   │   └── dashboard.py       # Interactive dashboard
│   ├── config.py              # Configuration classes
│   ├── simulation.py          # Main simulation orchestrator
│   └── cli.py                 # Command-line interface
├── examples/                  # Example scripts
├── tests/                     # Test suite
├── docs/                      # Documentation
├── main.py                    # Quick start script
└── requirements.txt           # Dependencies
```

## 🔧 Configuration

### Scenario Configuration

```python
from reserveflow.config import CrisisConfig, DepollarizationConfig

# Crisis scenario with heightened volatility
crisis_config = CrisisConfig()
crisis_config.gold_volatility = 0.40
crisis_config.geopolitical_risk_baseline = 0.8

# De-dollarization scenario
dedollar_config = DepollarizationConfig()
dedollar_config.usd_dominance_decline_rate = 0.02
dedollar_config.gold_central_bank_purchases = 1800.0
```

### Custom Parameters

```python
from reserveflow.config import BaseConfig

class CustomConfig(BaseConfig):
    initial_gold_price = 2500.0
    gold_central_bank_purchases = 1500.0
    geopolitical_risk_baseline = 0.5
    # Add any custom parameters
```

## 📚 Examples

### Scenario Comparison

```python
from reserveflow import ReserveFlowSimulation
from reserveflow.config import DefaultConfig, CrisisConfig, DepollarizationConfig

scenarios = {
    'baseline': DefaultConfig(),
    'crisis': CrisisConfig(),
    'dedollarization': DepollarizationConfig()
}

results = {}
for name, config in scenarios.items():
    sim = ReserveFlowSimulation(config)
    results[name] = sim.run_simulation(duration_months=24)

# Compare gold performance across scenarios
for name, df in results.items():
    gold_return = (df['gold_price'].iloc[-1] / df['gold_price'].iloc[0] - 1) * 100
    print(f"{name}: {gold_return:.1f}% gold return")
```

### Interactive Dashboard

```python
from reserveflow.visualization.dashboard import run_dashboard

# Launch interactive web dashboard
run_dashboard(port=8050)
# Navigate to http://localhost:8050
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python -m pytest tests/ -v
python -m pytest tests/test_simulation.py::test_full_simulation -v
```

## 📖 Documentation

Detailed documentation is available in the `docs/` directory:

- **User Guide**: Complete usage instructions and tutorials
- **API Reference**: Detailed function and class documentation  
- **Configuration Guide**: Parameter customization options
- **Examples**: Step-by-step simulation examples

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📊 Research Applications

### Academic Research
- Monetary policy transmission analysis
- Exchange rate determination studies
- Financial stability and systemic risk assessment
- International coordination mechanisms

### Policy Analysis
- Reserve adequacy assessment
- Intervention strategy optimization
- SDR allocation impact analysis
- Financial sanctions impact modeling

### Market Intelligence
- Central bank behavior prediction
- Precious metal market forecasting
- Currency crisis early warning systems

## 📈 Performance

- **Simulation Speed**: 6-month simulation completes in under 30 seconds
- **Memory Efficient**: Optimized data structures for large-scale simulations
- **Parallel Processing**: Multi-core support for scenario analysis
- **Reproducible Results**: Deterministic random number generation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- International Monetary Fund (IMF) for SDR methodology
- Bank for International Settlements (BIS) for central banking data
- Academic research community for financial modeling frameworks
- Open source community for foundational libraries

## 📞 Support

- **Issues**: Report bugs and request features via [GitHub Issues](https://github.com/deluair/ReserveFlow/issues)
- **Documentation**: Comprehensive guides in the `docs/` directory
- **Examples**: Working examples in the `examples/` directory

## 🔮 Roadmap

- [ ] Real-time data integration with financial APIs
- [ ] Machine learning-based parameter calibration
- [ ] Additional reserve asset classes (cryptocurrencies, commodities)
- [ ] Enhanced geopolitical risk modeling
- [ ] Multi-language support for broader accessibility

---

**ReserveFlow** - Modeling the future of international finance through sophisticated simulation and analysis. 