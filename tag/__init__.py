#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (C) 2015 Daniel Standage <daniel.standage@gmail.com>
#
# This file is part of tag (http://github.com/standage/tag) and is licensed
# under the BSD 3-clause license: see LICENSE.
# -----------------------------------------------------------------------------
"""Package-wide configuration"""

try:
    import __builtin__ as builtins
except:  # pragma: no cover
    import builtins
from tag.comment import Comment
from tag.directive import Directive
from tag.feature import Feature
from tag.sequence import Sequence
from tag.range import Range
from tag.reader import GFF3Reader
from tag.writer import GFF3Writer
from tag.score import Score
from tag import cli
from tag import index
from tag import select
from tag import transcript
from gzip import open as gzopen

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


def open(filename, mode):
    if mode not in ['r', 'w']:
        raise ValueError('invalid mode "{}"'.format(mode))
    openfunc = builtins.open
    if filename.endswith('.gz'):
        openfunc = gzopen
        mode += 't'
    return openfunc(filename, mode)


def pkgdata(filename, mode='r'):
    fullpath = '{dir}/{fn}'.format(dir='tests/testdata/', fn=filename)
    return open(fullpath, mode)


def demo_feature():
    gene = feature.Feature(
        'contig1\tsnap\tgene\t1000\t7500\t.\t+\t.\tID=gene1'
    )
    mrna = feature.Feature(
        'contig1\tsnap\tmRNA\t1000\t7500\t.\t+\t.\tID=mrna1;Parent=gene1'
    )
    exon1 = feature.Feature(
        'contig1\tsnap\texon\t1000\t3700\t.\t+\t.\tParent=mrna1'
    )
    exon2 = feature.Feature(
        'contig1\tsnap\texon\t7250\t7500\t.\t+\t.\tParent=mrna1'
    )
    cds1 = feature.Feature(
        'contig1\tsnap\tCDS\t1289\t3700\t.\t+\t0\tID=cds1;Parent=mrna1'
    )
    cds2 = feature.Feature(
        'contig1\tsnap\tCDS\t7250\t7352\t.\t+\t0\tID=cds1;Parent=mrna1'
    )
    cds1.add_sibling(cds2)
    for f in [exon1, exon2, cds1, cds2]:
        mrna.add_child(f)
    gene.add_child(mrna)
    return gene
