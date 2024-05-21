import os, sys, time

from src.argparse import parse_args
from src.distributeprocesess import DistributeProcesses


def main():
    args = parse_args()
    net_path = args.net_path
    distprocs = DistributeProcesses(args, args.algorithm)
    distprocs.run()


if __name__ == "__main__":
    main()
