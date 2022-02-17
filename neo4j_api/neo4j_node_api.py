from flask import request, make_response, jsonify
# from flask_restful import Resource
from flask_restx import Api, Resource
from . import neo4j_connection
from neo4j_api.neo4j_base import Neo4jNode, Neo4jClient, neo_quick_query
from utils import neo4j_obj_2_json, node_2_json
from . import node_ns
from neo4j_api.swagger_modules import (
    node_update_module, node_create_module,
    node_query_module, node_query_module_count, labels_module, node_query_module_v2, node_batch_update)
import math
import json


class ActionOnNodeById(Resource):
    # initialize the class for using the method
    node_method = Neo4jClient()

    get_returns = """
     Container response:
     [
        {'id': <Node-ID>,
         'labels': ['Container'],
         'code': <project-code>,
         'is_new': False,
         'last_login': '2020-11-23T17:06:27.600313',
         'roles': [<project_enabled-roles>],
         'description': <project-description>,
         'type': 'Usecase',
         'tags': [<project-tags>],
         'path': <nfs-path>,
         'time_lastmodified': <time-string>,
         'discoverable': <whether-discoverable-to-all-users>,
         'name': <project-name>,
         'time_created': <time-string>}
     ]\n
     User response:
    [
        {"id": <node-id>,
         "labels": ["User"],
         "path": "users",
         "time_lastmodified": <time-string>,
         "role": <user-role>,
         "last_login": <time-string>,
         "name": <username>,
         "time_created": <time-string>,
         "last_name": <lastname>,
         "realm": "realm",
         "first_name": <firstname>,
         "email": <email>,
         "status": "active"}
    ]\n
    Default response:
    [
        {
            "id": <ID>,
            "labels": [
                <node-label>
            ],
            "name": <node-name>,
            "time_created": <time-string>,
            "time_lastmodified": <time-string>,
            "other_property": "xxxx",
            "other_property_2": "xxxx"
        }
    ]
    """

    @node_ns.doc(params={'label': 'Container', 'id': 'Node ID'})
    @node_ns.response(200, get_returns)
    @node_ns.response(403, """Exception""")
    def get(self, label, id):
        """
        Get the Node with the input Node ID
        Usage: used for check if project exists
        """
        try:
            result = self.node_method.get_node(label, int(id))
            if result:
                result = [node_2_json(result)]
            else:
                result = []
        except Exception as e:
            return str(e), 403

        return result, 200

    put_returns = """
        Container response:
        [
            {"id": 66,
             "labels": ["Container"],
             "code": "firefoxcreation",
             "is_new"(If exists): false,
             "roles": ["admin", "contributor"],
             "description": "",
             "admin"(If exists): [<project-admin>],
             "type": "Usecase",
             "tags": [<project-tag>],
             "path": <nfs-path>,
             "time_lastmodified": <time-string>,
             "discoverable": <whether-discoverable-to-all-users>,
             "name": <project-name>,
             "time_created": <time-string>,
             }
        ]\n
        User response:
        [
            {"id": <node-id>,
            "labels": ["User"],
            "path": "users",
            "time_lastmodified": <time-string>,
            "role": <platform-role>,
            "last_login": <time-string>,
            "name": <username>,
            "time_created": <time-string>,
            "last_name": <lastname>,
            "realm": "realm",
            "first_name": <firstname>,
            "email": <user-email>,
            "status": "active"
            }
        ]\n
        Default response:
        [
            {"id": <ID>,
             "labels": [<node-label>],
             "name": <node-name>,
             "time_created": <time-string>,
             "time_lastmodified": <time-string>,


             "other_property": "xxxx",
             "other_property_2": "xxxx",
             "new_attribute":"new_value"
            }
        ]
    """

    @node_ns.doc(params={'label': 'Container/User', 'id': 'Node ID'})
    @node_ns.expect(node_update_module)
    @node_ns.response(200, put_returns)
    @node_ns.response(403, 'Exception')
    def put(self, label, id):
        """
        Update the Node with Input Node ID
        Usage: used for updating users' status, or projects' name, discoverable, description, tags
        """
        post_data = request.get_json()

        try:
            if len(post_data.keys()) == 1 and "last_login" in post_data.keys():
                res = self.node_method.update_node(label, int(
                    id), post_data, update_modified_time=False)
            else:
                res = self.node_method.update_node(label, int(id), post_data)
            result = [node_2_json(res)]
        except Exception as e:
            return str(e), 403

        return result, 200

    def delete(self, label, id):
        """
        Delete node by label and id
        """
        try:
            self.node_method.delete_node(label, int(id))
        except Exception as e:
            return str(e), 403
        return 'success', 200


