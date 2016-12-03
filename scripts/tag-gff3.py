#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (C) 2015 Daniel Standage <daniel.standage@gmail.com>
#
# This file is part of tag (http://github.com/standage/tag) and is licensed
# under the BSD 3-clause license: see LICENSE.
# -----------------------------------------------------------------------------

from __future__ import print_function
import argparse
import tag

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--out', metavar='FILE', default='/dev/stdout',
                    help='write output to the specified file; default is '
                    'terminal (stdout))')
parser.add_argument('gff3', help='input file in GFF3 format')
args = parser.parse_args()

infile = tag.open(args.gff3, 'r')
outfile = tag.open(args.out, 'w')

reader = tag.reader.GFF3Reader(infile)
for feature in reader:
    print(repr(feature), file=outfile)