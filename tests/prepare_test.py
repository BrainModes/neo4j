from neo4j_api.neo4j_base import Neo4jNode
from config import ConfigClass
import requests


from app import create_app

class SetUpTest:

    def __init__(self, log):
        self.log = log
        self.app = self.create_test_client()

    def create_test_client(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['DEBUG'] = True
        test_client = app.test_client(self)
        return test_client

    def create_project(self, code, discoverable='true'):
        self.log.info("\n")
        self.log.info("Preparing testing project".ljust(80, '-'))
        testing_api = "/v1/neo4j/nodes/Container"
        params = {"name": "Neo4jUnitTest",
                  "path": code,
                  "code": code,
                  "description": "Project created by unit test, will be deleted soon...",
                  "discoverable": discoverable,
                  "type": "Usecase",
                  "tags": ['test']
                  }
        self.log.info(f"POST API: {testing_api}")
        self.log.info(f"POST params: {params}")
        try:
            res = self.app.post(testing_api, json=params)
            self.log.info(f"RESPONSE DATA: {res.get_json()}")
            self.log.info(f"RESPONSE STATUS: {res.status_code}")
            if res.status_code != 200:
                self.log.error(f"create_project request failed : {res.text}")
            assert res.status_code == 200
            node_id = res.get_json()[0]['id']
            return node_id
        except Exception as e:
            self.log.info(f"ERROR CREATING PROJECT: {e}")
            raise e

    def create_file(self, file_event):
        self.log.info("\n")
        self.log.info("Creating testing file".ljust(80, '-'))
        filename = file_event.get('filename')
        file_type = file_event.get('file_type')
        namespace = file_event.get('namespace')
        project_code = file_event.get('project_code')
        path = "/"
        payload = {
                      "uploader": "EntityInfoUnittest",
                      "file_name": filename,
                      "path": path,
                      "file_size": 10,
                      "description": "string",
                      "namespace": namespace,
                      "data_type": file_type,
                      "labels": ['unittest'],
                      "project_code": project_code,
                      "dcm_id": "",
                      "process_pipeline": "",
                      "operator": "EntityInfoUnittest",
                      "parent_query": {}
                    }
        if file_event.get("parent_geid"):
            payload["parent_folder_geid"] = file_event.get("parent_geid")
        testing_api = ConfigClass.DATAOPS + '/v1/filedata/'
        try:
            self.log.info(f'POST API: {testing_api}')
            self.log.info(f'POST API: {payload}')
            res = requests.post(testing_api, json=payload)
            self.log.info(f"RESPONSE DATA: {res.text}")
            self.log.info(f"RESPONSE STATUS: {res.status_code}")
            if res.status_code != 200:
                self.log.error(f"create_file request failed : {res.text}")
            assert res.status_code == 200
            result = res.json().get('result')
            return result
        except Exception as e:
            self.log.info(f"ERROR CREATING FILE: {e}")
            raise e

    def create_node(self, label, attribute):
        self.log.info(f"Create node payload {attribute}")
        res = self.app.post("/v1/neo4j/nodes/%s" % label, json=attribute)
        if isinstance(res, str):
            raise Exception(str(
                {
                    "url": "/v1/neo4j/nodes/%s" % label,
                    "attribute": attribute,
                    "error_msg": "create_node failed.",
                    "detail": res.json
                }
        ))
        self.log.info(f"Create node response {res}")
        response = res.json[0]
        # Retrieve current node information by ID
        self.log.info(f"Create node response {response}")
        if res.status_code != 200:
            self.log.error(f"create_node request failed : {res.get_json()}")
        else:
            self.log.info(f"create_node request succeed : {res}")
        res_creation = self.app.get("/v1/neo4j/nodes/%s/node/%d" % (label, response.get('id', None)))
        assert res_creation.status_code == 200
        self.log.info(f"TESTING NODE {label} CREATED WITH ATTRIBUTES {attribute}")
        return response.get('id', None)


    def delete_node(self, node_id, label):
        '''
        self.log.info("Delete the testing node".center(50, '='))
        node_method = Neo4jNode()
        # Call delete_node function to delete node recursively by ID
        node_method.delete_node(node_id)
        self.log.warning(f"DELETING TESTING NODE: {node_id}")
        # Retrieve current node information again to make sure it had been deleted
        response = self.app.get("/v1/neo4j/nodes/%s/node/%d" % (label, node_id))
        self.log.info(f'The testing node {node_id} has been deleted, record: {response.data}"')
        '''
        self.log.warning(f"DELETING TESTING NODE: {node_id}")
        res = self.app.delete("/v1/neo4j/nodes/%s/node/%d" % (label, node_id))
        self.log.info(f"{res}")
        self.log.info(f"COMPARING: {res.status_code} VS {200}")
        assert res.status_code == 200
        response = self.app.get("/v1/neo4j/nodes/%s/node/%d" % (label, node_id))
        content = response.data
        self.log.info(f'The testing node {node_id} has been deleted, record: {content}"')

    def get_project_details(self, project_code):
        try:
            url = "/v1/neo4j/nodes/Container/query"
            response = self.app.post(url, json={"code":project_code})
            if response.status_code == 200:
                response = response.json
                self.log.info(f"POST RESPONSE: {response}")
                return response
        except Exception as error:
            self.log.info(f"ERROR WHILE GETTING PROJECT: {error}")
            raise error
