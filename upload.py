from utils import *
from flask import request, jsonify, url_for, send_from_directory
from request_gpt4 import *
import json
import chardet
import shutil  # python自带模块，用于文件高级操作，可与os互补

# 定义允许上传的文件扩展名,这里后期需要根据实际情况实时更新
ALLOWED_EXTENSIONS = {'zip', 'py', 'java', 'c', 'h', 'cpp', 'cc', 'cxx', 'C', 'c++', 'hpp', 'hh', 'hxx', 'cs', 'cpp',
                      'java', 'class', 'pyc', 'pyo', 'rb', 'pl', 'pm', 'kt', 'swift', 'go', 'js', 'ts', 'jsx', 'tsx',
                      'less', 'scss', 'sass', 'vue', 'spec.ts', 'module.ts', 'pipe.ts', 'service.ts', 'directive.ts',
                      'component.ts', 'php', 'html', 'css', 'dart', 'yaml', 'txt'}

# 设置上传文件的保存路径
app.config['UPLOAD_FOLDER'] = './uploads'

# 设置上传文件的最大大小为16MB todo 使用token计数器
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


# 定义一个检查文件扩展名的函数
def allowed_file(filename):
    # 如果文件名以 .env 开头，返回 True允许检测该文件
    if filename.startswith(".env"):
        return True
    # 获取文件的扩展名
    ext = filename.rsplit('.', 1)[-1]
    # 如果文件的扩展名是 zip，返回 zip
    if ext == 'zip':
        return 'zip'
    # 否则，按照原来的逻辑判断文件扩展名是否在允许的集合中
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# uploaded sussess, 返回评价结果
def send_response(pingjia):
    pingjia = str(pingjia)  # 转换评价为字符串格式
    output("[*]:评价完成\n" + pingjia)
    score = get_score_from_pingjia(pingjia)
    return jsonify({
        'code': 0,  # 状态码，0表示成功，其他表示失败
        'msg': '上传成功!',  # 提示信息
        'data': {
            'score': score,
            'text': json.dumps(pingjia)
            # 'text': pingjia
        }
    })


# uploaded failed
def upload_failed(e):
    return jsonify({
        'code': 1,
        'msg': '上传失败! ' + str(e),  # 提示信息，包含错误原因
        'data': None  # 数据内容，无
    })


# 定义一个处理文件上传请求的路由
@app.route('/upload', methods=['POST'])
def upload_file():
    # 从请求中获取上传的文件对象，request.files 对象，这个对象可以获取上传的文件对象，会把前端element-ui el-upload转为二进制的文件恢复为非二进制的文件对象
    file = request.files['file']
    output('[*]:收到文件')
    if file and allowed_file(file.filename):
        # 判断 file 是否 zip 后缀
        if allowed_file(file.filename) == 'zip':
            # 如果是 zip 后缀，调用 unzip_file 函数
            output('[+]:检测到zip文件')
            zipfile_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
            # 保存zip到同级目录uploads
            # zipfile_path = save_zip_and_get_the_path(file)
            # output(os.path.abspath(__file__))
            file.save(zipfile_path)
            # 解压zip到其相同名称下的目录中，获取解压文件夹名称和相对路径
            [unzipped_folder_name, unzipped_file_path] = unzip_file(zipfile_path)
            # todo 文件筛选，删除0kb，超过1MB，图片视频和encoding异常的文件
            delete_non_coding_files(os.path.join(app.config['UPLOAD_FOLDER'], unzipped_folder_name))
            # 初始化一个请求GPT的对象，调用get_multi_ai_judge对解压后的文件进行综合评估
            judger = GptJudgeMain()
            output('[unzipped_folder_name, unzipped_file_path]:%s,%s' % (unzipped_folder_name, unzipped_file_path))
            zonghe_pingjia = judger.get_multi_ai_judge(unzipped_folder_name, unzipped_file_path)
            # 清理解压后的临时文件夹
            output('[+]:清理解压后的临时文件夹......\n')
            # shutil.rmtree(unzipped_file_path)
            output('[*]:评估已完成，综合评价如下：\n')
            resp = send_response(zonghe_pingjia)
            return resp
        # 否则作为单文件进行分析
        else:
            try:
                encoding = chardet.detect(file.read())['encoding']
                output("[*]:文件编码格式为：" + encoding)
                file.seek(0)
                # 读取文件内容并转换为字符串
                file_content = file.read().decode(encoding, errors='ignore')
                # output("file_content" + file_content)
                file.seek(0)
                # 将文件指针移回文件开头，以便再次读取
                # print('文件内容为：', file_content)
                judger = GptJudgeMain()  # 初始化一个请求GPT的对象
                pingjia = judger.get_single_ai_judge(file_content, file.filename)
                # 调用judger对象中的get_ai_judge函数来实现请求
                return send_response(pingjia)
            except Exception as e:  # 如果发生任何异常，执行以下代码
                return upload_failed(e)
    else:
        # 返回一个JSON格式的数据，表示上传失败
        return jsonify({
            'code': 1,  # 状态码，1表示失败，其他表示成功
            'msg': '上传失败!暂不支持该文件格式，请联系系统管理员',  # 提示信息
            'data': None  # 数据内容，无
        })


# if __name__ == '__main__':
#     unziped_file_path = r'B:\VueProject\code_judger_sys\JudgerSys - flask\uploads\JudgerSys - flask'
#     judger = GptJudgeMain()  # 初始化一个请求GPT的对象
#     output('[+]:开始调用get_multi_ai_judge函数，unziped_file_path为%s' % unziped_file_path)
#     zonghe_pingjia = judger.get_multi_ai_judge(unziped_file_path)
#     output('[+]:输出综合评价')
#     resp = send_response(zonghe_pingjia)
