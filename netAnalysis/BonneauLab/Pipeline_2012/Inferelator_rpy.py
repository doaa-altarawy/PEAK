"""Implimentation of greenfield 2012 in python using rpy to call
the R code

Author: Doaa Altarawy,
Virginia Tech
Data: March 2015
"""

import rpy2.robjects as robjects
import rpy2.rinterface as rinterface
from rpy2.robjects.packages import SignatureTranslatedAnonymousPackage as rpkg
import os

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def run_Inf_R(options):
    """Runs Inferelator pipline by calling R code
        This function uses rpy2 to use R within python.
        The goal is to reactor needed code from R to Python gradually.

    @param options: string of Inferelator parameters
    @return:
    """

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #           Set parameters
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # Read R source file
    curPath = os.path.dirname(os.path.realpath(__file__)) ### TODO
    with open(curPath+'/R_readOptions.R', 'r') as f:
        string = ''.join(f.readlines())

    # import the file as a package
    readParam = rpkg(string, "readParam")

    robjects.r("givenOptions <- c('')")
    robjects.globalenv['givenOptions'] = options

    # I couldn't pass parameter to the R function!!!!!!! ### TODO
    readParam.parseOptions()

    # robjects.r('print(PARAMS)')

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #       Run main Inferelator pipline
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    robjects.r('''
        source(paste(sep="",PARAMS[["general"]][["scripts.path"]],"/init_util.R"))
        source(paste(sep="",PARAMS[["general"]][["scripts.path"]],"/utils.R"))
        source(paste(sep="",PARAMS[["general"]][["scripts.path"]],"/larsUtil.R"))
        source(paste(sep="",PARAMS[["general"]][["scripts.path"]],"/bootstrapUtil.R"))
        source(paste(sep="",PARAMS[["general"]][["scripts.path"]],"/d5_util.R"))
        source(paste(sep="",PARAMS[["general"]][["scripts.path"]],"/prepare_data.R"))

        # Doaa: Inint some param, construct matrices
        source(paste(sep="",PARAMS[["general"]][["scripts.path"]],"/init.R"))

        # Doaa: just ran/add discMIhelper c code!, include many funcs
        #we are sourcing CLR here bceause a needed library is loaded in init.R
        source(paste(sep="",PARAMS[["general"]][["scripts.path"]],"/clr.R"))

        print('~~~~~~~~~~~~starting main~~~~~~~~~~~~')
        source(paste(sep="",PARAMS[["general"]][["scripts.path"]],"/main.R"))

        q(status=1)
    ''')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def end_R():
    rinterface.endr()