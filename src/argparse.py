import argparse
import os


def parse_args():
    parser = argparse.ArgumentParser()

    # multi processing parameters
    parser.add_argument(
        "-n",
        type=int,
        default=os.cpu_count() - 1,
        dest="n",
        help="number of sim procs (parallel simulations) generating experiences, default: os.cpu_count()-1",
    )
    # sumo parameters
    parser.add_argument(
        "-port",
        type=int,
        default=9000,
        dest="port",
        help="port to connect self.conn.server, default: 9000",
    )
    parser.add_argument(
        "-simulation",
        type=str,
        default=None,
        dest="simulation",
        help="simulation scenario, default: wielun, options:wroclaw, wielun",
    )
    parser.add_argument(
        "-netpath",
        type=str,
        default="networks/wielun/wielun.net.xml",
        dest="net_path",
        help="path to desired simulation network file, default: networks/wielun/wielun.net.xml",
    )
    parser.add_argument(
        "-sumocfg",
        type=str,
        default="networks/wielun/wielun.sumocfg",
        dest="cfg_path",
        help="path to desired simulation configuration file, default: networks/wielun/wielun.sumocfg",
    )
    parser.add_argument(
        "-algorithm",
        type=str,
        default="GA",
        dest="algorithm",
        help="genetic algorithm, default:GA",
    )
    parser.add_argument(
        "-nogui",
        default=False,
        action="store_true",
        dest="nogui",
        help="disable gui, default: False",
    )

    parser.add_argument(
        "-scale",
        type=float,
        default=1.0,
        dest="scale",
        help="vehicle generation scale parameter, higher values generates more vehicles, default: 1.0",
    )  # Nie wiem czy zadziała

    parser.add_argument(
        "-offset",
        type=float,
        default=0.25,
        dest="offset",
        help="max sim offset fraction of total sim length, default: 0.3",
    )

    # shared tsc params
    parser.add_argument(
        "-gmin",
        type=int,
        default=5,
        dest="g_min",
        help="minimum green phase time (s), default: 5",
    )
    parser.add_argument(
        "-y",
        type=int,
        default=2,
        dest="y",
        help="yellow change phase time (s), default: 2",
    )
    parser.add_argument(
        "-r",
        type=int,
        default=3,
        dest="r",
        help="all red stop phase time (s), default: 3",
    )

    # genetic algorithm parameters
    parser.add_argument(
        "-nreplay",
        type=int,
        default=100,
        dest="nreplay",
        help="maximum size of experience replay, default: 100",
    )
    parser.add_argument(
        "-steps",
        type=int,
        default=86400,
        dest="steps",
        help="length of simulation in seconds/steps",
    )
    return parser.parse_args()
