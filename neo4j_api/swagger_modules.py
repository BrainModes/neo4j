from flask_restx import Api, Resource, fields

from . import module_api

def return_all(res):
    return res

node_module = module_api.model('node_module', {
    "id": fields.Integer(readOnly=True, description='Unique id of neo4j node'),
    # "labels": fields.List(fields.String, readOnly=True, description='The labe of the node'),
    # "name": fields.String(readOnly=True, description='The name of the node(allow duplication)'),
    # "path": fields.String(readOnly=True, description='The path store in nfs'),
    # "time_created": fields.String(readOnly=True, description='Time when node is created'),
    # "time_lastmodified": fields.String(readOnly=True, description='The path store in nfs')
}, mask=return_all)

path_module_simple  = module_api.model('path_module_simple',{
    "id": fields.Integer(readOnly=True, description='Unique id of neo4j node'),
    "children": fields.String(readOnly=True, description='Nested dict')
})
path_module  = module_api.model('path_module',{
    "node_name": fields.Nested(path_module_simple, readOnly=True, description='node info and children info')
})

relation_module = module_api.model('relation_module',{
	"type": fields.String(readOnly=True, description='Label of relationship')
})

# genitic_module

property_module = module_api.model('property_module', {
    "property_key": fields.List(fields.String, readOnly=True, description='List of possible values'),
})

node_update_module = module_api.model('node_update_module', {

    "role": fields.String(readOnly=True, description="(User) user's role in platform"),
    "status": fields.String(readOnly=True, description="(User) The user's status"),

    "name": fields.String(readOnly=True, description='(Dataset) The name of the node(allow duplication)'),
    "discoverable": fields.String(readOnly=True,
                                  description='(Dataset) Whether the project should be discovered by all platform user, or only project members'),
"description": fields.String(readOnly=True, description='(Dataset) The description of the project'),
    "tags": fields.List(fields.String, readOnly=True, description="(Dataset) The tags added to the project"),

    "new_property_1": fields.String(readOnly=True, description='If property does not exist, neo4j will create it'),
    "update_property_2": fields.String(readOnly=True, description='If property exist, neo4j will update value'),
})


node_create_module = module_api.model('node_create_module', {
    "name": fields.String(readOnly=True, description='The name of the node(allow duplication)'),
    "path": fields.String(readOnly=True, description='The path store in nfs'),

    "email": fields.String(readOnly=True, description='(User) The email that user used for self-registrar'),
    "first_name": fields.String(readOnly=True, description='(User) The first name that user used for self-registrar'),
    "last_name": fields.String(readOnly=True, description='(User) The last name that user used for self-registrar'),
    "role": fields.String(readOnly=True, description="(User) user's role in platform"),
    "status": fields.String(readOnly=True, description="(User) The user's status"),

    "code": fields.String(readOnly=True, description='(Dataset) The project code used for creating project'),
    "description": fields.String(readOnly=True, description='(Dataset) The description of the project'),
    "discoverable": fields.Boolean(readOnly=True, description='(Dataset) Whether the project should be discovered by all platform user, or only project members'),
    "roles": fields.List(fields.String, readOnly=True, description="(Dataset) The possible roles in the project"),
    "type": fields.String(readOnly=True, description="(Dataset) The type of project, default is 'Usecase'"),
    "tags": fields.List(fields.String, readOnly=True, description="(Dataset) The tags added to the project"),
    "metadatas": fields.Raw(readOnly=True, description="(Dataset) Default value {}"),


    "other_property_1": fields.String(readOnly=True, description='(optional) others are the attributes you want to attach to node'),
    "other_property_2": fields.String(readOnly=True, description='(optional) others are the attributes you want to attach to node'),
})

node_query_module = module_api.model('node_query_module', {
    "limit": fields.Integer(readOnly=True, description='page_size, number of records to be displayed per page'),
    "skip": fields.Integer(readOnly=True, description='page*page_size, total number of records to skip'),
    "order by": fields.String(readOnly=True, description="The column to be sorted, default order by 'time_created',"
                                                         "other options are: 'name', 'email', 'first_name', 'last_name', 'last_login'"),
    "order_type": fields.String(readOnly=True, description='The sorting method, default by desc, can choose asc'),
    "name (optional)": fields.String(readOnly=True, description="The characters that account 'name' contains for filtering"),
    "email (optional)": fields.String(readOnly=True, description="The characters that account 'email' contains for filtering"),

})

