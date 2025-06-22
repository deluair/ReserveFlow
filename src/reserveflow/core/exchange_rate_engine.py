"""
Exchange Rate Engine - Multi-Currency Exchange Rate System with Stochastic Volatility
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
from datetime import datetime
from .base_engine import BaseEngine


class ExchangeRateEngine(BaseEngine):
    """
    Multi-Currency Exchange Rate System with stochastic volatility models
    for major reserve currencies with correlation structures
    """
    
    def __init__(self, config: Any, random_state: int = None):
        super().__init__(config, random_state)
        self.currencies = config.major_currencies
        self.base_currency = "USD"  # Base currency for all rates
        
        # Exchange rate levels (all vs USD)
        self.exchange_rates = {}
        self.volatilities = {}
        self.correlation_matrix = None
        
        # Stochastic volatility parameters
        self.vol_mean_reversion = 0.1
        self.vol_of_vol = 0.3
        self.vol_persistence = 0.95
        
        # Regime switching parameters
        self.regime_probabilities = np.array([0.8, 0.2])  # [calm, crisis]
        self.current_regime = 0  # Start in calm regime
        self.regime_volatility_multipliers = np.array([1.0, 2.5])
        
    def initialize(self) -> None:
        """Initialize exchange rate system"""
        # Initialize exchange rates from config
        for currency in self.currencies:
            if currency == self.base_currency:
                self.exchange_rates[currency] = 1.0
            else:
                pair = f"{currency}/USD" if currency in ["EUR", "GBP", "AUD"] else f"USD/{currency}"
                if pair in self.config.initial_exchange_rates:
                    if currency in ["EUR", "GBP", "AUD"]:
                        self.exchange_rates[currency] = self.config.initial_exchange_rates[pair]
                    else:
                        self.exchange_rates[currency] = 1.0 / self.config.initial_exchange_rates[pair]
                else:
                    # Default rates if not specified
                    default_rates = {
                        "EUR": 1.12, "GBP": 1.31, "JPY": 0.009, 
                        "CNY": 0.155, "CHF": 1.09, "CAD": 0.80, "AUD": 0.75
                    }
                    self.exchange_rates[currency] = default_rates.get(currency, 1.0)
        
        # Initialize volatilities
        for currency in self.currencies:
            if currency == self.base_currency:
                self.volatilities[currency] = 0.0
            else:
                # Ensure we get a float, not a dict
                vol_config = self.config.currency_volatility
                if isinstance(vol_config, dict):
                    self.volatilities[currency] = vol_config.get(currency, 0.10)
                else:
                    self.volatilities[currency] = float(vol_config)
        
        # Initialize correlation matrix
        self._initialize_correlation_matrix()
        
    def _initialize_correlation_matrix(self) -> None:
        """Initialize realistic correlation matrix for currencies"""
        n_currencies = len(self.currencies) - 1  # Exclude base currency
        
        # Create realistic correlation structure
        base_correlations = {
            # EUR correlations
            ("EUR", "GBP"): 0.65, ("EUR", "JPY"): 0.25, ("EUR", "CNY"): 0.15,
            ("EUR", "CHF"): 0.85, ("EUR", "CAD"): 0.45, ("EUR", "AUD"): 0.35,
            
            # GBP correlations  
            ("GBP", "JPY"): 0.20, ("GBP", "CNY"): 0.10, ("GBP", "CHF"): 0.55,
            ("GBP", "CAD"): 0.40, ("GBP", "AUD"): 0.50,
            
            # JPY correlations
            ("JPY", "CNY"): 0.30, ("JPY", "CHF"): 0.15, ("JPY", "CAD"): 0.25,
            ("JPY", "AUD"): 0.35,
            
            # CNY correlations
            ("CNY", "CHF"): 0.05, ("CNY", "CAD"): 0.20, ("CNY", "AUD"): 0.25,
            
            # CHF correlations
            ("CHF", "CAD"): 0.30, ("CHF", "AUD"): 0.25,
            
            # CAD correlations  
            ("CAD", "AUD"): 0.60,
        }
        
        # Build correlation matrix
        non_base_currencies = [c for c in self.currencies if c != self.base_currency]
        n = len(non_base_currencies)
        correlation_matrix = np.eye(n)
        
        for i, curr1 in enumerate(non_base_currencies):
            for j, curr2 in enumerate(non_base_currencies):
                if i != j:
                    key = tuple(sorted([curr1, curr2]))
                    correlation = base_correlations.get(key, 0.1)  # Default low correlation
                    correlation_matrix[i, j] = correlation
                    
        # Ensure positive definite
        eigenvals, eigenvecs = np.linalg.eigh(correlation_matrix)
        eigenvals = np.maximum(eigenvals, 0.01)  # Minimum eigenvalue
        correlation_matrix = eigenvecs @ np.diag(eigenvals) @ eigenvecs.T
        
        # Normalize diagonal
        d = np.sqrt(np.diag(correlation_matrix))
        correlation_matrix = correlation_matrix / np.outer(d, d)
        
        self.correlation_matrix = correlation_matrix
        
    def step(self, current_time: datetime, market_state: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate one step of exchange rate evolution"""
        dt = 1.0 / 365.25  # Daily time step
        
        # Update regime
        self._update_regime(market_state)
        
        # Update stochastic volatilities
        self._update_volatilities(dt)
        
        # Generate correlated currency shocks
        shocks = self._generate_currency_shocks(dt)
        
        # Update exchange rates
        self._update_exchange_rates(shocks, dt, market_state)
        
        # Prepare output
        output = {
            "exchange_rates": self.exchange_rates.copy(),
            "volatilities": self.volatilities.copy(),
            "regime": self.current_regime,
            "currency_shocks": shocks
        }
        
        # Add to history
        self.add_to_history(output)
        
        return output
    
    def _update_regime(self, market_state: Dict[str, Any]) -> None:
        """Update market regime (calm vs crisis)"""
        # Get geopolitical risk factor
        geopolitical_risk = market_state.get("geopolitical_risk", 0.3)
        
        # Get market stress indicators
        market_stress = 0.0
        if "market_stress" in market_state:
            market_stress = market_state["market_stress"]
        
        # Calculate regime transition probabilities
        stress_factor = geopolitical_risk + market_stress
        crisis_probability = min(0.4, 0.05 + stress_factor * 0.3)
        
        if self.current_regime == 0:  # Currently calm
            if self.get_random_uniform() < crisis_probability:
                self.current_regime = 1
        else:  # Currently crisis
            if self.get_random_uniform() < 0.1:  # 10% chance to return to calm
                self.current_regime = 0
                
    def _update_volatilities(self, dt: float) -> None:
        """Update stochastic volatilities using mean-reverting process"""
        regime_multiplier = self.regime_volatility_multipliers[self.current_regime]
        
        for currency in self.currencies:
            if currency == self.base_currency:
                continue
                
            base_vol = self.config.currency_volatility.get(currency, 0.10)
            target_vol = base_vol * regime_multiplier
            current_vol = self.volatilities[currency]
            
            # Mean-reverting stochastic volatility
            vol_shock = self.get_random_normal() * self.vol_of_vol * np.sqrt(dt)
            new_vol = current_vol + self.vol_mean_reversion * (target_vol - current_vol) * dt + vol_shock
            
            # Ensure positive volatility
            self.volatilities[currency] = max(new_vol, 0.01)
    
    def _generate_currency_shocks(self, dt: float) -> Dict[str, float]:
        """Generate correlated currency shocks"""
        non_base_currencies = [c for c in self.currencies if c != self.base_currency]
        
        # Ensure volatilities are scalar floats
        vol_values = []
        for c in non_base_currencies:
            vol = self.volatilities.get(c, 0.1)
            if isinstance(vol, dict): # Safeguard against nested dicts
                vol = vol.get(c, 0.1)
            vol_values.append(float(vol))

        volatilities = np.array(vol_values)
        
        # Generate correlated shocks
        shocks_array = self.generate_correlated_shocks(
            self.correlation_matrix, 
            volatilities * np.sqrt(dt)
        )
        
        # Convert to dictionary
        shocks = {currency: shock for currency, shock in zip(non_base_currencies, shocks_array)}
        
        return shocks
    
    def _update_exchange_rates(self, shocks: Dict[str, float], dt: float, 
                             market_state: Dict[str, Any]) -> None:
        """Update exchange rates with geometric Brownian motion"""
        
        # Get central bank interventions
        interventions = market_state.get("cb_interventions", {})
        
        for currency in self.currencies:
            if currency == self.base_currency:
                continue
                
            current_rate = self.exchange_rates[currency]
            shock = shocks[currency]
            
            # Add drift (interest rate differential, trend, etc.)
            drift = self._calculate_drift(currency, market_state)
            
            # Add intervention effect
            intervention_effect = interventions.get(currency, 0.0)
            
            # Geometric Brownian motion with interventions
            rate_change = (drift + intervention_effect) * dt + shock
            new_rate = current_rate * np.exp(rate_change)
            
            self.exchange_rates[currency] = new_rate
    
    def _calculate_drift(self, currency: str, market_state: Dict[str, Any]) -> float:
        """Calculate drift term for exchange rate"""
        # Base drift from fundamentals
        base_drift = 0.0
        
        # Add currency-specific trends
        if currency == "CNY":
            # Yuan appreciation trend
            base_drift += 0.02  # 2% annual appreciation
        elif currency == "EUR":
            # Euro stability
            base_drift += 0.001
        elif currency == "JPY":
            # Yen intervention bias
            base_drift -= 0.005
            
        # Add market-wide factors
        risk_sentiment = market_state.get("risk_sentiment", 0.0)
        if currency in ["CHF", "JPY"]:  # Safe haven currencies
            base_drift += risk_sentiment * 0.1
        else:  # Risk currencies
            base_drift -= risk_sentiment * 0.05
            
        return base_drift
    
    def get_cross_rate(self, from_currency: str, to_currency: str) -> float:
        """Calculate cross exchange rate"""
        if from_currency == self.base_currency:
            return 1.0 / self.exchange_rates[to_currency]
        elif to_currency == self.base_currency:
            return self.exchange_rates[from_currency]
        else:
            return self.exchange_rates[from_currency] / self.exchange_rates[to_currency]
    
    def get_all_cross_rates(self) -> Dict[str, float]:
        """Get all currency cross rates"""
        cross_rates = {}
        for from_curr in self.currencies:
            for to_curr in self.currencies:
                if from_curr != to_curr:
                    pair = f"{from_curr}/{to_curr}"
                    cross_rates[pair] = self.get_cross_rate(from_curr, to_curr)
        return cross_rates 