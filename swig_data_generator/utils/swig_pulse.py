"""
Swig Pulse Algorithm - Temporal Distribution Generator
Uses Non-Homogeneous Poisson Process (NHPP) to simulate realistic order arrival times.
Swig's unique pattern: Sharp spike at 3pm for school rush.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Tuple


class SwigPulse:
    """Generates realistic order timestamps based on Swig's operational patterns."""

    def __init__(self, seed: int = None):
        if seed:
            np.random.seed(seed)

        # Hourly weights (0-23 hours) - representing relative traffic volume
        # Swig typically opens at 6am and closes at 10pm
        self.weekday_weights = [
            0.00, 0.00, 0.00, 0.00, 0.00, 0.00,  # 0-5am: Closed
            0.03, 0.05, 0.04, 0.03, 0.04, 0.06,  # 6-11am: Morning slow build
            0.08, 0.06, 0.05,                      # 12-2pm: Lunch moderate
            0.18, 0.20, 0.12,                      # 3-5pm: SCHOOL RUSH (Peak!)
            0.08, 0.05, 0.03,                      # 6-8pm: Evening decline
            0.00, 0.00, 0.00                       # 9-11pm: Closed/winding down
        ]

        self.weekend_weights = [
            0.00, 0.00, 0.00, 0.00, 0.00, 0.00,  # 0-5am: Closed
            0.02, 0.04, 0.06, 0.08, 0.10, 0.12,  # 6-11am: Gradual morning build
            0.12, 0.10, 0.10,                      # 12-2pm: Sustained lunch
            0.10, 0.08, 0.06,                      # 3-5pm: No school rush, steady
            0.06, 0.04, 0.02,                      # 6-8pm: Evening
            0.00, 0.00, 0.00                       # 9-11pm: Closed
        ]

        # Special day modifiers
        self.friday_modifier = 1.15  # Fridays are busier
        self.monday_modifier = 0.90  # Mondays slightly slower

    def _normalize_weights(self, weights: List[float]) -> np.ndarray:
        """Normalize weights to sum to 1.0"""
        arr = np.array(weights)
        return arr / arr.sum()

    def _apply_day_modifier(self, base_volume: int, date: datetime) -> int:
        """Apply day-of-week modifiers to base volume."""
        weekday = date.weekday()
        if weekday == 4:  # Friday
            return int(base_volume * self.friday_modifier)
        elif weekday == 0:  # Monday
            return int(base_volume * self.monday_modifier)
        return base_volume

    def _apply_weather_modifier(self, base_volume: int, weather: str = 'normal') -> int:
        """Apply weather modifiers (simplified)."""
        modifiers = {
            'hot': 1.20,      # Hot days = more drinks
            'cold': 0.85,     # Cold days = fewer
            'rainy': 0.75,    # Rain = significantly fewer
            'normal': 1.00
        }
        return int(base_volume * modifiers.get(weather, 1.0))

    def generate_daily_timestamps(
        self,
        date: datetime,
        base_volume: int = 1000,
        is_weekend: bool = None,
        weather: str = 'normal',
        store_open: int = 6,
        store_close: int = 22
    ) -> List[datetime]:
        """
        Generate order timestamps for a single day.

        Args:
            date: The date to generate timestamps for
            base_volume: Target number of orders (will vary +-15%)
            is_weekend: Override weekend detection
            weather: Weather condition ('hot', 'cold', 'rainy', 'normal')
            store_open: Opening hour (24h format)
            store_close: Closing hour (24h format)

        Returns:
            List of datetime timestamps sorted chronologically
        """
        # Determine if weekend
        if is_weekend is None:
            is_weekend = date.weekday() >= 5

        # Select appropriate weights
        weights = self.weekend_weights if is_weekend else self.weekday_weights

        # Zero out closed hours
        adjusted_weights = weights.copy()
        for h in range(24):
            if h < store_open or h >= store_close:
                adjusted_weights[h] = 0

        probs = self._normalize_weights(adjusted_weights)

        # Calculate actual volume with modifiers and randomness
        volume = self._apply_day_modifier(base_volume, date)
        volume = self._apply_weather_modifier(volume, weather)
        daily_volume = int(np.random.normal(volume, volume * 0.15))
        daily_volume = max(daily_volume, int(volume * 0.5))  # Floor at 50% of target

        # Generate hour distribution
        hours = np.random.choice(np.arange(24), size=daily_volume, p=probs)

        # Generate random minutes and seconds within each hour
        minutes = np.random.randint(0, 60, size=daily_volume)
        seconds = np.random.randint(0, 60, size=daily_volume)

        # Create timestamps
        base_date = datetime(date.year, date.month, date.day)
        timestamps = [
            base_date + timedelta(hours=int(h), minutes=int(m), seconds=int(s))
            for h, m, s in zip(hours, minutes, seconds)
        ]

        return sorted(timestamps)

    def generate_rush_timestamps(
        self,
        date: datetime,
        rush_start: int = 15,  # 3pm
        rush_end: int = 17,    # 5pm
        intensity: float = 1.5
    ) -> List[datetime]:
        """
        Generate additional timestamps during rush periods (school rush).
        Use this to inject extra volume during peak times.
        """
        rush_volume = int(200 * intensity)  # Extra orders during rush
        hours = np.random.uniform(rush_start, rush_end, size=rush_volume)

        base_date = datetime(date.year, date.month, date.day)
        timestamps = []

        for h in hours:
            hour_int = int(h)
            minute_float = (h - hour_int) * 60
            minute_int = int(minute_float)
            second_int = int((minute_float - minute_int) * 60)

            timestamps.append(
                base_date + timedelta(hours=hour_int, minutes=minute_int, seconds=second_int)
            )

        return sorted(timestamps)

    def get_hourly_distribution(self, date: datetime) -> dict:
        """Get expected hourly distribution for a given date (for validation)."""
        is_weekend = date.weekday() >= 5
        weights = self.weekend_weights if is_weekend else self.weekday_weights
        probs = self._normalize_weights(weights)

        return {
            f"{h:02d}:00": round(p * 100, 2)
            for h, p in enumerate(probs)
        }


def get_time_period(timestamp: datetime) -> str:
    """Classify timestamp into time period for business logic."""
    hour = timestamp.hour

    if 6 <= hour < 11:
        return 'morning'
    elif 11 <= hour < 14:
        return 'lunch'
    elif 14 <= hour < 17:
        return 'after_school'
    elif 17 <= hour < 22:
        return 'evening'
    else:
        return 'closed'


def simulate_queue_position(
    timestamp: datetime,
    is_linebuster: bool = True
) -> int:
    """
    Simulate queue position based on time and whether linebuster is active.
    Linebuster moves upstream; window-only has position 0-1.
    """
    if not is_linebuster:
        return np.random.choice([0, 1], p=[0.7, 0.3])

    hour = timestamp.hour

    # Peak hours = deeper queues
    if 15 <= hour <= 17:  # School rush
        return int(np.random.choice(range(1, 16), p=np.array([
            0.02, 0.03, 0.05, 0.08, 0.10, 0.12, 0.12, 0.12,
            0.10, 0.08, 0.06, 0.04, 0.03, 0.03, 0.02
        ])))
    elif 11 <= hour <= 14:  # Lunch
        return int(np.random.choice(range(1, 10), p=np.array([
            0.05, 0.10, 0.15, 0.20, 0.20, 0.15, 0.08, 0.05, 0.02
        ])))
    else:  # Off-peak
        return int(np.random.choice(range(1, 6), p=np.array([
            0.30, 0.30, 0.20, 0.12, 0.08
        ])))
