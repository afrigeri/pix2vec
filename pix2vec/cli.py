"""Console script for pix2vec."""
import argparse
import sys
#import pix2vec

def main():
    """Console script for pix2vec."""
    parser = argparse.ArgumentParser()
    parser.add_argument('_', nargs='*')
    parser.add_argument('-c','--cube')          
    parser.add_argument('-o','--output')     
    parser.add_argument('-l', '--lines')     
    parser.add_argument('-s', '--samples')  
    parser.add_argument('-d', '--debug')  	
    parser.add_argument('-i', '--info', action='store_true', dest='info')  
    args = parser.parse_args()

    print("Arguments: " + str(args._))
    print("Replace this message by putting your code into "
          "pix2vec.cli.main")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
