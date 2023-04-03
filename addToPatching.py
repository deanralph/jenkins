import pymssql
import json
import sys

# Define database connection parameters
with open('/jenkins/sqlcreds.json') as f:
    servcreds = json.load(f)

# Connect to SQL database
conn = pymssql.connect(server=servcreds['server'], database=servcreds["database"], user=servcreds["username"], password=servcreds['password'])

# Define SQL query
sql = f"INSERT INTO [dbo].[servers] ([servername] ,[ipaddress] ,[patchingstatus] ,[rebootreq]) VALUES ({sys.argv[1]}, {sys.argv[2]} ,'Unpatched' ,'False')"

with conn.cursor() as cursor:
    cursor.execute(sql)
    conn.commit()