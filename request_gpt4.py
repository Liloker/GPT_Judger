import urllib3
import yaml
import os
import requests
from Output.output import output


class GptJudgeMain:
    def __init__(self):
        # 全局header头
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Upgrade-Insecure-Requests": "1",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "Connection": "close",  # 解决Max retries exceeded with url报错
        }
        # 忽略HTTPS告警
        urllib3.disable_warnings()
        # 获取当前文件路径
        current_path = os.path.dirname(__file__) # 返回当前文件所在的目录名称

        # 初始化读取配置文件
        config = yaml.safe_load(open(os.path.join(current_path, "Config", "config.yaml"), encoding='UTF-8'))
        # config = yaml.load(open(current_path + './Config/config.yaml', encoding='UTF-8'), yaml.Loader)
        # docker会路径错误，因为您在current_path后面加了一个点，表示当前目录，而不是当前文件所在的目录
        self.OpenAi_Initiating_System_Message = config['Prompts']['Initiating_System_Message']
        self.OpenAi_Initiating_User_Message = config['Prompts']['Initiating_User_Message']
        self.OpenAi_Key = config['Api_Config']['OpenAi_Key']

        # 设置初始上下文消息队列
        self.messages = [{"role": "system", "content": f"{self.OpenAi_Initiating_System_Message}"}]

    # AI对话接口
    def get_ai_judge(self, file, filename):
        judge_content = self.OpenAi_Initiating_User_Message.format(filename) + file  # 将文件名拼接到user message中
        output('[-]:正在调用AI接口进行代码分析... ...')
        output(judge_content)
        self.messages.append({"role": "user", "content": f'{judge_content}'})

        headers = {}
        body_data = {
            "api_key": self.OpenAi_Key,
            "model": "gpt-4-0125-preview",  # "gpt-4"
            "messages": self.messages
        }
        url = 'http://proxy-script-scr替换为你自己的代理app.run/chat'  # 'https://api.openai.com/v1/chat/completions'

        try:
            output("1")
            resp = requests.post(url=url, headers=headers, json=body_data, timeout=300)
            output(resp)
            output("2")
            json_data = resp.json()
            output(json_data)
            assistant_content = json_data['result']['choices'][0]['message']['content']
        except Exception as e:
            output(f'[ERROR]:AI对话接口出现错误，错误信息： {e}')
            # 出现 错误，错误信息：replace() argument 1 must be str, not None 提问：用python写一段post代码
            return '[ERROR] TimeOut!'
        self.messages.append({"role": "assistant", "content": f"{assistant_content}"})
        if len(self.messages) == 30:
            # 对话长度超过30就设置重开
            self.messages = self.messages[0]
        return assistant_content


