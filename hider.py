import argparse 
import getpass
import pyaes
import hashlib
import pathlib


parser=argparse.ArgumentParser()
parser.add_argument("cover",help="cover file png or jpg",metavar="[cover]")
parser.add_argument("hidden",metavar="[hidden]",help="file that you want to hide ",nargs='?')
parser.add_argument("-o",'--output',help="output file",metavar='')
parser.add_argument("-d",action="store_true",help="fetch data from cover file")
args=parser.parse_args()


def image_process(image_type):
    if args.d:
       
        password=getpass.getpass("enter your passkey:")
        aes = pyaes.AESModeOfOperationCTR(hashlib.sha256(password.encode()).digest())
        if image_type=='jpg':
            data=filedata[filedata.find(b'\xff\xd9')+2:]
            data=aes.decrypt(bytes(data))
            file_name=data[data.find(b'\xff'*8+b'\xfa'*8+b'\xdf'*8+b'\xfd'*8)+32:]
            data=data[:data.find(b'\xff'*8+b'\xfa'*8+b'\xdf'*8+b'\xfd'*8)]
            with open(file_name.decode(),'wb') as plain:
                plain.write(data)
        if image_type=='png':
            data=filedata[filedata.find(b'\x49\x45\x4e\x44\xae\x42\x60\x82')+8:]
            data=aes.decrypt(bytes(data))
            file_name=data[data.find(b'\xff'*8+b'\xfa'*8+b'\xdf'*8+b'\xfd'*8)+32:]
            data=data[:data.find(b'\xff'*8+b'\xfa'*8+b'\xdf'*8+b'\xfd'*8)]
            with open(file_name.decode(),'wb') as plain:
                plain.write(data)



    else:
        if not args.hidden :
            print("hidden file needed!")
        else:
            password=getpass.getpass("enter your passkey:")
            re_password=getpass.getpass("re_enter your password:")
            if password==re_password:
                aes = pyaes.AESModeOfOperationCTR(hashlib.sha256(password.encode()).digest())
                with open(args.hidden,"rb")as hidden:
                    data=hidden.read()
                    data=data+b'\xff'*8+b'\xfa'*8+b'\xdf'*8+b'\xfd'*8+pathlib.Path(args.hidden).name.encode()
                    data=aes.encrypt(data)
                    if args.output:
                        with open(args.output,'wb') as wrt:
                            wrt.write(filedata+data)
                    else:
                        with open(f'output.{image_type}','wb') as wrt:
                            wrt.write(filedata+data)
            else:
                print("passwords do not match!")

if __name__ == "__main__":        
    try:
        with open(args.cover,'rb+') as file:
            filedata=file.read()
            file.seek(0,0)
            begin=file.read(8)
            file.seek(-8,2)
            end=file.read(8)
            if b'\xff\xd9' in filedata and b'\xff\xd8\xff' in begin:
                image_process('jpg')
            elif  b'\x49\x45\x4e\x44\xae\x42\x60\x82' in filedata and b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a' in begin:
                image_process('png')
            else:
                print("cover file must be png or jpg")    
    except Exception as er:
        print(str(er))