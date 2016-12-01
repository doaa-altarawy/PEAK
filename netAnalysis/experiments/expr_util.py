__author__ = 'doaa'

from netAnalysis.Peak import *
import numpy as np
import csv, datetime
from netAnalysis.utils import Datasets as ds
from netAnalysis.utils import helpers as hlp
from netAnalysis.utils import Datasets as ds
from netAnalysis.utils.config import *


def run_Peak_test(datasetName, params, alphas=None, runCLR=False):
    """Main test for Peak py using DREAM5 datasets"""

    params['fileName'] = "_priorPerct"+str(params['priorPercent'])+\
                        "_weight"+str(params['priorWeight'])+"_"
    if (params['scaleX']):
        params['fileName'] += '_scaled_'

    params['fileName'] += '_{0:%b}-{0:%d}_{0:%H}-{0:%M}--{0:%S}'\
                                .format(datetime.datetime.now())
    params['fileName'] += params['method']

    print('----- Dataset: {}----'.format(datasetName))
    print("Running Inference for params:", params)

    dataset = ds.datasets[datasetName]
    inf = Peak(dataset, maxPredictors=30, # use maxPredictors=0 to use all genes
                      halfLife=params['halfLife'],
                      scaleX=params['scaleX'],
                      alpha=params['alpha'],
                      l1_ratio=params['l1_ratio'],
                      useCV=params['isCV'],
                      alphas=alphas,
                      verbose=False,
                      maxItr=200,
                      fit_intercept=params['fit_intercept'])

    # read saved data
    if (not runCLR and datasetName in
            ['Net1', 'Net3_conn_final', 'Net4', 'Grene_all', 'Grene']):
        clr_data_path = get_pathToCLRData()
        inf.readInputData(clr_data_path+"/mixedCLRMatrixAll_"+str(datasetName)+".csv",
                          clr_data_path+"/X_lars_"+str(datasetName)+".csv",
                          clr_data_path+"/Y_lars_"+str(datasetName)+".csv")
    else:   # Run R code to calculate CLR, then read output
        inf.getMixedCLR(clrOnly=True)
        inf.readInputData()

    priorFile = params['priorFile'] if 'priorFile' in params else None
    pkEachGene = params['pkEachGene'] if 'pkEachGene' in params else None
    priorTFs = getTrueFalsePrior(dataset, inf.geneNames, inf.tfNames, params['priorPercent'],
                                    params['falsePriorRatio'], priorFile, pkEachGene)

    inf.predict_GRN(priorTFs, params['priorWeight'], method=params['method'])

    # Get combined predictions
    resultCLR, resultInf, resultComb = inf.getConbinedInfCLR_Scores()   # Inf + CLR

    resultComb = inf.scaleToMaxOne(resultComb)  # doesn't affect accuracy
    resultInf = inf.scaleToMaxOne(resultInf)
    resultCLR = inf.scaleToMaxOne(resultCLR)
    #print("Results:", resultInf)
    if (params['isCV']==1):
        params['alpha'] = inf.cv_alpha


    if (params['method'] == 'PenaltyScaling' and params['priorPercent']==0):
        inf.savePredictions(resultCLR, params['fileName']+"::CLROnly")

    inf.savePredictions(resultInf, params['fileName'] + "::InfOnly")
    inf.savePredictions(resultComb, params['fileName'] + "::Combined")

    return params['fileName'] + "::InfOnly"

    # # Map gene names to real names and save
    # # print('ResultInf', resultInf)
    # resultMap = pd.DataFrame(resultInf, columns=['From', 'To', 'Weight'])
    # # print ('results: ', resultMap)
    # resultMap.From = map(lambda x: inf.geneNames[x], resultMap.From)
    # resultMap.To = map(lambda x: inf.geneNames[x], resultMap.To)
    #
    # # print('old gene names: ', resultMap)
    # resultMap.From = hlp.mapGeneNames(resultMap.From, dataset)
    # resultMap.To = hlp.mapGeneNames(resultMap.To, dataset)
    #
    # print('After mapping: ', resultMap)
    #
    # resultMap.to_csv(dataset.pathToData + dataset.outFile() +
    #                     params['fileName']+"::InfOnly_realNames",
    #                     sep='\t', index=False)

# ----------------------------------------------------------------------------