class ActionOnNodeByGeid(Resource):
    # initialize the class for using the method
    node_method = Neo4jClient()

    get_returns = """
     Container response:
     [
        {'id': <Node-ID>,
         'labels': ['Container'],
         'code': <project-code>,
         'is_new': False,
         'last_login': '2020-11-23T17:06:27.600313',
         'roles': [<project_enabled-roles>],
         'description': <project-description>,
         'type': 'Usecase',
         'tags': [<project-tags>],
         'path': <nfs-path>,
         'time_lastmodified': <time-string>,
         'discoverable': <whether-discoverable-to-all-users>,
         'name': <project-name>,
         'time_created': <time-string>}
     ]\n
     User response:
    [
        {"id": <node-id>,
         "labels": ["User"],
         "path": "users",
         "time_lastmodified": <time-string>,
         "role": <user-role>,
         "last_login": <time-string>,
         "name": <username>,
         "time_created": <time-string>,
         "last_name": <lastname>,
         "realm": "realm",
         "first_name": <firstname>,
         "email": <email>,
         "status": "active"}
    ]\n
    Default response:
    [
        {
            "id": <ID>,
            "labels": [
                <node-label>
            ],
            "name": <node-name>,
            "time_created": <time-string>,
            "time_lastmodified": <time-string>,
            "other_property": "xxxx",
            "other_property_2": "xxxx"
        }
    ]
    """

    @node_ns.doc(params={'geid': 'Node global entity id'})
    @node_ns.response(200, get_returns)
    @node_ns.response(403, """Exception""")
    def get(self, geid):
        """
        Get the Node with the input geid since now most operation
        are use the geid
        """
        try:
            result = self.node_method.get_node_by_geid(geid)
            if result:
                result = [node_2_json(result)]
            else:
                result = []
        except Exception as e:
            return str(e), 403

        return result, 200


class BatchCreateNode(Resource):
    node_method = Neo4jClient()

    def post(self, label):
        """
        Create New Node with Given Label
        Usage: used for creating new user or new project
        """
        post_data = request.get_json()
        payload = post_data['payload']
        extra_labels = post_data.get('extra_labels', [])

        # try:
        #     res = self.node_method.bulk_add_node(label, payload, extra_labels)
        #     # res
        # except Exception as e:
        #     return str(e), 403
        res = self.node_method.bulk_add_node(label, payload, extra_labels)
        return {"result": "success"}, 200


class CreateNode(Resource):
    # initialize the class for using the method
    node_method = Neo4jClient()

    post_returns = """
    Container response:
    {
        "result": {
            "parent_relation": <relation-label>,
            "admin"(this one has been deprecated): [<admin-username>],
            "time_lastmodified": <time-string>,
            "_key2": "value2",
            "path": <nfs-path/project/code>,
            "id": <Node-ID>,
            "time_created": <time-string>,
            "name": <node-name>
            "labels": [
                "Container"
            ],
            "_key1": "value1",
            "parent_id": <parent-id>,
            "tags": [
                "tag1",
                "tag2"
            ],
            "type": "Container"
        }
    }\n
    User response:
    {
        result: {
            "time_created": "2020-07-03T18:23:15",
            "first_name": <first-name>,
            "name": <user-name>,
            "time_lastmodified": <time-string>,
            "last_name": <last-name>,
            "path": "users",
            "role": <plstform-role>,
            "labels": [
                "User"
            ],
            "id": <ID>
        }
    }\n
    Default response:
    {'id': <ID>,
    'labels': ['test_label'],
    'name': <node-name>,
    "time_created": <time-string>,
    "time_lastmodified": <time-string>,
    "parent_relation":  <relation>,
    "parent_id": <parent-node-ID>,
    "other_property": "xxxx"}
    """

    @node_ns.expect(node_create_module)
    @node_ns.doc(params={'label': 'Container/User'})
    @node_ns.response(200, post_returns)
    @node_ns.response(403, """Exception""")
    def post(self, label):
        """
        Create New Node with Given Label
        Usage: used for creating new user or new project
        """
        post_data = request.get_json()

        # node name is required
        node_name = post_data.pop("name", None)
        try:
            res = self.node_method.add_node(label, node_name, post_data)
            result = [node_2_json(res)]
        except Exception as e:
            return str(e), 403

        return result, 200


