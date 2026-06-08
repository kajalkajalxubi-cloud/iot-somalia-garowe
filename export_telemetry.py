import sqlite3, csv
DB='iot_data.db'
OUT='telemetry_export.csv'
conn=sqlite3.connect(DB)
c=conn.cursor()
c.execute('SELECT id,device_id,timestamp,metric,value,unit,status,created_at FROM telemetry ORDER BY id')
with open(OUT,'w',newline='',encoding='utf-8') as f:
    writer=csv.writer(f)
    writer.writerow(['id','device_id','timestamp','metric','value','unit','status','created_at'])
    for row in c:
        writer.writerow(row)
conn.close()
print('Exported to', OUT)
