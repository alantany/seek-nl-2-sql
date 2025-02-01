import requests
import json
from openai import OpenAI
import pandas as pd
import time

class LLMClient:
    def __init__(self, base_url, model, openai_key=None, openai_base_url=None, openai_model=None):
        self.base_url = base_url
        self.model = model
        # 保存OpenAI配置但不创建客户端
        self.openai_key = openai_key
        self.openai_base_url = openai_base_url
        self.openai_model = openai_model
    
    def generate_sql(self, prompt, db=None):
        """调用LLM生成SQL查询"""
        system_prompt = """你是一个SQLite数据库专家，请将用户的自然语言转换为SQLite SQL查询语句。
        
        注意事项：
        1. 使用SQLite支持的语法
        2. 不要使用其他数据库特有的函数
        3. 日期函数使用SQLite的date/datetime函数
        4. 字符串连接使用 || 而不是 CONCAT
        5. 使用标准的SQL聚合函数(COUNT, SUM, AVG, MAX, MIN)
        6. 请按照以下格式编写SQL:
           - SELECT/INSERT/UPDATE/DELETE 单独一行
           - FROM 子句单独一行
           - WHERE/GROUP BY/HAVING/ORDER BY 各自单独一行
           - JOIN 子句每个单独一行
           - 使用适当的缩进
           - 子查询使用合适的换行和缩进
        
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
        
        results = {}
        
        # 先执行ChatGPT
        try:
            start_time = time.time()
            chatgpt_response = self._generate_sql_chatgpt(system_prompt, prompt)
            chatgpt_time = time.time() - start_time
            results['chatgpt'] = {
                'sql': chatgpt_response,
                'time': chatgpt_time
            }
        except Exception as e:
            results['chatgpt'] = {
                'sql': f"Error: {str(e)}",
                'time': 0
            }
        
        # 不再重复执行DeepSeek
        results['deepseek'] = None
        
        return results
    
    def _generate_sql_deepseek(self, system_prompt, prompt, db, log_callback=None):
        """使用DeepSeek模型生成SQL，并自动修正错误"""
        def log(message):
            if log_callback:
                log_callback(message)
            print(message)
        
        max_attempts = 3
        attempt = 1
        attempt_history = []
        start_time = time.time()
        
        while attempt <= max_attempts:
            if attempt > 1:
                log(f"\n=== 第{attempt}次尝试生成SQL ===")
            else:
                log("\n=== 开始生成SQL ===")
            
            log(f"[{time.strftime('%H:%M:%S')}] 正在从DeepSeek获取响应...")
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"{system_prompt}\n\n用户查询：{prompt}\n\n" + 
                             (f"前一次生成的SQL有错误，请修正：{error_msg}\n\n" if 'error_msg' in locals() else "") +
                             "SQLite SQL语句：\n",
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
                
                # 在返回之前格式化SQL
                def format_sql(sql):
                    # 移除多余的空格和换行
                    sql = ' '.join(sql.split())
                    
                    # 添加适当的换行和缩进
                    keywords = ['SELECT', 'FROM', 'WHERE', 'GROUP BY', 'HAVING', 'ORDER BY', 'JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'INNER JOIN']
                    formatted = []
                    lines = sql.split(';')[0].strip().split(' ')
                    current_line = []
                    
                    for word in lines:
                        if word.upper() in keywords:
                            if current_line:
                                formatted.append(' '.join(current_line))
                                current_line = []
                            if word.upper().endswith('JOIN'):
                                formatted.append('    ' + word)  # 添加缩进
                            else:
                                formatted.append(word)
                        else:
                            current_line.append(word)
                    
                    if current_line:
                        if formatted and formatted[-1] in keywords:
                            formatted.append('    ' + ' '.join(current_line))  # 添加缩进
                        else:
                            formatted.append(' '.join(current_line))
                    
                    return '\n'.join(formatted) + ';'
                
                # 格式化SQL并返回
                cleaned_response = format_sql(cleaned_response)
                log(f"[{time.strftime('%H:%M:%S')}] 生成的SQL:\n{cleaned_response}\n")
                
                # 尝试执行SQL
                try:
                    log(f"[{time.strftime('%H:%M:%S')}] 正在验证SQL...")
                    result = db.execute_query(cleaned_response)
                    if isinstance(result, pd.DataFrame):
                        log(f"[{time.strftime('%H:%M:%S')}] SQL验证成功！")
                        execution_time = time.time() - start_time
                        return {
                            'sql': cleaned_response,
                            'attempts': attempt,
                            'success': True,
                            'history': attempt_history,
                            'time': execution_time
                        }
                    else:
                        # 直接使用数据库返回的错误信息
                        raise Exception(str(result))
                except Exception as e:
                    error_msg = str(e)
                    log(f"[{time.strftime('%H:%M:%S')}] SQL执行失败: {error_msg}")
                    
                    attempt_history.append({
                        'attempt': attempt,
                        'sql': cleaned_response,
                        'error': error_msg,
                        'timestamp': time.strftime('%H:%M:%S')
                    })
                    
                    if attempt == max_attempts:
                        log(f"[{time.strftime('%H:%M:%S')}] 达到最大重试次数({max_attempts})，停止尝试")
                        execution_time = time.time() - start_time
                        return {
                            'sql': cleaned_response,
                            'attempts': attempt,
                            'success': False,
                            'error': error_msg,
                            'history': attempt_history,
                            'time': execution_time
                        }
                    
                    log(f"[{time.strftime('%H:%M:%S')}] 准备进行第{attempt + 1}次尝试...")
                    attempt += 1
                    continue
            else:
                execution_time = time.time() - start_time
                return {
                    'sql': f"Error: {response.status_code}",
                    'attempts': attempt,
                    'success': False,
                    'error': f"API错误: {response.status_code}",
                    'history': [],
                    'time': execution_time
                }
        
        execution_time = time.time() - start_time
        return {
            'sql': "达到最大重试次数",
            'attempts': max_attempts,
            'success': False,
            'error': "无法生成有效SQL",
            'history': attempt_history,
            'time': execution_time
        }
    
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
            # 移除开头的```sql和结尾的```
            sql = sql.strip('`').strip()
            if sql.lower().startswith('sql'):
                sql = sql[3:].strip()
            
            # 提取SQL语句
            if 'SELECT' in sql.upper():
                sql = sql[sql.upper().find('SELECT'):]
            elif 'INSERT' in sql.upper():
                sql = sql[sql.upper().find('INSERT'):]
            elif 'UPDATE' in sql.upper():
                sql = sql[sql.upper().find('UPDATE'):]
            elif 'DELETE' in sql.upper():
                sql = sql[sql.upper().find('DELETE'):]
            
            # 清理引号和分号
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