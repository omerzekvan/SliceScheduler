import psycopg2
import numpy as np
from psycopg2.extensions import register_adapter, AsIs
def addapt_numpy_float64(numpy_float64):
    return AsIs(numpy_float64)
def addapt_numpy_int64(numpy_int64):
    return AsIs(numpy_int64)
register_adapter(np.float64, addapt_numpy_float64)
register_adapter(np.int64, addapt_numpy_int64)

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
        #id_of_new_row = self.cursor.fetchone()[0]
        count = self.cursor.rowcount
        #print(count, "Record inserted successfully into Slices table")

        postgres_select_query = """SELECT id FROM public."Slices" ORDER BY id DESC LIMIT 1"""

        self.cursor.execute(postgres_select_query)

        self.connection.commit()
        id_of_new_row = self.cursor.fetchone()[0]
        #print('StatusMessage: ', self.cursor.statusmessage)

        return id_of_new_row

    def activateSlice(self, sliceId: int):
        postgres_update_query = """ UPDATE public."Slices" SET "active" = 'true' WHERE "id" = %s """
        record_to_update = (sliceId,)
        self.cursor.execute(postgres_update_query, record_to_update)

        self.connection.commit()

        #id_of_row = list(self.cursor.fetchone()[0])
        #print("Slice activated successfully")

    def insertService(self, functions: str, availability: float):
        # columnCount = len(keyvalues)

        postgres_insert_query = """INSERT INTO public."Services" (functions, availability) VALUES (%s, %s)"""

        record_to_insert = (functions, availability)
        #print("Inserting to Services Table", record_to_insert)
        self.cursor.execute(postgres_insert_query, record_to_insert)
        #self.cursor.execute(postgres_insert_query)

        self.connection.commit()
        #print('StatusMessage: ', self.cursor.statusmessage)

        count = self.cursor.rowcount
        #print(count, "Record inserted successfully into Services table")

        postgres_select_query = """SELECT id FROM public."Services" ORDER BY id DESC LIMIT 1"""
        self.cursor.execute(postgres_select_query)
        self.connection.commit()
        id_of_new_row = self.cursor.fetchone()[0]
        #print('StatusMessage: ', self.cursor.statusmessage)

        return id_of_new_row

    def addSlicetoService(self, serviceId: int, sliceId: int):
        postgres_select_query = """ SELECT slices FROM public."Services" WHERE "id" == %s """
        record_to_select = (serviceId)
        self.cursor.execute(postgres_select_query, record_to_select)
        self.connection.commit()
        slicesList = list(self.cursor.fetchone()[0])
        slicesList.append(sliceId)

        postgres_update_query = """ UPDATE public."Services" SET slices = %s WHERE "id" == %s """
        record_to_update = (slicesList, serviceId)
        self.cursor.execute(postgres_update_query, record_to_update)
        self.connection.commit()
        id_of_row = list(self.cursor.fetchone()[0])
        #print(id_of_row, "Record updated successfully in Services table")
        

    def insertFunction(self, type: str, cpuNeed: int, availability, nodes: str, serviceId: int):
        # columnCount = len(keyvalues)
        postgres_insert_query = """ INSERT INTO public."Functions" (type, cpuNeed, availability, nodes, serviceId) VALUES (%s, %s, %s, %s, %s)"""
        record_to_insert = (type, cpuNeed, availability, nodes, serviceId)
        #print("Inserting to Functions table", record_to_insert)
        self.cursor.execute(postgres_insert_query, record_to_insert)

        self.connection.commit()
        #id_of_new_row = self.cursor.fetchone()[0]
        count = self.cursor.rowcount
        #print(count, "Record inserted successfully into Functions table")

        postgres_select_query = """SELECT id FROM public."Functions" ORDER BY id DESC LIMIT 1"""
        self.cursor.execute(postgres_select_query)
        self.connection.commit()
        id_of_new_row = self.cursor.fetchone()[0]
        #print('StatusMessage: ', self.cursor.statusmessage)

        return id_of_new_row

    def getFunctions(self):
        # columnCount = len(keyvalues)
        postgres_select_query = """ SELECT * FROM public."Functions" """
        # record_to_insert = (type, cpuNeed, nodes, serviceId)
        #print("Selecting all from Functions table")
        self.cursor.execute(postgres_select_query)

        self.connection.commit()
        #id_of_new_row = self.cursor.fetchone()[0]
        count = self.cursor.rowcount
        #print(count, "Record selected from Functions table")

        #postgres_select_query = """SELECT id FROM public."Functions" ORDER BY id DESC LIMIT 1"""
        #self.cursor.execute(postgres_select_query)
        #self.connection.commit()
        rows = self.cursor.fetchall()
        #print('StatusMessage: ', self.cursor.statusmessage)

        return rows

    def addNodesToFunc(self, functionId: int, nodes):
        postgres_update_query = """ UPDATE public."Functions" SET nodes = %s WHERE "id" = %s """
        record_to_update = (nodes, functionId)
        #print("Inserting to Functions table", record_to_update)
        self.cursor.execute(postgres_update_query, record_to_update)

        self.connection.commit()
        #id_of_new_row = self.cursor.fetchone()[0]
        count = self.cursor.rowcount
        #print(count, "Record updated successfully in Functions table")

        return

    def deleteService(self, serviceId: int):
        # columnCount = len(keyvalues)

        postgres_delete_query = """ DELETE FROM public."Services" WHERE "id" = %s """
        record_to_delete = (serviceId,)
        self.cursor.execute(postgres_delete_query, record_to_delete)

        self.connection.commit()
        # id_of_new_row = self.cursor.fetchone()[0]
        count = self.cursor.rowcount
        #print(count, "Record deleted successfully from Functions table")

        # return id_of_new_row

    def deleteFunctions(self, serviceId: int):
        # columnCount = len(keyvalues)
        try:
            postgres_delete_query = """ DELETE FROM public.\"Functions\""""
            if serviceId > -1:
                postgres_delete_query += " WHERE \"serviceid\" = %s"
                record_to_delete = (serviceId,)
                self.cursor.execute(postgres_delete_query, record_to_delete)
            else:
                self.cursor.execute(postgres_delete_query)

            self.connection.commit()
            #id_of_new_row = self.cursor.fetchone()[0]
            count = self.cursor.rowcount
            #print(count, "Record deleted successfully from Functions table")
        except BaseException as Err:
            print("Exception occured why deleting the function: ", Err)

        #return id_of_new_row

if __name__ == '__main__':
    db = DBConn()

    db.connect()

    #db.insertSlice("[{}]", 0.9)

    db.addNodesToFunc(8648, [2, 3])
