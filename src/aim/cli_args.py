import argparse


def build_parser():
    parser = argparse.ArgumentParser(prog="aim")

    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("test")
    p.add_argument("-c", "--config", required=True)

    p = sub.add_parser("set-reference")
    p.add_argument("-c", "--config", required=True)

    p = sub.add_parser("set-baseline")
    p.add_argument("-c", "--config", required=True)
    p.add_argument("-r", "--runs", type=int, required=True)

    p = sub.add_parser("report")
    p.add_argument("-c", "--config", required=True)

    return parser
