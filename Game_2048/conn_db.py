import pymssql, socket, datetime

# 配置
conn = pymssql.connect(
    user='sa',
    password='123456',
    host='192.168.31.223',
    database='test',
    port=1433,
    charset='GB18030'
)

# 创建数据库游标对象
cursor = conn.cursor()


# 获取数据
def get_data(sql='select top 10 * from scores order by score desc'):
    try:
        cursor.execute(sql)
        data = cursor.fetchall()
        json_data = []
        for i in data:
            result_data = {'玩家': i[0], '分数': i[1],
                           '创建时间': i[2].strftime("%Y-%m-%d %H:%M:%S")}
            json_data.append(result_data)
        return json_data
    except Exception as e:
        print('失败\n' + str(e))
    # finally:
    #     cursor.close()
    #     conn.close()


# 插入数据
def set_data(player=socket.gethostbyname(socket.gethostname()), score=0):
    sql = "insert into scores (player,score,create_time) values (%s,%s,CURRENT_TIMESTAMP)"
    values = [(player, score)]
    try:
        cursor.executemany(sql, values)
        # 提交事务
        conn.commit()
        print('成功')
    except Exception as e:
        # 出现错误回滚事务
        conn.rollback()
        print('失败\n' + str(e))
    # finally:
    #     print(get_data('select * from scores'))
    #     cursor.close()
    #     conn.close()
