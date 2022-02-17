#
# so as the neo4j it requires the connection
# as the mandetory parameter in the config file
#

# from flask_restful import Api
from flask_restx import Api, Resource, fields
from config import ConfigClass
from neo4j import GraphDatabase

# first check the necessary config parameter
required_parameters = ["NEO4J_URL", "NEO4J_PASS", "NEO4J_USER"]
for x in required_parameters:
	if not getattr(ConfigClass, x, None):
		raise Exception("Error: Missing the attribute %s in config."%x)


neo4j_connection = GraphDatabase.driver(ConfigClass.NEO4J_URL, 
	auth=(ConfigClass.NEO4J_USER, ConfigClass.NEO4J_PASS),encrypted=False)

page_description="Neo4j is the GraphDB modeling used in project. " \
				 "As of the Release 0.2.0, there are 2 different types" \
				 " of node that are used to model the projects, users, and the " \
				 "relationships between them. " \
				 "Once a project is created from the portal, a project node, " \
				 "labelled as Dataset, will be created in neo4j.  When a user " \
				 "was added into the project via the portal, a user node, " \
				 "will be created if not already exists, is then connected to " \
				 "that project node with the relationship to indicate hers role " \
				 "in that project. \n\n" \
				 "Some useful links: \n\n " \
				 "\n"

module_api = Api(version='1.0', title='Neo4j API',
    			 description=page_description, doc='/v1/api-doc')

# create namespace for node
node_ns = module_api.namespace('Node', description='Operation on Neo4j Nodes', path ='/')
# create namespace for relationship
relationship_ns = module_api.namespace('Relationship', description='Operation on Neo4j Relationship', path ='/')


from .neo4j_node_api import (
	ActionOnNodeById, 
	ActionOnNodeByGeid,
	CreateNode, 
    BatchCreateNode,
	ActionOnNodeByQuery, 
	CountActionOnNodeByQuery, 
	ActionOnProperty,
    ChangeLabels,
    NodeQueryAPI,
	NodeQuickCountAPI,
	FileQuickCountAPI,
	BatchUpdate,
    QueryByGeidBulk,
    BulkUpdate,
)
from .neo4j_relation_api import (
	RelationshipActions, 
 	BatchRelationshipActions,
	RelationshipActionsLabelOption, 
	ActionOnRelationshipByQuery,
	CountActionOnRelationshipByQuery,
	ActionOnNodeByRelationships,
	RelationshipQueryV2,
	RelationConnected
)


node_ns.add_resource(ActionOnNodeById, '/v1/neo4j/nodes/<label>/node/<id>')
node_ns.add_resource(ActionOnNodeByGeid, '/v1/neo4j/nodes/geid/<geid>')
node_ns.add_resource(CreateNode, '/v1/neo4j/nodes/<label>')
node_ns.add_resource(BatchCreateNode, '/v1/neo4j/nodes/<label>/batch')
node_ns.add_resource(ActionOnNodeByQuery, '/v1/neo4j/nodes/<label>/query')
node_ns.add_resource(CountActionOnNodeByQuery, '/v1/neo4j/nodes/<label>/query/count')
node_ns.add_resource(NodeQueryAPI, '/v2/neo4j/nodes/query')
node_ns.add_resource(NodeQuickCountAPI, '/v1/neo4j/nodes/quick/count')
node_ns.add_resource(FileQuickCountAPI, '/v1/neo4j/file/quick/count')
node_ns.add_resource(BatchUpdate,'/v1/neo4j/nodes/<node_property>/batch/update')
node_ns.add_resource(ActionOnProperty, '/v1/neo4j/nodes/<label>/properties')
node_ns.add_resource(ChangeLabels, '/v1/neo4j/nodes/<id>/labels')
node_ns.add_resource(QueryByGeidBulk, '/v1/neo4j/nodes/query/geids')
node_ns.add_resource(BulkUpdate, '/v2/neo4j/nodes/batch/update')

relationship_ns.add_resource(RelationshipActions, '/v1/neo4j/relations/<label>')
relationship_ns.add_resource(BatchRelationshipActions, '/v1/neo4j/relations/<label>/batch')
relationship_ns.add_resource(RelationshipActionsLabelOption, '/v1/neo4j/relations')

relationship_ns.add_resource(ActionOnRelationshipByQuery, '/v1/neo4j/relations/query')
relationship_ns.add_resource(CountActionOnRelationshipByQuery, '/v1/neo4j/relations/query/count')
relationship_ns.add_resource(RelationshipQueryV2, '/v2/neo4j/relations/query')
relationship_ns.add_resource(ActionOnNodeByRelationships, '/v1/neo4j/relations/<label>/node/<id>')

relationship_ns.add_resource(RelationConnected, '/v1/neo4j/relations/connected/<geid>')

# # Actions on specific dataset
# module_api.add_resource(dataset, '/v1/datasets/<dataset_id>')

# # relationship between dataset and dataset
# module_api.add_resource(dataset_relation_child, '/v1/datasets/<dataset_id>/relations/children')
# module_api.add_resource(dataset_relation_parent, '/v1/datasets/<dataset_id>/relations/parent')
# module_api.add_resource(dataset_relation_none, '/v1/datasets/<dataset_id>/relations/none')

# module_api.add_resource(files, '/v1/<dataset_id>/files')

# # Actions on multiple users
# module_api.add_resource(dataset_users, '/v1/datasets/<dataset_id>/users')

# # Actions on the specific user
# module_api.add_resource(dataset_user, '/v1/datasets/<dataset_id>/users/<username>')


# module_api.add_resource(users, '/v1/users')
# module_api.add_resource(user_dataset_query, '/v1/users/<username>/datasets')

# test for the general neo4j api
# module_api.add_resource(neo4j_node, '/v1/neo4j/node')
