from lxml import etree
from bottle import route, run, request, response

def check_content_type(f):
    def wrapper(*args, **kwargs):
        acc_hdr = request.headers.get('accept')
        if acc_hdr == 'application/xml':
            return f(*args, **kwargs)
        else:
            response.status = 406
            return 'Unrecognized "accept" header'

    return wrapper

def authenticate(f):
    '''Very basic authentication method to check if the logon-token'''
    def wrapper(*args, **kwargs):
        token = request.headers.get('X-SAP-LogonToken')
        if token == ('COMMANDCOM-LCM:6400@{3&2=5595,U3&p=40674.9596541551,Y7&4F='
                     '12,U3&63=secEnterprise,0P&66=60,03&68=secEnterprise:Admini'
                     'strator,0P&qe=100,U3&vz=SFY6agrLPxpfQBK1ZKYCwoBZKCbfsQm7Vg'
                     'WZFiH.RhM,UP'):
            return f(*args, **kwargs)
        else:
            response.status = 401
            return 'Unrecognized logon token'

    return wrapper
        
@route('/biprws/logon/long')
@check_content_type
def login():
    return ('<attrs xmlns="http://www.sap.com/rws/bip">'
            '<attr name="userName" type="string"></attr>'
            '<attr name="password" type="string"></attr>'
            '<attr name="auth" type="string" possibilities="secEnterprise,secLDAP,secWinAD,secSAPR3">secEnterprise</attr>'
            '</attrs>')

@route('/biprws/logon/long', method='POST')
@check_content_type
def login():
    body = request.body.read()
    root = etree.fromstring(body)

    user, pw = root[0].text, root[1].text

    # This only works for a demo. Authentication would be way more complex
    # and use middleware / a database in a real application, but for now
    # we'll just check for a user of myUserName and password of myPassword
    # to match the SAP examples
    if user == 'myUserName' and pw == 'myPassword':
        return ('<attrs xmlns="http://www.sap.com/rws/bip">'
                '<attr name="LogonToken" type="string">COMMANDCOM-LCM:'
                '6400@{3&amp;2=5595,U3&amp;p=40674.9596541551,Y7&amp;4F=12,U3&amp;63=secEnterprise,0P&amp;66=60,03&amp;68='
                'secEnterprise:Administrator,'
                '0P&amp;qe=100,U3&amp;vz=SFY6agrLPxpfQBK1ZKYCwoBZKCbfsQm7VgWZFiH.RhM,UP</attr>'
                '</attrs>')

    # Fall back to a 401
    response.status = 401
    return 'Could not authenticate user with provided credentials'

@route('/biprws/raylight/v1/universes')
@check_content_type
@authenticate
def universes():
    return ('<universes>'
            '<universe>'
            '<id>6773</id>'
            '<cuid>AXyRzvmRrJxLqUm6_Jbf7lE</cuid>'
            '<name>efashion.unv</name>'
            '<type>unv</type>'
            '<folderId>6771</folderId>'
            '</universe>'
            '<universe>'
            '<id>5808</id>'
            '<cuid>AUW2qRdU0IdPkyhlpZWrxvo</cuid>'
            '<name>Warehouse.unx</name>'
            '<type>unx</type>'
            '<folderId>5807</folderId>'
            '</universe>'
            '</universes>')
    
run(host='localhost', port=8080)
