import sqlite3
import pandas as pd
from datetime import datetime

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """初始化数据库，创建Scott Schema的表结构"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 创建部门表(DEPT)
        c.execute('''
        CREATE TABLE IF NOT EXISTS DEPT (
            DEPTNO INTEGER PRIMARY KEY,
            DNAME TEXT NOT NULL,
            LOC TEXT
        )
        ''')
        
        # 创建员工表(EMP)
        c.execute('''
        CREATE TABLE IF NOT EXISTS EMP (
            EMPNO INTEGER PRIMARY KEY,
            ENAME TEXT NOT NULL,
            JOB TEXT,
            MGR INTEGER,
            HIREDATE DATE,
            SAL DECIMAL(7,2),
            COMM DECIMAL(7,2),
            DEPTNO INTEGER,
            FOREIGN KEY (DEPTNO) REFERENCES DEPT(DEPTNO),
            FOREIGN KEY (MGR) REFERENCES EMP(EMPNO)
        )
        ''')
        
        # 创建薪资等级表(SALGRADE)
        c.execute('''
        CREATE TABLE IF NOT EXISTS SALGRADE (
            GRADE INTEGER PRIMARY KEY,
            LOSAL DECIMAL(7,2),
            HISAL DECIMAL(7,2)
        )
        ''')
        
        # 创建奖金表(BONUS)
        c.execute('''
        CREATE TABLE IF NOT EXISTS BONUS (
            ENAME TEXT,
            JOB TEXT,
            SAL DECIMAL(7,2),
            COMM DECIMAL(7,2)
        )
        ''')
        
        # 插入部门数据
        c.execute('SELECT count(*) FROM DEPT')
        if c.fetchone()[0] == 0:
            c.executemany('INSERT INTO DEPT (DEPTNO, DNAME, LOC) VALUES (?, ?, ?)',
                [
                    (10, 'ACCOUNTING', 'NEW YORK'),
                    (20, 'RESEARCH', 'DALLAS'),
                    (30, 'SALES', 'CHICAGO'),
                    (40, 'OPERATIONS', 'BOSTON')
                ])
        
        # 插入员工数据
        c.execute('SELECT count(*) FROM EMP')
        if c.fetchone()[0] == 0:
            c.executemany('''
                INSERT INTO EMP (EMPNO, ENAME, JOB, MGR, HIREDATE, SAL, COMM, DEPTNO) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                [
                    (7839, 'KING', 'PRESIDENT', None, '1981-11-17', 5000, None, 10),
                    (7698, 'BLAKE', 'MANAGER', 7839, '1981-05-01', 2850, None, 30),
                    (7782, 'CLARK', 'MANAGER', 7839, '1981-06-09', 2450, None, 10),
                    (7566, 'JONES', 'MANAGER', 7839, '1981-04-02', 2975, None, 20),
                    (7654, 'MARTIN', 'SALESMAN', 7698, '1981-09-28', 1250, 1400, 30),
                    (7499, 'ALLEN', 'SALESMAN', 7698, '1981-02-20', 1600, 300, 30),
                    (7844, 'TURNER', 'SALESMAN', 7698, '1981-09-08', 1500, 0, 30),
                    (7900, 'JAMES', 'CLERK', 7698, '1981-12-03', 950, None, 30),
                    (7521, 'WARD', 'SALESMAN', 7698, '1981-02-22', 1250, 500, 30),
                    (7902, 'FORD', 'ANALYST', 7566, '1981-12-03', 3000, None, 20),
                    (7369, 'SMITH', 'CLERK', 7902, '1980-12-17', 800, None, 20),
                    (7788, 'SCOTT', 'ANALYST', 7566, '1982-12-09', 3000, None, 20),
                    (7876, 'ADAMS', 'CLERK', 7788, '1983-01-12', 1100, None, 20),
                    (7934, 'MILLER', 'CLERK', 7782, '1982-01-23', 1300, None, 10)
                ])
        
        # 插入薪资等级数据
        c.execute('SELECT count(*) FROM SALGRADE')
        if c.fetchone()[0] == 0:
            c.executemany('INSERT INTO SALGRADE (GRADE, LOSAL, HISAL) VALUES (?, ?, ?)',
                [
                    (1, 700, 1200),
                    (2, 1201, 1400),
                    (3, 1401, 2000),
                    (4, 2001, 3000),
                    (5, 3001, 9999)
                ])
        
        conn.commit()
        conn.close()
    
    def execute_query(self, query):
        """执行SQL查询并返回结果"""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        except Exception as e:
            return str(e)
    
    def test_db(self):
        """测试数据库是否正确初始化"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # 检查各个表的记录数
            tables = {
                'DEPT': 'SELECT COUNT(*) FROM DEPT',
                'EMP': 'SELECT COUNT(*) FROM EMP',
                'SALGRADE': 'SELECT COUNT(*) FROM SALGRADE',
                'BONUS': 'SELECT COUNT(*) FROM BONUS'
            }
            
            results = {}
            for table, query in tables.items():
                c.execute(query)
                count = c.fetchone()[0]
                results[table] = count
            
            conn.close()
            return results
            
        except Exception as e:
            return f"Error: {str(e)}" 