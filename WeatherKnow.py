"""
-------------------------------------------------
Project Name: WeatherKnow
File Name: weather.py
Author: YUWEI JIANG
Create Date: 2023/9/24
Description：ui for weather monitor system
-------------------------------------------------
"""

import random
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import streamlit as st
from weather_utils import *

# 解决中文显示问题
plt.rcParams['font.sans-serif'] = ['KaiTi']  # 指定默认字体
plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题

if __name__ == '__main__':
    # 设置网页
    st.set_page_config(page_title="WeatherKnow",
                       page_icon=" :sunny: ",
                       layout="wide")

    # 主页面
    st.title("WeatherKnow :sunny:")
    st.write("This is a weather data monitor system developed by **JYW**")
    st.markdown("###")

    # 读取爬取的csv文件
    df = preprocess_csv()

    # 获取时间
    now_year, now_month, ymd = get_time()

    # 侧边栏
    st.sidebar.header(f"Current Date: {ymd}")

    # 在侧边栏中创建一个输入框
    with st.sidebar:
        user_input = st.text_input("Please input the city name（待开发）:")

    st.sidebar.text('(请输入城市的中文，不用添加“市”，如：成都)')
    st.sidebar.markdown('---')  # 分割线

    # bgm曲目功能
    music = st.sidebar.radio('Choose a music',
                             ['卡农', 'Summer'],
                             index=random.choice(range(2)))
    st.sidebar.write(f'Loading {music}... :musical_note:')

    audio_bytes = get_audio_bytes(music)
    st.sidebar.audio(audio_bytes, format='audio/mp3')

    st.sidebar.markdown('---')  # 分割线

    # 选择城市
    city = st.sidebar.selectbox("Current City:",
                                options=df["City"].unique())

    mode = st.sidebar.selectbox("Current Mode:",
                                ("Weather History", "Weather Forecast(待开发)"))

    time = st.sidebar.multiselect("Current Month:",
                                  options=df["Month"].unique(),
                                  default=df["Month"].unique())

    df_selection = df.query("Month == @time & City == @city")  # query中含有变量！是之前的三个侧边框

    # 在主界面中显示用户输入的文本city
    st.write(f"您查询的城市为：{city}，其天气信息如下:")

    # 温度数据
    max_temperature, min_temperature, average_hightemperature, average_lowtemperature = cal_temp(df_selection)

    col1, col2, col3, col4 = st.columns(4)
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
    st.markdown(f'##### Temperature Cruve(截至{now_year}年{now_month}月)')

    fig1 = px.line(df_selection, x = df_selection['Date'], y = df_selection['Max Temperature'], color_discrete_sequence=['red'])
    fig2 = px.line(df_selection, x = df_selection['Date'], y = df_selection['Min Temperature'], color_discrete_sequence=['blue'])

    layout = go.Layout(
        xaxis={'title': 'Time'},
        yaxis={'title': 'Temperature/℃'})

    fig = go.Figure(data=fig1.data + fig2.data, layout=layout)
    st.plotly_chart(fig, use_container_width=True)

    # 分隔符
    st.markdown("""---""")
    st.markdown(f'##### Weather Statistics(截至{now_year}年{now_month}月)')

    # 筛选天气类型并统计
    weather_dataframe = df_selection.groupby(["Weather"]).count()[['Date']].sort_values(by="Date",ascending = True).rename(columns={'Date':'天数'}) # 此处要设置True从小到大排序，为了方便后续画直方图

    col1, col2 = st.columns(2)
    with col1:
        # 直方图
        st.markdown('Bar Chart')

        weathers_bar = px.bar(
            weather_dataframe,
            x="天数",
            y=weather_dataframe.index,
            orientation='h',  # 水平条形图
            color_discrete_sequence=["#0083B8"] * len(weather_dataframe),
            template="plotly_white"
        )
        weathers_bar.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=(dict(showgrid=False))  # 隐去网格等
        )

        st.plotly_chart(weathers_bar, use_container_width=True)  # Plot

    with col2:
        # 饼图
        st.markdown('Pie Chart')

        index = weather_dataframe.index.tolist()
        data = weather_dataframe['天数'].tolist()

        fig = px.pie(weather_dataframe, values=data, names=index)

        st.plotly_chart(fig)

    # 气球动画
    st.balloons()

    # 分隔符
    st.markdown("""---""")

    # 展示全部天气数据
    st.markdown('##### All data')
    st.write(df)

    # 分隔符
    st.markdown("""---""")

    # 图片模块
    st.markdown('##### Cities Images')

    pic1, pic2, pic3, pic4 = st.columns(4)
    with pic1:
        st.markdown('##### Beijing')
        picture1 = get_pictures('beijing')
        st.image(picture1, caption='故宫')

    with pic2:
        st.markdown('##### Fuzhou')
        picture2 = get_pictures('fuzhou')
        st.image(picture2, caption='三坊七巷')

    with pic3:
        st.markdown('##### Xiamen')
        picture3 = get_pictures('xiamen')
        st.image(picture3, caption='双子塔')

    with pic4:
        st.markdown('##### Shanghai')
        picture4 = get_pictures('shanghai')
        st.image(picture4, caption='陆家嘴')

    # 分隔符
    st.markdown("""---""")

    # 视频模块
    st.markdown('##### 科普视频')

    v1, v2 = st.columns(2)  # 分两列

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
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
