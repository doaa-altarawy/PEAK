__author__ = 'doaa'

from netAnalysis.experiments.expr_util import *


def batteryTests(datasetName, priorFile=None):
    """
        Run battery tests and save parameters in a file, and predictions
        each in a file with cross-ref name in the param file.
    :return:
    """

    print("pathToData: ", ds.pathToData)

    alphas = [0.001, 0.01, 0.1, 0.2, 0.6, 0.8, 2]
    l1_ratio_best = 0.5
    params = OrderedDict([('fileName', ''), ('priorPercent', 0), ('priorWeight', 0.01),
                ('alpha', 0.1), ('l1_ratio',0.5), ('isCV',0), ('fit_intercept', 1),
                ('scaleX',1), ('halfLife',10), ('method',''), ('freeCV', 0),
                         ('falsePriorRatio', 0), ('priorFile', priorFile)])

    paramFileName = "paramsLog/paramFile_" + datasetName + \
                    '_{0:%Y}-{0:%b}-{0:%d}_{0:%H}-{0:%M}'.format(datetime.datetime.now()) + ".tsv"
    print(paramFileName)

    with open(paramFileName, 'w', buffering=1) as fp:
        paramFile = csv.writer(fp, delimiter='\t')
        paramFile.writerow(list(params.keys()))

        # Fixed parameters
        params['halfLife'] = 10         # Dataset dependent
        params['scaleX'] = 1
        params['fit_intercept'] = 1     # the same if data is centered like net1


        # CV = 1
        params['isCV'] = 1
        params['l1_ratio'] = l1_ratio_best
        params['freeCV'] = 0
        #-- Run Inference
        priorWeightTest(datasetName, paramFile, params, penaltyScaling=False)
        params['freeCV'] = 1
        #-- Run Inference
        priorWeightTest(datasetName, paramFile, params, featureScaling=False)

        CV = 0
        params['isCV'] = 0
        for alpha in alphas:
            for l1_ratio in [.5,]: #[0.4, 0.5, 0.6, 0.7, 0.9]:
                params['alpha'] = alpha
                params['l1_ratio'] = l1_ratio
                # Run Inference
                priorWeightTest(datasetName, paramFile, params)


        return paramFileName

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def testFalsePrior(datasetName):
    """
        Test PEAK with false Prior Knowledge
    :param datasetName:
    :return:
    """
    print("pathToData: ", ds.pathToData)

    params = OrderedDict([('fileName', ''), ('priorPercent', 1), ('priorWeight', 0.01),
                          ('alpha', 0.1), ('l1_ratio', 0.5), ('isCV', 1), ('fit_intercept', 1),
                          ('scaleX', 1), ('halfLife', 10), ('method', ''), ('freeCV', 0),
                          ('falsePriorRatio', 0)])

    paramFileName = "paramsLog/paramFile_" + datasetName + \
                    '_{0:%Y}-{0:%b}-{0:%d}_{0:%H}-{0:%M}'.format(datetime.datetime.now()) + ".tsv"
    print(paramFileName)

    with open(paramFileName, 'w', buffering=1) as fp:
        paramFile = csv.writer(fp, delimiter='\t')
        paramFile.writerow(list(params.keys()))


        for falsePriorRatio in [0, 1, 2, 5, 10]:
            params['falsePriorRatio'] = falsePriorRatio

            params['freeCV'] = 0
            # -- Run featureScaling
            priorWeightTest(datasetName, paramFile, params, penaltyScaling=False)
            params['freeCV'] = 1
            # -- Run penaltyScaling
            priorWeightTest(datasetName, paramFile, params, featureScaling=False)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def priorWeightTest(datasetName, paramFile, params, featureScaling=True, penaltyScaling=True):
    """
        Run PEAK with different prior weight and prior percent values
    :param datasetName:
    :param paramFile:
    :param params:
    :param featureScaling:
    :param penaltyScaling:
    :return:
    """

    priorWeightList = [0.01] #[0.001, 0.01, 0.1, 0.2, 0.5, 0.8]
    priorPrecentList = [0, 50, 100] #[0, 10, 20, 40, 60, 80, 100]
    alphas_small = [0.001, 0.01, 0.05, 0.1]
    alphas_large = [0.1, 0.2, 0.4, 0.6, 0.8, 1, 2, 3]

    for priorPrecent in priorPrecentList:
        for priorWeight in priorWeightList:
            params['priorPercent'] = priorPrecent
            params['priorWeight'] = priorWeight
            # Run Inference
            if penaltyScaling:
                params['method'] = 'PenaltyScaling'
                if (params['freeCV']):
                    run_Peak_test(datasetName, params)
                else:
                    run_Peak_test(datasetName, params, alphas_large)
                paramFile.writerow(list(params.values()))

            if featureScaling:
                params['method'] = 'FeatureScaling'
                if (params['freeCV']):
                    run_Peak_test(datasetName, params)
                else:
                    run_Peak_test(datasetName, params, alphas_small)
                paramFile.writerow(list(params.values()))

            if (priorPrecent == 0):
                break


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def testFalseTruePrior():
    """
        Small test for false+true prior knowledge
    :return:
    """
    datasetName = 'Net3_conn_final' #['Net1', 'Net3_conn_final', 'Net4']
    dataset = ds.datasets[datasetName]
    inf = Peak(dataset, maxPredictors=30,
               halfLife=10,
               scaleX=True,
               alpha=0.1,
               l1_ratio=0.5,
               useCV=False,
               alphas=None,
               verbose=False,
               maxItr=200,
               fit_intercept=True)

    clr_data_path = get_pathToCLRData()
    inf.readInputData(clr_data_path + "/mixedCLRMatrixAll_" + str(datasetName) + ".csv",
                          clr_data_path + "/X_lars_" + str(datasetName) + ".csv",
                          clr_data_path + "/Y_lars_" + str(datasetName) + ".csv")


    # All true
    # priorTFs = readPriorKnowledge(dataset, inf.geneNames, 100)
    #
    # for i in priorTFs:
    #     print(i)

    # true:false  =  1:1
    priorTFs = getTrueFalsePrior(dataset, inf.geneNames, inf.tfNames, 100, 1)

    for i in priorTFs:
        print(i)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == "__main__":

    # Get small data set
    # data = ds.datasets['Net1']
    # Peak.convertToSize(data, 30)
    datasetName = 'Root' #'Net1', 'Net3_conn_final', 'Net4', 'Grene'


    alphas_small = [0.001, 0.01, 0.05, 0.1]
    alphas_large = [0.1, 0.2, 0.4, 0.6, 0.8, 1, 2, 3]

    params = OrderedDict([('fileName', ''), ('priorPercent', 100), ('falsePriorRatio', 0),
                          ('priorWeight', 0.01),
                          ('alpha', 0.1), ('l1_ratio', 0.5), ('isCV', 1), ('fit_intercept', 1),
                          ('scaleX', 1), ('halfLife', 10), ('method', 'FeatureScaling'), ('freeCV', 0)])

    # params = OrderedDict([('fileName', ''), ('priorPercent', 100), ('falsePriorRatio', 0),
    #                       ('priorWeight', 0.01),
    #                       ('alpha', 0.1), ('l1_ratio', 0.5), ('isCV', 1), ('fit_intercept', 1),
    #                       ('scaleX', 1), ('halfLife', 10), ('method', 'PenaltyScaling'), ('freeCV', 1)])


    paramsFileName = batteryTests(datasetName, priorFile='data/Roots_li/processed/PK_file.csv')
    test_data(network='Root', paramsFile=paramsFileName, save=True)


    # === Paper 1!
    # testFalseTruePrior()
    # testFalsePrior('Net1')
    # testFalsePrior('Net3_conn_final')
    # testFalsePrior('Net4')

    # dataset = ds.datasets['Net3_conn_final']
    # filename = dataset.pathToData + dataset.goldStd
    # mapGeneNames(dataset=dataset, filename)