def mapGeneNames(datasetName='', filename=''):

    dataset = ds.datasets[datasetName]
    network = pd.read_csv(filename, sep='\t', header=None)
    network[0] = hlp.mapGeneNames(network[0], dataset)
    network[1] = hlp.mapGeneNames(network[1], dataset)
    print (network)
    network.to_csv(filename + '_realNames', index=False, sep='\t', header=False)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def readPriorKnowledge(dataset, geneNames, priorPercent, priorFile, pkEachGene):
    """ Read prior knowledge from gold standard file
    and return percent of the perior equals to priorPercent

    :param dataset: dataset name, of type Dataset
    :param geneNames: list of gene names in the dataset
    :param priorPercent: percent of prior to return
    :param priorFile: if not None, read PK from that file
    :param pkEachGene : read PK percent for each target gene

    :returns priorTFs: adjacency list of genes with its TFs
            ex. (with TF3 is replaced with its index in geneNames
                G1: [TF3, TF4, TF8]
                G2: []
                G3: [TF4, TF5]
    """

    if (np.isclose(priorPercent, 0)):
        return None

    # read gold std (prior knowledge) graph
    if priorFile is None:
        goldStd = pd.read_csv(dataset.get_goldStd(), sep='\t', header=None)
    else:
        goldStd = pd.read_csv(priorFile, sep='\t', header=None)

    numOfPriorsToUse = int(goldStd.shape[0] * priorPercent / 100.0)
    priorTFs = {} # np.zeros(len(geneNames), dtype=object)  # Prior list for every gene
    geneNamesDF = pd.DataFrame(geneNames)

    if pkEachGene:
        # For all genes, get its TFs in priorTFs[gene] as a list
        for i, node in enumerate(geneNames):
            trueTFNames = goldStd[goldStd[1] == node][0].values
            trueTFIndices = geneNamesDF[geneNamesDF.isin(trueTFNames).values].index.values
            priorTFs[i] = trueTFIndices  # save TF index not its name

        # choose only priorPercent for each gene
        # print('TFs \t # True_TF \t #_of_PK_to_use \t to_use')
        # for i, geneList in enumerate(priorTFs):
        #     print(i, geneList)
        #     numOfPriorsToUse = int(len(geneList) * priorPercent / 100.0)
        #     print('{}\t{}\t{}\t{}'.format(geneList, len(geneList),
        #                       numOfPriorsToUse, priorTFs[i][:numOfPriorsToUse]))
        #     priorTFs[i] = priorTFs[i][:numOfPriorsToUse]
        for geneIndex in priorTFs: # for each key (geneIndex)
            geneList = priorTFs[geneIndex]
            numOfPriorsToUse = int(len(geneList) * priorPercent / 100.0)
            # print('{}\t{}\t{}\t{}'.format(geneList, len(geneList),
            #                     numOfPriorsToUse, priorTFs[geneIndex][:numOfPriorsToUse]))
            priorTFs[geneIndex] = priorTFs[geneIndex][:numOfPriorsToUse]

    else:

        goldStd = goldStd.iloc[:numOfPriorsToUse]

        # For all genes, get its TFs in priorTFs[gene] as a list
        for i, node in enumerate(geneNames):
            trueTFNames = goldStd[goldStd[1]== node][0].values
            trueTFIndices = geneNamesDF[geneNamesDF.isin(trueTFNames).values].index.values
            priorTFs[i] = trueTFIndices   # save TF index not its name

        print("numOfPriorsToUse Prior knowledge:", numOfPriorsToUse)

    return priorTFs

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def getTrueFalsePrior(dataset, geneNames, tfNames, truePriorPercent, falsePriorRatio,
                            priorFile=None, pkEachGene=False):
    """ Read prior knowledge from gold standard file
    and retuen true prior with percentage = truePriorPercent
    and false prior with ratio = falsePriorRatio

    :param dataset: dataset name, of type Dataset
    :param geneNames: list of gene names in the dataset
    :param truePriorPercent: percent of true prior to use
    :param falsePriorRatio: the ration of false prior, i.e.:
                true:false  =  1:falsePriorRatio
    :param priorFile: if not None, load prior knowledge from that file
    :param pkEachGene : read PK percent for each target gene

    :returns priorTFs: adjacency list of genes with its TFs
    """

    if (np.isclose(truePriorPercent, 0)):
        return None;

    # Read True prior interactions
    priorTFs = readPriorKnowledge(dataset, geneNames, truePriorPercent, priorFile, pkEachGene)
    allPriorTFs = readPriorKnowledge(dataset, geneNames, 100., priorFile, pkEachGene)

    numOfFalsePrior = int(len(allPriorTFs) * truePriorPercent / 100.0) * falsePriorRatio
    currentCount = 0

    # falsePrior = np.zeros(len(geneNames), dtype=object)  # Prior list for every gene
    # For all genes, get its TFs in priorTFs[gene] as a list
    while (currentCount < numOfFalsePrior):
        gene_idx = np.random.random_integers(0, len(geneNames)-1) # random gene index
        TF_name = np.random.choice(tfNames) # random TF name
        TF_idx = np.where(geneNames == TF_name)[0][0] # find index of that TF gene

        if (TF_idx in allPriorTFs[gene_idx]):
            print(gene_idx, TF_idx, 'already found as True interaction.')
            continue
        # Add false prior
        print("adding gene: {}, TF: {}".format(gene_idx, TF_idx))
        priorTFs[gene_idx] = np.append(priorTFs[gene_idx], TF_idx)
        currentCount += 1

    print("numOfFalsePrior Prior knowledge:", numOfFalsePrior)

    # merge true and false prior
    return priorTFs

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
