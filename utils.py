from werkzeug.utils import secure_filename
from Output.output import output
from flask import Flask
from flask_cors import CORS
import re
import os
import zipfile
from pathlib import Path
import chardet  # 检测encoding，用于判断encoding异常情况

# 创建flask应用对象
app = Flask(__name__)
CORS(app, supports_credentials=True)  # 允许所有的跨域请求，并支持凭证


# 提取GPT返回评价中的分数并计算综合评分
def get_score_from_pingjia(pj_text):
    # 定义一个正则表达式，匹配文本中的“：x分”中的x
    # pattern = re.compile(r'：(\d+)分')  # (?:\**)(?:：|，|,)(?:\**)(\d+)分(?:\**)(?:：|，|,)或者(r'\**：|，|,\**(\d+)\**分：|，|,')
    pattern = re.compile(r'\**[：:，,]\**(\d+)\**分[：:，,。.]')
    # 使用findall方法，返回所有匹配的结果，结果是一个列表
    matches = pattern.findall(pj_text)
    # output(matches)
    # 如果匹配到了6个数字，就进行计算
    if len(matches) == 6:
        # 将列表中的字符串转换为整数
        scores = [int(x) for x in matches]
        # output(scores)
        # 计算平均分，乘以10，得到百分制的分数
        average = sum(scores) / len(scores) * 10
        average = round(average, 2)  # 这里使用round函数，保留两位小数
        # 返回百分制的分数
        print(average)
        return average
    else:
        # 如果匹配的结果不是6个数字，就返回None
        error = "分数计算错误"
        output('[Error]:%s' % error)
        return error


# 获取uploads目录,当前py文件与uploads文件夹需要在同一级目录下, todo 和app.config['UPLOAD_FOLDER'] = './uploads'功能重复
def get_uploads_dirname():
    try:
        # 获取当前脚本所在的目录，abspath(__file__)获取当前脚本的绝对路径,如 D:\Python\Scripts\test.py，dirname获取其目录路径，如D:\Python\Scripts
        # output('__file__：%s' % __file__) 获取当前脚本的绝对路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # 拼接出 uploads 目录的绝对路径
        uploads_dir = os.path.join(script_dir, 'uploads')
        # 如果 uploads 目录不存在，创建它
        if not os.path.exists(uploads_dir):
            output('[+]:上传目录不存在，正在创建中……')
            os.makedirs(uploads_dir)
            output('[+]:上传目录创建完成')
        return uploads_dir
    except Exception as e:
        output('[Error]:zip文件保存失败，错误信息为 %s' % e)
        raise


# 将接收到的zip文件保存到当前脚本同级目录uploads目录下，该函数和app.config['UPLOAD_FOLDER']部分功能不重复，该配置只记录upload路径而已
def save_zip_and_get_the_path(file):
    try:
        # 获取当前脚本同级目录uploads目录
        uploads_dir = get_uploads_dirname()
        # 拼接出文件的保存路径，secure_filename 获取文件的安全文件名
        file_path = os.path.join(uploads_dir, secure_filename(file.filename))
        # 保存文件到uploads/filename.zip
        file.save(file_path)
        output('[*]:zip文件保存成功，保存路径为 %s' % file_path)
        return file_path
    except Exception as e:
        output('[Error]:zip文件保存失败，错误信息为 %s' % e)
        raise  # 抛出异常


# 定义 unzip_file 函数，接受一个 zip 文件名作为参数
def unzip_file(saved_path):
    try:
        output('[*]:正在打开zip文件： %s' % saved_path)
        # 创建一个 ZipFile 对象，表示 zip 文件
        zip_file = zipfile.ZipFile(saved_path)
        # 获取 zip 文件的基本名，即去掉后缀的部分，saved_path= ./uploads\project.zip
        base_name = Path(saved_path).stem
        # base_name = os.path.splitext(saved_path)[0]
        output('[*]:获取zip不含后缀文件名为%s' % base_name)
        # 拼接目标解压路径，即当前脚本同级目录的 upload 目录下以 zip 文件名命名的文件夹
        unzipped_path = os.path.join('./uploads', base_name)
        output(unzipped_path)
        # 如果目标路径不存在，创建该文件夹
        if not os.path.exists(unzipped_path):
            os.makedirs(unzipped_path)
            output('[+]:已创建解压路径')
        # 遍历 zip 文件中的每个文件
        for file in zip_file.namelist():
            # 输出文件名和压缩后的大小
            output('[*]:开始解压文件 %s' % file)
            # 解压文件到目标路径
            zip_file.extract(file, unzipped_path)
        # 关闭并删除zip 文件
        zip_file.close()
        # os.remove(saved_path)
        output('[+]:解压完成，关闭并已删除该zip文件')
        return base_name, unzipped_path
    except Exception as e:
        output('[Error]:解压失败，错误信息为 %s' % e)
        raise


