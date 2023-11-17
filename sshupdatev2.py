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
            result = self.session.expect([rf'{new_hostname}\(config\)#', pexpect.TIMEOUT, pexpect.EOF])

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

    def save_running_config_with_details(self, output_file):
        try:
            show_commands = ['show version', 'show interfaces', 'show ip route']  # Add more show commands as needed

            with open(output_file, 'w') as f:
                for command in show_commands:
                    print(f"Executing command: {command}")
                    self.session.sendline(command)
                    result = self.session.expect([pexpect.TIMEOUT, '#'])

                    if result == 0:
                        logging.error(f'Timeout waiting for prompt after {command} for {self.ip}')
                        print(f"Timeout waiting for prompt after {command} for {self.ip}")
                        return False

                    command_output = self.session.before  # Get the output before the prompt
                    f.write(f"=== {command} ===\n")
                    f.write(command_output)
                    f.write("\n\n")

                    logging.info(f'Successfully captured the output of {command} for {self.ip}')
                    logging.info(f'Command output: {command_output}')
                    print(f"Successfully captured the output of {command} for {self.ip}")
                    print(f'Command output: {command_output}')

            return True
        except Exception as e:
            logging.error(f"Failed to save the running configuration with details: {e}")
            print(f"Failed to save the running configuration with details: {e}")
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
    password = 'cisco123!'
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
        else:
            print(f'--- Failed to save running configuration.')

        # Save the running configuration with additional details to a file
        output_file_with_details = 'running_config_with_details.txt'
        if device.save_running_config_with_details(output_file_with_details):
            print(f'--- Running configuration with details saved to {output_file_with_details}')
        else:
            print(f'--- Failed to save running configuration with details.')

        logging.info(f"Configuration of {ip_address} successful.")
    else:
        # Connection or configuration failed
        print(f"Configuration of {ip_address} failed.")
        logging.error(f"Configuration of {ip_address} failed.")

    # Disconnect from the device
    device.disconnect()
