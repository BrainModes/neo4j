import unittest
from tests.prepare_test import SetUpTest
from tests.logger import Logger
import json

default_project_code = "neo4j_unit_test"

def setUpModule():
    _log = Logger(name='test_relation_v2.log')
    _test = SetUpTest(_log)
    project_details = _test.get_project_details(default_project_code)
    if len(project_details) > 0:
        project_id = _test.get_project_details(default_project_code)[0].get('id')
        _log.info(f'Existing project_id: {project_id}')
        _test.delete_node(project_id, "Container")

@unittest.skip("need update")
class TestRelationQueryV2(unittest.TestCase):
    log = Logger(name='test_relation_v2.log')
    test = SetUpTest(log)

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = cls.test.app
        cls.project_code = "neo4j_unit_test"
        cls.container_id = cls.test.create_project(cls.project_code)
        raw_file_event = {
            'filename': 'neo4j_unit_test',
            'namespace': 'greenroom',
            'project_code': cls.project_code,
            'file_type': 'raw'
        }
        cls.file1 = cls.test.create_file(raw_file_event)
        raw_file_event['filename'] = 'neo4j_unit_test2'
        cls.file2 = cls.test.create_file(raw_file_event)
    @classmethod
    def tearDownClass(cls):
        cls.test.delete_node(cls.file1["id"], "File")
        cls.test.delete_node(cls.file2["id"], "File")
        cls.test.delete_node(cls.container_id, "Container")


    def test_1_relation_query_v2(self):
        self.log.info("\n")
        self.log.info('1' + 'test relation_query_v2'.center(80, '-'))
        payload = {
            "start_label": "Container",
            "end_labels": [
                "File",
            ],
            "query": {
                "start_params": {
                    "code": self.project_code,
                },
                "end_params": {
                    "File": {
                        "name": "neo4j_unit_test",
                    }
                }
            }
        }
        try:
            response = self.app.post("/v2/neo4j/relations/query", json=payload)
            self.assertEqual(response.status_code, 200)
            data = response.json
            self.log.info(f"POST RESPONSE: {data}")
            print(data["total"])
            self.assertEqual(data["results"][0]["id"], self.file1["id"])
        except Exception as e:
            self.log.error(e)
            raise e

    def test_2_relation_query_v2_partial(self):
        self.log.info("\n")
        self.log.info('2' + 'test relation_query_v2'.center(80, '-'))
        payload = {
            "start_label": "Container",
            "end_labels": [
                "File",
            ],
            "query": {
                "start_params": {
                    "code": self.project_code,
                },
                "end_params": {
                    "File": {
                        "name": "neo4j_unit_test",
                        "partial": ["name"]
                    }
                    
                }
            }
        }
        try:
            response = self.app.post("/v2/neo4j/relations/query", json=payload)
            self.assertEqual(response.status_code, 200)
            data = response.json
            self.log.info(f"POST RESPONSE: {data}")
            self.assertEqual(data["results"][0]["id"], self.file2["id"])
            self.assertEqual(data["total"], 2)
        except Exception as e:
            self.log.error(e)
            raise e

    def test_3_relation_query_v2_no_start(self):
        self.log.info("\n")
        self.log.info('3' + 'test relation_query_v2'.center(80, '-'))
        payload = {
            "start_label": "Container",
            "end_labels": [
                "File",
            ],
            "query": {
                "start_params": {
                },
                "end_params": {
                    "File": {
                        "name": "neo4j_unit_test",
                        "partial": ["name"]
                    }
                    
                }
            }
        }
        try:
            response = self.app.post("/v2/neo4j/relations/query", json=payload)
            self.assertEqual(response.status_code, 400)
            data = response.json
            self.log.info(f"POST RESPONSE: {data}")
            self.assertEqual(data, "start_params required")
        except Exception as e:
            self.log.error(e)
            raise e

    def test_4_relation_query_v2_invalid_partial(self):
        self.log.info("\n")
        self.log.info('3' + 'test relation_query_v2'.center(80, '-'))
        payload = {
            "start_label": "Container",
            "end_labels": [
                "File",
            ],
            "query": {
                "start_params": {
                    "code": self.project_code,
                },
                "end_params": {
                    "File": {
                        "file_size": 12,
                        "partial": ["file_size"]
                    }
                    
                }
            }
        }
        try:
            response = self.app.post("/v2/neo4j/relations/query", json=payload)
            self.assertEqual(response.status_code, 403)
            data = response.json
            self.log.info(f"POST RESPONSE: {data}")
            self.assertEqual(data, "Only string parameters can use partial search")
        except Exception as e:
            self.log.error(e)
            raise e

    def test_5_relation_query_v2_invalid_partial(self):
        self.log.info("\n")
        self.log.info('5' + 'test relation_query_v2'.center(80, '-'))
        payload = {
            "start_label": "Container",
            "end_labels": [
                "File",
            ],
            "query": {
                "start_params": {
                    "code": self.project_code,
                },
                "end_params": {
                    "File": {
                        "id": self.file1["id"],
                    }
                    
                }
            }
        }
        try:
            response = self.app.post("/v2/neo4j/relations/query", json=payload)
            self.assertEqual(response.status_code, 200)
            data = response.json
            self.log.info(f"POST RESPONSE: {data}")
            self.assertEqual(data["results"][0]["id"], self.file1["id"])
        except Exception as e:
            self.log.error(e)
            raise e


    def test_6_relation_query_v2_multi_label(self):
        self.log.info("\n")
        self.log.info('6' + 'test relation_query_v2'.center(80, '-'))
        payload = {
            "start_label": "Container",
            "end_labels": [
                "File:Raw",
                "File:Greenroom",
            ],
            "query": {
                "start_params": {
                    "code": self.project_code,
                },
                "end_params": {
                    "File:Raw": {
                        "name": "neo4j_unit_test",
                    },
                    "File:Greenroom": {
                        "name": "neo4j_unit_test",
                    }
                    
                }
            }
        }
        try:
            response = self.app.post("/v2/neo4j/relations/query", json=payload)
            self.assertEqual(response.status_code, 200)
            data = response.json
            self.log.info(f"POST RESPONSE: {data}")
            self.assertEqual(data["results"][0]["id"], self.file1["id"])
        except Exception as e:
            self.log.error(e)
            raise e

    def test_7_relation_query_v2_page(self):
        self.log.info("\n")
        self.log.info('7' + 'test relation_query_v2'.center(80, '-'))
        payload = {
            "limit": 1,
            "skip": 1,
            "order_by": "name",
            "order_type": "desc",
            "start_label": "Container",
            "end_labels": [
                "File",
            ],
            "query": {
                "start_params": {
                    "code": self.project_code,
                },
                "end_params": {
                    "File": {
                        "name": "neo4j_unit_test",
                        "partial": ["name"]
                    }
                }
            }
        }
        try:
            response = self.app.post("/v2/neo4j/relations/query", json=payload)
            self.assertEqual(response.status_code, 200)
            data = response.json
            self.log.info(f"POST RESPONSE: {data}")
            self.assertEqual(data["results"][0]["id"], self.file1["id"])
            self.assertEqual(len(data["results"]), 1)
            self.assertEqual(data["total"], 2)
        except Exception as e:
            self.log.error(e)
            raise e

    def test_8_relation_query_v2_order(self):
        self.log.info("\n")
        self.log.info('8' + 'test relation_query_v2'.center(80, '-'))
        payload = {
            "limit": 1,
            "skip": 1,
            "order_by": "name",
            "order_type": "asc",
            "start_label": "Container",
            "end_labels": [
                "File",
            ],
            "query": {
                "start_params": {
                    "code": self.project_code,
                },
                "end_params": {
                    "File": {
                        "name": "neo4j_unit_test",
                        "partial": ["name"]
                    }
                }
            }
        }
        try:
            response = self.app.post("/v2/neo4j/relations/query", json=payload)
            self.assertEqual(response.status_code, 200)
            data = response.json
            self.log.info(f"POST RESPONSE: {data}")
            self.assertEqual(data["results"][0]["id"], self.file2["id"])
            self.assertEqual(len(data["results"]), 1)
            self.assertEqual(data["total"], 2)
        except Exception as e:
            self.log.error(e)
            raise e

    def test_9_relation_query_v2_invalid_order(self):
        self.log.info("\n")
        self.log.info('8' + 'test relation_query_v2'.center(80, '-'))
        payload = {
            "limit": 1,
            "skip": 1,
            "order_by": "name",
            "order_type": "asc2",
            "start_label": "Container",
            "end_labels": [
                "File",
            ],
            "query": {
                "start_params": {
                    "code": self.project_code,
                },
                "end_params": {
                    "File": {
                        "name": "neo4j_unit_test",
                        "partial": ["name"]
                    }
                }
            }
        }
        try:
            response = self.app.post("/v2/neo4j/relations/query", json=payload)
            self.assertEqual(response.status_code, 403)
            data = response.json
            self.log.info(f"POST RESPONSE: {data}")
            self.assertEqual(data, "Invalid order_type")
        except Exception as e:
            self.log.error(e)
            raise e
