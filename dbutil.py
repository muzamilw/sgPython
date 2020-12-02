import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
   
       
    return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute("DROP TABLE profiles")
        c.execute(create_table_sql)
    except Error as e:
        print(e)

sql_create_profiles_table = """ CREATE TABLE IF NOT EXISTS profiles (
                                        id integer PRIMARY KEY,
                                        profilename text NOT NULL,
                                        igloginjson text NOT NULL,
                                        isConnected integer

                                    ); """

def create_profile(conn, profile):
    """
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
    """
    sql = ''' INSERT INTO profiles(profilename,igloginjson,isConnected)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, profile)
    conn.commit()
    return cur.lastrowid

def update_profile(conn, profile):
    """
    update priority, begin_date, and end date of a task
    :param conn:
    :param task:
    :return: project id
    """
    sql = ''' UPDATE profiles
              SET igloginjson = ? ,
                  isConnected = ? 
              WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, profile)
    conn.commit()

def select_all_profiles(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM profiles")

    rows = cur.fetchall()

    for row in rows:
        print(row)


def select_profile_byname(conn,profilename):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM profiles where profilename = '" +profilename+ "'")

    rows = cur.fetchall()

    return rows[0]

def select_profile_byId(conn,id):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM profiles where id = " +str(id) )

    rows = cur.fetchall()

    return rows[0]                        