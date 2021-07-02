import requests

def WintogLineNotify(msg):
    url = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': 'Bearer ' + 'xPWZyL5AgxPGl70nIPNHoiLU3330tWA3TcJMaCh8JbX'}
    pay_load = {'message':msg}
    requests.post(url, headers=headers, data=pay_load)
    
if __name__ == '__main__':
    WintogLineNotify('Kevin Test Notify')