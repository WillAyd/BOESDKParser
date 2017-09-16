import requests
from lxml import etree

class BOESDKParser():
    '''
    This class is a very basic demo of how you can use Python to log into
    a Business Objects platform using its REST API. The class provides methods
    for logging into a theoretical system (provided in the sap_rest_example.py
    module) and retrieving a list of universes.
    '''
    def __init__(self, protocol='http', host='localhost', port='8080',
                 content_type='application/xml'):
        base_url = protocol + '://' + host + ':' + port
        self.bip_url = base_url + '/biprws'
        self.webi_url = self.bip_url + '/raylight/v1'
        self.sl_url = self.bip_url + '/sl/v1'
        self.headers = {
            'accept' : content_type
            }
        
    def _get_auth_info(self):
        return requests.get(self.bip_url + '/logon/long',
                            headers=self.headers)

    def _send_auth_info(self, username, password):
        '''Helper function to retrieve a log in token'''
        root = etree.fromstring(self._get_auth_info().text)
        root[0].text = username
        root[1].text = password

        return requests.post(self.bip_url + '/logon/long',
                             headers=self.headers,
                             data=etree.tostring(root))

    def set_logon_token(self, username, password):
        resp = self._send_auth_info(username, password)
        if resp.status_code == 200:
            root = etree.fromstring(resp.text)
            # Set logon token in headers
            self.headers['X-SAP-LogonToken'] = root[0].text
        else:
            # Crude exception handling
            raise Exception("Could not log on and set the logon token!")

    def get_universes(self):
        resp = requests.get(self.webi_url + '/universes', headers=self.headers)
        if resp.status_code == 200:
            root = etree.fromstring(resp.text)
            # Iterate over the children elements and convert them into a dict
            # of dicts
            univs = dict()
            for index, univ in enumerate(root):
                univs[index] = dict()
                for child in univ:
                    univs[index][child.tag] = child.text

            return univs
        else:
            # Crude Exception handling
            raise Exception(('Could not retrieve universes - have you set a '
                             'valid logon token?'))
        
