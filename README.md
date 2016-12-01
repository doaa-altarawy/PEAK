# PEAK

PEAK: Integrating Curated and Noisy Prior Knowledge in Gene Regulatory Network Inference.

PEAK is a framework for predicting gene regulatory network from gene expression data
with different types of prior knowledge.

#### Types of prior knowledge:
  1. Noisy: use penaltyScaling option
  2. Reliable: use FeatureScaling option

####(Under development): <br>
A Web server to submit gene expression data and prior knowledge 
and to visualize the results will be available soon.


## Installation


### 1- Python requirements:

PEAK works in both Python 2.7+ and Python 3.4+

1- Install the following Python packages:

- scipy
- numpy
- matplotlib
- pandas

You can either use pip or anaconda:

```
pip install scipy numpy matplotlib pandas
```

2- build and intsall a modified version of scikit-learn<br>
https://github.com/doaa-altarawy/scikit-learn

Instructions on building scikit-learn can be found here<br>
http://scikit-learn.org/stable/developers/advanced_installation.html


### 2- R requirements:

Install packages:

 - inline
 - multicore
 - elasticnet
 - Matrix
 - corpcor
 - nnls
 - parallel
 
### Detailed instruction how to install R and its required packages:

1- On ubuntu, first install R:

  ```linux
  sudo apt-get update
  sudo apt-get install r-base
  sudo apt-get install r-base-dev
  ```

2- Next, install open the R shell:

  ```
  sudo R
  ```

Then in the R shell install packages:

  ```
  install.packages(c("inline"))
  install.packages(c("multicore"))
  install.packages(c("elasticnet"))
  install.packages(c("Matrix"))
  install.packages(c("corpcor"))
  install.packages(c("nnls"))
  install.packages(c("parallel"))
  ```

3- To install the multicore package
download it from:\
http://cran.r-project.org/src/contrib/Archive/multicore/

Then:

```
install.packages('/path/to/downloaded/multicore', repos = NULL, type="source")
```



