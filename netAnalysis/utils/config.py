__author__ = 'doaa'

import yaml
import os

config = None
projectPath = None

def getConfig():
    """Load config file"""
    global config
    global projectPath
    if (config == None):
        print(os.getcwd())
        currPath = os.path.dirname(os.path.realpath(__file__))
        # print(currPath)
        f = open(currPath +'/config.yaml')
        config = yaml.safe_load(f)
        f.close()
        projectPath = currPath.split('DeTangle/DeTangle')[0] + 'DeTangle/DeTangle/'
        #print(projectPath)

    return config

getConfig()

def get_pathToData():
    return projectPath + config['data']['pathToData']

def get_pathToOutput():
    return projectPath + config['data']['pathToOut']

def get_pathToCLRData():
    return projectPath + config['data']['pathToCLRData']
