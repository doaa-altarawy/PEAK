"""
Utility functions to read and write different finds of files
such as:
    - Gene expression files
    - Graphs files (g1, g2, weight, others, ..)
"""

import csv
import logging
from .graph import Graph
import json
from . import Datasets as Datasets

log = logging.getLogger(__name__)


class InOutUtil:    # TODO: remove the class, no need

    def __init__(self):
        pass

    @staticmethod
    def readGraphFileAsJSON1(fileName, maxLines=float("inf"), sep='\t', startLine=0, geneID=''):
        graph = InOutUtil.readGraph(fileName, maxLines, sep, startLine, geneID)
        return json.dumps(graph.getLinks())

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def readGraph(fileName, maxLines=float("inf"), sep='\t', startLine=0,
                  geneID='', skipHeader=True):
        """
        Read graph from cvs file using simple impl of a graph
        :param fileName:
        :param maxLines:
        :param sep:
        :param startLine:
        :param geneID:
        :return:
        """
        log.info("Read Graph function, geneID= {}".format(geneID))
        graph = Graph()
        with open(fileName, 'rU') as tsvfile:
            reader = csv.reader(tsvfile, delimiter=sep)
            # Read header
            if (skipHeader):
                header = next(reader)
            for line in reader:
                if geneID=='' and reader.line_num < startLine: # skip first 'startLine'
                    continue
                if geneID=='' and reader.line_num > (startLine + maxLines):
                    break     # max number of lines reached
                if len(line) != 0:  # Line is not empty
                    if (line[2] == '+'): w = '100'        # + equivalent to weight 1
                    elif (line[2] == '-'): w = '-100'     # - equivalent to weight -1
                    else: w = line[2]
                    if (geneID=='' or line[0]==geneID or line[1]==geneID):
                        graph.addLink(line[0], line[1], w)
        return graph

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def getNumberOfRecords(fileName):
        """
            Get number of rows (records) in a file.
        :param fileName:
        :return: number of rows
        """
        with open(fileName, 'rU') as file:
            reader = csv.reader(file)
            count = sum(1 for _ in reader)
        return count
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def readGraphFileAsJSON(fileName, maxLines=float("inf"), sep='\t', startLine=0):
        """
        Read graph from cvs using NextworkX
        :param fileName:
        :param maxLines:
        :param sep:
        :param startLine:
        :return:
        """
        # Import here, nextworkx is not working with wsgi+apache
        import networkx as nx
        from networkx.readwrite import json_graph

        graph = nx.DiGraph()
        with open(fileName, 'rU') as tsvfile:
            reader = csv.reader(tsvfile, delimiter=sep)
            # Read header
            header = next(reader)
            for line in reader:
                if reader.line_num < startLine:   # skip first 'startLine'
                    continue
                if reader.line_num > (startLine + maxLines):
                    break     # max number of lines reached
                if len(line) != 0:  # Line is not empty
                    if (line[2] == '+'): w = '100'        # + equivalent to weight 1
                    elif (line[2] == '-'): w = '-100'     # - equivalent to weight -1
                    else: w = line[2]
                    graph.add_edge(line[0], line[1], weight=w)

        # convert graph to:
        #       nodes[name, group] and links[source -> target] JSON lists
        data = json_graph.node_link_data(graph)
        return json.dumps(data)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def convertTSV(exprFile, max_lines=0, isChip=False):
        with open(Datasets.pathToData+exprFile, 'rU') as infile:
            with open(Datasets.pathToData+exprFile[:-4]+'_small.tsv', 'w') as outfile:
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

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def convertToSize(size):
        """
        Copy small part of the large input data file
        :return:
        """
        exprFile = 'Network1_small/net1_expression_data.tsv'
        chipFile = 'Network1_small/net1_chip_features.tsv'
        InOutUtil.convertTSV(exprFile, size)
        InOutUtil.convertTSV(chipFile, size, True)

