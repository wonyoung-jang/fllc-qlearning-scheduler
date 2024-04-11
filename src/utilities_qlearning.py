"""
This module contains utility functions for the Q-learning algorithm.

"""


def normalize_reward(reward, min_reward, max_reward) -> float:
    """
    Normalize the reward for the current state-action pair.

    """
    if max_reward - min_reward == 0:
        return 0
    else:
        return (reward - min_reward) / (max_reward - min_reward)