#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (C) 2015 Daniel Standage <daniel.standage@gmail.com>
#
# This file is part of aeneas (http://github.com/standage/aeneas) and is
# licensed under the BSD 3-clause license: see LICENSE.txt.
# -----------------------------------------------------------------------------
import pytest
import re
from .range import Range


dirtypes = ['gff-version', 'sequence-region', 'feature-ontology', 'species',
            'attribute-ontology', 'source-ontology', 'genome-build']


class Directive():
    """
    Represents a directive from a GFF3 file.

    This class is primarily for error checking and data access. Once created,
    `Directive` objects should be treated as read-only: modify at your peril!
    Also, separator directives (`###`) and the `##FASTA` directive are handled
    directly by parsers and not by this class.
    """

    def __init__(self, data):
        assert data.startswith('##')
        self._rawdata = data

        formatmatch = re.match('##gff-version\s+(\d+)', data)
        if formatmatch:
            self.dirtype = 'gff-version'
            self.version = formatmatch.group(1)
            assert self.version == '3', 'Only GFF version 3 is supported'
            return

        formatmatch = re.match('##sequence-region\s+(\S+) (\d+) (\d+)', data)
        if formatmatch:
            self.dirtype = 'sequence-region'
            self.seqid = formatmatch.group(1)
            self.region = Range(int(formatmatch.group(2)) - 1,
                                int(formatmatch.group(3)))
            return

        formatmatch = re.match('##((feature|attribute|source)-ontology)'
                               '\s+(\S+)', data)
        if formatmatch:
            self.dirtype = formatmatch.group(1)
            self.uri = formatmatch.group(3)
            return

        formatmatch = re.match('##species\s+(\S+)', data)
        if formatmatch:
            self.dirtype = 'species'
            self.uri = formatmatch.group(1)
            return

        formatmatch = re.match('##genome-build\s+(\S+)\s+(\S+)', data)
        if formatmatch:
            self.dirtype = 'genome-build'
            self.source = formatmatch.group(1)
            self.build_name = formatmatch.group(2)
            return

        formatmatch = re.match('##(\S+)(\s+(.+))*', data)
        assert formatmatch
        self.dirtype = formatmatch.group(1)
        self.data = formatmatch.group(3)

        assert self.dirtype is not None

    @property
    def type(self):
        """
        Directives not following one of the explicitly described formats in the
        GFF3 spec are application specific and not supported.
        """
        if self.dirtype in dirtypes:
            return self.dirtype
        return None

    def __repr__(self):
        return self._rawdata

    def __lt__(self, other):
        if self.type == 'gff-version':
            return True

        if self.type == 'sequence-region':
            if isinstance(other, Directive):
                if other.type == 'gff-version':
                    return False
                elif other.type == 'sequence-region':
                    if self.seqid == other.seqid:
                        return self.region.__lt__(other.region)
                    else:
                        return self.seqid < other.seqid
                else:
                    return True
            else:
                return True

        if isinstance(other, Directive):
            return self._rawdata < other._rawdata
        else:
            return True

    def __le__(self, other):
        if self.type == 'gff-version':
            return True

        if self.type == 'sequence-region':
            if isinstance(other, Directive):
                if other.type == 'gff-version':
                    return False
                elif other.type == 'sequence-region':
                    if self.seqid == other.seqid:
                        return self.region.__le__(other.region)
                    else:
                        return self.seqid <= other.seqid
                else:
                    return True
            else:
                return True

        if isinstance(other, Directive):
            return self._rawdata <= other._rawdata
        else:
            return True

    def __gt__(self, other):
        return not self.__le__(other)

    def __ge__(self, other):
        return not self.__lt__(other)


# -----------------------------------------------------------------------------
# Unit tests
# -----------------------------------------------------------------------------

def test_basic():
    """Test basic object construction."""
    d = Directive('##gff-version 3')
    assert d.type == 'gff-version' and d.version == '3'
    d = Directive('##gff-version    3')  # 3 spaces
    assert d.type == 'gff-version' and d.version == '3'
    d = Directive('##gff-version	3')  # tab
    assert d.type == 'gff-version' and d.version == '3'
    assert '%r' % d == '##gff-version	3'

    with pytest.raises(AssertionError):
        d = Directive('')  # No data

    with pytest.raises(AssertionError) as ae:
        d = Directive('##gff-version   2.2')
    assert 'Only GFF version 3 is supported' in str(ae)

    with pytest.raises(AssertionError):
        d = Directive('not a directive')

    with pytest.raises(AssertionError):
        d = Directive('# Still not a directive')


def test_custom_directive():
    """Test custom directive type."""
    d1 = Directive('##bogus-directive')
    d2 = Directive('##bonus-directive   abc 1 2 3')
    d3 = Directive('##Type DNA NC_005213.1')

    assert d1.type is None and d1.dirtype == 'bogus-directive'
    assert d1.data is None
    assert d2.type is None and d2.dirtype == 'bonus-directive'
    assert d2.data == 'abc 1 2 3'
    assert d3.type is None and d3.dirtype == 'Type'
    assert d3.data == 'DNA NC_005213.1'


