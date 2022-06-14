import subprocess
from modules import Tele

if __name__ == '__main__':
    ret = subprocess.check_output(["nslookup","myip.opendns.com", "resolver1.opendns.com"], encoding='cp950')
    data = ret.split('\n')
    current_open_ip = data[-3]
    Tele().sendMessage(current_open_ip, group='UpdateMessage')