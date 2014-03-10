from . import utils
from . import DATABASE

class List(object):
    def __init__(self, list_id, title, password):
        self.list_id = list_id
        self.title = title
        self.password = password
        self.items = None

    def delete(self):
        with utils.connection as c:
            c.execute("""
                    DELETE FROM items
                    WHERE list_id=?
                    """, (self.list_id,))
            c.execute("""
                    DELETE FROM todos
                    WHERE list_id=?
                    """, (self.list_id,))
            self.list_id    = None
            self.title      = None
            self.password   = None
            self.items      = None

    def get_id(self):
        return self.list_id

    def set_title(self, title):
        with utils.connection as c:
            c.execute("""
                    UPDATE todos
                    SET title=?
                    WHERE list_id=?
                    """, (title, self.list_id))

    def get_title(self):
        return self.title

    def set_password(self, raw_password):
        if len(raw_password) > 0:
            hashed_password = utils.get_hash(raw_password)
            with utils.connection as c:
                c.execute("""
                        UPDATE todos
                        SET password=?
                        WHERE list_id=?
                        """, (hashed_password, self.list_id))
                return hashed_password

    def get_password(self):
        return self.password

    def has_password(self):
        return len(self.password) > 0

    def get_items(self):
        if not self.items:
            self.items = Item.get_by_list_id(self.list_id)
        return self.items

    def add_item(self, text):
        item = Item.new(self.list_id, text, False)
        if self.items:
            self.items.append(item)

    def remove_item(self, item_id):
        pass

    def remove_marked(self):
        if not self.items: self.get_items()
        with utils.connection as c:
            c.execute("""
                    DELETE FROM items
                    WHERE list_id=? AND done=1
                    """, (self.list_id,))

    @classmethod
    def get_by_id(cls, list_id):
        with utils.connection as c:
            c.execute("""
                    SELECT title, password
                    FROM todos
                    WHERE list_id=?
                    """, (list_id,))
            data = c.fetchone()
            if not data:
                return None
        return List(list_id, data[0], data[1])

class Item(object):
    def __init__(self, item_id, text, done):
        self.item_id  = item_id
        self.text = text
        self.done = done

    def get_id(self):
        return self.item_id

    def get_text(self):
        return self.text

    def is_done(self):
        return self.done

    def mark(self):
        with utils.connection as c:
            c.execute("""
                    UPDATE items
                    SET done=1
                    WHERE item_id=?
                    """, (self.item_id,))

    def unmark(self):
        with utils.connection as c:
            c.execute("""
                    UPDATE items
                    SET done=0
                    WHERE item_id=?
                    """, (self.item_id,))

    @classmethod
    def remove(cls, list_id, item_id):
        with connection as c:
            c.execute("""
                    DELETE FROM items
                    WHERE list_id=? AND item_id=?
                    """, (list_id, item_id))

    @classmethod
    def new(cls, list_id, text, done):
        with utils.connection as c:
            c.execute("""
                    INSERT INTO items (list_id, todo, done)
                    VALUES (?, ?, ?)
                    """, (list_id, text, done))
            return Item(list_id, text, done)

    @classmethod
    def get_by_list_id(cls, list_id):
        with utils.connection as c:
            c.execute("""
                SELECT todo, done, item_id
                FROM items
                WHERE list_id=?
                """, (list_id,))
            items = c.fetchall()
            items_list = []
            for item in items:
                i = Item(item[2], item[0], item[1])
                items_list.append(i)
            return items_list


    @classmethod
    def get_by_id(cls, list_id, item_id):
        with utils.connection as c:
            c.execute("""
                    SELECT todo, done
                    FROM items
                    WHERE list_id=? AND item_id=?
                    """, (list_id, item_id))
            data = c.fetchone()
            return Item(item_id, data[0], data[1])
