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

    def compare_with_cisco_hardening(self):
        try:
            self.session.sendline('show running-config')
            result = self.session.expect(['#', pexpect.TIMEOUT, pexpect.EOF])

            if result != 0:
                logging.error(f'Failed to capture the running configuration for {self.ip}')
                return False

            running_config = self.session.before  # Get the output before the prompt

            # Cisco device hardening advice from provided text
            cisco_hardening_advice = """
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
            crypto key generate rsa modulus 2048
            ip ssh version 2
            """

            # Compare the running configuration with the hardening advice
            if cisco_hardening_advice.strip() in running_config.strip():
                print('------------------------------------------------------')
                print(f'--- Running configuration complies with Cisco device hardening advice for {self.ip}')
                print('------------------------------------------------------')
                return True
            else:
                print('------------------------------------------------------')
                print(f'--- Running configuration does not comply with Cisco device hardening advice for {self.ip}')
                print('------------------------------------------------------')
                return False
        except Exception as e:
            logging.error(f"Failed to compare with Cisco device hardening advice: {e}")
            return False

    def enable_syslog(self):
        try:
            self.session.sendline('configure terminal')
            self.session.sendline('logging on')  # Enable syslog
            self.session.sendline('end')
            result = self.session.expect(['#', pexpect.TIMEOUT, pexpect.EOF])

            if result != 0:
                logging.error(f'Failed to enable syslog for {self.ip}')
                return False

            return True
        except Exception as e:
            logging.error(f"Failed to enable syslog: {e}")
            return False

    def disconnect(self):
        if self.session:
            self.session.close()
            self.session = None

if __name__ == "__main__":
    # Initialize logging for error tracking
    logging.basicConfig(filename='network_device_configurator.log', level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

    # Set the device and user credentials
    ip_address = '192.168.1.1'  # Update with your actual device IP
    username = 'your_username'  # Update with your actual username
    password = 'your_password'  # Update with your actual password
    password_enable = 'your_enable_password'  # Update with your actual enable password
    new_hostname = 'R1'

    # Create a NetworkDeviceConfigurator instance
    device = NetworkDeviceConfigurator(ip_address, username, password, password_enable)

    if device.connect() and device.configure_hostname(new_hostname):
        # Successful connection and hostname configuration
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

        # Compare with Cisco device hardening advice
        if device.compare_with_cisco_hardening():
            print('--- Device complies with Cisco device hardening advice.')

        # Enable syslog
        if device.enable_syslog():
            print('--- Syslog enabled on the device.')

        logging.info(f"Configuration of {ip_address} successful.")
    else:
        # Connection or configuration failed
        print(f"Configuration of {ip_address} failed.")
        logging.error(f"Configuration of {ip_address} failed.")

    # Disconnect from the device
    device.disconnect()
