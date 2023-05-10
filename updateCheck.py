import pymssql
import subprocess
import json
from fabric import Connection

def ping(host):
    """
    Returns True if host responds to a ping request, False otherwise.
    """
    command = ['ping', '-c', '1', host]
    # Use subprocess.PIPE to redirect the output to the Python script
    # instead of printing it to the console
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 0

def updateDB(serverIP, state):
    """
    Updates reboot required field in DB
    """
    insertsql = f"UPDATE dbo.servers SET patchingstatus = '{state}' WHERE ipaddress = '{serverIP}'"

    with pymssql.connect(server=servcreds['server'], database=servcreds["database"], user=servcreds["username"], password=servcreds['password']) as dbconn:
        with dbconn.cursor() as dbcursor:
            dbcursor.execute(insertsql)
            dbconn.commit()


with open('/jenkins/sqlcreds.json') as f:
    servcreds = json.load(f)

# Connect to SQL database
conn = pymssql.connect(server=servcreds['server'], database=servcreds["database"], user=servcreds["username"], password=servcreds['password'])

# Define SQL query
sql = "SELECT servername, ipaddress FROM servers"

with conn.cursor() as cursor:
    cursor.execute(sql)
    for row in cursor:
        servername = row[0]
        ipaddress = row[1]
        print(f"""Servername: {servername}
        IP: {ipaddress}""")

        if ping(ipaddress):
            print("Server Online")

            with Connection(ipaddress) as sshconn:
                result = sshconn.sudo("apt-get -s dist-upgrade | grep '^Inst' | wc -l", hide=True)
                if result.stdout.strip().isdigit():
                    print(f'{result.stdout.strip()} Outstanding Patches Found')
                    updateDB(ipaddress, 'Unpatched')
                else:
                    print('No Outstanding Patches Found')
                    updateDB(ipaddress, 'Patched')

        else:
            print("Server Offline")

        print()
