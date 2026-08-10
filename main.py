# RESONANCE - entry point
# Run: python main.py

import sys
import os

# make the package importable when run as a plain script
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.app import App


def main():
    app = App()
    app.run()


if __name__ == "__main__":
    main()
