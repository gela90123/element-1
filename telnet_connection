import pexpect
import logging

# Configure the logging module
logging.basicConfig(filename='telnet_log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def establish_telnet_connection(ip_address, username, password):
    try:
        # Create a Telnet session
        session = pexpect.spawn(f'telnet {ip_address}', encoding='utf-8', timeout=20)
        result = session.expect(['Username:', pexpect.TIMEOUT])

        if result != 0:
            raise Exception(f'Error: Failed to establish a connection to {ip_address}')

        # Enter the username
        session.sendline(username)
        result = session.expect(['Password:', pexpect.TIMEOUT])

        if result != 0:
            raise Exception(f'Error: Failed to enter username {username}')

        # Enter the password
        session.sendline(password)
        result = session.expect(['#', pexpect.TIMEOUT])

        if result != 0:
            raise Exception(f'Error: Failed to enter password {password}')

        # Now that we're connected, modify the device hostname
        session.sendline('configure terminal')
        session.expect('#')
        session.sendline(f'hostname NewHostName')  # Modify the hostname as required
        session.expect('#')
        session.sendline('end')
        session.expect('#')

        # Send a command to the remote device to output the running configuration and save it to a file locally
        session.sendline('show running-config')
        config_output = session.expect(['#', pexpect.TIMEOUT])
        
        if config_output == 0:
            with open('running-config.txt', 'w') as config_file:
                config_file.write(session.before)

        logging.info('Connected to %s', ip_address)
        logging.info('Username: %s', username)
        logging.info('Password: %s', password)

        print('------------------------------------------------------')
        print('Success: Connected to', ip_address)
        print('Username:', username)
        print('Password: ********')
        print('Modified hostname and saved running config locally.')
        print('------------------------------------------------------')
        
        return session

    except Exception as e:
        logging.error(e)
        print(e)
        return None

def main():
    ip_address = '192.168.56.101'
    username = 'cisco'
    password = 'cisco123!'

    session = establish_telnet_connection(ip_address, username, password)

    if session:
        # Terminate the Telnet session
        session.sendline('quit')
        session.close()

if __name__ == '__main__':
    main()
