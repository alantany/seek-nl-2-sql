# SQL示例查询
EXAMPLE_QUERIES = {
    "查询所有部门": "SELECT * FROM DEPT;",
    "查询员工及其部门": """
SELECT e.ENAME, d.DNAME, e.SAL
FROM EMP e
JOIN DEPT d ON e.DEPTNO = d.DEPTNO
ORDER BY e.SAL DESC;
    """,
    "查询各部门平均工资": """
SELECT d.DNAME, COUNT(e.EMPNO) as EMP_COUNT, 
       AVG(e.SAL) as AVG_SAL
FROM DEPT d
LEFT JOIN EMP e ON d.DEPTNO = e.DEPTNO
GROUP BY d.DEPTNO, d.DNAME;
    """,
    "查询工资等级分布": """
SELECT s.GRADE, COUNT(e.EMPNO) as EMP_COUNT
FROM EMP e
JOIN SALGRADE s ON e.SAL BETWEEN s.LOSAL AND s.HISAL
GROUP BY s.GRADE
ORDER BY s.GRADE;
    """
} 