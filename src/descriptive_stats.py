''' TODO
"""This module contains the MplWidget class, which is responsible for plotting Q-Learning data using Matplotlib and PyQt."""
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import QWidget, QVBoxLayout


class MplWidget(QWidget):
    """Class to plot Q-Learning data using Matplotlib and PyQt."""
    
    def __init__(self, parent=None):
        """Initialize MplWidget object."""
        super(MplWidget, self).__init__(parent)
        self.figure = Figure(
            figsize=(5, 3),
            dpi=100,
            tight_layout=True,
            facecolor="aliceblue",
            edgecolor="darkslategrey",
            linewidth=0.8,
        )
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def plot_convergence(self, x_data, y_data, avg_change_data, eps):
        """Plot the convergence of Q-values over training episodes."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # Existing Q-value change plot
        ax.plot(x_data, y_data, "-o", label="Q-Value Change", color="orange")  # Using color for differentiation

        # Check if average change data is provided
        if avg_change_data:
            # Plotting average change as a second line
            ax.plot(
                x_data,
                avg_change_data,
                "^",
                linestyle="solid",
                label="Average Q-Value Change",
                color="purple",
            )  # Different color

        ax.set_title("Q-Value Changes Over Episodes")
        ax.set_xlabel("Training Episode")
        ax.set_ylabel("Q-Value Change (Rewards)")
        ax.set_ylim(
            [
                min(min(y_data), min(avg_change_data if avg_change_data else y_data)),
                max(max(y_data), max(avg_change_data if avg_change_data else y_data)),
            ]
        )
        ax.set_xlim([1, eps])  # Ensure the X-axis correctly represents the episode range

        ax.legend(loc="upper right")

        ax.grid(True)  # Add gridlines for better readability

        ax.set_xticks(np.arange(1, eps + 1, 1))
        ax.set_xticklabels(np.arange(1, eps + 1, 1), horizontalalignment="right")
        if eps > 10:
            ax.set_xticks(np.arange(1, eps + 1, 10))
            ax.set_xticklabels(np.arange(1, eps + 1, 10), horizontalalignment="right")

        ax.set_yticks(np.arange(ax.get_ylim()[0], ax.get_ylim()[1], 5.0))
        ax.set_yticklabels(
            np.arange(ax.get_ylim()[0], ax.get_ylim()[1], 5.0),
            horizontalalignment="right",
        )

        # Optionally, add data labels to the plot for both datasets
        # for i, j in zip(x_data, y_data):
        ax.annotate(
            f"{y_data[-1]:.2f}",
            xy=(x_data[-1], y_data[-1]),
            xytext=(5, -15),
            textcoords="offset points",
            color="orange",
        )
        ax.annotate(
            f"{avg_change_data[-1]:.2f}",
            xy=(x_data[-1], avg_change_data[-1]),
            xytext=(5, 5),
            textcoords="offset points",
            color="purple",
        )

        self.canvas.draw()

    def plot_heatmap(self, data, xticklabels=None, yticklabels=None):
        """Plot the Q-table as a heatmap."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        sns.heatmap(
            data,
            ax=ax,
            cmap="viridis",
            annot=False,  # Set annot to False to remove cell labels
            xticklabels=xticklabels,
            yticklabels=yticklabels,
            cbar=True,
            cbar_kws={
                "label": "Q-value",
                "orientation": "vertical",
                "fraction": 0.10,
                "extend": "both",
                "format": "%.2f",
            },
            linewidths=0.5,
            linecolor="black",
            square=False,
            center=0.0,
            robust=True,
        )
        ax.set_title("Q-Table Heatmap")
        ax.set_xlabel("Actions (Teams)")
        ax.set_ylabel("States")

        # Optional: Improve readability of labels if they are too dense
        if xticklabels is not None:
            ax.set_xticklabels(xticklabels, rotation=45, horizontalalignment="right")  # Directly use provided labels
        if yticklabels is not None:
            ax.set_yticklabels(yticklabels, rotation=0, horizontalalignment="right")  # Directly use provided labels

        self.canvas.draw()

    def plot_exploration_exploitation_balance(self, num_exploration_counts, num_exploitation_counts, eps, start, end, decays):
        """Plot the exploration-exploitation balance over training episodes."""
        self.figure.clear()

        training_episodes = range(1, len(num_exploration_counts) + 1)
        total_actions_per_episode = [
            explore + exploit for explore, exploit in zip(num_exploration_counts, num_exploitation_counts)
        ]
        # Calculate ratios for each episode
        exploration_ratios = [
            explore / total if total > 0 else 0 for explore, total in zip(num_exploration_counts, total_actions_per_episode)
        ]
        exploitation_ratios = [
            exploit / total if total > 0 else 0
            for exploit, total in zip(num_exploitation_counts, total_actions_per_episode)
        ]
        ax = self.figure.add_subplot(111)
        ax.plot(
            training_episodes,
            exploration_ratios,
            "-o",
            label="Exploration Ratio",
            color="indigo",
        )
        ax.plot(
            training_episodes,
            exploitation_ratios,
            "-o",
            label="Exploitation Ratio",
            color="darkgoldenrod",
        )

        ax.set_title("Exploration-Exploitation Balance Over Episodes")
        ax.set_xlabel("Training Episode")
        ax.set_ylabel("Ratio of Actions (Exploration/Exploitation)")
        ax.set_ylim([-0.1, 1.1])  # Ensure the ratios are between 0 and 1
        ax.legend(loc="upper right")
        ax.grid(True)
        ax.set_xlim([1, eps])
        ax.set_yticks(np.arange(0, 1.0, 0.1))
        ax.set_xticks(np.arange(1, eps + 1, 1))
        ax.set_xticklabels(np.arange(1, eps + 1, 1), horizontalalignment="right")
        if eps > 10:
            ax.set_xticks(np.arange(1, eps + 1, 10))
            ax.set_xticklabels(np.arange(1, eps + 1, 10), horizontalalignment="right")

        ax.axhline(y=start, color="r", linestyle="dotted", label="Epsilon Start")
        ax.axhline(y=end, color="g", linestyle="dotted", label="Epsilon End")
        ax.axhline(y=0.5, color="b", linestyle="dotted", label="Epsilon 50%")
        ax.plot(
            training_episodes,
            decays[: list(training_episodes)[-1]],
            linestyle="dashdot",
            color="darkorange",
            label="Epsilon Decay",
        )
        ax.legend(loc="upper left")

        self.canvas.draw()

    def plot_schedule_scores(self, phase, eps, scores, percentages):
        """Plot the schedule scores for benchmark, training, and optimal phases."""
        self.figure.clear()

        ax = self.figure.add_subplot(111)
        ax.set_title("Average Scores")
        ax.set_xlabel("Phase")
        ax.set_ylabel("Average Score")

        # Calculate averages scores
        if phase == "benchmark":
            avg_benchmark_score = sum(scores["Benchmarks"]) / len(scores["Benchmarks"]) * 100
            avg_training_score = 0
            avg_optimal_score = 0
        if phase == "training":
            avg_benchmark_score = sum(scores["Benchmarks"]) / len(scores["Benchmarks"]) * 100
            avg_training_score = sum(scores["Training"]) / len(scores["Training"]) * 100
            avg_optimal_score = 0
        if phase == "optimal":
            avg_benchmark_score = sum(scores["Benchmarks"]) / len(scores["Benchmarks"]) * 100
            avg_training_score = sum(scores["Training"]) / len(scores["Training"]) * 100
            avg_optimal_score = scores["Optimal"][0] * 100

        # Create the bar chart
        phases = ["Benchmark", "Training", "Optimal"]
        scores = [avg_benchmark_score, avg_training_score, avg_optimal_score]

        # ax.bar(phases, scores)
        ax.set_ylim([0, 100])
        ax.set_yticks(np.arange(0, 105, 10))
        ax.set_xticks(np.arange(0, 3, 1))
        ax.set_xticklabels(phases, horizontalalignment="center")  # Rotate labels if needed

        for i, score in enumerate(scores):
            ax.text(i, score, f"{score:.2f}%", ha="center", va="baseline", color="black")

        ax.bar(phases, scores, color=["blue", "red", "green"])

        ax.grid(True, axis="y")
        self.canvas.draw()
'''