def test_sequence_region():
    """Test sequence-region directive type."""
    r1 = Directive('##sequence-region ctg123 1 1497228')
    r2 = Directive('##sequence-region   ctg123 1 1497228')  # 3 spaces
    r3 = Directive('##sequence-region	ctg123 1 1497228')  # tab
    r4 = Directive('##sequence-region 1 1 1000')

    assert r1.type == 'sequence-region' and r1.seqid == 'ctg123' and \
        r1.region == Range(0, 1497228)
    assert r2.type == 'sequence-region' and r2.seqid == 'ctg123' and \
        r2.region == Range(0, 1497228)
    assert r3.type == 'sequence-region' and r3.seqid == 'ctg123' and \
        r3.region == Range(0, 1497228)
    assert r4.type == 'sequence-region' and r4.seqid == '1' and \
        r4.region == Range(0, 1000)

    with pytest.raises(AssertionError) as ae:
        r5 = Directive('##sequence-region   BoGuScHr 123456 4321')
    assert '[123455, 4321] invalid, start must be <= end' in str(ae)


def test_ontology_directives():
    """Test ontology directives."""
    so_uri = ('http://song.cvs.sourceforge.net/viewvc/song/ontology/'
              'so.obo?revision=1.263')
    attr_uri = 'http://www.bogus.edu/attr-o.obo'
    src_uri = 'http://www.bogus.edu/src-o.obo'

    o1 = Directive('##feature-ontology ' + so_uri)
    o2 = Directive('##attribute-ontology   ' + attr_uri)
    o3 = Directive('##source-ontology	' + src_uri)

    assert o1.type == 'feature-ontology' and o1.uri == so_uri
    assert o2.type == 'attribute-ontology' and o2.uri == attr_uri
    assert o3.type == 'source-ontology' and o3.uri == src_uri


def test_species_directive():
    """Test species directive."""
    amel = 'http://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=7460'
    pdom = 'http://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=743375'
    sinv = 'http://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=13686'

    s1 = Directive('##species ' + amel)
    s2 = Directive('##species   ' + pdom)
    s3 = Directive('##species	' + sinv)

    assert s1.type == 'species' and s1.uri == amel
    assert s2.type == 'species' and s2.uri == pdom
    assert s3.type == 'species' and s3.uri == sinv


def test_genome_build_directive():
    """Test genome-build directive."""
    b1 = Directive('##genome-build NCBI B36')
    b2 = Directive('##genome-build   WormBase ws110')
    b3 = Directive('##genome-build	FlyBase  r4.1')

    assert b1.type == 'genome-build' and b1.source == 'NCBI' and \
        b1.build_name == 'B36'
    assert b2.type == 'genome-build' and b2.source == 'WormBase' and \
        b2.build_name == 'ws110'
    assert b3.type == 'genome-build' and b3.source == 'FlyBase' and \
        b3.build_name == 'r4.1'


def test_sorting():
    """Test sorting and comparison"""
    from .comment import Comment
    from .feature import Feature

    gv = Directive('##gff-version   3')
    sr1 = Directive('##sequence-region chr1 500 2000')
    sr2 = Directive('##sequence-region chr1 3000 4000')
    sr3 = Directive('##sequence-region chr2 500 2000')
    sr4 = Directive('##sequence-region chr10 500 2000')
    d1 = Directive('##bonus-directive   abc 1 2 3')
    s1 = Directive('##species http://www.ncbi.nlm.nih.gov/Taxonomy/Browser/'
                   'wwwtax.cgi?id=7460')
    gff3 = ['chr', 'vim', 'mRNA', '1001', '1420', '.', '+', '.', 'ID=t1']
    f1 = Feature('\t'.join(gff3))
    c1 = Comment('# The quick brown fox jumps over the lazy dog.')

    for record in [sr1, d1, s1, f1, c1]:
        assert gv < record
        assert gv <= record
        assert not gv > record
        assert not gv >= record

    assert sr1 > gv
    assert not sr1 < gv
    for record in [d1, s1, f1, c1]:
        assert sr1 < record
        assert sr1 <= record
        assert not sr1 > record
        assert not sr1 >= record
    assert sorted([sr4, sr1, sr3, sr2]) == [sr1, sr2, sr4, sr3], '%r %r' % \
        (sorted([sr4, sr1, sr3, sr2]), [sr1, sr2, sr4, sr3])
    assert sr1 > gv
    assert sr1 >= gv
    assert sr1 <= sr2
    assert sr1 <= sr3
    assert not sr1 >= sr2
    assert not sr1 >= sr3
    assert d1 < s1
    assert d1 <= s1
    assert d1 < f1
    assert d1 <= f1
    assert s1 < c1
    assert s1 <= c1

    for record in [s1, f1, c1]:
        assert d1 < record
