# import urllib3
import yaml
import os
import requests
from Output.output import output
import chardet

class GptJudgeMain:
    def __init__(self):
        # 初始化读取配置文件
        config = yaml.safe_load(open(os.path.join(os.path.dirname(__file__), "Config", "config.yaml"), encoding='UTF-8'))
        # config = yaml.load(open(current_path + './Config/config.yaml', encoding='UTF-8'), yaml.Loader)
        # docker会路径错误，因为在current_path后面加了一个点，表示当前目录，而不是当前文件所在的目录
        self.OpenAi_Key = config['Api_Config']['OpenAi_Key']
        # 配置单个代码文件评价
        self.OpenAi_Initiating_System_Message_Single = config['Prompts']['Initiating_System_Message_Single']
        self.OpenAi_Initiating_User_Message_Single = config['Prompts']['Initiating_User_Message_Single']
        # 配置基于解压包对多个代码文件综合评价
        self.OpenAi_Initiating_System_Message_Multi = config['Prompts']['Initiating_System_Message_Multi']
        self.OpenAi_Initiating_User_Message_Multi = config['Prompts']['Initiating_User_Message_Multi']
        self.OpenAi_Chatting_User_Message_In = config['Prompts']['Chatting_User_Message_In']
        self.OpenAi_Chatting_User_Message_End = config['Prompts']['Chatting_User_Message_End']
        # 设置初始上下文消息队列
        self.messages_single = [{"role": "system", "content": f"{self.OpenAi_Initiating_System_Message_Single}"}]
        self.messages_multi = [{"role": "system", "content": f"{self.OpenAi_Initiating_System_Message_Multi}"}]
        # 配置post信息
        # urllib3.disable_warnings()  # 忽略HTTPS告警
        self.headers = {}
        self.url = 'http://pr-替换为你自己的gpt代理-capp.run/chat'  # 'https://api.openai.com/v1/chat/completions'

    # AI对话接口,单文件评价
    def get_single_ai_judge(self, file, filename):
        judge_content = self.OpenAi_Initiating_User_Message_Single.format(filename) + file  # 将文件名拼接到user message中
        output('[-]:正在调用AI接口进行代码分析... ...')
        # output(judge_content)
        self.messages_single.append({"role": "user", "content": f'{judge_content}'})
        body_data = {
            "api_key": self.OpenAi_Key,
            "model": "gpt-4-0125-preview",  # "gpt-4"
            "messages": self.messages_single,
            "temperature": 0.5  # 设置温度为 0.8,温度越高,输出的随机性越大，范围0-2
        }
        try:
            # output("1")
            resp = requests.post(url=self.url, headers=self.headers, json=body_data, timeout=300)
            output(resp)
            # output("2")
            json_data = resp.json()
            output(json_data)
            assistant_content = json_data['result']['choices'][0]['message']['content']
        except Exception as e:
            output(f'[ERROR]:AI对话接口出现错误，错误信息： {e}')
            # 出现 错误，错误信息：replace() argument 1 must be str, not None 提问：用python写一段post代码
            return '[ERROR] TimeOut!'
        self.messages_single.append({"role": "assistant", "content": f"{assistant_content}"})
        if len(self.messages_single) == 30:
            # 对话长度超过30就设置重开
            self.messages_single = self.messages_single[0]
        return assistant_content

    # AI对话接口,多文件评价。连续多轮对话，基于GPT上下文记忆功能实现的连续多轮评价，用于解压项目zip之后对相应文件夹路径下多个代码文件的智能评价
    def get_multi_ai_judge(self, unzipped_folder_name, unzipped_file_path):
        # todo 添加日志功能
        output('[+]:开始调用get_multi_ai_judje函数')
        # 获取解压文件夹目录的绝对路径，unzipped_file_path为相对路径./uploads/unzipped_dir
        # abs_path = os.path.abspath(unzipped_file_path)
        # output('[*]:abs_path= %s' % abs_path)
        # 获取解压文件夹名称
        # folder_name = os.path.basename(abs_path)
        output('[*]:folder_name = %s' % unzipped_folder_name)
        # 遍历unziped_file_path这个解压缩之后文件夹中的文件，这里的unziped_file_path就是项目解压后的文件夹路径，在当前py文件的同级目录uploads下的test_project文件夹下，test_project就是项目文件夹，由test_project.zip解压而来
        # 获取项目名称
        Project_Name = unzipped_folder_name
        # Project_Folder = unzipped_file_path  # todo 替换后面的abs_path
        # 遍历项目文件夹下的文件，每读取一个文件，就把该文件拼接到judge_content中，提交一次到gpt接口，进行一次循环，索引是Index_of_file，文件名保存在Filename变量中

        # 初始化一个计数器，用于记录文件的序号
        count = count_files = 0
        # 获取项目中代码文件数量
        for item in os.listdir(unzipped_file_path):
            # 拼接文件或子目录的绝对路径
            item_path = os.path.join(unzipped_file_path, item)
            output('[*]:item_path' + item_path)
            # 判断是否是文件
            if os.path.isfile(item_path):
                # 如果是文件，增加计数器
                count_files += 1
            else:
                continue
        lastone = count_files

        # 使用 for 循环遍历目录下的所有文件和子目录
        for item in os.listdir(unzipped_file_path):
            # 拼接文件或子目录的绝对路径
            item_path = os.path.join(unzipped_file_path, item)
            output('[*]:item_path' + item_path)
            # 判断是否是文件
            if os.path.isfile(item_path):
                # 如果是文件，增加计数器
                count += 1
                # 获取文件的文件名
                file_name = os.path.basename(item_path)
                # 打印文件的序号和文件名
                output('[+]第%d个文件：%s' % (count, file_name))
                # 打开文件，并用二进制模式读取
                with open(item_path, 'rb') as f:
                    data = f.read()
                    encoding = chardet.detect(data)['encoding']
                    output('[*]文件编码格式为：%s' % encoding)
                    file_content = data.decode(encoding, errors='ignore')  # with语法糖不影响file_content作用域

                # 模式一：所有count，即所有解压缩的文件对话都共用message_multi,注意token128k上限，所有文件加起来不能超过128k的token，好处是不依赖上下文记忆
                if count == 1:  # 项目中第1个代码文件
                    # 将文件名拼接到user message中,format匹配到3个占位符{}
                    judge_content = "{}{}{}".format(self.OpenAi_Initiating_User_Message_Multi.format(Project_Name, count, file_name), "\n", file_content)
                    output('[+]:正在调用AI接口进行代码分析... ...这是第%d 个' % count)
                    try:
                        assistant_content = self.get_response_from_gpt(count, judge_content)
                        output('[-]:第%d个文件评价结果为%s' % (count, assistant_content))
                    except Exception as e:
                        output(f'[ERROR]:AI对话接口出现错误，错误信息： {e}')
                        return '[ERROR] TimeOut!'
                    self.messages_multi.append({"role": "assistant", "content": f"{assistant_content}"})

                elif count == lastone:  # 项目最后一个代码文件
                    judge_content = "{}{}{}".format(
                        self.OpenAi_Chatting_User_Message_End.format(file_name, count), "\n", file_content)
                    output('[-]:正在调用AI接口进行代码分析... ...这是第%d 个,也是最后一个：%s' % (count, file_name))
                    try:
                        assistant_comprehensive_content = self.get_response_from_gpt(count, judge_content)
                        output('[-]:最后一个文件，即第%d个文件评价结果为：\n%s' % (count, assistant_comprehensive_content))
                        # todo 关闭所有已打开的文件
                        return assistant_comprehensive_content
                    except Exception as e:
                        output(f'[ERROR]:AI对话接口出现错误，错误信息： {e}')
                        return '[ERROR] TimeOut!'
                else:  # 项目第2到倒数第2个
                    judge_content = "{}{}{}".format(
                        self.OpenAi_Chatting_User_Message_In.format(count, file_name), "\n", file_content)
                    output('[+]:正在调用AI接口进行代码分析... ...这是第%d 个，：%s ' % (count, file_name))
                    try:
                        assistant_content = self.get_response_from_gpt(count, judge_content)
                        output('[-]:第%d个文件评价结果为%s' % (count, assistant_content))
                    except Exception as e:
                        output(f'[ERROR]:AI对话接口出现错误，错误信息： {e}')
                        return '[ERROR] TimeOut!'
                    self.messages_multi.append({"role": "assistant", "content": f"{assistant_content}"})
                    if len(self.messages_multi) == 100:
                        # todo 观察如果对话长度过长会怎样？是否需要设置超过30就设置重开
                        output(f'[ERROR]:AI对话轮数超过30，检查是否需要提高轮数参数')
                        # self.messages_multi = self.messages_multi[0]

                # todo 模式二：所有count，即所有解压缩的文件对话都不共用message_multi,不需要太注意token128k上限，尝试依赖上下文记忆，效果取决于gpt内部记忆窗口

            else:
                output('[+]已掠过一个非文件对象')
                continue

    # 供get_multi_ai_judge调用
    def get_response_from_gpt(self, count, judge_content):
        output('[-]发送内容judge_content为:\n' + judge_content)
        self.messages_multi.append({"role": "user", "content": f'{judge_content}'})
        body_data = {
            "api_key": self.OpenAi_Key,
            "model": "gpt-4-0125-preview",  # "gpt-4"
            "messages": self.messages_multi,
            "temperature": 0.5  # 设置温度为 0.8,温度越高,输出的随机性越大，范围0-2
        }
        resp = requests.post(url=self.url, headers=self.headers, json=body_data, timeout=300)
        output('[*]:成功获取到response')
        json_data = resp.json()
        # output('[*]json_data内容为%s' % json_data)
        assistant_content = json_data['result']['choices'][0]['message']['content']
        return assistant_content
