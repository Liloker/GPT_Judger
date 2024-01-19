from Output.output import output
from flask import Flask
from flask_cors import CORS
# 创建flask应用对象
app = Flask(__name__)
CORS(app, supports_credentials=True)  # 允许所有的跨域请求，并支持凭证

success_result = {
    "status": 200,
    "msg": "success",
    "data": {}
}

notfound_result = {
    "status": 404,
    "msg": "查找的实体不存在",
    "data": {}
}


