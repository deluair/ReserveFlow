"""
Precious Metals Engine - Gold and Silver Market Dynamics with Supply-Demand Fundamentals
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from datetime import datetime
from .base_engine import BaseEngine


class PreciousMetalsEngine(BaseEngine):
    """
    Simulates gold and silver price movements with supply-demand fundamentals,
    central bank buying patterns, mining production, and investor demand cycles
    """
    
    def __init__(self, config: Any, random_state: int = None):
        super().__init__(config, random_state)
        
        # Current prices (USD per ounce) - ensure scalar values
        self.gold_price = float(config.initial_gold_price)
        self.silver_price = float(config.initial_silver_price)
        
        # Volatilities
        self.gold_volatility = config.gold_volatility
        self.silver_volatility = config.silver_volatility
        
        # Central bank holdings and buying patterns (must be set before demand initialization)
        self.cb_gold_holdings = 36000.0  # Global CB holdings in tonnes
        self.annual_cb_purchases = config.gold_central_bank_purchases
        
        # Supply-demand fundamentals
        self.gold_supply = self._initialize_gold_supply()
        self.silver_supply = self._initialize_silver_supply()
        self.gold_demand = self._initialize_gold_demand()
        self.silver_demand = self._initialize_silver_demand()
        
        # Market structure parameters
        self.gold_silver_ratio = 80.0  # Historical average
        self.correlation_with_currencies = {
            "USD": -0.3,  # Negative correlation with USD
            "real_rates": -0.7,  # Strong negative correlation with real rates
            "inflation": 0.6   # Positive correlation with inflation
        }
        
        # Price momentum and mean reversion
        self.momentum_factor = 0.1
        self.mean_reversion_speed = 0.05
        self.long_term_gold_price = 2200.0
        self.long_term_silver_price = 28.0
        
    def initialize(self) -> None:
        """Initialize precious metals market state"""
        # Set initial supply-demand balance
        self._calibrate_supply_demand_balance()
        
        # Initialize storage costs and convenience yields
        self.gold_storage_cost = 0.001  # 0.1% annual
        self.silver_storage_cost = 0.002  # 0.2% annual
        self.convenience_yield = 0.005  # 0.5% annual
    
    def _get_scalar_value(self, value: Any, default: float = 0.0) -> float:
        """Safely extract scalar value from potentially array-like input"""
        if hasattr(value, '__iter__') and not isinstance(value, str):
            # If it's array-like, take the first element or mean
            try:
                if hasattr(value, 'iloc'):  # pandas Series
                    return float(value.iloc[0])
                elif hasattr(value, '__len__') and len(value) > 0:
                    return float(value[0] if hasattr(value, '__getitem__') else np.mean(value))
                else:
                    return default
            except (IndexError, TypeError, ValueError):
                return default
        try:
            return float(value)
        except (TypeError, ValueError):
            return default
        
    def _initialize_gold_supply(self) -> Dict[str, float]:
        """Initialize gold supply components (tonnes per year)"""
        return {
            "mine_production": 3200.0,
            "recycling": 1200.0,
            "central_bank_sales": 0.0,  # Currently net buyers
            "total": 4400.0
        }
    
    def _initialize_silver_supply(self) -> Dict[str, float]:
        """Initialize silver supply components (million ounces per year)"""
        return {
            "mine_production": 800.0,
            "recycling": 180.0,
            "total": 980.0
        }
    
    def _initialize_gold_demand(self) -> Dict[str, float]:
        """Initialize gold demand components (tonnes per year)"""
        return {
            "jewelry": 2100.0,
            "investment": 800.0,
            "central_banks": self.annual_cb_purchases,
            "technology": 300.0,
            "total": 3200.0 + self.annual_cb_purchases
        }
    
    def _initialize_silver_demand(self) -> Dict[str, float]:
        """Initialize silver demand components (million ounces per year)"""
        return {
            "industrial": 550.0,
            "jewelry": 180.0,
            "investment": 200.0,
            "silverware": 50.0,
            "total": 980.0
        }
    
    def _calibrate_supply_demand_balance(self) -> None:
        """Calibrate initial supply-demand balance"""
        # Adjust demand to match supply for initial equilibrium
        gold_supply_demand_gap = self.gold_supply["total"] - self.gold_demand["total"]
        silver_supply_demand_gap = self.silver_supply["total"] - self.silver_demand["total"]
        
        # Store the gaps for price pressure calculation
        self.gold_supply_demand_imbalance = gold_supply_demand_gap
        self.silver_supply_demand_imbalance = silver_supply_demand_gap
    
    def step(self, current_time: datetime, market_state: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate one step of precious metals market evolution"""
        dt = 1.0 / 365.25  # Daily time step
        
        # Update supply-demand fundamentals
        self._update_supply_demand(market_state, dt)
        
        # Calculate price pressure from fundamentals
        gold_pressure = self._calculate_price_pressure("gold", market_state, current_time)
        silver_pressure = self._calculate_price_pressure("silver", market_state, current_time)
        
        # Generate price movements
        gold_return = self._generate_price_return("gold", gold_pressure, market_state, dt)
        silver_return = self._generate_price_return("silver", silver_pressure, market_state, dt)
        
        # Update prices - ensure scalar operations
        self.gold_price = float(self.gold_price * np.exp(gold_return))
        self.silver_price = float(self.silver_price * np.exp(silver_return))
        
        # Update gold-silver ratio dynamics
        self._update_gold_silver_ratio()
        
        # Prepare output
        output = {
            "gold_price": self.gold_price,
            "silver_price": self.silver_price,
            "gold_return": gold_return,
            "silver_return": silver_return,
            "gold_silver_ratio": self.gold_silver_ratio,
            "gold_supply_demand": self.gold_supply_demand_imbalance,
            "silver_supply_demand": self.silver_supply_demand_imbalance,
            "cb_gold_demand": self._get_cb_gold_demand(market_state),
            "gold_supply": self.gold_supply.copy(),
            "gold_demand": self.gold_demand.copy(),
            "silver_supply": self.silver_supply.copy(),
            "silver_demand": self.silver_demand.copy()
        }
        
        # Add to history
        self.add_to_history(output)
        
        return output
    
    def _update_supply_demand(self, market_state: Dict[str, Any], dt: float) -> None:
        """Update supply and demand components"""
        # Update gold demand components
        self._update_gold_demand(market_state, dt)
        self._update_gold_supply(market_state, dt)
        
        # Update silver demand components
        self._update_silver_demand(market_state, dt)
        self._update_silver_supply(market_state, dt)
        
        # Recalculate imbalances
        self.gold_supply_demand_imbalance = self.gold_supply["total"] - self.gold_demand["total"]
        self.silver_supply_demand_imbalance = self.silver_supply["total"] - self.silver_demand["total"]
    
    def _update_gold_demand(self, market_state: Dict[str, Any], dt: float) -> None:
        """Update gold demand components"""
        # Central bank demand (responsive to geopolitical risk)
        geopolitical_risk = self._get_scalar_value(market_state.get("geopolitical_risk", 0.3), 0.3)
        inflation_expectation = self._get_scalar_value(market_state.get("inflation_expectation", 0.02), 0.02)
        
        # CB demand increases with risk and inflation
        cb_demand_multiplier = 1.0 + geopolitical_risk * 2.0 + inflation_expectation * 5.0
        self.gold_demand["central_banks"] = self.annual_cb_purchases * cb_demand_multiplier
        
        # Investment demand (responsive to real rates and currency weakness)
        real_rates = self._get_scalar_value(market_state.get("real_interest_rates", 0.01), 0.01)
        usd_strength = self._get_scalar_value(market_state.get("usd_index", 100.0), 100.0) / 100.0
        
        investment_demand_factor = 1.0 - real_rates * 20.0 - (usd_strength - 1.0) * 2.0
        investment_demand_factor = max(0.5, min(2.0, investment_demand_factor))
        self.gold_demand["investment"] = 800.0 * investment_demand_factor
        
        # Jewelry demand (responsive to price and economic growth)
        gdp_growth = self._get_scalar_value(market_state.get("global_gdp_growth", 0.03), 0.03)
        price_elasticity = -0.5  # Negative elasticity
        price_change = (self.gold_price / self.config.initial_gold_price - 1.0)
        
        jewelry_factor = (1.0 + gdp_growth * 3.0) * (1.0 + price_elasticity * price_change)
        jewelry_factor = max(0.6, min(1.4, jewelry_factor))
        self.gold_demand["jewelry"] = 2100.0 * jewelry_factor
        
        # Update total demand
        self.gold_demand["total"] = sum(v for k, v in self.gold_demand.items() if k != "total")
    
    def _update_gold_supply(self, market_state: Dict[str, Any], dt: float) -> None:
        """Update gold supply components"""
        # Mine production (relatively inelastic in short term)
        production_growth = market_state.get("mining_sector_growth", 0.01)
        supply_constraints = market_state.get("mining_supply_constraints", 0.0)
        
        mine_production_factor = (1.0 + production_growth) * (1.0 - supply_constraints)
        self.gold_supply["mine_production"] = 3200.0 * mine_production_factor
        
        # Recycling (responsive to price)
        price_change = (self.gold_price / self.config.initial_gold_price - 1.0)
        recycling_elasticity = 0.3  # Positive elasticity
        recycling_factor = 1.0 + recycling_elasticity * price_change
        self.gold_supply["recycling"] = 1200.0 * recycling_factor
        
        # Update total supply
        self.gold_supply["total"] = sum(v for k, v in self.gold_supply.items() if k != "total")
    
    def _update_silver_demand(self, market_state: Dict[str, Any], dt: float) -> None:
        """Update silver demand components"""
        # Industrial demand (responsive to economic growth and tech adoption)
        gdp_growth = self._get_scalar_value(market_state.get("global_gdp_growth", 0.03), 0.03)
        tech_growth = self._get_scalar_value(market_state.get("technology_sector_growth", 0.05), 0.05)
        
        industrial_factor = 1.0 + gdp_growth * 2.0 + tech_growth * 1.5
        industrial_factor = max(0.8, min(1.5, industrial_factor))
        self.silver_demand["industrial"] = 550.0 * industrial_factor
        
        # Investment demand (follows gold but more volatile)
        gold_investment_factor = self.gold_demand["investment"] / 800.0
        silver_investment_factor = 1.0 + (gold_investment_factor - 1.0) * 1.5
        self.silver_demand["investment"] = 200.0 * silver_investment_factor
        
        # Update total demand
        self.silver_demand["total"] = sum(v for k, v in self.silver_demand.items() if k != "total")
    
    def _update_silver_supply(self, market_state: Dict[str, Any], dt: float) -> None:
        """Update silver supply components"""
        # Mine production (often byproduct of other metals)
        base_metals_production = market_state.get("base_metals_production", 1.0)
        self.silver_supply["mine_production"] = 800.0 * base_metals_production
        
        # Recycling
        price_change = (self.silver_price / self.config.initial_silver_price - 1.0)
        recycling_factor = 1.0 + 0.4 * price_change  # Higher elasticity than gold
        self.silver_supply["recycling"] = 180.0 * recycling_factor
        
        # Update total supply
        self.silver_supply["total"] = sum(v for k, v in self.silver_supply.items() if k != "total")
    
    def _calculate_price_pressure(self, metal: str, market_state: Dict[str, Any], current_time: datetime) -> float:
        """Calculate fundamental price pressure"""
        if metal == "gold":
            imbalance = self.gold_supply_demand_imbalance
            total_demand = self.gold_demand["total"]
        else:
            imbalance = self.silver_supply_demand_imbalance
            total_demand = self.silver_demand["total"]
        
        # Convert imbalance to price pressure (negative imbalance = demand > supply = upward pressure)
        pressure = -imbalance / total_demand
        
        # Add seasonal factors
        month = current_time.month
        seasonal_factor = self._get_seasonal_factor(metal, month)
        pressure += seasonal_factor
        
        return pressure
    
    def _get_seasonal_factor(self, metal: str, month: int) -> float:
        """Get seasonal demand factors"""
        if metal == "gold":
            # Q4 jewelry demand surge (wedding season, holidays)
            if month in [10, 11, 12]:
                return 0.05
            # Chinese New Year
            elif month in [1, 2]:
                return 0.03
            else:
                return 0.0
        else:  # silver
            # Industrial demand follows economic cycles
            if month in [3, 4, 5, 9, 10]:  # Peak industrial quarters
                return 0.02
            else:
                return 0.0
    
    def _generate_price_return(self, metal: str, pressure: float, 
                             market_state: Dict[str, Any], dt: float) -> float:
        """Generate price return with fundamentals, momentum, and noise"""
        
        # Get current price and parameters
        if metal == "gold":
            current_price = self.gold_price
            volatility = self.gold_volatility
            long_term_price = self.long_term_gold_price
        else:
            current_price = self.silver_price
            volatility = self.silver_volatility
            long_term_price = self.long_term_silver_price
        
        # Fundamental pressure component
        fundamental_return = pressure * 0.1  # Convert pressure to return
        
        # Mean reversion component
        price_deviation = np.log(current_price / long_term_price)
        mean_reversion = -self.mean_reversion_speed * self._get_scalar_value(price_deviation) * dt
        
        # Momentum component (trend following)
        if hasattr(self, 'data_history') and len(self.data_history) > 5:
            # Ensure returns are scalar before calculating mean
            recent_returns = [self._get_scalar_value(d.get(f"{metal}_return", 0.0)) for d in self.data_history[-5:]]
            momentum = self.momentum_factor * np.mean(recent_returns)
        else:
            momentum = 0.0
        
        # Market factor influences
        market_factors = self._get_market_factor_influence(metal, market_state)
        
        # Random component
        random_shock = self.get_random_normal() * volatility * np.sqrt(dt)
        
        # Combine components
        total_return = (fundamental_return + mean_reversion + momentum + 
                       market_factors) * dt + random_shock
        
        return self._get_scalar_value(total_return)
    
    def _get_market_factor_influence(self, metal: str, market_state: Dict[str, Any]) -> float:
        """Calculate influence of market factors on precious metal prices"""
        influence = 0.0
        
        # USD strength effect (negative correlation)
        usd_index = self._get_scalar_value(market_state.get("usd_index", 100.0), 100.0)
        usd_change = (usd_index / 100.0 - 1.0)
        influence += self.correlation_with_currencies["USD"] * usd_change
        
        # Real interest rates effect
        real_rates = self._get_scalar_value(market_state.get("real_interest_rates", 0.01), 0.01)
        influence += self.correlation_with_currencies["real_rates"] * real_rates
        
        # Inflation expectation effect
        inflation_expectation = self._get_scalar_value(market_state.get("inflation_expectation", 0.02), 0.02)
        influence += self.correlation_with_currencies["inflation"] * inflation_expectation
        
        # Risk sentiment effect (safe haven demand)
        risk_sentiment = self._get_scalar_value(market_state.get("risk_sentiment", 0.0), 0.0)
        if risk_sentiment > 0:  # Risk-off sentiment
            influence += 0.1 * risk_sentiment
        
        return float(influence)
    
    def _update_gold_silver_ratio(self) -> None:
        """Update gold-silver ratio with mean reversion"""
        current_ratio = self.gold_price / self.silver_price
        target_ratio = 80.0  # Long-term average
        
        # Mean reversion with some persistence
        reversion_speed = 0.01
        ratio_adjustment = reversion_speed * (target_ratio - current_ratio)
        
        # Apply adjustment through silver price (gold leads)
        if abs(ratio_adjustment) > 0.1:
            silver_adjustment = ratio_adjustment / target_ratio
            self.silver_price *= (1 + silver_adjustment)
        
        self.gold_silver_ratio = self.gold_price / self.silver_price
    
    def _get_cb_gold_demand(self, market_state: Dict[str, Any]) -> float:
        """Get current central bank gold demand"""
        return self.gold_demand["central_banks"]
    
    def get_real_return(self, metal: str, inflation_rate: float) -> float:
        """Calculate real return adjusted for inflation"""
        if metal == "gold":
            nominal_return = (self.gold_price / self.config.initial_gold_price - 1.0)
        else:
            nominal_return = (self.silver_price / self.config.initial_silver_price - 1.0)
        
        real_return = (1 + nominal_return) / (1 + inflation_rate) - 1
        return real_return 