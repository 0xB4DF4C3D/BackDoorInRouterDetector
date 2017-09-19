import paramiko as pm

class SSH():

    def __init__(self, hostname, username, password, port=22):
        self.__hostname = hostname
        self.__password = password
        self.__username = username
        self.__port     = port

        self.__client = pm.SSHClient()
        self.__client.load_system_host_keys()
        self.__client.set_missing_host_key_policy(pm.WarningPolicy)
        self.__client.connect(self.__hostname, self.__port, self.__username, self.__password)

        self.__channel = self.__client.invoke_shell()
        
    def send(self, command):
        self.__channel.send(command+'\n')
        
    def recv(self):
        return self.__channel.recv(9999)

    def __del__(self):
        self.__client.close()


