# -*- coding: utf-8 -*-
"""Simple script for checking current state of optimization scripts"""
import subprocess as sp
import pandas as pd
import glob
import os


def main():
    found_results = False
    # find all sub-directories of current directory
    dirs = glob.glob(os.getcwd()+'/*')
    for d in dirs:
        # only look at directories with results.h5 files in them
        contents = glob.glob(d+'/*')
        if 'results.h5' in ''.join(contents).split('/'):
            found_results = True
            sp.call(['cp', d+'/results.h5', '.'], cwd=os.getcwd())
            res = pd.HDFStore('results.h5')
            print("%s completed %i iterations" % (d.split('/')[-1], res.root._v_nchildren))
            res.close()
            sp.call(['rm', 'results.h5'], cwd=os.getcwd())

    if not found_results:
        print("No 'results.h5' file was found in sub-directories...")


if __name__ == "__main__":
    main()
