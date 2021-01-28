# 爬蟲參考資料:
#https://www.royenotes.com/python-104-employment-agency/
#https://tlyu0419.github.io/2019/04/18/Crawl-JobList104/
#https://tlyu0419.github.io/2020/06/19/Crawler-104HumanResource/


import requests
import bs4
import time
import streamlit as st
import base64
from pandas import DataFrame
from PIL import Image

columns_name = ['職缺名稱', '公司名稱', '地址', '薪資', '網址', '工作內容']    # 欄的名稱

@st.cache(allow_output_mutation=True)
def find_job(url_original, search_input, search_condition, search_order, job_number):   # search_condition為list, search_order為string
    search_inputs = "%20".join(search_input.split())    # keyword要用%20串起來   # keyword等於使用者鍵入之關鍵字
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
        if len(search_inputs):
            url = f"{url_original}&keyword={search_inputs}&page={page}&{last_url}"
        else:
            url = f"{url_original}&page={page}&{last_url}"
        #print(url)

        htmlFile = requests.get(url)
        ObjSoup = bs4.BeautifulSoup(htmlFile.text, 'lxml')
        jobs = ObjSoup.find_all('article', class_='js-job-item')  # 搜尋所有職缺

        for job in jobs:
            job_name = job.find('a', class_="js-job-link").text  # 職缺名稱
            job_company = job.get('data-cust-name')  # 公司名稱

            job_loc = job.find('ul', class_='job-list-intro').find('li').text  # 地址
            job_pay = job.find('span', class_='b-tag--default').text  # 薪資
            job_url = "https:"+job.find('a').get('href')  # 網址
            JOB = f"<a href={job_url}>{job_url}</a>"

            try:         # 有些職位會沒有"工作內容"這一項，當爬蟲爬不到時，會產生錯誤 (如'NoneType' object has no attribute 'text')
                job_content = job.find('p', class_="job-list-item__info").text  # 工作內容
            except Exception as e:
                print(e, "error")
                print(job_url)
                continue

            # print(job_url.split("?")[-1].split("=")[-1])    # 去除並非為廣告的工作，而是完全符合搜尋關鍵字的工作
            if job_url.split("?")[-1].split("=")[-1] == "hotjob_chr":  # 若為廣告的職缺，不予紀錄 (去除打廣告的布相關職位)
                continue

            job_data = {'職缺名稱': job_name, '公司名稱': job_company,
                        '地址': job_loc, '薪資': job_pay, '網址': JOB, '工作內容': job_content}
            all_job_datas.append(job_data)
        time.sleep(0.25)
    return all_job_datas


# !!!如何從streamlit app上，下載檔案: https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806/43
# https://github.com/MarcSkovMadsen/awesome-streamlit
def filedownload(df):
    csv = df.to_csv(index=False, encoding="utf_8_sig")
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="find_jobs.csv">Download CSV File</a>'
    return href

url_not_complete = 'https://www.104.com.tw/jobs/search/?ro=0&mode=s&jobsource=2020indexpoc'


icon = Image.open('./img/job.png')
st.set_page_config(page_title='Humming 104JobFinder.io',page_icon=icon)    #set_page_config() can only be called once per app, and must be called as the first Streamlit command in your script.
st.title('老司機找工作 v1.01')
my_profile = Image.open('./img/business_card.jpg')

placeholder = st.image(my_profile, use_column_width=True)

st.sidebar.header('Searching bar')
search_input = st.sidebar.text_input("關鍵字(例: 工作職稱、公司名、技能專長...)")

search_condition = st.sidebar.multiselect('條件', ['暑假工讀', '短期工讀', '實習工作'], [])
# print(selected_condition)  # 每當多選擇一個條件時，就會增加搜尋的條件

search_order = st.sidebar.selectbox('排序依', ['符合度排序', '日期排序', '學歷 高->低', '學歷 低->高', '經歷 多->少', '經歷 少->多', '應徵人數 多->少', '應徵人數 少->多', '待遇 高->低', '待遇 低->高'])

search_number = st.sidebar.number_input('工作數', step=20, min_value=20)
job_number = int((search_number)/20)    # 需要爬的頁數(每頁有20個工作)

col1, col2, col3 = st.sidebar.beta_columns([1, 1, 1])
job_datas = []

if col2.button('搜尋'):
    placeholder.empty()
    job_datas = list(find_job(url_not_complete, search_input, search_condition, search_order, job_number))

    if len(job_datas) == 0:
        st.balloons()
        # 分欄顯示
        #col1, col2 = st.beta_columns([2, 3])
        #col2.warning("呃拍謝，搜尋結果好像很少~~")
        image = Image.open('./img/sorry.jpg')
        st.image(image, caption="", use_column_width=True)
    else:
        fn = f'104人力銀行職缺內容共{job_number}頁.csv'  # 取CSV檔名
        #st.table(job_datas)
        df = DataFrame(job_datas, columns=columns_name)
        df_selected = df.loc[:, ['職缺名稱', '公司名稱', '地址', '薪資']]  # 只取某幾列顯示 https://blog.csdn.net/aaa_aaa1sdf/article/details/77414387
        df_shown = df_selected.style.set_properties(**{'text-align': 'left'}).\
            set_table_styles([dict(selector='th', props=[('text-align', 'left')])])    # 靠左顯示(left alignment)

        del job_datas[:]
        df.to_csv(fn, index=False, encoding="utf_8_sig")

        st.dataframe(df_shown, 1200, 400)
        st.markdown(f'*Data Dimension:  {df_selected.shape[0]} rows and {df_selected.shape[1]} columns.*')
        st.markdown(filedownload(df), unsafe_allow_html=True)
else:
    pass