# 定义删除函数
def delete_non_coding_files(folder):
    # todo 添加剔除非自己开发的文件，包括大量的第三方库文件
    output('[+]:开始剔除%s中无效代码文件' % folder)
    # 遍历文件夹中的所有文件和子文件夹
    for root, dirs, files in os.walk(folder):
        # output('[+]:开始遍历代码文件')
        # 遍历所有文件
        for file in files:
            # 获取文件的绝对路径
            file_path = os.path.join(root, file)
            # 获取文件的大小
            file_size = os.path.getsize(file_path)
            # 如果文件大小为 0
            if file_size == 0:
                # 删除文件
                os.remove(file_path)
                # 打印提示信息
                output(f"[+]:Deleted {file_path} because it is 0kb.")
            # 如果文件大小超过 1MB，删除
            elif file_size > 1024 * 1024:
                # 删除文件
                os.remove(file_path)
                # 打印提示信息
                output(f"Deleted {file_path} because it is larger than 1MB.")
            # 否则
            else:
                # 尝试获取文件的编码格式
                try:
                    # 以二进制模式打开文件
                    with open(file_path, "rb") as f:
                        # 读取文件内容
                        data = f.read()
                        # 检测文件的编码格式
                        encoding = chardet.detect(data)["encoding"]
                        output('[*]:%s的编码格式为：%s' % (file_path, encoding))
                        # 如果文件的编码格式为 None
                        if encoding is None:
                            # 删除文件
                            os.remove(file_path)
                            # 打印提示信息
                            output(f"[+]:Deleted {file_path} because its encoding is None.")
                # 如果发生异常
                except Exception as e:
                    # 打印异常信息
                    output(f"[Error]:Failed to open {file_path} because of {e}.")
            # 获取文件的扩展名
            file_ext = os.path.splitext(file_path)[1]
            # 定义图片和视频文件的扩展名列表
            image_exts = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]
            video_exts = [".mp4", ".avi", ".mkv", ".mov", ".flv"]
            # 如果文件的扩展名在图片或视频文件的扩展名列表中
            if file_ext in image_exts or file_ext in video_exts:
                # 删除文件
                os.remove(file_path)
                # 打印提示信息
                output(f"[+]Deleted {file_path} because it is an image or video file.")

# 正则匹配测试用例
# if __name__ == '__main__':
#     texttest = ("### 代码质量打分如下：1. "
#             "**代码注释：**7分。代码的注释基本清晰，提供了足够的信息帮助理解代码的功能（如定义允许上传的文件扩展名、设置文件保存路径和最大大小等），但某些功能的实现细节（如`allowed_file"
#             "`函数的特殊逻辑、文件编码检测和处理异常的具体原因）缺乏详细说明，导致部分逻辑的理解需要结合代码本身推敲。 2. "
#             "**命名规范：**8分。大多数的函数和变量命名均遵循了清晰的命名规范，一般而言能够准确地反映其含义和作用。然而，在某些地方（如`pingjia`和`judger"
#             "`变量）命名较为通俗，可能不够正式，略微损失了一些专业性3. "
#             "**代码格式：**9分。代码的格式整体良好，使用了恰当的缩进、空格和换行，有利于提高代码的可读性。除了少数地方（如`ALLOWED_EXTENSIONS`集合的定义）略显紧凑，整体上很容易阅读和理解。4. "
#             "**代码冗余：**7分。代码在处理文件编码和读取内容时有些许冗余，如连续两次读取文件内容并进行`seek(0)`操作，这部分逻辑可以进行简化。同时，注释掉的代码（如`# import "
#             "openai`）若无实际用途应当移除。5. "
#             "**代码安全：**6分。代码对于上传文件的扩展名有一定检查，以及`.env"
#             "`文件的特殊处理显示出了安全意识。但是，直接使用用户上传的文件名和内容进行操作（如文件读取和编码检测）可能存在安全风险，如路径遍历攻击和编码探测导致的安全问题。同时，异常处理虽有尝试，但未看到具体的安全措施来防止潜在的安全威胁。6. **运行性能：**7分。文件的读取和处理过程考虑到了编码问题，尝试保证了文件内容的准确性和兼容性，但多次读取文件操作可能影响性能。同时，对于大文件的处理策略不够明确，可能对性能产生影响。")
#
#     get_score_from_pingjia(texttest)
