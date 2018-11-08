

import socket as st
import sys
import os
import signal


# 发送消息、请求
def do_child(s, name, addr):
    while True:
        msg = input("发言：")
        # 如果输入quit表示用户退出
        if msg == "quit":
            msg = 'Q ' + name
            s.sendto(msg.encode(), addr)
            os.kill(os.getppid(), signal.SIGKILL)
            sys.exit(0)
        # 正常聊天
        else:
            msg = 'C %s %s' % (name, msg)
            s.sendto(msg.encode(), addr)


# 接收
def do_parent(s):
    while True:
        msg, addr = s.recvfrom(1024)
        msg = msg.decode() + '\n发言：'
        print(msg, end='')


def connect(s, ADDR):
    while True:
        name = input("请输入姓名：")
        msg = 'L ' + name
        s.sendto(msg.encode(), ADDR)
        data, addr = s.recvfrom(1024)
        if data.decode() == 'OK':
            return (name, addr)
        else:
            print("用户名已存在")


def main():
    if len(sys.argv) < 3:
        print("argv error")
        sys.exit(1)
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    ADDR = (HOST, PORT)
    # 创建数据报套接字
    s = st.socket(st.AF_INET, st.SOCK_DGRAM)
    s.setsockopt(st.SOL_SOCKET, st.SO_REUSEADDR, 1)
    name, addr = connect(s, ADDR)
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    # 创建进程
    pid = os.fork()
    if pid < 0:
        print('创建子进程失败')
        return
    elif pid == 0:
        do_child(s, name, addr)
    else:
        do_parent(s)


if __name__ == '__main__':
    main()
