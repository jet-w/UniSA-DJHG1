import os
import sys
import requests as req

sys.path.append(os.path.join(os.path.split(__file__)[0], ".."))
from utils.pdf_utils import pdf_extractor
from utils.spec_db import spec_db
from etc import DATA_PATH
import pdfplumber
import pandas as pd


class spec_extract:
  def __init__(self, pdf):
    self.__filename__ = pdf
    self.__pdf_obj__ = pdf_extractor(self.__filename__)
    self.__img_base__ = "https://jet-w.github.io/data/unisa/CapstoneProfessionalProject/bim_spec/"

  # judge whether a table is a spec table
  def is_spec_tbl(self, tbl):
    content = tbl.extract()
    return len(content[0]) == 3
  
  # Get relative of a table include 
  # 1. Associated text
  # 2. Includes Text
  # 3. Code
  # 4. Name
  def get_relative_text(self, pre_lines):
    rc = dict()
    temp = ""
    for item in reversed(pre_lines):
      if type(item)==pdfplumber.table.Table:
        continue
      if abs(item['chars'][0]['size'] - 9) < 0.001:
        if item['text'].strip().startswith('Associated') or item['text'].strip().startswith('Includes'):
          if item['text'].strip().startswith('Associated'):
            temp = f"{item['text']} {temp}"
            rc['associated'] = temp
            temp = ""
          else:
            temp = f"{item['text']} {temp}"
            rc['includes'] = temp
            temp = ""
        else:
          temp = f"{item['text']} {temp}"
      else:
        if item['text'].__contains__('/') or item['text'].__contains__('.'):
          rc['code'] = item['text']
          break
        else:
          rc['name'] = item['text']
    return rc
  
  def __get_table_ret__(self, tbl, objs, page):
    rc = list()
    idx = objs.index(tbl)
    tbl_relative_info = self.get_relative_text(objs[:idx])

    # process tables
    tbls_content = tbl.extract()
    imgs = self.__pdf_obj__.get_page_imgs(page)
    for row in range(len(tbl.rows)):
      obj = dict(tbl_relative_info)
      row_content = tbls_content[row]
      imgs_objid = self.__pdf_obj__.get_images_obj(
                     self.__pdf_obj__.__find_row_imgs__(tbl.rows[row], imgs)
                   )
      row_content[2] = ", ".join(map(str, imgs_objid))
      obj['level'] = row_content[0]
      obj['desc'] = row_content[1]
      obj['imgs'] = row_content[2]
      obj['page'] = page + 1

      for idx, img in enumerate(filter(lambda x: len(x.strip()) > 0, obj['imgs'].split(','))):
        obj[f'img_{idx+1}'] = f"{self.__img_base__}{img.strip()}.png"
        # Save Image to Disk
        out_path = os.path.join(DATA_PATH, "spec_imgs", f"{img.strip()}.png")
        self.__pdf_obj__.__extract_img__(int(img)).save(out_path) if not os.path.exists(out_path) else None
      
      if page >= 179 and page <=186:
        if not obj['code'].__contains__('/'):
          idx = obj['code'].index(' ')
          obj['name'] = obj['code'][idx+1:]
          obj['code'] = obj['code'][:idx]
      rc.append(obj)
    return rc
  
  def save_imgs(self, imgs, out_path):
    for img_ids in map(lambda line: list(filter(lambda x: len(x) > 0, line.split(','))), imgs):
      for img_id in img_ids:
        self.__pdf_obj__.__extract_img__(img_id).save(os.path.join(out_path, img_id, ".png"))

    pass
  def run(self):
    objs      = list()
    page_objs = list()
    page_keep = 3
    rc = []
    
    for page in range(19, 190):
      # get all valid items for page
      current_objs = self.__pdf_obj__.__get_pages_objs__(page)
      # sort all items based on position
      current_objs = [current_objs[key] for key in sorted(current_objs.keys())]

      page_objs.append(current_objs)
      if len(page_objs) > page_keep:
        page_objs.pop(0)
      
      objs = list()
      for item in page_objs:
        objs.extend(item)
      
      # The start index of current page
      idx = len(objs) - len(page_objs[-1])
      for i in range(idx, len(objs)):
        if type(objs[i])==pdfplumber.table.Table:
          if self.is_spec_tbl(objs[i]):
            rc.extend(self.__get_table_ret__(objs[i], objs, page))
    return rc

# Download data from BIMForum
def get_pdf():
  header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}
  pdf_url = "https://bimforum.org/wp-content/uploads/2023/10/LOD-Spec-2023-Part-I-Public-Comment-Draft-2023-12-28.pdf"
  filename = os.path.join(DATA_PATH, os.path.split(pdf_url)[1])
  if not os.path.exists(filename):
    with open(filename, 'wb') as fb:
      resp = req.get(pdf_url, headers=header)
      fb.write(resp.content)
  return filename

if __name__ == "__main__":
  spec_obj = spec_extract(get_pdf())
  df = pd.DataFrame(spec_obj.run())
  df.to_csv(os.path.join(DATA_PATH, 'spec.csv'))
  spec_obj = spec_db(os.path.join(DATA_PATH, "spec.db"))
  try:
    for index, row  in df.iterrows():
      spec_obj.insert_tile(row)
  finally:
    del spec_obj