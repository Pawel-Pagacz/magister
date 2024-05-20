from collections import namedtuple
import traci
import sumolib

Phase = namedtuple("Phase", ["duration", "state", "minDur", "maxDur"])
Logic = namedtuple(
    "Logic", ["programID", "type", "currentPhaseIndex", "phases", "subParameter"]
)

# Dane wejściowe
traffic_light_logistic = [
    (
        "419734825",
        Logic(
            programID="0",
            type=3,
            currentPhaseIndex=0,
            phases=(
                Phase(duration=25.0, state="GGrrrrrr", minDur=5.0, maxDur=500.0),
                Phase(duration=3.0, state="yyrrrrrr", minDur=3.0, maxDur=3.0),
                Phase(duration=25.0, state="rrrrrrGG", minDur=5.0, maxDur=500.0),
                Phase(duration=3.0, state="rrrrrryy", minDur=3.0, maxDur=3.0),
                Phase(duration=25.0, state="rrrGGrrr", minDur=5.0, maxDur=500.0),
                Phase(duration=3.0, state="rrryyrrr", minDur=3.0, maxDur=3.0),
            ),
            subParameter={"show-detectors": "true"},
        ),
    ),
    (
        "cluster_2556814094_429774589",
        Logic(
            programID="0",
            type=3,
            currentPhaseIndex=0,
            phases=(
                Phase(duration=41.0, state="GGgrrrGGgrrr", minDur=5.0, maxDur=500.0),
                Phase(duration=3.0, state="yyyrrryyyrrr", minDur=3.0, maxDur=3.0),
                Phase(duration=41.0, state="rrrGGgrrrGGg", minDur=5.0, maxDur=500.0),
                Phase(duration=3.0, state="rrryyyrrryyy", minDur=3.0, maxDur=3.0),
            ),
            subParameter={"show-detectors": "true"},
        ),
    ),
    (
        "cluster_259602058_2924318333",
        Logic(
            programID="0",
            type=3,
            currentPhaseIndex=0,
            phases=(
                Phase(duration=20.0, state="rrrGGGrrrrrr", minDur=5.0, maxDur=500.0),
                Phase(duration=5.0, state="rrryyyrrrrrr", minDur=5.0, maxDur=5.0),
                Phase(duration=15.0, state="GGGrrrrrrrrr", minDur=5.0, maxDur=500.0),
                Phase(duration=5.0, state="yyyrrrrrrrrr", minDur=5.0, maxDur=5.0),
                Phase(duration=20.0, state="grrrrrrrrGGG", minDur=5.0, maxDur=500.0),
                Phase(duration=5.0, state="rrrrrrrrrryy", minDur=5.0, maxDur=5.0),
                Phase(duration=20.0, state="rrrrrrGGGrrr", minDur=5.0, maxDur=500.0),
                Phase(duration=5.0, state="rrrrrryyyrrr", minDur=5.0, maxDur=5.0),
            ),
            subParameter={"show-detectors": "true"},
        ),
    ),
    (
        "429723386",
        Logic(
            programID="0",
            type=3,
            currentPhaseIndex=0,
            phases=(
                Phase(duration=30.0, state="GrrrrrGGr", minDur=5.0, maxDur=500.0),
                Phase(duration=3.0, state="yrrrrryyr", minDur=3.0, maxDur=3.0),
                Phase(duration=10.0, state="GGrrrrrrr", minDur=5.0, maxDur=500.0),
                Phase(duration=3.0, state="yyrrrrrrr", minDur=3.0, maxDur=3.0),
                Phase(duration=20.0, state="rrrGGrrrr", minDur=5.0, maxDur=500.0),
                Phase(duration=3.0, state="rrryyrrrr", minDur=3.0, maxDur=3.0),
            ),
            subParameter={"show-detectors": "true"},
        ),
    ),
]


def filter_phases():
    filtered_genotype = []
    for tl_id, logic in traffic_light_logistic:
        filtered_phases = [
            phase for phase in logic.phases if "G" in phase.state or "g" in phase.state
        ]
        if filtered_phases:
            filtered_genotype.append(
                (
                    tl_id,
                    Logic(
                        programID=logic.programID,
                        type=logic.type,
                        currentPhaseIndex=logic.currentPhaseIndex,
                        phases=tuple(filtered_phases),
                        subParameter=logic.subParameter,
                    ),
                )
            )

    for tl_id, logic in filtered_genotype:
        print(f"Traffic Light ID: {tl_id}")
        for phase in logic.phases:
            print(
                f"  Phase: duration={phase.duration}, state={phase.state}, minDur={phase.minDur}, maxDur={phase.maxDur}"
            )
