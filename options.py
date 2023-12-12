import argparse
import os

class CommitArgs:
    def __init__(self):
        self.message = ""

def from_argv() -> CommitArgs:
    return __create_parser().parse_args()

def from_list(args: list[str]) -> CommitArgs:
    return __create_parser().parse_args(args)

def __create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument("--root", "-r", default=os.getcwd(), help="The root directory of the repository (not the .git folder), defaults to working directory.")

    subparsers = parser.add_subparsers(dest="command", required=True)

    commit_parser = subparsers.add_parser("commit", help="create a commit reflecting the state of the repo.")
    commit_parser.add_argument("message", default=None, help="Your commit message.")

    config_parser = subparsers.add_parser("config", help="Add or set a configuration option in local configuration file.")
    config_parser.add_argument("section", help="Section that variable should fall under.")
    config_parser.add_argument("variable", help="The name of the variable to be set.")
    config_parser.add_argument("value", help="The value of the variable to be set.")
    return parser