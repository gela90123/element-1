import netmiko
import difflib

# Function to compare configurations
def compare_configs(current_config, baseline_config):
    d = difflib.Differ()
    diff = list(d.compare(current_config.splitlines(), baseline_config.splitlines()))
    return '\n'.join(diff)

# Function to enable syslog on the device
def enable_syslog(session):
    syslog_commands = [
        "logging host 192.168.1.2",  # Replace with your syslog server IP
        "logging trap informational",
        "logging on",
    ]
    session.send_config_set(syslog_commands)

# Device connection information
connection_info = {
    "device_type": "cisco_ios",
    "host": "192.168.1.1",
    "username": "cisco",
    "password": "cisco",
    "secret": "class",
}

# Connect to the device
session = netmiko.ConnectHandler(**connection_info)
session.enable()

# Get the running configuration
run_config = session.send_command("show running-config")

# Hardening advice (replace with your own hardening recommendations)
hardening_advice = """
! Add your hardening advice here
"""

# Compare running configuration with hardening advice
config_diff = compare_configs(run_config, hardening_advice)

# Display the differences
print("Differences between running config and hardening advice:\n")
print(config_diff)

# Enable syslog on the device
enable_syslog(session)

# Close the session
session.disconnect()
