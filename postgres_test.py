from core.postgres_managers.db_manager import PostgresDBManager
from core.postgres_managers.connection_manager import PostgresConnectionManager

db_manager = PostgresDBManager()
conn_manager = PostgresConnectionManager(db_manager)

# def convert_connection_data_to_json(data):
#     json_list = []

#     for d in data:
#         json_list.append({
#             "name" : d[0],
#             "user": d[1],
#             "password": d[2],
#             "dsn": d[3]
#         })

#     return json_list

# data = conn_manager.load_connections()
# json_list = convert_connection_data_to_json(data)
# print(json_list)

conn = db_manager.get_connection()
print(conn.autocommit)
db_manager.release_connection(conn)


