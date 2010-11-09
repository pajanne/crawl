#!/usr/bin/env python
# encoding: utf-8
"""
pysam_test.py

Created by Giles Velarde on 2010-11-04.
Copyright (c) 2010 Wellcome Trust Sanger Institute. All rights reserved.
"""

import optparse
import pysam
import subprocess
import sys

def main():
    
    parser = optparse.OptionParser(usage="pysam_test.py [-s] [-e] /path/to/bam reference_name")
    
    parser.add_option(
        "-s", "--start", 
        dest="start", 
        action="store", 
        default=0, 
        help="the start position")

    parser.add_option(
        "-e", "--end", 
        dest="end", 
        action="store", 
        default=1000, 
        help="the end position")
    
    (options, args) = parser.parse_args()
    
    try:
        file_path = args[0]
        reference = args[1]
        start = int(options.start)
        end = int(options.end)
    except Exception, e:
        print "Error:"
        print e
        print 
        parser.print_help()
        sys.exit(1)
    
    print (reference, start, end)
    
    samtools_cli_exec = ["samtools", "view",  file_path,  "%s:%d-%s" % (reference, start, end) ]
    samfile = pysam.Samfile( file_path, "rb" )
    
    pysam_reads = []
    samtools_reads = []
    
    for aligned_read in samfile.fetch( reference=reference, start=start, end=end ):
        pysam_reads.append(aligned_read.qname)
    
    samtools_cli_results = subprocess.Popen(samtools_cli_exec, stdout=subprocess.PIPE).communicate()[0]
    for line in samtools_cli_results.split("\n"):
         cols = line.split("\t")
         if len(cols[0]) == 0:
             continue
         samtools_reads.append(cols[0])
    
    assert len(pysam_reads) == len(samtools_reads)
    assert len (set(pysam_reads) - set(samtools_reads)) == 0
    assert len (set(samtools_reads) - set(pysam_reads)) == 0
    
    print ((len(pysam_reads), len(samtools_reads)))
    
    for r in pysam_reads:
        assert r in samtools_reads
    
    for r in samtools_reads:
        assert r in pysam_reads
    
if __name__ == '__main__':
    main()

