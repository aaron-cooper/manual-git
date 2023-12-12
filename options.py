import argparse

class CommitArgs:
    def __init__(self):
        self.message = ""

def from_argv() -> CommitArgs:
    return __create_parser().parse_args()

def from_list(args: list[str]) -> CommitArgs:
    return __create_parser().parse_args(args)

def __create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest="command", required=True)

    commit_parser = subparsers.add_parser("commit", help="create a commit reflecting the state of the repo.")
    commit_parser.add_argument("message", default=None, help="Your commit message.")
    return parser