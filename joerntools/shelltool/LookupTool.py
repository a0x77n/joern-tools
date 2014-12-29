#!/usr/bin/env python2

import sys, os
from TraversalTool import TraversalTool

class LookupTool(TraversalTool):
    
    # @Override

    def __init__(self, DESCRIPTION):
        TraversalTool.__init__(self, DESCRIPTION)
        
        group = self.argParser.add_mutually_exclusive_group()

        group.add_argument('-c', '--complete',
                           action='store_true',
                           default=False,
                           help = """Output the complete node,
                           not just its ID.""")
        group.add_argument('-a', '--attributes',
                           nargs='+',
                           type=str,
                           help="""Attributes of interest""",
                           default = None)
        group.add_argument('--no-transformation',
                           action = 'store_true',
                           default = False,
                           help = """Raw output""")
                           
        group = self.argParser.add_mutually_exclusive_group()
        group.add_argument('-l', '--lucene-query',
                           action='store_true',
                           default=True,
                           help = """query is treated as a lucene query""")
        group.add_argument('-g', '--gremlin',
                           action='store_true',
                           default=False,
                           help = """query is a gremlin traversal as opposed
                           to a lucene query""")
        group.add_argument('-n', '--node-id',
                           action='store_true',
                           default=False,
                           help = """query is treated as a node id""")

        


    # @Override
    def queryFromLine(self, line):
        
        if self.args.no_transformation:
            return line
        
        if line.startswith('id:') or self.args.node_id:
            node_id = line.split(':')[-1]
            query = 'g.v(%s)' % (node_id)
        elif self.args.gremlin:
            query = line
        else:
            luceneQuery = line
            query = """queryNodeIndex('%s')""" % (luceneQuery)
        
        return self.addOutputTransformation(query)
        

    def addOutputTransformation(self, query):
        """
        Calculate the output transformation term based on command line
        options.
        """

        if self.args.complete:
            return query + '.transform{ [it.id, it]}'
        else:
            term = '.transform{{ [it.id, [{}]]}}'
            attr = ','.join(map(lambda x: 'it.{}'.format(x), self.args.attributes))
            term = term.format(attr)
            return query + term
    

    # @Override
    def outputResult(self, result):
        for r in result:
            self._outputRecord(r)

    
    def _outputRecord(self, record):
        
        if self.args.no_transformation:
            self.output(str(record))
            self.output('\n')
            return

        id, node = record
        
        if type(node) == list:
            keys = self.args.attributes
            keyValPairs = [(keys[i] + ':' + str(node[i])) for i in range(len(keys))]
        else:
            node = node.properties
            keys = [k for k in node]
            keyValPairs = [str(k) + ':' + str(node[k]) for k in keys]
            keyValPairs.sort()
        
        keyValPairs = [k.replace('\t', '') for k in keyValPairs]
        
        self.output(str(id))
        if keyValPairs:
            self.output('\t%s\n' % ('\t'.join(keyValPairs)))
        else:
            self.output('\n')

