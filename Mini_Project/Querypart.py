from database import database

class Queries:
    def __init__(self, database=database(), dbname=None):
        self.database = database
        self.text = database.get_connect()
        if dbname:
            self.create_database(dbname)
        else:
            print("Database Not exists provide it as Query parameter")
            exit(0)
        self.text.execute("""
            CREATE TABLE IF NOT EXISTS user (
                user_id INT PRIMARY KEY Auto_Increment,
                name VARCHAR(100),
                email VARCHAR(100) UNIQUE,
                password VARCHAR(100),
                conform_password VARCHAR(100),
                third_grade_marks VARCHAR(10),
                fourth_grade_marks VARCHAR(10),
                score INT DEFAULT 0,
                percentage DECIMAL(5, 2) DEFAULT 0.0,
                classification VARCHAR(50) DEFAULT NULL,
                class VARCHAR(10)
            );""") 
#         self.text.execute("""CREATE TABLE IF NOT EXISTS quiz_results (
#     quiz_result_id INT AUTO_INCREMENT PRIMARY KEY,
#     student_id INT,
#     quiz_id INT,
#     score INT,
#     percentage DECIMAL(5, 2),
#     FOREIGN KEY (student_id) REFERENCES user(user_id) ON DELETE CASCADE
# );
# """)

    def insert(self, table_name, values, parameters=None):
        """
        returns int
        """
        data_to_insert = f"""
            INSERT INTO {table_name} {f"({parameters})" if parameters else ""} VALUES ({values})"""
        self.text.execute(data_to_insert)
        self.database.commit()
        return self.text.rowcount

    def create_database(self, dbname):
        self.text.execute(f"CREATE DATABASE IF NOT EXISTS {dbname};")
        self.text.execute(f"USE {dbname};")
    
    def check_login(self, email, password):
        self.text.execute(f"""
        SELECT user_id, third_grade_marks, fourth_grade_marks 
        FROM user 
        WHERE email = '{email}' AND password = '{password}';""")
        return self.text.fetchall()

    
    def get_current_user_info(self,user_id):
        self.text.execute(f"""
        select name from user where user_id = {user_id};""")
        return self.text.fetchall()
    
    def check_email(self,email):
        self.text.execute(f"""
        select user_id from user where email = '{email}';""")
        return self.text.fetchall()
    def update_marks(self, user_id, third_grade_marks, fourth_grade_marks):
        self.text.execute(f"""
        UPDATE user SET third_grade_marks = '{third_grade_marks}', fourth_grade_marks = '{fourth_grade_marks}' WHERE user_id = {user_id};""")
        self.database.commit()
        return self.text.rowcount
    def user_count(self):
            self.text.execute(f"""
        select count(user_id)
        from user;
        """)
            return self.text.fetchall()
    def update_classification(self, user_id, classification):
        self.text.execute(f"""
        UPDATE user SET classification = '{classification}' WHERE user_id = {user_id};""")
        self.database.commit()
        print(f"Updated classification for user_id {user_id} to {classification}")
        return self.text.rowcount
    def get_classification_results(self):
        self.text.execute("SELECT user_id, name, email, class, third_grade_marks, fourth_grade_marks, score, percentage, classification FROM user;")
        return self.text.fetchall()



    def get_user_details(self, user_id):
        self.text.execute(f"""
        SELECT class,email,third_grade_marks, fourth_grade_marks, score, percentage, classification
        FROM user
        WHERE user_id = {user_id};""")
        return self.text.fetchall()
    
    def get_students_by_class(self, class_name):
        self.text.execute("""
        SELECT u.user_id, u.name, AVG(q.percentage) as avg_percentage,
        CASE 
            WHEN AVG(q.percentage) < 50 THEN 'Poor'
            WHEN AVG(q.percentage) < 75 THEN 'Average'
            ELSE 'Advanced'
        END as classification
        FROM user u
        LEFT JOIN quiz_results q ON u.user_id = q.student_id
        WHERE u.class = %s  -- Parameterized query
        GROUP BY u.user_id
        """, (class_name,))
        return self.text.fetchall()






        



    
