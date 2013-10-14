DROP TABLE IF EXISTS items;
DROP TABLE IF EXISTS todos;

CREATE TABLE todos (
	list_id INTEGER PRIMARY KEY,
	title VARCHAR(40),
	password VARCHAR(40)
);

CREATE TABLE items (
	item_id INTEGER PRIMARY KEY AUTOINCREMENT,
	list_id INTEGER,
	todo TEXT NOT NULL,
	done INTEGER NOT NULL,
	FOREIGN KEY (list_id) REFERENCES todos(list_id)
);
