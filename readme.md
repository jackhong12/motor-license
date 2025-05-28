# 機車路考自動預定系統

### Requirement
```
python3.12
google-chrome
```

### Install
```bash
# By script
./install

# Manually
python3.12 -m venv venv
source venv/bin/active
pip3 install -r ./requirement.txt
sed -i "s|^REPO_PATH=.*|REPO_PATH=$(pwd)|" run
```

### Configure
修改 `.env` 檔:

```bash
EMAIL_USER=發信信箱
EMAIL_PASS=Google 應用程式密碼
EMAIL_RECV=收信信箱1;收信信箱2;...
EMAIL_DEV=開發者信箱1;開發者信箱2;...

SIGNUP_ID=身分證
SIGNUP_BIRTH=生日 (ex: 0990101)
SIGNUP_NAME=姓名
SIGNUP_PHONE=手機
SIGNUP_EMAIL=信箱
SIGNUP_IS_FIRST=True # 是否為初次報名
SIGNUP_PREFER_SITE=板橋;樹林
SIGNUP_PREFER_DATE=622;623 # 優先日期 (ex: 6/22,6/23)
```

### Run
```bash
./run
```
