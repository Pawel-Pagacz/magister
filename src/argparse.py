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

    parser.add_argument(
        "-simulation",
        type=str,
        default="wielun",
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
        "-steps",
        type=int,
        default=50400,
        dest="steps",
        help="length of simulation in seconds/steps",
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
        "-mutation_rate",
        type=int,
        default=0.1,
        dest="mutation_rate",
        help="set mutation rate for genetic algorithm, default: 0.3",
    )
    parser.add_argument(
        "-crossover_rate",
        type=int,
        default=0.8,
        dest="crossover_rate",
        help="set crossover rate for genetic algorithm, default: 0.8",
    )

    parser.add_argument(
        "-pop_size",
        type=int,
        default=10,
        dest="pop_size",
        help="set population size for genetic algorithm, default: 10",
    )

    parser.add_argument(
        "-cont",
        type=int,
        default="0",
        dest="cont",
        help="continue algorithm, from previous run, default: 0",
    )
    return parser.parse_args()
