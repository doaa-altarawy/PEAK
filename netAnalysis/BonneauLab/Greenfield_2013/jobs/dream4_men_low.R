PARS$input.dir <- 'input/dream4'

PARS$meta.data.file <- 'meta_data.tsv'
# PARS$priors.file <- 'gold_standard.tsv'
PARS$priors.file <- 'priors_empty.tsv'
PARS$gold.standard.file <- 'gold_standard.tsv'

PARS$num.boots <- 1
#PARS$cores <- 12
PARS$cores <- 1

PARS$delT.max <- 110
PARS$delT.min <- 0
PARS$tau <- 45

PARS$perc.tp <- 100
PARS$perm.tp <- 1
PARS$perc.fp <- 0
PARS$perm.fp <- 1

PARS$eval.on.subset <- FALSE

PARS$method <- 'MEN'
PARS$prior.weight <- 0.5

PARS$save.to.dir <- paste('output/dream4', PARS$method, PARS$prior.weight, sep='_')

# Doaa: stop execution after saving mixedCLR matrix
PARS$get.mixedCLR.only <- TRUE
