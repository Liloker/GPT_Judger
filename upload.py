from utils import *
from flask import request, jsonify, url_for, send_from_directory
# from werkzeug.utils import secure_filename
import os
from request_gpt4 import *
import json
import openai


# 定义允许上传的文件扩展名,这里后期需要根据实际情况实时更新
ALLOWED_EXTENSIONS = {'py', 'java', 'c', 'cpp', 'js', 'html', 'css'}

# 设置上传文件的保存路径
app.config['UPLOAD_FOLDER'] = './uploads'

# 设置上传文件的最大大小为16MB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


# 定义一个检查文件扩展名的函数
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# 定义一个处理文件上传请求的路由
@app.route('/upload', methods=['POST'])
def upload_file():
    # 从请求中获取上传的文件对象，request.files 对象，这个对象可以获取上传的文件对象，会把前端element-ui el-upload转为二进制的文件恢复为非二进制的文件对象
    file = request.files['file']
    output('[+]:收到文件')

    if file and allowed_file(file.filename):

        file_content = file.read().decode("utf-8")  # 读取文件内容并转换为字符串
        file.seek(0)  # 将文件指针移回文件开头，以便再次读取
        # print('文件内容为：', file_content)
        judger = GptJudgeMain()
        pingjia = judger.get_ai_judge(file_content)
        pingjia = str(pingjia)  # 转换评价为字符串格式
        output("[*]:评价完成\n" + pingjia)
        return jsonify({
            'code': 0,  # 状态码，0表示成功，其他表示失败
            'msg': '上传成功!',  # 提示信息
            'data': {
                'text': json.dumps(pingjia)
                # 'text': pingjia
            }
        })
    else:
        # 返回一个JSON格式的数据，表示上传失败
        return jsonify({
            'code': 1,  # 状态码，1表示失败，其他表示成功
            'msg': '上传失败! Invalid file',  # 提示信息
            'data': None  # 数据内容，无
        })



