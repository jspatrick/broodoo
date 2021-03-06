import requests
import json

API_URL = 'http://broodoo.herokuapp.com/brewstats/api/'

def send_request(command, data):
    headers = {'Content-type': 'text/json',
               'user-agent': 'brew-temp-wand/0.0.1'}
    url = API_URL + command + '/'
    r = requests.post(url, data=json.dumps(data), headers=headers)
    if r.status_code != requests.codes.ok:
        print r
        raise RuntimeError("Bad request")
    return json.loads(r.text)


def set_brew_complete():
    """
    Remove a brew
    """
    pass



class Brew(object):
    def __init__(self, username, brewname, id=None):
        if not id:
            self.brew_id = send_request('create_brew', {'user': username, 'name': brewname}).get('brew_id')
        else:
            self.brew_id = id
        if not self.brew_id:
            raise RuntimeError("Couldn't create brew")
        
    def update_temp(self, temp):
        r = send_request('update_brew', {'brew_id': self.brew_id, 'add_temp': temp})
        print r
        
    def create_event(self, event_name="unknown event"):
        r = send_request('update_brew', {'brew_id': self.brew_id, 'add_event': event_name})
        print r
        
