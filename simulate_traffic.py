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


def run():
    step = 0
    print(traci.vehicle.getIDList())

    traci.close()
    sys.stdout.flush()


def main():
    options = get_options()

    if options.nogui:
        sumoBinary = checkBinary("sumo")
    else:
        sumoBinary = checkBinary("sumo-gui")

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


if __name__ == "__main__":
    main()
