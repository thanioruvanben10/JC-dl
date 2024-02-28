import requests,json,re,jwt
import os, sys
import base64

# define 
def load_config():
    global accesstoken, devid
    with open ("creds.txt", "r") as f:
        try:
            Creds = json.load(f)
            accesstoken = Creds['accesstoken']
            devid = Creds['deviceid']
        except json.JSONDecodeError:
            accesstoken = ''
            devid = ''    

Request_URL = "https://apis-jiovoot.voot.com/playbackjv/v4/"
Meta_URL = "https://prod.media.jio.com/apis/common/v3/metamore/get/"
OTPSendURL = "https://auth-jiocinema.voot.com/userservice/apis/v4/loginotp/send"
OTPVerifyURL = "https://auth-jiocinema.voot.com/userservice/apis/v4/loginotp/verify"
IdURL = "https://cs-jv.voot.com/clickstream/v1/get-id"
GuestURL = "https://auth-jiocinema.voot.com/tokenservice/apis/v4/guest"

def get_accesstoken():
    id = requests.get(url=IdURL).json()['id']

    token = requests.post(url=GuestURL, json={
            'adId': id,
            "appName": "RJIL_JioCinema",
            "appVersion": "23.10.13.0-841c2bc7",
            "deviceId": id,
            "deviceType": "phone",
            "freshLaunch": True,
            "os": "ios"
        }, headers={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
        }).json()

    return token["authToken"], id

def login(mobile_number):
    accesstoken, id = get_accesstoken()
    
    send = requests.post(url=OTPSendURL, json={
            "number": base64.b64encode(f"+91{mobile_number}".encode()).decode(),
            "appVersion": "23.10.13.0-841c2bc7"
        }, headers = {
            'accesstoken': accesstoken,
            'appname': 'RJIL_JioCinema',
            'cache-control': 'no-cache',
            'devicetype': 'phone',
            'os': 'ios',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
})
    print(send.content)
    if 'karix' in str(send.content):
        OTP = input ('Enter OTP Received: ')
        verify = requests.post(url = OTPVerifyURL, headers = {
            'accesstoken': accesstoken,
            'appname': 'RJIL_JioCinema',
            'cache-control': 'no-cache',
            'devicetype': 'phone',
            'os': 'ios',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        }, json={
            "appVersion": "23.10.13.0-841c2bc7",
            "deviceInfo": {
                "consumptionDeviceName": "iPhone",
                "info": {
                    "androidId": id,
                    "platform": {
                        "name": "iPhone OS"
                    },
                    "type": "iOS"
                }
            },
            "number": base64.b64encode(f"+91{mobile_number}".encode()).decode(),
            "otp": OTP
        })
        creds = json.loads(verify.content)
        load_creds(creds)
    else:
        print ("Wrong/Unregistered Mobile Number (ensure there's no +91 or 0 in the beginning)")
        sys.exit()

def load_creds(creds):
    try:
        accesstoken = creds['authToken']
        devid = creds['deviceId']
    except KeyError:
        print ("Wrong OTP, Try again!")
        sys.exit()
    Creds = {
        "accesstoken" : accesstoken,
        "deviceid" : devid
    }
    with open("creds.txt", "w") as f:
        f.write(json.dumps(Creds))

def get_manifest(VideoID):
    headers = {
    "Accesstoken": accesstoken,
    "Appname": "RJIL_JioCinema",
    "Versioncode": "2310130",
    "Deviceid": devid,
    "x-apisignatures": "o668nxgzwff",
    "X-Platform": "androidweb",
    "X-Platform-Token": "web",
    "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    }
    response = requests.post(url=Request_URL + VideoID, headers=headers, json={
            "4k": False,
            "ageGroup": "18+",
            "appVersion": "3.4.0",
            "bitrateProfile": "xhdpi",
            "capability": {
                "drmCapability": {
                    "aesSupport": "yes",
                    "fairPlayDrmSupport": "none",
                    "playreadyDrmSupport": "none",
                    "widevineDRMSupport": "none"
                },
                "frameRateCapability": [
                    {
                    "frameRateSupport": "60fps",
                    "videoQuality": "2160p"
                    }
                ]
            },
            "continueWatchingRequired": True,
            "dolby": True,
            "downloadRequest": False,
            "hevc": False, # adjust accordingly
            "kidsSafe": False,
            "manufacturer": "Windows",
            "model": "Windows",
            "multiAudioRequired": True,
            "osVersion": "10",
            "parentalPinValid": True,
            "x-apisignatures": "o668nxgzwff"
        })
    return json.loads(response.text)

load_config()
if accesstoken == "" and devid == "":
    M_No = input ('Enter Mobile Number: ')
    login (M_No)
    load_config()
VideoID = input ('Enter VideoID: ')
manifest = get_manifest(VideoID)
print("MANIFEST: ",manifest)

access_token = accesstoken  
    
print('\ntest link: https://www.jiocinema.com/movies/sergeant-bhojpuri/3767689\ntest link: https://www.jiocinema.com/tv-shows/kaalkoot/1/janam-din/3788001\n')

link = input('link: ')
link_id = re.findall(r'.*/(.*)', link)[0].strip()

decoded = jwt.decode(access_token, options={"verify_signature": False})
#print(f'\n{decoded}\n')

deviceId = decoded['data']['deviceId']
uniqueid = decoded['data']['userId']
appName = decoded['data']['appName']

headers2 = {
    'authority': 'apis-jiovoot.voot.com',
    'accept': 'application/json, text/plain, */*',
    'accesstoken': access_token,
    'appname': appName,
    'content-type': 'application/json',
    'deviceid': deviceId,
    'origin': 'https://www.jiocinema.com',
    'referer': 'https://www.jiocinema.com/',
    'uniqueid': uniqueid,
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'versioncode': '560',
    'x-platform': 'androidweb',
    'x-platform-token': 'web',
}

json_data2 = {
    '4k': False,
    'ageGroup': '18+',
    'appVersion': '3.4.0',
    'bitrateProfile': 'xhdpi',
    'capability': {
        'drmCapability': {
            'aesSupport': 'yes',
            'fairPlayDrmSupport': 'yes',
            'playreadyDrmSupport': 'none',
            'widevineDRMSupport': 'yes',
        },
        'frameRateCapability': [
            {
                'frameRateSupport': '30fps',
                'videoQuality': '1440p',
            },
        ],
    },
    'continueWatchingRequired': True,
    'dolby': False,
    'downloadRequest': False,
    'hevc': False,
    'kidsSafe': False,
    'manufacturer': 'Windows',
    'model': 'Windows',
    'multiAudioRequired': True,
    'osVersion': '10',
    'parentalPinValid': True,
}

response2 = requests.post('https://apis-jiovoot.voot.com/playbackjv/v4/'+link_id+'', headers=headers2, json=json_data2, verify=False).json()
print("META2: ",response2)
