#https://www.royenotes.com/python-104-employment-agency/
#https://tlyu0419.github.io/2019/04/18/Crawl-JobList104/
#https://tlyu0419.github.io/2020/06/19/Crawler-104HumanResource/

"""
import pandas as pd
import re, time, requests
from selenium import webdriver
from bs4 import BeautifulSoup

# 加入使用者資訊(如使用什麼瀏覽器、作業系統...等資訊)模擬真實瀏覽網頁的情況
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'}



# 查詢的關鍵字
my_params = {'ro': '1',  # 限定全職的工作，如果不限定則輸入0
             'keyword': '資料科學',  # 想要查詢的關鍵字
             'area': '6001001000',  # 限定在台北的工作
             'isnew': '30',  # 只要最近一個月有更新的過的職缺
             'mode': 'l'}  # 清單的瀏覽模式

url = requests.get('https://www.104.com.tw/jobs/search/?', my_params, headers=headers).url
driver = webdriver.Chrome(executable_path = 'C:/Program Files (x86)/chromedriver_win32/chromedriver.exe')
driver.get(url)

# 網頁的設計方式是滑動到下方時，會自動加載新資料，在這裡透過程式送出Java語法幫我們執行「滑到下方」的動作
for i in range(20):
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    time.sleep(0.6)

# 自動加載只會加載15次，超過之後必須要點選「手動載入」的按鈕才會繼續載入新資料（可能是防止爬蟲）
k = 1
while k != 0:
    try:
        # 手動載入新資料之後會出現新的more page，舊的就無法再使用，所以要使用最後一個物件
        driver.find_elements_by_class_name("js-more-page", )[-1].click()
        # 如果真的找不到，也可以直接找中文!
        # driver.find_element_by_xpath("//*[contains(text(),'手動載入')]").click()
        print('Click 手動載入，' + '載入第' + str(15 + k) + '頁')
        k = k + 1
        time.sleep(1)  # 時間設定太短的話，來不及載入新資料就會跳錯誤
    except:
        k = 0
        print('No more Job')

# 透過BeautifulSoup解析資料
soup = BeautifulSoup(driver.page_source, 'html.parser')
List = soup.findAll('a', {'class': 'js-job-link'})
print('共有 ' + str(len(List)) + ' 筆資料')


def bind(cate):
    k = []
    for i in cate:
        if len(i.text) > 0:
            k.append(i.text)
    return str(k)


JobList = pd.DataFrame()

i = 0
while i < len(List):
    # print('正在處理第' + str(i) + '筆，共 ' + str(len(List)) + ' 筆資料')
    content = List[i]
    # 這裡用Try的原因是，有時候爬太快會遭到系統阻擋導致失敗。因此透過這個方式，當我們遇到錯誤時，會重新再爬一次資料！
    try:
        resp = requests.get('https://' + content.attrs['href'].strip('//'))
        soup2 = BeautifulSoup(resp.text, 'html.parser')
        df = pd.DataFrame(
            data=[{
                '公司名稱': soup2.find('a', {'class': 'cn'}).text,
                '工作職稱': content.attrs['title'],
                '工作內容': soup2.find('p').text,
                '職務類別': bind(soup2.findAll('dd', {'class': 'cate'})[0].findAll('span')),
                '工作待遇': soup2.find('dd', {'class': 'salary'}).text.split('\n\n', 2)[0].replace(' ', ''),
                '工作性質': soup2.select('div > dl > dd')[2].text,
                '上班地點': soup2.select('div > dl > dd')[3].text.split('\n\n', 2)[0].split('\n', 2)[1].replace(' ', ''),
                '管理責任': soup2.select('div > dl > dd')[4].text,
                '出差外派': soup2.select('div > dl > dd')[5].text,
                '上班時段': soup2.select('div > dl > dd')[6].text,
                '休假制度': soup2.select('div > dl > dd')[7].text,
                '可上班日': soup2.select('div > dl > dd')[8].text,
                '需求人數': soup2.select('div > dl > dd')[9].text,
                '接受身份': soup2.select('div.content > dl > dd')[10].text,
                '學歷要求': soup2.select('div.content > dl > dd')[12].text,
                '工作經歷': soup2.select('div.content > dl > dd')[11].text,
                '語文條件': soup2.select('div.content > dl > dd')[14].text,
                '擅長工具': soup2.select('div.content > dl > dd')[15].text,
                '工作技能': soup2.select('div.content > dl > dd')[16].text,
                '其他條件': soup2.select('div.content > dl > dd')[17].text,
                '公司福利': soup2.select('div.content > p')[1].text,
                '科系要求': soup2.select('div.content > dl > dd')[13].text,
                '聯絡方式': soup2.select('div.content')[3].text.replace('\n', ''),
                '連結路徑': 'https://' + content.attrs['href'].strip('//')}],
            columns=['公司名稱', '工作職稱', '工作內容', '職務類別', '工作待遇', '工作性質', '上班地點', '管理責任', '出差外派',
                     '上班時段', '休假制度', '可上班日', '需求人數', '接受身份', '學歷要求', '工作經歷', '語文條件', '擅長工具',
                     '工作技能', '其他條件', '公司福利', '科系要求', '聯絡方式', '連結路徑'])
        JobList = JobList.append(df, ignore_index=True)
        i += 1
        print("Success and Crawl Next 目前正在爬第" + str(i) + "個職缺資訊")
        time.sleep(0.5)  # 執行完休息0.5秒，避免造成對方主機負擔
    except:
        print("Fail and Try Again!")

print(JobList)

JobList.to_excel('C:/Users/Kevinsky/Downloads/JobList2.xlsx', encoding='cp950')
"""
import requests
import bs4
import time
import streamlit as st
import pandas as pd
import base64
from pandas import DataFrame
from PIL import Image

