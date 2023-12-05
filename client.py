import socket
import threading
import json
import time
import signal
from colorama import init, Fore

class Client():
    prompt = ''
    intro = ''

    def __init__(self):
        super().__init__()
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__id = None
        self.__nickname = None
        self.__isLogin = False

    def __receive_message_thread(self):
        while self.__isLogin:
            try:
                buffer = self.__socket.recv(1024).decode()
                obj = json.loads(buffer)
                print(Fore.LIGHTBLUE_EX + str(obj['sender_nickname']) + '：' + Fore.RESET + obj['message'])
            except Exception:
                print(Fore.RED + '[ERROR] ' + Fore.RESET + '服务端故障，请重新进入')
                time.sleep(5)

    def __send_message_thread(self, message):
        self.__socket.send(json.dumps({
            'type': 'broadcast',
            'sender_id': self.__id,
            'message': message
        }).encode())

    def start(self):
        signal.signal(signal.SIGINT, self.handle_ctrl_c)
        init(autoreset=True)
        self.__socket.connect(('172.20.31.220', 2333))
        nickname = ""
        while nickname == "":
            nickname = input(Fore.YELLOW + '[INPUT] ' + Fore.RESET + '用户名：')
        self.do_login(nickname)
        self.do_send()

    def do_login(self, args):
        nickname = args.split(' ')[0]

        self.__socket.send(json.dumps({
            'type': 'login',
            'nickname': nickname
        }).encode())
        try:
            buffer = self.__socket.recv(1024).decode()
            obj = json.loads(buffer)
            if obj['id']:
                self.__nickname = nickname
                self.__id = obj['id']
                self.__isLogin = True
                print(Fore.GREEN + '[INFO] ' + Fore.RESET + '登录成功')
                thread = threading.Thread(target=self.__receive_message_thread)
                thread.daemon = True
                thread.start()
            else:
                print(Fore.RED + '[ERROR] ' + Fore.RESET + '登录失败')
        except Exception:
            print(Fore.RED + '[ERROR] ' + Fore.RESET + '服务端故障，请重新进入')

    def do_send(self):
        while True:
            message = input()
            print(Fore.LIGHTBLUE_EX + str(self.__nickname) + '：' + Fore.RESET + message)
            thread = threading.Thread(target=self.__send_message_thread, args=(message,))
            thread.daemon = True
            thread.start()

    def handle_ctrl_c(self, signum, frame):
        print('\n' + Fore.GREEN + '[INFO] ' + Fore.RESET + '正常退出')
        self.do_logout()
        exit(0)

    def do_logout(self, args=None):
        self.__socket.send(json.dumps({
            'type': 'logout',
            'sender_id': self.__id
        }).encode())
        self.__isLogin = False
        return True

client = Client()
client.start()
