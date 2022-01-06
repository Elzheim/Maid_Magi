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
        self.data = Uploader.data_digest(self,data)
        self.data_list = self.data.values.tolist()
        cells1 = worksheet_fixed.findall(self.goods)
        cells2 = worksheet_fixed.findall(self.server)
        cells=[cell for cell in cells1 for cell2 in cells2 if cell.row==cell2.row]
        if cells==[]:
            worksheet_fixed.insert_rows(self.data_list,row=2)
        else:
            for i, cell in enumerate(cells):
                for j, data in enumerate(self.data_list[i]):
                    worksheet_fixed.update_cell(cell.row,cell.col+j, data)

        Uploader.search_upload(self)

    def search_upload(self):
        workspace =doc.worksheet(self.server)
        for i in range(len(self.data_list)):
            city = self.data_list[i][2]
            frag = self.data_list[i][3:]
            cell=workspace.find(city)
            for j, data in enumerate(frag):
                workspace.update_cell(cell.row,cell.col+4+j,data)

    def data_digest(self,data):
        line_list = Uploader.line_split(data)
        stack=[None]*len(line_list)
        for i, line in enumerate(line_list):
            list_in = line.split()
            stack[i]=list_in
        stack= pd.DataFrame(stack,columns=['city','price','trend','drop'])
        stack.insert(0,'goods',[self.goods]*len(stack))
        stack.insert(1,'server',[self.server]*len(stack))
        now = datetime.now()
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
        stack.insert(6,'time',[date_time]*len(stack))
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

    def firstparser(self): # goods 값만 찾는 경우
        cells = worksheet_fixed.findall(self.goods) #goods 검색
        self.data_list = [None]*len(cells)          #빈 레이어 생성
        for i in range(len(cells)):
            cell = cells[i]
            self.data_list[i] = worksheet_fixed.row_values(cell.row)
        self.data_list = pd.DataFrame(self.data_list, columns=['goods','server','city','price','trend','drop','time'])
        return self.data_list

    def goods_only(self):
        data = Downloader.firstparser(self) #데이터 파싱 
        self.data_goods = data.values.tolist()  #리스트 변환
        self.goods_list = ["\t".join(data) for data in self.data_goods] #각 요소 합치기
        self.goods_list.sort()  #정렬
        return self.goods_list
    
    def goods_server(self):
        data = Downloader.firstparser(self)
        query = f'server.str.contains("{self.server}",case=False)'
        data_select = data.query(query)
        self.data_select = data_select.values.tolist()
        self.select_list = ["\t".join(data) for data in self.data_select]
        self.select_list.sort()
        return self.select_list

    def goods_call(self,goods):
        goods = goods
        workplace = doc.worksheet('교역품')
        cell = workplace.find(goods)
        line = workplace.row_values(cell.row)
        goods, cate = line[:2]
        data = line[2:]
        data_dic = {data[i]: data[i+1] for i in range(0, len(data),2)}
        return goods, cate, data_dic

    def culture_call(self, culture):
        culture = culture
        workplace = doc.worksheet('도시')
        cells = workplace.findall(culture)
        lines = [workplace.row_values(cell.row)[1] for cell in cells]
        print(lines)
        return lines

ud = Uploader()
goods = '초롱'
server = 'a'
data = '런던 120 상 향신폭\n더블린 100 상 미술폭\n플리머스 90 하 '
#ud.upload(goods,server,data)

dl = Downloader()
#dl.call_back(goods)
#print(dl.call_back(goods))
#dl.call_back(goods,server)
#dl.goods_call(goods)
dl.culture_call('브리튼 섬')