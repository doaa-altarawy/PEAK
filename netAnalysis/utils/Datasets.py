__author__ = 'doaa'

from . import config as config

class Dataset():
    """PEAK predefined test dataset class"""


    def __init__(self, pathToData, dsName, exprFile, TF_File, chipFile,
                        goldStd, outFile='', geneNamesFile=''):
        self.dsName = dsName
        self.pathToData = pathToData
        self.exprFile = exprFile
        self.TF_File = TF_File
        self.chipFile = chipFile
        self.goldStd = goldStd
        self._outFile = outFile
        self.geneNamesFile = geneNamesFile

    def get_exprFile(self):
        return self.pathToData + self.exprFile

    def get_goldStd(self):
        return self.pathToData + self.goldStd

    def get_outFile(self):
        return self.pathToData + self.outFile()


    def getArguments(self, clrOnly=True):
        string = r'--data_file ' + self.pathToData + self.exprFile + \
                    r' --meta_file ' + self.pathToData + self.chipFile

        # Assume no TFs, get all
        if (self.TF_File != ''):
            string += r' --reg_file ' + self.pathToData + self.TF_File

        # Call CLR then stop execution, don't run Inferelator
        if (clrOnly):
            string += r' --clr_then_stop 1 '
        else:
            string += r' --clr_then_stop 0 '

        return string

    def outFile(self, methodName=None):
        method = predictMethod.get(methodName)
        print(method)
        filename = self._outFile
        if (method is None): # use default name
            pass #filename = filename + "_" +defaultMethod
        else:
            filename = filename + "_" + method

        return filename

    @staticmethod
    def getDREAM5_datasets():
        return DREAM5_datasets

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Different network inference methods
predictMethod = {"CLR": "clrOnly", "Inferelator Python": "InfCLR_py",
                 "Inferelator R": "??", "Regression": "Regression1"}
defaultMethod = 'InfCLR_py'

pathToData = config.get_pathToData()

datasets = dict()
datasets['Grene'] = Dataset(pathToData + 'Arabidopsis/grene/processed/',
                           'Grene',
                           'genes_WT.fpkm_tracking_AGI_Description.tsv',
                           'arab_transcription_factors.tsv',
                           'arab_chip_features.tsv',
                           'true_edge.txt',
                           'output/NetworkInference_grene',
                           'arab_gene_ids.tsv')

datasets['Root'] = Dataset(pathToData + 'Roots_li/processed/',
                            'Root',
                            '102715_ave.FPKM.pro.tsv',
                            'root_transcription_factors.tsv',
                            'root_chip_features.tsv',
                            # 'true_edge.txt',
                            'paper_figure_table_original_mapped.csv',
                            'output/NetworkInference_root',
                            'root_gene_ids.tsv')

datasets['Net1'] = Dataset(pathToData+'DREAM5/Network1/',
                    'Network1',
                    'net1_expression_data.tsv',
                    'net1_transcription_factors.tsv',
                    'net1_chip_features.tsv',
                    'gold_standard/net1_gold_standard.tsv',
                    'output/NetworkInference_Network1',
                    'anonymization/net1_gene_ids.tsv')


datasets['Net1_small'] = Dataset(pathToData+'DREAM5/Network1/',
                        'Network1_small',
                        'net1_expression_data_small.tsv',
                        'net1_transcription_factors.tsv',
                        'net1_chip_features_small.tsv',
                        'gold_standard/net1_gold_standard.tsv',
                        'output/NetworkInference_Network1_small',
                        'anonymization/net1_gene_ids.tsv')


datasets['Net3'] = Dataset(pathToData+'DREAM5/Network3/',
                    'Network3',
                    'net3_expression_data.tsv',
                    'net3_transcription_factors.tsv',
                    'net3_chip_features.tsv',
                    'gold_standard/net3_gold_standard.tsv',
                    'output/NetworkInference_Network3',
                    'anonymization/net3_gene_ids.tsv')


datasets['Net3_conn_final'] = Dataset(pathToData + 'DREAM5/Network3_connected/',
                           'Net3_conn_final',
                           'net3_expression_data.tsv',
                           'net3_transcription_factors.tsv',
                           'net3_chip_features.tsv',
                           'gold_standard/net3_gold_standard.tsv',
                           'output/NetworkInference_Network3',
                            'anonymization/net3_gene_ids.tsv')

datasets['Net4'] = Dataset(pathToData+'DREAM5/Network4/',
                    'Network4',
                    'net4_expression_data.tsv',
                    'net4_transcription_factors.tsv',
                    'net4_chip_features.tsv',
                    'gold_standard/net4_gold_standard.tsv',
                    'output/NetworkInference_Network4',
                    'anonymization/net4_gene_ids.tsv')


datasets['Subgraph1'] = Dataset(pathToData+'DREAM5/Subgraphs/',
                    'Subgraph1',
                    'net1_sub1_expression_data.tsv',
                    '',
                    'net1_chip_features.tsv',
                    'net1_sub1.tsv',
                    'output/NetworkInference_Network1_sub1',
                    'anonymization/net1_gene_ids.tsv')

# getSubGraph(node='128')
datasets['Subgraph2'] = Dataset(pathToData+'DREAM5/Subgraphs/',
                    'Subgraph2',
                    'net1_sub2_expression_data.tsv',
                    '',
                    'net1_chip_features.tsv',
                    'net1_sub2.tsv',
                    'output/NetworkInference_Network1_sub2',
                    'anonymization/net1_gene_ids.tsv')

datasets['Subgraph3'] = Dataset(pathToData+'DREAM5/Subgraphs/',
                    'Subgraph3',
                    'net1_sub3_expression_data.tsv',
                    '',
                    'net1_chip_features.tsv',
                    'net1_sub3.tsv',
                    'output/NetworkInference_Network1_sub3',
                    'anonymization/net1_gene_ids.tsv')

datasets['Subgraph4'] = Dataset(pathToData+'DREAM5/Subgraphs/',
                    'Subgraph4',
                    'net1_sub4_expression_data.tsv',
                    '',
                    'net1_chip_features.tsv',
                    'net1_sub4.tsv',
                    'output/NetworkInference_Network1_sub4',
                    'anonymization/net1_gene_ids.tsv')

DREAM5_datasets = list(datasets.keys()) 


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def runTest():
    print(datasets['Net1'].getOutputFile())
    print(datasets['Net1'].getOutputFile("CLR"))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == "__main__":
    runTest()
