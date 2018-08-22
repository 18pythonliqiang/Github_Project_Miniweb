import re
import socket

import gevent
import sys
from gevent import monkey

monkey.patch_all()


class HTTPServer(object):
    """Http服务器类(Web服务器类)"""

    def __init__(self,port):
        # 1.1.造tcp服务端socket
        tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 1.2.端口复用
        tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 1.3.绑定ip及端口
        ip_port1 = ('', port)
        tcp_server_socket.bind(ip_port1)
        # 1.4.变主动套接字为被动套接字
        tcp_server_socket.listen(128)
        print('服务器已开启...')
        # 绑定属性
        self.tcp_server_socket = tcp_server_socket

    def start(self):
        """开启服务"""

        # 循环接收客户端发送来了的链接请求
        while True:
            service_client_socket, ip_port2 = self.tcp_server_socket.accept()

            # 打印一下,谁链接到了我们的服务器
            print(ip_port2, '已连接...')

            # 协程实现多任务
            g1 = gevent.spawn(self.client_handler, service_client_socket)

    def client_handler(self, service_client_socket):
        """服务端对客户端的请求处理"""

        # [一] ---------------------解析Http请求报文 -----------------------------

        request_data_bin = service_client_socket.recv(4096)  # 获取请求报文
        if not request_data_bin:
            # print('客户端已断开!')
            service_client_socket.close()
            return

        request_str = request_data_bin.decode('utf-8')  # 解码
        #   把\r\n分割字符串, 获取一个列表,取出第一项,看看是否符合HTTP格式
        request_list = request_str.split('\r\n')
        # print(request_list[0])
        # 正则表达式进行校验: GET /hehehe.html HTTP/1.1
        obj = re.match(r'\w+\s+(\S+)\s+\S+', request_list[0])
        # 如果格式匹配没有通过,说明格式不对
        if obj is None:
            print('客户端发送的内容,不是HTTP协议...')
            service_client_socket.close()
            return
        # 获取资源路径   : request_list[0].split(' ')[1]
        request_url = obj.group(1)
        print("请求路径：",request_url)

        # 注意: 任何网站都有默认主页,如果客户端发送过来的报文,资源路径为: / 把么,我们默认添加一个主页
        if request_url == '/':
            # 添加一个默认主页
            request_url = '/index.html'




        # [二] ---------------------发送Http响应报文 -----------------------------
        # 1. 在web服务器区别处理请求，静态页面请求由自己处理，而动态页面请求交个框架应用程序处理
        # ps: 以.html结尾的请求都视为动态页面请求，其他请求视为静态页面请求
        if request_url.endswith(".html"):
            """处理动态页面请求"""
            """
            2. 按照事先约定好的协议实现双方的通信(web服务器与框架应用程序)
                - web服务器把请求报文信息以字典形式传递给框架应用程序对接的函数
                    env={"PATH_INFO":"/index.html"}
                - 在框架应用程序把处理的结果以返回值的形式返回给web服务器
                    return '200 OK',[('Content-Type','text/html')],'response body'
            """
            env={"PATH_INFO":request_url} # 以字典的形式封装请求报文信息
            import mini_frame
            # '200 OK',[('Content-Type','text/html')],'response body'
            status,headers,response_body=mini_frame.app(env)

            # 4. web服务器把框架应用程序返回的数据组拼成响应报文发送给浏览器客户端
            response_line="HTTP/1.1 %s \r\n"%status
            response_headers="Server: SZPWS/1.0\r\n"
            # 遍历框架传递的头部信息
            for header  in headers:
                #('Content-Type','text/html')
                response_headers+="%s: %s\r\n"%header

            # 组拼响应报文
            response_data=response_line+response_headers+"\r\n"+response_body

            # 发送响应报文给浏览器
            service_client_socket.send(response_data.encode("utf-8"))
            service_client_socket.close()


        else:
            """处理静态页面请求"""
            self.static_response(request_url, service_client_socket)

    def static_response(self, request_url, service_client_socket):
        """处理静态页面请求"""
        try:
            file = open("./static" + request_url, "rb")
        except Exception as e:
            # 打开文件异常
            response_line = "HTTP/1.1 404 Not Found\r\n"
            response_headers = "Server: SZPWS/1.0\r\n"
            # 把错误信息当做body 返回给前台页面
            response_body = "<h1>哎呦, 出错啦 404 %s</h1>" % str(e)
            response_body = response_body.encode()  # 转成二进制码

        else:
            response_line = "HTTP/1.1 200 OK\r\n"
            response_headers = "Server: SZPWS/1.0\r\n"
            # response_headers += "Content-Type: text/html; charset=utf-8\r\n"
            # 打开文件成功
            # 读取内容 二进制
            response_body = file.read()
            # 关闭文件
            file.close()

        finally:
            # print("finally中的代码是一定会执行的代码")
            # 一定需要执行的代码, 或者expect和else中都需要执行的代码

            # 响应行           响应头           空行      响应体
            response_data = (response_line + response_headers + "\r\n").encode('utf-8') + response_body
            service_client_socket.send(response_data)

            # 不模拟长连接,模拟短连接
            service_client_socket.close()


def main():
    if len(sys.argv) == 2:
        try:
            port = int(sys.argv[1])  # 取得执行程序传递过来的端口
        except:
            print("请输入合法参数,比如:")
            print("python3 web.py 8888")
            return
    else:
        print("请输入合法参数,比如:")
        print("python3 web.py 8888")
        return

    # http的请求和响应和都封装在HttpServer类中
    h1 = HTTPServer(port)
    # 开启服务
    h1.start()


# 程序入口
if __name__ == '__main__':
    main()
