#카톨릭대학교 인천성모병원
#심장혈관내과 : https://www.cmcism.or.kr/treatment/treatment_team?deptSeq=36
#흉부외과 : https://www.cmcism.or.kr/treatment/treatment_team?deptSeq=50

from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import pymysql
from selenium import webdriver

def doctor(conn, cursor, new_table, driver_path):

    main_url = 'https://www.cmcism.or.kr/treatment/treatment_team?deptSeq='
    depart_list = ['36', '50']
    wd = webdriver.Chrome(executable_path=driver_path)

    doctor_list = []
    major_list = []
    education_list = []
    career_list = []
    link_list = []
    hospital_code = "403010"

    for depart in depart_list:
        try:
            wd.implicitly_wait(10)
            wd.get(main_url + depart)

            click_page = '#right > div.sub_wrap > div.Team_write > div > div'
            doc_list = wd.find_elements_by_css_selector(click_page)
            doc_num = len(doc_list)

            for doctor in doc_list:
                try:
                    id_name = doctor.find_element_by_css_selector('a').get_attribute("id") ##btn_open_31
                    id_name = id_name.split("_")
                    id_num = id_name[2] ## 31

                    
                    #wd.implicitly_wait(10)
                    doctor.find_element_by_css_selector('a').send_keys(Keys.ENTER)
                    time.sleep(2)


                    #이름
                    temp_name = wd.find_element_by_css_selector(
                        '#tab%s_1 > div > div.text_box > div > ul > li.li_h > span'%(id_num)
                    ).text
                    temp_name = temp_name[:-2]

                    #진료분야
                    temp_major = []
                    temp_major.append(wd.find_element_by_css_selector(
                        '#tab%s_1 > div > div.text_box > div > table > tbody > tr:nth-child(2) > td'%(id_num)
                    ).text)

                    #경력/학력 페이지 클릭
                    #wd.implicitly_wait(10)

                    wd.find_element_by_css_selector(
                        '#layer_pop_%s > div > ul > li:nth-child(2)'%(id_num)
                    )
                    wd.switch_to(wd.window_handles[1])
                    time.sleep(2)

                    #경력
                    temp_career = []
                    data_list = wd.find_elements_by_css_selector(
                        '#tab%s_2 > dl:nth-child(1) > dd'%(id_num)
                    )

                    for career in data_list:
                        temp_career.append(career.text)

                    #학력
                    temp_edu = []
                    edu_list = wd.find_elements_by_css_selector(
                        '#tab%s_2 > dl:nth-child(2) > dd'%(id_num)
                    )

                    for edu in edu_list:
                        temp_edu.append(edu.text)
                    #print(temp_edu)

                    temp_link = wd.current_url

                    #데이터 저장
                    doctor_list.append(temp_name)
                    major_list.append(temp_major)
                    education_list.append(temp_edu)
                    career_list.append(temp_career)
                    link_list.append(temp_link)

                    #팝업창 닫기 => 의료진 페이지 닫기
                    wd.find_element_by_css_selector('#btn_close_'+id_num).send_keys(Keys.ENTER)

                except Exception as e1:
                    print("의료진 페이지 오류 : ", e1)

        except Exception as e1:
            print("전체 페이지 오류 : ", e1)

    for i in range(len(doctor_list)):
        try:
            major = major_list[i]
            
            if not education_list[i]:
                education = None
            else:
                education = ', '.join(education_list[i])

            if not career_list[i]:
                career = None
            else:
                career = ', '.join(career_list[i])

            #의료진 DB 추가
            sql = """INSERT INTO """+new_table+"""(name_kor, belong, major, education, career, link, hospital_code)
            VALUES(%s, %s, %s, %s, %s, %s, %s)
            """%(doctor_list[i], "카톨릭대학교인천성모병원", major, education, career, link_list[i], hospital_code)

            cursor.execute(sql)
            conn.commit()

        except Exception as e1:
            print("DB 저장 오류 : ", e1)
            conn.close()

            wd.close()
            wd.quit()
            import sys
            sys.exit()

    wd.close()
    wd.quit()
