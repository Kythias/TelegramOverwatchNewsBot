import sqlite3

class DBHelper:
    def __init__(self, dbname="ownewschats.sqlite"):
        # Takes a database name, creates connection
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def setup(self):
        # Creates a new table called "items" with one column called "description"
        stmt = "CREATE TABLE IF NOT EXISTS items (description text)"
        self.conn.execute(stmt)
        self.conn.commit()

    def add_item(self, item_text):
        # Takes text, adds item to table
        stmt = "INSERT INTO items (description) VALUES (?)"
        args = (item_text, )
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_item(self, item_text):
        # Takes text, deletes item from table
        stmt = "DELETE FROM items WHERE description = (?)"
        args = (item_text, )
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_items(self):
        # Returns a list of all items in database, using list comprehension to convert tuple into simple string
        stmt = "SELECT description FROM items"
        return [x[0] for x in self.conn.execute(stmt)]
