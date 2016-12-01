"""
================
Precision-Recall
================

Precision-Recall metric to evaluate classifier output quality.

Precision (:math:`P`) is defined as the number of true positives (:math:`T_p`)
over the number of true positives plus the number of false positives
(:math:`F_p`).

:math:`P = \\frac{T_p}{T_p+F_p}`

Recall (:math:`R`) is defined as the number of true positives (:math:`T_p`)
over the number of true positives plus the number of false negatives
(:math:`F_n`).

:math:`R = \\frac{T_p}{T_p + F_n}`

These quantities are also related to the (:math:`F_1`) score, which is defined
as the harmonic mean of precision and recall.

:math:`F1 = 2\\frac{P \\times R}{P+R}`

"""

import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import precision_score, average_precision_score
from sklearn.metrics import roc_curve, auc
import pandas as pd
import itertools
from netAnalysis.utils import Datasets as ds



def get_AUPR(y_true, y_score, visualize=True):
    """Compute area under the Precision-Recall curve
    and plot PR curve

    :param y_true: True known labdels (TF, gene)
    :param y_score: predicted labels (TF, gene)
    :param visualize: If true, plot ROC curve
    :return: Area under PR curve
    """

    precision, recall, _ = precision_recall_curve(y_true, y_score)
    average_precision = average_precision_score(y_true, y_score)
    # average_precision = auc(recall, precision)

    if visualize:
        # Plot Precision-Recall curve
        plt.clf()
        plt.plot(recall, precision, label='Precision-Recall curve')
        plt.plot([0, 1], [1, 0], 'k--')
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.ylim([0.0, 1.05])
        plt.xlim([0.0, 1.0])
        plt.title('Precision-Recall: AUPR={0:0.2f}'.format(average_precision))
        plt.legend(loc="lower left")
        plt.show()

    return average_precision

# --------------------------------------------------------------------

def get_ROC(y_true, y_score, visualize=True):
    """Calculate Area under ROC accuracy for y_score

    :param y_true: True known labdels (TF, gene)
    :param y_score: predicted labels (TF, gene)
    :param visualize: If true, plot ROC curve
    :return: tuple: (AUROC, FPR, TPR)
    """

    fpr, tpr, _ = roc_curve(y_true, y_score)
    roc_auc = auc(fpr, tpr)

    if visualize:
        # Plot of a ROC curve
        plt.figure()
        plt.plot(fpr, tpr, label='ROC curve (area = %0.2f)' % roc_auc)
        plt.plot([0, 1], [0, 1], 'k--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver operating characteristic')
        plt.legend(loc="lower right")
        plt.show()

    return roc_auc, fpr, tpr

# ------------------------------------------------------------------------

def get_accuracy_realData(network='test', predFile=None, visualize=True):
    """Calculate the accuracy of a network (predefined dataset) using the
    given prediction file (otherwise use the default prediction file)

    :param network: predefined dataset name in ds.datasets
    :param predFile: prediction file
    :param visualize:
    :return: tuple: (ROC, AUPR, fpr, tpr)
    """

    dataset = ds.datasets[network]

    expr = pd.read_csv(dataset.get_exprFile(), sep='\t', header=None)

    uniqueGenes = np.unique(expr.loc[0])
    allComb = np.array(getCombinations(uniqueGenes))
    allComb = [str(edge[0])+','+ str(edge[1]) for edge in allComb]
    allComb = sorted(allComb)
    # print('all combinations shape:', len(allComb))

    # Gold standard
    # -------------
    gold_std = pd.read_csv(dataset.get_goldStd(), sep='\t', header=None)

    gold_std = gold_std.iloc[:, 0:2].values
    gold_std =  map(sorted, gold_std)

    gold_std = [str(edge[0])+','+ str(edge[1]) for edge in gold_std]
    gold_std = getTrueNegativeEdges(gold_std, allComb)


    # Predictions
    # --------------------------
    if predFile is None:
        predFile = dataset.get_outFile()

    pred = pd.read_csv(predFile, sep='\t', header=None)
    confid = pred.iloc[:, 2].values
    pred = pred.iloc[:, 0:2].values
    pred =  map(sorted, pred)
    pred = [str(edge[0])+','+ str(edge[1]) for edge in pred]
    # print("predictions shape: ", len(pred))
    pred = getTrueNegativeEdges(pred, allComb, confid=confid)
    print('Number of edges in final pred: ', np.count_nonzero(pred))

    d = pd.DataFrame(allComb)
    d['value'] = pred

    d = pd.DataFrame(allComb)
    d['value'] = gold_std

    AUPR = get_AUPR(gold_std, pred, visualize=visualize)
    print("AUPR: ", AUPR)

    ROC, fpr, tpr = get_ROC(gold_std, pred, visualize=visualize)
    print('AUCROC', ROC)

    return ROC, AUPR, fpr, tpr


