"""
Reserve Management Engine - Models central bank decision-making for optimal portfolio allocation
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
from .base_engine import BaseEngine


class ReserveManagementEngine(BaseEngine):
    """
    Models central bank decision-making processes for optimal portfolio allocation 
    across foreign currencies, gold, SDRs, and government securities
    """
    
    def __init__(self, config: Any, random_state: int = None):
        super().__init__(config, random_state)
        
        # Reserve composition targets (global average approximation)
        self.target_allocation = {
            "USD": 0.59,  # 59% USD dominance
            "EUR": 0.20,  # 20% EUR
            "JPY": 0.06,  # 6% JPY
            "GBP": 0.05,  # 5% GBP
            "CNY": 0.03,  # 3% CNY (growing)
            "gold": 0.05, # 5% gold
            "SDR": 0.02   # 2% SDR
        }
        
        # Current allocation
        self.current_allocation = self.target_allocation.copy()
        
        # Rebalancing parameters
        self.rebalancing_threshold = 0.02  # 2% deviation triggers rebalancing
        self.rebalancing_speed = 0.1       # 10% adjustment per period
        
        # Risk management
        self.max_concentration = 0.7  # Maximum 70% in any single currency
        self.min_diversification = 0.05  # Minimum 5% in major currencies
        
    def initialize(self) -> None:
        """Initialize reserve management state"""
        # Set initial allocation
        self.current_allocation = self.target_allocation.copy()
        self.last_rebalancing_date = self.current_time
        
    def step(self, current_time: datetime, market_state: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate one step of reserve management decisions"""
        
        # Update target allocation based on market conditions
        self._update_target_allocation(market_state)
        
        # Check if rebalancing is needed
        rebalancing_needed = self._check_rebalancing_trigger(current_time, market_state)
        
        # Execute rebalancing if needed
        if rebalancing_needed:
            self._execute_rebalancing(market_state)
            
        # Calculate intervention decisions
        interventions = self._calculate_interventions(market_state)
        
        # Prepare output
        output = {
            "current_allocation": self.current_allocation.copy(),
            "target_allocation": self.target_allocation.copy(),
            "rebalancing_executed": rebalancing_needed,
            "cb_interventions": interventions,
            "allocation_deviation": self._calculate_allocation_deviation()
        }
        
        self.add_to_history(output)
        return output
    
    def _update_target_allocation(self, market_state: Dict[str, Any]) -> None:
        """Update target allocation based on market conditions"""
        # Get market indicators
        geopolitical_risk = market_state.get("geopolitical_risk", 0.3)
        dedollarization_pressure = market_state.get("dedollarization_pressure", 0.0)
        gold_attractiveness = market_state.get("gold_attractiveness", 0.5)
        
        # Adjust USD allocation
        usd_adjustment = -dedollarization_pressure * 0.1
        self.target_allocation["USD"] = max(0.4, min(0.7, 
            self.target_allocation["USD"] + usd_adjustment))
        
        # Adjust gold allocation
        gold_adjustment = geopolitical_risk * 0.05 + gold_attractiveness * 0.03
        self.target_allocation["gold"] = max(0.02, min(0.15,
            self.target_allocation["gold"] + gold_adjustment))
        
        # Normalize to ensure sum = 1
        self._normalize_allocations()
    
    def _normalize_allocations(self) -> None:
        """Normalize allocations to sum to 1.0"""
        total = sum(self.target_allocation.values())
        for asset in self.target_allocation:
            self.target_allocation[asset] /= total
    
    def _check_rebalancing_trigger(self, current_time: datetime, 
                                 market_state: Dict[str, Any]) -> bool:
        """Check if rebalancing should be triggered"""
        # Time-based rebalancing
        days_since_rebalancing = (current_time - self.last_rebalancing_date).days
        time_trigger = days_since_rebalancing >= self.config.reserve_rebalancing_frequency
        
        # Deviation-based rebalancing
        max_deviation = max(abs(self.current_allocation[asset] - self.target_allocation[asset])
                           for asset in self.target_allocation)
        deviation_trigger = max_deviation > self.rebalancing_threshold
        
        # Market stress emergency rebalancing
        market_stress = market_state.get("market_stress", 0.0)
        stress_trigger = market_stress > 0.8
        
        return time_trigger or deviation_trigger or stress_trigger
    
    def _execute_rebalancing(self, market_state: Dict[str, Any]) -> None:
        """Execute portfolio rebalancing"""
        for asset in self.current_allocation:
            current = self.current_allocation[asset]
            target = self.target_allocation[asset]
            
            # Gradual adjustment
            adjustment = (target - current) * self.rebalancing_speed
            self.current_allocation[asset] = current + adjustment
        
        # Normalize after adjustments
        total = sum(self.current_allocation.values())
        for asset in self.current_allocation:
            self.current_allocation[asset] /= total
            
        self.last_rebalancing_date = self.current_time
    
    def _calculate_interventions(self, market_state: Dict[str, Any]) -> Dict[str, float]:
        """Calculate foreign exchange intervention decisions"""
        interventions = {}
        
        # Get exchange rate data
        exchange_rates = market_state.get("exchange_rates", {})
        volatilities = market_state.get("volatilities", {})
        
        for currency in self.config.major_currencies:
            if currency == "USD":
                continue
                
            # Calculate intervention probability based on volatility and allocation
            vol = volatilities.get(currency, 0.1)
            allocation = self.current_allocation.get(currency, 0.0)
            
            # Higher allocation currencies get more intervention support
            intervention_strength = allocation * vol * self.config.intervention_strength
            
            # Random intervention decision
            if self.get_random_uniform() < self.config.intervention_probability:
                # Intervention direction based on recent movements (simplified)
                direction = self.get_random_uniform() > 0.5
                interventions[currency] = intervention_strength * (1 if direction else -1)
        
        return interventions
    
    def _calculate_allocation_deviation(self) -> float:
        """Calculate total deviation from target allocation"""
        return sum(abs(self.current_allocation[asset] - self.target_allocation[asset])
                  for asset in self.target_allocation) 