"""
Main ReserveFlow Simulation Class
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

from .config import BaseConfig, DefaultConfig
from .core import (
    ReserveManagementEngine,
    ExchangeRateEngine, 
    PreciousMetalsEngine,
    GeopoliticalRiskEngine,
    SDREngine
)


class ReserveFlowSimulation:
    """
    Main simulation class that orchestrates all engines and manages the simulation flow
    """
    
    def __init__(self, config: BaseConfig = None):
        """
        Initialize the ReserveFlow simulation
        
        Args:
            config: Configuration object for simulation parameters
        """
        self.config = config or DefaultConfig()
        self.current_time = pd.to_datetime(self.config.start_date)
        self.end_time = pd.to_datetime(self.config.end_date)
        
        # Initialize engines
        self.exchange_rate_engine = ExchangeRateEngine(self.config)
        self.precious_metals_engine = PreciousMetalsEngine(self.config)
        self.geopolitical_engine = GeopoliticalRiskEngine(self.config)
        self.sdr_engine = SDREngine(self.config)
        self.reserve_engine = ReserveManagementEngine(self.config)
        
        # Market state
        self.market_state = {}
        self.simulation_results = []
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def initialize_simulation(self) -> None:
        """Initialize all engines and market state"""
        self.logger.info("Initializing ReserveFlow simulation...")
        
        # Initialize all engines
        self.exchange_rate_engine.initialize()
        self.precious_metals_engine.initialize()
        self.geopolitical_engine.initialize()
        self.sdr_engine.initialize()
        self.reserve_engine.initialize()
        
        # Initialize market state
        self.market_state = self._initialize_market_state()
        
        self.logger.info("Simulation initialized successfully")
    
    def _initialize_market_state(self) -> Dict[str, Any]:
        """Initialize the global market state"""
        return {
            "timestamp": self.current_time,
            "global_gdp_growth": 0.03,
            "global_inflation": 0.025,
            "global_reserves_usd": 12000,  # $12 trillion
            "market_stress": 0.0,
            "risk_sentiment": 0.0,
            "real_interest_rates": 0.01,
            "inflation_expectation": 0.025,
            "usd_index": 100.0,
            "technology_sector_growth": 0.05,
            "mining_sector_growth": 0.01,
            "base_metals_production": 1.0,
            "mining_supply_constraints": 0.0
        }
    
    def step(self) -> Dict[str, Any]:
        """Execute one simulation step"""
        # Update geopolitical state first (influences other markets)
        geo_output = self.geopolitical_engine.step(self.current_time, self.market_state)
        self.market_state.update(geo_output)
        
        # Update exchange rates
        fx_output = self.exchange_rate_engine.step(self.current_time, self.market_state)
        self.market_state.update(fx_output)
        
        # Update precious metals
        pm_output = self.precious_metals_engine.step(self.current_time, self.market_state)
        self.market_state.update(pm_output)
        
        # Update SDR system
        sdr_output = self.sdr_engine.step(self.current_time, self.market_state)
        self.market_state.update(sdr_output)
        
        # Update reserve management
        reserve_output = self.reserve_engine.step(self.current_time, self.market_state)
        self.market_state.update(reserve_output)
        
        # Update global market indicators
        self._update_market_indicators()
        
        # Store results
        step_results = {
            "timestamp": self.current_time,
            **self.market_state
        }
        self.simulation_results.append(step_results)
        
        return step_results
    
    def _update_market_indicators(self) -> None:
        """Update global market stress and other indicators"""
        # Calculate market stress based on volatilities
        vols = self.market_state.get("volatilities", {})
        if isinstance(vols, dict):
            vol_values = [v for v in vols.values() if isinstance(v, (int, float))]
            currency_vol = np.mean(vol_values) if vol_values else 0.1
        else:
            currency_vol = float(vols)

        geopolitical_risk = self.market_state.get("geopolitical_risk", 0.3)
        
        # Market stress index
        market_stress = min(1.0, currency_vol * 5 + geopolitical_risk * 0.5)
        self.market_state["market_stress"] = market_stress
        
        # Risk sentiment (inverse of market stress)
        self.market_state["risk_sentiment"] = market_stress
        
        # Update USD index based on exchange rates
        usd_strength = 0.0
        exchange_rates = self.market_state.get("exchange_rates", {})
        for currency in ["EUR", "GBP", "JPY", "CNY"]:
            if currency in exchange_rates:
                # Simplified USD index calculation
                if currency in ["EUR", "GBP"]:
                    usd_strength += (1.0 / exchange_rates[currency]) * 0.25
                else:
                    usd_strength += exchange_rates[currency] * 0.25
        
        self.market_state["usd_index"] = 100.0 * usd_strength
    
    def run_simulation(self, duration_months: int = 24) -> pd.DataFrame:
        """
        Run the complete simulation
        
        Args:
            duration_months: Duration of simulation in months
            
        Returns:
            DataFrame with simulation results
        """
        self.logger.info(f"Starting {duration_months}-month simulation...")
        
        # Initialize simulation
        self.initialize_simulation()
        
        # Calculate end time
        self.end_time = self.current_time + timedelta(days=duration_months * 30)
        
        step_count = 0
        while self.current_time < self.end_time:
            # Execute simulation step
            self.step()
            
            # Advance time (daily steps)
            self.current_time += timedelta(days=1)
            step_count += 1
            
            # Log progress
            if step_count % 30 == 0:  # Every 30 days
                self.logger.info(f"Completed {step_count} days of simulation")
        
        self.logger.info("Simulation completed successfully")
        
        # Convert results to DataFrame
        results_df = pd.DataFrame(self.simulation_results)
        results_df.set_index('timestamp', inplace=True)
        
        return results_df
    
    def run_scenario(self, scenario_name: str, duration_months: int = 24) -> pd.DataFrame:
        """
        Run a specific scenario simulation
        
        Args:
            scenario_name: Name of scenario ('baseline', 'crisis', 'dedollarization', 'inflation_surge')
            duration_months: Duration in months
            
        Returns:
            DataFrame with simulation results
        """
        # Import scenario configs
        from .config import CrisisConfig, DepollarizationConfig, InflationSurgeConfig
        
        scenario_configs = {
            'baseline': DefaultConfig(),
            'crisis': CrisisConfig(),
            'dedollarization': DepollarizationConfig(), 
            'inflation_surge': InflationSurgeConfig()
        }
        
        if scenario_name not in scenario_configs:
            raise ValueError(f"Unknown scenario: {scenario_name}")
        
        # Update configuration
        old_config = self.config
        self.config = scenario_configs[scenario_name]
        
        try:
            # Run simulation with scenario config
            results = self.run_simulation(duration_months)
            return results
        finally:
            # Restore original config
            self.config = old_config
    
    def get_summary_statistics(self, results: pd.DataFrame) -> Dict[str, Any]:
        """Calculate summary statistics from simulation results"""
        stats = {}
        
        # Exchange rate statistics
        if 'exchange_rates' in results.columns:
            stats['fx_stats'] = {}
            for currency in self.config.major_currencies[1:]:  # Exclude USD
                if currency in str(results['exchange_rates'].iloc[0]):
                    rates = [r.get(currency, 1.0) for r in results['exchange_rates'] if isinstance(r, dict)]
                    if rates:
                        stats['fx_stats'][currency] = {
                            'final_rate': rates[-1],
                            'volatility': np.std(np.diff(np.log(rates))) * np.sqrt(252),
                            'total_return': (rates[-1] / rates[0] - 1) * 100
                        }
        
        # Precious metals statistics
        if 'gold_price' in results.columns:
            gold_prices = results['gold_price'].dropna()
            stats['gold_stats'] = {
                'final_price': gold_prices.iloc[-1],
                'total_return': (gold_prices.iloc[-1] / gold_prices.iloc[0] - 1) * 100,
                'volatility': gold_prices.pct_change().std() * np.sqrt(252) * 100,
                'max_price': gold_prices.max(),
                'min_price': gold_prices.min()
            }
        
        # Geopolitical risk statistics
        if 'geopolitical_risk' in results.columns:
            geo_risk = results['geopolitical_risk'].dropna()
            stats['geopolitical_stats'] = {
                'average_risk': geo_risk.mean(),
                'max_risk': geo_risk.max(),
                'risk_volatility': geo_risk.std(),
                'crisis_periods': (geo_risk > 0.7).sum()
            }
        
        return stats 