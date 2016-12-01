# Authors: Doaa Altarawy


import numpy as np
from sklearn.utils.testing import assert_array_almost_equal
from sklearn.utils.testing import assert_almost_equal
from sklearn.utils.testing import assert_equal
from sklearn.utils.testing import assert_true
from sklearn.utils.testing import assert_greater
from sklearn.utils.testing import ignore_warnings
from sklearn.utils.testing import assert_array_equal
from netAnalysis.scoring.PR_ROC import get_accuracy_realData
from netAnalysis.utils.Datasets import datasets as ds

np.set_printoptions(formatter={'float': '{: 0.5f}'.format})



def test_overall_accuracy_Root():
    pathToPred = ds.datasets['Root'].get_outFile() + \
        '_priorPerct100_weight0.01__scaled_FeatureScaling::InfOnly'

    AUROC, AUPR, fpr, tpr = get_accuracy_realData(network='Root',
                                       predFile=pathToPred, visualize=False)
    assert_almost_equal(AUROC, 0.36)
    assert_almost_equal(AUPR, 0.85)

# -------------------------------------------------------------------

def test_overall_accuracy_Net1():
    pathToPred = ds.datasets['Net1'].get_outFile() + \
        '_priorPerct100_weight0.01__scaled_FeatureScaling::InfOnly'

    AUROC, AUPR, fpr, tpr = get_accuracy_realData(network='Net1',
                                       predFile=pathToPred, visualize=False)
    assert_almost_equal(AUROC, 0.41)
    assert_almost_equal(AUPR, 0.95)

# -------------------------------------------------------------------

def test_overall_accuracy_Net4():
    pathToPred = ds.datasets['Net4'].get_outFile() + \
        '_priorPerct100_weight0.01__scaled_FeatureScaling::InfOnly'

    AUROC, AUPR, fpr, tpr = get_accuracy_realData(network='Net4',
                                       predFile=pathToPred, visualize=False)
    assert_almost_equal(AUROC, 0.31)
    assert_almost_equal(AUPR, 0.75)

# -------------------------------------------------------------------
