"""Utility functions for processing and analyzing scheduling data."""

from typing import Any


def average(seq: Any) -> float:
    """Calculate the average of a sequence of numbers."""
    return sum(seq) / len(seq) if seq else 0.0


def normalize(reward: float, min_reward: int, max_reward: int) -> float:
    """
    Normalize the reward value to a range between 0 and 1.

    Args:
        reward (float): The reward value to normalize.
        min_reward (int): The minimum possible reward.
        max_reward (int): The maximum possible reward.
    Returns:
        float: The normalized reward value between 0 and 1.
    """
    reward_range = max_reward - min_reward
    if reward_range == 0:
        return 0
    return (reward - min_reward) / reward_range
