##  .-.-.   .-.-.   .-.-.   .-.-.   .-.-.   .-.-.   .-.-.   .-.-.
## /|/ \|\ /|/ \|\ /|/ \|\ /|/ \|\ /|/ \|\ /|/ \|\ / / \ \ / / \ \
##`-'   `-`-'   `-`-'   `-`-'   `-`-'   `-`-'   `-`-'   `-`-'   ' '

## Feb 2012 Dream5 pipeline (MCZ,tlCLR,Inferelator)
## Bonneau lab - "Aviv Madar" <am2654@nyu.edu>,
##  		     "Alex Greenfield" <ag1868@nyu.edu>
## NYU - Center for Genomics and Systems Biology

##  .-.-.   .-.-.   .-.-.   .-.-.   .-.-.   .-.-.   .-.-.   .-.-.
## /|/ \|\ /|/ \|\ /|/ \|\ /|/ \|\ /|/ \|\ /|/ \|\ / / \ \ / / \ \
##`-'   `-`-'   `-`-'   `-`-'   `-`-'   `-`-'   `-`-'   `-`-'   ' '

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Doaa: functions to parese input from a string
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


############################

read.cmd.line.params.must <- function(args.nms, cmd.line.args){
	args <- sapply(strsplit(cmd.line.args," "),function(i) i)
	vals <- character(length(args.nms))
	# split cmd.line to key and value pairs
	for(i in 1:length(args.nms)){
		ix <- grep(args.nms[i],args)
		if(length(ix)>1){
			stop("arg ",args.nms[i]," used more than once.  Bailing out...\n")
		} else if (length(ix)==0){
			stop("could not find ",args.nms[i],". Bailing out...\n")
		} else {
			vals[i] <- args[ix+1]
		}
	}
	return(vals)
}
############################
read.cmd.line.params.optional <- function(args.nms, cmd.line.args){
	args <- sapply(strsplit(cmd.line.args," "),function(i) i)
	vals <- character(length(args.nms))
	# split cmd.line to key and value pairs
	for(i in 1:length(args.nms)){
		ix <- grep(args.nms[i],args)
		if(length(ix)>1){
			stop("arg ",args.nms[i]," used more than once.  Bailing out...\n")
		} else if (length(ix)==0){ # if --param was not written in cmd line
			vals[i] <- NA
		} else if(( (ix+1) <= length(args) ) & ( length(grep("--",args[ix+1])) == 0) ){
			# if --param was written in cmd line AND not followed by another --param
		 	vals[i] <- args[ix+1]
		} else { # otherwise
			vals[i] <- NA
		}
	}
	return(vals)
}
############################

parseOptions <- function(givenOptions){
    rm(list = ls())
    # global var
    assign("verbose", F, envir = .GlobalEnv)
    # verbose = F

    args.nms.must <- c(
            "--data_file",      #1
            "--path_to_scripts" #2
    )

    args.nms.optional <- c(
            "--reg_file",  	 #1
            "--meta_file", 	 #2
            "--inf_max_reg", #3
            "--n_boots", 	 #4
            "--tau",		 #5
            "--num_pred",     #6
            "--num_processors", #7
            "--clr_then_stop" #8
    )

    # get parameters
    vals.must <- read.cmd.line.params.must(args.nms = args.nms.must, cmd.line.args = givenOptions)

    vals.optional <- read.cmd.line.params.optional(args.nms = args.nms.optional, cmd.line.args = givenOptions)

    assign("INPUT", list(), envir = .GlobalEnv)
    # INPUT              = list()
    INPUT[["general"]] <<- list()
    INPUT[["clr"]]     <<- list()
    INPUT[["lars"]]    <<- list()

    assign("PARAMS", list(), envir = .GlobalEnv)
    # PARAMS              = list()
    PARAMS[["general"]] <<- list()
    PARAMS[["clr"]]     <<- list()
    PARAMS[["lars"]]    <<- list()
    PARAMS[["output"]]  <<- list()

    PARAMS[["general"]][["d.path"]] <<- vals.must[1]
    PARAMS[["general"]][["scripts.path"]] <<- vals.must[2]

    if(is.na(vals.optional[1])){
        PARAMS[["general"]][["tfs.path"]] <<- NA
    } else {
        PARAMS[["general"]][["tfs.path"]] <<- vals.optional[1]
    }

    if(is.na(vals.optional[2])){
        PARAMS[["general"]][["f.path"]] <<- NA
    } else {
        PARAMS[["general"]][["f.path"]] <<- vals.optional[2]
    }

    if(is.na(vals.optional[3])){
        PARAMS[["lars"]][["max_single_preds"]] <<- 25
    }else{
        PARAMS[["lars"]][["max_single_preds"]] <<- as.numeric(vals.optional[3])
    }

    if(is.na(vals.optional[4])){
        PARAMS[["general"]][["numBoots"]] <<- 10
    }else{
        PARAMS[["general"]][["numBoots"]] <<- as.numeric(vals.optional[4])
    }

    if(is.na(vals.optional[5])){
        PARAMS[["general"]][["tau"]] <<- 10
    }else{
        PARAMS[["general"]][["tau"]] <<- as.numeric(vals.optional[5])
    }

    if(is.na(vals.optional[6]) || (vals.optional[6] == -1)){
        PARAMS[["general"]][["num.inters.out"]] <<- Inf
    }else{
        PARAMS[["general"]][["num.inters.out"]] <<- as.numeric(vals.optional[6])
    }

    if(is.na(vals.optional[7])){
        PARAMS[["general"]][["processorsNumber"]] <<- 2
    }else{
        PARAMS[["general"]][["processorsNumber"]] <<- as.numeric(vals.optional[7])
    }

    if(is.na(vals.optional[8])){
        PARAMS[["general"]][["clr_then_stop"]] <<- FALSE
    }else{
        PARAMS[["general"]][["clr_then_stop"]] <<- as.numeric(vals.optional[8])
    }

    numeric.params <- c("numBoots", "tau", "num.inters.out")
    # check if numeric params are indeed numeric
    for(i in numeric.params){
        if(is.na(as.numeric(PARAMS$general[[paste(i, sep = "")]]))){
            stop("arg ",args.nms.optional[i]," is not numeric.  Bailing out...\n")
        }
    }
    #print(PARAMS)
}

#########################

# Testing
#given.options = c('--data_file input/DREAM5/net3/net3_expression_data_1250.tsv --reg_file input/DREAM5/net3/net3_transcription_factors.tsv --meta_file input/DREAM5/net3/net3_chip_features.tsv --inf_max_reg 30 --n_boots 3 --tau 15 --num_pred 10000 --path_to_scripts ./scripts_GenePattern/')
#parseOptions(given.options)
#print(PARAMS)