class ActionOnNodeByQuery(Resource):
    # initialize the class for using the method
    node_method = Neo4jClient()

    post_returns = """
    User response:
    [
        {"id": 0,
         "labels": ["User"],
         "path": "users",
         "time_lastmodified": <time-string>,
         "role": <platform-role>,
         "last_login": <time-string>,
         "name": <user-name>,
         "last_name": <last-name>,
         "first_name": <first-name>,
         "email": <email-address>,
         "status": <user-status>
         },
    ]\n
    Default response:
    [
        {
            "id": <ID>,
            "labels": [
                <node-label>
            ],
            "path": <nfs-path>,
            "time_lastmodified": <time-string>,
            "name": <node-name>,
            "time_created": <time-string>
        }
    ]

    """

    # because we will pass the payload to search so I have to
    # use the post to get the nodes
    @node_ns.expect(node_query_module)
    @node_ns.doc(params={'label': 'User'})
    @node_ns.response(200, post_returns)
    @node_ns.response(403, """Exception""")
    def post(self, label):
        """
        Get platform users with given pages in Administrator Console
        Usage: used for listing users, listing projects, check if user exists with given username
        """
        post_data = request.get_json()
        limit = None
        skip = None
        partial = False
        order_by = None
        order_type = None
        is_all = None
        if post_data:
            if "partial" in post_data:
                partial = post_data["partial"]
                del post_data["partial"]
            if "limit" in post_data:
                limit = post_data["limit"]
                del post_data["limit"]
            if "skip" in post_data:
                skip = post_data["skip"]
                del post_data["skip"]
            if "order_by" in post_data:
                order_by = post_data["order_by"]
                del post_data["order_by"]
            if "order_type" in post_data:
                order_type = post_data["order_type"]
                del post_data["order_type"]
            if "is_all" in post_data:
                is_all = post_data["is_all"]
                del post_data["is_all"]
        try:
            nodes = []
            if is_all:
                nodes = self.node_method.query_node(
                    label,
                    post_data,
                    partial=partial,
                    order_by=order_by,
                    order_type=order_type
                )
            else:
                nodes = self.node_method.query_node(
                    label,
                    post_data,
                    limit=limit,
                    skip=skip,
                    partial=partial,
                    order_by=order_by,
                    order_type=order_type
                )
            result = [node_2_json(x) for x in nodes]
        except Exception as e:
            return str(e), 403

        return result, 200


class CountActionOnNodeByQuery(Resource):
    # initialize the class for using the method
    node_method = Neo4jClient()

    post_returns = """
        {"count": <number-of-records>}
    """

    @node_ns.expect(node_query_module_count)
    @node_ns.doc(params={'label': 'User'})
    @node_ns.response(200, post_returns)
    @node_ns.response(403, """Exception""")
    def post(self, label):
        """
        Get number of platform users with given pages in Administrator Console
        Usage: count the number of users to be displayed in the Administrators Console
        """
        post_data = request.get_json()
        partial = False
        if "count" in post_data:
            del post_data["count"]
        if "partial" in post_data:
            partial = post_data["partial"]
            del post_data["partial"]

        try:
            res = self.node_method.query_node(
                label, post_data, count=True, partial=partial)
        except Exception as e:
            return str(e), 403

        return {"count": int(res)}, 200


class ActionOnProperty(Resource):
    # initialize the class for using the method
    node_method = Neo4jNode()

    get_returns = """
    User response:
    {"last_login": [<time-string>],
     "status": ["active", "disabled"],
     "email": [<email>],
     "first_name": [<first-name>],
     "path": ["users"],
     "role": ["admin", "member"],
     "name": [<user-name>],
     "last_name": [<last-name>],
     "realm": ["realm"]
    }\n
    Container response:
    {"code": [<project-code>],
     "description": [<project-description>],
     "admin"(no longer in use): [<[project_creator-admin]>],
     "roles": [["admin","contributor"],["admin"]],
     "discoverable": [false, true],
     "name": [<project-name>],
     "tags": [<[project-tags]>],
     "labels": [["Container"]],
     "id": [<project-ID>],
     "is_new"(no longer in use): [false,true]
    }\n
    Default response:
    {"attribute_1":["all possible value"],
     "attribute_2":["all possible value"],
    }
    """

    @node_ns.doc(params={'label': 'Container'})
    @node_ns.response(200, get_returns)
    @node_ns.response(403, """Exception""")
    def get(self, label):
        """
        Retreive the All the Property and Possible Value with Given Label
        Usage: used for getting project properties such as metadata, tag, usecase.
        """
        try:
            res = self.node_method.get_property_by_label(label)

            result = {}
            for x in res:
                temp = dict(x)
                result.update({temp["key"]: temp["options"]})

            # pop out the time type
            result.pop("time_lastmodified", None)
            result.pop("time_created", None)
        except Exception as e:
            return str(e), 403

        return result, 200


