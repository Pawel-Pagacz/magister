import os, sys, time

from src.argparse import parse_args
from src.network import Network


def main():
    args = parse_args()
    net_path = args.net_path
    network = Network(net_path)
    print(network.get_net_data())


if __name__ == "__main__":
    main()
