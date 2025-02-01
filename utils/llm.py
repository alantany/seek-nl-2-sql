import requests
import json
from openai import OpenAI

class LLMClient:
    def __init__(self, base_url, model, openai_key=None, openai_base_url=None, openai_model=None):
        self.base_url = base_url
        self.model = model
        # 保存OpenAI配置但不创建客户端
        self.openai_key = openai_key
        self.openai_base_url = openai_base_url
        self.openai_model = openai_model
    
    def generate_sql(self, prompt):
        """调用LLM生成SQL查询"""
        system_prompt = """你是一个SQLite数据库专家，请将用户的自然语言转换为SQLite SQL查询语句。
        
        注意事项：
        1. 使用SQLite支持的语法
        2. 不要使用其他数据库特有的函数
        3. 日期函数使用SQLite的date/datetime函数
        4. 字符串连接使用 || 而不是 CONCAT
        5. 使用标准的SQL聚合函数(COUNT, SUM, AVG, MAX, MIN)
        
        目前的数据库表结构如下：
        
        DEPT (部门表):
        - DEPTNO: INTEGER PRIMARY KEY (部门编号)
        - DNAME: TEXT (部门名称)
        - LOC: TEXT (位置)
        
        EMP (员工表):
        - EMPNO: INTEGER PRIMARY KEY (员工编号)
        - ENAME: TEXT (员工姓名)
        - JOB: TEXT (职位)
        - MGR: INTEGER (上级编号)
        - HIREDATE: DATE (入职日期)
        - SAL: DECIMAL (薪资)
        - COMM: DECIMAL (提成)
        - DEPTNO: INTEGER (部门编号)
        
        SALGRADE (薪资等级表):
        - GRADE: INTEGER PRIMARY KEY (等级)
        - LOSAL: DECIMAL (最低工资)
        - HISAL: DECIMAL (最高工资)
        
        BONUS (奖金表):
        - ENAME: TEXT (员工姓名)
        - JOB: TEXT (职位)
        - SAL: DECIMAL (薪资)
        - COMM: DECIMAL (奖金)
        
        请只返回SQL语句，不需要其他解释。确保SQL语句符合SQLite语法规范。"""
        
        # 获取两个模型的结果
        results = {}
        
        # DeepSeek模型
        try:
            deepseek_response = self._generate_sql_deepseek(system_prompt, prompt)
            results['deepseek'] = deepseek_response
        except Exception as e:
            results['deepseek'] = f"Error: {str(e)}"
        
        # ChatGPT模型
        chatgpt_response = self._generate_sql_chatgpt(system_prompt, prompt)
        results['chatgpt'] = chatgpt_response
        
        return results
    
    def _generate_sql_deepseek(self, system_prompt, prompt):
        """使用DeepSeek模型生成SQL"""
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": f"{system_prompt}\n\n用户查询：{prompt}\n\nSQLite SQL语句：",
                "stream": True
            },
            stream=True
        )
        
        if response.status_code == 200:
            full_response = ""
            thinking_mode = False
            
            for line in response.iter_lines():
                if line:
                    try:
                        json_response = json.loads(line)
                        if 'response' in json_response:
                            content = json_response['response']
                            
                            # 处理特殊标记
                            if content == '<think>':
                                thinking_mode = True
                                continue
                            elif content == '</think>':
                                thinking_mode = False
                                continue
                            elif content == '\n\n':
                                continue
                            
                            # 如果不在思考模式，添加内容
                            if not thinking_mode:
                                full_response += content
                                
                    except json.JSONDecodeError:
                        continue
            
            # 清理响应文本
            cleaned_response = full_response.strip()
            # 移除解释性文本，只保留SQL语句
            if 'SELECT' in cleaned_response.upper():
                cleaned_response = cleaned_response[cleaned_response.upper().find('SELECT'):]
            elif 'INSERT' in cleaned_response.upper():
                cleaned_response = cleaned_response[cleaned_response.upper().find('INSERT'):]
            elif 'UPDATE' in cleaned_response.upper():
                cleaned_response = cleaned_response[cleaned_response.upper().find('UPDATE'):]
            elif 'DELETE' in cleaned_response.upper():
                cleaned_response = cleaned_response[cleaned_response.upper().find('DELETE'):]
                
            # 清理SQL语句
            cleaned_response = cleaned_response.strip()
            # 去掉末尾的引号
            cleaned_response = cleaned_response.rstrip('"').rstrip("'")
            # 确保以分号结尾，并去掉分号后的内容
            if ';' in cleaned_response:
                cleaned_response = cleaned_response.split(';')[0] + ';'
            elif not cleaned_response.endswith(';'):
                cleaned_response += ';'
            
            return cleaned_response
        else:
            return f"Error: {response.status_code}"
    
    def _generate_sql_chatgpt(self, system_prompt, prompt):
        """使用ChatGPT模型生成SQL"""
        try:
            # 直接使用硬编码的API密钥（临时测试）
            client = OpenAI(
                api_key="sk-1pUmQlsIkgla3CuvKTgCrzDZ3r0pBxO608YJvIHCN18lvOrn",
                base_url="https://api.chatanywhere.tech/v1"
            )
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # 直接使用模型名称
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=100
            )
            
            sql = response.choices[0].message.content.strip()
            
            # 清理SQL语句
            if 'SELECT' in sql.upper():
                sql = sql[sql.upper().find('SELECT'):]
            elif 'INSERT' in sql.upper():
                sql = sql[sql.upper().find('INSERT'):]
            elif 'UPDATE' in sql.upper():
                sql = sql[sql.upper().find('UPDATE'):]
            elif 'DELETE' in sql.upper():
                sql = sql[sql.upper().find('DELETE'):]
            
            sql = sql.strip().rstrip('"').rstrip("'")
            if ';' in sql:
                sql = sql.split(';')[0] + ';'
            elif not sql.endswith(';'):
                sql += ';'
            
            return sql
        except Exception as e:
            print(f"ChatGPT error: {str(e)}")
            return f"Error: {str(e)}"

    def check_health(self):
        """检查模型服务是否正常"""
        try:
            # 使用chat接口发送测试消息
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "user", "content": "test"}
                    ]
                }
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Health check error: {str(e)}")  # 添加错误日志
            return False

    def get_model_info(self):
        """获取当前模型信息"""
        return {
            "name": self.model,
            "endpoint": self.base_url
        }

    def chat(self, message):
        """与模型对话"""
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "user", "content": message}
                    ],
                    "stream": True
                },
                stream=True
            )
            
            if response.status_code == 200:
                full_response = ""
                thinking_mode = False
                
                for line in response.iter_lines():
                    if line:
                        try:
                            json_response = json.loads(line)
                            if 'message' in json_response and 'content' in json_response['message']:
                                content = json_response['message']['content']
                                
                                # 处理特殊标记
                                if content == '<think>':
                                    thinking_mode = True
                                    continue
                                elif content == '</think>':
                                    thinking_mode = False
                                    continue
                                elif content == '\n\n':
                                    continue
                                
                                # 如果不在思考模式，添加内容
                                if not thinking_mode:
                                    full_response += content
                                    
                        except json.JSONDecodeError:
                            continue
                
                # 清理响应文本
                cleaned_response = full_response.strip()
                # 移除以"好，"或"好。"开头的思考语句
                if cleaned_response.startswith('好，') or cleaned_response.startswith('好。'):
                    cleaned_response = cleaned_response.split('\n', 1)[-1].strip()
                # 移除"首先，"开头的规划语句
                if cleaned_response.startswith('首先，'):
                    cleaned_response = cleaned_response.split('首先，', 1)[-1].strip()
                # 移除"接下来，"开头的过程语句
                if cleaned_response.startswith('接下来，'):
                    cleaned_response = cleaned_response.split('接下来，', 1)[-1].strip()
                    
                return cleaned_response
            else:
                return f"Error: {response.status_code}"
        except Exception as e:
            print(f"Chat error: {str(e)}")
            return f"Error: {str(e)}"

    def explain_sql_result(self, sql, df):
        """解释SQL查询结果"""
        try:
            # 将DataFrame转换为易读的文本
            result_text = df.to_string() if not df.empty else "空结果"
            
            prompt = f"""请用简洁的语言解释以下SQL查询的结果：

SQL查询：
{sql}

查询结果：
{result_text}

请用通俗易懂的语言解释这个结果的含义，不需要解释SQL语句本身。"""

            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "stream": True
                },
                stream=True
            )
            
            if response.status_code == 200:
                full_response = ""
                thinking_mode = False
                
                for line in response.iter_lines():
                    if line:
                        try:
                            json_response = json.loads(line)
                            if 'message' in json_response and 'content' in json_response['message']:
                                content = json_response['message']['content']
                                
                                # 处理特殊标记
                                if content == '<think>':
                                    thinking_mode = True
                                    continue
                                elif content == '</think>':
                                    thinking_mode = False
                                    continue
                                elif content == '\n\n':
                                    continue
                                
                                # 如果不在思考模式，添加内容
                                if not thinking_mode:
                                    full_response += content
                    
                        except json.JSONDecodeError:
                            continue
                
                # 清理响应文本
                cleaned_response = full_response.strip()
                # 移除常见的思考开头语句
                if cleaned_response.startswith('好，') or cleaned_response.startswith('好。'):
                    cleaned_response = cleaned_response.split('\n', 1)[-1].strip()
                
                return cleaned_response
            else:
                return "无法生成解释"
        except Exception as e:
            print(f"Explain result error: {str(e)}")
            return "解释结果时发生错误" 