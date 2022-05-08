import http.client
import json
import threading
import CoreEngine.transform
from CoreEngine.Parser import Parser

def command_line(user_id, task_list, multi_thread):
    # Check whether user exists
    parser = Parser(user_id)
    if not parser.find_user():
        print("User doesn't exist")
        return None

    # Validate the given tasks
    for task in task_list:
        split_task = task.split(" ")
        operation = split_task[0]
        params = split_task[1:]
        if ' > ' not in task and not parser.check_permission(task=operation, params=params):
            # this user doesn't have permission to this specific task
            print("User doesn't have permission to: " + task)
            return None

    result = []
    thread_list = []
    for task in task_list:
        if multi_thread:
            thread = threading.Thread(target=task_thread, args=(task, parser, result))
            thread_list.append(thread)
        else:
            # sequentail operation
            task_thread(task, parser, result)
    if multi_thread:
        for thread in thread_list:
            thread.start()
        for thread in thread_list:
            thread.join()
    return result

def execute_task(https, authorization, payload, api_path):
    conn = http.client.HTTPSConnection(https)
    headers = authorization
    json_payload = json.dumps(payload)
    if len(payload) != 0:
        conn.request(api_path.split(" ")[0], api_path.split(" ")[1], json_payload, headers=headers)
    else:
        conn.request(api_path.split(" ")[0], api_path.split(" ")[1], headers=headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))
    return data.decode("utf-8")

def task_thread(task, parser, result):
    parts = task.split(' > ')
    if len(parts) > 1:
        # ETL operation contains multiple parts
        # use tmp to save the previous operation result
        tmp = None
        for part in parts:
            split_task = part.split(' ')
            job = split_task[0]
            if job.endswith('.py'):
                # transform.py
                try:
                    # use CoreEngine.transfrom.user_defined_function to transform
                    tmp = eval("CoreEngine.transform." + split_task[1])(tmp)
                    result.append("{\"status\": \"Data Transformation Completed!\"}")
                except:
                    result.append("{\"status\": \"Data Transformation failed!\"}")
            else:
                operation = split_task[0]
                if tmp is None:
                    # for the first operation, the tmp is None 
                    params = split_task[1:]
                else:
                    # for the remaining operation, use previous output as params
                    params = tmp
                api_path = parser.generate_path(operation, params)
                https = parser.get_https(operation)
                authentication = parser.get_authentication(operation)
                payload = parser.generate_payload(params)
                tmp = execute_task(https, authentication, payload, api_path)
                result.append(tmp)
    else:
        split_task = task.split(" ")
        operation = split_task[0]
        params = split_task[1:]
        api_path = parser.generate_path(operation, params)
        https = parser.get_https(operation)
        authentication = parser.get_authentication(operation)
        payload = parser.generate_payload(params)
        tmp = execute_task(https, authentication, payload, api_path)
        result.append(tmp)