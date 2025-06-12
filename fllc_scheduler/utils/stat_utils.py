"""Utility functions for processing and analyzing scheduling data."""

from typing import Any

import numpy as np


def aggregated_data_to_2d_array(aggregated_data: dict) -> tuple[np.ndarray, list[str], list[str]]:
    """
    Convert aggregated data into a 2D array suitable for heatmap visualization.

    Args:
        aggregated_data (dict): A dictionary where keys are tuples of (detailed_state, action)
                                and values are the aggregated data (e.g., Q-values).
    Returns:
        tuple: A tuple containing:
            - A 2D numpy array representing the heatmap data.
            - A list of detailed state labels for the rows.
            - A list of action labels for the columns.
    """
    detailed_states = sorted(set(k[0] for k in aggregated_data.keys()), key=lambda x: (x[1], x[0]))
    actions = sorted(set(k[1] for k in aggregated_data.keys()))
    heatmap_data = np.zeros((len(detailed_states), len(actions)))
    for (detailed_state, action), value in aggregated_data.items():
        row = detailed_states.index(detailed_state)
        col = actions.index(action)
        heatmap_data[row, col] = value
    state_labels = [f"{state[0]}-{state[1]}" for state in detailed_states]
    action_labels = [str(action) for action in actions]
    return heatmap_data, action_labels, state_labels


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
