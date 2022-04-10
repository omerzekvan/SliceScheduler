import psycopg2

class DBConn:
    def __init__(self):
        #self.services = services
        #self.availability = availability
        #self.active = False
        a = 5

    def connect(self):
        conn = None
        try:

            # connect to the PostgreSQL server
            print('Connecting to the PostgreSQL database...')
            self.connection = psycopg2.connect(
                host="172.17.0.2",
                database="postgres",
                user="postgres",
                password="mysecretpassword")

            # create a cursor
            self.cursor = self.connection.cursor()

            # execute a statement
            print('PostgreSQL database version:')
            self.cursor.execute('SELECT version()')

            # display the PostgreSQL database server version
            db_version = self.cursor.fetchone()
            print(db_version)

            # close the communication with the PostgreSQL
            # cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        #finally:
            #if conn is not None:
                # conn.close()
                # print('Database connection closed.')

    def insertSlice(self, services: str, availability: float):
            # columnCount = len(keyvalues)
            postgres_insert_query = """ INSERT INTO public."Slices" (services, availability) VALUES (%s,%s)"""
            record_to_insert = (services, availability)
            self.cursor.execute(postgres_insert_query, record_to_insert)

            self.connection.commit()
            count = self.cursor.rowcount
            print(count, "Record inserted successfully into mobile table")

db = DBConn()

db.connect()

db.insertSlice("[{}]", 0.9)

