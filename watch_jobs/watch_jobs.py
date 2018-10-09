# -*- coding: utf-8 -*-
"""Simple script for checking current state of optimization scripts"""
import subprocess as sp
import pandas as pd
import argparse as ap
import numpy as np
import glob
import os

#################################
#  PARSING COMMAND LINE INPUTS  #
##########################################################################
parser = ap.ArgumentParser(
    description=("""Check progress of optimization jobs and if desired
                 already make plots based on preliminary data """),
    formatter_class=ap.ArgumentDefaultsHelpFormatter)
parser.add_argument('-plots', dest='plots', action='store_true',
                    help='make plots based on preliminary data')
parser.add_argument('-combine', dest='combine', action='store_true',
                    help='combine different runs into one directory')
# TODO: think about plotting jobs with different dt's or number of profiles used...
parser.add_argument('-dt', dest='dt', type=int, default=10,
                    help='temporal discretization used for optimization')
parser.add_argument('-sep', dest='sep', type=str, default='_',
                    help='separator for subjobs.')
# parsing command line flags
args = parser.parse_args()
##########################################################################

#######################
#  SETUP ENVIRONMENT  #
##########################################################################
found_results = False
##########################################################################


###############
#  FUNCTIONS  #
##########################################################################
def check_iterations(directories):
    """Check number of completed iterations."""
    for d in directories:
        # only look at directories with results.h5 files in them
        contents = glob.glob(d+'/*')
        if 'results.h5' in ''.join(contents).split('/'):
            global found_results  # apparently found some results
            found_results = True
            sp.call(['cp', d+'/results.h5', '.'], cwd=os.getcwd())
            res = pd.HDFStore('results.h5')
            print("%s completed %i iterations" % (d.split('/')[-1], res.root._v_nchildren))
            res.close()
            sp.call(['rm', 'results.h5'], cwd=os.getcwd())


def make_plots(directories):
    """Make plots for different runs."""
    for d in directories:
        # only look at directories with results.h5 files in them
        contents = glob.glob(d+'/*')
        if 'results.h5' in ''.join(contents).split('/'):
            sp.call(['cp', '-r', d, 'temp'], cwd=os.getcwd())
            # assume .txt file contains profile data
            txt = glob.glob(os.getcwd()+'/temp/*.txt')[0]  # NOTE: assuming only one .txt file...
            plt_cmd = sp.Popen(['python', 'DF_fitting.py', '-p', txt, '-ana'],
                               cwd=os.getcwd()+'/temp/', stdin=sp.PIPE)
            # NOTE: asssuming all profiles have been fitted ...
            plt_cmd.communicate(input=b'%i\nall\n1' % args.dt)
            # copy plots made to correct directory
            sp.call(['cp', '-r', os.getcwd()+'/temp/results', d+'/results'],
                    cwd=os.getcwd())
            sp.call(['rm', '-r', os.getcwd()+'/temp'], cwd=os.getcwd())


def combine_runs(directories, sep='_'):
    """
    Combine runs of same setup in different directories into one directory.

    sep     -   character separating identical setups
    """
    # find unique optimization setups
    setups = np.unique([sep.join(d.split('/')[-1].split('%s' % sep)[:-1])
                        for d in directories])
    prefix = '/'.join(directories[0].split('/')[:-1])  # path to cwd
    for s in setups:
        jobs = glob.glob('/'.join([prefix, s])+'*')  # all subdirectories with suffixes
        # create final directory for combination
        combi_dir = sep.join(jobs[0].split(sep)[:-1])
        sp.call(['cp', '-r', jobs[0], combi_dir], cwd=os.getcwd())
        sp.call(['rm', '-r', 'results.h5', 'results'], cwd=combi_dir)

        # write everything into combined storage
        with pd.HDFStore(combi_dir+'/results.h5', complevel=9) as res_combi:
            iter = 1  # start with run 1
            for j in jobs:
                print('Currently gathering runs from %s...' % j.split('/')[-1])
                contents = glob.glob(j+'/*')
                # only look at directories with results.h5 files in them

                # TODO: built in check that takes care of corrupt hdf stores
                # and skip to next job run
                if 'results.h5' in ''.join(contents).split('/'):
                    global found_results  # apparently found some results
                    found_results = True
                    res_job = pd.HDFStore(j+'/results.h5', 'r')
                    for run in list(res_job.root._v_children.keys()):
                        try:
                            res_combi['r%i' % iter] = res_job[run]  # copy current run
                            for sub in ['active_mask', 'fun', 'grad', 'jac', 'x']:
                                print('Copying run {:>4}/{:12}'.format(run, sub), end='\r', flush=True)
                                # copy sub directories
                                res_combi['r%i/%s' % (iter, sub)] = res_job["%s/%s" % (run, sub)]
                        except KeyError:
                            res_combi.remove('r%i' % iter)
                            break  # skip run if sub-directory is missing, due to unfinished run

                        iter += 1  # count to next run
                    res_job.close()  # closing opened store

    # from now on only work on new combined directories
    combined_dirs = ['/'.join([prefix, s]) for s in setups]
    return combined_dirs
##########################################################################


###############
#  FUNCTIONS  #
##########################################################################
def main():
    # find all sub-directories of current directory
    dirs = glob.glob(os.getcwd()+'/*')

    # first combine results
    if args.combine:
        print("Combining different jobs...\n")
        dirs = combine_runs(dirs, sep='_')   # now only work on combined results directories
        args.plots = True  # also make plots when combining results

    # count number of completed iterations
    check_iterations(dirs)

    # only make plots if results were found
    if args.plots and found_results:
        print("\nNow making plots...")
        make_plots(dirs)

    if not found_results:
        print("\nNo 'results.h5' file was found in sub-directories...")
##########################################################################


if __name__ == "__main__":
    main()
