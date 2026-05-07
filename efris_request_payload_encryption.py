from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding as pad , dsa, ec, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from cryptography.hazmat.primitives import padding

from Crypto.Hash import SHA256
import json
from Crypto.PublicKey import RSA
import base64
import json
import requests
from log_handler import LogHandler

from OpenSSL import crypto


import datetime


class EfrisHandler():

  

    def __init__(self,logger, t104_string, password, private_key_path,url):
        
        self.logger = logger
        self.auth_string = t104_string
        self.key_password = password
        self.p12_private_key_path = private_key_path
        self.efris_url = url
    
    def generateHeader(self):
        
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
       

        return headers
    
    def send_request(self, req,body):
        """Sends the REST request
        """
        headers = self.generateHeader()
       
       
        no_proxies = {'http': None,'https': None}
       
        if req == 'GET':
            response = requests.get(f'{self.efris_url}', json=body,
                                    headers=headers, verify=False,timeout=120)
        elif req == 'POST':
            response = requests.post(f'{self.efris_url}', json=body,
                                     headers=headers, verify=False,timeout=120)
        parsed_response = response
        return parsed_response
    
    def generateRequestbody(self, content, signature, tin):
    
     
        request_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        body =    {
                "data": {
                "content": content,
                "signature": signature,
                "dataDescription": {
                "codeType": "0",
                "encryptCode": "1" ,
                "zipCode": "0"
                        }
                        },
                 "globalInfo": {
                 "appId": "AP01",
                 "version": "1.1.20191201",
                 "dataExchangeId": "9230489223014123",
                 "interfaceCode": "T119",
                 "requestCode": "TP",
                 "requestTime": request_time,
                 "responseCode": "TA",
                 "userName": "admin",
                 "deviceMAC": "FFFFFFFFFFFF",
                 "deviceNo": tin+'_01',
                 "tin": tin,
                 "brn": "",
                 "taxpayerID": "1",
                 "longitude": "116.397128",
                 "latitude": "39.916527",
                 "extendField": {
                 "responseDateFormat": "dd/MM/yyyy",
                 "responseTimeFormat": "dd/MM/yyyy HH:mm:ss",
                "referenceNo": "21PL010020807"
                  }
                  },
                  "returnStateInfo": {
                  "returnCode": "",
                  "returnMessage": ""
                  }
                  }
        self.logger.info(f"Generated requestbody for: {tin}")
        return body
    
    
    def get_password(self):
        t104 = base64.b64decode(self.auth_string  )

        decoded = json.loads(t104)
        encryted_data = decoded['passowrdDes']
          
        self.logger.info(f'Password Description! :{encryted_data}')
        return encryted_data
      
        
                
     
    def generate_aes_key(self,password_description):
        with open(self.p12_private_key_path,'rb') as f:
              p12_data = f.read()
            
              private_key, certificate, ca_certificates = pkcs12.load_key_and_certificates( p12_data,self.key_password.encode('utf-8'),default_backend())
              private_key_pem = private_key.private_bytes(encoding=serialization.Encoding.PEM,format=serialization.PrivateFormat.TraditionalOpenSSL,encryption_algorithm=serialization.NoEncryption())
        
              aes_key = private_key.decrypt(base64.b64decode(password_description),pad.PKCS1v15())
              self.logger.info(f'AES KEY! :{aes_key} ')
        
        return aes_key, private_key_pem
         
    def generate_aes_key_alternative_method(self,password_description):
        
        # OpenSSL Method
        
        with open(self.p12_private_key_path,'rb') as f:
              p12_data = f.read()
              
              p12_key = crypto.load_pkcs12(p12_data,self.key_password)
              certificate = p12_key.get_certificate()
              private_key = p12_key.get_privatekey()
             
              private_key_pem = crypto.dump_privatekey(crypto.FILETYPE_PEM, private_key)
              loaded_private_key = serialization.load_pem_private_key(private_key_pem,password=None, backend=default_backend())
           
              aes_key= loaded_private_key.decrypt(base64.b64decode(password_description.encode('UTF-8')),pad.PKCS1v15())
            
            
              self.logger.info(f'AES KEY! :{aes_key} ')
        
        return aes_key, private_key_pem
         
    def encrypt_payload(self,payload, encryption_key):
        
        key = base64.b64decode(encryption_key)
    
    
        json_string = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    
      
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(json_string) + padder.finalize()

        cipher = Cipher(algorithms.AES(key), modes.ECB())
        encryptor = cipher.encryptor()
    
        encrypted_binary = encryptor.update(padded_data) + encryptor.finalize()
    
        return base64.b64encode(encrypted_binary).decode('utf-8')

        
    def generate_signature(self,data, private_key_pem):
     
       
        pkey = serialization.load_pem_private_key(private_key_pem,password=None)
       
        signature = pkey.sign(data.encode('utf-8') if isinstance(data, str) else data,pad.PKCS1v15(),  hashes.SHA1())
        

        return base64.b64encode(signature).decode('utf-8')
    
    

def main():
    """Main function to handle program logic."""
    # Instantiate the object
    logging = LogHandler.logger()
    
    taxpayer_tin= ''
    efris_url =''
    private_key_path = ''
    private_key_password = ''
    t104_interface_response = 'bGd2RGlMcFg4SStNVVcrNDcyVC9EQnNJZjNnZ2J0aWRlUT09Iiwic2lnbiI6ImFVQTdjNzN6aVZkRWJnb2JHMnZmeHF3SE1WaDJLX1hvcml3UE56OXVxREZVSkJGdjBGaGxqR3JqSTBxenlfY2J4YTVaWlRUUURRSXlfc2FKSXIyVDZQdzVBc0VibVVKX21QaDQxaEwtSG0yeVY5V2ZwdzBFYWloVGgzUFJfdjZBa1NSWEI4V0FJRnJXNF9nVHhNVFFsV3Zrem1hdEEtT2s3RzZmaUdpOE9WN2R3Y1lycktwTy16ZHdweEI3eGhVLXVnLWtHSlMwSlo5RUIxMDdyTXQyQzZmVVdCUFJ3eHZrYmhielFPdktWaS1fUzEydEd5WHEwcVBMREFkOHlORF9Sanhha0VVRkdnZ19zUVpISXFGaTEyY2VLbjBPM2Y3cTlWemFIQWVFRVh2eVVpQmg3ZHJOZXlTYUFGTWx4TnUwRk9tcE43cnlSMmhlblJmbTJabDM1QSJ9'
    payload = {"tin":"101838XXXX","ninBrn":""}
    
    start = EfrisHandler(logging,t104_interface_response,private_key_password,private_key_path,efris_url)
    
    password_desc = start.get_password()
    aes_key, private_key_pem = start.generate_aes_key(password_desc)
    
    encrypted_data = start.encrypt_payload(payload,aes_key)
    signature  = start.generate_signature(encrypted_data,private_key_pem)
    
    main_payload = start.generateRequestbody(encrypted_data,signature, taxpayer_tin)
    print( main_payload)
    response = start.send_request('POST',main_payload)
    
    print(response.json())
    
   
    
    
    

if __name__ == "__main__":
    main()