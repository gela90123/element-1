import pexpect
import logging

class NetworkDeviceConfigurator:
    def __init__(self, ip, username, password, enable_password):
        self.ip = ip
        self.username = username
        self.password = password
        self.enable_password = enable_password
        self.session = None

    def connect(self):
        try:
            # Establish an SSH session
            self.session = pexpect.spawn(f'ssh {self.username}@{self.ip}', encoding='utf-8', timeout=20)
            result = self.session.expect(['Password:', pexpect.TIMEOUT, pexpect.EOF])

            if result != 0:
                logging.error(f'Failed to create an SSH session for {self.ip}')
                return False

            self.session.sendline(self.password)
            result = self.session.expect(['>', pexpect.TIMEOUT, pexpect.EOF])

            if result != 0:
                logging.error(f'Failed to enter the password for {self.ip}')
                return False

            self.session.sendline('enable')
            result = self.session.expect(['Password:', pexpect.TIMEOUT, pexpect.EOF])

            if result != 0:
                logging.error(f'Failed to enter enable mode for {self.ip}')
                return False

            self.session.sendline(self.enable_password)
            result = self.session.expect(['#', pexpect.TIMEOUT, pexpect.EOF])

            if result != 0:
                logging.error(f'Failed to enter enable mode after sending the password for {self.ip}')
                return False

            return True
        except Exception as e:
            logging.error(f"Failed to establish an SSH connection: {e}")
            return False

    def configure_hostname(self, new_hostname):
        try:
            self.session.sendline('configure terminal')
            result = self.session.expect([r'\(config\)#', pexpect.TIMEOUT, pexpect.EOF])

            if result != 0:
                logging.error(f'Failed to enter config mode for {self.ip}')
                return False

            self.session.sendline(f'hostname {new_hostname}')
            result = self.s
