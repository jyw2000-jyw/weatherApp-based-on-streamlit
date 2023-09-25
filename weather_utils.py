import datetime
import pypinyin
import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
# pd.set_option('max_rows', None)  # 显示最多行数
# pd.set_option('max_columns', None)  # 显示最多列数
pd.set_option('display.unicode.east_asian_width', False)  # 设置输出右对齐


# 获取当前时间
def get_time():
    now_time = datetime.datetime.now()
    now_year = now_time.strftime('%Y')
    now_month = now_time.strftime('%m')
    ymd = now_time.strftime('%Y-%m-%d')
    return now_year, now_month, ymd


# 汉字转拼音
def pinyin(word):
    pinyin = ''
    for i in pypinyin.pinyin(word, style=pypinyin.NORMAL):
        pinyin += ''.join(i)
    return pinyin


# 爬虫
def get_weather(cities):
    print("Weather data scraping started...")

    now_year, now_month, _ = get_time()
    month_list = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    urls = []

    for city in cities:
        city_pinyin = pinyin(city)
        for month in month_list:
            if month <= now_month:
                url = 'http://lishi.tianqi.com/' + city_pinyin + '/' + now_year + month + '.html'
                urls.append((city, url))

    with open('st_weather.csv', 'w', encoding='utf-8', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['City', 'Date', 'Max Temperature', 'Min Temperature', 'Weather', 'Wind'])

        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'}

        for city, url in urls:
            try:
                response = requests.get(url, headers=header)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, 'html.parser')
                weather_list = soup.select('div[class="tian_three"]')

                for weather in weather_list:
                    ul_list = weather.select('li')
                    for ul in ul_list:
                        li_list = ul.select('div')
                        row_data = [city]
                        for li in li_list:
                            if li.string is None:
                                row_data.append('无数据')
                            else:
                                row_data.append(li.string)
                        if row_data:
                            csv_writer.writerow(row_data)

            except requests.exceptions.RequestException as e:
                print(f"Error fetching data from {url}: {e}")

    print("Weather data scraping completed! Saved to st_weather.csv")


# 读取csv
def get_data_from_excel(csv_name):
    df = pd.read_csv(csv_name)
    print(df)
    # return df


# csv预处理
def preprocess_csv():
    df = pd.read_csv("st_weather.csv")
    # 小小改下df格式
    df['Date'] = df['Date'].str[:-5]
    df['Date'] = pd.to_datetime(df['Date'])  # 转换日期格式为datetime
    df['Month'] = df['Date'].dt.month  # add Month col
    df['Max Temperature'] = pd.to_numeric(df['Max Temperature'].str[:-1]).astype(int)  # 字符串切割与转换为int类型
    df['Min Temperature'] = pd.to_numeric(df['Min Temperature'].str[:-1]).astype(int)

    # Save the modified DataFrame to a new CSV file
    df.to_csv("st_weather_modified.csv", index=False)
    return df


# 最高温最低温计算
def cal_temp(df_selection):
    # 最高温，最低温，平均高/低温
    max_temperature = df_selection['Max Temperature'].max()
    min_temperature = df_selection['Min Temperature'].min()
    average_hightemperature = round(df_selection['Max Temperature'].mean(), 1)
    average_lowtemperature = round(df_selection['Min Temperature'].mean(), 1)
    return max_temperature, min_temperature, average_hightemperature, average_lowtemperature


# 读取图片
def get_pictures(picture):
    picture_file = open(f'cityPictures/{picture}.jpg', 'rb')
    p = picture_file.read()
    picture_file.close()
    return p


# 读取视频
def get_video_bytes(video):
    video_file = open(f'weather_video/{video}.mp4', 'rb')
    video_bytes = video_file.read()
    video_file.close()
    return video_bytes


# 读取音频
def get_audio_bytes(music):
    audio_file = open(f'weather_music/{music}.mp3', 'rb')
    audio_bytes = audio_file.read()
    audio_file.close()
    return audio_bytes


if __name__ == "__main__":
    cities = ['北京', '福州', '厦门', '上海']
    get_weather(cities)
    preprocess_csv()
    # csv_name = 'st_weather.csv'
    # get_data_from_excel(csv_name)