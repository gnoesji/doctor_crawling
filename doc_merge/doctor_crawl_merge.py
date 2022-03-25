from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from urllib.request import urlopen
from bs4 import BeautifulSoup
import time
import pymysql
import requests
import re
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

start = time.time()

#아주대학교병원 - AJOUMC
import ajoumc_doctor
#창원경상국립대학교병원 - GNUCH
import gnuch_doctor
#경상국립대학교병원 - GNUH
import gnuh_doctor
#고려대학교 안암/구로/안산 - KUMC
import kumc_doctor
#가톨릭대학교성모병원(서울/여의도/은평/의정부/부천/성빈센트) - CMC
import cmc_doctor
#단국대학교 - DANKOOK
import dankook_doctor
#서울한양대학교병원 - HANYANG
import hanyang_doctor
#연세대학교세브란스 의대강남/용인/본원- SEV
import sev_doctor
#서울대학교병원(본원) - SNUH
import snuh_doctor
#영남대학교병원 - YEONGNAM
import yeungnam_doctor
# ---------------------------------------------------- 추가
#중앙대학교병원 - CAU
import cau_doctor
#충북대학교병원 - CBN
import cbn_doctor
#동아대학교병원 - DAMC
import dongA_doctor
#강릉아산병원-GNAH
import gnah_doctor
#계명대학교동산병원-DSMC
import keimyung_doctor
#삼성서울-SAMSUNG
import samsung_doctor
#연세대학교원주세브란스기독병원-YWMC
import wonjuSeverance_doctor
#경희대학교병원-KHUH
import khuh_doctor
#전남대학교병원-CHONNAM
import chonnam_doctor
#충남대학교병원-CNUH
import chungnam_doctor
#부산대학교병원-PNUHM
import pnuhm_doctor
#강북삼성병원-KBSMC
import kbsmc_doctor
#건국대학교-KUH
import kuh_doctor
#양산/어린이 부산대학교-PNUH
import pnuh_doctor
#분당서울대학교병원-SNUBH
import snubh_doctor
#삼성창원병원-CWSMC
import cwsmc_doctor
#인제대학교병원-INJE
import inje_doctor
#카톨릭대학교 대전성모병원-CMCDJ
import cmcdj_doctor
#카톨릭대학교 인천성모병원-CMCISM
import cmcism_doctor


host = 'localhost'
user = 'root'
passwd = '[password name]'
db = '[schema name]'
driver_path = './chromedriver'

doctor_table = 'doctor_merge'

conn = pymysql.connect(
    user =user,
    passwd = passwd,
    db = db,
    host = host,
    charset = 'utf8mb4'
)
cursor = conn.cursor()

"""
# 의료진 Table
sql = '''CREATE TABLE '''+doctor_table+'''(
name_kor VARCHAR(20) NOT NULL,
belong VARCHAR(30),
department mediumtext,
major mediumtext,
education mediumtext,
career mediumtext,
link mediumtext,
hospital_code VARCHAR(6)
)'''
cursor.execute(sql)
conn.commit()
"""


#아주대학교병원 - ajoumc
ajoumc_doctor.doctor(conn, cursor, doctor_table, driver_path)
print("아주대학교병원 - 의료진 성공")

#충북대학교병원 - CBN
cbn_doctor.doctor(conn, cursor, doctor_table, driver_path)
print("충북대학교병원 - 의료진 성공")

#창원경상국립대학교병원
gnuch_doctor.doctor(conn, cursor, doctor_table, driver_path)
print("창원경상국립대학교병원 - 의료진 성공")

#경상국립대학교병원 - GNUH
gnuh_doctor.doctor(conn, cursor, doctor_table, driver_path)
print("경상국립대학교병원 - 의료진 성공")

#고려대학교 안암/구로/안산 - KUMC
kumc_doctor.doctor(conn, cursor, doctor_table, driver_path)
print("고려대학교 안암/구로/안산 - 의료진 성공")

#가톨릭대학교성모병원(서울/여의도/은평/의정부/부천/성빈센트) - CMC
cmc_doctor.doctor(conn, cursor, doctor_table, driver_path)
print("가톨릭대학교성모병원(서울/여의도/은평/의정부/부천/성빈센트) - 의료진 성공")

