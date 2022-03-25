from util.peewee import MySQLDatabase, Model
from util.peewee import CharField, FloatField

#Connect to mysql database (database name, connection name, port, username, password)
myDB=MySQLDatabase("amsas",host="localhost",port=3306,user="root",passwd="123456")
print("Database connection succeeded")

class Order(Model):
    # order id
    o_id = CharField()

    # start timestamp
    s_time = CharField()

    # end timestamp
    e_time = CharField()

    # starting point longitude
    s_lon = CharField()
    # Starting point latitude
    s_lat = CharField()
    # end point longitude
    e_lon = CharField()
    # End point latitude
    e_lat = CharField()

    class Meta:
        database =myDB
        primary_key = False  # Disable automatic generation of unique id columns
    @classmethod
    def fetch_all(self):
        return list(self.select().dicts())

