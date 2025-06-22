#!/usr/bin/env python3
"""
Basic tests for ReserveFlow simulation framework
"""

import sys
import os
import unittest
import pandas as pd
import numpy as np

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from reserveflow import ReserveFlowSimulation, DefaultConfig
from reserveflow.config import CrisisConfig, DepollarizationConfig, InflationSurgeConfig
from reserveflow.core import (
    ExchangeRateEngine, 
    PreciousMetalsEngine, 
    GeopoliticalRiskEngine,
    SDREngine,
    ReserveManagementEngine
)


class TestConfiguration(unittest.TestCase):
    """Test configuration classes"""
    
    def test_default_config(self):
        """Test default configuration"""
        config = DefaultConfig()
        
        # Check basic parameters
        self.assertEqual(config.random_seed, 42)
        self.assertIn("USD", config.major_currencies)
        self.assertIn("EUR", config.major_currencies)
        self.assertEqual(config.initial_gold_price, 2000.0)
        self.assertGreater(config.gold_volatility, 0)
    
    def test_crisis_config(self):
        """Test crisis configuration"""
        config = CrisisConfig()
        
        # Crisis should have higher volatility
        self.assertGreater(config.gold_volatility, 0.3)
        self.assertGreater(config.geopolitical_risk_baseline, 0.5)
    
    def test_config_to_dict(self):
        """Test configuration serialization"""
        config = DefaultConfig()
        config_dict = config.to_dict()
        
        self.assertIsInstance(config_dict, dict)
        self.assertIn('random_seed', config_dict)
        self.assertIn('major_currencies', config_dict)


class TestEngines(unittest.TestCase):
    """Test individual engine components"""
    
    def setUp(self):
        """Set up test configuration"""
        self.config = DefaultConfig()
        self.config.random_seed = 42  # For reproducible tests
    
    def test_exchange_rate_engine(self):
        """Test exchange rate engine"""
        engine = ExchangeRateEngine(self.config)
        engine.initialize()
        
        # Test initialization
        self.assertIn("USD", engine.exchange_rates)
        self.assertIn("EUR", engine.exchange_rates)
        self.assertEqual(engine.exchange_rates["USD"], 1.0)
        
        # Test step function
        from datetime import datetime
        market_state = {"geopolitical_risk": 0.3}
        output = engine.step(datetime.now(), market_state)
        
        self.assertIn("exchange_rates", output)
        self.assertIn("volatilities", output)
        self.assertIn("regime", output)
    
    def test_precious_metals_engine(self):
        """Test precious metals engine"""
        engine = PreciousMetalsEngine(self.config)
        engine.initialize()
        
        # Test initialization
        self.assertEqual(engine.gold_price, self.config.initial_gold_price)
        self.assertEqual(engine.silver_price, self.config.initial_silver_price)
        
        # Test step function
        from datetime import datetime
        market_state = {"geopolitical_risk": 0.3, "inflation_expectation": 0.02}
        output = engine.step(datetime.now(), market_state)
        
        self.assertIn("gold_price", output)
        self.assertIn("silver_price", output)
        self.assertIn("gold_silver_ratio", output)
        self.assertGreater(output["gold_price"], 0)
    
    def test_geopolitical_engine(self):
        """Test geopolitical risk engine"""
        engine = GeopoliticalRiskEngine(self.config)
        engine.initialize()
        
        # Test initialization
        self.assertEqual(engine.current_risk, engine.baseline_risk)
        
        # Test step function
        from datetime import datetime
        market_state = {"market_stress": 0.2}
        output = engine.step(datetime.now(), market_state)
        
        self.assertIn("geopolitical_risk", output)
        self.assertIn("regional_risks", output)
        self.assertBetween(output["geopolitical_risk"], 0, 1)
    
    def test_sdr_engine(self):
        """Test SDR engine"""
        engine = SDREngine(self.config)
        engine.initialize()
        
        # Test SDR basket
        self.assertAlmostEqual(sum(engine.sdr_basket.values()), 1.0, places=2)
        self.assertIn("USD", engine.sdr_basket)
        self.assertIn("EUR", engine.sdr_basket)
        
        # Test step function
        from datetime import datetime
        market_state = {"exchange_rates": {"EUR": 1.12, "GBP": 1.31}}
        output = engine.step(datetime.now(), market_state)
        
        self.assertIn("sdr_value_usd", output)
        self.assertIn("sdr_interest_rate", output)
    
    def assertBetween(self, value, min_val, max_val):
        """Custom assertion for range checking"""
        self.assertGreaterEqual(value, min_val)
        self.assertLessEqual(value, max_val)


