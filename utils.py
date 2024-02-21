from Output.output import output
from flask import Flask
from flask_cors import CORS
import re
# 创建flask应用对象
app = Flask(__name__)
CORS(app, supports_credentials=True)  # 允许所有的跨域请求，并支持凭证


def get_score_from_pingjia(pj_text):
    # 定义一个正则表达式，匹配文本中的“：x分”中的x
    # pattern = re.compile(r'：(\d+)分')  # (?:\**)(?:：|，|,)(?:\**)(\d+)分(?:\**)(?:：|，|,)
    # pattern = re.compile(r'\**：|，|,\**(\d+)\**分：|，|,')
    pattern = re.compile(r'\**[：:，,]\**(\d+)\**分[：:，,]')
    # output(pattern)
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
        return average
    else:
        # 如果匹配的结果不是6个数字，就返回None
        error = "数字匹配异常"
        return error


