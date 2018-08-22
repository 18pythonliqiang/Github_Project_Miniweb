import re
import time

# 定义一个空的路由列表
import pymysql

g_route_list=[]

# 装饰器工厂
def route(url): # 装饰器工厂
    def wrapper(func): # 装饰器函数
        # url : /index.html
        # func--->index(被装饰的函数的内存空间)
        print("装饰器:url-->",url)
        g_route_list.append((url,func))  # ("/index.html",index)
        def inner():
            print("正在执行拓展的功能...")
            func() # 执行被装饰的函数
        return inner
    return wrapper

@route("/index.html") # 1. 执行route("/index.html")  2. 执行@ wrapper  index=wrapper(index)
# @wrapper
# @wrapper  本质： index=wrapper(index)
def index():
    """处理首页页面请求 路径: /index.html"""
    """
    实现步骤：
        1. 访问数据库，获取动态数据
        2. 读取模板文件
        3. 通过正则表达式，把动态数据替换到模板页面中，形成一个新的动态页面
        4. 返回新的动态页面内容(响应体)
    """
    #1. 访问数据库，获取动态数据
    data_from_mysql=""

    # 创建连接
    conn = pymysql.connect(host='localhost', user='root', password='mysql', port=3306, database='stock_db',charset='utf8')

    # 取得游标
    cs1 = conn.cursor()

    # 执行sql
    sql="select * from info"
    cs1.execute(sql)

    # 取得结果集
    # (1, '000007', '全新好', '10.01%', '4.40%', Decimal('16.05'), Decimal('14.60'), datetime.date(2017, 7, 18))
    result=cs1.fetchall()

    # 遍历结果集
    for line in result:
        line_ui_data="""<tr>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>
                    <input type="button" value="添加" id="toAdd" name="toAdd" systemidvaule="000036">
                </td>
            </tr>"""%(line[0],line[1],line[2],line[3],line[4],line[5],line[6],line[7])
        data_from_mysql+=line_ui_data

    # 2. 读取模板文件
    with open("./templates/index.html") as f:
        content=f.read()

    # 3. 通过正则表达式，把动态数据替换到模板页面中，形成一个新的动态页面
    # 返回替换后的数据
    content=re.sub(r"{%content%}",data_from_mysql,content)

    # 返回新的动态页面内容(响应体)
    return content

@route("/center.html")
def center():
    """处理个人页面请求 路径: /center.html"""
    """
    实现步骤：
        1. 访问数据库，获取动态数据
        2. 读取模板文件
        3. 通过正则表达式，把动态数据替换到模板页面中，形成一个新的动态页面
        4. 返回新的动态页面内容(响应体)
    """
    #1. 访问数据库，获取动态数据
    data_from_mysql=""

    # 创建连接
    conn = pymysql.connect(host='localhost', user='root', password='mysql', port=3306, database='stock_db',
                           charset='utf8')

    # 取得游标
    cs1 = conn.cursor()

    # 执行sql
    sql = "select i.code,i.short,i.chg,i.turnover ,i.price,i.highs,f.note_info from info as i inner join focus as f  on i.id=f.info_id"
    cs1.execute(sql)

    # 取得结果集
    # (1, '000007', '全新好', '10.01%', '4.40%', Decimal('16.05'), Decimal('14.60'), datetime.date(2017, 7, 18))
    result = cs1.fetchall()

    # 遍历结果集
    for line in result:
        line_ui_data="""<tr>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>
                    <a type="button" class="btn btn-default btn-xs" href="/update/300268.html"> <span class="glyphicon glyphicon-star" aria-hidden="true"></span> 修改 </a>
                </td>
                <td>
                    <input type="button" value="删除" id="toDel" name="toDel" systemidvaule="300268">
                </td>
            </tr>"""%(line[0],line[1],line[2],line[3],line[4],line[5],line[6])
        data_from_mysql+=line_ui_data

    # 2. 读取模板文件
    with open("./templates/center.html") as f:
        content=f.read()

    # 3. 通过正则表达式，把动态数据替换到模板页面中，形成一个新的动态页面
    # 返回替换后的数据
    content=re.sub(r"{%content%}",data_from_mysql,content)

    # 返回新的动态页面内容(响应体)
    return content

@route("/gettime.html")
def gettime():
    """处理time页面请求 路径: /gettime.html"""
    return time.ctime()


def error_pager():
    """处理错误页面 """
    return "<a href='http://www.douyu.com/directory/game/yz'><img src='/images/404.jpg'/></a>"



# 路由：(一条请求路径，对应的执行代码) 称为一条路由
# [('/index.html',index),('/center.html',center)]
# 以总揽全局、更加简洁的方式查看与管理请求路径与执行函数的对应关系
# 先配置一个全局的路由列表
# g_route_list=[("/index.html",index),
#               ("/center.html",center),
#               ("/gettime.html",gettime)
#               ]
def app(env):
    """用于处理动态页面的请求，与web服务器对接的函数"""
    """
    按照事先约定好的协议实现双方的通信(web服务器与框架应用程序)
        - web服务器把请求报文信息以字典形式传递给框架应用程序对接的函数
            env={"PATH_INFO":"/index.html"}
        - 在框架应用程序把处理的结果以返回值的形式返回给web服务器
            return '200 OK',[('Content-Type','text/html;charset=utf-8')],'response body'
    """
    #1. 解析字典，获取请求信息
    request_url=env["PATH_INFO"]
    print("请求路径:",request_url)

    #2. 区别不同的请求，请求不同，返回的数据也不同
    # 一条路由('/index.html',index)  (url,func)
    # 遍历路由列表
    for url,func  in g_route_list:
        # request_url: /index.html
        if url==request_url:
            """合法请求"""
            return '200 OK', [('Content-Type', 'text/html;charset=utf-8')], func()  #
    else:
        """非法路径"""
        #返回错误页面
        return '404 Not Found',[('Content-Type','text/html;charset=utf-8')],error_pager()
