#!/usr/bin/env python3

import sys
import os
import requests
import json
import re
import signal
import logging
import datetime


logging.Formatter.formatTime = (lambda self, record, datefmt: datetime.datetime.fromtimestamp(
    record.created, datetime.timezone.utc).astimezone().isoformat())  # from https://stackoverflow.com/a/58777937
logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] %(levelname)-8s   %(message)s')


class DelayedKeyboardInterrupt:  # from https://stackoverflow.com/a/21919644
  def __enter__(self):
    self.signal_received = False
    self.old_handler = signal.signal(signal.SIGINT, self.handler)

  def handler(self, sig, frame):
    self.signal_received = (sig, frame)
    logging.debug('SIGINT received. Delaying KeyboardInterrupt.')

  def __exit__(self, type, value, traceback):
    signal.signal(signal.SIGINT, self.old_handler)
    if self.signal_received:
      self.old_handler(*self.signal_received)


products = None


def add_products(new_products):
  global products, output_file

  if products is None:
    if os.path.isfile(output_file):
      with open(output_file, "r") as f:
        products = json.loads(f.read())
    else:
      products = {}

  for p in new_products:
    internal_id = p["productId"] + "+" + p["productNumber"]
    if internal_id in products:
      logging.warning(f"Detected duplicate internal id {internal_id}")
    products[internal_id] = p
  with DelayedKeyboardInterrupt():
    with open(output_file, "w") as f:
      f.write(json.dumps(products, separators=(',', ':')))


homepage = requests.get("https://www.systembolaget.se",
                        headers={"User-Agent": "xxx"}).text  # need to use different User-Agent to prevent 403 error
print(homepage)
settings_url = re.search(
    '(?<=\<script rel\="preload" src\=")(https\:\/\/cdn\.systembolaget\.se\/appsettings\.[a-z0-9-]+\.js)', homepage).group(0)
settings = json.loads(requests.get(settings_url).text[35:-1])

api_root = settings["apiGatewayEndpoint"] + settings["apiGatewayVersion"]
headers = {"Ocp-Apim-Subscription-Key": settings["ocpApimSubscriptionKey"]}


def get_json(url, params):  # from https://github.com/pontuspalmenas/ctbolaget/blob/master/query_sb_api.py#L13
  global headers
  resp = requests.get(url, headers=headers, params=params)
  if resp.status_code == 200:
    return resp.json()
  else:
    resp_json = resp.json()
    logging.error(
        f"Request to {url} failed: {resp.status_code} {resp.reason}: {', '.join(resp_json['error'])}\n{resp_json['stackTrace']}")
    sys.exit()


def get_all_products(params):
  page = 1
  while page > 0:
    params["page"] = page
    data = get_json(f"{api_root}/productsearch/search", params)
    add_products(data["products"])
    logging.info(f"Fetched {json.dumps(params)}")
    page = data["metadata"]["nextPage"]


# need to get these one after another, because the maximum value for the "page" parameter is 666, otherwise we get HTTP 500 Internal Server Error
# luckily the API seems to have no rate limiting
'''
output_file = "products-global.json"
get_all_products({"categoryLevel1": "Öl"})
get_all_products({"categoryLevel1": "Vin", "categoryLevel2": "Rött"})
get_all_products({"categoryLevel1": "Vin", "categoryLevel2": "Vitt"})
get_all_products({"categoryLevel1": "Vin", "categoryLevel2": "Mousserande"})
get_all_products({"categoryLevel1": "Vin", "categoryLevel2": "Rosé"})
get_all_products({"categoryLevel1": "Vin", "categoryLevel2": "Vinlåda"})
get_all_products({"categoryLevel1": "Vin", "categoryLevel2": "Starkvin"})
get_all_products(
    {"categoryLevel1": "Vin", "categoryLevel2": "Smaksatt vin & fruktvin"})
get_all_products({"categoryLevel1": "Vin", "categoryLevel2": "Sake"})
get_all_products(
    {"categoryLevel1": "Vin", "categoryLevel2": "Glögg och Glühwein"})
get_all_products({"categoryLevel1": "Vin", "categoryLevel2": "Vermouth"})
get_all_products({"categoryLevel1": "Vin", "categoryLevel2": "Aperitif"})
get_all_products({"categoryLevel1": "Sprit"})
get_all_products({"categoryLevel1": "Cider & blanddrycker"})
get_all_products({"categoryLevel1": "Alkoholfritt"})
'''

for store_id in ["0102", "0104", "0106", "0110", "0113", "0114", "0132", "0133", "0137", "0138", "0140", "0143", "0144", "0145", "0146", "0166", "0167", "0174"]:
  output_file = "products/products-" + store_id + ".json"
  get_all_products({"storeId": store_id, "isInStoreAssortmentSearch": "true"})
