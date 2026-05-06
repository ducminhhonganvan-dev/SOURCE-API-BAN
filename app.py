from flask import Flask, request, jsonify
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import MajorLogin_res_pb2
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp
import base64
import json
import socket
import time
import traceback
import warnings
import urllib3
import random
import uuid
import os

# Disable warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore')

app = Flask(__name__)

# ---------------- SimpleProtobuf Class  ---------------- #
class SimpleProtobuf:
    @staticmethod
    def encode_varint(value):
        result = bytearray()
        while value > 0x7F:
            result.append((value & 0x7F) | 0x80)
            value >>= 7
        result.append(value & 0x7F)
        return bytes(result)   

    @staticmethod
    def decode_varint(data, start_index=0):
        value = 0
        shift = 0
        index = start_index
        while index < len(data):
            byte = data[index]
            index += 1
            value |= (byte & 0x7F) << shift
            if not (byte & 0x80):
                break
            shift += 7
        return value, index    

    @staticmethod
    def parse_protobuf(data):
        result = {}
        index = 0        
        while index < len(data):
            if index >= len(data):
                break
            tag = data[index]
            field_num = tag >> 3
            wire_type = tag & 0x07
            index += 1            
            if wire_type == 0:
                value, index = SimpleProtobuf.decode_varint(data, index)
                result[field_num] = value
            elif wire_type == 2:
                length, index = SimpleProtobuf.decode_varint(data, index)
                if index + length <= len(data):
                    value_bytes = data[index:index + length]
                    index += length
                    try:
                        result[field_num] = value_bytes.decode('utf-8')
                    except:
                        result[field_num] = value_bytes
            else:
                break        
        return result    

    @staticmethod
    def encode_string(field_number, value):
        if isinstance(value, str):
            value = value.encode('utf-8')        
        result = bytearray()
        result.extend(SimpleProtobuf.encode_varint((field_number << 3) | 2))
        result.extend(SimpleProtobuf.encode_varint(len(value)))
        result.extend(value)
        return bytes(result)   

    @staticmethod
    def encode_int32(field_number, value):
        result = bytearray()
        result.extend(SimpleProtobuf.encode_varint((field_number << 3) | 0))
        result.extend(SimpleProtobuf.encode_varint(value))
        return bytes(result)   

    @staticmethod
    def create_login_payload(open_id, access_token, platform):
        p = str(platform)
        random_ip = f"1{random.randint(0,9)}{random.randint(0,9)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
        random_device = f"Google|{str(uuid.uuid4())}"

        payload = bytearray()
        payload.extend(SimpleProtobuf.encode_string(3,  datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        payload.extend(SimpleProtobuf.encode_string(4,  "free fire"))
        payload.extend(SimpleProtobuf.encode_int32 (5,  4))
        payload.extend(SimpleProtobuf.encode_string(7,  "1.123.1"))
        payload.extend(SimpleProtobuf.encode_string(8,  "Android OS 11 / API-30 (RP1A.200720.012/G991BXXU3AUL1)"))
        payload.extend(SimpleProtobuf.encode_string(9,  "Handheld"))
        payload.extend(SimpleProtobuf.encode_string(10, "vn"))
        payload.extend(SimpleProtobuf.encode_string(11, "WIFI"))
        payload.extend(SimpleProtobuf.encode_int32 (12, 2400))
        payload.extend(SimpleProtobuf.encode_int32 (13, 1080))
        payload.extend(SimpleProtobuf.encode_string(14, "560"))
        payload.extend(SimpleProtobuf.encode_string(15, "ARM64 FP ASIMD AES | 8192 | 8"))
        payload.extend(SimpleProtobuf.encode_int32 (16, 3328))
        payload.extend(SimpleProtobuf.encode_string(17, "Adreno (TM) 640"))
        payload.extend(SimpleProtobuf.encode_string(18, "OpenGL ES 3.2 V@0490.0 (GIT@f51fd3a, Ia8bab3e8c8, 1602597876) (Date:10/13/20)"))
        payload.extend(SimpleProtobuf.encode_string(19, random_device))
        payload.extend(SimpleProtobuf.encode_string(20, random_ip))
        payload.extend(SimpleProtobuf.encode_string(21, "en"))
        payload.extend(SimpleProtobuf.encode_string(22, open_id))
        payload.extend(SimpleProtobuf.encode_string(23, p))
        payload.extend(SimpleProtobuf.encode_string(24, "Handheld"))
        payload.extend(SimpleProtobuf.encode_string(25, "samsung SM-G991B"))
        payload.extend(SimpleProtobuf.encode_string(29, access_token))
        payload.extend(SimpleProtobuf.encode_int32 (30, 1))
        payload.extend(SimpleProtobuf.encode_string(41, "vn"))
        payload.extend(SimpleProtobuf.encode_string(42, "WIFI"))
        payload.extend(SimpleProtobuf.encode_string(57, "4a10243f7968f0b4bea6b7c7c678e6fa"))
        payload.extend(SimpleProtobuf.encode_int32 (60, 2019120270))
        payload.extend(SimpleProtobuf.encode_int32 (61, 1424))
        payload.extend(SimpleProtobuf.encode_int32 (62, 3349))
        payload.extend(SimpleProtobuf.encode_int32 (63, 24))
        payload.extend(SimpleProtobuf.encode_int32 (64, 1552))
        payload.extend(SimpleProtobuf.encode_int32 (65, 2019120270))
        payload.extend(SimpleProtobuf.encode_int32 (66, 1552))
        payload.extend(SimpleProtobuf.encode_int32 (67, 2019120270))
        payload.extend(SimpleProtobuf.encode_int32 (73, 1))
        payload.extend(SimpleProtobuf.encode_string(74, "/data/app/~~lqYdjEs9bd43CagTaQ9JPg==/com.dts.freefireth-i72Sh_-sI0zZHs5Bw6aufg==/lib/arm64"))
        payload.extend(SimpleProtobuf.encode_int32 (76, 2))
        payload.extend(SimpleProtobuf.encode_string(77, "4a10243f7968f0b4bea6b7c7c678e6fa|/data/app/~~lqYdjEs9bd43CagTaQ9JPg==/com.dts.freefireth-i72Sh_-sI0zZHs5Bw6aufg==/base.apk"))
        payload.extend(SimpleProtobuf.encode_int32 (78, 2))
        payload.extend(SimpleProtobuf.encode_int32 (79, 2))
        payload.extend(SimpleProtobuf.encode_string(81, "64"))
        payload.extend(SimpleProtobuf.encode_string(83, "2019120270"))
        payload.extend(SimpleProtobuf.encode_int32 (85, 1))
        payload.extend(SimpleProtobuf.encode_string(86, "OpenGLES3"))
        payload.extend(SimpleProtobuf.encode_int32 (87, 16383))
        payload.extend(SimpleProtobuf.encode_int32 (88, 4))
        payload.extend(SimpleProtobuf.encode_string(90, "HoChiMinh"))
        payload.extend(SimpleProtobuf.encode_string(91, "VN"))
        payload.extend(SimpleProtobuf.encode_int32 (92, 70000))
        payload.extend(SimpleProtobuf.encode_string(93, "android"))
        payload.extend(SimpleProtobuf.encode_string(94, "MIIFhjCCA26gAwIBAgIUVCQdTKC364qgxvKKn15UMOLnM0wwDQYJKoZIhvcNAQELBQAwdDELMAkGA1UEBhMCVVMxEzARBgNVBAgTCkNhbGlmb3JuaWExFjAUBgNVBAcTDU1vdW50YWluIFZpZXcxFDASBgNVBAoTC0dvb2dsZSBJbmMuMRAwDgYDVQQLEwdBbmRyb2lkMRAwDgYDVQQDEwdBbmRyb2lkMB4XDTE3MDkyODEwMDgyNloXDTQ3MDkyODEwMDgyNlowdDELMAkGA1UEBhMCVVMxEzARBgNVBAgTCkNhbGlmb3JuaWExFjAUBgNVBAcTDU1vdW50YWluIFZpZXcxFDASBgNVBAoTC0dvb2dsZSBJbmMuMRAwDgYDVQQLEwdBbmRyb2lkMRAwDgYDVQQDEwdBbmRyb2lkMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAvylTyLEk6kqvaTtO+5+GW/sQ8P2yhsXpDiuRSQis56yl8UMR8mx8roLnnTU/mv8sKBf8Y811Z5BBBTaty/305IMnx5Exl/fE30atgemNjt66wGFio1wT1qhTPgK1qZYRTBpGIAcADd1g6xfw5ujF00XfzeOQBRWmYPioCpWI9tK+VayHk6jU09I9Y1TNUz5D76X4y7WQjIotpFRP8y9dzZJPG7Nh+RYbQdW2RxD10NITD6FQdRanWFRJP5YCQEMN/SGGdPnfCetDxXLwSVGdTfsWwTWrYBueMTUlFBSZDgSt8MXW1R9bF5UUEiz74OiZNONhx1LRrydyTDC3O/K0LaJ8d6s+Dyfonq4bRF4UQ0C/tQtJtz5XTkmY9wsscLekZ+TDwHKEP0m0j7pktBq54Bdr+TNPlyQ/NaWr4SeKiLbFEDfIPy5XoOcJX3anIjw4sm2xPr4YST8zDcnNFiq4RkMdOyyumxapasD0JSTslQu1MjLBH7S1QdNLIU+EByyjd5X9wtLww40jHxcPLUihb0glIJTg6YTWKDIg9dcJ/gc7uSSaqjG8cX86wBTaleV32x+gYtFxy4SNIEiwevP0zFirhTcQ7eJvfDvtyMqnpDUHzvTmvddyekQuWOr2Lmh0ZnBWb8H93heQcrr7gOUgi/DZS6MwMRK8fy6nQT39RzsCAwEAAaMQMA4wDAYDVR0TBAUwAwEB/zANBgkqhkiG9w0BAQsFAAOCAgEAP+WSvrwEWPjLMWyIB8KfPjkWMgPf+6/SWhw1Yj0Fnoo430rcmDw9YHInJXvDxW8gSOfxxzKzENLFQEQl08K7htiEI7lDPHqdrjV615cV+tzrTM5mX4i0jbZ3zKDBrY8pHbzvrPuaZm5Nk4N06L+jsLDkzPq/gUKdGLSjiYK32asOduq4ILNlh2QFJkQm/cFZw71c+UWNDiLQ2PX1644e9/Akzh5X4X2lMA4yAGWDRhFFzbdDCGlsUkD/3qxvN1O3k82YIzYQKrpN9c9J3lvnDDKzpwNptZRLB+mWej637FWrByRygbxzqAjtfhPoGW7Kd6vvRtvVGlyCJzYMMhtZPnmHRqCaGzo9MKh+9IICDCDWt4u2HR4QcYCAsZeCJE3gkP4vnqLp3y2BqOisZHgIB94MlUeTzJOLLHY+jIdr9sKDGvtgy5FHwdd8aCHxRvjNF2W/oDnWX7mVPcwueGbToEszvoP0hbEqgJIOHGGgLIjQ7+0gqkT/az3owaP/KNRtkDpoRXCA8aSCjC+UyY01qnj/rS4l9IAxIthSqf6BYEUWnL53KpQWuYVHq5CNEjjnM/0LKIvTh1wIDQCCtfn9Hwp6cud2LYafRKgOZekqb/UlZGf/LJ1vkBKvIr48xLRCDHeRW5kuPFBZISMfSR/KRjIQTCn07fbXunufqeJ868c="))
        payload.extend(SimpleProtobuf.encode_int32 (97, 1))
        payload.extend(SimpleProtobuf.encode_int32 (98, 1))
        payload.extend(SimpleProtobuf.encode_string(99,  p))
        payload.extend(SimpleProtobuf.encode_string(100, p))
        payload.extend(SimpleProtobuf.encode_string(102, ""))
        return bytes(payload)

# ---------------- Helper Functions ---------------- #
def b64url_decode(input_str: str) -> bytes:
    rem = len(input_str) % 4
    if rem:
        input_str += '=' * (4 - rem)
    return base64.urlsafe_b64decode(input_str)

def get_available_room(input_text):
    try:
        data = bytes.fromhex(input_text)
        result = {}
        index = 0        
        while index < len(data):
            if index >= len(data):
                break                
            tag = data[index]
            field_num = tag >> 3
            wire_type = tag & 0x07
            index += 1            
            if wire_type == 0:
                value = 0
                shift = 0
                while index < len(data):
                    byte = data[index]
                    index += 1
                    value |= (byte & 0x7F) << shift
                    if not (byte & 0x80):
                        break
                    shift += 7
                result[str(field_num)] = {"wire_type": "varint", "data": value}                
            elif wire_type == 2:
                length = 0
                shift = 0
                while index < len(data):
                    byte = data[index]
                    index += 1
                    length |= (byte & 0x7F) << shift
                    if not (byte & 0x80):
                        break
                    shift += 7                
                if index + length <= len(data):
                    value_bytes = data[index:index + length]
                    index += length
                    try:
                        value_str = value_bytes.decode('utf-8')
                        result[str(field_num)] = {"wire_type": "string", "data": value_str}
                    except:
                        result[str(field_num)] = {"wire_type": "bytes", "data": value_bytes.hex()}
            else:
                break                
        return json.dumps(result)
    except Exception as e:
        return None

def extract_jwt_payload_dict(jwt_s: str):
    try:
        parts = jwt_s.split('.')
        if len(parts) < 2:
            return None
        payload_b64 = parts[1]
        payload_bytes = b64url_decode(payload_b64)
        payload = json.loads(payload_bytes.decode('utf-8', errors='ignore'))
        if isinstance(payload, dict):
            return payload
    except Exception:
        pass
    return None

def encrypt_packet(hex_string: str, aes_key, aes_iv) -> str:
    if isinstance(aes_key, str):
        aes_key = bytes.fromhex(aes_key)
    if isinstance(aes_iv, str):
        aes_iv = bytes.fromhex(aes_iv)   
    data = bytes.fromhex(hex_string)
    cipher = AES.new(aes_key, AES.MODE_CBC, aes_iv)
    encrypted = cipher.encrypt(pad(data, AES.block_size))
    return encrypted.hex()

def build_start_packet(account_id: int, timestamp: int, jwt: str, key, iv) -> str:
    try:
        encrypted = encrypt_packet(jwt.encode().hex(), key, iv)
        head_len = hex(len(encrypted) // 2)[2:]
        ide_hex = hex(int(account_id))[2:]
        zeros = "0" * (16 - len(ide_hex))
        timestamp_hex = hex(timestamp)[2:].zfill(2)
        head = f"0115{zeros}{ide_hex}{timestamp_hex}00000{head_len}"
        start_packet = head + encrypted        
        return start_packet
    except Exception as e:
        return None

def send_once(remote_ip, remote_port, payload_bytes, recv_timeout=3.0):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(recv_timeout)
    try:
        s.connect((remote_ip, remote_port))
        s.sendall(payload_bytes)        
        chunks = []
        try:
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                chunks.append(chunk)
        except socket.timeout:
            pass
        return b"".join(chunks)
    finally:
        s.close()

# --------------- ---------------- #
def process_login(access_token):
    try:
        # Step 1: Inspect token
        inspect_url = f"https://100067.connect.garena.com/oauth/token/inspect?token={access_token}"
        inspect_headers = {
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "close",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "100067.connect.garena.com",
            "User-Agent": "GarenaMSDK/4.0.19P4(G011A ;Android 9;en;US;)"
        }

        try:
            resp = requests.get(inspect_url, headers=inspect_headers, timeout=10)
            data = resp.json()
            if 'error' in data:
                return {"success": False, "message": f"Token error: {data.get('error')}"}
        except Exception as e:
            return {"success": False, "message": f"Failed to inspect token: {str(e)}"}

        NEW_OPEN_ID = data.get('open_id')
        platform_ = data.get('platform')

        # Step 2: MajorLogin
        key = b'Yg&tc%DEuh6%Zc^8'
        iv = b'6oyZDr22E3ychjM%'
        MajorLogin_url = "https://loginbp.ggpolarbear.com/MajorLogin"
        MajorLogin_headers = {
            "Host": "loginbp.ggpolarbear.com",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; SM-G991B Build/RP1A.200720.012)",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Content-Type": "application/octet-stream",
            "Expect": "100-continue",
            "X-GA": "v1 1",
            "X-Unity-Version": "2018.4.11f1",
            "ReleaseVersion": "OB53"
        }

        data_pb = SimpleProtobuf.create_login_payload(NEW_OPEN_ID, access_token, str(platform_))
        data_padded = pad(data_pb, 16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        enc_data = cipher.encrypt(data_padded)

        try:
            response = requests.post(MajorLogin_url, headers=MajorLogin_headers, data=enc_data, timeout=15)
            # Show Debug
#            print(f"[D6] status: {response.status_code}")
#            print(f"[D7] response headers: {dict(response.headers)}")
#            print(f"[D8] response body hex: {response.content.hex()}")
#            print(f"[D9] response body text: {response.text}")
            if not response.ok:
                return {"success": False, "message": f"MajorLogin error: {response.status_code}"}
        except Exception as e:
            return {"success": False, "message": f"MajorLogin failed: {str(e)}"}

        # Step 3: Parse MajorLogin response
        resp_enc = response.content
        cipher_resp = AES.new(key, AES.MODE_CBC, iv)
        resp_msg = MajorLogin_res_pb2.MajorLoginRes()
        parsed_data = None

        try:
            resp_dec = unpad(cipher_resp.decrypt(resp_enc), 16)
            resp_msg.ParseFromString(resp_dec)
            parsed_data = SimpleProtobuf.parse_protobuf(resp_dec)
        except Exception:
            resp_msg.ParseFromString(resp_enc)
            parsed_data = SimpleProtobuf.parse_protobuf(resp_enc)

        # Get timestamp
        field_21_value = parsed_data.get(21, None)
        if field_21_value:
            ts = Timestamp()
            ts.FromNanoseconds(field_21_value)
            timetamp = ts.seconds * 1_000_000_000 + ts.nanos
        else:
            payload = extract_jwt_payload_dict(resp_msg.account_jwt)
            exp = int(payload.get("exp", 0))
            ts = Timestamp()
            ts.FromNanoseconds(exp * 1_000_000_000)
            timetamp = ts.seconds * 1_000_000_000 + ts.nanos

        # Step 4: GetLoginData
        GetLoginData_resURL = "https://clientbp.ggpolarbear.com/GetLoginData"
        GetLoginData_res_headers = {
            'Expect': '100-continue',
            'Authorization': f'Bearer {resp_msg.account_jwt}',
            'X-Unity-Version': '2018.4.11f1',
            'X-GA': 'v1 1',
            'ReleaseVersion': 'OB53',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 11; SM-G991B Build/RP1A.200720.012)',
            'Host': 'clientbp.ggpolarbear.com',
            'Connection': 'close',
            'Accept-Encoding': 'gzip, deflate, br',
        }

        try:
            r2 = requests.post(GetLoginData_resURL, headers=GetLoginData_res_headers, data=enc_data, timeout=12, verify=False)
            if r2.status_code != 200:
                return {"success": False, "message": f"GetLoginData error: {r2.status_code}"}
        except Exception as e:
            return {"success": False, "message": f"GetLoginData failed: {str(e)}"}

        # Step 5: Parse server address
        online_ip = None
        online_port = None

        try:
            x = r2.content.hex()
            json_result = get_available_room(x)

            if json_result:
                parsed_data_login = json.loads(json_result)
                if '14' in parsed_data_login and 'data' in parsed_data_login['14']:
                    online_address = parsed_data_login['14']['data']
                    parts = online_address.rsplit(":", 1)
                    online_ip = parts[0]
                    online_port = int(parts[1])
                else:
                    return {"success": False, "message": "Could not find server address"}
            else:
                return {"success": False, "message": "Failed to parse GetLoginData response"}
        except Exception as e:
            return {"success": False, "message": f"Error processing response: {str(e)}"}

        # Step 6: Build and send packet
        payload_jwt = extract_jwt_payload_dict(resp_msg.account_jwt)
        if payload_jwt is None:
            return {"success": False, "message": "Failed to decode JWT"}

        account_id = int(payload_jwt.get("account_id", 0))
        final_token_hex = build_start_packet(
            account_id=account_id,
            timestamp=timetamp,
            jwt=resp_msg.account_jwt,
            key=resp_msg.key,
            iv=resp_msg.iv)

        if not final_token_hex:
            return {"success": False, "message": "Failed to build packet"}

        try:
            payload_bytes = bytes.fromhex(final_token_hex)
            response = send_once(online_ip, online_port, payload_bytes, recv_timeout=5.0)
            if response:
                return {"success": True,"account_id":account_id,"open_id":NEW_OPEN_ID,"platform": platform_,"data": response.hex(),"Dev": "@vhhh1"}
            else:
                return {"success": False, "message": "No response from server"}
        except Exception as e:
            return {"success": False, "message": f"Connection error: {str(e)}"}

    except Exception as e:
        return {"success": False, "message": f"Unexpected error: {str(e)}"}

# ---------------- FLASK API ENDPOINTS ---------------- #
@app.route('/ban', methods=['GET'])
def ban_endpoint():
    access_token = request.args.get('access', '')
    
    if not access_token:
        return jsonify({
            "success": False,
            "message": "access_token parameter is required"
        })
    
    result = process_login(access_token)
    return jsonify(result)

# For Vercel - WSGI compatible
def application(environ, start_response):
    return app(environ, start_response)

# For local development
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=False)
