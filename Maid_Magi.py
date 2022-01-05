import discord
from discord.ext import commands
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from Dataflow import *

token = open('Token.txt','r').readline() # 봇 토큰 

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
        embed = discord.Embed(title="시세 받아라~", desciption='물어보신 교역품과 서버 시세에요!',color=discord.Color.random())
        for i, data in enumerate(datas):
            embed.add_field(name=f'{i+1}번째 기록된 도시예요!', value=data,inline= False)
        await ctx.send(embed=embed)
    else:
        up.upload(goods,server,message)
        await ctx.send('소중한 정보를 주셔서 감사합니당!')
    
client.run(token)
