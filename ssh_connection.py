import pexpect
import logging
import difflib

class NetworkDeviceConfigurator:
    def __init__(self, ip, username, password, enable_password):
        self.ip = ip
        self.username = username
        self.password = password
        self.enable_password = enable_password
        self.session = None

    def connect(self):
        try:
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
            result = self.session.expect([fr'{new_hostname}\(config\)#', pexpect.TIMEOUT, pexpect.EOF])

            if result != 0:
                logging.error(f'Failed to set the hostname for {self.ip}')
                return False

            self.session.sendline('exit')
            self.session.sendline('exit')

            return True
        except Exception as e:
            logging.error(f"Configuration failed: {e}")
            return False

    def save_running_config(self, output_file):
        try:
            self.session.sendline('show running-config')
            result = self.session.expect(['#', pexpect.TIMEOUT, pexpect.EOF])

            if result != 0:
                logging.error(f'Failed to capture the running configuration for {self.ip}')
                return False

            running_config = self.session.before  # Get the output before the prompt

            with open(output_file, 'w') as f:
                f.write(running_config)

            return True
        except Exception as e:
            logging.error(f"Failed to save the running configuration: {e}")
            return False

    def compare_with_hardening_advice(self, hardening_advice_file):
        try:
            with open(hardening_advice_file, 'r') as f:
                hardening_advice = f.read()

            self.session.sendline('show running-config')
            result = self.session.expect(['#', pexpect.TIMEOUT, pexpect.EOF])

            if result != 0:
                logging.error(f'Failed to capture the running configuration for {self.ip}')
                return False

            running_config = self.session.before

            # Compare running configuration with hardening advice
            d = difflib.Differ()
            diff = list(d.compare(hardening_advice.splitlines(), running_config.splitlines()))

            if any(line.startswith('- ') or line.startswith('+ ') for line in diff):
                print('------------------------------------------------------')
                print('Configuration does not match Cisco device hardening advice:')
                for line in diff:
                    print(line)
                print('------------------------------------------------------')
            else:
                print('------------------------------------------------------')
                print('Configuration matches Cisco device hardening advice.')
                print('------------------------------------------------------')

            return True
        except Exception as e:
            logging.error(f"Failed to compare with hardening advice: {e}")
            return False

    def configure_syslog(self, syslog_server_ip):
        try:
            self.session.sendline('configure terminal')
            result = self.session.expect([r'\(config\)#', pexpect.TIMEOUT, pexpect.EOF])

            if result != 0:
                logging.error(f'Failed to enter config mode for {self.ip}')
                return False

            self.session.sendline(f'logging host {syslog_server_ip}')
            result = self.session.expect([r'\(config\)#', pexpect.TIMEOUT, pexpect.EOF])

            if result != 0:
                logging.error(f'Failed to configure syslog for {self.ip}')
                return False

            self.session.sendline('end')

            return True
        except Exception as e:
            logging.error(f"Syslog configuration failed: {e}")
            return False

    def disconnect(self):
        if self.session:
            self.session.close()
            self.session = None

if __name__ == "__main__":
    logging.basicConfig(filename='network_device_configurator.log', level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

    ip_address = '192.168.56.101'
    username = 'prne'
    password = 'cisco123!'
    password_enable = 'class123!'
    new_hostname = 'R1'
    syslog_server_ip = '<syslog_server_ip>'

    device = NetworkDeviceConfigurator(ip_address, username, password, password_enable)

    if device.connect() and device.configure_hostname(new_hostname):
        print('------------------------------------------------------')
        print('')
        print(f'--- Success! Connecting to {ip_address} as user {username}')
        print(f'--- Password: {password}')
        print(f'--- Hostname changed to: {new_hostname}')
        print('')
        print('------------------------------------------------------')

        # Save the running configuration to a file
        output_file = 'running_config.txt'
        if device.save_running_config(output_file):
            print(f'--- Running configuration saved to {output_file}')
        else:
            print(f'--- Failed to save running configuration.')

        # i. Compare running configuration with hardening advice
        hardening_advice = """
        en
        conf t
        int g0/0
        ip address 192.168.1.1 255.255.255.0
        no shut
        exit
        line vty 0 4
        transport input all
        login local
        username cisco password cisco
        ip domain-name domain.com
        hostname R1
        enable secret class
        crypto key generate rsa
        ip ssh version 2
        """
        with open('cisco_device_hardening.txt', 'w') as f:
            f.write(hardening_advice)

        device.compare_with_hardening_advice('cisco_device_hardening.txt')

        # ii. Configure syslog
        if device.configure_syslog(syslog_server_ip):
            print('--- Syslog configuration successful.')
        else:
            print('--- Syslog configuration failed.')

        logging.info(f"Configuration of {ip_address} successful.")
    else:
        print(f"Configuration of {ip_address} failed.")
        logging.error(f"Configuration of {ip_address} failed.")

    device.disconnect()
