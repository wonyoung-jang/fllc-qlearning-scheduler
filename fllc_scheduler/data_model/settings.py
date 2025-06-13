"""Settings for the FLLC Scheduler."""

from ..utils.config import Constraint, QParam, RoundType, Configuration, Time

SETTINGS = {
    Configuration.NUM_TEAMS: 42,
    Configuration.NUM_ROUNDS: 7,
    Configuration.NUM_TABLES: 4,
    Configuration.ROUND_TYPES: {
        RoundType.JUDGING: 1,
        RoundType.PRACTICE: 2,
        RoundType.TABLE: 3,
    },
    Time.JUDGING_START: "08:00",
    Time.PRACTICE_START: "09:00",
    Time.PRACTICE_STOP: "12:00",
    Time.TABLE_START: "13:30",
    Time.TABLE_STOP: "16:21",
    QParam.ALPHA: 0.20,
    QParam.GAMMA: 0.80,
    QParam.EPSILON_START: 1.00,
    QParam.EPSILON_END: 0.01,
    QParam.EPSILON_DECAY: 0.995,
    QParam.EPISODES: 5,
    Constraint.TABLE_CONSISTENCY: 1.0,
    Constraint.OPP_VARIETY: 1.0,
    Constraint.BTB_PENALTY: 1.0,
    Constraint.BREAK_TIME: 1.0,
}
