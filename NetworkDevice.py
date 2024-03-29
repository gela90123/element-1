import pexpect
import logging
import getpass
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

    def compare_startup_config(self):
        try:
            self.session.sendline('show startup-config')
            result = self.session.expect(['#', pexpect.TIMEOUT, pexpect.EOF])

            if result != 0:
                logging.error(f'Failed to capture the startup configuration for {self.ip}')
                return False

            startup_config = self.session.before  # Get the output before the prompt

            # You can now compare the running and startup configurations
            diff = difflib.unified_diff(self.session.before.splitlines(), startup_config.splitlines())
            diff_str = '\n'.join(diff)

            print(f'--- Differences between running and startup configurations for {self.ip}:')
            print(diff_str)

            return True
        except Exception as e:
            logging.error(f"Failed to compare configurations: {e}")
            return False

    def compare_local_config(self, local_config_path):
        try:
            with open(local_config_path, 'r') as f:
                local_config = f.read()

            # You can now compare the running and local configurations
            diff = difflib.unified_diff(self.session.before.splitlines(), local_config.splitlines())
            diff_str = '\n'.join(diff)

            print(f'--- Differences between running and local configurations for {self.ip}:')
            print(diff_str)

            return True
        except Exception as e:
            logging.error(f"Failed to compare configurations: {e}")
            return False

    def disconnect(self):
        if self.session:
            self.session.close()
            self.session = None

if __name__ == "__main__":
    # Initialize logging for error tracking
    logging.basicConfig(filename='network_device_configurator.log', level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

    # Set the device and user credentials
    ip_address = '192.168.56.101'
    username = 'prne'
    
    # Prompt for the SSH password
    password = getpass.getpass(f'Enter password for user {username}: ')
    
    password_enable = 'class123!'
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
            
            # Compare running and startup configurations
            if device.compare_startup_config():
                print('--- Startup configuration comparison successful')
            else:
                print('--- Failed to compare startup configuration')

            # Compare running configuration with a local offline version
            local_config_path = 'local_config.txt'  # Provide the path to the local configuration file
            if device.compare_local_config(local_config_path):
                print(f'--- Local configuration comparison successful ({local_config_path})')
            else:
                print('--- Failed to compare local configuration')

            logging.info(f"Configuration of {ip_address} successful.")
        else:
            print(f'--- Failed to save running configuration.')
            logging.error(f"Configuration of {ip_address} failed.")
    else:
        # Connection or configuration failed
        print(f"Configuration of {ip_address} failed.")
        logging.error(f"Configuration of {ip_address} failed.")

    # Disconnect from the device
    device.disconnect()