#단국대학교 - DANKOOK
dankook_doctor.doctor(conn, cursor, doctor_table, driver_path)
print("단국대학교 - 의료진 성공")

#서울한양대학교병원 - HANYANG
hanyang_doctor.doctor(conn, cursor, doctor_table, driver_path)
print("서울한양대학교병원 - 의료진 성공")

#연세대학교세브란스 의대강남/용인/본원 - SEV
sev_doctor.doctor(conn, cursor, doctor_table, driver_path)
print("연세대학교세브란스 의대강남/용인/본원 - 의료진 성공")

#서울대학교병원(본원) - SNUH
snuh_doctor.doctor(conn, cursor, doctor_table, driver_path)
print("서울대학교병원(본원) - 의료진 성공")

#영남대학교병원 - YEONGNAM
yeungnam_doctor.doctor(conn, cursor, doctor_table, driver_path)
print("영남대학교병원 - 의료진 성공")

#동아대학교병원 - DAMC
dongA_doctor.doctor(conn, cursor, doctor_table, driver_path)
print("동아대학교병원 - 의료진 성공")

#강릉아산병원-GNAH
gnah_doctor.doctor(conn, cursor, doctor_table, driver_path)
print("강릉아산병원 - 의료진 성공")

#계명대학교동산병원-DSMC
keimyung_doctor.doctor(conn, cursor, doctor_table, driver_path)
print("계명대학교동산병원 - 의료진 성공")

#삼성서울-SAMSUNG
samsung_doctor.doctor(conn, cursor, doctor_table, driver_path)
print("삼성서울 - 의료진 성공")

#연세대학교원주세브란스기독병원-YWMC
wonjuSeverance_doctor.doctor(conn, cursor, doctor_table, driver_path)
print("연세대학교원주세브란스기독병원 - 의료진 성공")


#전남대학교병원-CHONNAM
chonnam_doctor.doctor(conn, cursor, doctor_table, driver_path)
print("전남대학교병원 - 의료진 성공")

#충남대학교병원-CNUH
chungnam_doctor.doctor(conn, cursor, doctor_table, driver_path)
print("충남대학교병원 - 의료진 성공")

#부산대학교병원-PNUHM
pnuhm_doctor.doctor(conn, cursor, doctor_table, driver_path)
print("부산대학교병원 - 의료진 성공")

#건국대학교-KUH
kuh_doctor.doctor(conn, cursor, doctor_table, driver_path)
print("건국대학교 - 의료진 성공")

#양산/어린이 부산대학교-PNUH
pnuh_doctor.doctor(conn, cursor, doctor_table, driver_path)
print("양산/어린이 부산대학교 - 의료진 성공")

#분당서울대학교병원-SNUBH
snubh_doctor.doctor(conn, cursor, doctor_table, driver_path)
print("분당서울대학교병원 - 의료진 성공")

#인제대학교병원-INJE
inje_doctor.doctor(conn, cursor, doctor_table, driver_path)
print("인제대학교병원 - 의료진 성공")


## 오류 발생하는 코드
'''
#삼성창원병원-CWSMC
cwsmc_doctor.doctor(conn, cursor, doctor_table, driver_path)
print("삼성창원병원 - 의료진 성공")

#중앙대학교병원 - CAU
cau_doctor.doctor(conn, cursor, doctor_table, driver_path)
print("중앙대학교병원 - 의료진 성공")

#가톨릭대학교 대전성모병원-CMCDJ
cmcdj_doctor.doctor(conn, cursor, doctor_table, driver_path)
print("가톨릭대학교 대전성모병원 - 의료진 성공")

#가톨릭대학교 인천성모병원-CMCISM
cmcism_doctor.doctor(conn, cursor, doctor_table, driver_path)
print("가톨릭대학교 인천성모병원 - 의료진 성공")

#강북삼성병원-KBSMC
kbsmc_doctor.doctor(conn, cursor, doctor_table, driver_path)
print("강북삼성병원 - 의료진 성공")

#경희대학교병원-KHUH
khuh_doctor.doctor(conn, cursor, doctor_table, driver_path)
print("경희대학교병원 - 의료진 성공")
'''



conn.close()
print(time.time()-start)


