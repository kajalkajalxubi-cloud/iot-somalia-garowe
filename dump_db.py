import sqlite3, json
DB='iot_data.db'
conn=sqlite3.connect(DB)
c=conn.cursor()
# Telemetry count
c.execute('SELECT COUNT(*) FROM telemetry')
count=c.fetchone()[0]
# Last 50 telemetry
c.execute('SELECT id,device_id,timestamp,metric,value,unit,status,created_at FROM telemetry ORDER BY id DESC LIMIT 50')
rows=[dict(zip(["id","device_id","timestamp","metric","value","unit","status","created_at"],r)) for r in c.fetchall()]
# Users
c.execute('SELECT id,name,email,created_at FROM users')
users=[dict(zip(["id","name","email","created_at"],r)) for r in c.fetchall()]
conn.close()
print(json.dumps({"telemetry_count":count,"recent_telemetry":rows,"users":users}, default=str, indent=2))
