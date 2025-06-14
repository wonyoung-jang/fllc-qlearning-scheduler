"""Module for plotting various statistics related to the FLLC scheduler."""

from dataclasses import dataclass, field

import numpy as np
import seaborn as sns
from matplotlib.axes import Axes
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGroupBox, QSplitter, QVBoxLayout, QWidget

from ..q_learning.q_learning import QLearning, QLearningMetrics
from ..utils.config import Training
from ..utils.stat_utils import average


@dataclass
class BasePlotWidget(QWidget):
    """Base class for plot widgets with common functionality."""

    q_learning: QLearning = None
    figure: Figure = None
    canvas: FigureCanvas = None
    _cached_episodes: int = field(default=None, init=False)
    _cached_step: int = field(default=None, init=False)

    def __post_init__(self) -> None:
        """Initialize the plot widget with a Matplotlib figure and canvas."""
        super().__init__()
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

    def set_q_learning(self, q_learning: QLearning) -> None:
        """Set the QLearning instance for the plot widget."""
        self.q_learning = q_learning
        self._cached_episodes = None
        self._cached_step = None

    def _prepare_ax(self) -> Axes:
        """Prepare the Axes for plotting by clearing the figure."""
        self.figure.clear()
        return self.figure.add_subplot(111)

    def _get_episodes_and_step(self) -> tuple[int, int]:
        """Get the number of episodes and step size for plotting."""
        if not self.q_learning:
            return 1, 1

        if self._cached_episodes is not None and self._cached_step is not None:
            return self._cached_episodes, self._cached_step

        eps = self.q_learning.config.episodes
        step = max(1, eps // 10)
        self._cached_episodes = eps
        self._cached_step = step
        return eps, step


@dataclass(slots=True)
class ScheduleScoresPlotWidget(BasePlotWidget):
    """Widget for plotting schedule scores across different phases."""

    def plot(self, phase: Training = None) -> None:
        """
        Plot the average scores for different phases of the schedule.

        Args:
            phase (Training): The phase of the schedule to plot ("benchmark", "training", "optimal").
        """
        if phase is None:
            phase = "Initialization"
        ax = self._prepare_ax()
        phases = ("Benchmark", "Training", "Optimal")
        colors = ("red", "green", "blue")
        scores = self._get_scores(phase)

        ax.set(
            title="Average Scores",
            ylabel="Average Score",
            xlabel="Phase",
            ylim=(0, 105),
            yticks=np.arange(0, 101, 10),
            xticks=range(len(phases)),
            xticklabels=phases,
        )
        bars = ax.bar(phases, scores, fc=colors, alpha=0.7, edgecolor="black")
        for _bar, score in zip(bars, scores):
            height = _bar.get_height()
            ax.text(
                _bar.get_x() + _bar.get_width() / 2.0,
                height + 1,
                f"{score:.1f}%",
                ha="center",
                va="bottom",
                fontweight="bold",
            )

        ax.grid(True, axis="y", alpha=0.5)
        self.canvas.draw()

    def _get_scores(self, phase: Training) -> tuple[float, float, float]:
        """
        Get the average scores for different phases of the schedule.

        Args:
            phase (Training): The phase of the schedule to get scores for ("benchmark", "training", "optimal").

        Returns:
            tuple[float, float, float]: Average scores for benchmark, training, and optimal phases.
        """
        scores = self.q_learning.metrics.scores
        benchmarks = scores.get("Benchmark", [])
        trainings = scores.get("Training", [])
        optimals = scores.get("Optimal", [])
        avg_benchmark_score = average(benchmarks) * 100
        avg_training_score = average(trainings) * 100 if phase != Training.BENCHMARK else 0
        avg_optimal_score = optimals[0] * 100 if phase == Training.OPTIMAL else 0
        return avg_benchmark_score, avg_training_score, avg_optimal_score


@dataclass(slots=True)
class HeatmapPlotWidget(BasePlotWidget):
    """Widget for plotting Q-table heatmap."""

    def plot(self) -> None:
        """Plot a heatmap of the Q-table data."""
        data, xticklabels, yticklabels = self.q_learning.state.to_heatmap()

        ax = self._prepare_ax()
        ax.set(
            title="Q-Table Heatmap",
            xlabel="Actions (Teams)",
            ylabel="States",
        )

        sns.heatmap(
            data,
            ax=ax,
            cmap="viridis",
            annot=False,
            xticklabels=xticklabels,
            yticklabels=yticklabels,
            cbar=True,
            cbar_kws={
                "label": "Q-value",
                "orientation": "vertical",
                "fraction": 0.10,
                "format": "%.2f",
            },
            linewidths=0.5,
            linecolor="black",
            square=False,
            center=0.0,
            robust=True,
            rasterized=True,
        )

        self.canvas.draw()


@dataclass(slots=True)
class ConvergencePlotWidget(BasePlotWidget):
    """Widget for plotting Q-value convergence over training episodes."""

    def plot(self, x_data: list = None) -> None:
        """Plot the convergence of Q-values over training episodes."""
        if x_data is None:
            x_data = []
        ax = self._prepare_ax()
        q = self.q_learning.metrics
        eps, step = self._get_episodes_and_step()

        min_limit, max_limit = ConvergencePlotWidget._get_ylim(q.q_value_changes, q.avg_reward_changes)
        yticks = np.arange(min_limit, max_limit, 5)
        xticks = np.arange(1, eps + 1, step)

        ax.set(
            title="Q-Value Changes Over Episodes",
            xlabel="Training Episode",
            ylabel="Q-Value Change (Rewards)",
            ylim=(min_limit, max_limit),
            xlim=(1, eps),
            xticks=xticks,
            yticks=yticks,
        )

        ConvergencePlotWidget._plot_convergence_data(ax, x_data, q)

        ax.legend(loc="best")
        ax.grid(True, alpha=0.5)
        self.canvas.draw()

    @staticmethod
    def _get_ylim(value_changes: list, avg_changes: list) -> tuple[float, float]:
        """Get the y-limits for the plot based on value changes and average changes."""
        min_y = min(value_changes) if value_changes else 0
        max_y = max(value_changes) if value_changes else 0
        min_avg = min(avg_changes) if avg_changes else min_y
        max_avg = max(avg_changes) if avg_changes else max_y
        return min(min_y, min_avg) - 1, max(max_y, max_avg) + 1

    @staticmethod
    def _plot_convergence_data(ax: Axes, x_data: list, q: QLearningMetrics) -> None:
        """
        Plot the convergence data on the given Axes.

        Args:
            ax (Axes): The Axes object to plot on.
            x_data (list): The x-axis data for the plot.
            q (QLearningMetrics): The QLearningMetrics instance containing the data to plot.
        """
        if q.q_value_changes:
            ax.plot(x_data, q.q_value_changes, "-o", label="Q-Value Change", c="orange")
            ax.annotate(
                text=f"{q.q_value_changes[-1]:.2f}",
                xy=(x_data[-1], q.q_value_changes[-1]),
                xytext=(5, -15),
                textcoords="offset points",
                c="orange",
            )

        if q.avg_reward_changes:
            ax.plot(x_data, q.avg_reward_changes, "-^", label="Average Q-Value Change", c="purple")
            ax.annotate(
                text=f"{q.avg_reward_changes[-1]:.2f}",
                xy=(x_data[-1], q.avg_reward_changes[-1]),
                xytext=(5, 5),
                textcoords="offset points",
                c="purple",
            )


@dataclass(slots=True)
class ExplorationExploitationPlotWidget(BasePlotWidget):
    """Widget for plotting exploration vs exploitation balance."""

    def plot(self, decays: list = None) -> None:
        """Plot the exploration-exploitation balance over training episodes."""
        if decays is None:
            decays = []
        exploration_counts = self.q_learning.strategy.exploration_counts
        exploitation_counts = self.q_learning.strategy.exploitation_counts
        eps, step = self._get_episodes_and_step()
        q_param = self.q_learning.param

        ax = self._prepare_ax()
        ExplorationExploitationPlotWidget._setup_plot_axes(ax, eps, step)

        episodes = np.arange(1, len(exploration_counts) + 1)
        total_actions = np.array(exploration_counts) + np.array(exploitation_counts)

        exploration_ratios = np.divide(
            exploration_counts,
            total_actions,
            out=np.zeros_like(exploration_counts, dtype=float),
            where=total_actions != 0,
        )
        exploitation_ratios = np.divide(
            exploitation_counts,
            total_actions,
            out=np.zeros_like(exploitation_counts, dtype=float),
            where=total_actions != 0,
        )

        ExplorationExploitationPlotWidget._setup_reference_lines(ax, q_param.epsilon_start, q_param.epsilon_end)
        ExplorationExploitationPlotWidget._plot_exploration_data(
            ax, episodes, exploration_ratios, exploitation_ratios, decays
        )

        ax.grid(True, alpha=0.5)
        ax.legend(loc="best")
        self.canvas.draw()

    @staticmethod
    def _setup_plot_axes(ax: Axes, eps: int, step: int) -> None:
        """Setup exploration plot axes."""
        yticks = np.arange(0, 1.1, 0.1)
        xticks = np.arange(1, eps + 1, step)

        ax.set(
            title="Exploration vs. Exploitation Ratios Over Episodes",
            xlabel="Training Episode",
            ylabel="Ratio of Explore/Exploit Actions",
            ylim=(-0.05, 1.05),
            yticks=yticks,
            xlim=(1, eps),
            xticks=xticks,
        )

    @staticmethod
    def _setup_reference_lines(ax: Axes, start: int, end: int) -> None:
        """
        Setup reference lines for exploration and exploitation ratios.

        Args:
            ax (Axes): The Axes object to plot on.
            start (int): The starting epsilon value.
            end (int): The ending epsilon value.
        """
        ax.axhline(y=start, ls=":", label="Epsilon Start", c="r", alpha=0.6)
        ax.axhline(y=end, ls=":", label="Epsilon End", c="g", alpha=0.6)
        ax.axhline(y=0.5, ls=":", label="Epsilon 50%", c="b", alpha=0.6)

    @staticmethod
    def _plot_exploration_data(
        ax: Axes,
        episodes: np.ndarray,
        exploration_ratios: np.ndarray,
        exploitation_ratios: np.ndarray,
        decays: list,
    ) -> None:
        """
        Plot the exploration and exploitation data on the given Axes.

        Args:
            ax (Axes): The Axes object to plot on.
            episodes (np.ndarray): The x-axis data for the plot.
            exploration_ratios (np.ndarray): The exploration ratios to plot.
            exploitation_ratios (np.ndarray): The exploitation ratios to plot.
            decays (list): The epsilon decay values to plot.
        """
        decay_data = decays[: len(episodes)]
        ax.plot(episodes, exploration_ratios, "-o", label="Exploration Ratio", c="indigo")
        ax.plot(episodes, exploitation_ratios, "-o", label="Exploitation Ratio", c="darkgoldenrod")
        ax.plot(episodes, decay_data, "--", label="Epsilon Decay", c="darkorange", alpha=0.8)


@dataclass(slots=True)
class MplWidgets(QGroupBox):
    """Class for embedding Matplotlib figures in a PyQt widget."""

    q_learning: QLearning = None
    schedule_scores: ScheduleScoresPlotWidget = None
    convergence: ConvergencePlotWidget = None
    heatmap: HeatmapPlotWidget = None
    explore_exploit: ExplorationExploitationPlotWidget = None

    def __post_init__(self) -> None:
        """Initialize the MplWidgets with Matplotlib figures and a layout."""
        super(MplWidgets, self).__init__()
        self.schedule_scores = ScheduleScoresPlotWidget()
        self.convergence = ConvergencePlotWidget()
        self.heatmap = HeatmapPlotWidget()
        self.explore_exploit = ExplorationExploitationPlotWidget()
        self.setTitle("Visualizations")
        self.initialize_layout()

    def set_q_learning(self, q_learning: QLearning) -> None:
        """
        Set the QLearning instance for the MplWidgets.

        Args:
            q_learning (QLearning): The QLearning instance to set.
        """
        for w in (self.convergence, self.heatmap, self.explore_exploit, self.schedule_scores):
            w.set_q_learning(q_learning)

    def initialize_layout(self) -> None:
        """Initialize the layout for the MplWidgets."""
        splitter = QSplitter(Qt.Orientation.Vertical)
        for w in (self.convergence, self.heatmap, self.explore_exploit, self.schedule_scores):
            splitter.addWidget(w)
        layout = QVBoxLayout()
        layout.addWidget(splitter)
        self.setLayout(layout)