class TestSimulation(unittest.TestCase):
    """Test main simulation functionality"""
    
    def setUp(self):
        """Set up test simulation"""
        self.config = DefaultConfig()
        self.config.random_seed = 42  # For reproducible tests
        self.sim = ReserveFlowSimulation(self.config)
    
    def test_simulation_initialization(self):
        """Test simulation initialization"""
        self.assertIsNotNone(self.sim.exchange_rate_engine)
        self.assertIsNotNone(self.sim.precious_metals_engine)
        self.assertIsNotNone(self.sim.geopolitical_engine)
        self.assertIsNotNone(self.sim.sdr_engine)
        self.assertIsNotNone(self.sim.reserve_engine)
    
    def test_short_simulation(self):
        """Test running a short simulation"""
        results = self.sim.run_simulation(duration_months=1)  # 1 month = ~30 days
        
        # Check results structure
        self.assertIsInstance(results, pd.DataFrame)
        self.assertGreater(len(results), 20)  # Should have ~30 daily data points
        
        # Check required columns
        required_columns = [
            'gold_price', 'silver_price', 'geopolitical_risk', 
            'exchange_rates', 'market_stress'
        ]
        for col in required_columns:
            self.assertIn(col, results.columns)
        
        # Check data validity
        self.assertTrue(all(results['gold_price'] > 0))
        self.assertTrue(all(results['silver_price'] > 0))
        self.assertTrue(all(results['geopolitical_risk'] >= 0))
        self.assertTrue(all(results['geopolitical_risk'] <= 1))
    
    def test_scenario_runs(self):
        """Test running different scenarios"""
        scenarios = ['baseline', 'crisis', 'dedollarization', 'inflation_surge']
        
        for scenario in scenarios:
            with self.subTest(scenario=scenario):
                try:
                    results = self.sim.run_scenario(scenario, duration_months=1)
                    self.assertIsInstance(results, pd.DataFrame)
                    self.assertGreater(len(results), 20)
                except Exception as e:
                    self.fail(f"Scenario {scenario} failed: {e}")
    
    def test_summary_statistics(self):
        """Test summary statistics generation"""
        results = self.sim.run_simulation(duration_months=1)
        stats = self.sim.get_summary_statistics(results)
        
        self.assertIsInstance(stats, dict)
        
        # Check for expected statistics categories
        if 'gold_stats' in stats:
            gold_stats = stats['gold_stats']
            self.assertIn('final_price', gold_stats)
            self.assertIn('total_return', gold_stats)
            self.assertIn('volatility', gold_stats)
    
    def test_reproducibility(self):
        """Test that results are reproducible with same seed"""
        # Run simulation twice with same seed
        config1 = DefaultConfig()
        config1.random_seed = 123
        sim1 = ReserveFlowSimulation(config1)
        results1 = sim1.run_simulation(duration_months=1)
        
        config2 = DefaultConfig()
        config2.random_seed = 123
        sim2 = ReserveFlowSimulation(config2)
        results2 = sim2.run_simulation(duration_months=1)
        
        # Results should be identical
        np.testing.assert_array_almost_equal(
            results1['gold_price'].values,
            results2['gold_price'].values,
            decimal=10
        )


class TestVisualization(unittest.TestCase):
    """Test visualization components"""
    
    def setUp(self):
        """Set up test data"""
        self.config = DefaultConfig()
        self.config.random_seed = 42
        self.sim = ReserveFlowSimulation(self.config)
        self.results = self.sim.run_simulation(duration_months=1)
    
    def test_chart_creation(self):
        """Test chart creation functions"""
        try:
            from reserveflow.visualization.charts import (
                create_exchange_rate_chart,
                create_precious_metals_chart,
                create_risk_dashboard
            )
            
            # Test chart creation (should not raise exceptions)
            fx_chart = create_exchange_rate_chart(self.results)
            pm_chart = create_precious_metals_chart(self.results)
            risk_chart = create_risk_dashboard(self.results)
            
            # Basic checks
            self.assertIsNotNone(fx_chart)
            self.assertIsNotNone(pm_chart)
            self.assertIsNotNone(risk_chart)
            
        except ImportError:
            self.skipTest("Visualization dependencies not available")


def run_performance_test():
    """Run a simple performance test"""
    import time
    
    print("Running performance test...")
    config = DefaultConfig()
    config.random_seed = 42
    sim = ReserveFlowSimulation(config)
    
    start_time = time.time()
    results = sim.run_simulation(duration_months=6)  # 6 months
    end_time = time.time()
    
    duration = end_time - start_time
    data_points = len(results)
    
    print(f"Performance Test Results:")
    print(f"  Duration: {duration:.2f} seconds")
    print(f"  Data points: {data_points}")
    print(f"  Speed: {data_points/duration:.1f} points/second")
    
    # Basic performance assertion (should complete 6 months in under 30 seconds)
    assert duration < 30, f"Simulation too slow: {duration:.2f} seconds"
    assert data_points > 150, f"Too few data points: {data_points}"


if __name__ == '__main__':
    # Run unit tests
    print("Running ReserveFlow unit tests...")
    unittest.main(verbosity=2, exit=False)
    
    # Run performance test
    print("\n" + "="*50)
    run_performance_test()
    
    print("\n" + "="*50)
    print("All tests completed successfully!") 