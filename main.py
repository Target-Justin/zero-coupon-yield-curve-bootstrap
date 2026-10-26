import argparse as ap

from scripts.bonds.pipeline import run_bonds
from scripts.ois.pipeline import run_ois

def main():
    """Run the bootstrap pipelines selected on the command line.

    Usage: python main.py [bonds|ois|all]. Without argument, all the pipelines are run.
    The OIS step is skipped if its raw data are missing (the Bloomberg data are not published).
    """

    parser = ap.ArgumentParser(description = "Run a bootstrap pipeline")
    parser.add_argument("target", choices = ["bonds","ois","all"], nargs = "?", default = "all")
    args = parser.parse_args()

    if args.target == "bonds":
        run_bonds()
    elif args.target == "ois":
        try:
            run_ois()
        except FileNotFoundError as error:
            print(f"OIS pipeline skipped: {error}")
    elif args.target == "all":
        run_bonds()
        try:
            run_ois()
        except FileNotFoundError as error:
                print(f"OIS pipeline skipped: {error}")

if __name__ == "__main__":
    main()