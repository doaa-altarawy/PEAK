__author__ = 'doaa'

from enum import Enum
import pandas as pd


class Methods(Enum):
     penaltyScaling = 'PenaltyScaling'
     featureScaling = 'FeatureScaling'


def mapGeneNames(oldList, dataset):
    """Find a list of the corresponding actual gene names
        ordered by the dataframe order
    """

    realNames = pd.read_csv(dataset.pathToData+ dataset.geneNamesFile, sep='\t')

    # Map gene names preserving order
    newList = map(lambda x: realNames[realNames['#ID'] == x]['Name'].values[0], oldList)

    return newList