class ChangeLabels(Resource):
    node_method = Neo4jClient()

    put_returns = """
    [
        {
            "id": <ID>,
            "labels": [
                <node-label>
            ],
            "name": <node-name>,
            "time_created": <time-string>,
            "time_lastmodified": <time-string>,
            "other_property": "xxxx",
            "other_property_2": "xxxx"
        }
    ])
    """

    @node_ns.expect(labels_module)
    @node_ns.response(200, put_returns)
    @node_ns.response(403, """Exception""")
    def put(self, id):
        """
        Update the labels to match the given list
        """
        data = request.get_json()
        labels = data.get("labels")
        if not isinstance(labels, list):
            return "labels must be list", 400
        if not labels:
            return "labels is required", 400

        try:
            result = self.node_method.change_labels(int(id), labels)
            if result:
                result = [node_2_json(result)]
            else:
                result = []
        except Exception as e:
            return str(e), 403

        return result, 200


class NodeQueryAPI(Resource):
    node_method = Neo4jClient()
    response = """
    {
    'code': 200,
    'error_msg': '',
    'num_of_pages': 33,
    'page': 0,
    'result': [   {   'archived': False,
                      'description': 'description',
                      'file_size': 0,
                      'full_path': 'test/zy//testzy6',
                      'dcm_id': '',
                      'guid': '083a7459-9a2f-4b4d-bfe5-c1d683e1103c',
                      'id': 59,
                      'labels': ['Greenroom', 'Raw', 'File'],
                      'name': 'testzy6',
                      'path': 'test/zy/',
                      'time_created': '2021-01-08T17:04:04',
                      'time_lastmodified': '2021-01-08T17:04:04',
                      'uploader': 'testzy'},
    ],
    'total': 806
    }
    """

    @node_ns.response(200, response)
    @node_ns.expect(node_query_module_v2)
    def post(self):
        data = request.get_json()
        partial = data.pop("partial", False)
        order_by = data.pop("order_by", None)
        order_type = data.pop("order_type", None)
        page = data.pop("page", 0)
        page_size = data.pop("page_size", 25)
        skip = page * page_size
        limit = page_size
        query = data.get("query")
        if not query["labels"]:
            return "labels is required in query", 400
        labels = query.pop("labels")
        try:
            nodes = self.node_method.query_node(
                labels,
                query,
                limit=limit,
                skip=skip,
                partial=partial,
                order_by=order_by,
                order_type=order_type
            )
            total = self.node_method.query_node(
                labels, query, count=True, partial=partial)
            result = [node_2_json(x) for x in nodes]
        except Exception as e:
            return str(e), 403
        response = {
            'code': 200,
            'error_msg': '',
            'result': result,
            'page': page,
            'total': total,
            'num_of_pages': math.ceil(total / page_size),
        }
        return response, 200


class NodeQuickCountAPI(Resource):
    node_method = Neo4jNode()
    get_return = """
    {
        "result": [
        ]
    }
    """

    @node_ns.doc(params={
        'labels': 'Greenroom:File',
        'other_args': '[str] or [bool] or [int]'})
    @node_ns.response(200, get_return)
    def get(self):
        """
        query count in neo4j with match query syntax
        """
        try:
            labels = request.args.get('labels', None)
            if not labels:
                return "labels is required", 404
            # get query params
            query_params_kwargs = {}
            for arg_key in request.args:
                if not arg_key == 'labels':
                    query_params_kwargs[arg_key] = request.args[arg_key]
            where_condition = ""
            if query_params_kwargs:
                def convert_value(val):
                    if val.startswith('[bool]'):
                        return val.replace('[bool]', '').lower()
                    if val.startswith('[int]'):
                        return val.replace('[int]', '')
                    return '"{}"'.format(val)

                where_condition = " and ".join(['n.{}={}'.format(key, convert_value(query_params_kwargs[key]))
                                                for key in query_params_kwargs])
            query = 'MATCH (n:{}) '.format(labels)
            if where_condition:
                query += " where {}".format(where_condition)
            query += " RETURN count(n) as count"
            print(query)
            res = neo_quick_query(query)
            for record in res:
                result = record.items()[0][1]
            return {"result": result}, 200
        except Exception as e:
            print(e)
            return str(e), 403


