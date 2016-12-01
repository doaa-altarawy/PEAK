__author__ == 'Doaa'

from __future__ import division, print_function
import numpy as np
import csv
from subprocess import call
import time
# from .utils.Datasets import Dataset
from utils import Datasets as ds
from utils.helpers import *
from utils.InOut import InOutUtil as IO
from sklearn.linear_model import ElasticNet, ElasticNetCV
# from sklearn.preprocessing import normalize

np.set_printoptions(precision=5, suppress=True, linewidth=1000)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Peak(object):
    """Peak: Predicting gene regulatory network from gene expression data
    with prior knowledge.

    Types of prior knowledge:
    ------------------------
    1- Noisy: use penaltyScaling option
    2- Reliable: use FeatureScaling option

    """

    # CLR code path constants:
    pathToScripts   = r'../BonneauLab/Pipeline_2012/scripts/'
    command         = r'Rscript ' + pathToScripts + 'runInf.R '
    args            = r' --inf_max_reg 30 ' \
                      r'--n_boots 1 ' \
                      r'--num_pred 10000 ' \
                      r'--num_processors 4 ' \
                      r'--path_to_scripts ' + pathToScripts
                      # r'--tau 15 ' \

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def __init__(self, dataset, maxPredictors=5, alpha=0.1, l1_ratio=0.6,
                 scaleX=True, halfLife=10, useCV=True, alphas=None,
                 verbose=False, fit_intercept=True, maxItr=500):
        """
        :param dataset: one of the predefined datasets in ds.datasets
        :param maxPredictors: number of max predictors per gene
        :param alpha: float or None
                      weight of the penalty term
        :param l1_ratio: balancing parameter between lasso and ridge
        :param scaleX: whether to scale X or not
        :param halfLife: half live of the mRNA
        :param useCV: whether to use cross validation to find alphas
        :param alphas: array or None
                    list of alphas to try in the CV
        :param verbose: if true, print more degubging data
        :param fit_intercept: thether to fit_indtercept in elastic net
        :param maxItr:  number of max iteration in elastic net
        """
        self.dataset = dataset
        self.X = []             # n_obser x n_TF
        self.Y = []             # n_obser x n_genes
        self.clr = []           # n_genes x n_TF
        self.tfNames = []       # n_TF
        self.geneNames = []     # n_genes
        self.geneToTFInx = []   # maps the index of TF in CLR to index in X, n_TF x1
        self.maxPredictors = maxPredictors
        self.alpha = alpha
        self.alphas = alphas    # alphas to try in elastic net CV
        self.l1_ratio = l1_ratio
        self.scaleX = scaleX
        self.halfLife = halfLife
        self.useCV = useCV
        self.verbose = verbose
        self.fit_intercept = fit_intercept
        self.maxItr = maxItr

        # Results
        self.predictors_   = []     # array of objects(arrays)
                                    # predictor id for each gene (var length)

        self.predict_coef_ = []     # same structure as predictors
                                    # coeff of each predictor
        self.scoreMatrix   = []     # n_genes x n_TF

        self.n_genes    = 0         # num of genes
        self.n_TF       = 0         # total possible predictors
        self.n_obser    = 0         # number of observations


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getMixedCLR(self, clrOnly=True):
        """Calls R code of Inferelator2012 to get mixedCRL and
        designe and response matrices

        To call Inferelator (CLR):
        --tau is: half-life / ln2
            # what is the maximum delta T to consider (in minutes)?
            # (if delta T is bigger than it will be treated as steady state)
            delT_max] = tau * 3
            delT_min = tau / 3


        :param clrOnly: (bool) call CLR only then exit
                        if False: continue and call Inferelator in the R code

        :return: saved files (in main.R):
            mixedCLRMatrixAll.csv
            mixedCLRMatrixTF.csv  (threshold = 0.5!)
            X_lars.csv  (TF only)
            Y_lars.csv
        """

        # Call R code to calc mixed CLR and save it in csv files
        data = self.dataset.getArguments(clrOnly=clrOnly)
        command = Peak.command + data + Peak.args +\
                    ' --tau ' + str(self.halfLife/ np.log(2))  # ==log_e(2)==ln(2)
        print(command)
        start = time.time()
        call(command, shell=True)
        # Inferelator_rpy.run_Inf_R(data + Inferelator.args)
        runTime = (time.time() - start) / 60.0
        print('Running Time = {:.2f} mins'.format(runTime))


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def readInputData(self, clrFile="mixedCLRMatrixAll.csv",
                      XFile="X_lars.csv", YFile="Y_lars.csv"):
        """Read saved files that contains CLR matricies: X, Y"""

        # read CRL matrix:
        # mat = np.genfromtxt(open(clrFile,"rb"), # or use TF ???
        #                     delimiter=" ", skip_header=1, dtype='|U20')
        mat = pd.read_csv(clrFile, sep=' ', index_col=0)
        mat.fillna(0, inplace=True)
        # print(mat)
        # self.clr = mat[:, 1:].astype(float)     # n_genes x n_TF
        self.clr = mat.as_matrix()

        #  Read design matrix
        # mat = np.genfromtxt(open(XFile,"rb"),
        #                     delimiter=" ", skip_header=1, dtype='|U20')

        mat = pd.read_csv(XFile, sep=' ', index_col=0)

        self.tfNames = mat.index.values

        self.X = mat.as_matrix()

        self.X = np.transpose(self.X)   # n_obser x n_TF

        # scale X
        if (self.scaleX):
            self.X /= self.X.std(axis=0)
        # center X
        #self.X -= self.X.mean(axis=0)

        # Read response
        mat = pd.read_csv(YFile, sep=' ', index_col=0)

        self.geneNames = mat.index.values

        self.Y = mat.as_matrix()

        self.Y = np.transpose(self.Y)   # n_obser x n_genes

        self.geneToTFInx = np.zeros(len(self.geneNames), dtype=int)

        # store mapping of index of Gene to TF index
        for i, tf in enumerate(self.tfNames):
            for j, gene in enumerate(self.geneNames):
                if (tf == gene):
                    self.geneToTFInx[j] = i
                    break

        print("Data: X: {} \tY: {}, CLR: {}"
              .format(self.X.shape, self.Y.shape, self.clr.shape))

        self.n_genes = len(self.geneNames)      # num of genes
        self.n_TF = len(self.tfNames)           # total possible predictors
        self.n_obser = self.Y.shape[0]          # number of observations



    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def predict_GRN(self, priorTFs=None, priorWeight=0.01, method='PenaltyScaling'):
        """Predict best regulators among the top P ones in mixedCLR matrix

            If weights is not None, use weights to scale features,
                then scale calculated coeff back
        :param
            method: PenaltyScaling : penalty scaling (MEN, Greenfield, 2013)
                    FeatureScaling : scale design matrix
        """

        n = len(self.geneNames)         # num of genes
        p = len(self.tfNames)           # total possible predictors
        m = self.Y.shape[0]             # number of observations
        nCV = int(min(10, np.floor(m/2)))    # number of cross-valid. (from Pipeline 2012)
        print("Total num of genes: {}, total TF: {}, # of Obser: {}"
              .format(n, p, m))

        X_p = np.zeros(n, dtype=object)     # for each gene, potential predictors
                                            # (possibly variable len per gene)
        predict_coef = np.zeros(n, dtype=object)    # final chosen predictors coef for each gene
        intercept = np.zeros(n, dtype=float)       # used to predict system's response to new perturbations

        ### Loop over all genes in Y
        for curGene in range(n):
            if (self.verbose):
                print("Predicting regulators of Gene num {}, {}\n"
                       "========================================\n"
                       .format(curGene, self.geneNames[curGene]))

            # Prior knowledge array if exist
            priorArr, priorArrGene = None, None
            if (priorTFs is not None and len(priorTFs[curGene]) != 0):
                priorArrGene = priorTFs[curGene]
                # map priorTFs indices from gene Indices to TF indices
                priorArr = self.geneToTFInx[priorArrGene]

            Y_curr = self.Y[:, curGene]
            X_p[curGene], X_curr = self.getOneGeneDesignMatrix_(curGene, priorArr)

            if (len(X_curr)==0): # no features, skip this gene
                predict_coef[curGene] = []
                continue

            #-- If method is FeatureScaling:
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # 1- Build the design matrix for curGene and scale prior features
            # 2- predict with usual Elasticnet
            # 3- rescale coeff back
            if (method == 'FeatureScaling'):
                # Add feature scaling #
                X_curr = self.scaleMatrix_(X_curr, X_p[curGene], priorArr, priorWeight)
                betas, intercept[curGene] = self.elasticNetRegNT(X_curr, Y_curr, nCV)
                # Because of feature scaling, coeff needs to be scaled back
                betas = self.scaleMatrix_(betas, X_p[curGene], priorArr, priorWeight)

            #-- If method is PenaltyScaling:
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # 1- Build the design matrix for curGene
            # 2- predict with weighted penalty Elasticnet
            elif (method == 'PenaltyScaling'):
                l1_weights = np.ones(X_p[curGene].shape[0])
                l1_weights = self.scaleMatrix_(l1_weights, X_p[curGene],
                                               priorArr, 1.0/priorWeight)
                betas, intercept[curGene] = self.elasticNetRegNT(X_curr,
                                                Y_curr, nCV, l1_weights)

            # for testing
            self.logBetas(X_p[curGene], priorArr, priorWeight, betas)

            #>>>>>> no threshold for now:
            # predict_coef[curGene] = self.applyThreshould(betas)  # Or:
            predict_coef[curGene] = betas

        #-- Print information:
        if (self.verbose):
            self.printInformation(n, intercept, X_p, predict_coef)

        #-- Output:
        self.predictors_ = X_p              # array of objects(arrays)
                                            # predictors for each gene

        self.predict_coef_ = predict_coef   # same structure as predictors
                                            # coeff of each predictor

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def logBetas(self, xp, priorArr, priorWeight, betas):
        """Print betas for testing"""

        if self.verbose:
            l1_weights = np.ones(xp.shape[0])
            l1_weights = self.scaleMatrix_(l1_weights, xp, priorArr, 1.0 / priorWeight)
            print('prior:')
            for pw in l1_weights:
                if pw < 1:
                    print('%.2f' % pw, '\t',)
                else:
                    print('-----', '\t',)
            print('')
            for b in betas:
                if np.abs(b) > 0.009:
                    print('%.2f' % b, '\t',)
                else:
                    print('-----', '\t',)
            print('\n====================================================')

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def getOneGeneDesignMatrix_(self, curGene, priorTFs=None):
        """Build the design matrix for gene curGene from the big table
        of pbservation X

        :return:
        X_p np list of potential regulators from CLR + prior knowledge
                (indices of X)
        """

        ## Get ind of top regulators of curGene from clr matrix,
        #   if 0 takes all pred
        # ind = np.argpartition(self.clr[curGene],
        #           self.maxPredictors)[-self.maxPredictors:] # not working!

        ind = np.argsort(self.clr[curGene])[::-1]
        if (self.maxPredictors > 0):       # take only maxPredictors predictors
            ind = ind[:self.maxPredictors]

        # remove from ind where the clr value is ~zero TODO: should be after prior?!
        nonZero = []
        for i in ind:
            # remove self regulator from ind:
            if self.geneNames[curGene] == self.tfNames[i]:
                continue
            if (self.clr[curGene][i] > 0.0001):
                nonZero.append(i)

        X_p = np.array(nonZero)

        # - Add prior regulators to the list of potential regulators X_p
        # - create a new copy of the ndarray since ndarray must be contiguous
        #   in memory
        if (priorTFs is not None):
            X_p = np.concatenate((X_p, priorTFs), axis=0)
            X_p = np.unique(X_p).astype(int)       # sorted and unique

        # Get a copy (advanced indexing) of self.X corresponding to
        #   the chosen regulators
        X_curr = self.X[:, X_p] if len(X_p)>0 else []

        # for missing genes, fill na with 0 ########### TODO
        X_curr = np.nan_to_num(X_curr)

        return X_p, X_curr


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def scaleMatrix_(self, matrix, columsTags, columnsToScale, weight):
        """Helper function to scale selected columns from a matrix
           by dividing them by weight.

            # Add feature scaling #
            # ~~~~~~~~~~~~~~~~~~~ #
            # - divide columns corresponding to prior knowledge by priorWeight
            # - columns in X_curr are in the same order as X_p
            # - Impl using a loop to avoid copying the whole X matrix to divide
            #   prior TF columns since priorTFs are the indices in self.X

        :param matrix:
        :param columsTags: tags (num) corresponding to each column in matrix
        :param columnsToScale: tags of columns that need to be scaled
        :param weight: the number used to scale the selected columns
        :return: the scaled matrix
        """

        if (columnsToScale is not None):
            for i, TF in enumerate(columsTags):
                if (TF in columnsToScale):
                    matrix[..., i] /= weight

        return matrix

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def elasticNetRegNT(self, X, Y, nCV, l1_weights=None):
        """Run elastic net with the given params

        :param X: design matrix
        :param Y: true labels
        :param nCV: number of CVs
        :param l1_weights: weights of the lasso term
        :return:
        """

        # very difficult to choose alpha, better use CV
        # enet = ElasticNet(alpha=self.alpha, l1_ratio=0.8, fit_intercept=False)
        # enet = ElasticNetCV(fit_intercept=False, cv=nCV)
        if (self.useCV):
            enet = ElasticNetCV(cv=nCV, max_iter=self.maxItr, l1_weights=l1_weights,
                                fit_intercept=self.fit_intercept,
                                alphas=self.alphas, l1_ratio=self.l1_ratio)
            enet.fit(X, Y)
            self.cv_alpha = enet.alpha_
        else:
            enet = ElasticNet(alpha=self.alpha, l1_ratio=self.l1_ratio,
                              max_iter=self.maxItr, l1_weights=l1_weights)
            enet.fit(X, Y)

        if self.verbose:
            print("Num of iter: %d"%enet.n_iter_)
        # print("Best alpha: {}, l1_ratio: {}"
        #       .format(enet.alpha_, enet.l1_ratio_))
        # print(enet.get_params())
        ## plot regulation path for testing
        # testReg.lassoElasticnetPaths(X, Y)

        return enet.coef_, enet.intercept_

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def applyThreshould(self, coef, threshold=0.0001):
        """Apply Cut off on betas to choose corresponding predictors"""

        predict_coef = np.zeros(coef.shape)
        i = 0
        for b in coef:
            val = 0
            if b < threshold: val = -1
            elif b > threshold: val = 1

            predict_coef[i] = val
            i += 1

        return predict_coef

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def getConbinedInfCLR_Scores(self):
        """A heuristic described in Mader et al., 2010
           Combines: self.predict_coef_ and self.clr
           and returns self.scoreMatrix[numOfGenes][numOfTF]
           totalScore = sqrt( s1^2 + s2^2)
        """

        print("Calculating combinted Peak and CLR..")
        nGenes = self.geneNames.size
        nTF = self.clr.shape[1]
        scoreMatrix = np.zeros((nGenes,nTF))

        # Get sorted lists of predictions
        clrList = self.getCLRPred_Scores()
        infList = self.getInfPred_Scores(saveNegative=False)

        # For every row in infList
        for i in range(infList.shape[0]):
            TF = infList[i, 0]
            gene = infList[i, 1]
            # print("{}- TF: {}\t gene: {}".format(i, TF, gene))

            if (i< clrList.shape[0]):
                score = clrList[i, 2]  # get the weight of the ith rank
            else:
                score = infList[i, 2]   ### TODO: Check what to do?
                print("##### Doesn't exsit in CLR???")
            scoreMatrix[gene,TF] += score**2
            # print("Score: {}".format(scoreMatrix[gene,TF]))

        # For every row in clrList
        for i in range(clrList.shape[0]):
            TF = clrList[i, 0]
            gene = clrList[i, 1]
            # print("{}- TF: {}\t gene: {}".format(i, TF, gene))

            score = clrList[i, 2]  # get the weight of the ith rank
            scoreMatrix[gene,TF] += score**2
            # print("Score: {}".format(scoreMatrix[gene,TF]))

        scoreMatrix = np.sqrt(scoreMatrix)
        scoreList = self.getPredListFromMatrix_(scoreMatrix)
        return clrList, infList, scoreList

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def getInfPred_Scores(self, saveNegative=True):
        """Get the list of the predictions of Peak from elastic net coef"""

        nGenes = self.geneNames.size
        nTF = self.clr.shape[1]
        result = np.zeros((nGenes*nTF, 3)) # from, to, weight

        c = 0
        for i in range(nGenes):
            # print("Curr Gene: ", self.geneNames[i])
            for pIndx,weight in zip(self.predictors_[i], self.predict_coef_[i]):
                if (weight > 0.0001 or weight < -0.0001):
                    w = np.round(weight, 4)
                    if (not saveNegative):
                        w = np.abs(w)
                    # print("{}\t{}".format(self.geneNames[pIndx], w))
                    result[c] = [pIndx, i, w]
                    c += 1

        # Sort the edges by the weight
        _, result = getSorted(result, descending=True, sortByCol=2)

        # delete empty rows
        for i in range(result.shape[0]):
            if (np.isclose(result[i, 0], 0)
                and np.isclose(result[i, 1], 0)
                and np.isclose(result[i, 2], 0)):
                break

        result = result[:i, :]

        return result

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def getCLRPred_Scores(self):
        """Get list of the predictions of CLR from self.clr"""

        return self.getPredListFromMatrix_(self.clr)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def getPredListFromMatrix_(self, matrix):
        """Get list of the prediction from a 2D pred matrix"""

        nGenes = matrix.shape[0]
        nTF = matrix.shape[1]
        result = np.zeros((nGenes*nTF, 3)) # from, to, weight

        c = 0
        for i in range(nGenes):
            # print("Curr Gene: ", self.geneNames[i])
            for j in range(nTF):
                # don't include self regulation
                if (self.geneNames[i] == self.tfNames[j]):
                    continue
                weight = matrix[i][j]
                if (weight > 0.0001 or weight < -0.0001):
                    w = np.round(weight, 4)
                    # print("{}\t{}".format(self.geneNames[j], w))
                    result[c] = [j, i, w]
                    c += 1

        # Sort the edges by the weight
        _, result = getSorted(result, descending=True, sortByCol=2)

        # delete empty rows
        for i in range(result.shape[0]):
            if (np.isclose(result[i, 0], 0) and np.isclose(result[i, 1], 0)):
                break

        result = result[:i, :]

        return result

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def printInformation(self, n, intercept, X_p, predict_coef):
        for i in range(n):
            print("Gene {}\nIntercept: {}".format(self.geneNames[i], intercept[i]))
            print("Predictors: ", self.tfNames[X_p[i]])
            print("CLRs: ", self.clr[i][X_p[i]])
            print("Coef: ", predict_coef[i])

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def scaleToMaxOne(self, result):
         # Scale ranking to have max 1s
        max = np.max(np.abs(result[:,2]))
        if (max != 0):
            result[:,2] /= max
        return result

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def savePredictions(self, result, name=''):
        """Save predicted interactions in a csv text file

        :param name: special tag to add to dataset filename
        :param result: nx3 matrix to save (from, to, weight)
        """

        fileName = self.dataset.pathToData + self.dataset.outFile() + name

        with open(fileName, 'wt') as outfile:
            writer = csv.writer(outfile, delimiter='\t')
            for i in range(result.shape[0]):
                # writer.writerow([self.geneNames[result[i, 0]],
                #                  self.geneNames[result[i, 1]],
                #                  result[i, 2]])
                # Changed to make index in tfNames
                writer.writerow([self.tfNames[result[i, 0]],
                                 self.geneNames[result[i, 1]],
                                 result[i, 2]])

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @staticmethod
    def convertToSize(data, size):
        """Copy small part of the large input data file"""

        exprFile = data.exprFile
        chipFile = data.chipFile
        path = data.pathToData
        Peak.getSmallData(path, exprFile, size)
        Peak.getSmallData(path, chipFile, size, True)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @staticmethod
    def getSmallData(path, exprFile, max_lines=0, isChip=False):
        """Generate a small dataset from the given expr file"""

        with open(path+exprFile, 'rU') as infile:
            # with open(path+exprFile.split('.')[0]+'_small.tsv', 'w') as outfile: # same as:
            with open(path+exprFile[:-4]+'_small.tsv', 'w') as outfile:
                reader = csv.reader(infile, delimiter="\t")
                writer = csv.writer(outfile, delimiter='\t')
                # Read header
                header = next(reader)
                numOfCol = len(header)
                writer.writerow(header)
                for line in reader:     # data rows
                    if (len(line)==0):  # skip empty lines
                        continue
                    # max num of lines in expr files, or skip expr# >max in chip file
                    if (isChip and int(line[0])<max_lines) or \
                            (not isChip and len(line)==numOfCol):
                        writer.writerow(line)
                    else:
                        print('line num {} is skipped'.format(reader.line_num))
                    # If max number of rows reached, break
                    if(not isChip and max_lines!=0 and reader.line_num==max_lines):
                        break

