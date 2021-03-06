import os
import time
import sqlite3


DB_PATH = "data/tasks.db"


def init_db(db_path:str=DB_PATH) -> None:
    """ Initializes task db if it doesnt exists. """
    if not os.path.isfile(db_path):
        create_tasks_table()
        for i in range(3):
            add_task(f"TEST TASK {i}", os.getenv("ADMIN_ID"))
    else:
        print("Task db already exists!")
    

def create_tasks_table(db_path:str=DB_PATH) -> None:
    """ Creates empty tasks db. """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""CREATE TABLE all_tasks (
            user integer,
            task_name text,
            date_completed real,
            hours_spent real,
            task_group text,
            deadline text,
            started_time real
            )""")
    conn.close()


def add_task(task_name:str, user:int, db_path:str=DB_PATH) -> None:
    """ Adds task to a text file. """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    with conn:
        c.execute(""" INSERT INTO all_tasks VALUES (:user, 
        :task_name, :date_completed, :hours_spent, :task_group, :deadline, 
        :started_time)""", 
            {"user": user,
             "task_name": task_name, 
             "date_completed": 0, 
             "hours_spent": 0, 
             "task_group": "",
             "deadline": "",
             "started_time": 0})
    conn.close()


def delete_task(task_to_delete:str, user:int, db_path:str=DB_PATH) -> None:
    """ Deletes given task from text file. """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    with conn:
        c.execute("DELETE FROM all_tasks WHERE user = :user AND task_name = :task_name",
                  {"user":user,
                   "task_name": task_to_delete})
    conn.close()


def load_all_tasks(db_path:str=DB_PATH) -> list:
    """ Returns list of all tasks. """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    with conn:
        c.execute("SELECT * FROM all_tasks")
    return c.fetchall()


def get_unfinished_tasks(user:int, db_path:str=DB_PATH):
    task_list = load_all_tasks(db_path)
    output_list = []
    for task in task_list:
        task_user, task_name, date_completed = task[:3]
        if task_user == user and date_completed == 0:
            output_list.append(task_name)
    return output_list


def begin_task(task_name:str, user:int, db_path:str=DB_PATH) -> None:
    """ Mark beginning of a task. """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    with conn:
        c.execute("""UPDATE all_tasks SET started_time = 0 WHERE user = :user""",
                      {"user": user})

    with conn:
        c.execute(""" UPDATE all_tasks SET started_time = :current_time
                    WHERE user = :user AND task_name = :task_name""", 
                    {"current_time": time.monotonic(),
                     "user": user,
                     "task_name": task_name})
    conn.close()


def complete_task(user:int, db_path:str=DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    task_name, hours_spent = get_hours_spent(user)
    with conn:
        c.execute("""UPDATE all_tasks SET date_completed = :current_time,
                 hours_spent = :hours_spent, started_time = 0 
                 WHERE user = :user AND task_name = :task_name""", 
                  {"current_time": time.time(),
                  "hours_spent": hours_spent,
                  "user": user,
                  "task_name": task_name})
    conn.close()
    return task_name, hours_spent


def add_time(user:int, db_path:str=DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    task_name, hours_spent = get_hours_spent(user)
    with conn:
        c.execute("""UPDATE all_tasks SET hours_spent = :hours_spent, started_time = 0 WHERE user = :user AND task_name = :task_name""", 
                  {"hours_spent": hours_spent,
                  "user": user,                                 
                  "task_name": task_name})
    conn.close()
    return task_name, hours_spent


def get_hours_spent(user:int, db_path:str=DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    with conn:
        c.execute("""SELECT * FROM all_tasks WHERE user = :user 
                     AND started_time != 0""", {"user":user})
    _, task_name, _, hours_spent, _, _, begin_time = c.fetchone()
    hours_spent += round((time.monotonic() - begin_time)/60, 2)    
    return task_name, hours_spent


def main():
    init_db()
    print(load_all_tasks())


if __name__ == "__main__":
    main()
