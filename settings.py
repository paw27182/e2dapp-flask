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
ENVIRONMENT = "development"
# ENVIRONMENT = "production"


# In case of Windows 10
PYTHON_EXE_FILE = r"C:/Python/enve2d/Scripts/python.exe"  # specify python executable file
BASE_DIR = r"C:/temp/e2dapp-flask"  # specify base directory
HOST = "127.0.0.1"  # localhost
PORT = 5002
DB_ADMINISTRATOR = ["kate.walsh@example.com", "mack.davis@example.com"]
DATABASE_TYPE = "SQLite3"
# DATABASE_TYPE = "PostgreSQL"  # UNDISCLOSED
# DATABASE_TYPE = "MongoDB"  # UNDISCLOSED

# # In case of Ubuntu 20.04.6 LT
# PYTHON_EXE_FILE = "/home/paw/enve2d/bin/python3.10"  # specify python executable file
# BASE_DIR = "/home/paw/e2dapp-flask"  # specify base directory
# HOST = "127.0.0.1"
# PORT = 5002
# DB_ADMINISTRATOR = ["kate.walsh@example.com", "mack.davis@example.com"]
# DATABASE_TYPE = "SQLite3"


# # In case of Azure(Linux)
# BASE_DIR = r"."
# HOST = None
# PORT = None
# DB_ADMINISTRATOR = ["kate.walsh@example.com", "mack.davis@example.com"]
# DATABASE_TYPE = "SQLite3"
