#
# this file is the basic operation on the neo4j includes
# add the node and relationship to fullfill the basic
# requirement on the neo4j
#

from datetime import datetime

from . import neo4j_connection
from config import ConfigClass
from utils import neo4j_obj_2_json, path_2_json, node_2_json
from services.logger_services.logger_factory_service import SrvLoggerFactory
from py2neo import Graph, Node, Relationship
from py2neo.bulk import create_nodes, create_relationships, merge_nodes
from py2neo.matching import RelationshipMatcher, NodeMatcher, CONTAINS, LIKE, OR, IN
import neotime
import ast
import re


class Neo4jClient(object):

    def __init__(self):
        self._logger = SrvLoggerFactory('api_invitation').get_logger()
        try:
            self.graph = Graph(
                ConfigClass.NEO4J_URL,
                username=ConfigClass.NEO4J_USER,
                password=ConfigClass.NEO4J_PASS,
                max_connections=200,
            )
            self.nodes = NodeMatcher(self.graph)
            self.relationships = RelationshipMatcher(self.graph)
        except Exception as e:
            self._logger.error(
                "Error in __init__ connecting to Neo4j:" + str(e))

    def bulk_add_node(self, label, data, extra_labels=[]):
        if extra_labels and len(extra_labels) > 0:
            extra_labels = set(extra_labels)
            extra_labels.add(label)

        # new add attribute here to add time_create&time_modified
        for node in data:
            node.update({
                "time_created": neotime.DateTime.utc_now(),
                "time_lastmodified": neotime.DateTime.utc_now(),
            })

        result = create_nodes(self.graph.auto(), data, labels=extra_labels)

        return result

    def bulk_update_nodes(self, data, merge_key):
        merge_nodes(self.graph.auto(), data, merge_key)

    def add_node(self, label, name, param={}):
        if label[0].isnumeric():
            raise Exception("Invalid input")

        extra_labels = param.get("extra_labels")
        if extra_labels:
            if not isinstance(extra_labels, list):
                raise Exception("extra_labels needs to be a list")
            del param["extra_labels"]

        node = Node(
            label,
            name=name,
            time_created=neotime.DateTime.utc_now(),
            time_lastmodified=neotime.DateTime.utc_now(),
            **param,
        )

        if extra_labels:
            for label in extra_labels:
                if not node.has_label(label):
                    node.add_label(label)
        parent_id = param.pop("parent_id", None)
        parent_relation = param.pop("parent_relation", None)
        # if we have parent then add relationship
        if parent_id and parent_relation:
            end_node = self.nodes.get(parent_id)
            relationship = Relationship(node, parent_relation, end_node)
            self.graph.create(relationship)
        self.graph.create(node)
        return node

    def get_node(self, label, id):
        return self.graph.nodes.match(label).where("id(_) = %d" % id).first()
        # return self.graph.nodes.get(id)

    def get_node_by_geid(self, geid):
        return self.graph.nodes.match(**{"global_entity_id": geid}).first()
        # return self.graph.nodes.get(id)

    def query_by_geid_bulk(self, geids):
        return self.graph.nodes.match().where(**{"global_entity_id": IN(geids)})

    # in order to facilitate the query in the frontend
    # we provide all the possible key with value with it
    def get_property_by_label(self, label):
        #neo4j_session = neo4j_connection.session()
        # query = 'MATCH (n:%s) UNWIND keys(n) as key \
        #    return key, collect(distinct n[key]) as options' % (label)
        #res = neo4j_session.run(query)
        # return res
        return self.nodes.match(label).all()

    def update_node(self, label, id, params={}, update_modified_time=True):
        node = self.get_node(label, id)

        extra_labels = params.get("extra_labels")
        if extra_labels:
            if not isinstance(extra_labels, list):
                raise Exception("extra_labels needs to be a list")
            del params["extra_labels"]

        if update_modified_time:
            node.update(**params, time_lastmodified=neotime.DateTime.utc_now())
        else:
            node.update(**params)

        if extra_labels:
            for label in extra_labels:
                if not node.has_label(label):
                    node.add_label(label)
        self.graph.push(node)
        return node

    def change_labels(self, id, labels):
        node = self.graph.nodes.get(id)
        node.clear_labels()
        node.update_labels(labels)
        self.graph.push(node)
        return node

    def query_node(self, label, params=None, limit=None, skip=None, count=False, partial=False, order_by=None, order_type=None):
        tags = []
        query_params = {}
        create_time = {}
        for key, value in params.items():
            if "create_time" in key:
                create_time[key] = value
            elif key == "tags":
                tags = value
                if type(value) is str:
                    tags = ast.literal_eval(value)
            elif key == "description":
                # LIKE uses a regex, so we use regex escape for special characters
                #value = re.escape(value)
                value = re.escape(value)
                if partial:
                    query_params[key] = LIKE(f"(?i)(?s)(?m).*{value}.*")
                else:
                    query_params[key] = LIKE(f"(?i)(?s)(?m){value}")
            elif key == "location":
                query_params[key] = value
            elif key == "full_path" and not partial:
                query_params[key] = value
            elif key == "status" and isinstance(value, list):
                query_params[key] = IN(value)
            elif isinstance(value, str):
                # LIKE uses a regex, so we use regex escape for special characters
                value = re.escape(value)
                if partial:
                    query_params[key] = LIKE(f"(?i).*{value}.*")
                else:
                    query_params[key] = LIKE(f"(?i){value}")
            elif key == "id":
                query = self.nodes.match(label)
                query = query.where("id(_) = %d" % value)
                return query.all()
            else:
                query_params[key] = value

        if isinstance(label, str):
            label = [label]

        if query_params:
            query = self.nodes.match(*label, **query_params)
        else:
            query = self.nodes.match(*label)

        if create_time:
            start = create_time.get(
                "create_time_start", datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"))
            end = create_time.get(
                "create_time_end", datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"))
            query = query.where(
                f"datetime(_.time_created) > datetime('{start}')")
            query = query.where(
                f"datetime(_.time_created) < datetime('{end}')")
        if tags:
            for tag in tags:
                tag = tag.replace("\\", "\\\\")
                query = query.where(f"'{tag}' IN _.tags")

        if count:
            return query.count()
        if order_by:
            if order_type and order_type.lower() == "desc":
                order_by = f"_.{order_by} DESC"
            else:
                order_by = f"_.{order_by}"
            query = query.order_by(order_by)
        if limit:
            query = query.limit(limit)
        if skip:
            query = query.skip(skip)
        return query.all()

    # method allow to query the relationship
    # also the parameter allow the none so that we can query the 1-to-1
    def get_relation(self, relation_label, start_id=None, end_id=None):
        start_node = None
        end_node = None
        if start_id:
            start_node = self.nodes.get(start_id)
        if end_id:
            end_node = self.nodes.get(end_id)

        # avoid case of id = 0
        if not str(start_node) or not str(end_node):
            return []
        if relation_label:
            return self.relationships.match((start_node, end_node), r_type=relation_label).all()
        else:
            return self.relationships.match((start_node, end_node)).all()

    def bulk_add_relation_between_nodes(self, relation_label, data, start_params_key=None, end_params_key=None):
        if start_params_key and not end_params_key:
            result = create_relationships(
                self.graph.auto(), data, relation_label, start_node_key=start_params_key)
            return result
        if end_params_key and not start_params_key:
            result = create_relationships(
                self.graph.auto(), data, relation_label, end_node_key=end_params_key)
            return result
        if end_params_key and start_params_key:
            result = create_relationships(
                self.graph.auto(), data, relation_label, end_node_key=end_params_key, start_node_key=start_params_key)
            return result
        if not end_params_key and not start_params_key:
            result = create_relationships(
                self.graph.auto(), data, relation_label)
            return result

    def add_relation_between_nodes(self, relation_label, start_id, end_id, properties={}):
        if type(start_id) == list and type(end_id) == list:
            raise Exception('Both start_id and end_id can be the list')
        if start_id == end_id:
            raise Exception("Error cannot add yourself as parent/child")
        start_node = self.nodes.get(start_id)
        end_node = self.nodes.get(end_id)
        relationship = self.relationships.match((start_node, end_node)).first()
        if hasattr(relationship, "start_node") and hasattr(relationship, "end_node"):
            raise Exception("dataset(s) already be the parent(s).")
        relationship = Relationship(start_node, relation_label, end_node)
        for key, value in properties.items():
            relationship[key] = value
        self.graph.create(relationship)
        return relationship

    def update_relation(self, label, new_label, start_id, end_id, properties={}):
        start_node = self.nodes.get(start_id)
        end_node = self.nodes.get(end_id)
        relationship = self.relationships.match((start_node, end_node)).first()
        if not properties:
            properties = dict(relationship)
        self.graph.separate(relationship)
        relationship = Relationship(start_node, new_label, end_node)
        for key, value in properties.items():
            relationship[key] = value
        self.graph.create(relationship)
        return relationship

    def delete_relation(self, start_id, end_id):
        start_node = self.nodes.get(start_id)
        end_node = self.nodes.get(end_id)
        if start_node and end_node:
            relationship = self.relationships.match(
                (start_node, end_node)).first()
            self.graph.separate(relationship)
            return relationship
        else:
            raise Exception

    def delete_node(self, label, id):
        node = self.graph.nodes.match(label).where("id(_) = %d" % id).first()
        if node:
            self.graph.separate(node)
            self.graph.delete(node)
        else:
            raise Exception


class Neo4jNode(object):
    # todo move the neo4j_connection here?

    # in order to facilitate the query in the frontend
    # we provide all the possible key with value with it
    def get_property_by_label(self, label):
        neo4j_session = neo4j_connection.session()

        query = 'MATCH (n:%s) UNWIND keys(n) as key \
            return key, collect(distinct n[key]) as options' % (label)

        res = neo4j_session.run(query)

        return res

    # delete node recursively, this function does not have API, test only
    def delete_node(self, node_id):
        neo4j_session = neo4j_connection.session()
        query = "MATCH (n:test_label) \
                 where id(n)=%s \
                 DETACH DELETE n" % node_id
        res = neo4j_session.run(query)

        return res


class Neo4jRelationship(object):

    # note here it is not necessary to have label and parameter
    def get_relation_with_params(self, relation_label=None,
                                 start_label=None, end_label=None,
                                 start_params=None, end_params=None,
                                 count=False, partial=False, page_kwargs={}, extra_query="", sort_node="end"):
        def format_label(label):
            if isinstance(label, list):
                result = ""
                for l in label:
                    if(l):
                        result += ":" + l
                return result
            else:
                if(label):
                    return ':'+label
                return ''

        relation_label = format_label(relation_label)
        start_label = format_label(start_label)
        end_label = format_label(end_label)

        create_time = {}

        query = 'match p=(start_node%s)-[r%s]->(end_node%s) %s' % (
                start_label, relation_label, end_label, extra_query)

        if(isinstance(start_params, dict)):
            query += 'where'
            for key, value in start_params.items():
                if type(value) == str:
                    value = "'%s'" % value

                # id have special function
                if key == 'id':
                    query += ' Id(start_node) = {value} and'.format(value=value)
                else:
                    if partial:
                        if key == 'name':
                            query += ' start_node.{key} CONTAINS {value} and'.format(
                                key=key, value=value)
                        else:
                            query += ' start_node.{key} contains {value} and'.format(
                                key=key, value=value)
                    else:
                        query += ' start_node.{key} = {value} and'.format(
                            key=key, value=value)
            query = query[:-3]

        if(isinstance(end_params, dict)):
            query += 'with * where'
            for key, value in end_params.items():
                if type(value) == str:
                    value = "'%s'" % value
                # id have special function
                if key == 'id':
                    query += ' Id(end_node) = {value} and'.format(value=value)
                elif "create_time" in key:
                    create_time[key] = value
                elif key == 'tags':
                    for tag in value:
                        tag = tag.replace("\\", "\\\\")
                        query += f' "{tag}" IN end_node.tags and'
                else:
                    # Exclude from partial search in == is in value
                    if value and isinstance(value, str) and value.startswith("'=="):
                        value = "'" + value[3:]
                        partial_exclude = True
                    else:
                        partial_exclude = False

                    if partial_exclude or isinstance(value, bool) or isinstance(value, int):
                        if key in ["container_id"] or isinstance(value, bool) or isinstance(value, int):
                            query += ' end_node.{key} = {value} and'.format(
                                key=key, value=value)
                        else:
                            query += ' TOLOWER(end_node.{key}) = TOLOWER({value}) and'.format(
                                key=key, value=value)
                    else:
                        if partial and value:
                            if key in ["container_id"]:
                                query += ' end_node.{key} CONTAINS {value} and'.format(
                                    key=key, value=value)
                            else:
                                query += ' TOLOWER(end_node.{key}) CONTAINS TOLOWER({value}) and'.format(
                                    key=key, value=value)
                        else:
                            if key in ["container_id"]:
                                query += ' end_node.{key} = {value} and'.format(
                                    key=key, value=value)
                            else:
                                query += ' TOLOWER(end_node.{key}) = TOLOWER({value}) and'.format(
                                    key=key, value=value)
            if create_time:
                start = create_time.get(
                    "create_time_start", "'" + datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S") + "'")
                end = create_time.get(
                    "create_time_end", "'" + datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S") + "'")
                query += f" datetime(end_node.time_created) > datetime({start}) and"
                query += f" datetime(end_node.time_created) < datetime({end}) and"
            query = query[:-3]
        if count:
            query += 'return count(*)'
        else:
            query += 'return *'
            if page_kwargs.get("order_by"):
                order = page_kwargs['order_by']
                if sort_node == "start":
                    query += f' ORDER BY start_node.{order}'
                else:
                    query += f' ORDER BY end_node.{order}'
            if page_kwargs.get("order_type"):
                order_type = page_kwargs['order_type']
                query += f' {order_type}'
            if page_kwargs.get("skip"):
                skip = page_kwargs["skip"]
                query += f' skip {skip}'
            if page_kwargs.get("limit"):
                limit = page_kwargs["limit"]
                query += f' limit {limit}'

        neo4j_session = neo4j_connection.session()
        res = neo4j_session.run(query)

        return res

    # method allow to query the nodes on other side of relation
    # also the parameter allow the none so that we can query the
    # 1-to-n, n-to-1 if start == True -> node_id-to-others
    def get_node_along_relation(self, relation_label, node_id, start=True):
        query = 'match r=(start_node)-[:%s]->(end_node) ' % relation_label

        # now start add the start node and end node condition
        if start:
            query += 'where ID(start_node)=$node_id return end_node as node'
        else:
            query += 'where ID(end_node)=$node_id return start_node as node'

        neo4j_session = neo4j_connection.session()
        res = neo4j_session.run(query, node_id=node_id)

        return res

    def relation_query_multiple_labels(self, start_label, end_labels, query_params={}, page_kwargs={}):
        start_query = query_params.get("start_params", {})
        end_query = query_params.get("end_params", {})
        neo_query = f"MATCH p=(start_node:{start_label}"
        neo_params = {}
        count = 0
        for key, value in start_query.items():
            neo_query += "{" + key + ":$start_value_" + str(count) + "}"
            neo_params[f"start_value_{count}"] = value
            count += 1
        neo_query += ")-[r]->(end_node) WITH * "

        neo_query += "WHERE "
        count = 0
        for label in end_labels:
            neo_query += f"(end_node:{label}"
            neo_params[f"end_label_{count}"] = label
            param_count = 0
            partial_fields = end_query.get(label, {}).pop("partial", [])
            startswith_fields = end_query.get(label, {}).pop("startswith", [])
            for key, value in end_query.get(label, {}).items():
                if not isinstance(value, str) and key in partial_fields:
                    raise Exception(
                        "Only string parameters can use partial search")
                if key == "id":
                    neo_query += f" AND ID(end_node) = $end_query_value_{count}{param_count}"
                # elif key in ["time_created", "time_lastmodified"]:
                #    pass
                else:
                    if partial_fields and key in partial_fields:
                        neo_query += f" AND TOLOWER(end_node.{key}) CONTAINS TOLOWER($end_query_value_{count}{param_count})"
                    elif startswith_fields and key in startswith_fields:
                        neo_query += f" AND TOLOWER(end_node.{key}) STARTS WITH TOLOWER($end_query_value_{count}{param_count})"
                    else:
                        neo_query += f" AND end_node.{key} = $end_query_value_{count}{param_count}"
                neo_params[f"end_query_value_{count}{param_count}"] = value
                param_count += 1
            neo_query += ")"
            count += 1
            if count != len(end_labels):
                neo_query += " OR "
        neo_count = neo_query + " RETURN count(*)"
        neo4j_session = neo4j_connection.session()
        total = neo4j_session.run(neo_count, **neo_params)
        total = total.value()[0]

        neo_query += " RETURN *"
        if page_kwargs.get("order_by"):
            order = page_kwargs['order_by']
            neo_query += f' ORDER BY end_node.{order}'
        if page_kwargs.get("order_type"):
            order_type = page_kwargs['order_type']
            if not order_type.lower() in ["desc", "asc"]:
                raise Exception("Invalid order_type")
            neo_query += f' {order_type}'
        if page_kwargs.get("skip"):
            skip = page_kwargs["skip"]
            neo_query += f' skip {skip}'
        if page_kwargs.get("limit"):
            limit = page_kwargs["limit"]
            neo_query += f' LIMIT {limit}'
        neo4j_session = neo4j_connection.session()
        print(neo_query, neo_params)
        result = neo4j_session.run(neo_query, **neo_params)
        return result, total

    def get_connected_nodes(self, global_entity_id, relation='own', direction='input'):
        neo4j_session = neo4j_connection.session()
        query_map_direction = {
            "input": 'MATCH ({global_entity_id: $geid})<-[:' + relation + '*]-(connected) RETURN connected as node',
            "output": 'MATCH ({global_entity_id: $geid})-[:' + relation + '*]->(connected) RETURN connected as node',
            "both": 'MATCH ({global_entity_id: $geid})<-[:' + relation + '*]->(connected) RETURN connected as node'
        }.get(direction.lower())
        res = neo4j_session.run(query_map_direction, geid=global_entity_id)

        return res


def neo_quick_query(query):
    '''
    quick count number of nodes in neo4j
    '''
    neo4j_session = neo4j_connection.session()
    res = neo4j_session.run(query)
    return res
