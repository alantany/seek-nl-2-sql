import sqlite3

class HistoryDB:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """初始化历史问题数据库"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 创建历史问题表
        c.execute('''
        CREATE TABLE IF NOT EXISTS question_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_question(self, question):
        """保存问题"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('INSERT INTO question_history (question) VALUES (?)', (question,))
        
        conn.commit()
        conn.close()
    
    def get_questions(self, limit=50):
        """获取历史问题"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('SELECT id, question FROM question_history ORDER BY id DESC LIMIT ?', (limit,))
        questions = c.fetchall()
        
        conn.close()
        return questions 