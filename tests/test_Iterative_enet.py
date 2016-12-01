# Authors: Doaa Altarawy


import numpy as np
from sklearn.utils.testing import assert_array_almost_equal
from sklearn.utils.testing import assert_almost_equal
from sklearn.utils.testing import assert_equal
from sklearn.utils.testing import assert_true
from sklearn.utils.testing import assert_greater
from sklearn.utils.testing import ignore_warnings
from sklearn.utils.testing import assert_array_equal

from sklearn.linear_model.coordinate_descent import ElasticNet, \
                    ElasticNetCV, lasso_path, enet_path
import matplotlib.pyplot as plt

from sklearn.metrics import r2_score
from sklearn import datasets



np.set_printoptions(formatter={'float': '{: 0.5f}'.format})



def test_enet_small():
    """Toy tests with generated X and Y"""

    # TODO: add \theta prior knowledge here and test the output

    X = np.array([[-1.], [0.], [1.]])
    Y = [-1, 0, 1]          # a straight line
    T = [[2.], [3.], [4.]]  # test sample

    # this should be the same as lasso
    clf = ElasticNet(alpha=1e-8, l1_ratio=1.0)
    clf.fit(X, Y)
    pred = clf.predict(T)
    assert_array_almost_equal(clf.coef_, [1])
    assert_array_almost_equal(pred, [2, 3, 4])
    assert_almost_equal(clf.dual_gap_, 0)

    clf = ElasticNet(alpha=0.5, l1_ratio=0.3, max_iter=100,
                     precompute=False)
    clf.fit(X, Y)
    pred = clf.predict(T)
    assert_array_almost_equal(clf.coef_, [0.50819], decimal=3)
    assert_array_almost_equal(pred, [1.0163, 1.5245, 2.0327], decimal=3)
    assert_almost_equal(clf.dual_gap_, 0)

    clf.set_params(max_iter=100, precompute=True)
    clf.fit(X, Y)  # with Gram
    pred = clf.predict(T)
    assert_array_almost_equal(clf.coef_, [0.50819], decimal=3)
    assert_array_almost_equal(pred, [1.0163, 1.5245, 2.0327], decimal=3)
    assert_almost_equal(clf.dual_gap_, 0)

    clf.set_params(max_iter=100, precompute=np.dot(X.T, X))
    clf.fit(X, Y)  # with Gram
    pred = clf.predict(T)
    assert_array_almost_equal(clf.coef_, [0.50819], decimal=3)
    assert_array_almost_equal(pred, [1.0163, 1.5245, 2.0327], decimal=3)
    assert_almost_equal(clf.dual_gap_, 0)

    clf = ElasticNet(alpha=0.5, l1_ratio=0.5)
    clf.fit(X, Y)
    pred = clf.predict(T)
    assert_array_almost_equal(clf.coef_, [0.45454], 3)
    assert_array_almost_equal(pred, [0.9090, 1.3636, 1.8181], 3)
    assert_almost_equal(clf.dual_gap_, 0)

# -----------------------------------------------------------------------------

def test_ElasticnetWeights():
    """Test elastic net with different weight for each predictor
    alpha: a vector of weight, small # means prior knowledge
            1 : means no prior knowledge
    """

    # Has 10 features
    diabetes = datasets.load_diabetes()
    # pprint(diabetes)
    print("Size of data:{}".format(diabetes.data.shape))
    X = diabetes.data
    y = diabetes.target

    X /= X.std(axis=0)  # Standardize data (easier to set the l1_ratio parameter)

    eps = 5e-3   # the smaller it is the longer is the path
    alphas = np.arange(2, 4, 0.2)
    alphas = np.append(alphas, 2.27889) # best aplpha from cv

    # Computing regularization path using the lasso
    alphas_lasso, coefs_lasso, _ = lasso_path(X, y, eps, fit_intercept=False,
                                              alphas=alphas)

    # Computing regularization path using the elastic net
    alphas_enet, coefs_enet, _ = enet_path(
        X, y, eps=eps, l1_ratio=0.8, fit_intercept=False, alphas=alphas)


    # ElasticnetCV
    num_predict = X.shape[1]
    alphas = np.zeros(num_predict)
    alphas.fill(1)
    val = 0.1
    alphas[2] = val
    alphas[3] = val
    alphas[6] = val
    enetCV_alpha, enetCV_coef = runPrintResults(X,y, None, "EnetCV")
    runPrintResults(X,y, alphas, "EnetCVWeight 1")

    # print("coefs_enet: {}".format(coefs_enet[:, -1]))
    # print("coefs_lasso: {}".format(coefs_lasso[:, -1]))

    # Display results
    plt.figure(1)
    ax = plt.gca()
    ax.set_color_cycle(2 * ['b', 'r', 'g', 'c', 'k'])
    l1 = plt.plot(alphas_lasso, coefs_lasso.T)
    l2 = plt.plot(alphas_enet, coefs_enet.T, linestyle='--')

    # repeat alpha for x-axis values for plotting
    enetCV_alphaVect = [enetCV_alpha] * num_predict
    l3 = plt.scatter(enetCV_alphaVect, enetCV_coef, marker='x')

    plt.xlabel('alpha')
    plt.ylabel('coefficients')
    plt.title('Lasso and Elastic-Net Paths')
    plt.legend((l1[-1], l2[-1]), ('Lasso', 'Elastic-Net'),
                loc='upper right')
    plt.axis('tight')
    plt.savefig("fig/lassoEnet")

# -----------------------------------------------------------------------------

def runPrintResults(X, y, alpha, name):

    print(name+":\n=========")

    if (alpha is not None):
        X_new = np.divide(X, alpha)
    else:
        X_new = X

    enetCV = ElasticNetCV(l1_ratio=0.8, fit_intercept=False) # cv=nCV, max_iter=5000
    # enetCV = LassoCV(fit_intercept=False) # cv=nCV, max_iter=5000

    enetCV.fit(X_new, y)
    y_pred_enet = enetCV.predict(X_new)
    r2_score_enet = r2_score(y, y_pred_enet)
    print("R2= ", r2_score_enet)


    if (alpha is not None):
        enetCV_coef = np.divide(enetCV.coef_, alpha)
    else:
        enetCV_coef = enetCV.coef_

    print("Best Alpha: {}".format(enetCV.alpha_))
    # print("coefs_: {}".format(enetCV.coef_))
    print("coefs_/alpha: {}".format(enetCV_coef))

    return enetCV.alpha_, enetCV_coef

# -----------------------------------------------------------------------------

def build_dataset(n_samples=50, n_features=200, n_informative_features=10,
                  n_targets=1):
    """
    build an ill-posed linear regression problem with many noisy features and
    comparatively few samples
    """
    random_state = np.random.RandomState(0)
    if n_targets > 1:
        w = random_state.randn(n_features, n_targets)
    else:
        w = random_state.randn(n_features)
    w[n_informative_features:] = 0.0
    X = random_state.randn(n_samples, n_features)
    y = np.dot(X, w)
    X_test = random_state.randn(n_samples, n_features)
    y_test = np.dot(X_test, w)
    return X, y, X_test, y_test


