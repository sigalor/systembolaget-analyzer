# systembolaget-analyzer

Interested in analyzing the inventory of your local Systembolaget, the national Swedish alcohol store? Look no further.

## Trying it out

1. Install the required Python 3 dependencies: `pip3 install -r requirements.txt`
2. Fetch the products currently in stock for the Systembolaget stores from Stockholm (this uses the reverse-engineered API from the Systembolaget website): `./sb-fetch-all.py`
3. Generate the output Excel spreadsheets in the `output` directory, which uses the JSON files downloaded previously: `./write-excel.py`

Currently, only the file `cheapest-drinks.xlsx` is written out, where the most important column is "Price per liters and per percent alcohol". With this, you can easily find the cheapest drink in each category.

Also have a look at the JSON files in the `products` directory, as the API actually provides much more information about each product.
