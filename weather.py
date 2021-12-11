import json
import time
import random
import datetime
import pypinyin

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import streamlit as st
from PIL import Image

#解决中文显示问题
plt.rcParams['font.sans-serif'] = ['KaiTi'] # 指定默认字体
plt.rcParams['axes.unicode_minus'] = False # 解决保存图像是负号'-'显示为方块的问题


# 设置网页
st.set_page_config(page_title="天气看板", page_icon=":sunny:", layout="wide")


# 获取时间
now_time = datetime.datetime.now()
now_year = now_time.strftime('%Y')
now_month = now_time.strftime('%m')
now_day = now_time.strftime('%d')

# 设置爬取的城市
cityList = ['北京','福州','厦门','龙岩']
pinyinList = []

# 汉子转拼音
def pinyin(word):
    pinyin = ''
    for i in pypinyin.pinyin(word, style=pypinyin.NORMAL):
        pinyin += ''.join(i)
    return pinyin

for c in cityList:
    pinyin(c)
    pinyinList.append(pinyin(c))

# 数据爬虫
month_list = ['01','02','03','04','05','06','07','08','09','10','11','12'] # 月份列表
urls = []

for p in pinyinList: # 多个城市本年所有历史天气urls
    for j in range(0,len(month_list)):
        if month_list[j] < '11': # 12月好像会出点问题，再看看
            url = 'http://lishi.tianqi.com/' + p + '/'+ now_year + month_list[j] + '.html'
            urls.append(url)

file = open('st_weather.csv','w',encoding='utf-8')
header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'}

for url in urls:                                                       
    response = requests.get(url,headers = header)                                                     
    soup = BeautifulSoup(response.text, 'lxml')                               
    weather_list = soup.select('div[class="tian_three"]')
    for weather in weather_list:
        if url == urls[0]: # 判断：只有第一次爬取标题
            # 爬取标题
            a = soup.select('div[class="flex thalin"]')
            for i in a:
                j = i.select('div')
                str="" 
                for h in j:
                    if(h.string == None):
                        str = str+'无数据'+',' # 逗号表示分隔符（到下一格）
                    else:
                        str = str+h.string+','
                if (str!=' '):                                                                 
                    file.write(str+'\n')
            
            # 爬取数据
            ul_list = weather.select('li')                                                                                                                    
            for ul in ul_list:                                                           
                li_list= ul.select('div')
                str="" 
                for li in li_list:
                    if(li.string == None):
                        str = str+'无数据'+','
                    else:
                        str = str+li.string+','
                if (str!=' '):                                                                 
                    file.write(str+'\n')
        else:
            ul_list = weather.select('li')                                                                                                                    
            for ul in ul_list:                                                           
                li_list= ul.select('div')
                str="" 
                for li in li_list:
                    if(li.string == None):
                        str = str+'无数据'+','
                    else:
                        str = str+li.string+','
                if (str!=' '):                                                                 
                    file.write(str+'\n')
                
                                                                 
file.close() 

# 读取数据
def get_data_from_excel():
    df = pd.read_csv("st_weather.csv")
    return df

df = get_data_from_excel()

# 获取时间
ymd = now_time.strftime('%Y-%m-%d')

# 小小改下df格式
df['日期'] = df['日期'].str[:-5]
df['日期'] = pd.to_datetime(df['日期']) # 转换日期格式为datetime
df['Month'] = df['日期'].dt.month # 增加一列“月份”
df['最高气温'] = pd.to_numeric(df['最高气温'].str[:-1]).astype(int) # 字符串切割与转换为int类型
df['最低气温'] = pd.to_numeric(df['最低气温'].str[:-1]).astype(int)
m = int(len(df.index)/len(cityList)) # 计算多少个月
newCityList = [val for val in cityList for i in range(m)] # 使每个元素重复，方便放入dataframe
df['城市'] = newCityList # 增加城市列

# 侧边栏
st.sidebar.header(f"当前日期：{ymd}")

# bgm曲目功能
music = st.sidebar.radio('选择你喜欢的曲目',['卡农','Summer'],index=random.choice(range(2)))
st.sidebar.write(f'正在播放 {music}... :musical_note:')

@st.cache
def get_audio_bytes(music):
    audio_file = open(f'weather-music/{music}.mp3', 'rb')
    audio_bytes = audio_file.read()
    audio_file.close()
    return audio_bytes

audio_bytes = get_audio_bytes(music)
st.sidebar.audio(audio_bytes, format='audio/mp3')

city = st.sidebar.selectbox(
    "当前城市:",
    options = df["城市"].unique()
)

mode = st.sidebar.selectbox(
    "当前模式:",
    ("历史天气","天气预报(待开发)")
)

time = st.sidebar.multiselect(
    "当前月份:",
    options = df["Month"].unique(),
    default = df["Month"].unique()
)

