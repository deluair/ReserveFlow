"""
ReserveFlow: International Currency Reserves and Precious Metal Dynamics Simulation

A comprehensive Python-based simulation framework that models the complex dynamics 
between international currency reserves, precious metal holdings, and exchange rate 
volatilities in the global financial system.
"""

__version__ = "0.1.0"
__author__ = "ReserveFlow Development Team"
__email__ = "dev@reserveflow.org"

from .simulation import ReserveFlowSimulation
from .config import DefaultConfig, CrisisConfig, DepollarizationConfig

__all__ = [
    "ReserveFlowSimulation",
    "DefaultConfig", 
    "CrisisConfig",
    "DepollarizationConfig"
] 