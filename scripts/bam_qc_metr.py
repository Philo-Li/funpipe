#!/usr/bin/env python3

from os.path import dirname, basename, splitext, join
import sys
import argparse
from crimson import picard
import json
import pandas as pd

stats = {
    'alignment_summary_metrics':
        ['TOTAL_READS', 'PCT_PF_READS_ALIGNED', 'PCT_CHIMERAS'],
    'gc_bias.summary_metrics':
        ['AT_DROPOUT', 'GC_DROPOUT'],
    'insert_size_metrics':
        ['MEDIAN_INSERT_SIZE', 'STANDARD_DEVIATION'],
    'wgs_metrics': ['MEAN_COVERAGE']
}

stats_list = [
    'TOTAL_READS', 'PCT_PF_READS_ALIGNED', 'PCT_CHIMERAS', 'AT_DROPOUT',
    'GC_DROPOUT', 'MEDIAN_INSERT_SIZE', 'STANDARD_DEVIATION', 'MEAN_COVERAGE']


def get_picard_stat(file):
    all_metr = picard.parse(file)['metrics']['contents']
    if isinstance(all_metr, dict):
        return all_metr
    else:
        return all_metr[-1]


def get_ref_fa(file):
    ''' get reference sequence from "analysis files"
    :param file: path to the bam files
    '''
    df = pd.read_csv('/seq/picard_aggregation/G143266/CL161/current/analysis_files.txt', header=0, sep='\t')


def parse_gp_bam_path(path):
    ''' parse on-prem BAM path from the genomic platform, to get directory,
    base name, prefix and suffix of the BAM. Prefix of the BAM is usually
    sample name.
    :param path: on-prem bam path from the genomic platform
    '''
    fdir = dirname(path)          # file directory
    base = basename(path)         # base name of the bam
    prefix = splitext(base)[0]    # prefix of the bam file, usually sample name
    suffix = splitext(base)[-1]   # suffix of the bam file
    return fdir, base, prefix, suffix


def output_stats(qc_stats, bam_qc_file):
    ''' output qc statistics to a file
    :param qc_stats: an array that contains all BAM QC statistics
    :param bam_qc_file: file path to output all the metrics
    '''
    with open(bam_qc_file, 'w+') as bam_qc:
        # output header to the file
        bam_qc.write('\t'.join(['Sample'] + stats_list)+'\n')
        # output QC stats for each sample from the array
        for sample in qc_stats:
            stats = [sample]
            for stat in stats_list:
                stats.append(str(qc_stats[sample][stat]))
            bam_qc.write('\t'.join(stats)+'\n')


def process_bam_files(bam_list_file, bam_qc_file):
    ''' process all bam files and get corresponding QC metrics and reference
    paths from Broad's Genomic Platform
    :param bam_list_file: a list of bam files
    :param bam_qc_file: file path to output all QC metrics
    '''
    qc_stats = {}
    with open(bam_list_file, 'r') as bam_list:
        # process each bam record in the bam list
        for line in bam_list:
            sample, path = line.strip().split('\t')
            fdir, fname, prefix, suffix = parse_gp_bam_path(path)
            qc_stats[sample] = {}
            for suffix in pstats:
                all_metr = get_picard_stat(join(fdir, prefix+'.'+suffix))
                for stat in pstats[suffix]:
                    qc_stats[sample][stat] = all_metr[stat]
    output_stats(qc_stats, bam_qc_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Parse Picard metrics from broad GP platform')
    # required arguments
    required = parser.add_argument_group('required arguments')
    required.add_argument(
        '-i', '--input', required=True, help='BAM list')
    required.add_argument(
        '-o', '--output', help="Output file")

    # optional arguments
    parser.add_argument(
        '-d', '--outdir', default='.', help='Output Directory')

    args = parser.parse_args()
    process_bam_files(
        args.input, join(args.outdir, args.output))