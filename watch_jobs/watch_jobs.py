# -*- coding: utf-8 -*-
"""Simple script for checking current state of optimization scripts"""
import subprocess as sp
import pandas as pd
import argparse as ap
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
            global found_results
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


def main():
    # find all sub-directories of current directory
    dirs = glob.glob(os.getcwd()+'/*')
    # count number of completed iterations
    found_results = check_iterations(dirs)

    # combine results if found
    if args.combine and found_results:
        # TODO: write function combining all runs into one directory...

    # only make plots if results were found
    if args.plots and found_results:
        print("Now making plots...")
        make_plots(dirs)

    if not found_results:
        print("No 'results.h5' file was found in sub-directories...")


if __name__ == "__main__":
    main()
