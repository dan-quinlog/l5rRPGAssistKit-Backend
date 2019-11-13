# import mysql.connector #UNINSTALLED, GUIDE FOR MYSQL COMMANDS ONLY

# mydb = mysql.connector.connect(
#   host="localhost",
#   user="root",
#   password="edu34tMY@$$",
#   database="mydatabase" #make sure this is defined at all points after CREATE DATABASE
# )

# mycursor = mydb.cursor()

#create database
# mycursor.execute("CREATE DATABASE mydatabase")

#show all database
# mycursor.execute("SHOW DATABASES")

# for x in mycursor:
#   print(x)

#create table in database
# mycursor.execute("CREATE TABLE customers (name VARCHAR(255), address VARCHAR(255))")

#show tables
# mycursor.execute("SHOW TABLES")

# for x in mycursor:
#   print(x)

#create primary key
# mycursor.execute("CREATE TABLE customers (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), address VARCHAR(255))") #when creating table
# mycursor.execute("ALTER TABLE customers ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY") #when updating table

#insert row of data into table
# sql = "INSERT INTO customers (name, address) VALUES (%s, %s)"
# val = ("John", "Highway 21")
# mycursor.execute(sql, val)

# mydb.commit()

# print(mycursor.rowcount, "record inserted.")

#insert multiple rows of data into table
# sql = "INSERT INTO customers (name, address) VALUES (%s, %s)"
# val = [
#   ('Peter', 'Lowstreet 4'),
#   ('Amy', 'MNE blvd')
# ]

# mycursor.executemany(sql, val)

# mydb.commit()

# print(mycursor.rowcount, "was inserted.")

#insert 1 row and return id
# sql = "INSERT INTO customers (name, address) VALUES (%s, %s)"
# val = ("Michelle", "Blue's Clues")
# mycursor.execute(sql, val)

# mydb.commit()

# print("1 record inserted, ID:", mycursor.lastrowid)

#select all records from the "customers" table and display the result
# mycursor.execute("SELECT * FROM customers")

# myresult = mycursor.fetchall()

# for x in myresult:
#   print(x)

#using fetchone to return the first row of the result
# mycursor.execute("SELECT * FROM customers")

# myresult = mycursor.fetchone()

# print(myresult)