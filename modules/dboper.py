# coding:utf-8
import MySQLdb

class MySqlOper(object):
    def __init__(self, ip, user, pwd, dbname):
        self._ip, self._user, self._pwd, self._dbname, self._isconn = ip, user, pwd, dbname, False
       
    def connect(self):
        try:
            self._conn = MySQLdb.connect(host=self._ip, user=self._user, passwd=self._pwd, db=self._dbname)
            self._cur = self._conn.cursor()
            self._isconn = True
            print '成功连接到数据库'
        except MySQLdb.Error as e:
            self._isconn = False
            print 'error %d,%s' % (e.args[0], e.args[1])

    def delete_data(self, orbit):
        if not self._isconn:
            print 'connect error, unable to insert data'
            return
        try:
            self._cur.execute("delete from IDBL1SAMProd WHERE Orbit='%s'" % orbit)
            self._conn.commit()
            print 'delete ok.'
        except MySQLdb.Error as e:
            print 'error %d,%s' % (e.args[0], e.args[1])

    def insert_data(self, sql):
        if not self._isconn:
            print 'connect error, unable to insert data'
            return

        try:
            # sql = "INSERT INTO IDBL1SAMProd (SatId,InstrumentId,Date,Orbit,Latitude,Longitude,SolarZenith,SumValue,ProdType,Bak1,Bak2,Bak3) VALUES ('%s','%s','%s', '%s',%f,%f,%f,%f,'%s','%s','%s','%s')" % \
            #       (data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11])

            # sql = "INSERT INTO IDBL1SAMProd VALUES (%d,'%s','%s','%s', '%s',%f,%f,%f,%f,'%s','%s','%s','%s')" % \
            #       (0, data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11])
            self._cur.execute(sql)
        except MySQLdb.Error as e:
            # logger.warn(e.args[1])
            print 'error %d,%s' % (e.args[0], e.args[1])

    def get_data(self, sql):
        if not self._isconn:
            print 'connect error, unable to insert data'
            return
        try:
            self._cur.execute(sql)
            return self._cur.fetchall()
        except MySQLdb.Error as e:
            # logger.warn(e.args[1])
            print 'error %d,%s' % (e.args[0], e.args[1])
        return None

    def commit_data(self):
        self._conn.commit()

    def close(self):
        self._cur.close()
        self._conn.close()