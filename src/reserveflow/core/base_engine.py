"""
Base engine class for all simulation engines
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
from datetime import datetime, timedelta


class BaseEngine(ABC):
    """Abstract base class for all simulation engines"""
    
    def __init__(self, config: Any, random_state: Optional[int] = None):
        """
        Initialize base engine
        
        Args:
            config: Configuration object
            random_state: Random seed for reproducibility
        """
        self.config = config
        self.random_state = random_state or config.random_seed
        self.rng = np.random.RandomState(self.random_state)
        self.current_time = pd.to_datetime(config.start_date)
        self.end_time = pd.to_datetime(config.end_date)
        self.data_history = []
        
    @abstractmethod
    def initialize(self) -> None:
        """Initialize engine state"""
        pass
    
    @abstractmethod
    def step(self, current_time: datetime, market_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform one simulation step
        
        Args:
            current_time: Current simulation time
            market_state: Current market state
            
        Returns:
            Updated market state from this engine
        """
        pass
    
    def reset(self) -> None:
        """Reset engine to initial state"""
        self.current_time = pd.to_datetime(self.config.start_date)
        self.data_history = []
        self.initialize()
    
    def get_random_normal(self, size: int = 1, loc: float = 0.0, scale: float = 1.0) -> np.ndarray:
        """Generate random normal values"""
        return self.rng.normal(loc, scale, size)
    
    def get_random_uniform(self, size: int = 1, low: float = 0.0, high: float = 1.0) -> np.ndarray:
        """Generate random uniform values"""  
        return self.rng.uniform(low, high, size)
    
    def add_to_history(self, data: Dict[str, Any]) -> None:
        """Add data point to history"""
        data['timestamp'] = self.current_time
        self.data_history.append(data.copy())
    
    def get_history_df(self) -> pd.DataFrame:
        """Get history as pandas DataFrame"""
        if not self.data_history:
            return pd.DataFrame()
        return pd.DataFrame(self.data_history).set_index('timestamp')
    
    def generate_correlated_shocks(self, correlation_matrix: np.ndarray, 
                                 volatilities: np.ndarray) -> np.ndarray:
        """
        Generate correlated random shocks
        
        Args:
            correlation_matrix: Correlation matrix
            volatilities: Volatility vector
            
        Returns:
            Correlated random shocks
        """
        # Cholesky decomposition for correlation
        try:
            cholesky = np.linalg.cholesky(correlation_matrix)
        except np.linalg.LinAlgError:
            # If correlation matrix is not positive definite, use identity
            cholesky = np.eye(len(correlation_matrix))
            
        # Generate independent shocks
        independent_shocks = self.get_random_normal(size=len(volatilities))
        
        # Apply correlation and scale by volatilities
        correlated_shocks = cholesky @ independent_shocks
        return correlated_shocks * volatilities 