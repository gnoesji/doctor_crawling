#양산부산대하교병원 심혈관센터 : http://cc.pnuyh.or.kr/TCF/cb/treat/docList.do?menuIdx=12&id=1
#부산대학교어린이병원 소아심장센터 : http://ptsphc.pnuyh.or.kr/TCF/cb/treat/docList.do?menuIdx=12&id=56

from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import pymysql

def doctor(conn, cursor, new_table, driver_path):

    driver = wd.Chrome(executable_path=driver_path)
    page_list = ['http://cc.pnuyh.or.kr/TCF/cb/treat/docList.do?menuIdx=12&id=1',
                 'http://ptsphc.pnuyh.or.kr/TCF/cb/treat/docList.do?menuIdx=12&id=56']

    doctor_list = []
    dpt_list = []
    major_list = []
    edu_list = []
    career_list = []
    link_list = []
    belong_list = []
    hospital_code = "626610"

    for idx, page in enumerate(page_list):
        try:
            driver.implicitly_wait(10)
            driver.get(page)

            tbListA = driver.find_elements_by_css_selector(
                '#tabcontent0 > table > tbody > tr'
            )
            tbListA_len = len(tbListA)

            for col in range(1, tbListA_len+1):
                try:
                    #의료진 페이지 들어가기
                    driver.implicitly_wait(10)
                    driver.find_element_by_css_selector(
                        "#tabcontent0 > table > tbody > tr:nth-child(%s) > td.name > a"%(col)
                    ).send_keys(Keys.ENTER)

                    #이름
                    temp_name = driver.find_element_by_css_selector(
                        "#contents_ws > div.psnlTitle > h4").text
                    #print(temp_name)

                    #진료과
                    temp_dpt = []
                    temp_dpt.append(driver.find_element_by_css_selector('#contents_ws > div.profileWrap > div.profile > p:nth-child(4)').text.split(' ')[1])

                    #진료분야
                    temp_major = []
                    temp_major.append(driver.find_element_by_css_selector(
                        "#contents_ws > div.profileWrap > div.profile > p:nth-child(6)"
                    ).text)

                    #학력
                    education_text = driver.find_element_by_xpath(
                        "//*[@id='contents_ws']/div[4]/div[2]/ul[2]/li"
                    ).text.strip('\n')
                    education_list = [data for data in education_text.split("\n")]
                    temp_edu = []

                    for edu in education_list:
                        if edu == '':
                            continue
                        temp_edu.append(edu)
                    #print(temp_edu)

                    #경력
                    career_text = driver.find_element_by_xpath(
                        "//*[@id='contents_ws']/div[4]/div[2]/ul[3]/li"
                    ).text.strip('\n')
                    data_list = [data for data in career_text.split("\n")]
                    temp_career = []

                    for career in data_list:
                        if career == '':
                            continue
                        temp_career.append(career)
                    #print(temp_career)

                    if idx == 0:
                        temp_belong = "양산부산대학교병원"
                    else:
                        temp_belong = "부산대학교어린이병원"

                    temp_link = driver.current_url

                    #의료진 페이지 나가기
                    driver.back()

                    #데이터 저장
                    doctor_list.append(temp_name)
                    belong_list.append(temp_belong)
                    dpt_list.append(temp_dpt)
                    major_list.append(temp_major)
                    edu_list.append(temp_edu)
                    career_list.append(temp_career)
                    link_list.append(temp_link)

                except Exception as e1:
                    print( '의료진 페이지 검색 오류', e1 )

        except Exception as e1:
            print( '전체 페이지 검색 오류', e1 )            

    #DB 저장
    for i in range(len(doctor_list)): 
        try:
            if major_list[i] == '':
                major = None
            else:
                major = ', '.join(major_list[i])

            if dpt_list[i] == '':
                dpt = None
            else:
                dpt = ', '.join(dpt_list[i])

            if not edu_list[i]:
                education = None
            else:
                education = ', '.join(edu_list[i])

            if not career_list[i]:
                career = None
            else:
                career = ', '.join(career_list[i])

            #의료진 DB 추가
            cursor.execute(
                "INSERT INTO " + new_table + "(name_kor, belong, department, major, education, career, link, hospital_code) values (%s, %s, %s, %s, %s, %s, %s, %s);",
                (doctor_list[i], belong_list[i], dpt, major, education, career, link_list[i], hospital_code))
            conn.commit()

        except Exception as e1:
            print("DB 저장 오류 : ", e1)
            conn.close()        

            driver.close()
            driver.quit()
            import sys
            sys.exit()        

    driver.close()
    driver.quit()




