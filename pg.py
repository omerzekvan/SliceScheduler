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
            id_of_new_row = self.cursor.fetchone()[0]
            count = self.cursor.rowcount
            print(count, "Record inserted successfully into Slices table")

            return id_of_new_row

    def insertService(self, functions: str):
        # columnCount = len(keyvalues)
        postgres_insert_query = """ INSERT INTO public."Services" (functions) VALUES (%s)"""
        record_to_insert = (functions)
        self.cursor.execute(postgres_insert_query, record_to_insert)

        self.connection.commit()
        id_of_new_row = self.cursor.fetchone()[0]
        count = self.cursor.rowcount
        print(count, "Record inserted successfully into Services table")

        return id_of_new_row

    def insertFunction(self, type: str, cpuNeed: int, nodes: str, serviceId: int):
        # columnCount = len(keyvalues)
        postgres_insert_query = """ INSERT INTO public."Functions" (type, cpuNeed, nodes, serviceId) VALUES (%s,%s, %s, %s)"""
        record_to_insert = (type, cpuNeed, nodes, serviceId)
        self.cursor.execute(postgres_insert_query, record_to_insert)

        self.connection.commit()
        id_of_new_row = self.cursor.fetchone()[0]
        count = self.cursor.rowcount
        print(count, "Record inserted successfully into Functions table")

        return id_of_new_row

if __name__ == '__main__':
    db = DBConn()

    db.connect()

    db.insertSlice("[{}]", 0.9)
