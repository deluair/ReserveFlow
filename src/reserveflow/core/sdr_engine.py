"""
SDR Engine - Special Drawing Rights System modeling IMF SDR as international reserve asset
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime
from .base_engine import BaseEngine


class SDREngine(BaseEngine):
    """
    Models the IMF's SDR system as an international reserve asset based on 
    a basket of five currencies (USD, EUR, CNY, JPY, GBP)
    """
    
    def __init__(self, config: Any, random_state: int = None):
        super().__init__(config, random_state)
        
        # SDR basket composition (as of 2022 review)
        self.sdr_basket = {
            "USD": 0.43,    # 43.38%
            "EUR": 0.29,    # 29.31% 
            "CNY": 0.13,    # 12.28%
            "JPY": 0.08,    # 7.59%
            "GBP": 0.07     # 7.44%
        }
        
        # Total SDR outstanding (in SDR billions)
        self.total_sdr_outstanding = 660.0  # After 2021 allocation
        
        # SDR value in USD
        self.sdr_value_usd = 1.35  # Approximate
        
        # Interest rate on SDR
        self.sdr_interest_rate = 0.02  # 2% annual
        
        # Allocation and usage tracking
        self.country_allocations = self._initialize_country_allocations()
        self.sdr_transactions = []
        
    def initialize(self) -> None:
        """Initialize SDR system state"""
        # Calculate initial SDR value
        self._update_sdr_value({})
        
        # Initialize transaction tracking
        self.quarterly_sdr_usage = 0.0
        self.emergency_allocations = 0.0
        
    def _initialize_country_allocations(self) -> Dict[str, float]:
        """Initialize SDR allocations by country (SDR billions)"""
        # Major economies' SDR allocations (approximate)
        return {
            "USA": 66.0,
            "CHN": 43.0,
            "JPN": 31.0,
            "GER": 26.0,
            "FRA": 20.0,
            "GBR": 20.0,
            "ITA": 15.0,
            "IND": 13.0,
            "RUS": 12.0,
            "CAN": 11.0,
            "others": 403.0  # Rest of the world
        }
    
    def step(self, current_time: datetime, market_state: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate one step of SDR system evolution"""
        
        # Update SDR value based on basket currencies
        self._update_sdr_value(market_state)
        
        # Update SDR interest rate
        self._update_sdr_interest_rate(market_state)
        
        # Process SDR transactions
        transactions = self._simulate_sdr_transactions(market_state)
        
        # Check for emergency allocations
        emergency_allocation = self._check_emergency_allocation(market_state)
        
        # Calculate SDR demand and usage metrics
        sdr_metrics = self._calculate_sdr_metrics(market_state)
        
        # Prepare output
        output = {
            "sdr_value_usd": self.sdr_value_usd,
            "sdr_interest_rate": self.sdr_interest_rate,
            "sdr_basket": self.sdr_basket.copy(),
            "total_outstanding": self.total_sdr_outstanding,
            "sdr_transactions": transactions,
            "emergency_allocation": emergency_allocation,
            "sdr_metrics": sdr_metrics,
            "basket_performance": self._get_basket_performance(market_state)
        }
        
        # Add to history
        self.add_to_history(output)
        
        return output
    
    def _update_sdr_value(self, market_state: Dict[str, Any]) -> None:
        """Update SDR value based on basket currency movements"""
        sdr_value = 0.0
        
        # Get exchange rates (assume USD base)
        exchange_rates = market_state.get("exchange_rates", {})
        
        for currency, weight in self.sdr_basket.items():
            if currency == "USD":
                currency_value = weight  # USD component
            else:
                # Convert to USD using exchange rates
                rate = exchange_rates.get(currency, 1.0)
                if currency in ["EUR", "GBP"]:
                    currency_value = weight * rate  # These are quoted as XXX/USD
                else:
                    currency_value = weight / rate  # These are quoted as USD/XXX
                    
            sdr_value += currency_value
            
        self.sdr_value_usd = sdr_value
    
    def _update_sdr_interest_rate(self, market_state: Dict[str, Any]) -> None:
        """Update SDR interest rate based on basket currency rates"""
        # SDR rate is weighted average of money market rates of basket currencies
        basket_rates = {
            "USD": market_state.get("usd_3m_rate", 0.05),
            "EUR": market_state.get("eur_3m_rate", 0.03),
            "CNY": market_state.get("cny_3m_rate", 0.03),
            "JPY": market_state.get("jpy_3m_rate", 0.001),
            "GBP": market_state.get("gbp_3m_rate", 0.04)
        }
        
        weighted_rate = sum(
            self.sdr_basket[currency] * basket_rates.get(currency, 0.02)
            for currency in self.sdr_basket
        )
        
        # Apply smoothing
        self.sdr_interest_rate = 0.9 * self.sdr_interest_rate + 0.1 * weighted_rate
    
    def _simulate_sdr_transactions(self, market_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Simulate SDR transactions between countries"""
        transactions = []
        
        # Probability of transactions increases with market stress
        market_stress = market_state.get("market_stress", 0.0)
        geopolitical_risk = market_state.get("geopolitical_risk", 0.3)
        
        transaction_probability = 0.02 + market_stress * 0.1 + geopolitical_risk * 0.05
        
        if self.get_random_uniform() < transaction_probability:
            # Generate a transaction
            transaction = self._generate_sdr_transaction(market_state)
            transactions.append(transaction)
            self.sdr_transactions.append(transaction)
            
        return transactions
    
    def _generate_sdr_transaction(self, market_state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a realistic SDR transaction"""
        # Countries more likely to use SDRs during stress
        high_stress_countries = ["emerging", "small_economies"]
        reserve_rich_countries = ["USA", "CHN", "JPN", "GER"]
        
        # Transaction size (SDR millions)
        transaction_size = self.rng.lognormal(np.log(100), 0.5)  # Log-normal distribution
        transaction_size = min(transaction_size, 5000)  # Cap at 5 billion SDR
        
        # Transaction type
        transaction_types = ["voluntary_exchange", "designation", "repurchase"]
        transaction_type = self.rng.choice(transaction_types, p=[0.4, 0.4, 0.2])
        
        transaction = {
            "type": transaction_type,
            "amount_sdr": transaction_size,
            "amount_usd": transaction_size * self.sdr_value_usd,
            "purpose": self._get_transaction_purpose(market_state),
            "stress_related": market_state.get("market_stress", 0.0) > 0.5
        }
        
        return transaction
    
    def _get_transaction_purpose(self, market_state: Dict[str, Any]) -> str:
        """Determine purpose of SDR transaction"""
        market_stress = market_state.get("market_stress", 0.0)
        
        if market_stress > 0.7:
            return "crisis_liquidity"
        elif market_stress > 0.4:
            return "reserve_management"
        else:
            return "portfolio_optimization"
    
    def _check_emergency_allocation(self, market_state: Dict[str, Any]) -> float:
        """Check if emergency SDR allocation is needed"""
        # Emergency allocation criteria
        global_crisis = market_state.get("global_crisis", False)
        liquidity_shortage = market_state.get("global_liquidity_shortage", 0.0)
        
        emergency_allocation = 0.0
        
        if global_crisis and liquidity_shortage > 0.5:
            # Probability of emergency allocation
            allocation_probability = 0.01 * liquidity_shortage  # 1% chance per 100% shortage
            
            if self.get_random_uniform() < allocation_probability:
                # Emergency allocation (SDR billions)
                emergency_allocation = self.rng.uniform(50, 200)  # 50-200 billion SDR
                self.total_sdr_outstanding += emergency_allocation
                self.emergency_allocations += emergency_allocation
                
                # Distribute to countries
                for country in self.country_allocations:
                    if country != "others":
                        quota_share = self.country_allocations[country] / 257.0  # Excluding others
                        self.country_allocations[country] += emergency_allocation * quota_share
                    else:
                        # Others get remaining
                        others_share = emergency_allocation * 0.5
                        self.country_allocations[country] += others_share
                        
        return emergency_allocation
    
    def _calculate_sdr_metrics(self, market_state: Dict[str, Any]) -> Dict[str, float]:
        """Calculate various SDR system metrics"""
        # SDR as percentage of global reserves
        global_reserves = market_state.get("global_reserves_usd", 12000)  # $12 trillion
        sdr_share = (self.total_sdr_outstanding * self.sdr_value_usd) / global_reserves * 100
        
        # SDR volatility vs USD
        sdr_volatility = self._calculate_sdr_volatility()
        
        # SDR attractiveness index
        attractiveness = self._calculate_sdr_attractiveness(market_state)
        
        # Usage rate (percentage of SDRs actively used)
        quarterly_usage = sum(t["amount_sdr"] for t in self.sdr_transactions[-90:])  # Last 90 days
        usage_rate = quarterly_usage / self.total_sdr_outstanding * 100
        
        return {
            "sdr_share_of_reserves": sdr_share,
            "sdr_volatility": sdr_volatility,
            "sdr_attractiveness": attractiveness,
            "usage_rate": usage_rate,
            "average_transaction_size": np.mean([t["amount_sdr"] for t in self.sdr_transactions[-30:]]) if self.sdr_transactions else 0
        }
    
    def _calculate_sdr_volatility(self) -> float:
        """Calculate SDR volatility based on basket"""
        if len(self.data_history) < 30:
            return 0.05  # Default volatility
            
        # Get recent SDR values, ensuring they are floats
        recent_values = []
        for d in self.data_history[-30:]:
            val = d.get("sdr_value_usd")
            if isinstance(val, (int, float)):
                recent_values.append(val)
        
        if len(recent_values) < 2:
            return 0.05 # Not enough data to calculate

        returns = np.diff(np.log(recent_values))
        
        return np.std(returns) * np.sqrt(252)  # Annualized volatility
    
    def _calculate_sdr_attractiveness(self, market_state: Dict[str, Any]) -> float:
        """Calculate SDR attractiveness relative to individual currencies"""
        attractiveness = 0.5  # Base attractiveness
        
        # Factors that increase SDR attractiveness
        geopolitical_risk = market_state.get("geopolitical_risk", 0.3)
        usd_dominance_concern = market_state.get("dedollarization_pressure", 0.0)
        currency_volatility = market_state.get("currency_volatility_index", 0.1)
        
        # SDR benefits from diversification during uncertainty
        attractiveness += geopolitical_risk * 0.3
        attractiveness += usd_dominance_concern * 0.4
        attractiveness += currency_volatility * 0.2
        
        # Factors that decrease attractiveness
        sdr_complexity = 0.1  # Operational complexity
        limited_liquidity = 0.05  # Limited secondary market
        
        attractiveness -= sdr_complexity + limited_liquidity
        
        return max(0.0, min(1.0, attractiveness))
    
    def _get_basket_performance(self, market_state: Dict[str, Any]) -> Dict[str, Any]:
        """Get performance metrics of SDR basket currencies"""
        performance = {}
        
        for currency in self.sdr_basket:
            weight = self.sdr_basket[currency]
            
            # Get currency performance metrics
            currency_volatility = market_state.get(f"{currency.lower()}_volatility", 0.1)
            currency_return = market_state.get(f"{currency.lower()}_return", 0.0)
            
            performance[currency] = {
                "weight": weight,
                "volatility": currency_volatility,
                "return": currency_return,
                "contribution_to_sdr": weight * currency_return
            }
        
        # Overall basket metrics
        performance["basket_return"] = sum(
            perf["contribution_to_sdr"] for perf in performance.values() 
            if isinstance(perf, dict)
        )
        
        performance["basket_volatility"] = np.sqrt(
            sum(
                (performance[curr]["weight"] * performance[curr]["volatility"]) ** 2
                for curr in self.sdr_basket
            )
        )
        
        return performance
    
    def simulate_basket_rebalancing(self, new_weights: Dict[str, float]) -> Dict[str, Any]:
        """Simulate SDR basket rebalancing (happens every 5 years)"""
        if abs(sum(new_weights.values()) - 1.0) > 0.001:
            raise ValueError("New weights must sum to 1.0")
            
        old_basket = self.sdr_basket.copy()
        self.sdr_basket = new_weights.copy()
        
        # Calculate impact of rebalancing
        rebalancing_impact = {
            "old_basket": old_basket,
            "new_basket": new_weights,
            "weight_changes": {
                curr: new_weights.get(curr, 0) - old_basket.get(curr, 0)
                for curr in set(list(old_basket.keys()) + list(new_weights.keys()))
            }
        }
        
        return rebalancing_impact
    
    def get_sdr_demand_forecast(self, market_state: Dict[str, Any], months_ahead: int = 12) -> Dict[str, float]:
        """Forecast SDR demand based on current conditions"""
        base_demand = self.total_sdr_outstanding * 0.1  # 10% annual turnover
        
        # Adjust for risk factors
        geopolitical_risk = market_state.get("geopolitical_risk", 0.3)
        currency_crisis_risk = market_state.get("currency_crisis_risk", 0.1)
        liquidity_stress = market_state.get("liquidity_stress", 0.0)
        
        demand_multiplier = 1.0 + geopolitical_risk * 0.5 + currency_crisis_risk * 0.8 + liquidity_stress * 0.3
        
        forecast = {
            "base_demand": base_demand,
            "risk_adjusted_demand": base_demand * demand_multiplier,
            "demand_multiplier": demand_multiplier,
            "forecast_horizon_months": months_ahead
        }
        
        return forecast 