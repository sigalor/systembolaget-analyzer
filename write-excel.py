#!/usr/bin/env python3

import json
import xlsxwriter
import datetime

meta = {
    "Generated at": datetime.datetime.utcnow().isoformat() + "Z",
    "GitHub repository": "https://github.com/sigalor/systembolaget-analyzer"
}

stores = {
    "0102": ["Karlaplan 13", "115 20 Stockholm"],
    "0104": ["Östermalmstorg 47", "114 39 Stockholm"],
    "0106": ["Karlavägen 100A", "115 26 Stockholm"],
    "0110": ["Hötorgshallen", "111 57 Stockholm"],
    "0113": ["Drottninggatan 45", "111 21 Stockholm"],
    "0114": ["Norrlandsgatan 3", "111 47 Stockholm"],
    "0132": ["Rålambsvägen 7-9", "112 59 Stockholm"],
    "0133": ["Kungsholmstorg 11A", "112 21 Stockholm"],
    "0137": ["Fleminggatan 56", "112 45 Stockholm"],
    "0138": ["Odengatan 92", "113 22 Stockholm"],
    "0140": ["Solnavägen 2b", "113 65 Stockholm"],
    "0143": ["Odengatan 58", "113 22 Stockholm"],
    "0144": ["Birger Jarlsgatan 84", "114 20 Stockholm"],
    "0145": ["Sveavägen 66", "111 34 Stockholm"],
    "0146": ["Vasagatan 25", "111 20 Stockholm"],
    "0166": ["Medborgarplatsen 3", "118 26 Stockholm"],
    "0167": ["Folkungagatan 101", "116 30 Stockholm"],
    "0174": ["Långholmsgatan 21A", "117 33 Stockholm"]
}

workbook = xlsxwriter.Workbook('output/cheapest-drinks.xlsx')
heading = workbook.add_format({'bold': True, 'font_size': 20})
bold = workbook.add_format({'bold': True})

general_ws = workbook.add_worksheet("Overview")
general_ws.set_row(0, 30)
general_ws.set_column(0, 0, 40)
general_ws.set_column(1, 1, 60)
general_ws.write(0, 0, "Overview", heading)
for i, (k, v) in enumerate(meta.items()):
  general_ws.write(i+2, 0, k)
  general_ws.write(i+2, 1, v)

links_start = len(meta.items()) + 4
general_ws.set_row(links_start, 30)
general_ws.write(
    links_start, 0, "Links to worksheets of individual stores", heading)
for i, (k, v) in enumerate(stores.items()):
  general_ws.write_url(links_start + 2 + i, 0,
                       f"internal:'{v[0]}'!A1", string=", ".join(v))


for store_id in stores.keys():
  with open("products/products-" + store_id + ".json", "r") as f:
    products = [p for p in list(json.loads(
        f.read()).values()) if p["alcoholPercentage"] > 0]

  products.sort(key=lambda p: p["price"] /
                (p["volume"] * p["alcoholPercentage"]))

  worksheet = workbook.add_worksheet(stores[store_id][0])
  worksheet.set_row(0, 30)
  for col_no, width in enumerate([13, 18, 15, 25, 35, 37, 12, 18, 15]):
    worksheet.set_column(col_no, col_no, width)

  worksheet.write(0, 0, ", ".join(stores[store_id]), heading)
  for col_no, head_str in enumerate(["Product ID", "Product number", "Type (1)", "Type (2)", "Product name", "Price per liter per percent alcohol (SEK)", "Price (SEK)", "Alcohol percentage", "Volume (ml)"]):
    worksheet.write(2, col_no, head_str, bold)

  for row_no, p in enumerate(products):
    name = p["productNameBold"]
    if p["productNameThin"] is not None:
      name += " – " + p["productNameThin"]

    for col_no, cell_str in enumerate([p["productId"], p["productNumber"], p["categoryLevel1"], p["categoryLevel2"], name, p["price"] / (p["volume"] / 1000) / p["alcoholPercentage"], p["price"], p["alcoholPercentage"], p["volume"]]):
      worksheet.write(row_no + 3, col_no, cell_str)

workbook.close()
