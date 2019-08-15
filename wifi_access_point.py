import subprocess
import re
from time import sleep


dhcpcd_conf_lines = ["interface wlan0\n",
                     "static ip_address=192.168.4.1/24\n",
                     "nohook wpa_supplicant\n"]


def start_access_point():
    """Start the wifi access point.

    Sets up dhcpcd dnsmasq and hostapd.
    """
    if not _is_dhcpcd_configured_for_ap():
        with open("/etc/dhcpcd.conf", "a") as f:
            f.writelines(dhcpcd_conf_lines)
    subprocess.Popen("sudo systemctl restart dhcpcd", shell=True)
    sleep(1)
    subprocess.Popen("sudo systemctl start dnsmasq", shell=True)
    sleep(1)
    subprocess.Popen("sudo systemctl unmask hostapd", shell=True)
    sleep(1)
    subprocess.Popen("sudo systemctl enable hostapd", shell=True)
    sleep(1)
    subprocess.Popen("sudo systemctl start hostapd", shell=True)


def stop_access_point():
    """Stop access point and switch to normal wifi.

    Stops dnsmasq and hostapd. Also configures dhcpcd and restarts it.
    """
    if _is_dhcpcd_configured_for_ap():
        with open("/etc/dhcpcd.conf", "r") as f:
            contents = f.readlines()
        for line in dhcpcd_conf_lines:
            contents.remove(line)
        with open("/etc/dhcpcd.conf", "w") as f:
            f.writelines(contents)
    subprocess.Popen("sudo systemctl stop dnsmasq", shell=True)
    sleep(1)
    subprocess.Popen("sudo systemctl stop hostapd", shell=True)
    sleep(1)
    subprocess.Popen("sudo systemctl restart dhcpcd", shell=True)
    sleep(1)


def is_client_connected():
    """Check if there is a client connected to the access point."""
    output = str(subprocess.Popen("sudo hostapd_cli all_sta", shell=True, stdout=subprocess.PIPE).stdout.read())
    if output.startswith("Selected interface 'wlan0'"):
        # The program works properly
        if "signal" in output:
            return True
        return False
    else:
        print("ERROR: got incorrect header:\n{}".format(output))
        return False    
            
            
def _is_dhcpcd_configured_for_ap():
    lines = dhcpcd_conf_lines[:]
    with open("/etc/dhcpcd.conf", "r") as f:
        contents = f.readlines()
    for line in contents:
        if line in lines:
            lines.remove(line)
    if lines:
        return False
    return True
