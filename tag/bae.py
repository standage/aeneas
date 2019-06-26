#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (C) 2019 Battelle National Biodefense Institute.
#
# This file is part of tag (http://github.com/standage/tag) and is licensed
# under the BSD 3-clause license: see LICENSE.
# -----------------------------------------------------------------------------

from __future__ import division
from collections import defaultdict
import tag


def eval_locus(features):
    """Evaluate congruence between gene predictions from different sources.

    Gene predictions are assumed to be microbial protein-coding genes, marked
    as type `CDS`. Any reference protein alignments can be included as features
    of type `translated_nucleotide_match`. Compute the agreement between
    different sources of start/stop codon position, entire ORF position, and
    coverage from reference proteins.
    """
    starts = defaultdict(int)
    ends = defaultdict(int)
    intervals = defaultdict(int)
    coverage = defaultdict(int)

    numorfs = len(list(tag.select.features(features, type='CDS')))

    for feature in features:
        starts[feature.start] += 1
        ends[feature.end] += 1
        intervals[feature.range] += 1

    aligns = tag.select.features(features, type='translated_nucleotide_match')
    ranges = [a.range for a in aligns]
    for block in tag.Range.merge_overlapping(ranges):
        for feature in tag.select.features(features, type='CDS'):
            bpoverlap = feature.range.overlap_extent(block)
            coverage[feature] += bpoverlap

    for feature in tag.select.features(features, type='CDS'):
        start_confirmed = starts[feature.start] - 1
        start_shared = starts[feature.start] / sum(starts.values())
        end_confirmed = ends[feature.end] - 1
        end_shared = ends[feature.end] / sum(ends.values())
        interval_confirmed = intervals[feature.range] - 1
        interval_shared = intervals[feature.range] / sum(intervals.values())
        prot_coverage = coverage[feature] / len(feature)
        feature.add_attribute('start_confirmed', start_confirmed)
        feature.add_attribute('start_shared', start_shared)
        feature.add_attribute('end_confirmed', end_confirmed)
        feature.add_attribute('end_shared', end_shared)
        feature.add_attribute('orf_confirmed', interval_confirmed)
        feature.add_attribute('orf_shared', interval_shared)
        feature.add_attribute('locus_orfs', numorfs)
        feature.add_attribute('protein_coverage', prot_coverage)


def eval_stream(locusstream):
    """Feature stream for bacterial annotation evaluation."""
    for seqid, interval, locus in locusstream:
        eval_locus(locus)
        for feature in locus:
            yield feature
        yield tag.Directive('###')
