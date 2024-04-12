import threading
import sqlite3
import os
import requests as req
import pandas as pd
from etc import DATA_PATH

class spec_db:
  _instance_lock = threading.Lock()
  def __init__(self, dbfile):
    self.__db__ = sqlite3.connect(dbfile, check_same_thread = False)
    self.__locker__ = threading.Lock()

  def __del__(self):
    if self.__db__:
      self.__db__.close()
    pass

  def get_create_tbl_sql(self):
    return f'''create table if not exists bim_spec(
               gid INTEGER PRIMARY KEY AUTOINCREMENT,
               associated varchar,
               includes varchar,
               name varchar,
               code varchar,
               level smallint,
               desc varchar,
               imgs varchar,
               page smallint,
               img_1 varchar,
               img_2 varchar,
               img1 blob,
               img2 blob
           );'''

  def insert_tile(self, row):
    with self.__locker__:
      db_cursor = self.__db__.cursor()
      columns = list(row.index)
      sql = "INSERT INTO bim_spec("
      values = "VALUES ("
      data = []
      for col in columns:
        if pd.isna(row[col]):
          continue
        sql = f"{sql}{col},"
        values = f"{values}?,"
        data.append(row[col])
        if col.startswith('img_'):
          sql = f"{sql}img{col[4:]},"
          with open(os.path.join(DATA_PATH, "spec_imgs", os.path.split(row[col])[1]), 'rb') as fr:
            #data.append(req.get(row[col]).content)
            data.append(fr.read())
          values = f"{values}?,"
      sql = f"{sql[:-1]})"
      values = f"{values[:-1]})"
      sql = f"{sql} {values}"
      db_cursor.execute(self.get_create_tbl_sql())
      db_cursor.execute(sql, data)
      self.__db__.commit()
      db_cursor.close()