from netmiko import ConnectHandler
from paramiko.ssh_exception import SSHException

def connect_to_device(device_info):
    try:
        connection = ConnectHandler(**device_info)
        connection.enable()
        return connection
    except SSHException as e:
        print(f"Error connecting to the device: {e}")
        return None

def configure_acl(connection):
    acl_config_commands = [
        'ip access-list standard MY_ACL',
        'permit 192.168.56.0 0.0.0.255',
        'deny any',
    ]
    try:
        connection.send_config_set(acl_config_commands)
        connection.send_command('write memory')
        print("ACL Configuration Successful.")
    except Exception as e:
        print(f"Error configuring ACL: {e}")

def configure_ipsec(connection):
    ipsec_config_commands = [
        'crypto isakmp policy 10',
        'encryption aes',
        'authentication pre-share',
        'group 2',
        'exit',
        'crypto isakmp key YOUR_PRESHARED_KEY address R2_IP',
        'crypto ipsec transform-set MY_TRANSFORM esp-aes esp-sha-hmac',
        'crypto map MY_MAP 10 ipsec-isakmp',
        'set peer R2_IP',
        'set transform-set MY_TRANSFORM',
        'match address MY_ACL',
    ]
    try:
        connection.send_config_set(ipsec_config_commands)
        connection.send_command('write memory')
        print("IPSec Configuration Successful.")
    except Exception as e:
        print(f"Error configuring IPSec: {e}")

# Define device information
device_info = {
    'device_type': 'cisco_ios',
    'ip': 'CSR1000v_IP',
    'username': 'your_username',
    'password': 'your_password',
}

# Replace placeholder values
device_info['ip'] = input("Enter the device IP: ")
device_info['username'] = input("Enter your username: ")
device_info['password'] = input("Enter your password: ")
YOUR_PRESHARED_KEY = input("Enter your pre-shared key: ")
R2_IP = input("Enter R2's IP: ")

# Connect to the device
device_connection = connect_to_device(device_info)

if device_connection:
    # Configure ACL
    configure_acl(device_connection)

    # Configure IPSec
    configure_ipsec(device_connection)

    # Disconnect from the device
    device_connection.disconnect()
