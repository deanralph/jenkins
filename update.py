import pymssql
import subprocess
import json
from fabric import Connection

# Define database connection parameters
with open('/jenkins/sqlcreds.json') as f:
    servcreds = json.load(f)

# Connect to SQL database
conn = pymssql.connect(server=servcreds['server'], database=servcreds["database"], user=servcreds["username"], password=servcreds['password'])

# Define SQL query
sql = "SELECT servername, ipaddress FROM servers where patchingstatus = 'Unpatched'"

def ping(host):
    # Returns True if host responds to a ping request, False otherwise.
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
            
            # Connect to server using Fabric and run apt update
            with Connection(ipaddress) as c:
                c.sudo('sudo apt-get update && sudo apt-get upgrade -y && sudo apt-get dist-upgrade -y')
                
        else:
            print("Server Offline")
        
        print()
