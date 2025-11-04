import paramiko

class ssh:
    def __init__(self, hostname, username, password):
        self.hostname = hostname
        self.username = username
        self.password = password
    
    def execute(self, commande):
        stdin, stdout, stderr = self.ssh.exec_command(commande)
        return stdout.read().decode()
    
    def connect(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.ssh.connect(
            self.hostname,
            username=self.username,
            password=self.password,
            port=22,
            look_for_keys=False,
            allow_agent=False
        )
    
    def close_connection(self):       
        self.ssh.close()


