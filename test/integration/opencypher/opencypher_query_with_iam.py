"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: Apache-2.0
"""

from graph_notebook.configuration.generate_config import AuthModeEnum
from graph_notebook.authentication.iam_credentials_provider.credentials_factory import IAMAuthCredentialsProvider
from graph_notebook.opencypher import do_opencypher_query
from graph_notebook.sparql.query import do_sparql_query, do_sparql_explain
from graph_notebook.request_param_generator.factory import create_request_generator

from test.integration import IntegrationTest


class TestOpenCypherQueryWithIam(IntegrationTest):
    def test_do_opencypher_query(self):
        query = 'CREATE (p:Person)-[:LIKES]->(t:Technology)'
        request_generator = create_request_generator(AuthModeEnum.IAM, IAMAuthCredentialsProvider.ENV)
        res = do_opencypher_query(query, self.host, self.port, self.ssl, request_generator)
        self.assertEqual(type(res), dict)

    # def test_do_sparql_explain(self):
    #     query = "SELECT * WHERE {?s ?p ?o} LIMIT 1"
    #     request_generator = create_request_generator(AuthModeEnum.IAM, IAMAuthCredentialsProvider.ENV)
    #
    #     res = do_sparql_explain(query, self.host, self.port, self.ssl, request_generator)
    #     self.assertEqual(type(res), str)
    #     self.assertTrue(res.startswith('<!DOCTYPE html>'))
