#!/usr/bin/python3

"""
Example of a script that executes a CLI command on a remote device over\
 established SSH connection.

Administrator login options and CLI commands are device specific, thus\
 this script needs to be adapted to a concrete device specifics.
    Current script assumes interaction with Cisco IOS device.
NOTES: Requires installation of the 'paramiko' Python package using:\
 pip install paramiko
        The 'paramiko' package is documented at: http://docs.paramiko.org
        Complete set of SSH client operations is available at:\
 http://docs.paramiko.org/en/1.15/api/client.html

pydoc-example.py
"""

# Third-party required modules/packages/library
import pexpect


# Read device information from the file
def get_devices_list():
    """
    Get a list of devices from a text file.

    =return: List of devices
    """
    # Create empty list
    devices_list = []

    # Open the device file with the data
    file = open('devices-15.txt', 'r')

    # Retrieve the device IPs and append to list
    for line in file:
        devices_list.append(line.rstrip())

    file.close()

    # Print list of devices
    print('\nDevices list: ', devices_list, end='\n\n')
    return devices_list


# Connect to devices through ssh
def connect(ip_address, username, password):
    """
    Connect to device using pexpect.

    :ip_address: The IP address of the device we are connecting to
    :username: The username that we should use when logging in
    :password: The password that we should use when logging in
    =return: pexpect session object if successful, 0 otherwise
    """
    print('Establishing SSH session: ', ip_address, username, password)

    # Connect via ssh to device
    session = pexpect.spawn('ssh ' + username + '@' + ip_address,
                            encoding='utf-8', timeout=20)
    ssh_newkey = 'Are you sure you want to continue connecting'
    result = session.expect([ssh_newkey, 'Password:', pexpect.TIMEOUT,
                            pexpect.EOF])

    # Check for error, if so then print error and exit
    if result == 0:
        session.sendline('yes')
        result = session.expect([ssh_newkey, 'Password:', pexpect.TIMEOUT,
                                pexpect.EOF])
    elif result != 1:
        print('!!! SSH failed creating session for: ', ip_address)
        exit()

    # Enter the username
    session.sendline(password)
    result = session.expect(['#', pexpect.TIMEOUT, pexpect.EOF])

    # Check for error, if so then print error and exit
    if result != 0:
        print('!!! Password failed: ', password)
        exit()

    print('--- Connected to: ', ip_address)
    return session


# Get version information
def get_version_info(session):
    """
    Get the IOS version from the device.

    :session: The pexpect session object that we are using
    =return: Version number
    """
    print('--- Getting version information')

    # Send command to get version
    session.sendline('show version | include Version')
    result = session.expect(['#', pexpect.TIMEOUT, pexpect.EOF])

    # Check for error, if so then print error and exit
    if result != 0:
        print('!!! FAILED to get version information')
        exit()

    # Extract the 'version' part of the output
    version_output_lines = session.before.splitlines()
    version_output_parts = version_output_lines[1].split(',')
    version = version_output_parts[1].strip()

    print('--- Got version: ', version, end='\n\n')
    return version


# Get list of devices
devices_list = get_devices_list()

# Create file to save output
version_file_out = open('version-info-out.txt', 'w')

# Loop through all the devices in the devices list
for ip_address in devices_list:

    # Connect to the device via CLI and get version information
    session = connect(ip_address, 'cisco', 'cisco123!')
    device_version = get_version_info(session)

    # Close the session
    session.close()

    # Write device data to output file
    version_file_out.write('IP: '+ip_address+'  Version: '+device_version+'\n')

# Done with all devices and writing the file, so close
version_file_out.close()

print('The file version-info-out.txt has been created with device version\
 data\n')