@st.cache
def find_job(url_original, search_input, search_condition, search_order, job_number):   # search_condition為list, search_order為string
    search_inputs = "%20".join(search_input.split())    # keyword要用%20串起來
    more = []

    # 條件增加為多選多
    if '暑假工讀' in search_condition:
        more.append("wt=16")
    if '短期工讀' in search_condition:
        more.append("wt=2")
    if '實習工作' in search_condition:
        more.append("rostatus=1024")

    # 排序為多選一
    if search_order=='符合度排序':
        more.append("order=12")
    elif search_order=='日期排序':
        more.append("order=11")
    elif search_order=='學歷 高->低':
        more.append("order=4&asc=0")
    elif search_order=='學歷 低->高':
        more.append("order=4&asc=1")
    elif search_order=='經歷 多->少':
        more.append("order=3&asc=0")
    elif search_order=='經歷 少->多':
        more.append("order=3&asc=1")
    elif search_order=='應徵人數 多->少':
        more.append("order=7&asc=0")
    elif search_order=='應徵人數 少->多':
        more.append("order=7&asc=1")
    elif search_order=='待遇 高->低 ':
        more.append("order=13&asc=0")
    elif search_order=='待遇 低->高 ':
        more.append("order=13&asc=1")

    last_url = "&".join(more)

    all_job_datas = []
    for page in range(1, job_number + 1):     # 最多有150頁
        url = f"{url_original}&keyword={search_inputs}&page={page}&{last_url}"
        #print(url)

        htmlFile = requests.get(url)
        ObjSoup = bs4.BeautifulSoup(htmlFile.text, 'lxml')
        jobs = ObjSoup.find_all('article', class_='js-job-item')  # 搜尋所有職缺


        for job in jobs:
            #try:
            job_name = job.find('a', class_="js-job-link").text  # 職缺名稱
            job_company = job.get('data-cust-name')  # 公司名稱

            job_loc = job.find('ul', class_='job-list-intro').find('li').text  # 地址
            job_pay = job.find('span', class_='b-tag--default').text  # 薪資
            job_url = "https:"+job.find('a').get('href')  # 網址

            try:
                job_content = job.find('p', class_="job-list-item__info").text  # 工作內容
            except Exception as e:
                print(e)
                print(job_url)
                print("有問題")
                continue

            #except Exception as e:
                #print(e)
                #continue

            #print(job_url)
            #print("dfa")
            # print(job_url.split("?")[-1].split("=")[-1])    # 去除並非為廣告的工作，而是完全符合搜尋關鍵字的工作
            if job_url.split("?")[-1].split("=")[-1] == "hotjob_chr":  # 若為廣告的職缺，不予紀錄
                continue

            job_data = {'職缺名稱': job_name, '公司名稱': job_company,
                        '地址': job_loc, '薪資': job_pay, '網址': job_url, '工作內容': job_content}
            all_job_datas.append(job_data)
        time.sleep(0.5)

    fn = f'104人力銀行職缺內容共{job_number}頁.csv'  # 取CSV檔名
    columns_name = ['職缺名稱', '公司名稱', '地址', '薪資', '網址', '工作內容']  # 第一欄的名稱

    df = DataFrame(all_job_datas, columns=columns_name)
    df_selected = df.loc[:, ['職缺名稱', '公司名稱', '地址', '薪資']]     # 只取某幾列顯示 https://blog.csdn.net/aaa_aaa1sdf/article/details/77414387

    del all_job_datas[:]

    df.to_csv(fn, index=False, encoding="utf_8_sig")
    """
    #with open(fn, 'w', newline='', encoding="utf_8_sig") as csvFile:  # 定義CSV的寫入檔,並且每次寫入完會換下一行
        dictWriter = csv.DictWriter(csvFile, fieldnames=columns_name)  # 定義寫入器
        dictWriter.writeheader()
        for data in all_job_datas:
            dictWriter.writerow(data)
    """

    return df_selected, df


