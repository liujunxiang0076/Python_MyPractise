import json

import pymssql
import pandas as pd


def get_conn():
    # 1.创建sqlserver数据库连接对象connection
    # connection对象支持的方法有cursor(),commit(),rollback(),close()
    conn = pymssql.connect(
        user='sa',
        password='123456',
        host='localhost',
        database='test',
        port=1433,
        charset='GB2312'
    )
    return conn


# 2.创建mysql数据库游标对象 cursor
# cursor对象支持的方法有execute(sql语句),fetchone(),fetchmany(size),fetchall(),rowcount,close()
cursor = get_conn().cursor()
# 3.编写sql
sql = 'select * from plane'
# 4.执行sql命令
# execute可执行数据库查询select和命令insert，delete，update三种命令(这三种命令需要commit()或rollback())
cursor.execute(sql)
# 5.获取数据
# fetchall遍历execute执行的结果集。取execute执行后放在缓冲区的数据，遍历结果，返回数据。
# 返回的数据类型是元组类型，每个条数据元素为元组类型:
# (('第一条数据的字段1的值','第一条数据的字段2的值',...,'第一条数据的字段N的值'),(第二条数据),...,(第N条数据))
data = cursor.fetchall()

# 6.关闭cursor
cursor.close()
# 7.关闭connection
get_conn().close()
# 循环读取元组数据
# 将元组数据转换为列表类型，每个条数据元素为字典类型:
# [{'字段1':'字段1的值','字段2':'字段2的值',...,'字段N:字段N的值'},{第二条数据},...,{第N条数据}]
json_data = []
for i in data:
    result = dict()
    result['id'] = i[0]
    result['begin_city'] = i[1]
    result['begin_city_x'] = i[2]
    result['begin_city_y'] = i[3]
    result['end_city'] = i[4]
    result['end_city_x'] = i[5]
    result['end_city_y'] = i[6]
    result['length'] = i[7]
    json_data.append(result)

col_name = ['id', 'begin_city', 'begin_city_x', 'begin_city_y', 'end_city', 'end_city_x', 'end_city_y', 'length']
pd.set_option('display.width', None)  # 设置字符显示无限制
pd.set_option('display.max_rows', None)  # 设置行数显示无限制
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)

df = pd.DataFrame(data, columns=col_name)
# print(df)
print(json_data)


# print(json.dumps(json_data, ensure_ascii=False)[1:len(json.dumps(json_data, ensure_ascii=False)) - 1])