df_selection = df.query("Month == @time & 城市 == @city") # query中含有变量！是之前的三个侧边框

# 主页面
st.title(":sunny: 小蒋带你看天气")
st.text('目前仅可查看2021年天气数据(我是废物...)')
st.markdown("###")

# 最高温，最低温，平均高/低温
max_temperature = df_selection['最高气温'].max()
min_temperature = df_selection['最低气温'].min()
average_hightemperature = round(df_selection['最高气温'].mean(),1)
average_lowtemperature = round(df_selection['最低气温'].mean(),1)

# 4列布局
col1, col2, col3, col4 = st.columns(4)

# 添加相关信息
with col1:
    st.subheader(f"{max_temperature}℃")
    st.caption("最高气温")
with col2:
    st.subheader(f"{min_temperature}℃")
    st.caption("最低气温")
with col3:
    st.subheader(f"{average_hightemperature}℃")
    st.caption("平均高温")
with col4:
    st.subheader(f"{average_lowtemperature}℃")
    st.caption("平均低温")

# 分隔符
st.markdown("""---""")

# 折线图
st.markdown(f'##### 气温曲线(截至{now_year}年11月)')

fig1 = px.line(df_selection, x = df_selection['日期'], y = df_selection['最高气温'], color_discrete_sequence=['red'])
fig2 = px.line(df_selection, x = df_selection['日期'], y = df_selection['最低气温'], color_discrete_sequence=['blue'])

layout = go.Layout(
    xaxis={'title':'时间'},
    yaxis={'title':'温度/℃'})

fig = go.Figure(data = fig1.data + fig2.data, layout=layout)
st.plotly_chart(fig, use_container_width=True)

# 分隔符
st.markdown("""---""")
st.markdown(f'##### 天气情况统计(截至{now_year}年11月)')

# 2列布局
col1, col2 = st.columns(2)

#筛选天气类型并统计
weather_dataframe = df_selection.groupby(["天气"]).count()[['日期']].sort_values(by="日期",ascending = True).rename(columns={'日期':'天数'}) # 此处要设置True从小到大排序，为了方便后续画直方图

# 添加相关信息
with col1:
    # 直方图
    st.markdown('直方图')
    
    weathers_bar = px.bar(
        weather_dataframe,
        x = "天数", 
        y = weather_dataframe.index,
        orientation= 'h',# 水平条形图
        color_discrete_sequence=["#0083B8"] * len(weather_dataframe),
        template="plotly_white"
    )
    weathers_bar.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=False))# 隐去网格等
    )

    st.plotly_chart(weathers_bar, use_container_width=True) # Plot

with col2:
    # 饼图
    st.markdown('饼图')
    
    index = weather_dataframe.index.tolist()
    data = weather_dataframe['天数'].tolist()

    fig = px.pie(weather_dataframe, values = data, names = index)
    
    st.plotly_chart(fig)


# 好看的气球动画
st.balloons()

# 分隔符
st.markdown("""---""")

# 展示全部天气数据
st.markdown('##### 全部数据')
st.write(df)

# 分隔符
st.markdown("""---""")

# 图片模块
st.markdown('##### 城市图片')

@st.cache
def get_pictures(picture):
    picture_file = open(f'cityPictures/{picture}.jpg', 'rb')
    p = picture_file.read()
    picture_file.close()
    return p

pic1, pic2, pic3, pic4 = st.columns(4)

with pic1:
    st.markdown('##### 北京')
    picture1 = get_pictures('北京')
    st.image(picture1, caption='故宫')

with pic2:
    st.markdown('##### 福州')
    picture2 = get_pictures('福州')
    st.image(picture2, caption='三坊七巷')

with pic3:
    st.markdown('##### 厦门')
    picture3 = get_pictures('厦门')
    st.image(picture3, caption='双子塔')
    
with pic4:
    st.markdown('##### 龙岩')
    picture4 = get_pictures('龙岩')
    st.image(picture4, caption='龙岩站')

    
# 分隔符
st.markdown("""---""")  

# 视频模块
st.markdown('##### 一些视频')

@st.cache
def get_video_bytes(video):
    video_file = open(f'weather-video/{video}.mp4', 'rb')
    video_bytes = video_file.read()
    video_file.close()
    return video_bytes

v1, v2 = st.columns(2)# 分两列

with v1:
    video1=get_video_bytes('福建特产')
    v1.video(video1, format='video/mp4')
    st.caption("福建特产")

with v2:  
    video2=get_video_bytes('洪涝来了怎么办')
    v2.video(video2, format='video/mp4')
    st.caption("如何在洪涝中逃生")
    
    
# 隐藏streamlit默认格式信息
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
    
    
    
st.write('数据来源：天气网 https://www.tianqi.com/')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    