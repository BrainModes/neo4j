import unittest
import sys
import json
import os
import shutil
import time
import copy
import pytest
from tests.logger import Logger
from tests.prepare_test import SetUpTest
from config import ConfigClass


def skipIfTrue(flag):
    def deco(f):
        def wrapper(self, *args, **kwargs):
            if getattr(self, flag):
                self.skipTest('Skipped by condition')
            else:
                f(self, *args, **kwargs)
        return wrapper
    return deco

default_project_code_list = ["utest","utest2","utestup","utestd"]

def setUpModule():
    _log = Logger(name='test_neo4j_dataset.log')
    _test = SetUpTest(_log)
    for default_project_code in default_project_code_list:
        project_details = _test.get_project_details(default_project_code)
        if len(project_details) > 0:
            project_id = _test.get_project_details(default_project_code)[0].get('id')
            _log.info(f'Existing project_id: {project_id}')
            _test.delete_node(project_id, "Container")


#@unittest.skip('not used for now')
class TestNeo4jDataset(unittest.TestCase):
    # some node properties
    label = "Container"
    #dataset for put, get
    dataset_id = None
    #update label
    update_dataset_id = None
    #delete
    delete_dataset_id = None
    #total dataset in the dataset
    # some of the attribute return from neo4j
    payload = {
            "name": "Unittest_dataset",
            "path": "utest",
            "code": "utest",
            "description": "unit test dataset, will be deleted soon",
            "discoverable": True,
            "type": "Container",
            "tags": [
                "tag1"
            ]
        }

    attribute = {
        "name": "Unittest_dataset",
        "path": "ctest",
        "code": "ctest",
        "description": "unit test dataset, will be deleted soon",
        "discoverable": True,
        "type": "Container",
        "tags": [
            "tag1"
            ]
    }

    update_attribute = {
            "name": "update_dataset_info",
            "discoverable": "False",
            "description": "test upadate description for unit test will be deleted soon.",
        }

    # required key to update payload
    payload_key = ["path", "code"]
    # identity key in response body
    property_key = ["code", "id"]
    query = {
            "page": 0,
            "page_size": 25,
            "partial": True,
            "order_by": "id",
            "order_type": "desc",
            "query": {
                "name": "Unittest_dataset",
                "labels": [
                    label
                    ]
                }
            }

    #is_delete = False
    log = Logger(name='test_neo4j_dataset.log')

    test = SetUpTest(log)

    @classmethod
    def setup_class(cls):
        cls.log = cls.test.log
        cls.app = cls.test.app
        #self.node_id = self.test.create_node(self.label, self.attribute)
        cls.log.info("Preparing test".ljust(80, '-'))
        try:
            # create node for dataset_id
            cls.dataset_id = cls.test.create_node(cls.label, cls.payload)
            # create node for update_dataset_id
            copy_payload = copy.deepcopy(cls.payload)
            for i in cls.payload_key:
                copy_payload[i] = copy_payload[i] + "up"
            cls.update_dataset_id = cls.test.create_node(cls.label, copy_payload)
            # create node for delete_dataset_id
            copy_payload = copy.deepcopy(cls.payload)
            for i in cls.payload_key:
                copy_payload[i] = copy_payload[i] + "d"
            cls.delete_dataset_id = cls.test.create_node(cls.label, copy_payload)

            payload = {
                **cls.payload,
                "global_entity_id": "neo4j_unit_test_geid",
            }
            payload["code"] = "utest2"
            cls.dataset_id2 = cls.test.create_node(cls.label, payload)
        except Exception as e:
            cls.log.error(f"Error happened during setup: {e}")
            raise Exception(f"Failed setup test {e}")

    @classmethod
    def teardown_class(cls):
        cls.log.info("\n")
        cls.log.info("START TEAR DOWN PROCESS".ljust(80, '-'))
        cls.test.delete_node(cls.dataset_id, cls.label)
        cls.test.delete_node(cls.update_dataset_id, cls.label)
        cls.test.delete_node(cls.dataset_id2, cls.label)
        #cls.test.delete_node(cls.delete_dataset_id, cls.label)

    def setUp(self):
        if self.label == "User":
            self.skip_condition = False
            self.skip_only = True
        elif self.label == "Container":
            self.skip_only = False
            self.skip_condition = True
        else:
            self.skip_only = True
            self.skip_condition = True

    def test_01_0_create_dataset(self):
        self.log.info("\n")
        self.log.info('01'+f'test create {self.label}'.center(80, '-'))
        testing_api = "/v1/neo4j/nodes/%s" % self.label
        self.log.info(f"POST API: {testing_api}")
        try:
            res = self.app.post("/v1/neo4j/nodes/%s" % self.label, json = self.attribute)
            self.log.info(f"POST RESPONSE: {res}")
            self.log.info(f"COMPARING: {res.status_code} VS {200}")
            self.assertEqual(res.status_code, 200)
        except Exception as e:
            self.log.error(e)
            raise e
        response = res.json[0]
        self.log.info(f"RESPONSE JSON: \n {response}")
        create_id = response.get('id', None)
        # check the payload is correct
        self.log.info(f"COMPARING LABELS: {response['labels']} VS {self.label}")
        self.assertEqual(response['labels'], [self.label])
        # also check each attribute is correct
        for x in self.attribute:
            self.log.info(f"COMPARING ATTRIBUTE of {x}: {self.attribute[x]} VS {response.get(x, None)}")
            self.assertEqual(self.attribute[x], response.get(x, None))
        self.test.delete_node(create_id, self.label)

    @skipIfTrue("skip_only")
    def test_01_1_create_dataset_with_exist_code(self):
        self.log.info("\n")
        self.log.info('01.1'+ f'test create {self.label} with exist code'.center(80, '-'))
        testing_api = "/v1/neo4j/nodes/%s" % self.label
        self.log.info(f"POST API: {testing_api}")
        try:
            res = self.app.post(testing_api, json=self.payload)
            self.log.info(f"POST RESPONSE: {res}")
            self.log.info(f"RESPONSE DATA: {res.data}")
            self.log.info(f"COMPARING: {res.status_code} VS {403}")
            self.assertEqual(res.status_code, 403)
            #self.log.info(f"COMPARING: {b'The requested URL was not found on the server'} "
                          #f"IN {res.data}")
            #self.assertTrue(b"The requested URL was not found on the server" in res.data)
        except Exception as e:
            self.log.error(e)
            raise e

    #@unittest.skip
    def test_01_2_create_dataset_with_integer_label(self):
        self.log.info("\n")
        self.log.info('01.2'+ f'test create {self.label} with empty code'.center(80, '-'))
        int_label = 6
        testing_api = "/v1/neo4j/nodes/%s" % int_label
        self.log.info(f"POST API: {testing_api}")
        try:
            res = self.app.post(testing_api, json=self.attribute)
            self.log.info(f"POST RESPONSE: {res}")
            self.log.info(f"RESPONSE DATA: {res.data}")
            self.log.info(f"COMPARING: {res.status_code} VS {403}")
            self.assertEqual(res.status_code, 403)
            #self.log.info(f"COMPARING: {b'The requested URL was not found on the server'} "
                          #f"IN {res.data}")
            #self.assertTrue(b"The requested URL was not found on the server" in res.data)
        except Exception as e:
            self.log.error(e)
            raise e


    #@unittest.skip
    def test_02_0_update_dataset(self):
        self.log.info("\n")
        self.log.info('02'+ f'test update {self.label}'.center(80, '-'))
        testing_api = "/v1/neo4j/nodes/%s/node/%d" % (self.label, self.update_dataset_id)
        self.log.info(f"PUT API: {testing_api}")
        try:
            res = self.app.put(testing_api, json=self.update_attribute)
            self.log.info(f"PUT RESPONSE: {res}")
            self.log.info(f"RESPONSE DATA: {res.data}")
            self.log.info(f"COMPARING: {res.status_code} VS {200}")
            self.assertEqual(res.status_code, 200)
            response = res.json[0]
            self.log.info(f"COMPARING LABELS: {response['labels']} VS {self.label}")
            self.assertIn(self.label, response['labels'])
            for x in self.update_attribute:
                self.assertEqual(self.update_attribute[x], response.get(x, None))
        except Exception as e:
            self.log.error(e)
            raise e

    @unittest.skip
    def test_02_1_update_dataset_with_wrong_id(self):
        self.log.info("\n")
        self.log.info('02.1'+ f'test update {self.label} with not exist id'.center(80, '-'))
        not_exist_id = 14159265
        testing_api = "/v1/neo4j/nodes/%s/node/%d" % (self.label, not_exist_id)
        self.log.info(f"PUT API: {testing_api}")
        try:
            res = self.app.put(testing_api, json = self.update_attribute)
            self.log.info(f"PUT RESPONSE: {res}")
            self.log.info(f"RESPONSE DATA: {res.data}")
            self.log.info(f"COMPARING: {res.status_code} VS {403}")
            self.assertEqual(res.status_code, 403)
            #self.log.info(f"COMPARING: {b'The requested URL was not found on the server'} "
                          #f"IN {res.data}")
            #self.assertTrue(b"The requested URL was not found on the server" in res.data)
        except Exception as e:
            self.log.error(e)
            raise e


    #@skipIfTrue("skip_condition")
    @unittest.skip("seems to be broken")
    def test_03_1_get_all_datasets_properties(self):
        self.log.info("\n")
        self.log.info('03'+ f'test get all {self.label} properties'.center(80, '-'))
        testing_api = "/v1/neo4j/nodes/%s/properties" % self.label
        self.log.info(f"GET API: {testing_api}")
        try:
            res = self.app.get(testing_api)
            self.log.info(f"GET RESPONSE: {res}")
            self.log.info(f"COMPARING: {res.status_code} VS {200}")
            self.assertEqual(res.status_code, 200)
            response = res.json
            #self.log.info(f"GET RESPONSE JSON: {response}")
            code_total = len(response[self.property_key[0]])
            id_total = len(response[self.property_key[1]])
            self.log.info(f"COMPARING NUMBER: {self.property_key[0]} {code_total} VS {self.property_key[1]} {id_total}")
            #self.assertEqual(code_total, id_total)
            if "labels" in response:
                self.log.info(f"COMPARING: {response['labels']} VS {self.label}")
                self.assertEqual(response['labels'], [[self.label]])
        except Exception as e:
            self.log.error(e)
            raise e

    @unittest.skip("seems to be broken")
    def test_03_2_get_property_with_additional_dataset(self):
        self.log.info("\n")
        self.log.info('03.1'+ f'test total {self.label} after create a new one'.center(80, '-'))
        testing_api = "/v1/neo4j/nodes/%s/properties" % self.label
        self.log.info(f"GET API: {testing_api}")
        create_api = "/v1/neo4j/nodes/%s" % self.label
        try:
            get_total = self.app.get(testing_api).json
            code_total = len(get_total[self.property_key[0]])
            id_total = len(get_total[self.property_key[1]])
            create = self.app.post(create_api, json = self.attribute)
            res = self.app.get(testing_api)
            self.log.info(f"GET RESPONSE: {res}")
            self.log.info(f"COMPARING: {res.status_code} VS {200}")
            response = res.json
            code_current = len(response[self.property_key[0]])
            id_current = len(response[self.property_key[1]])
            self.log.info(f"COMPARING: CURRENT {self.label} {self.property_key[0]} {code_current} VS ORIGINAL {code_total}")
            self.assertEqual(code_current, code_total+1)
            self.log.info(f"COMPARING: CURRENT {self.label} {self.property_key[1]} {id_current} VS ORIGINAL {id_total}")
            self.assertEqual(id_current, id_total+1)
            self.log.info(f"COMPARING NUMBER: {self.property_key[0]} VS {self.property_key[1]}")
            #self.assertEqual(code_current, id_current)
            self.test.delete_node(create.json[0].get('id', None), self.label)
        except Exception as e:
            if create.status_code == 200:
                self.test.delete_node(create.json[0].get('id', None), self.label)
            self.log.error(e)
            raise e


    #@skipIfTrue("skip_condition")
    def test_03_3_get_all_datasets_properties_with_int_label(self):
        self.log.info("\n")
        self.log.info('03.2'+f'test get all {self.label} properties'.center(80, '-'))
        int_label = 14159265
        testing_api = "/v1/neo4j/nodes/%s/properties" % int_label
        self.log.info(f"GET API: {testing_api}")
        try:
            res = self.app.get(testing_api)
            self.log.info(f"GET RESPONSE: {res}")
            self.log.info(f"COMPARING: {res.status_code} VS {403}")
            self.assertEqual(res.status_code, 403)
        except Exception as e:
            self.log.error(e)
            raise e


    #@unittest.skip
    def test_04_0_query_dataset(self):
        self.log.info("\n")
        self.log.info('04'+ f'test query {self.label} with given information'.center(80, '-'))
        testing_api = "/v2/neo4j/nodes/query"
        self.log.info(f"GET API: {testing_api}")
        query_key = []
        for i in self.query["query"]:
            if i != "labels":
                query_key.append(i)
        try:
            res = self.app.post(testing_api, json = self.query)
            self.log.info(f"GET RESPONSE: {res}")
            self.log.info(f"COMPARING: {res.status_code} VS {200}")
            self.assertEqual(res.status_code, 200)
            response = res.json
            self.log.info(f"GET RESPONSE JSON: {response}")
            result = response['result']
            expect_dataset_id = [self.delete_dataset_id, self.dataset_id]
            self.log.info(f"COMPARE {self.label} IN THE QUERY")
            self.log.info(f"COMAPRING QUERY KEY ARE {query_key}")
            for item in result:
                if item['id'] in expect_dataset_id:
                    for k in query_key:
                        self.log.info(f"COMPARE {item['id']} {self.label}_{k}: {item[k]} VS {self.payload[k]}")
                        self.assertEqual(item[k], self.payload[k])
                    expect_dataset_id.remove(item['id'])
            self.log.info(f"The left {self.label} that does not found: {expect_dataset_id}")
            self.assertEqual(expect_dataset_id, [])
        except Exception as e:
            self.log.error(e)
            raise e


    #@unittest.skip
    def test_05_0_delete_dataset(self):
        self.log.info("\n")
        self.log.info('05'+ f'test delete {self.label}'.center(80, '-'))
        testing_api = "/v1/neo4j/nodes/%s/node/%d" % (self.label, self.delete_dataset_id)
        self.log.info(f"DELETE API: {testing_api}")
        try:
            res = self.app.delete(testing_api)
            self.log.info(f"DELETE RESPONSE: {res}")
            self.log.info(f"RESPONSE DATA: {res.data}")
            self.log.info(f"COMPARING: {res.status_code} VS {200}")
            self.assertEqual(res.status_code, 200)
            #if res.status_code == 200:
                #self.is_delete = True
            #find node again to check whether node is actually deleted
            #get_node = self.app.get(testing_api)
        except Exception as e:
            self.log.error(e)
            raise e

    #@unittest.skip
    def test_05_1_delete_dataset_again(self):
        self.log.info("\n")
        self.log.info('05.1'+ f'test delete {self.label} that has already been deleted'.center(80, '-'))
        testing_api = "/v1/neo4j/nodes/%s/node/%d" % (self.label, self.delete_dataset_id)
        self.log.info(f"DELETE API: {testing_api}")
        try:
            res = self.app.delete(testing_api)
            self.log.info(f"DELETE RESPONSE: {res}")
            self.log.info(f"RESPONSE DATA: {res.data}")
            self.log.info(f"COMPARING: {res.status_code} VS {403}")
            self.assertEqual(res.status_code, 403)
        except Exception as e:
            self.log.error(e)
            raise e

    #@unittest.skip
    def test_06_0_get_dataset(self):
        self.log.info("\n")
        self.log.info('06'+ f'test get {self.label} with exist id'.center(80, '-'))
        testing_api = "/v1/neo4j/nodes/%s/node/%d" % (self.label, self.dataset_id)
        self.log.info(f"GET API: {testing_api}")
        try:
            res = self.app.get(testing_api)
            self.log.info(f"GET RESPONSE: {res}")
            self.log.info(f"RESPONSE DATA: {res.data}")
            self.log.info(f"COMPARING: {res.status_code} VS {200}")
            self.assertEqual(res.status_code, 200)
            response = res.json[0]
            self.log.info(f"COMPARING LABELS: {response['labels']} VS {self.label}")
            self.assertIn(self.label, response['labels'])
            for x in self.payload:
                if x in response:
                    self.assertEqual(self.payload[x], response.get(x, None))
        except Exception as e:
            self.log.error(e)
            raise e

    @unittest.skip
    def test_06_1_get_deleted_dataset(self):
        self.log.info("\n")
        self.log.info('06.1'+ f'test get {self.label} with deleted node'.center(80, '-'))
        testing_api = "/v1/neo4j/nodes/%s/node/%d" % (self.label, self.delete_dataset_id)
        self.log.info(f"GET API: {testing_api}")
        try:
            res = self.app.get(testing_api)
            self.log.info(f"GET RESPONSE: {res}")
            self.log.info(f"RESPONSE DATA: {res.data}")
            self.log.info(f"COMPARING: {res.status_code} VS {200}")
            self.assertEqual(res.status_code, 200)
            self.log.info(f"COMPARING CONTENT: '[]' VS {res.data}")
            self.assertIn(b'[]', res.data)
        except Exception as e:
            self.log.error(e)
            raise e

    @unittest.skip
    def test_06_2_get_dataset_with_wrong_id(self):
        self.log.info("\n")
        self.log.info('06.2'+ f'test get {self.label} with not exist id'.center(80, '-'))
        not_exist_id = 1415926
        testing_api = "/v1/neo4j/nodes/%s/node/%d" % (self.label, not_exist_id)
        self.log.info(f"GET API: {testing_api}")
        try:
            res = self.app.get(testing_api)
            self.log.info(f"GET RESPONSE: {res}")
            self.log.info(f"RESPONSE DATA: {res.data}")
            self.log.info(f"COMPARING: {res.status_code} VS {200}")
            self.assertEqual(res.status_code, 200)
            self.log.info(f"COMPARING CONTENT: '[]' VS {res.data}")
            self.assertIn(b'[]', res.data)
        except Exception as e:
            self.log.error(e)
            raise e

    @unittest.skip
    def test_07_query_by_geids(self):
        self.log.info("\n")
        self.log.info('07'+ f'query_by_geids'.center(80, '-'))
        testing_api = "/v1/neo4j/nodes/query/geids"
        self.log.info(f"POST API: {testing_api}")
        res = self.post.get(testing_api, {"geids": ["neo4j_unit_test_geid"]})
        self.log.info(f"POST RESPONSE: {res}")
        self.log.info(f"RESPONSE DATA: {res.data}")
        self.assertEqual(res.status_code, 200)
        self.assertIn(len(res.json["result"]), 1)


