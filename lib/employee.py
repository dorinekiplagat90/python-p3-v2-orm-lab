from __init__ import CONN, CURSOR

class Employee:

    all = {}

    def __init__(self, name, job_title, department_id, id=None):
        self.id = id
        self.name = name
        self.job_title = job_title
        self.department_id = department_id

    def __repr__(self):
        return f"<Employee {self.id}: {self.name}, {self.job_title}, Dept {self.department_id}>"

    # --------------------
    # PROPERTIES
    # --------------------
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str) or len(value.strip()) == 0:
            raise ValueError("Name must be a non-empty string")
        self._name = value

    @property
    def job_title(self):
        return self._job_title

    @job_title.setter
    def job_title(self, value):
        if not isinstance(value, str) or len(value.strip()) == 0:
            raise ValueError("Job title must be a non-empty string")
        self._job_title = value

    @property
    def department_id(self):
        return self._department_id

    @department_id.setter
    def department_id(self, value):
        from department import Department
        dept = Department.find_by_id(value)
        if not dept:
            raise ValueError("Department must exist before assigning department_id")
        self._department_id = value

    # --------------------
    # DATABASE METHODS
    # --------------------
    @classmethod
    def create_table(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                name TEXT,
                job_title TEXT,
                department_id INTEGER,
                FOREIGN KEY (department_id) REFERENCES departments(id)
            )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        sql = "DROP TABLE IF EXISTS employees"
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        if self.id is None:
            sql = "INSERT INTO employees (name, job_title, department_id) VALUES (?, ?, ?)"
            CURSOR.execute(sql, (self.name, self.job_title, self.department_id))
            CONN.commit()
            self.id = CURSOR.lastrowid
            Employee.all[self.id] = self
        else:
            self.update()

    @classmethod
    def create(cls, name, job_title, department_id):
        emp = cls(name, job_title, department_id)
        emp.save()
        return emp

    @classmethod
    def instance_from_db(cls, row):
        emp_id = row[0]
        if emp_id in cls.all:
            emp = cls.all[emp_id]
            emp.name = row[1]
            emp.job_title = row[2]
            emp.department_id = row[3]
        else:
            emp = cls(row[1], row[2], row[3], id=emp_id)
            cls.all[emp_id] = emp
        return emp

    @classmethod
    def find_by_id(cls, id):
        sql = "SELECT * FROM employees WHERE id=?"
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    @classmethod
    def find_by_name(cls, name):
        """
        Returns the Employee instance whose name matches the given string,
        or None if no such employee exists.
        """
        sql = "SELECT * FROM employees WHERE name = ?"
        row = CURSOR.execute(sql, (name,)).fetchone()
        return cls.instance_from_db(row) if row else None

    def update(self):
        sql = "UPDATE employees SET name=?, job_title=?, department_id=? WHERE id=?"
        CURSOR.execute(sql, (self.name, self.job_title, self.department_id, self.id))
        CONN.commit()

    def delete(self):
        sql = "DELETE FROM employees WHERE id=?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        del Employee.all[self.id]
        self.id = None

    @classmethod
    def get_all(cls):
        sql = "SELECT * FROM employees"
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    # --------------------
    # RELATIONSHIP: Employee → Reviews
    # --------------------
    def reviews(self):
        from review import Review
        sql = "SELECT * FROM reviews WHERE employee_id=?"
        rows = CURSOR.execute(sql, (self.id,)).fetchall()
        return [Review.instance_from_db(row) for row in rows]
