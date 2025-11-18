"""
Circuit breaker pattern implementation for handling API failures.

This module provides a circuit breaker to prevent cascading failures when
the API is experiencing issues. When failure threshold is exceeded, the
circuit opens and prevents further requests until recovery timeout expires.
"""

import time
from typing import Optional
from threading import Lock


class CircuitBreaker:
    """
    Circuit breaker to prevent cascading failures.
    
    Implements the circuit breaker pattern to stop making requests
    when the API is experiencing failures. The circuit opens after
    reaching the failure threshold and closes after the timeout period.
    
    Example:
        >>> breaker = CircuitBreaker(failure_threshold=10, timeout=60)
        >>> if breaker.can_proceed():
        ...     try:
        ...         # Make API request
        ...         breaker.record_success()
        ...     except Exception:
        ...         breaker.record_failure()
    """
    
    def __init__(
        self,
        failure_threshold: int = 10,
        timeout: int = 60,
        enabled: bool = True
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of consecutive failures before opening circuit
            timeout: Seconds to wait before attempting to close circuit (half-open state)
            enabled: Whether circuit breaker is enabled (default: True)
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.enabled = enabled
        
        # State tracking
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half-open
        self._lock = Lock()
    
    def can_proceed(self) -> bool:
        """
        Check if requests can proceed based on circuit state.
        
        Returns:
            True if requests should proceed, False if circuit is open
        """
        if not self.enabled:
            return True
        
        with self._lock:
            if self.state == "closed":
                return True
            
            elif self.state == "open":
                # Check if timeout has passed to enter half-open state
                if self.last_failure_time and (
                    time.time() - self.last_failure_time >= self.timeout
                ):
                    self.state = "half-open"
                    self.success_count = 0
                    return True
                return False
            
            elif self.state == "half-open":
                # Allow limited requests to test if service recovered
                return True
            
            return True
    
    def record_success(self) -> None:
        """
        Record a successful request.
        
        Resets failure count and closes circuit if it was half-open.
        """
        if not self.enabled:
            return
        
        with self._lock:
            if self.state == "half-open":
                self.success_count += 1
                # If we get enough successes, close the circuit
                if self.success_count >= 3:  # Require 3 successes to fully close
                    self.state = "closed"
                    self.failure_count = 0
                    self.success_count = 0
            elif self.state == "closed":
                # Reset failure count on success
                self.failure_count = 0
    
    def record_failure(self) -> None:
        """
        Record a failed request.
        
        Increments failure count and opens circuit if threshold is reached.
        """
        if not self.enabled:
            return
        
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.state == "half-open":
                # Immediately open on failure in half-open state
                self.state = "open"
                self.failure_count = self.failure_threshold
            elif self.state == "closed":
                # Open circuit if failure threshold reached
                if self.failure_count >= self.failure_threshold:
                    self.state = "open"
    
    def get_state(self) -> str:
        """
        Get current circuit breaker state.
        
        Returns:
            Current state: "closed", "open", or "half-open"
        """
        with self._lock:
            return self.state
    
    def get_failure_count(self) -> int:
        """
        Get current failure count.
        
        Returns:
            Number of consecutive failures
        """
        with self._lock:
            return self.failure_count
    
    def reset(self) -> None:
        """
        Reset circuit breaker to initial state.
        
        Useful for testing or manual recovery.
        """
        with self._lock:
            self.failure_count = 0
            self.success_count = 0
            self.last_failure_time = None
            self.state = "closed"

