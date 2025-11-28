from __init__ import CONN, CURSOR
from employee import Employee

class Review:

    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return f"<Review {self.id}: {self.year}, Emp {self.employee_id}>"

    # --------------------
    # PROPERTIES
    # --------------------

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if type(value) is not int or value < 2000:
            raise ValueError("Year must be an integer >= 2000")
        self._year = value

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if type(value) is not str or len(value.strip()) == 0:
            raise ValueError("Summary must be a non-empty string")
        self._summary = value

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        emp = Employee.find_by_id(value)
        if not emp:
            raise ValueError("Employee must exist before assigning employee_id")
        self._employee_id = value

    # --------------------
    # DATABASE METHODS
    # --------------------

    @classmethod
    def create_table(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                year INTEGER,
                summary TEXT,
                employee_id INTEGER,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        sql = "DROP TABLE IF EXISTS reviews"
        CURSOR.execute(sql)
        CONN.commit()

    # --------------------
    # ORM METHODS
    # --------------------

    def save(self):
        if self.id is None:
            sql = """
                INSERT INTO reviews (year, summary, employee_id)
                VALUES (?, ?, ?)
            """
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
            CONN.commit()
            self.id = CURSOR.lastrowid
            Review.all[self.id] = self
        else:
            self.update()

    @classmethod
    def create(cls, year, summary, employee_id):
        review = cls(year, summary, employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        review_id = row[0]

        if review_id in cls.all:
            review = cls.all[review_id]
            review.year = row[1]
            review.summary = row[2]
            review.employee_id = row[3]
        else:
            review = cls(row[1], row[2], row[3], id=review_id)
            cls.all[review_id] = review

        return review

    @classmethod
    def find_by_id(cls, id):
        sql = "SELECT * FROM reviews WHERE id = ?"
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    def update(self):
        sql = """
            UPDATE reviews
            SET year = ?, summary = ?, employee_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    def delete(self):
        sql = "DELETE FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        del Review.all[self.id]
        self.id = None

    @classmethod
    def get_all(cls):
        sql = "SELECT * FROM reviews"
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]
