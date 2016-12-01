__author__ = 'doaa'

from netAnalysis.Peak import *
import csv, datetime
from netAnalysis.experiments.expr_util import *
from collections import OrderedDict
from netAnalysis.scoring.PR_ROC import get_accuracy_realData


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == "__main__":

    datasetName = 'Root' #'Net1', 'Net3_conn_final', 'Net4', 'Grene'

    alphas_small = [0.001, 0.01, 0.05, 0.1]
    alphas_large = [0.1, 0.2, 0.4, 0.6, 0.8, 1, 2, 3]
    #
    params = OrderedDict([('fileName', ''), ('priorPercent', 0), ('falsePriorRatio', 0),
                          ('priorWeight', 0.01),
                          ('alpha', 0.1), ('l1_ratio', 0.5), ('isCV', 1), ('fit_intercept', 1),
                          ('scaleX', 1), ('halfLife', 10), ('method', 'FeatureScaling'), ('freeCV', 0)])

    # params = OrderedDict([('fileName', ''), ('priorPercent', 100), ('falsePriorRatio', 0),
    #                       ('priorWeight', 0.01),
    #                       ('alpha', 0.1), ('l1_ratio', 0.5), ('isCV', 1), ('fit_intercept', 1),
    #                       ('scaleX', 1), ('halfLife', 10), ('method', 'PenaltyScaling'), ('freeCV', 1)])


    filename = run_Peak_test(datasetName, params, alphas_small)
    pathToPred = ds.datasets['Root'].get_outFile() + filename
    AUROC, AUPR, _, _ = get_accuracy_realData(network=datasetName, predFile=pathToPred, visualize=False)
    pathToCombined = pathToPred[:-9] + "::Combined"
    AUROC, AUPR, _, _ = get_accuracy_realData(network=datasetName, predFile=pathToCombined, visualize=False)
    mapGeneNames(datasetName='Root', filename=pathToPred)


    # print(paramsFileName)
    # filename = ds.datasets['Root'].get_outFile() + '_priorPerct100_weight0.01__scaled__Nov-18_18-22--03FeatureScaling::InfOnly'
    # mapGeneNames(datasetName='Root', filename=filename)

