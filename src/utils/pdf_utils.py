import pdfplumber
import fitz
import PIL.Image as Image
import io


class pdf_extractor:
  def __init__(self, filename):
    self.__filename__ = filename
    self.__pdf_obj__ = pdfplumber.open(self.__filename__)
    self.__pdf_fitz__ = fitz.open(filename)

  def __extract_img__(self, objid):
    base_image = self.__pdf_fitz__.extract_image(objid)
    image_bytes = base_image["image"]
    return Image.open(io.BytesIO(image_bytes))

  def __find_row_imgs__(self, row, imgs):
    ret = []
    is_for_row = lambda x: row.bbox[1] < x and x < row.bbox[3] or row.bbox[1] > x and x > row.bbox[3]
    for img in imgs:
      if is_for_row((img['top']+img['bottom'])/2):
        ret.append(img)
    return ret

  def get_images_obj(self, imgs):
    return list(set(map(lambda img: img['stream'].objid, imgs)))

  def __line_not_in_tabls__(self, line):
    '''
    whether line does not locates in tables,
    @return True: not locates in tables  False: locates in tables
    '''
    return not self.__line_in_tabls__(line)

  def __line_in_tabls__(self, line):
    '''
    whether text line locates in tables,
    @return True: locates in tables  False: does not locate in tables
    '''
    for tbl in self.__temp_tbls__:
      if tbl.bbox[1] < (line['top'] + line['bottom'])/2 < tbl.bbox[3]:
        return True
    return False

  def __is_valid_item__(self, y_pos):
    '''
    whether position locates in margins
    @retrun True: in margins  False: out of margins
    '''
    return 90.8442 < y_pos and y_pos <719.04

  def __get_pages_objs__(self, page):
    '''
    get all objects with orders, the objects contain text line and tables
    '''
    rc = dict()

    page = self.get_page(page)
    lines = page.extract_text_lines()
    tbls = page.find_tables()
    imgs = page.images

    self.__temp_tbls__ = tbls
    lines = list(filter(self.__line_not_in_tabls__, lines))
    for i in lines:
      if self.__is_valid_item__((i['top']+i['bottom'])/2):
        rc[int((i['top']+i['bottom'])/2)] = i
    for tbl in tbls:
      if self.__is_valid_item__((tbl.bbox[1]+tbl.bbox[3])/2):
        rc[int((tbl.bbox[1]+tbl.bbox[3])/2)] = tbl
    return rc
    #return [rc[key] for key in sorted(rc.keys())]

  def get_page(self, page):
    return self.__pdf_obj__.pages[page]

  def get_page_imgs(self, page):
    return self.get_page(page).images

  def show_page(self, page):
    #objs = self.__get_pages_objs__(page)
    #ret = [objs[key] for key in sorted(objs.keys())]
    ret = self.__get_pages_objs__(page)
    for item in ret:
      if type(item) == type(dict()):
        print(item['text'])
      else:
        print(item.extract())

  def show_all(self):
    for i in range(len(self.__pdf_obj__.pages)):
      print('-'*10, f"P{i+1}", '-'*10)
      self.show_page(i)