class FileQuickCountAPI(Resource):
    node_method = Neo4jNode()
    get_return = """
    {
        "result": [
        ]
    }
    """

    @node_ns.doc(params={
        'labels': 'Greenroom:File',
        'other_args': '[str] or [bool] or [int]'})
    @node_ns.response(200, get_return)
    def get(self):
        """
        only can be used for file data
        """
        try:
            labels = request.args.get('labels', None)
            if not labels:
                return "labels is required", 404
            # get query params
            query_params_kwargs = {}
            for arg_key in request.args:
                if arg_key != 'labels' and arg_key != 'startwith':
                    query_params_kwargs[arg_key] = request.args[arg_key]
            project_code = "{}".format(query_params_kwargs['project_code'])
            del query_params_kwargs['project_code']
            startwith = request.args.get('startwith', [])
            where_condition = ""
            if query_params_kwargs:
                def convert_value(val):
                    if val.startswith('[bool]'):
                        return val.replace('[bool]', '').lower()
                    if val.startswith('[int]'):
                        return val.replace('[int]', '')
                    return '"{}"'.format(val)

                def condition_generator(key, value):
                    operator = " STARTS WITH " if key in startwith else "="
                    generated = 'n.{}{}{}'.format(
                        key, operator, convert_value(value))
                    return generated

                where_condition = " and ".join([condition_generator(key, query_params_kwargs[key])
                                                for key in query_params_kwargs])
            query = 'MATCH (n:{}) <-[r:own*]-(p:Container) where p.code="{}"'.format(
                labels, project_code)
            if where_condition:
                query += " and {}".format(where_condition)
            query += " RETURN count(n) as count"
            print(query)
            res = neo_quick_query(query)
            for record in res:
                result = record.items()[0][1]
            return {"result": result}, 200
        except Exception as e:
            print(e)
            return str(e), 403


class BatchUpdate(Resource):
    """This API helps batch update of labels for listed nodes based on geid"""
    response = """"{
        "result":
        [{'id': 49, 'labels': ['Folder', 'Core'], 'global_entity_id': '6785869f-b017-4ed3-b602-a4ce7e8dcda2-1621605134', 'display_path': 'admin/test_copy_rename_36/testzy3/test_dest/test_copy_rename_56/testzyparent_34', 'project_code': 'test0511', 'tags': ['test_bulk123'], 'folder_level': 2, 'archived': False, 'list_priority': 10, 'folder_relative_path': 'admin/test_copy_rename_36/testzy3/test_dest/test_copy_rename_56', 'time_lastmodified': '2021-06-01T13:13:09', 'uploader': 'admin', 'system_tags': ['copied-to-core'], 'name': 'testzyparent_34', 'time_created': '2021-05-21T13:52:14'}]
        }"""

    @node_ns.response(200, response)
    @node_ns.expect(node_batch_update)
    def put(self, node_property):
        try:
            post_data = request.get_json()
            data = post_data.get('data')

            query = f'UNWIND $data as p ' \
                    f'MATCH (n) where n.global_entity_id = p.global_entity_id SET n.{node_property} = p.{node_property} return n'
            neo4j_session = neo4j_connection.session()
            res = neo4j_session.run(query, data=data)
            result = [neo4j_obj_2_json(x).get('n') for x in res]
            return {"result": result}, 200
        except Exception as error:
            return str(error), 403

class QueryByGeidBulk(Resource):
    node_method = Neo4jClient()

    def post(self):
        data = request.get_json()
        geids = data.pop("geids", [])
        if not geids:
            return "geids parameter is required", 400

        try:
            nodes = self.node_method.query_by_geid_bulk(geids)
            total = len(nodes)
            result = [node_2_json(x) for x in nodes]
        except Exception as e:
            return "Error running neo4j query: " + str(e), 500

        response = {
            'code': 200,
            'error_msg': '',
            'result': result,
            'page': 0,
            'total': total,
            'num_of_pages': 1,
        }
        return response, 200


class BulkUpdate(Resource):
    node_method = Neo4jClient()

    # https://py2neo.org/2021.1/bulk/index.html?highlight=bulk#py2neo.bulk.create_nodes
    def put(self):
        put_data = request.get_json()
        data = put_data.get("data")
        merge_key = put_data.get("merge_key")
        if not data or not merge_key:
            return {"error_msg": "Missing required parameter"}, 400

        merge_key = tuple(merge_key)

        try:
            self.node_method.bulk_update_nodes(data, merge_key)
        except Exception as e:
            return {"error_msg": "Error running neo4j query: " + str(e)}, 500
        return {"result": "success"}, 200