# -------------------------------------------------------------------------

def getTrueNegativeEdges(pred, allComb, confid=1):
    """Find tru genative edges by finding all possible combinations
    missing from the prediction

    :param pred: true predicted edges
    :param allComb: all possible edges
    :param confid:
    :return:
    """

    pred_all_indx = np.searchsorted(allComb, pred)
    pred_all_indx = np.extract(pred_all_indx<len(allComb), pred_all_indx) # and pred_all_indx>-1
    pred_all_indx = np.extract(pred_all_indx>-1, pred_all_indx) # and pred_all_indx>-1

    pred_all = np.zeros(len(allComb))
    pred_all[pred_all_indx] = confid

    return pred_all

# -------------------------------------------------------------------------

def isEdgeInSet(edge, eSet=[]):
    """Check if the given edge is in the eSet"""

    if edge in eSet:
        return 1
    return 0

# -------------------------------------------------------------------------

def getCombinations(alphabet, r=2):
    """Get all combinations using the given alphbet
    :param alphabet: array of the alphabet
    :param r: size
    """

    comb = [i for i in itertools.combinations(alphabet, r)]
    comb =  map(sorted, comb)
    return comb

# ------------------------------------------------------------------------

def getUniqueRows(array):
    sort = np.sort(array, axis=1)
    return np.vstack({tuple(row) for row in sort})


# -------------------------------------------------------------------------

def test_data(network='Grene', paramsFile='', save=True):
    """Calculate the accuracy of a network (predefined dataset) using
    the given prediction file (otherwise use the default prediction file)

    :param network: predefined dataset name in ds.datasets
    :param predFile: prediction file
    :param save: if true, save predictions to file
    """

    pathToPred = ds.datasets[network].get_outFile()
    print(pathToPred)

    params = pd.read_csv(paramsFile, sep='\t')

    lastIndex = params.shape[0]
    indices = params.index.values
    for i in indices:
        fileName = pathToPred + params.loc[i, 'fileName']
        print(fileName)
        AUROC, AUPR, _, _ = get_accuracy_realData(network=network,
                                        predFile=fileName + '::InfOnly', visualize=False)
        params.loc[i, 'method_x'] = 'InfOnly'
        params.loc[i, 'auroc'] = AUROC
        params.loc[i, 'aupr'] = AUPR

        print("Combined...")
        AUROC, AUPR, _, _ = get_accuracy_realData(network=network,
                                        predFile=fileName + '::Combined', visualize=False)
        params.loc[lastIndex] = params.loc[i]
        params.loc[lastIndex, 'method_x'] = 'Combined'
        params.loc[lastIndex, 'auroc'] = AUROC
        params.loc[lastIndex, 'aupr'] = AUPR
        lastIndex += 1

    if save:
        params.to_csv(paramsFile + '_score.tsv', sep='\t', index=False)

# -----------------------------------------------------------------

if __name__ == '__main__':

    # Test file
    pathToPred = ds.datasets['Root'].get_outFile() + \
               '_priorPerct100_weight0.01__scaled__Nov-17_19-40--50FeatureScaling::InfOnly'
    AUROC, AUPR, fpr, tpr = get_accuracy_realData(network='Root',
                                        predFile=pathToPred, visualize=True)
    print(fpr)
    print(tpr)