def filedownload(df):
    csv = df.to_csv(index=False, encoding="utf_8_sig")
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="find_jobs.csv">Download CSV File</a>'
    return href

url_not_complete = 'https://www.104.com.tw/jobs/search/?ro=0&mode=s&jobsource=2020indexpoc'   # keyword等於使用者鍵入之關鍵字

icon = Image.open('job.png')
st.set_page_config(page_title='104 Job Finder.io',page_icon=icon)    #set_page_config() can only be called once per app, and must be called as the first Streamlit command in your script.
st.title('老司機找工作')
my_profile = Image.open('business_card.jpg')
placeholder = st.image(my_profile, use_column_width=True)




st.sidebar.header('Searching bar')
search_input = st.sidebar.text_input("關鍵字(例: 工作職稱、公司名、技能專長...)")

search_condition = st.sidebar.multiselect('條件', ['暑假工讀', '短期工讀', '實習工作'], [])
# print(selected_condition)  # 每當多選擇一個條件時，就會增加搜尋的條件

search_order = st.sidebar.selectbox('排序依', ['符合度排序', '日期排序', '學歷 高->低', '學歷 低->高', '經歷 多->少', '經歷 少->多', '應徵人數 多->少', '應徵人數 少->多', '待遇 高->低', '待遇 低->高'])

search_number = st.sidebar.number_input('工作數', value=80, step=20, min_value=20)
job_number = int(int(search_number)/20)

col1, col2, col3 = st.sidebar.beta_columns([1, 1, 1])


if col2.button('搜尋'):
    placeholder.empty()
    df_shown, df_original = find_job(url_not_complete, search_input, search_condition, search_order, job_number)
    if len(df_shown) == 0:
        st.balloons()

        # 分欄顯示
        #col1, col2 = st.beta_columns([2, 3])
        #col2.warning("呃拍謝，搜尋結果好像很少~~")
        image = Image.open('sorry2.jpg')
        st.image(image, caption="", use_column_width=True)
    else:
        #st.subheader('符合工作:')
        st.dataframe(df_shown, 1200, 400)
        st.markdown(f'*Data Dimension:  {df_shown.shape[0]} rows and {df_shown.shape[1]} columns.*')
        st.markdown(filedownload(df_original), unsafe_allow_html=True)
else:
    pass





