By Doaa:
========

Buiding older R ()
==================

install the source code from:
http://cran.r-project.org/src/base/R-2/R-2.15.0.tar.gz

make this fix:
sudo ln -s /usr/lib/x86_64-linux-gnu/libgfortran.so.3 /usr/lib/libgfortran.so

Then unzip then run:
./configure --with-readline=no --with-x=no
make



==========================================================
Install Latest R:
------------------

sudo gedit /etc/apt/sources.list

Add entry:
deb http://cran.cnr.Berkeley.edu/bin/linux/ubuntu trusty/

sudo apt-get update
sudo apt-get install r-base
sudo apt-get install r-base-dev

Installing required packages:
------------------------------
sudo R

Then in the R shell install packages:

install.packages("inline")
or
install.packages(c("inline"))
install.packages(c("multicore"))
install.packages(c("elasticnet"))
install.packages(c("Matrix"))
install.packages(c("corpcor"))
install.packages(c("nnls"))
install.packages(c("parallel"))

To install the old multicore package:
download from:
http://cran.r-project.org/src/contrib/Archive/multicore/
Then:

install.packages('/var/www/DeTangle/DeTangle/netAnalysis/BonneauLab/Greenfield_2013/multicore', repos = NULL, type="source")

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Call the inferelator script from the base directory (the one containing this 
README) with a job config file as argument. 

Example call: Rscript inferelator.R jobs/dream4_cfg.R



--------------------------------------------------------------------------------
Default parameters and a brief explanation of each one
--------------------------------------------------------------------------------

PARS$input.dir <- 'input/dream4'  # path to the input files

PARS$exp.mat.file <- 'expression.tsv'  # required; see definition below
PARS$tf.names.file <- 'tf_names.tsv'  # required; see definition below
PARS$meta.data.file <- 'meta_data.tsv'  # assume all steady state if NULL
PARS$priors.file <- 'gold_standard.tsv'  # no priors if NULL
PARS$gold.standard.file <- 'gold_standard.tsv'  # no evaluation if NULL

PARS$job.seed <- 42  # random seed; can be NULL
PARS$save.to.dir <- file.path(PARS$input.dir, date.time.str)  # output directory
PARS$num.boots <- 20  # number of bootstraps; no bootstrapping with a value of 1
PARS$max.preds <- 10  # max number of predictors based on CLR to pass to model
                      # selection method
PARS$mi.bins <- 10  # number of bins to use for mutual information calculation
PARS$cores <- 8  # number of cpu cores

PARS$delT.max <- 110  # max number of time units allowed between time series 
                      # conditions
PARS$delT.min <- 0  # min number of time units allowed between time series 
                    # conditions
PARS$tau <- 45  # constant related to half life of mRNA (see Core model)

# These values make it use exactly the given priors
PARS$perc.tp <- 0  # percent of true priors that will be used; can be vector
PARS$perm.tp <- 1  # number of permutations of true priors
PARS$perc.fp <- 0  # percent of false priors (100 = as many false priors as 
                   # there are true priors); can be vector
PARS$perm.fp <- 1  # number of permutations of false priors

PARS$eval.on.subset <- FALSE  # whether to evaluate only on the part of the 
                              # network that has connections in the gold
                              # standard; if TRUE false priors will only be 
                              # drawn from that part of the network

PARS$method <- 'MEN'  # which method to use; either 'MEN' or 'BBSR'
PARS$prior.weight <- 0.5  # >>> the weight for the priors, if 1 then priors won't be used ???

# ???
PARS$use.tfa <- TRUE


--------------------------------------------------------------------------------
Required Input Files
--------------------------------------------------------------------------------

expression.tsv
--------------
expression values; must include row (genes) and column (conditions) names

tf_names.tsv
------------
one TF name on each line; must be subset of the row names of the expression data



--------------------------------------------------------------------------------
Optional Input Files
--------------------------------------------------------------------------------

meta_data.tsv
-------------
the meta data describing the conditions; must include column names;
has five columns:
isTs: TRUE if the condition is part of a time-series, FALSE else
is1stLast: "e" if not part of a time-series; "f" if first; "m" middle; "l" last
prevCol: name of the preceding condition in time-series; NA if "e" or "f"
del.t: time in minutes since prevCol; NA if "e" or "f"
condName: name of the condition

priors.tsv
----------
matrix of 0 and 1 indicating whether we have prior knowledge in 
the interaction of one TF and a gene; one row for each gene, one column for 
each TF; must include row (genes) and column (TF) names

gold_standard.tsv
-----------------
needed for validation; matrix of 0 and 1 indicating whether there is an 
interaction between one TF and a gene; one row for each gene, one column for 
each TF; must include row (genes) and column (TF) names



--------------------------------------------------------------------------------
Output Files
--------------------------------------------------------------------------------

One or more betas_frac_tp_X_perm_X--frac_fp_X_perm_X_X.RData files. One file
per true and false prior and prior weight combination. Each RData file contains
two lists of length PARS$num.boots where every entry is a matrix of betas and
confidence scores (rescaled betas) respectively.

One or more combinedconf_frac_tp_X_perm_X--frac_fp_X_perm_X_X.RData files with
one matrix each. The matrix is the rank-combined version of the confidence
scores of all bootstraps.

A params_and_input.RData file with data objects holding the user set parameters,
and input and input-derived objects.
