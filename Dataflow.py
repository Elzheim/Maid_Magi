import gspread
from gspread import worksheet
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

scope = [
'https://spreadsheets.google.com/feeds',
'https://www.googleapis.com/auth/drive',
]
json_file_name = 'maidmagi-2f63aacdce5f.json'
credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_name, scope)
gc = gspread.authorize(credentials)
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1G-GQQDwm3LwbH9LjuTU2AlCg6Sq18dUswcDIsd-rID4/edit?usp=sharing'
# 스프레스시트 문서 가져오기 
doc = gc.open_by_url(spreadsheet_url)
# 시트 선택하기
worksheet_fixed = doc.worksheet('입력로그')

class Uploader():
    def __init__(self, goods=None, server=None, data=None):
        self.goods = goods
        self.server = server
        self.data = data
    
    def line_split(data):
        Out = data.split('\n')
        return Out
    
    def splitter(data):
        Out = data.split()
        return Out

    def upload(self, goods=None, server=None, data=None):
        self.goods = goods
        self.server = server.upper()
        self.data = Uploader.data_digest(data)
        self.data.insert(0,'goods',[self.goods]*len(self.data))
        self.data.insert(1,'server',[self.server]*len(self.data))
        now = datetime.now()
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
        self.data.insert(6,'time',[date_time]*len(self.data))
        self.data_list = self.data.values.tolist()
        worksheet_fixed.insert_rows(self.data_list,row=2)
        Uploader.search_upload(self)

    def search_upload(self):
        workspace =doc.worksheet(self.server)
        for i in range(len(self.data_list)):
            city = self.data_list[i][2]
            frag = self.data_list[i][3:]
            cell=workspace.find(city)
            for j, data in enumerate(frag):
                workspace.update_cell(cell.row,cell.col+4+j,data)

    def data_digest(data):
        line_list = Uploader.line_split(data)
        stack=[None]*len(line_list)
        for i, line in enumerate(line_list):
            list_in = line.split()
            stack[i]=list_in
        stack= pd.DataFrame(stack,columns=['city','price','trend','drop'])
        return stack

class Downloader():
    def __init__(self, goods = None, server = None):
        self.goods = goods
        self.server = server

    def call_back(self, goods=None, server=None):
        self.goods = goods
        self.server = server
        if self.goods != None and self.server == None:
            return Downloader.goods_only(self)

        elif self.goods!= None and self.server!=None:
            return Downloader.goods_server(self)
        else:
            raise AttributeError

    def firstparser(self):
        cells = worksheet_fixed.findall(self.goods)
        self.data_list = [None]*len(cells)
        for i in range(len(cells)):
            cell = cells[i]
            self.data_list[i] = worksheet_fixed.row_values(cell.row)
        self.data_list = pd.DataFrame(self.data_list, columns=['goods','server','city','price','trend','drop','time'])
        return self.data_list

    def goods_only(self):
        data = Downloader.firstparser(self)
        self.data_goods = data.values.tolist()
        self.goods_list = ["\t".join(data) for data in self.data_goods]
        return self.goods_list
    
    def goods_server(self):
        data = Downloader.firstparser(self)
        query = f'server.str.contains("{self.server}",case=False)'
        data_select = data.query(query)
        self.data_select = data_select.values.tolist()
        self.select_list = [" ".join(data) for data in self.data_select]
        return self.select_list

ud = Uploader()
goods = '오수'
server = 'a'
data = '런던 103 상 귀금폭\n더블린 110 상 \n플리머스 90 하 향신폭'
#ud.upload(goods,server,data)

dl = Downloader()
dl.call_back(goods)
dl.call_back(goods,server)