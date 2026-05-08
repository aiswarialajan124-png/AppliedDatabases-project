print("start")
import pymysql
print("imported ok")
try:
    conn = pymysql.connect(host='localhost',user='root',password='root',database='appdbproj')
    print('connected ok')
    c = conn.cursor()
    c.execute('SHOW TABLES')
    print(c.fetchall())
except BaseException as e:
    print("ERROR:", type(e).__name__, e)
print("done")