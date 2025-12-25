"""
1.Virtual Organization(login users)
Database administrators
  kate.walsh@example.com, mack.davis@example.com
Group administrators
  group_dx: sakura.suwa@example.com
  group_hr: goro.tani@example.com
  group_sales: harold.meachum@example.com

Update: July 3rd, 2023
"""
from pathlib import Path

ENVIRONMENT = "development"
# ENVIRONMENT = "production"

BASE_DIR = Path(__file__).resolve().parent

# In case of Windows 10
PYTHON_EXE_FILE = r"C:/Python/env/Scripts/python.exe"  # specify python executable file
HOST = "127.0.0.1"  # localhost
PORT = 8000
DB_ADMINISTRATOR = ["kate.walsh@example.com", "mack.davis@example.com"]
DATABASE_TYPE = "SQLite3"
# DATABASE_TYPE = "PostgreSQL"  # UNDISCLOSED
# DATABASE_TYPE = "MongoDB"  # UNDISCLOSED

# # In case of Ubuntu 20.04.6 LT
# PYTHON_EXE_FILE = "/home/paw/enve2d-flask/bin/python3.10"  # specify python executable file
# HOST = "127.0.0.1"
# PORT = 8000
# DB_ADMINISTRATOR = ["kate.walsh@example.com", "mack.davis@example.com"]
# DATABASE_TYPE = "SQLite3"


# # In case of Azure(Linux)
# HOST = None
# PORT = None
# DB_ADMINISTRATOR = ["kate.walsh@example.com", "mack.davis@example.com"]
# DATABASE_TYPE = "SQLite3"
