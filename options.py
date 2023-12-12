import argparse

class CommitArgs:
    def __init__(self):
        self.message = ""

def from_argv() -> CommitArgs:
    return __parser().parse_args()

def from_list(args: list[str]) -> CommitArgs:
    return __parser().parse_args(args)

def __parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('message', default=None, help="Your commit message.")
    return parser