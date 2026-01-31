from dataclasses import dataclass


@dataclass
class Config:
    be_verbose: bool = False


config = Config()
