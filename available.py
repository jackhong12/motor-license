from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import private
from sendmail import MailHandler
from datetime import date
from datetime import datetime

_licenseTypeCode = "普通重型機車"
_expectExamDateStr = str(int(date.today().strftime("%Y")) - 1911) + date.today().strftime("%m%d")
_locations = {
    "板橋": ["臺北區監理所（北宜花）",        "板橋監理站(新北市中和區中山路三段116號)"],
    #"士林": ["臺北市區監理所（含金門馬祖）",  "士林監理站(臺北市士林區承德路5段80號)"],
    #"基隆": ["臺北市區監理所（含金門馬祖）",  "基隆監理站(基隆市七堵區實踐路296號)"],
    #"金門": ["臺北市區監理所（含金門馬祖）",  "金門監理站(金門縣金湖鎮黃海路六之一號)"],
    #"漣江": ["臺北市區監理所（含金門馬祖）",   "連江監理站(連江縣南竿鄉津沙村155號)"],
    #"樹林": ["臺北區監理所（北宜花）",        "臺北區監理所(新北市樹林區中正路248巷7號)"],
    #"蘆洲": ["臺北區監理所（北宜花）",        "蘆洲監理站(新北市蘆洲區中山二路163號)"],
    #"屏東": ["高雄區監理所（高屏澎東）",      "屏東監理站(屏東市忠孝路222號)"],
    #"恆春": ["高雄區監理所（高屏澎東）",      "恆春監理分站(屏東縣恒春鎮草埔路11號)"],
}

_signupInfos = {
    'id':    private.SIGNUP_ID,
    'birth': private.SIGNUP_BIRTH,
    'name':  private.SIGNUP_NAME,
    'phone': private.SIGNUP_PHONE,
    'email': private.SIGNUP_EMAIL,
}

# 設定 Selenium WebDriver（以 Chrome 為例）
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 無頭模式
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10) # Wait for 10 second at most

isBooked = False

def signupExam (signupElement):
    global isBooked
    if isBooked:
        return False
    # Go to signup link
    signupLinkTag = signupElement.find_element(By.TAG_NAME, "a")
    signupLink = signupLinkTag.get_attribute("onclick")
    driver.execute_script(signupLink)
    # Get rid of block UI
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "blockUI.blockMsg.blockPage")))
    driver.execute_script("$.unblockUI();	return false;")

    # Register the test
    idInput = wait.until(EC.presence_of_element_located((By.ID, "idNo")))
    idInput.send_keys(_signupInfos['id'])
    birthInput = wait.until(EC.presence_of_element_located((By.ID, "birthdayStr")))
    birthInput.send_keys(_signupInfos['birth'])
    nameInput = wait.until(EC.presence_of_element_located((By.ID, "name")))
    nameInput.send_keys(_signupInfos['name'])
    phoneInput = wait.until(EC.presence_of_element_located((By.ID, "contactTel")))
    phoneInput.send_keys(_signupInfos['phone'])
    emailInput = wait.until(EC.presence_of_element_located((By.ID, "email")))
    emailInput.send_keys(_signupInfos['email'])
    driver.execute_script("add()")
    isBooked = True

    return True

def findAvailableDate (mail, location, isBook = False):
    # Open the website 
    driver.get("https://www.mvdis.gov.tw/m3-emv-trn/exm/locations")

    # Fill the form:
    #   報考照類 Type of Test：
    #   預計考試日期 Date of Test：
    #   考試地點 Place of Test：
    examTypeSelect = Select(wait.until(EC.presence_of_element_located((By.ID, "licenseTypeCode"))))
    examTypeSelect.select_by_visible_text(_licenseTypeCode)

    examDateInput = wait.until(EC.presence_of_element_located((By.ID, "expectExamDateStr")))
    examDateInput.send_keys(_expectExamDateStr)

    regionSelect = Select(wait.until(EC.presence_of_element_located((By.ID, "dmvNoLv1"))))
    regionSelect.select_by_visible_text(location[0])

    stationSelect = Select(wait.until(EC.presence_of_element_located((By.ID, "dmvNo"))))
    stationSelect.select_by_visible_text(location[1])
    
    #import pdb; pdb.set_trace()
    # Submit the form and get avaliable dates.
    driver.execute_script("query()")

    # Click "選擇場次繼續報名"
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "msg_box_success")))
    driver.execute_script("$.unblockUI();")

    # Data
    titles = [] 

    tables = driver.find_elements(By.ID, "trnTable")
    assert len(tables) == 1
    table = tables[0]
    
    tableHeads = table.find_elements(By.TAG_NAME, "thead")
    assert len(tableHeads) == 1
    tableHead = tableHeads[0]
    tableTitles = tableHead.find_elements(By.TAG_NAME, "th")
    for tableTitle in tableTitles:
        titles += [tableTitle.text]

    tableBodies = table.find_elements(By.TAG_NAME, "tbody")
    assert len(tableBodies) == 1
    tableBody = tableBodies[0]

    rows = tableBody.find_elements(By.TAG_NAME, "tr")
    avaliableDates = []
    fullDates = []

    for row in rows:
        infos = []
        cols = row.find_elements(By.TAG_NAME, "td")
        for col in cols:
            infos += [col.text]
        assert len(infos) == len(titles) 
        infos[1] = infos[1].replace("\n", " ")

        data = {
            'date':        infos[0],
            'description': infos[1],
            'number':      infos[2],
            'avaliable':   False,
            'link':        cols[3]
        }

        if infos[2] != "額滿" and infos[1].find("重考") >= 0:
            avaliableDates += [data]
        else:
            fullDates += [data]
    
    if len(avaliableDates) > 0:
        if isBook:
            target = avaliableDates[0]
            if signupExam(target['link']):
                mail.textln(f"## 成功申請!!!!!")
                mail.textln(f"- 地點: {location[1]}")
                mail.textln(f"- 時間: {target['date']}")
                mail.textln(f"- 名額: {target['number']}")
                mail.textln(f"- 說明: {target['description']}")
                mail.textln(f"- 身分: {_signupInfos['id']}")
                mail.textln(f"- 名字: {_signupInfos['name']}")
                mail.textln(f"- 生日: {_signupInfos['birth']}")
                mail.textln(f"- 手機: {_signupInfos['phone']}")
                mail.textln(f"- 信箱: {_signupInfos['email']}")
                mail.textln("")

        mail.textln(f"#### {location[1]}")
    if len(fullDates) > 0:
        mail.textln(f"#### {location[1]}", False)

    for date in avaliableDates:
        mail.textln(f"##### {date['date']}")
        mail.textln(f"- 名額: {date['number']}")
        mail.textln(f"- 說明: {date['description']}")
        mail.textln("")

    for date in fullDates:
        mail.textln(f"- {date['date']}", False)


def tryAllSites ():
    mail = MailHandler()
    mail.textln("### 有名額時段:")
    mail.textln("### 額滿時段:", False)

    for loc, details in _locations.items():
        print(f"  - {details[1]}")
        #findAvailableDate(mail, details, True)
        findAvailableDate(mail, details, False)

    mail.plain()
    if isBooked:
        mail.send()
        return True
    return False

while True:
    print(f"\n-> {datetime.now()}")
    if tryAllSites():
        break
    time.sleep(10 * 60) # every 10 sec

driver.quit()
