import sqlite3
from pathlib import Path

def database_path():
    p=Path.home()/'.farcodo_hr'; p.mkdir(parents=True,exist_ok=True); return p/'farcodo_hr.sqlite3'
def connect():
    c=sqlite3.connect(database_path()); c.row_factory=sqlite3.Row; c.execute('PRAGMA foreign_keys=ON'); return c
def initialize():
    with connect() as c:
        c.executescript('''CREATE TABLE IF NOT EXISTS employees(id INTEGER PRIMARY KEY, employee_code TEXT UNIQUE NOT NULL, full_name TEXT NOT NULL, national_id TEXT UNIQUE, nationality TEXT DEFAULT '', job_title TEXT DEFAULT '', department TEXT DEFAULT '', phone TEXT DEFAULT '', email TEXT DEFAULT '', status TEXT NOT NULL DEFAULT 'Active', notes TEXT DEFAULT ''); CREATE TABLE IF NOT EXISTS contracts(id INTEGER PRIMARY KEY, contract_number TEXT UNIQUE NOT NULL, employee_id INTEGER NOT NULL REFERENCES employees(id), start_date TEXT NOT NULL, end_date TEXT NOT NULL, basic_salary REAL DEFAULT 0, housing_allowance REAL DEFAULT 0, transport_allowance REAL DEFAULT 0, other_allowance REAL DEFAULT 0, status TEXT DEFAULT 'Draft', notes TEXT DEFAULT '');''')
