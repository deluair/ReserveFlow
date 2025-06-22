"""
Configuration classes for different simulation scenarios
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import numpy as np


@dataclass
class BaseConfig:
    """Base configuration class for simulation parameters"""
    
    # Simulation parameters
    start_date: str = "2020-01-01"
    end_date: str = "2025-12-31"
    frequency: str = "D"  # Daily frequency
    random_seed: int = 42
    
    # Currency list
    major_currencies: List[str] = field(default_factory=lambda: ["USD", "EUR", "JPY", "GBP", "CNY"])
    reserve_currencies: List[str] = field(default_factory=lambda: ["USD", "EUR", "JPY", "GBP", "CNY", "CHF", "CAD", "AUD"])
    
    # Initial market conditions
    initial_exchange_rates: Dict[str, float] = field(default_factory=lambda: {
        "EUR/USD": 1.1200,
        "GBP/USD": 1.3100,
        "USD/JPY": 110.00,
        "USD/CNY": 6.4500,
        "USD/CHF": 0.9200,
        "USD/CAD": 1.2500,
        "AUD/USD": 0.7500
    })
    
    # Precious metals initial prices (USD per ounce)
    initial_gold_price: float = 2000.0
    initial_silver_price: float = 25.0
    
    # Volatility parameters
    currency_volatility: Dict[str, float] = field(default_factory=lambda: {
        "EUR": 0.08,
        "GBP": 0.12,
        "JPY": 0.10,
        "CNY": 0.06,
        "CHF": 0.09,
        "CAD": 0.11,
        "AUD": 0.14
    })
    
    gold_volatility: float = 0.20
    silver_volatility: float = 0.35
    
    # Central bank parameters
    num_central_banks: int = 50
    intervention_probability: float = 0.05
    reserve_rebalancing_frequency: int = 30  # days
    
    # Risk parameters
    correlation_decay: float = 0.95
    stress_threshold: float = 2.0  # Standard deviations
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return self.__dict__


@dataclass 
class DefaultConfig(BaseConfig):
    """Default baseline scenario configuration"""
    
    # Baseline trends
    usd_dominance_decline_rate: float = 0.005  # 0.5% per year
    gold_central_bank_purchases: float = 1000.0  # tonnes per year
    geopolitical_risk_baseline: float = 0.3  # Low risk
    
    # Policy parameters
    intervention_strength: float = 0.5
    reserve_diversification_speed: float = 0.02


@dataclass
class CrisisConfig(BaseConfig):
    """Crisis scenario configuration with heightened volatility"""
    
    # Crisis parameters
    currency_volatility: Dict[str, float] = field(default_factory=lambda: {
        "EUR": 0.25,
        "GBP": 0.30,
        "JPY": 0.20,
        "CNY": 0.15,
        "CHF": 0.18,
        "CAD": 0.28,
        "AUD": 0.35
    })
    
    gold_volatility: float = 0.40
    silver_volatility: float = 0.60
    
    # Crisis-specific parameters
    flight_to_safety_intensity: float = 2.0
    central_bank_intervention_frequency: float = 0.15
    intervention_strength: float = 1.2  # Stronger interventions during crisis
    gold_surge_factor: float = 1.5
    geopolitical_risk_baseline: float = 0.8
    gold_central_bank_purchases: float = 1500.0  # tonnes per year (increased during crisis)
    
    # Emergency liquidation parameters
    emergency_liquidation_probability: float = 0.02
    liquidation_impact_factor: float = 0.15


@dataclass
class DepollarizationConfig(BaseConfig):
    """De-dollarization acceleration scenario"""
    
    # De-dollarization parameters
    usd_dominance_decline_rate: float = 0.02  # 2% per year
    yuan_adoption_acceleration: float = 0.03
    gold_central_bank_purchases: float = 1800.0  # tonnes per year
    intervention_strength: float = 0.6  # More targeted interventions
    
    # Alternative reserve assets
    sdr_allocation_increase: float = 0.15
    bilateral_currency_swap_growth: float = 0.25
    
    # Policy coordination
    emerging_market_coordination: float = 0.7
    alternative_payment_system_adoption: float = 0.4
    
    # Sanctions impact
    sanctions_impact_factor: float = 0.3
    reserve_freezing_risk: float = 0.1


@dataclass 
class InflationSurgeConfig(BaseConfig):
    """Inflation surge and precious metal rally scenario"""
    
    # Inflation parameters
    global_inflation_surge: float = 0.08  # 8% inflation
    inflation_persistence: float = 0.9
    
    # Precious metal rally
    gold_target_price: float = 3500.0  # USD per ounce
    silver_target_price: float = 45.0   # USD per ounce
    precious_metal_momentum: float = 1.8
    
    # Supply constraints
    mining_supply_constraint: float = 0.15
    retail_demand_surge: float = 2.5
    
    # Central bank response
    gold_hoarding_intensity: float = 2.0
    reserve_currency_debasement_fear: float = 0.6
    intervention_strength: float = 0.9  # Strong interventions to defend currency
    gold_central_bank_purchases: float = 2000.0  # tonnes per year (highest during inflation surge) 