"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: Apache-2.0
"""

import json
import logging
import collections

from graph_notebook.network.EventfulNetwork import EventfulNetwork
from networkx import MultiDiGraph

logging.basicConfig()
logger = logging.getLogger(__file__)

DEFAULT_LABEL_MAX_LENGTH = 10
ENTITY_KEY="~entityType"
ID_KEY="~id"
START_KEY="~start"
END_KEY="~end"
PROPERTIES_KEY="~properties"
TYPE_KEY="~type"
LABEL_KEY="~labels"
NODE_ENTITY_TYPE='node'
REL_ENTITY_TYPE='relationship'

class OCNetwork(EventfulNetwork):
    """OCNetwork extends the EventfulNetwork class and uses the add_results method to parse any response that returns nodes/relationships 
    as part (or all) of the response.  Currently this only works with HTTPS response format but in the future, we will work to 
    support Bolt based responses as well.
    """

    def __init__(self, graph: MultiDiGraph = None, callbacks=None, label_max_length=DEFAULT_LABEL_MAX_LENGTH,
                 group_by_property=LABEL_KEY, ignore_groups=False):
        if graph is None:
            graph = MultiDiGraph()
        self.label_max_length = label_max_length
        try:
            self.group_by_property = json.loads(group_by_property)
        except ValueError:
            self.group_by_property = group_by_property
        self.ignore_groups = ignore_groups
        super().__init__(graph, callbacks)
    
    def flatten(self, d:dict, parent_key='', sep='_') -> dict:
        """Flattens dictionaries including nested dictionaties

        Args:
            d (dict): The dictionary to flatten
            parent_key (str, optional): The parent key name to append. Defaults to ''.
            sep (str, optional): The seperator between the parent and sub key. Defaults to '_'.

        Returns:
            [dict]: The flattened dictionary
        """
        items = []
        for k, v in d.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, collections.MutableMapping):
                items.extend(self.flatten(v).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def parse_node(self, node:dict):
        """This parses the node parameter and adds the node to the network diagram

        Args:
            node (dict): The node dictionary to parse
        """
        if LABEL_KEY in node.keys():
            title = node[LABEL_KEY][0]
        else:
            for key in node:
                title += str(node[key])
            label = title if len(title) <= self.label_max_length else title[:self.label_max_length - 3] + '...'
            
        label = title if len(title) <= self.label_max_length else title[:self.label_max_length - 3] + '...'
        if not isinstance(self.group_by_property, dict):  # Handle string format group_by
            if self.group_by_property in [LABEL_KEY, 'labels'] and len(node[LABEL_KEY])>0:
                group = node[LABEL_KEY][0]
            elif self.group_by_property in [ID_KEY, 'id']:
                group = node[ID_KEY]
            elif self.group_by_property in node[PROPERTIES_KEY]:
                group=node[PROPERTIES_KEY][self.group_by_property]
            else:
                group = ''
        else:  # handle dict format group_by
            try:
                if str(node[LABEL_KEY][0]) in self.group_by_property and len(node[LABEL_KEY])>0:
                    key=node[LABEL_KEY][0]
                    if self.group_by_property[key]['groupby'] in [LABEL_KEY, 'labels']:
                        group = node[LABEL_KEY][0]
                    else:
                        group = node[PROPERTIES_KEY][self.group_by_property[key]['groupby']]
                elif ID_KEY in self.group_by_property:
                    group = node[ID_KEY]
                else:
                    group = ''
            except KeyError:
                group = ''

        if title == '':
            for key in node[PROPERTIES_KEY]:
                title += str(node[PROPERTIES_KEY][key])
            label = title if len(title) <= self.label_max_length else title[:self.label_max_length - 3] + '...'
        data = {'properties': self.flatten(node), 'label': label, 'title': title, 'group': group}
        self.add_node(node[ID_KEY], data)
    
    def parse_rel(self, rel):
        data = {'properties': self.flatten(rel), 'label': rel[TYPE_KEY]}
        self.add_edge(rel[START_KEY],rel[END_KEY], rel[ID_KEY], rel[TYPE_KEY], data)

    def process_result(self, res:dict):
        """Determines the type of element passed in and processes it appropriately

        Args:
            res (dict): The dictionary to parse
        """
        if ENTITY_KEY in res:
            if res[ENTITY_KEY] == NODE_ENTITY_TYPE:
                self.parse_node(res)
            else:
                self.parse_rel(res)
        else:
            logger.debug("No Type Found")

    def add_results(self, results):
        """Adds the results parameter to the network

        Args:
            results (Object): Determines the type of the object and processes it
            appropriately
        """
        for res in results["results"]:
            if type(res) is dict:
                for k in res.keys():            
                    if type(res[k]) is dict:
                        self.process_result(res[k]) 
                    elif type(res[k]) is list:
                        for l in res[k]:
                            self.process_result(l)
