"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: Apache-2.0
"""

import logging

from graph_notebook.opencypher import do_opencypher_query
from graph_notebook.seed.load_query import get_queries

from test.integration import IntegrationTest

logger = logging.getLogger('DataDrivenOpenCypherTest')


class DataDrivenOpenCypherTest(IntegrationTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        airport_queries = get_queries('opencypher', 'epl')
        for q in airport_queries:
            try:  # we are deciding to try except because we do not know if the database we are connecting to has a partially complete set of airports data or not.
                do_opencypher_query(q['content'], cls.host, cls.port, cls.ssl, cls.request_generator)
            except Exception as e:
                logger.error(f'query {q["content"]} failed due to {e}')
                continue
