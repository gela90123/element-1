def save_running_config_with_details(self, output_file):
    try:
        show_commands = ['show version', 'show interfaces', 'show ip route']  # Add more show commands as needed

        with open(output_file, 'w') as f:
            for command in show_commands:
                print(f"Executing command: {command}")
                self.session.sendline(command)
                result = self.session.expect(['#', pexpect.TIMEOUT, pexpect.EOF])

                if result != 0:
                    logging.error(f'Failed to capture the output of {command} for {self.ip}')
                    print(f"Failed to capture the output of {command} for {self.ip}")
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
