#!/usr/bin/env python3
import pathlib

import common

scripts_dir = pathlib.Path(__file__).parent.absolute()


def main():
  common.configure_logging()
  common.stop_dev_server()


if __name__ == '__main__':
  main()