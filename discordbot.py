# -*- coding: utf-8 -*-

import asyncio
import discord
import datetime
from discord.ext import tasks
from subprocess import Popen, PIPE, call

# BOT_PREFIX = ("/")
# client = commands.Bot(command_prefix=BOT_PREFIX)

with open("./personal_data/token.txt", "r", encoding="utf_8") as f:
    TOKEN = f.readline()
with open("./personal_data/channelid.txt", "r", encoding="utf_8") as f:
    CHANNEL_ID = int(f.readline())
with open("./personal_data/iphone_IP.txt", "r", encoding="utf_8") as f:
    iphone_IP = f.readline()

wifi_condition = 1 # 続している状態で起動せよ
today = datetime.date.today() # today.month で月を取得
month = today.month
client = discord.Client() # 接続に必要なオブジェクトを生成

def determine_season(month): # 1~4,11.12月：冬, 5~10月：夏
    if month < 5:
        season = "winter"
    elif month < 11:
        season = "summer"
    elif month < 13:
        season = "winter"
    return season

async def aircon_on(message):
    season = determine_season(today.month)
    if season == "winter":
        call(["python3", "irrp.py", "-p", "-g17", "-f", "aircon_on_winter", "aircon_on_winter"])
        m = "もうつけてあるよ！\nあったか～"
    elif season == "summer":
        call(["python3", "irrp.py", "-p", "-g17", "-f", "aircon_on_summer", "aircon_on_summer"])
        m = "もうつけてあるよ！\nすずし～"
    await message.channel.send(m)
    print("A.C. ON")

async def light_on():
    channel = client.get_channel(CHANNEL_ID)
    call(["python3", "irrp.py", "-p", "-g17", "-f", "light_switch", "light_switch"])
    await channel.send("おかえり！")
    print("light ON")

async def light_off():
    channel = client.get_channel(CHANNEL_ID)
    call(["python3", "irrp.py", "-p", "-g17", "-f", "light_switch", "light_switch"])
    await channel.send("いってらっしゃい！")
    await asyncio.sleep(1)
    call(["python3", "irrp.py", "-p", "-g17", "-f", "light_switch", "light_switch"])
    print("light OFF")

async def greet():
    channel = client.get_channel(CHANNEL_ID)
    await channel.send("きたよ！")


@client.event # イベントを受信するための構文. デコレータ（おまじない的な）
async def on_ready(): # 起動したときにターミナルにログイン通知を表示
    await greet()
    print("---------------------------------")
    print("Logged in as")
    print("NAME :", client.user.name)
    print("ID   :", client.user.id)
    print("---------------------------------")
    # iPhoneが接続しているかどうか判定し接続していない場合強制終了したい


@client.event # おまじない的な
async def on_message(message):
    if client.user != message.author:
        if message.content.startswith("おはよ"):
            m = message.author.name + "きっしょ"
            await message.channel.send(m)
        if message.content.startswith("エアコン"): # エアコンつける
            await aircon_on(message)


@tasks.loop(seconds=5) # wifi接続判定
async def loop():
    global wifi_condition # global変数あんま使いたくないわね
    global previous_wifi_condition
    channel = client.get_channel(CHANNEL_ID)
    p1 = Popen(["ping", "-c", "1", iphone_IP], stdout=PIPE)
    stdout_value = p1.communicate()[0]
    previous_wifi_condition = wifi_condition
    if b'0 received' not in stdout_value:
        wifi_condition = 1 # 接続中
        print("FOUND iPhone")
        if previous_wifi_condition != wifi_condition:
            await light_on()
    else:
        wifi_condition = 0 # 接続なし
        print("NO iPhone")
        if previous_wifi_condition != wifi_condition:
            await light_off()


loop.start()

client.run(TOKEN) # bot起動とdiscordサーバーへの接続
