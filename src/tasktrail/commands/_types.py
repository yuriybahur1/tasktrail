import argparse
from typing import Any, Protocol


class Subparsers(Protocol):
    def add_parser(self, name: str, **kwargs: Any) -> argparse.ArgumentParser: ...
