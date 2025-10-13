import mysql.connector as c

class database:
    def __init__(self,host="localhost",user="root",passwd="Your Password"):
        self.__host=host
        self.__user=user
        self.__passwd=passwd

    def get_connect(self,database = None):
        self.conn = c.connect(
        host='localhost',
        user='root',
        passwd='Your Password',
        database = database if database else None
        )
        if self.conn == None:
            print("Failed to connect database...!")
        else:
            print("Database Connected...!")
            return self.conn.cursor()

    def commit(self):
        self.conn.commit()
    


    


