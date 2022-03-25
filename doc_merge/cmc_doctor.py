#가톨릭대학교성모병원(서울/여의도/은평/의정부/부천/성빈센트)
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
import time
import pymysql
from selenium.common.exceptions import WebDriverException

def wheel_element(element, deltaY = 120, offsetX = 0, offsetY = 0):
  error = element._parent.execute_script("""
    var element = arguments[0];
    var deltaY = arguments[1];
    var box = element.getBoundingClientRect();
    var clientX = box.left + (arguments[2] || box.width / 2);
    var clientY = box.top + (arguments[3] || box.height / 2);
    var target = element.ownerDocument.elementFromPoint(clientX, clientY);

    for (var e = target; e; e = e.parentElement) {
      if (e === element) {
        target.dispatchEvent(new MouseEvent('mouseover', {view: window, bubbles: true, cancelable: true, clientX: clientX, clientY: clientY}));
        target.dispatchEvent(new MouseEvent('mousemove', {view: window, bubbles: true, cancelable: true, clientX: clientX, clientY: clientY}));
        target.dispatchEvent(new WheelEvent('wheel',     {view: window, bubbles: true, cancelable: true, clientX: clientX, clientY: clientY, deltaY: deltaY}));
        return;
      }
    }    
    return "Element is not interactable";
    """, element, deltaY, offsetX, offsetY)
  if error:
    raise WebDriverException(error)

def doctor(connect, cursor, table_name, driver_path):

    department = ['순환기내과', '심장내과', '심장외과', '흉부외과', '심장혈관외과', '소아심장과','순환기(심장)내과']
    wd=webdriver.Chrome(executable_path=driver_path)

    cathseoulUrl='https://www.cmcseoul.or.kr/page/department/A'
    cathyeoUrl='https://www.cmcsungmo.or.kr/page/department/A' #'eunpyeong','uijeongbu','bucheon','vincent'
    cathepUrl='https://www.cmcep.or.kr/page/department/A'
    cathujbUrl='https://www.cmcujb.or.kr/page/department/A'
    cathbcUrl='https://www.cmcbucheon.or.kr/page/department/A'
    cathvcUrl='https://www.cmcvincent.or.kr/page/department/A'
    cathUrls=[cathseoulUrl, cathyeoUrl, cathepUrl, cathujbUrl, cathbcUrl, cathvcUrl]
    cathUrls1=[cathvcUrl]
    cathUrls2=[cathyeoUrl]

    docs=[]
    for a in cathUrls:
        departmentLink = []
        doctordepartmentLink = []
        doctorLink = []
        wd.get(a)
        time.sleep(1)
        data1 = wd.find_elements_by_class_name('front')
        data2 = wd.find_elements_by_class_name('back')
        for i in range(len(data1)):
            name = data1[i].find_element_by_class_name('office').text
            if any(name == this for this in department):
                departmentLink.append(data2[i].find_element_by_tag_name('a').get_attribute('href'))

        for i in departmentLink:
            wd.get(i)
            doctordepartmentLink.append(wd.find_element_by_link_text("의료진").get_attribute('href'))


        for i in doctordepartmentLink:
            wd.get(i)
            time.sleep(5)
            datas = wd.find_elements_by_class_name('btn_doc_info')
            for data in datas:
                doctorLink.append(data.get_attribute('href'))

        for i in doctorLink:
            doc=[]
            wd.get(i)
            time.sleep(2)
            link=wd.current_url
            education=[]
            career=[]
            html=wd.page_source
            soup=BeautifulSoup(html,'html.parser')
            # 이름
            name=wd.find_element_by_css_selector('#sub_section > div.content > div.cont_main > div.cont_main_int > div.doc_intro_txt> div.doc_name > strong').text
            #if name.count('교수')>0 or name.count('전문의')>0:
            #    name=name.split(' ')[0]
            doc.append(name)
            #소속
            if '서울' in wd.title:
                belong='가톨릭대학교서울성모병원'
                hospital_code = '302815'
            elif '여의도' in wd.title:
                belong='가톨릭대학교여의도성모병원'
                hospital_code = '150010'
            elif '은평' in wd.title:
                belong='가톨릭대학교은평성모병원'
                hospital_code = '130010'
            elif '의정부' in wd.title:
                belong='가톨릭대학교의정부성모병원'
                hospital_code = '480110'
            elif '부천' in wd.title:
                belong='가톨릭대학교부천성모병원'
                hospital_code = '420710'
            else:
                belong='가톨릭대학교성빈센트병원'
                hospital_code = '442010'
            doc.append(belong)
            #진료과
            dpt = wd.find_element_by_css_selector('#sub_section > div.content > div.cont_main > div.cont_main_int > div.doc_intro_txt > div.doc_name > em').text
            doc.append(dpt)
            #진료분야
            major=soup.find('a',{'class','medical_part_btn'}).text
            if major=='':
                major=None
            doc.append(major)
            divs=soup.find('div',{'class','cont_main_profile'})
            """
            for a in soup.find_all('a'):
                if a.get_text()=='더보기':
                    print(a.get_text)
            """

            elm=wd.find_element_by_css_selector('#sub_section > div.content > div.cont_main > span > img')
            wheel_element(elm, -120)
            time.sleep(1)
            # 학력
            count=0
            check=0
            for div in divs.find_all('div'):
                count+=1
                if '학력'in div.text:
                    check=count
                    break
            try:
                while(1):
                    wd.find_element_by_xpath('//*[@id="sub_section"]/div[2]/div[1]/div[3]/div['+str(check)+']/span/a').click()
            except:
                pass
            time.sleep(1)
            # 경력
            count=0
            check=0
            for div in divs.find_all('div'):
                count+=1
                if '경력'in div.text:
                    check=count
                    break
            try:
                while(1):
                    wd.find_element_by_xpath('//*[@id="sub_section"]/div[2]/div[1]/div[3]/div['+str(check)+']/span/a').click()
            except:
                pass
            time.sleep(1)

            html=wd.page_source
            soup=BeautifulSoup(html,'html.parser')
            divs=soup.find('div',{'class','cont_main_profile'})
            for div in divs.find_all('div'):
                text=div.get_text()
                if '학력'in text:
                    try:
                        for li in div.find_all('li'):
                            try:
                                texts=li.find('dt').text
                                year=texts.split('\n')[1]
                                year=year[len(year)-9:]
                            except:
                                year=''
                            educ=li.find('dd').text
                            if year!='':
                                educ=year+' '+educ
                            education.append(educ)
                        education=', '.join(education)
                    except:
                        education=None
                elif '경력'in text:
                    try:
                        for li in div.find_all('li'):
                            try:
                                texts=li.find('dt').text
                                year=texts.split('\n')[1]
                                if year[len(year)-1]=='재':
                                    year=year[len(year)-7:]
                                else:
                                    year=year[len(year)-9:]
                            except:
                                year=''
                            care=li.find('dd').text
                            if year!='':
                                care=year+' '+care
                            career.append(care)
                        career=', '.join(career)
                    except:
                        career=None
            if education==[]:
                education=None
            if career==[]:
                career=None
            doc.append(education)
            doc.append(career)
            doc.append(link)
            doc.append(hospital_code)
            docs.append(doc)

            #"""
            print(name)
            print(belong)
            print(dpt)
            print(major)
            print(education)
            print(career)
            print(link)
            #"""
    wd.close()

    for i in docs:
        cursor.execute("INSERT INTO "+table_name+" (name_kor, belong, department, major, education, career, link, hospital_code) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);",(i[0],i[1],i[2],i[3],i[4],i[5],i[6],i[7]))
        connect.commit()
