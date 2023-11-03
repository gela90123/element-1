import pexpect
import logging

# Configure the logging module
logging.basicConfig(filename='telnet_log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def establish_telnet_connection(ip_address, username, password=None):
    try:
        # Create a Telnet session
        session = pexpect.spawn(f'telnet {ip_address}', encoding='utf-8', timeout=20)
        result = session.expect(['Username:', pexpect.TIMEOUT])

        if result != 0:
            raise Exception(f'Error: Failed to establish a connection to {ip_address}')

        # Enter the username
        session.sendline(username)

        if password is None:
            # Prompt for the password
            password = input('Enter password: ')

        session.sendline(password)
        result = session.expect(['#', pexpect.TIMEOUT])

        if result != 0:
            raise Exception(f'Error: Authentication failed for {username}')

        logging.info('Connected to %s', ip_address)
        logging.info('Username: %s', username)
        logging.info('Password: ********')

        print('------------------------------------------------------')
        print('Success: Connected to', ip_address)
        print('Username:', username)
        print('Password: ********')
        print('------------------------------------------------------')

        # Change the hostname (replace these commands with the actual commands)
        session.sendline('configure terminal')
        session.sendline('hostname NEW_HOSTNAME')
        session.sendline('end')
        session.sendline('write memory')  # Save the configuration
        session.expect('#')

        return session

    except Exception as e:
        logging.error(e)
        print(e)
        return None

def main():
    ip_address = '192.168.56.101'
    username = 'cisco'

    session = establish_telnet_connection(ip_address, username)

    if session:
        # Terminate the Telnet session
        session.sendline('quit')
        session.close()

if __name__ == '__main__':
    main()
