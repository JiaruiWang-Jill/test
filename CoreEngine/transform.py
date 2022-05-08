import json

def load_mysql_data_into_kafka(my_sql_result):
    res = json.loads(my_sql_result)
    kafka_params = "topic_name:" + res["name"]
    return [kafka_params]