#@unittest.skip('not used for now')
class TestNeo4jUsers(TestNeo4jDataset):
    # some node properties
    label = "User"
    #dataset for put, get
    dataset_id = None
    #update label
    update_dataset_id = None
    #delete
    delete_dataset_id = None
    #id created by create test function
    # some of the attribute return from neo4j
    payload = {
            "name": "unittestuser1",
            "path": "users",
            "email": "amy.guindoc12+10@gmail.com",
            "first_name": "testunittest",
            "last_name": "unittestOnly",
            "role": "admin",
            "status": "active"
        }

    attribute = {
            "name": "unittestuser2",
            "path": "users",
            "email": "amy.guindoc12+20@gmail.com",
            "first_name": "test",
            "last_name": "user",
            "role": "admin",
            "status": "active"
        }
    updated_payload = {
            "name": "unittestuser1",
            "email": "amy.guindoc12+11@gmail.com"
    }

    updated_payload2 = {
            "name": "unittestuser1",
            "email": "amy.guindoc12+12@gmail.com"
    }

    update_attribute = {
            "role": "member",
            "status": "disabled"
        }

    query = {
            "page": 0,
            "page_size": 25,
            "partial": True,
            "order_by": "name",
            "order_type": "desc",
            "query": {
                "first_name": "testunittest",
                "last_name": "unittestOnly",
                "labels": [
                    label
                    ]
                }
            }

    property_key = ['name', 'email']
    teardown_user_id = []
    #is_delete = False
    log = Logger(name='test_neo4j_user.log')

    test = SetUpTest(log)

    @classmethod
    def setup_class(cls):
        cls.log = cls.test.log
        cls.app = cls.test.app
        #self.node_id = self.test.create_node(self.label, self.attribute)
        cls.log.info("Preparing test".ljust(80, '-'))
        try:
            # create node for dataset_id
            cls.dataset_id = cls.test.create_node(cls.label, cls.payload)
            # create node for update_dataset_id
            copy_payload = copy.deepcopy(cls.payload)
            copy_payload.update(cls.updated_payload)
            cls.update_dataset_id = cls.test.create_node(cls.label, copy_payload)
            # create node for delete_dataset_id
            copy_payload = copy.deepcopy(cls.payload)
            copy_payload.update(cls.updated_payload2)
            cls.delete_dataset_id = cls.test.create_node(cls.label, copy_payload)
        except Exception as e:
            cls.log.error(f"Error happened during setup: {e}")
            raise Exception(f"Failed setup test {e}")

    @classmethod
    def teardown_class(cls):
        cls.log.info("\n")
        cls.log.info("START TEAR DOWN PROCESS".ljust(80, '-'))
        if (cls.dataset_id in cls.teardown_user_id) and (cls.update_dataset_id in cls.teardown_user_id):
            cls.log.info(f"teardown_user_id {cls.teardown_user_id}")
            for i in cls.teardown_user_id:
                cls.log.info(f"Removing id: {i}")
                cls.test.delete_node(i, cls.label)
        else:
            cls.log.info(f"Removing {cls.dataset_id} and {cls.update_dataset_id}")
            cls.test.delete_node(cls.dataset_id, cls.label)
            cls.test.delete_node(cls.update_dataset_id, cls.label)
        #cls.test.delete_node(cls.delete_dataset_id, cls.label)

    @unittest.skip('broken')
    def test_07_1_count_total_user_number(self):
        self.log.info("\n")
        self.log.info('07'+ f'test count number of platform {self.label}'.center(80, '-'))
        testing_api = "/v1/neo4j/nodes/%s/query/count" % self.label
        self.log.info(f"GET API: {testing_api}")
        query_property = "/v1/neo4j/nodes/%s/properties" % self.label
        #specific for user node
        query_load = {
            "count": True
        }
        try:
            res = self.app.post(testing_api, json = query_load)
            self.log.info(f"GET RESPONSE: {res}")
            self.log.info(f"RESPONSE DATA: {res.data}")
            self.log.info(f"COMPARING: {res.status_code} VS {200}")
            self.assertEqual(res.status_code, 200)
            total = res.json['count']
            query_property = self.app.get(query_property)
            query_result = query_property.json
            expect = len(query_result[self.property_key[0]])
            self.log.info(f"COMPARING: EXPECT TOTAL {expect} VS ACTUAL COUNT {total}")
            self.assertEqual(total, expect)
        except Exception as e:
            self.log.error(e)
            raise e

    def test_07_2_count_total_user_number_after_adding(self):
        self.log.info("\n")
        self.log.info('07.1'+ f'test count number of platform {self.label} after addition'.center(80, '-'))
        testing_api = "/v1/neo4j/nodes/%s/query/count" % self.label
        self.log.info(f"GET API: {testing_api}")
        #specific for user node
        query_load = {
            "count": True
        }
        create_id = None
        try:
            res = self.app.post(testing_api, json = query_load)
            self.log.info(f"GET RESPONSE: {res}")
            self.log.info(f"RESPONSE DATA: {res.data}")
            self.log.info(f"COMPARING: {res.status_code} VS {200}")
            original_total = res.json['count']
            create_id = self.test.create_node(self.label, self.attribute)
            current = self.app.post(testing_api, json = query_load)
            current_total = current.json['count']
            self.log.info(f"COMPARING: original total {original_total} VS current total {current_total}")
            self.assertEqual(current_total, original_total+1)
            self.test.delete_node(create_id, self.label)
        except Exception as e:
            if create_id != None:
                self.test.delete_node(create_id, self.label)
            self.log.error(e)
            raise e

    @unittest.skip("seems to be broken")
    def test_07_3_count_single_name(self):
        self.log.info("\n")
        self.log.info('07.2'+ f'test number of platform {self.label} name'.center(80, '-'))
        testing_api = "/v1/neo4j/nodes/%s/query/count" % self.label
        self.log.info(f"GET API: {testing_api}")
        query_load = {
            "count": True,
            "name": self.payload["name"]
        }
        try:
            res = self.app.post(testing_api, json = query_load)
            self.log.info(f"GET RESPONSE: {res}")
            self.log.info(f"RESPONSE DATA: {res.data}")
            self.log.info(f"COMPARING: {res.status_code} VS {200}")
            total = res.json['count']
            #"name" should be unique
            self.log.info(f"RESULT: total number {total} should be 1")
            self.assertEqual(total, 1)
        except Exception as e:
            self.log.error(e)
            raise e

    @unittest.skip("seems to be broken")
    def test_07_4_count_single_email(self):
        self.log.info("\n")
        self.log.info('07.3'+ f'test number of platform {self.label} email'.center(80, '-'))
        testing_api = "/v1/neo4j/nodes/%s/query/count" % self.label
        self.log.info(f"GET API: {testing_api}")
        query_load = {
            "count": True,
            "email": self.payload["email"]
        }
        try:
            res = self.app.post(testing_api, json = query_load)
            self.log.info(f"GET RESPONSE: {res}")
            self.log.info(f"RESPONSE DATA: {res.data}")
            self.log.info(f"COMPARING: {res.status_code} VS {200}")
            total = res.json['count']
            #"name" should be unique
            self.log.info(f"RESULT: total number {total} should be 1")
            self.assertEqual(total, 1)
        except Exception as e:
            self.log.error(e)
            raise e

    @skipIfTrue("skip_condition")
    # @unittest.skip("require data cleaning before proceed")
    def test_08_1_query_user(self):
        self.log.info("\n")
        self.log.info('08'+ f'test the listing of {self.label}'.center(80, '-'))
        testing_api = "/v1/neo4j/nodes/%s/query" % self.label
        self.log.info(f"GET API: {testing_api}")
        query_load = {
            "name": self.payload["name"]
        }
        self.log.info(f"query payload: {query_load}")
        try:
            res = self.app.post(testing_api, json=query_load)
            self.log.info(f"GET RESPONSE: {res}")
            self.log.info(f"RESPONSE DATA: {res.data}")
            self.log.info(f"COMPARING: {res.status_code} VS {200}")
            response = res.json
            result_response = {}
            for i in response:
                self.teardown_user_id.append(i['id'])
                if i['id'] == self.dataset_id:
                    result_response = i
            self.log.info(f"teardown node id: {self.teardown_user_id}")
            self.log.info(f"COMPARING: user_id {self.teardown_user_id} VS actual_id {self.dataset_id}")
            self.assertIn(self.dataset_id, self.teardown_user_id)
            for x in self.payload:
                self.log.info(f"COMPARING ATTRIBUTE of {x}: {self.payload [x]} VS {result_response.get(x, None)}")
                self.assertEqual(self.payload[x], result_response.get(x, None))
        except Exception as e:
            self.log.error(e)
            raise e

