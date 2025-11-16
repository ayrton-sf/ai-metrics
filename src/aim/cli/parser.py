import argparse

class CLIArgumentParser:
    @staticmethod
    def parse_arguments():
        parser = argparse.ArgumentParser(description="AI Testing tools")

        parser.add_argument(
            "--set-reference",
            type=str,
            help="Sets reference data for semantic comparison given a file",
        )
        parser.add_argument(
            "--set-baseline",
            type=str,
            help="Sets a base threshold for each instance of semantic comparison",
        ),
        subparsers = parser.add_subparsers(dest="command")
        benchmark_parser = subparsers.add_parser(
            "run-benchmark",
            help="Run a benchmark with a given model and metric",
        )
        benchmark_parser.add_argument(
            "model",
            type=str,
            help="LLM Model",
        )
        benchmark_parser.add_argument(
            "metric",
            type=str,
            choices=["general_criteria","claim_check"],
            help="Benchmark type",
        )
        benchmark_parser.add_argument(
            "datafile",
            nargs="?",
            type=str,
            help="Optional custom data file (defaults to internal benchmark data)",
        )

        return parser.parse_args()