# =============================================================================
#                               Helper Functions
# =============================================================================

def chooseMaxN_test():
    """Get top k values in an array

    :return:
        indices of top k values NOT SORTED
    """

    a = np.random.rand(6)*10
    max = 3
    ind = np.argpartition(a, max)[-max:]
    print("a: ", a)
    print("ind of max: ", ind)
    print("max: ", a[ind])

    # Sort, reverse to descending, get top 3
    ind = a.argsort()[::-1][:3]
    print("ind of max: ", ind)
    print("max: ", a[ind])

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def getSorted(npArray, descending=True, sortByCol=0):
    """Sort a numpy array

    :param npArray: array to be sorted
    :param descending: is descending order
    :return:
        sortedIndx: The indices of the sorted elements
        sorted: The sorted array
    """

    # get the sorting indices (sort by sortByCol column)
    if (npArray.ndim ==1): # 1D array
        sortedIndx = npArray.argsort()
    else: # 2D array
        sortedIndx = npArray[:,sortByCol].argsort()
    if (descending):
        # reverse the array to make it descending order
        sortedIndx[:] = sortedIndx[::-1]

    # extract sorted arrays
    sorted = npArray[sortedIndx]

    return sortedIndx, sorted

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def testSort():
    a = np.array([[3, 'b'], [2, 'c'], [6, 'a']])
    print(a)
    print(a.dtype)
    # Sort by first column
    b = a[a[:,0].argsort()]
    print(b)
    # reverse array of u want descending order
    b[:] = b[::-1]
    print(b)

    result = np.zeros(2, dtype='U, U, float')
    print(result)
    result[1] = ('a', 'b', 3.3)
    print(result)

    # test getSorted
    print("Test getSorted")
    _, f = getSorted(a, descending=False)
    print(f)

# =============================================================================

