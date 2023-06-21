"""Console script for pix2vec."""
import argparse
import sys
from .pix2vec import Cube, GndPixels
import os

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

    #print("Arguments: " + str(args._))
    print("pix2vect - 2023 Alessandro Frigeri - Istituto Nazionale di Astrofisica")
    #return 0

    if args.cube:
        file_exists = os.path.exists(args.cube)
        if file_exists:
            c = Cube(args.cube)
        else:
            print("Cube %s does not exists\nexiting...."%(args.cube))
            sys.exit(0)

    if args.info and (c is not None):
        sys.stderr.write("Cube Type:%s samples:%d lines:%s file:%s\n"%(c.id,c.samples,c.lines,c.fname))
        sys.exit(0)

    if args.lines:
        lr = args.lines.split(',')
        l0 = int(lr[0])
        l1 = int(lr[1])
        if (l1 > c.lines) or (l0 > c.lines):
            print("maximum lines (%d) exceeded"%(c.lines))
            sys.exit(0)
    else:
        l0, l1 = 1, c.lines

    if args.samples:
        sr = args.samples.split(',')
        s0 = int(sr[0])
        s1 = int(sr[1])
        if (s1 > c.samples) or (s0 > c.samples):
            print("maximum sample (%d) exceeded"%(c.samples))
            sys.exit(0)
    else:
        s0, s1 = 1, c.samples

    if args.output:
        p = GndPixels(c,args.output,s0,s1,l0,l1)
        sys.exit(0)  # pragma: no cover

if __name__ == "__main__":
    main()