#@unittest.skip('not used for now')
class TestNeo4jFiles(TestNeo4jUsers):
    # some node properties
    label = "File"
    #dataset for put, get
    dataset_id = None
    #update label
    update_dataset_id = None
    #delete
    delete_dataset_id = None
    #create dataset for files
    create_dataset = None
    dataset_payload = {
            "name": "Unittest_dataset",
            "path": "utest",
            "code": "utest",
            "description": "unit test dataset, will be deleted soon",
            "discoverable": True,
            "type": "Container",
            "tags": [
                "tag1"
            ]
        }
    # some of the attribute return from neo4j
    payload = {
            "name": "Unittest_file10.txt",
            "extra_labels": ["Greenroom", "Raw"],
            "file_size": 7120,
            "operator": "amy11",
            "archived": False,
            "process_pipeline": "",
            "uploader": "amy11",
            "dcm_id": "undefined"
            #"path": "/data/storage/indoctestproject/processed/straight_copy",
            #"full_path": "/data/storage/indoctestproject/processed/straight_copy/10.3.7.220_workbench_indoctestproject_guacamole_.png",
        }

    updated_payload = {
            "name": "Unittest_file11.txt"
    }

    updated_payload2 = {
            "name": "Unittest_file12.txt"
    }

    attribute = {
            "name": "Unittest_file20.txt",
            "extra_labels": ["Greenroom", "Raw"],
            "file_size": 7120,
            "operator": "amy11",
            "archived": False,
            "process_pipeline": "",
            "uploader": "amy11",
            "dcm_id": "undefined"
    }

    update_attribute = {
            "uploader": "amy12",
            "file_size": 7000,
            "archived": True,
        }

    # required key to update payload
    payload_key = ["name", "path", "full_path"]
    # identity key in response body
    property_key = ["full_path", "code"]
    query = {
            "page": 0,
            "page_size": 25,
            "partial": True,
            "order_by": "id",
            "order_type": "desc",
            "query": {
                "archived": False,
                "operator": "amy11",
                "file_size": 7120,
                "labels": [
                "Greenroom",
                "Raw",
                "File"
                    ]
                }
            }

    #is_delete = False
    log = Logger(name='test_neo4j_file.log')

    test = SetUpTest(log)

    @classmethod
    def setup_class(cls):
        cls.log = cls.test.log
        cls.app = cls.test.app
        #self.node_id = self.test.create_node(self.label, self.attribute)
        cls.log.info("Preparing test".ljust(80, '-'))
        path = "/"
        try:
            # create node for dataset_id
            cls.create_dataset = cls.test.create_node("Container", cls.dataset_payload)
            # create file in the test dataset
            cls.payload["path"] = path  + cls.dataset_payload['path'] + "/raw"
            cls.payload["full_path"] = cls.payload["path"] + "/" + cls.payload["name"]
            cls.dataset_id = cls.test.create_node(cls.label, cls.payload)
            # create node for update_dataset_id
            copy_payload = copy.deepcopy(cls.payload)
            copy_payload.update(cls.updated_payload)
            copy_payload["full_path"] = copy_payload["path"] + "/" + copy_payload["name"]
            cls.update_dataset_id = cls.test.create_node(cls.label, copy_payload)
            # create node for delete_dataset_id
            copy_payload = copy.deepcopy(cls.payload)
            copy_payload.update(cls.updated_payload2)
            copy_payload["full_path"] = copy_payload["path"] + "/" + copy_payload["name"]
            cls.delete_dataset_id = cls.test.create_node(cls.label, copy_payload)
        except Exception as e:
            cls.test.delete_node(cls.create_dataset, "Container")
            cls.log.error(f"Error happened during setup: {e}")
            raise Exception(f"Failed setup test {e}")

    @classmethod
    def teardown_class(cls):
        cls.log.info("\n")
        cls.log.info("START TEAR DOWN PROCESS".ljust(80, '-'))
        cls.test.delete_node(cls.create_dataset, "Container")
        cls.test.delete_node(cls.dataset_id, cls.label)
        cls.test.delete_node(cls.update_dataset_id, cls.label)
        #cls.test.delete_node(cls.delete_dataset_id, cls.label)

    def test_01_0_create_dataset(self):
        self.log.info("\n")
        self.log.info('01'+f'test create {self.label}'.center(80, '-'))
        testing_api = "/v1/neo4j/nodes/%s" % self.label
        self.log.info(f"POST API: {testing_api}")
        path = "/"
        try:
            self.attribute["path"] = path + self.dataset_payload['path'] + "/raw"
            self.attribute["full_path"] = self.attribute["path"] + "/" + self.attribute["name"]
            res = self.app.post("/v1/neo4j/nodes/%s" % self.label, json = self.attribute)
            response = res.json[0]
            create_id = response.get('id', None)
            self.log.info(f"POST RESPONSE: {res}")
            self.log.info(f"COMPARING: {res.status_code} VS {200}")
            self.assertEqual(res.status_code, 200)
            self.log.info(f"RESPONSE JSON: \n {response}")
            # check the payload is correct
            self.log.info(f"COMPARING LABELS: {response['labels']} VS {self.label}")
            self.assertIn(self.label, response['labels'])
            # also check each attribute is correct
            for x in self.attribute:
                if x != "extra_labels":
                    self.log.info(f"COMPARING ATTRIBUTE of {x}: {self.attribute[x]} VS {response.get(x, None)}")
                    self.assertEqual(self.attribute[x], response.get(x, None))
            self.test.delete_node(create_id, self.label)
        except Exception as e:
            self.test.delete_node(create_id, self.label)
            self.log.error(e)
            raise e

