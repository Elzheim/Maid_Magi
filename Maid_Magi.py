import discord
from discord.ext import commands
import gspread
from gspread import worksheet
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import datetime
import os

token = os.environ.get('BOT_TOKEN') # 봇 토큰 

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix='!',intents=intents)

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

    def upload(self, goods=None, server=None, data=None):   # 기본적으로 None을 넣어줫지만 코드가 발동되는 조건이 모두 None이 아닌 경우 뿐
        self.goods = goods
        self.server = server.upper()
        self.data = Uploader.data_digest(self,data)         #data pandas로 만들기
        self.data_list = self.data.values.tolist()          #판다스를 리스트로 변환
        cells1 = worksheet_fixed.findall(self.goods)        #입력로그에서 goods 정보 찾기
        cells2 = worksheet_fixed.findall(self.server)       #입력로그에서 server 정보 찾기
        cells=[cell for cell in cells1 for cell2 in cells2 if cell.row==cell2.row]  #goods와 server의 교집합 cell들 찾기
        if cells==[]:
            worksheet_fixed.insert_rows(self.data_list,row=2)   #만약 입력된적 없는 데이터라면 insert
        else:
            for i, cell in enumerate(cells):                    #이미 기존 데이터가 있다면 update
                for j, data in enumerate(self.data_list[i]):
                    worksheet_fixed.update_cell(cell.row,cell.col+j, data)

    def data_digest(self,data):                             # 데이터 분석 함수
        line_list = Uploader.line_split(data)               # 라인별로 1차 분류
        stack=[None]*len(line_list)                         # 판다스용 틀 제작
        for i, line in enumerate(line_list):
            list_in = line.split()
            stack[i]=list_in
        stack= pd.DataFrame(stack,columns=['city','price','trend','drop'])  # 데이터 정리
        stack.insert(0,'goods',[self.goods]*len(stack))     # 교역품 추가
        stack.insert(1,'server',[self.server]*len(stack))   # 서버 추가
        now = datetime.now()
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
        stack.insert(6,'time',[date_time]*len(stack))       #입력 시간 추가
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

    def goods_only(self):                   # 교역품만 있는 경우
        data = Downloader.firstparser(self) # 데이터 파싱 
        self.data_goods = data.values.tolist()  # 리스트 변환
        self.goods_list = ["\t".join(data) for data in self.data_goods] # 각 요소 합치기
        self.goods_list.sort()  # 정렬
        return self.goods_list
    
    def goods_server(self):                 # 교역품과 서버가 주어진 경우
        data = Downloader.firstparser(self) # 데이터 파싱
        query = f'server.str.contains("{self.server}",case=False)'  #판다스에서 질문지 작성
        data_select = data.query(query)     # 쿼리 추출
        self.data_select = data_select.values.tolist()              # 리스트로 변환
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
        return lines

up=Uploader()
down=Downloader()

@client.event
async def on_ready(): # when bot get ready
    print('Hello World!')
    print(client.user)
    print('==========================================')

@client.command(aliases=['ㅅㅅ','ㅆ','시세']) #ㅅㅅ,ㅆ,시세에 명령어 작동
async def price(ctx, goods=None,server= None,*,message=None):
    goods = goods
    server = server
    message = message
    if message == None:
        datas = down.call_back(goods,server)
        if datas ==[]:      # call_back에 의한 자료가 없을 경우
            await ctx.send('죄송해요..... 입력된 자료가 없어요......ㅠㅠ')
        else:               # call_back에 의한 자료가 있는 경우
            embed = discord.Embed(title="시세 받아라~", desciption='물어보신 교역품과 서버 시세에요!',color=discord.Color.random())
            for i, data in enumerate(datas):
                embed.add_field(name=f'{i+1}번째 기록된 도시예요!', value=data,inline= False)
            await ctx.send(embed=embed)
    else:
        up.upload(goods,server,message)
        await ctx.send('소중한 정보를 주셔서 감사합니당!')
    
@client.command(aliases=['ㄱㅇㅍ','교역품'])
async def trades(ctx, goods):
    goods, cate, cul_city = down.goods_call(goods)
    embed = discord.Embed(title=f'{goods}', desciption=f'{cate}',color=discord.Color.random())
    for key, value in cul_city.items():
        embed.add_field(name=f'{key}',value=f'{value}',inline=False)
    await ctx.send(embed=embed)

@client.command(aliases=['ㅁㅎㄱ','문화권'])
async def cultures(ctx,*,culture):
    culture = culture
    data= down.culture_call(culture)
    embed = discord.Embed(title=f'{culture}',description=f'{data}', color=discord.Color.random())
    await ctx.send(embed=embed)

client.run(token)
