import pymssql
import subprocess
from fabric import Connection

# Define database connection parameters
server = '10.0.0.24'
database = 'patching'
username = 'sa'
password = ''

# Connect to SQL database
conn = pymssql.connect(server=server, database=database, user=username, password=password)

# Define SQL query
#insertsql = "INSERT INTO [dbo].[servers] ([servername],[ipaddress],[patchingstatus],[rebootreq]) VALUES ('testserver','testip','Patched','False')"
sql = "SELECT servername, ipaddress FROM servers"

command = """if [ -f /var/run/reboot-required ] 
then
    echo "[*** Hello $USER, you must reboot your machine ***]"
fi"""

def ping(host):
    """
    Returns True if host responds to a ping request, False otherwise.
    """
    command = ['ping', '-c', '1', host]
    # Use subprocess.PIPE to redirect the output to the Python script
    # instead of printing it to the console
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 0

# Execute SQL query and loop through results
with conn.cursor() as cursor:
    cursor.execute(sql)
    for row in cursor:
        servername = row[0]
        ipaddress = row[1]
        print(f"""Servername: {servername}
        IP: {ipaddress}""")

        if ping(ipaddress):
            print("Server Online")
        else:
            print("Server Offline")
        
        print()

        # Connect to server using Fabric and run apt update
        with Connection(ipaddress) as c:
            c.sudo(command)
            c.sudo('sudo apt-get update && sudo apt-get upgrade -y && sudo apt-get autoremove && sudo apt-get autoclean')