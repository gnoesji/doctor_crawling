#연세대학교 의대강남/용인/서울 세브란스병원

from selenium import webdriver
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
import time
import pymysql

def doctor(connect, cursor, table_name, driver_path):

    svheartUrl='https://sev.severance.healthcare/sev-heart/department/department.do'
    svUrl='https://sev.severance.healthcare/sev/department/department.do'
    svgnUrl='https://gs.severance.healthcare/gs/department/department.do'
    svyiUrl='https://yi.severance.healthcare/yi/department/department.do'
    svUrls=[svheartUrl,svUrl,svgnUrl,svyiUrl]
    department = ['순환기내과', '심장내과', '심장외과', '흉부외과', '심장혈관외과', '소아심장과','심장마취통증의학과','심장영상의학과']

    wd=webdriver.Chrome(executable_path=driver_path)
    docs=[]
    for a in svUrls:
        departmentLink = []
        doctorLink = []
        wd.get(a)
        time.sleep(2)
        options = wd.find_elements_by_class_name('card')
        count = 0
        size = len(options)
        while count < size:
            count += 1
            if any(this in options[count - 1].text for this in department):
                options[count - 1].send_keys(Keys.ENTER)
                departmentLink.append(wd.current_url)
                wd.find_element_by_xpath('//*[@id="cms-content"]/div[1]/div/div/a[2]').send_keys(Keys.ENTER)
                time.sleep(1)
                options = wd.find_elements_by_class_name('card')

        for i in departmentLink:
            wd.get(i)
            time.sleep(1)
            options = wd.find_elements_by_class_name('doctor-card-box')
            count = 0
            size = len(options)
            origin = wd.current_url
            while count < size:
                options[count].click()
                i = options[count].find_element_by_class_name('flip-btns').find_element_by_tag_name('a')
                i.click()
                wd.switch_to.window(wd.window_handles[1])
                doctorLink.append(wd.current_url)
                wd.close()
                wd.switch_to.window(wd.window_handles[0])
                count += 1

        for i in doctorLink:
            doc=[]
            wd.get(i)
            time.sleep(1)
            education=[]
            career=[]
            link=wd.current_url
            html=wd.page_source
            soup=BeautifulSoup(html,'html.parser')
            # 이름
            try:
                name= soup.find('strong',{'class','name nm'}).text
            except:
                continue
            doc.append(name)
            # 소속
            if 'gs' in a:
                belong='연세대학교강남세브란스병원'
                hospital_code = '135710'
            elif 'yi' in a:
                belong='연세대학교용인세브란스병원'
                hospital_code = '449830'
            elif 'heart' in a:
                belong = '연세대학교세브란스심장혈관병원'
                hospital_code = '120710'
            else:
                belong='연세대학교세브란스병원'
                hospital_code = '120710'
            
            doc.append(belong)
            # 진료과
            dpt = wd.find_element_by_css_selector('#content-doctor > div > div.profile-overview > h2 > span').text
            if dpt=='':
                dpt=None
            doc.append(dpt)
            # 진료분야
            major= soup.find('p',{'class','medical-subject'}).text
            if major=='':
                major=None
            doc.append(major)
            # 경력
            try:
                ul=soup.find('ul',{'class','list list1 acdmcrMatter'})
                lis= ul.find_all('li')
                i=0
                for li in lis:
                    i+=1
                    text=li.text
                    if i!=len(lis):
                        text=text[0:len(text)-1]
                    education.append(text)
                education=','.join(education)
            except:
                education=None
            doc.append(education)
            # 학력
            try:
                ul=soup.find('ul',{'class','list list1 edcNdClincCareer'})
                lis= ul.find_all('li')
                i=0
                for li in lis:
                    i+=1
                    text=li.text
                    if i!=len(lis):
                        text=text[0:len(text)-1]
                    career.append(text)
                career=','.join(career)
            except:
                career=None
            doc.append(career)
            doc.append(link)
            doc.append(hospital_code)

            print(name)
            print(belong)
            print(dpt)
            print(major)
            print(education)
            print(career)

            docs.append(doc)
    wd.close()

    for i in docs:
        cursor.execute(
            "INSERT INTO " + table_name + "(name_kor, belong, department, major, education, career, link, hospital_code) values (%s, %s, %s, %s, %s, %s, %s, %s);",
            (i[0],i[1],i[2],i[3],i[4],i[5],i[6],i[7]))
        connect.commit()
