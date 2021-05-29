#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 18:25:53 2020

@author: xdvora3d
"""

import socket
import sys
import signal
from urllib.parse import urlparse, parse_qs


def ret400badreq():
    return 'HTTP/1.1 400 Bad Request\r\n\r\n'

def ret404notfound():
    return 'HTTP/1.1 404 Not Found\r\n\r\n'


def typeA(question):
    message = 'HTTP/1.1 200 OK\r\n\r\n'
    try:
        answer = socket.gethostbyname(question)
        if answer == question:
            message = ret400badreq()
        else:
            message += question + ":A" + "=" + answer + "\n"
    except (socket.gaierror, socket.herror):
         message = ret404notfound()
    except:
         message = ret400badreq()
    finally:
        return message


def typePTR(question):
    message = 'HTTP/1.1 200 OK\r\n\r\n'
    try:
        socket.inet_aton(question)
        answer = socket.gethostbyaddr(question)[0]
        if answer == question:
            message = ret400badreq()
        else:
            message += question + ":PTR" + "=" + answer + "\n"
    except (socket.gaierror, socket.herror):
        message = ret404notfound()
    except:
        message = ret400badreq()
    finally:
        return message




def signal_handler(sig, frame):
    print ("\n")
    print ("Ukoncuji server...")
    sys.exit(0)
    
signal.signal(signal.SIGINT, signal_handler)




#print (str(sys.argv))
try:
    int(sys.argv[1])
except:
    print ("Spatne zadany port")
    sys.exit(1)
    
if (len(sys.argv) != 2 or int(sys.argv[1]) < 0 or int(sys.argv[1]) > 65535):
    print ("Spatne zadany port")
    sys.exit(1)



PORT = int(sys.argv[1])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("", PORT))
s.listen()

    

while True:
    conn, addr = s.accept()
    print("Pripojen", addr)
    data = conn.recv(1024)
    string = data.decode('utf-8')
    o = urlparse(string)
    if "GET " == string[:4]:
        if "/resolve" != string[4:12]:
            message = ret400badreq()
        else:
            try:
                arr = parse_qs(o.query)
                question = arr["name"]
                arr = arr["type"]
                arr = arr[0].split("\r\n")
                arr = arr[0].split(" ")
                typ = arr[0]
                if arr[1] != "HTTP/1.1":
                    raise Exception
            except:
                message = ret400badreq()
            else:
                if typ == "A":
                    message = typeA(question[0])
                elif typ == "PTR":
                    message = typePTR(question[0])
                else:
                    message = ret400badreq()
                          
    elif "POST" == string[:4]:
        if "/dns-query HTTP/1.1" != string[5:24]:
            message = ret400badreq()
        else:
            message = ""
            try:
                arr = o.path
                arr = arr.split("\r\n\r\n")
                arr = arr[1]
                arr = arr.split("\n")
                arr.pop()
            except:
                message = ret400badreq()
            else:
                if arr[len(arr)-1] == "":
                    arr.pop()
                message = 'HTTP/1.1 200 OK\r\n\r\n'
                for question in arr:
                    if not question.strip():
                        message = ret400badreq()
                        break
                    try:
                        question = question.split(":")
                        question[1] = question[1].strip()
                        question[0] = question[0].strip()
                    except:
                        message = ret400badreq()
                        break
                    if question[1] == "A":
                        try:
                            answer = socket.gethostbyname(question[0])
                            if answer == question[0]:
                                message = ret400badreq()
                                break
                            else:
                                message += question[0] + ":"+ question[1] + "=" + answer + "\n"
                        except (socket.gaierror, socket.herror):
                            pass
                        except:
                             message = ret400badreq()
                             break
                            
                    elif question[1] == "PTR":
                        try:
                            socket.inet_aton(question[0])
                            answer = socket.gethostbyaddr(question[0])[0]
                            if answer == question[0]:
                                message = ret400badreq()
                                break
                            else:
                                message += question[0] + ":"+ question[1] + "=" + answer + "\n"
                        except (socket.gaierror, socket.herror):
                            pass
                        except:
                            message = ret400badreq()
                            break
                            
                    else:
                        message = ret400badreq()
                        break
    else:
        message = 'HTTP/1.1 405 Method Not Allowed\r\n\r\n'
     
    conn.sendall(message.encode('utf-8'))
    conn.close()
        
        
            
            
            
