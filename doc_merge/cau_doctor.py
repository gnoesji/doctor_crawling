### import ###
from selenium import webdriver
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
import time
import requests
import re
import pymysql
def doctor(connect, cursor, table_name, driver_path):

    ### 크롬드라이버 생성 ###
    wd=webdriver.Chrome(executable_path=driver_path)

    ### 크롤링 코드 시작 ###
    department=['순환기내과','흉부외과']
    #department = ['순환기내과', '심장내과', '심장외과', '흉부외과', '심장혈관외과', '소아심장과']
    url="https://ch.cauhs.or.kr/medical/medical.asp?cat_no=02010000"
    wd.get(url)

    #진료과 링크
    departmentLink=[]
    doctor_click=[]
    doctorLink=[]
    
    ###한번에 커밋하기 위한 작업###
    name_kor=[]
    belong=[]
    dpt=[]
    major=[]
    education=[]
    career=[]
    link=[]
    data=[]
    time.sleep(1)

    k=0
    j=0
    s=0

    #진료과 링크담기
    data.append(wd.find_element_by_xpath('/html/body/div/div[4]/div[2]/div[3]/div/div[1]/ul/li[14]/a'))
    data.append(wd.find_element_by_xpath('/html/body/div/div[4]/div[2]/div[3]/div/div[1]/ul/li[36]/a'))


    
    for a in data:
        departmentLink.append(a.get_attribute("href"))
    #print(departmentLink)
    for i in departmentLink:
        wd.get(i)
        time.sleep(1)
        buttons=wd.find_elements_by_xpath('//*[@id="content"]/div/div/div[3]/ul/li/div[1]/a')
        
        #print(len(buttons))
        for m in buttons:
        
            m.click()
            wd.switch_to_window(wd.window_handles[1])
            time.sleep(2)
            
            ### name_kor 수집 ###
            name_kor.append(wd.find_element_by_css_selector('body > div > div.doc_content_wrap > div > div.doctor_txt > div.tit_area.fix > p.doctor_name'))
            name_kor[k]=name_kor[k].text
            #print(name_kor[k])
            ### dpt 수집 ###
            dpt.append(wd.find_element_by_css_selector('body > div > div.doc_content_wrap > div > div.doctor_txt > div.tit_area.fix > p.doctor_part'))
            dpt[k] = dpt[k].text
            ### major 수집 ###
            major.append(wd.find_element_by_css_selector('body > div > div.doc_content_wrap > div > div.doctor_txt > p.doctor_explain'))
            major[k]=major[k].text
            #print(major[k])
            k=k+1
            ###belong수집: notion_대학병원이름에서 병원 명칭(홈페이지)이름으로 저장 ###
            belong="중앙대학교병원"
            ###hospital_code수집: notion_대학병원이름에서 병원코드 저장 ###
            hospital_code ="100210"
            ### 학력 수집 ###
            try:
                education.append(wd.find_element_by_css_selector('body > div > div.doc_content_wrap > ul.tab_con > li.tab_con1 > div > ul:nth-child(4)'))
                education[j]=education[j].text.replace('\n','/')
                #print(education[j])
            except:
                education[j]=[]
        
            ### 경력 수집 ###
            try:
                career.append(wd.find_element_by_css_selector('body > div > div.doc_content_wrap > ul.tab_con > li.tab_con1 > div > ul:nth-child(6)'))
                career[j]=career[j].text.replace('\n','/')
                #print(career[j])
            except:
                career[j]=[]
            #print(wd.current_url)
            ###link수집###
            try:
                link.append(wd.current_url)
                #print(link[j])
            except:
                link=[]
            j=j+1
            time.sleep(2)   
            wd.close()
            wd.switch_to_window(wd.window_handles[-1])
    
    #print(len(name_kor))
    #print(len(major))
    #print(len(education))
    #print(len(career))
    wd.close()


    for i in range(len(name_kor)):
        cursor.execute("insert into "+table_name+"(name_kor, belong,department, major,education,career,link,hospital_code) values(%s, %s,%s,%s,%s,%s,%s,%s);",(name_kor[i],belong, dpt[i], major[i],education[i],career[i],link[i],hospital_code))
    connect.commit()

    #connect.close()
    wd.quit()




