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

def configure_ipsec(connection, your_pre_shared_key, r2_ip):
    ipsec_config_commands = [
        'crypto isakmp policy 10',
        'encryption aes',
        'authentication pre-share',
        'group 2',
        'exit',
        f'crypto isakmp key {your_pre_shared_key} address {r2_ip}',
        'crypto ipsec transform-set MY_TRANSFORM esp-aes esp-sha-hmac',
        'crypto map MY_MAP 10 ipsec-isakmp',
        f'set peer {r2_ip}',
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
    'ip': '192.168.56.101',  # Replace with the actual IP address of CSR1000v
    'username': 'cisco',
    'password': 'cisco123!',
}

# Connect to the device
device_connection = connect_to_device(device_info)

if device_connection:
    # Configure ACL
    configure_acl(device_connection)

    # Input your own pre-shared key
    YOUR_PRESHARED_KEY = input("Enter your pre-shared key: ")

    # Input R2's IP
    R2_IP = '172.16.1.2'  # Replace with the actual IP address of R2

    # Configure IPSec
    configure_ipsec(device_connection, YOUR_PRESHARED_KEY, R2_IP)

    # Disconnect from the device
    device_connection.disconnect()
