#!/usr/bin/env python

from os import path, chdir, system
from json import loads
from requests import get
from filecmp import cmp
from shutil import copyfile
from sys import argv, exit
from time import sleep
import logging

##### Configurations #####

# Cloudflare's API config
zoneid = "888f3b55f64e40afdbed4f813d0fb3a8_ChangeMe"
zone_api_key = "AUhXt7YtkLofzPE8AAaoQ8zZPR34JcioDE_UsxE3_ChangeMe"

# User defined A records to be replaced or Empty
replace_a_records = {"a.example.com": "111.111.111.111"}

# User defined CNAME records to be replaced or Empty
replace_cname_records = {"from.example.com": "to.example.com"}

# pihole's files location. Change for your pihole installation
pihole_custom_list_path = "/root/pihole/config/custom.list"
pihole_05_pihole_custom_cname_conf_path = "/root/pihole/dnsmasq.d/05-pihole-custom-cname.conf"

##########


# Set files to be used
custom_list = "custom.list"
custom_cname = "05-pihole-custom-cname.conf"

# Change the current directory to the location of the script
# example: how to run the script: /Users/fire1ce/.pyenv/versions/local-dns-cloudflare-to-pihole/bin/python ./server.py
chdir(path.dirname(argv[0]))

# Clears the log file before each run
open("output.log", "w").close()

# logging all the errors and other messages to the log file
logFormatter = logging.Formatter("%(asctime)s %(message)s")
logger = logging.getLogger()

fileHandler = logging.FileHandler("{0}/{1}.log".format(".", "output"))
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)
logger.setLevel(logging.DEBUG)

logger.debug("Starting...")

# Get cloudflare records from api depending on the record type
def get_records_from_cloudflare(record_type):
    cloudflare_api_url = f"https://api.cloudflare.com/client/v4/zones/{zoneid}/dns_records?type={record_type}&per_page=5000"
    cloudflare_api_headers = {
        "Authorization": f"Bearer {zone_api_key}",
        "Content-Type": "application/json",
    }
    api_response = get(cloudflare_api_url, headers=cloudflare_api_headers)
    api_response_json = loads(api_response.text)
    if not api_response_json["success"]:
        logger.error(
            "Error! Something went wrong with Cloudflare API: {0}".format(
                api_response_json["errors"]
            )
        )
        exit(1)
    logger.debug("==> Got " + record_type + " records from Cloudflare API")
    return api_response_json["result"]


# Get all the A records from Cloudflare API
# replace the IP address with the one from the dictionary and save it to the file
cloudflare_records = get_records_from_cloudflare("A")
with open(custom_list, "w", encoding="utf-8") as file:
    for record in cloudflare_records:
        if record["name"] in replace_a_records:
            record["content"] = replace_a_records[record["name"]]
        print(record["content"], record["name"], file=file)
logger.debug("==> Saved A records to custom.list")

# Get all the CNAME records from Cloudflare API
# replace the CNAME records with the one from the dictionary and save it to the file
cloudflare_records = get_records_from_cloudflare("CNAME")
with open(custom_cname, "w", encoding="utf-8") as file:
    for record in cloudflare_records:
        if record["name"] in replace_cname_records:
            record["content"] = replace_cname_records[record["name"]]
        print("cname=" + record["name"] + "," + record["content"], file=file)
logger.debug("==> Saved CNAME records to " + custom_cname)


pihole_need_restart = False

# if the custom.list file is different from the one in the pihole folder then
# copy it to the pihole folder and restart the pihole service
if cmp(custom_list, pihole_custom_list_path) is False:
    logger.debug("found difference in custom.list")
    copyfile(custom_list, pihole_custom_list_path)
    logger.debug("==> Copied " + custom_list + " to " + pihole_custom_list_path)
    pihole_need_restart = True

# if the custom-cname.conf file is different from the one in the pihole folder then
# copy it to the pihole folder and restart the pihole service
if cmp(custom_cname, pihole_05_pihole_custom_cname_conf_path) is False:
    logger.debug("found difference in " + custom_cname)
    copyfile(custom_cname, pihole_05_pihole_custom_cname_conf_path)
    logger.debug("==> Copied " + custom_cname + " to " + pihole_05_pihole_custom_cname_conf_path)
    pihole_need_restart = True

# if the pihole service needs to be restarted then restart it
if pihole_need_restart:
    sleep(5)
    logger.debug("==> Flushing pihole's DNS cache ")
    system("/usr/bin/docker exec -t pihole /usr/local/bin/pihole restartdns")
    logger.debug("==> Done")
else:
    logger.debug("==> No changes found in custom.list or 05-pihole-custom-cname.conf")

exit()
