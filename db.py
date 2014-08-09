from sqlite3            import connect
from datetime           import datetime

class ApartmentDatabase(object):
    def __init__(self, file_name):
        self.conn = connect(file_name)

        self._exec("CREATE TABLE IF NOT EXISTS appartemnts(ID UNIQUE, AREA TEXT, ADDRESS TEXT, DESCRIPTION TEXT, PRICE TEXT, URL TEXT, DISCOVERY_TIMESTAMP TEXT, LAST_SEEN_TIMESTAMP TEXT)")

    def _exec(self, sql, *args):
        res = self.conn.execute(sql, (args))
        if 'SELECT' in sql:
            return res.fetchone()
        else:
            self.conn.commit()

    def _get_now(self):
        return datetime.now().strftime("%H:%M:%S %d-%m-%Y")

    def id_exists(self, id):
        res = self._exec("SELECT COUNT(*) FROM appartemnts WHERE ID=?", id)
        return res[0] > 0

    def update_last_seen(self, id):
        self._exec("UPDATE appartemnts SET LAST_SEEN_TIMESTAMP = ? WHERE ID=?", self._get_now(), id)

    def add_new(self, id, area, address, description, price, url):
        now = self._get_now()
        self._exec("INSERT INTO appartemnts(ID, AREA, ADDRESS, DESCRIPTION, PRICE, URL, DISCOVERY_TIMESTAMP, LAST_SEEN_TIMESTAMP) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                   id, area, address, description, price, url, now, now)