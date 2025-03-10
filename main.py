import requests
import json

import time
import capsolver
import ctypes
import secrets

from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style,init
from datetime import datetime
from threading import Lock
from traceback import print_exc
from random import choice
from faker import Faker
from fake_useragent import UserAgent

lock = Lock()
fkr = Faker()
genned = 0
with open('config.json', 'r') as f:
    config = json.load(f)
capsolver.api_key = config["capsolver-key"]

def get_email():
  jsonr = requests.get('https://api.tempmail.lol/generate')
  return jsonr.json()["address"]+';'+jsonr.json()["token"]

def auth_email(token):
  jsonr2 = requests.get('https://api.tempmail.lol/auth/'+token)
  return jsonr2.json()
class Utils:
    def get_soln() -> str|None:
        try:
            soln = capsolver.solve({
            "type": "ReCaptchaV2TaskProxyLess",
            "websiteURL": "https://auth.opera.com/account/authenticate/email",
            "websiteKey": "6LdYcFgaAAAAAEH3UnuL-_eZOsZc-32lGOyrqfA4",
          })['gRecaptchaResponse']
            return soln
        except Exception as e:
            Logger.Sprint("ERROR",f"Captcha Error: {str(e)}",Fore.RED)
            return None
        
    def update_title() -> None:
        ctypes.windll.kernel32.SetConsoleTitleW(f"Opera GX Promo Gen By Notlit , Fixed by response | Generated : {genned}") 

class Logger:
    @staticmethod
    def Sprint(tag: str, content: str, color) -> None:
        ts = f"{Fore.RESET}{Fore.LIGHTBLACK_EX}{datetime.now().strftime('%H:%M:%S')}{Fore.RESET}"
        with lock:
            print(f"{Style.BRIGHT}{ts}{color} [{tag}] {Fore.RESET}{content}{Fore.RESET}")
    @staticmethod
    def Ask(tag: str, content: str, color):
        ts = f"{Fore.RESET}{Fore.LIGHTBLACK_EX}{datetime.now().strftime('%H:%M:%S')}{Fore.RESET}"
        return input(f"{Style.BRIGHT}{ts}{color} [{tag}] {Fore.RESET}{content}{Fore.RESET}")