node_query_module_count = module_api.model('node_query_module_count', {
    "count": fields.Boolean(readOnly=True, description='number of records'),
    "partial": fields.Boolean(readOnly=True, description='whether enable partial search'),
    "name (optional)": fields.String(readOnly=True, description="The characters that account 'name' contains for filtering"),
    "email (optional)": fields.String(readOnly=True, description="The characters that account 'email' contains for filtering"),
})

labels_module = module_api.model('labels_change', {
    "labels": fields.List(fields.String, readOnly=True, description='List of labels the node will be updated to'),
})

file_module = module_api.model('file_create', {
     "file_size": fields.Integer(description="file_size in bytes"),
     "full_path": fields.String(description="full_path to file"),
     "dcm_id": fields.String(description="dcm_id"),
     "guid": fields.String(description="guid from atlas"),
     "namespace": fields.String(description="greenroom or core"),
     "type": fields.String(description="raw or processed"),
     "uploader": fields.String(description="file uploader"),
     "project_id": fields.Integer(description="neo4j id for dataset"),
     "input_file_id": fields.Integer(description="neo4j id for input file to create relationship with"),
     "process_pipeline": fields.String(description="name of pipeline"),
})

query = module_api.model('file_query', {
    'archived': fields.Boolean(),
    'description': fields.String(example="description"),
    'file_size': fields.Integer(),
    'full_path': fields.String(example="/data/storage/raw/test_seeds"),
    'dcm_id': fields.String(),
    'guid': fields.String(example="f1547da2-8372-4ae3-9e2b-17c80e97f113"),
    'name': fields.String(example="testzy9.txt"),
    'path': fields.String(example="test/zy"),
    'time_created': fields.String(example="2021-01-08T17:09:51"),
    'time_lastmodified': fields.String(example="2021-01-08T17:09:51"),
    'uploader': fields.String(example="admin"),
    'labels': fields.List(fields.String, example=['File', 'Greenroom', 'Raw']),
})
file_query_module = module_api.model('file_query_module', {
     "page": fields.Integer(),
     "page_size": fields.Integer(),
     "partial": fields.Boolean(),
     "order_by": fields.String(example="name"),
     "order_type": fields.String(example="desc"),
     "query": fields.Nested(query)
})

node_query = module_api.model('query', {
    'archived': fields.Boolean(),
    'description': fields.String(example="description"),
    'file_size': fields.Integer(),
    'full_path': fields.String(example="/data/storage/raw/test_seeds"),
    'dcm_id': fields.String(),
    'guid': fields.String(example="f1547da2-8372-4ae3-9e2b-17c80e97f113"),
    'name': fields.String(example="testzy9.txt"),
    'path': fields.String(example="test/zy"),
    'time_created': fields.String(example="2021-01-08T17:09:51"),
    'time_lastmodified': fields.String(example="2021-01-08T17:09:51"),
    'uploader': fields.String(example="admin"),
    'labels': fields.List(fields.String, example=['File', 'Greenroom', 'Raw']),
})
node_query_module_v2 = module_api.model('node_query', {
     "page": fields.Integer(),
     "page_size": fields.Integer(),
     "partial": fields.Boolean(),
     "order_by": fields.String(example="name"),
     "order_type": fields.String(example="desc"),
     "query": fields.Nested(node_query)
})

trashfile_module = module_api.model('file_trash', {
     "trash_full_path": fields.String(description="full_path to trash file"),
     "full_path": fields.String(description="full_path to file"),
})

node_batch_update = module_api.model('',{
    'data': fields.List(fields.String, example=[{'global_entity_id': "6785869f-b017-4ed3-b602-a4ce7e8dcda2-1621605134", 'tags': ["test_bulk123"]},
   ]
)
})

#######################################################################
