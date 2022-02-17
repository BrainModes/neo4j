from neo4j_api import neo4j_connection

neo4j_session = neo4j_connection.session()

user_init = 'create (n:User) set n = {email:"ivana.zhangyf@gmail.com", \
first_name:"admin", last_name:"admin", name:"stage-admin", path:"users", role:"admin"} return n'

neo4j_session.run(user_init)


db_constraint_init = '''
    CREATE CONSTRAINT constraint_code
    ON (n:Container)
    ASSERT n.code IS UNIQUE
'''

neo4j_session.run(db_constraint_init)