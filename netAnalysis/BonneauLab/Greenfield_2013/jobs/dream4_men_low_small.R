PARS$input.dir <- 'input/dream4_small'

# ===========
PARS$exp.mat.file <- 'expression.tsv'
PARS$tf.names.file <- 'tf_names.tsv'
# ===========

PARS$meta.data.file <- 'meta_data.tsv'
PARS$priors.file <- 'gold_standard.tsv'
PARS$gold.standard.file <- 'gold_standard.tsv'

PARS$num.boots <- 1
#PARS$cores <- 12
PARS$cores <- 1

# Interval between time series data??
PARS$delT.max <- 110
PARS$delT.min <- 0
PARS$tau <- 45

# perc.tp, perm.tp, perc.fp and perm.tp must have the same length
#  This values means use all priors as is ~check.. ok
PARS$perc.tp <- 100
PARS$perm.tp <- 1
PARS$perc.fp <- 0
PARS$perm.fp <- 1
# Doaa: use permulation of priors or not
PARS$not.use.permulation <- TRUE

PARS$eval.on.subset <- FALSE

PARS$method <- 'MEN'
PARS$prior.weight <- 0.5

PARS$save.to.dir <- paste('output/dream4', PARS$method, PARS$prior.weight, sep='_')


PARS$use.tfa <- TRUE

PARS$enet.lambda <- 1  # l2 weights
