"""
Geopolitical Risk Engine - Models geopolitical tensions affecting reserve management
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
from .base_engine import BaseEngine


class GeopoliticalRiskEngine(BaseEngine):
    """
    Integrates geopolitical tension indicators that affect reserve reallocation decisions,
    modeling events like sanctions, trade wars, and regional conflicts
    """
    
    def __init__(self, config: Any, random_state: int = None):
        super().__init__(config, random_state)
        
        # Base geopolitical risk level
        self.baseline_risk = config.geopolitical_risk_baseline
        self.current_risk = self.baseline_risk
        
        # Risk components
        self.trade_tensions = 0.2
        self.military_conflicts = 0.1
        self.sanctions_risk = 0.1
        self.political_instability = 0.2
        self.economic_warfare = 0.0
        
        # Event persistence and volatility
        self.risk_persistence = 0.95
        self.risk_volatility = 0.1
        
        # Regional risk factors
        self.regional_risks = self._initialize_regional_risks()
        
        # Major event scenarios
        self.event_probabilities = self._initialize_event_probabilities()
        self.active_events = []
        
    def initialize(self) -> None:
        """Initialize geopolitical risk state"""
        # Initialize current risk levels
        self.current_risk = self.baseline_risk
        
        # Set up event tracking
        self.event_history = []
        self.risk_momentum = 0.0
        
    def _initialize_regional_risks(self) -> Dict[str, float]:
        """Initialize regional risk factors"""
        return {
            "europe": 0.2,      # EU-Russia tensions, Brexit aftereffects
            "asia_pacific": 0.4, # China-Taiwan, Korea, South China Sea
            "middle_east": 0.6,  # Regional conflicts, Iran sanctions
            "africa": 0.3,       # Political instability, resource conflicts
            "latin_america": 0.2, # Political changes, economic pressures
            "global": 0.3        # Trade wars, cyber threats
        }
    
    def _initialize_event_probabilities(self) -> Dict[str, Dict[str, Any]]:
        """Initialize major geopolitical event probabilities and impacts"""
        return {
            "trade_war_escalation": {
                "probability": 0.02,  # 2% per month
                "impact": 0.3,
                "duration": 12,  # months
                "affected_currencies": ["CNY", "USD", "EUR"]
            },
            "military_conflict": {
                "probability": 0.005,  # 0.5% per month
                "impact": 0.8,
                "duration": 6,
                "affected_currencies": ["all"]
            },
            "sanctions_expansion": {
                "probability": 0.03,   # 3% per month
                "impact": 0.4,
                "duration": 18,
                "affected_currencies": ["RUB", "CNY", "EUR"]
            },
            "cyberattack_major": {
                "probability": 0.01,   # 1% per month
                "impact": 0.2,
                "duration": 2,
                "affected_currencies": ["USD", "EUR"]
            },
            "political_crisis": {
                "probability": 0.015,  # 1.5% per month
                "impact": 0.25,
                "duration": 8,
                "affected_currencies": ["regional"]
            }
        }
    
    def step(self, current_time: datetime, market_state: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate one step of geopolitical risk evolution"""
        dt = 1.0 / 365.25  # Daily time step
        
        # Check for new geopolitical events
        new_events = self._check_for_events(current_time)
        
        # Update active events
        self._update_active_events(current_time)
        
        # Calculate overall risk level
        self._update_risk_level(market_state, dt)
        
        # Update regional risks
        self._update_regional_risks(dt)
        
        # Calculate de-dollarization pressure
        dedollarization_pressure = self._calculate_dedollarization_pressure()
        
        # Calculate flight-to-safety effects
        flight_to_safety = self._calculate_flight_to_safety_effects()
        
        # Prepare output
        output = {
            "geopolitical_risk": self.current_risk,
            "regional_risks": self.regional_risks.copy(),
            "active_events": self.active_events.copy(),
            "new_events": new_events,
            "dedollarization_pressure": dedollarization_pressure,
            "flight_to_safety": flight_to_safety,
            "trade_tensions": self.trade_tensions,
            "military_conflicts": self.military_conflicts,
            "sanctions_risk": self.sanctions_risk,
            "political_instability": self.political_instability,
            "economic_warfare": self.economic_warfare
        }
        
        # Add to history
        self.add_to_history(output)
        
        return output
    
    def _check_for_events(self, current_time: datetime) -> List[Dict[str, Any]]:
        """Check for new geopolitical events"""
        new_events = []
        
        for event_type, event_config in self.event_probabilities.items():
            # Adjust probability based on current risk level
            base_prob = event_config["probability"] / 30  # Convert monthly to daily
            adjusted_prob = base_prob * (1 + self.current_risk)
            
            if self.get_random_uniform() < adjusted_prob:
                # Event occurs
                event = {
                    "type": event_type,
                    "start_date": current_time,
                    "end_date": current_time + timedelta(days=event_config["duration"] * 30),
                    "impact": event_config["impact"],
                    "affected_currencies": event_config["affected_currencies"]
                }
                new_events.append(event)
                self.active_events.append(event)
                
        return new_events
    
    def _update_active_events(self, current_time: datetime) -> None:
        """Update and remove expired events"""
        self.active_events = [
            event for event in self.active_events 
            if current_time <= event["end_date"]
        ]
    
    def _update_risk_level(self, market_state: Dict[str, Any], dt: float) -> None:
        """Update overall geopolitical risk level"""
        # Base risk from active events
        event_risk = sum(event["impact"] for event in self.active_events)
        
        # Risk from market stress feedback
        market_stress = market_state.get("market_stress", 0.0)
        stress_feedback = market_stress * 0.2
        
        # Mean reversion to baseline
        target_risk = self.baseline_risk + event_risk + stress_feedback
        
        # Add random shocks
        risk_shock = self.get_random_normal() * self.risk_volatility * np.sqrt(dt)
        
        # Update with persistence
        risk_change = (target_risk - self.current_risk) * (1 - self.risk_persistence) * dt + risk_shock
        self.current_risk = max(0.0, min(1.0, self.current_risk + risk_change))
        
        # Update risk momentum
        self.risk_momentum = 0.9 * self.risk_momentum + 0.1 * risk_change
    
    def _update_regional_risks(self, dt: float) -> None:
        """Update regional risk factors"""
        for region in self.regional_risks:
            # Base regional trends
            base_trend = self._get_regional_trend(region)
            
            # Event spillover effects
            spillover = self._calculate_regional_spillover(region)
            
            # Random regional shocks
            regional_shock = self.get_random_normal() * 0.05 * np.sqrt(dt)
            
            # Update regional risk
            risk_change = base_trend + spillover + regional_shock
            new_risk = self.regional_risks[region] + risk_change * dt
            self.regional_risks[region] = max(0.0, min(1.0, new_risk))
    
    def _get_regional_trend(self, region: str) -> float:
        """Get baseline trend for regional risk"""
        trends = {
            "europe": -0.01,      # Gradual stabilization
            "asia_pacific": 0.02,  # Rising tensions
            "middle_east": 0.0,    # Stable but high
            "africa": 0.01,        # Slowly increasing
            "latin_america": -0.005, # Mild improvement
            "global": 0.005       # Increasing global tensions
        }
        return trends.get(region, 0.0)
    
    def _calculate_regional_spillover(self, region: str) -> float:
        """Calculate spillover effects from active events to regions"""
        spillover = 0.0
        
        for event in self.active_events:
            event_spillover = 0.0
            
            if event["type"] == "trade_war_escalation":
                if region in ["asia_pacific", "global"]:
                    event_spillover = event["impact"] * 0.5
                else:
                    event_spillover = event["impact"] * 0.2
                    
            elif event["type"] == "military_conflict":
                # Military conflicts affect all regions
                event_spillover = event["impact"] * 0.3
                
            elif event["type"] == "sanctions_expansion":
                if region in ["europe", "global"]:
                    event_spillover = event["impact"] * 0.4
                else:
                    event_spillover = event["impact"] * 0.1
                    
            spillover += event_spillover
            
        return spillover
    
    def _calculate_dedollarization_pressure(self) -> float:
        """Calculate pressure for de-dollarization from geopolitical events"""
        dedollar_pressure = 0.0
        
        # Base pressure from overall risk
        dedollar_pressure += self.current_risk * 0.3
        
        # Specific event impacts
        for event in self.active_events:
            if event["type"] in ["sanctions_expansion", "economic_warfare"]:
                dedollar_pressure += event["impact"] * 0.5
            elif event["type"] == "trade_war_escalation":
                dedollar_pressure += event["impact"] * 0.3
            elif event["type"] == "cyberattack_major":
                dedollar_pressure += event["impact"] * 0.2
        
        # Regional factors
        if self.regional_risks["asia_pacific"] > 0.5:
            dedollar_pressure += 0.1
        if self.regional_risks["global"] > 0.4:
            dedollar_pressure += 0.05
            
        return min(1.0, dedollar_pressure)
    
    def _calculate_flight_to_safety_effects(self) -> Dict[str, float]:
        """Calculate flight-to-safety effects on different assets"""
        # Base flight-to-safety intensity
        fts_intensity = self.current_risk
        
        # Asset-specific effects
        effects = {
            "gold": fts_intensity * 0.8,      # Strong safe haven
            "usd": fts_intensity * 0.6,       # Traditional safe haven
            "chf": fts_intensity * 0.7,       # Swiss franc safe haven
            "jpy": fts_intensity * 0.5,       # Yen safe haven
            "government_bonds": fts_intensity * 0.9  # Government bonds
        }
        
        # Adjust for specific events
        for event in self.active_events:
            if event["type"] == "sanctions_expansion":
                effects["usd"] *= 0.8  # USD less attractive if sanctions involve US
                effects["gold"] *= 1.2  # Gold more attractive
            elif event["type"] == "cyberattack_major":
                effects["gold"] *= 1.3  # Physical assets preferred
                
        return effects
    
    def get_currency_risk_premium(self, currency: str) -> float:
        """Get geopolitical risk premium for a specific currency"""
        base_premium = self.current_risk * 0.1
        
        # Currency-specific adjustments
        currency_risks = {
            "USD": -0.02,  # Safe haven discount
            "EUR": 0.01,   # Moderate risk
            "JPY": -0.01,  # Safe haven discount
            "GBP": 0.02,   # Brexit and political risk
            "CNY": 0.03,   # Trade tensions
            "CHF": -0.03,  # Strong safe haven
            "CAD": 0.005,  # Stable but commodity-linked
            "AUD": 0.01    # Regional tensions
        }
        
        currency_adjustment = currency_risks.get(currency, 0.0)
        
        # Event-specific adjustments
        for event in self.active_events:
            if currency in event.get("affected_currencies", []) or "all" in event.get("affected_currencies", []):
                currency_adjustment += event["impact"] * 0.1
                
        return base_premium + currency_adjustment
    
    def get_reserve_reallocation_pressure(self) -> Dict[str, float]:
        """Get pressure for reserve reallocation due to geopolitical factors"""
        pressures = {}
        
        # Base reallocation pressure
        base_pressure = self.current_risk * 0.2
        
        # Currency-specific pressures
        pressures["away_from_usd"] = self._calculate_dedollarization_pressure()
        pressures["toward_gold"] = self.current_risk * 0.4
        pressures["toward_diversification"] = base_pressure
        
        # Regional currency preferences
        if self.regional_risks["asia_pacific"] > 0.5:
            pressures["away_from_regional_currencies"] = 0.2
            
        if self.regional_risks["europe"] > 0.4:
            pressures["away_from_eur"] = 0.1
            
        return pressures
    
    def simulate_crisis_scenario(self, crisis_type: str, intensity: float = 1.0) -> Dict[str, Any]:
        """Simulate a specific crisis scenario"""
        if crisis_type == "major_conflict":
            # Simulate major military conflict
            self.current_risk = min(1.0, 0.8 * intensity)
            self.military_conflicts = 0.6 * intensity
            self.regional_risks["global"] = 0.7 * intensity
            
        elif crisis_type == "financial_warfare":
            # Simulate financial/economic warfare
            self.economic_warfare = 0.5 * intensity
            self.sanctions_risk = 0.7 * intensity
            self.current_risk = min(1.0, 0.6 * intensity)
            
        elif crisis_type == "trade_war":
            # Simulate trade war escalation
            self.trade_tensions = 0.8 * intensity
            self.regional_risks["asia_pacific"] = 0.6 * intensity
            self.regional_risks["global"] = 0.5 * intensity
            
        return self.step(datetime.now(), {}) 