
library(PRROC)

A <- read.table("/home/doaa/Dropbox/2_My_Results/EvaluationScripts_Matlab/INPUT/predictions/pred.tsv", sep=",")

B <- read.table("/home/doaa/Dropbox/2_My_Results/EvaluationScripts_Matlab/INPUT/predictions/gold.tsv", sep=",")

pr<-pr.curve(scores.class0 = B[['V2']], scores.class1 = A[['V2']])


---------------

library(ROCR)

A <- read.table("/home/doaa/Dropbox/2_My_Results/EvaluationScripts_Matlab/INPUT/predictions/pred.tsv", sep=",")

B <- read.table("/home/doaa/Dropbox/2_My_Results/EvaluationScripts_Matlab/INPUT/predictions/gold.tsv", sep=",")

test = A[['V2']]
gold = B[['V2']]

pred <- prediction( test, gold )

## precision/recall curve (x-axis: recall, y-axis: precision)
prec <- performance(pred, "prec")
rec <- performance(pred, "rec")

library(caTools)
auc <- trapz(rec, prec)