import requests
import json
import sys
from requests.auth import HTTPBasicAuth
import csv
import getpass
import os
import argparse
from urllib3.exceptions import InsecureRequestWarning

#############################
#suppress certificate warning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

####################################
#add arguments --format and --create
#arg is defined in the function because of the pytest
def arg(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", "-f", nargs='?', const = 3, help = "1 or 2")
    parser.add_argument("--create", "-c", nargs='?', const = "None", help = "import from file")
    return parser.parse_args(args)


##############################################################
#check if at least one argument is provided or more than three
if len(sys.argv) == 1:
    sys.exit("Too few command-line arguments")
if len(sys.argv) > 3:
    sys.exit("Too many command-line arguments")

############################################################################################################
#Define IP address of the Cisco ISE, username and password. User must be ERS-ADMIN or Super ADMIN in the ISE

ip = input("IP: ")
username = input("Username: ")
password = getpass.getpass("Password: ")

basic = HTTPBasicAuth(username, password)
header={'Content-type':'application/json', 'Accept':'application/json'}


##############################################################
############################ MAIN ############################
##############################################################
def main():
    args = arg(sys.argv[1:])
    if args.format == "1":
        format1()
    elif args.format == "2":
        format2()
    elif args.create == "None":
        sys.exit("specify a file from which to import acl, can't be named 'None'")
    elif args.create:
        post()
    elif args.format:
        sys.exit("format must be 1 or 2")
    else:
        sys.exit("Unknown argument")
##############################################################
##############################################################


#######################################################################################################################
#it goes through list of dicts with dACL's and puts it in the file with format where all ACL statements are in one line
def format1():
    dacl = get_dacl()
    n = 0
    with open("dacl_format_1.csv", "w"):
        pass
    with open("dacl_format_1.csv", "w", newline="") as acl:
        writer = csv.DictWriter(acl, fieldnames=["id", "name", "dacl"], delimiter=";")
        for f in dacl:
            dacl = f["dacl"]
            dacl = dacl.replace("\n", ",")
            writer.writerow({"id": f["id"], "name": f["name"], "dacl": dacl})
            n = n + 1
    print(f"\n\n{n} dACL exported")
    return((f"\n\n{n} dACL exported"))
#######################################################################################################################
#it goes through list of dicts with dACL's and puts it in the file with format where every ACL statement is in new line 
def format2():
    dacl = get_dacl()
    n = 0
    with open("dacl_format_2.csv", "w") as a, open("dacl_3.csv", "w") as b:
        pass
    
    with open("dacl_3.csv", "w", newline="") as acl:
        writer = csv.DictWriter(acl, fieldnames=["id", "name", "dacl"], delimiter=";")
        for f in dacl:
            dacl = f["dacl"]
            writer.writerow({"id": f["id"], "name": f["name"], "dacl": "\n"+dacl})
            n = n + 1
        
        
    with open("dacl_3.csv") as acl:
        with open("dacl_format_2.csv", "w", newline="") as acll:
            for line in acl:
                line = line.replace('"', '')
                acll.write(line)
                
    os.remove("dacl_3.csv")
    print(f"\n\n{n} dACL exported")
    return((f"\n\n{n} dACL exported"))
#################################################################################################################
#Cisco ISE gives max 100 results per page get_pages returns number of pages. Example if 283 dACL it will return 3
def get_pages():
    p = 1
    response = requests.get("https://"+ip+":9060/ers/config/downloadableacl/?size=100", auth=basic, verify=False, headers=header)
    while True:    
        if "nextPage" in response.json()['SearchResult']:
            p = p + 1
            response = requests.get("https://"+ip+":9060/ers/config/downloadableacl/?size=100&page="+str(p), auth=basic, verify=False, headers=header)
        else:
            break
    return(p)

######################################################################################################
#it goes trough all pages and all dACL's and takes their ID, puts it in the list and returns that list
def get_dacl_id():
    pages = get_pages()
    idlist = []
    for page in range(1, pages+1):    
        response = requests.get("https://"+ip+":9060/ers/config/downloadableacl/?size=100&page="+str(page), auth=basic, verify=False, headers=header)
        for i in response.json()['SearchResult']['resources']:
            idlist.append(i['id'])
    return(idlist)

###########################################################################################################################
#it goes through list of IDs and appends dictionary with (id, name, dacl) in the list and returns that list of dictionaries
def get_dacl():
    dacl = []
    n = 0
    for i in get_dacl_id():
        n = n + 1
        response = requests.get("https://"+ip+":9060/ers/config/downloadableacl/"+i, auth=basic, verify=False, headers=header)
        print(n)
        dacl.append({"id": i, "name": response.json()['DownloadableAcl']['name'], "dacl": response.json()['DownloadableAcl']['dacl']})
    return(dacl)


###########################################################################################################################
#it imports dACL from file
#format of the file needs to be:
#id;name;acl    where statements needs to be separeted by comma
#example:
#
#      628dc830-61e8-11ee-9cd4-4e623684bf76;0test1;permit ip any host 172.23.67.53,permit ip any host 172.23.67.15,permit ip any host 172.16.0.12
#      ffd474b0-61e6-11ee-9cd4-4e623684bf76;0test2;permit ip any 10.144.30.0 255.255.255.0,permit ip any 10.145.30.0 255.255.255.0,permit ip any host 10.50.50.184
#      fff9aff0-61e6-11ee-9cd4-4e623684bf76;0test3;permit ip any host 172.20.10.13,permit ip any host 172.20.10.174,permit ip any host 172.23.67.28
#      92fc3b90-4fa7-11ed-bcb2-c2e99d5b83ed;0test4;permit tcp any host 10.0.250.56 eq 8443,permit tcp any host 10.0.250.57 eq 8443,permit tcp any any eq 80
#      e98e8d60-61b2-11ed-9d57-4ac8a117c72c;0test5;permit tcp any host 10.0.250.56 eq 8443,permit tcp any host 10.0.250.57 eq 8443,permit udp any any eq 53
#
def post():
    args = arg(sys.argv[1:])
    n = 1
    with open(args.create, "r") as file:
        for line in file:
            id,name,acl = line.split(";")
            acl = acl.replace(",", "\n")
            acl = acl.strip("\n")
            response = requests.post("https://"+ip+":9060/ers/config/downloadableacl", json = {"DownloadableAcl": {"daclType": "IP_AGNOSTIC", "dacl": acl, "name": name, "description": name}}, auth=basic, verify=False, headers=header)
            print(f"{n}  {response}")
            n = n + 1



if __name__ == "__main__":
    main()
