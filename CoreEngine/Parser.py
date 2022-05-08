import json
import os

from flask import jsonify

class Parser:
    def __init__(self, user_id):
        mpath = os.path.abspath(os.path.dirname(__file__))
        cfg = os.path.join(mpath, "../configuration.json")
        self.user_id = user_id
        with open(cfg) as f:
            self.configuration = json.load(f)

    @staticmethod
    def build_params_dict(params):
        params_dict = {} 
        for p in params:
            print("current p is ", p) 
            if "resource" in p: 
                pair0 = p.split(":")[0]
                pair1 = p[p.index(":")+1:] 
                temp_dict = {}
                pair1_list = []
                while '{' in pair1:
                    name_value = pair1[pair1.index('{')+6 : pair1.index('}')]
                    pair1 = pair1[pair1.index('}')+1:]
                    temp_dict["name"] = name_value
                    pair1_list.append(temp_dict) 
                params_dict[pair0] = pair1_list
            else:
                pair = p.split(":")
                print("pair is ", pair)
                params_dict[pair[0]] = pair[1] 
        return params_dict

    def find_user(self):
        user_list = self.configuration["User"]
        for u in user_list:
            if self.user_id == u["id"]:
                return True
        return False

    def find_and_get_user(self):
        user_list = self.configuration["User"]
        for u in user_list:
            if self.user_id == u["id"]:
                return u
        return None

    def check_permission(self, task, params):
        """
         Check whether the given user has permission to perform a task

        :param task: a string of task in a format of Product:<Product>:<level1>:<level2>:...:Operations:<operation>.
                    For example, Product:kafka:topic:Operations:read.
        :param params: a list of parameters for this task, for example, ["topic_name:t1", "k2:v2"]
        :return: True if this user has permission to perform such task, otherwise False
        """
        cur_user = self.find_and_get_user()
        if cur_user is None:
            # Given user doesn't exist
            print("User doesn't exist.")
            return False

        # Check product permissions
        tlist = task.split(":")
        for i in range(len(tlist)):
            cur_user = cur_user.get(tlist[i])
            if cur_user is None:
                return False

        # Check parameters validity. There are two types of params, one is path params, another one is body params.
        operation = cur_user
        given_params = Parser.build_params_dict(params)
        if operation["Request"].get("Path_Param"):
            required_path_params = operation["Request"]["Path_Param"]
            if required_path_params is not None:
                for path_param in required_path_params:
                    if given_params.get(path_param) is None:
                        print("Need valid path parameters")
                        return False
        if operation["Request"].get("Body"):
            required_body_params = operation["Request"]["Body"]["Required"]
            if required_body_params is not None:
                for body_param in required_body_params:
                    if given_params.get(body_param) is None:
                        print("Need valid body parameters")
                        return False
        return True

    def generate_path(self, task, params):
        t_list = task.split(":")
        cur = self.find_and_get_user()
        for i in range(len(t_list)):
            cur = cur.get(t_list[i])

        # Replace the variable in API_Path with given params
        api_path = cur["API_Path"]
        if cur["Request"].get("Path_Param") is not None:
            params_dict = Parser.build_params_dict(params)
            for path_param in cur["Request"]["Path_Param"]:
                api_path = api_path.replace("{" + path_param + "}", params_dict.get(path_param))
        return api_path

    def generate_payload(self, params):
        # Replace the variable in Body_Param with given params
        params_dict = Parser.build_params_dict(params)
        return params_dict

    def get_https(self, task):
        t_list = task.split(":")
        cur = self.find_and_get_user()
        for i in range(len(t_list)):
            if t_list[i] == "Operations":
                break
            cur = cur.get(t_list[i])
        return cur["Https"]

    def get_authentication(self, task):
        t_list = task.split(":")
        cur = self.find_and_get_user()
        for i in range(len(t_list)):
            if t_list[i] == "Operations":
                break
            cur = cur.get(t_list[i])
        return cur["Authentication"]

# x = Parser(1)
# print(x.check_permission("Product:kafka:topic:Operations:DELETE", ["topic_name:t1"]))
# print(x.check_permission("Product:kafka:topic:Operations:POST", ["topic_name:t1"]))
# print(x.check_permission("Product:kafka:topic:Operations:POST", []))
# print(x.check_permission("Product:kafka:topic:Operations:DELETE", []))

# print(x.generate_path("Product:kafka:topic:Operations:DELETE", ["topic_name:t1"]))
# print(x.generate_payload(["topic_name:t1"]))
# print(x.get_https("Product:kafka:topic:Operations:DELETE"))
# print(x.get_authentication("Product:kafka:topic:Operations:DELETE"))
p = Parser
p.build_params_dict(['resource:[{name:jiarui2},{name:junyu2}]'])