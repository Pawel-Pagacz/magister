#!/usr/bin/env python

from sumolib import checkBinary  # Checks for the binary in environ vars
import traci
import os
import sys
import optparse

if "SUMO_HOME" in os.environ:
    tools = os.path.join(os.environ["SUMO_HOME"], "tools")
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


def get_options():
    opt_parser = optparse.OptionParser()
    opt_parser.add_option(
        "--nogui",
        action="store_true",
        default=False,
        help="run the commandline version of sumo",
    )
    options, args = opt_parser.parse_args()
    return options


# contains TraCI control loop
def run():
    step = 0
    print(traci.vehicle.getIDList())

    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        # print(step)

        if step == 30:
            traci.trafficlight.setRedYellowGreenState("J1", "GrGGrrrrGGGgrrrr")

        step += 1

    traci.close()
    sys.stdout.flush()


if __name__ == "__main__":
    options = get_options()

    # check binary
    if options.nogui:
        sumoBinary = checkBinary("sumo")
    else:
        sumoBinary = checkBinary("sumo-gui")

    # traci starts sumo as a subprocess and then this script connects and runs
    traci.start(
        [
            sumoBinary,
            "-c",
            "networks/single_intersection/test_light.sumocfg",
            "--tripinfo-output",
            "tripinfo.xml",
        ]
    )
    run()
