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

        logging.info('Connected to %s', ip_address)
        logging.info('Username: %s', username)
        logging.info('Password: %s', password)

        print('------------------------------------------------------')
        print('Success: Connected to', ip_address)
        print('Username:', username)
        print('Password: ********')
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
