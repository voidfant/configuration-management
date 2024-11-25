import argparse
import sys
from src.cli_handler import CLIHandler

def parse_args():
    parser = argparse.ArgumentParser(description="XML to config file CLI tool.")
    parser.add_argument(
        "--output-file", default='output.conf', help="Path to output file."
    )
    return parser.parse_args()


def main():
    args = parse_args()

    input_data = sys.stdin.read()

    cli_handler = CLIHandler()
    cli_handler.process(input_data, args.output_file)


if __name__ == "__main__":
    main()
