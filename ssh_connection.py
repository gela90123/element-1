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
        except pexpect.ExceptionPexpect as e:
            logging.error(f"Failed to establish an SSH connection: {e}")
            return False

    def compare_running_config_with_hardening_advice(self, hardening_advice):
        try:
            # Retrieve running configuration
            self.session.sendline('show running-config')
            self.session.expect(['#', pexpect.TIMEOUT, pexpect.EOF])
            running_config = self.session.before  # Get the output before the prompt

            # Compare configurations
            if running_config.strip() == hardening_advice.strip():
                print("Running configuration is in compliance with Cisco device hardening advice.")
            else:
                print("Running configuration does not match Cisco device hardening advice.")

            return True
        except pexpect.ExceptionPexpect as e:
            logging.error(f"Comparison failed: {e}")
            return False

    def enable_syslog(self, syslog_server_ip):
        try:
            self.session.sendline('configure terminal')
            self.session.expect([r'\(config\)#', pexpect.TIMEOUT, pexpect.EOF])

            self.session.sendline(f'logging host {syslog_server_ip}')
            self.session.expect([r'\(config\)#', pexpect.TIMEOUT, pexpect.EOF])

            self.session.sendline('end')
            self.session.expect(['#', pexpect.TIMEOUT, pexpect.EOF])

            return True
        except pexpect.ExceptionPexpect as e:
            logging.error(f"Syslog configuration failed: {e}")
            return False

    def disconnect(self):
        if self.session:
            self.session.close()
            self.session = None

# Usage
if __name__ == "__main__":
    # Set the device and user credentials
    ip_address = '192.168.56.101'
    username = 'prne'
    password = 'cisco123!'
    enable_password = 'class123!'
    syslog_server_ip = 'IPhere'  # put right ip here when testing
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

    # Initialize logging for error tracking
    logging.basicConfig(filename='network_device_configurator.log', level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

    # Create a NetworkDeviceConfigurator instance
    device = NetworkDeviceConfigurator(ip_address, username, password, enable_password)

    if device.connect():
        # Compare running config with hardening advice
        if device.compare_running_config_with_hardening_advice(hardening_advice):
            print("--- Configuration is in compliance with hardening advice.")
        else:
            print("--- Configuration does not match hardening advice.")

        # Enable syslog
        if device.enable_syslog(syslog_server_ip):
            print("--- Syslog configuration successful.")
        else:
            print("--- Syslog configuration failed.")

        # Disconnect from the device
        device.disconnect()
    else:
        print(f"Configuration of {ip_address} failed.")
        logging.error(f"Configuration of {ip_address} failed.")