class Opera:
    def __init__(self,proxy) -> None:
        self.session = requests.Session()
        self.session.proxies = proxy 
        self.user = secrets.token_hex(10)
        self.email, self.token = str(get_email()).split(';')
        self.user_agent = secrets.token_hex(10) # fire user agent 
        self.session.headers={
    'user-agent': self.user_agent,
}
    def exec_request(self,*args,**kwargs) -> requests.Response:
        for x in range(50):
            try:
                return self.session.request(*args,**kwargs)
            except:
                # print_exc()
                continue
        else:
            raise Exception("Failed To Execute Request After 50x Retries!")
    def post_request(self, *args, **kwargs) -> requests.Response:
        return self.exec_request("POST",*args,**kwargs)
    def get_request(self, *args, **kwargs) -> requests.Response:
        return self.exec_request("GET",*args,**kwargs)

    def regAndAuth(self) -> bool:
        self.get_request("https://auth.opera.com/account/authenticate",allow_redirects=True)
        start = time.time()
        soln = Utils.get_soln() 
        if not soln:
            return False
        Logger.Sprint("CAPTCHA","Successfully Solved in {}s".format("%.3f" % (time.time()-start)),Fore.LIGHTCYAN_EX)
        self.session.headers['x-language-locale'] = 'en'
        self.session.headers['referer'] = 'https://auth.opera.com/account/authenticate/signup'
        signUp = self.post_request("https://auth.opera.com/account/v4/api/signup",json={
    'email': self.email,
    'password': self.user,
    'password_repeated': self.user,
    'marketing_consent': False,
    'captcha' : soln,
    'services': ['gmx']})
        if "429" in signUp.text:
            Logger.Sprint("ERROR","Ratelimited On Signup!",Fore.LIGHTRED_EX)
            return False
        if not signUp.status_code in [200,201,204]:
            Logger.Sprint("ERROR",f"Signup Error: {signUp.text}",Fore.LIGHTRED_EX)
            return False
        self.csrf = self.session.cookies.get_dict()['__Host-csrftoken']
        self.session.headers['x-csrftoken'] = self.session.cookies.get_dict()['__Host-csrftoken']
        profile = self.exec_request("PATCH","https://auth.opera.com/api/v1/profile",json={"username":self.user})
        if not profile.status_code in [200,201,204]:
            Logger.Sprint("ERROR",f"Profile Set Error: {profile.json()}",Fore.LIGHTRED_EX)
            return False
        self.session.headers = {
    'authority': 'api.gx.me',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'referer': 'https://gx.me/signup/?utm_source=gxdiscord',
    'sec-ch-ua': '"Not A(Brand";v="99", "Opera GX";v="107", "Chromium";v="121"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-site',
    'upgrade-insecure-requests': '1',
    'user-agent': self.user_agent,
}
        time.sleep(2)
        self.get_request("https://api.gx.me/session/login?site=gxme&target=%2F",allow_redirects=True)
        self.get_request("https://auth.opera.com/account/login-redirect?service=gmx",allow_redirects=True)
        return True
        
    def gen(self) -> None:
        global genned
        for x in range(3):
            if not self.regAndAuth():
                continue
            break
        else:
            return 
        Logger.Sprint("AUTH",f"Fetched Auth on {self.email}",Fore.LIGHTMAGENTA_EX)
        json = {
  "email": self.email
}
        a = self.post_request("https://auth.opera.com/account/request-email-verification",
                          json=json,
                          headers = {
  "Accept": "application/json",
  "Accept-Encoding": "gzip, deflate, br",
  "Accept-Language": "en-US,en;q=0.9",
  "Connection": "keep-alive",
  "Content-Length": "47",
  "Content-Type": "application/json",
  "Host": "auth.opera.com",
  "Origin": "https://auth.opera.com",
  "Referer": "https://auth.opera.com/account/edit-profile",
  "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Opera";v="108"',
  "sec-ch-ua-mobile": "?0",
  "sec-ch-ua-platform": '"Windows"',
  "Sec-Fetch-Dest": "empty",
  "Sec-Fetch-Mode": "cors",
  "Sec-Fetch-Site": "same-origin",
  "User-Agent": self.user_agent,
  "X-CSRFToken": self.csrf
})
        time.sleep(10)
        try:
          full_json = auth_email(self.token)
          Vurl = full_json["email"][0]["body"]
          Incomplete = Vurl.split('https://auth.opera.com/account/email-verification?key=')[1].split('&service=auth')[0]
          FormattedUrl = 'https://auth.opera.com/account/email-verification?key='+Incomplete+'&service=auth'
        except:
            Logger.Sprint("EMAIL",f"Didn't Receive Email... [ Skipping Account.. ]", Fore.YELLOW)
            return
        self.get_request(FormattedUrl, allow_redirects=True)
        headers = {
  "Accept": "application/json",
  "Accept-Encoding": "gzip, deflate, br",
  "Accept-Language": "en-US,en;q=0.9",
  "Connection": "keep-alive",
  "Content-Length": "0",
  "Host": "auth.opera.com",
  "Origin": "https://auth.opera.com",
  "Referer": "https://auth.opera.com/account/email-verification/result?service=auth",
  "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Opera";v="108"',
  "sec-ch-ua-mobile": "?0",
  "sec-ch-ua-platform": '"Windows"',
  "Sec-Fetch-Dest": "empty",
  "Sec-Fetch-Mode": "cors",
  "Sec-Fetch-Site": "same-origin",
  "User-Agent": self.user_agent,
  "X-CSRFToken": self.csrf
}
        r = self.post_request('https://auth.opera.com/account/email-verification/confirm',
                          headers=headers)
        if r.status_code == 204:
            Logger.Sprint("EMAIL",f"Verified Email : {self.email}",Fore.BLUE)
        time.sleep(8)
        auth = self.get_request("https://api.gx.me/profile/token").json()['data']
        promoReq = self.post_request('https://discord.opr.gg/v2/direct-fulfillment', headers={
    'authorization': auth,
    'origin': 'https://www.opera.com',
    'referer': 'https://www.opera.com/',
    'user-agent': self.user_agent,
})
        if not "token" in promoReq.text or not promoReq.ok:
            Logger.Sprint("ERROR",f"Failed To Fetch Promo! Text: {promoReq.text} Code: {promoReq.status_code}",Fore.LIGHTRED_EX)
            return 
        promo = "https://discord.com/billing/partner-promotions/1180231712274387115/{}".format(promoReq.json()['token'])
        Logger.Sprint("PROMO",promo,Fore.LIGHTGREEN_EX)
        with lock:
            with open("promos.txt",'a') as io:
                io.write(f"{promo}\n")
                io.flush()
            genned += 1
            Utils.update_title()

def _task():
    while True:
        try:
            Opera(proxies).gen()
        except:
            print_exc()
            continue
if __name__ == "__main__":
    init()
    Utils.update_title()
    trds = int(Logger.Ask("INPUT","Enter Amount Of Threads: ",Fore.BLUE))
    proxies = {
        'http': 'http://'+config["rotating-proxy"] if config["useproxy"] == True else None,
        'https': 'https://'+config["rotating-proxy"] if config["useproxy"] == True else None
    }
    with ThreadPoolExecutor(max_workers=trds+1) as exc:
        for x in range(trds):
            exc.submit(_task)
