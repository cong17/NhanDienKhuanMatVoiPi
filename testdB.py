import sqlite3
from datetime import datetime
import re
import json
def getProfile(id):
    conn = sqlite3.connect("dbNhanDien.db")
    cursor = conn.execute("SELECT name,address FROM info WHERE ID=" + str(id))
    profile = None
    print(cursor)
    for row in cursor:
        profile = row
        profile = str(profile).replace("'", "")
    conn.close()
    return profile

def getProfile1():
    conn = sqlite3.connect("dbNhanDien.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name,address,age,time,Checkout from  info where id!=0")
    data = cursor.fetchall()
    print(data)
    conn.close()
    return json.dumps(data)
def resetCheckOut():
    conn = sqlite3.connect("dbNhanDien.db")
    cur = conn.cursor()

    cmd="UPDATE info SET CheckOut = 0"
    conn.execute(cmd)
    conn.commit()
    conn.close()
    return 1

#hàm điểm danh
def checkOut(id):
    conn = sqlite3.connect("dbNhanDien.db")
    time=datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    cur = conn.cursor()
    cmd1="SELECT checkout  from  info where id=="+str(id)
    cursor=conn.execute(cmd1)
    for row in cursor:
        TFcheckOut = row
        TFcheckOut = re.sub("[\(,\)]", "", str(TFcheckOut), 3)
        

    if int(TFcheckOut)==1:
        return 0
    cmd2="UPDATE info SET Time = '"+str(time)+"',checkout=1 where id="+str(id)
    conn.execute(cmd2)
    conn.commit()
    conn.close()
    return 1


print(getProfile1())

