
import sys
import os
import socket as st
import signal


def do_login(s, user, name, addr):
    for i in user:
        if i == name or name == '管理员':
            s.sendto(b'FALL', addr)
            return
    s.sendto(b'OK', addr)
    msg = "\n欢迎%s进入聊天室" % name
    # 发送消息给所有用户某人加入聊天室
    for i in user:
        s.sendto(msg.encode(), user[i])
    # 将用户添加到用户字典
    user[name] = addr
    return


def do_chat(s, user, tmp):
    msg = "\n%-4s: %s" % (tmp[1], tmp[2])
    for i in user:
        if i != tmp[1]:
            s.sendto(msg.encode(), user[i])


def do_quit(s, user, name):
    del user[name]
    msg = '\n' + name + '离开聊天室'
    for i in user:
        s.sendto(msg.encode(), user[i])
    return


# 接收处理
def do_child(s):
    # 存储用户
    user = {}
    while True:
        msg, addr = s.recvfrom(1024)
        msg = msg.decode()
        tmp = msg.split(' ', 2)
        if tmp[0] == 'L':
            do_login(s, user, tmp[1], addr)
        elif tmp[0] == 'C':
            do_chat(s, user, tmp)
        elif tmp[0] == 'Q':
            do_quit(s, user, tmp[1])


# 发送系统消息
def do_parent(s, ADDR):
    name = 'C 管理员 '
    while True:
        msg = input("管理员：")
        msg = name + msg
        s.sendto(msg.encode(), ADDR)
    s.close()
    sys.exit(0)


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
    s.bind(ADDR)
    # 处理僵尸进程
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    # 创建进程
    pid = os.fork()
    if pid < 0:
        print('创建子进程失败')
        return
    elif pid == 0:
        do_child(s)
    else:
        do_parent(s, ADDR)


if __name__ == '__main__':
    main()
