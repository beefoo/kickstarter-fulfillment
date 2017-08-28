# -*- coding: utf-8 -*-

# Convert Kickstarter exported .csv files to Amazon FBA's flat file fulfillment order request .tsv file
#   python ks2fba.py -in input/2017-08-26-1049 -out output/2017-08-26.tsv -prepend KSCCCB1

import argparse
import csv
import io
import os
from pprint import pprint
import sys

# input
parser = argparse.ArgumentParser()
parser.add_argument('-in', dest="INPUT_DIR", default="input/kickstarter-csv-folder", help="Input directory that contains downloaded Kickstarter .csv files")
parser.add_argument('-defaults', dest="INPUT_DEFAULTS", default="input/defaults.csv", help="Input .csv file that contains default order values")
parser.add_argument('-quantities', dest="INPUT_QUANTITIES", default="input/reward_quantities.csv", help="Input .csv file that contains reward quantity information")
parser.add_argument('-prepend', dest="PREPEND_ID", default="KICKSTARTER", help="String that will be prepended to order ID")
parser.add_argument('-out', dest="OUTPUT_FILE", default="output/fba_order_request.tsv", help=".tsv output file")

args = parser.parse_args()

HEADERS = [
    {"name": "MerchantFulfillmentOrderID", "map": "Backer Number", "prepend": args.PREPEND_ID},
    {"name": "DisplayableOrderID", "map": "Backer Number", "prepend": args.PREPEND_ID},
    {"name": "DisplayableOrderDate"},
    {"name": "MerchantSKU"},
    {"name": "Quantity", "map": "Reward ID"},
    {"name": "MerchantFulfillmentOrderItemID"},
    {"name": "GiftMessage"},
    {"name": "DisplayableComment"},
    {"name": "PerUnitDeclaredValue"},
    {"name": "DisplayableOrderComment"},
    {"name": "DeliverySLA"},
    {"name": "AddressName", "map": "Shipping Name"},
    {"name": "AddressFieldOne", "map": "Shipping Address 1"},
    {"name": "AddressFieldTwo", "map": "Shipping Address 2"},
    {"name": "AddressFieldThree"},
    {"name": "AddressCity", "map": "Shipping City"},
    {"name": "AddressCountryCode", "map": "Shipping Country Code"},
    {"name": "AddressStateOrRegion", "map": "Shipping State"},
    {"name": "AddressPostalCode", "map": "Shipping Postal Code"},
    {"name": "AddressPhoneNumber", "map": "Shipping Phone Number"},
    {"name": "NotificationEmail", "map": "Email"},
    {"name": "FulfillmentAction"},
    {"name": "MarketplaceID"}
]

def readCSV(filename):
    rows = []
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            s = f.read().decode("utf-8-sig").encode("utf-8")
            reader = csv.DictReader(s.splitlines(), skipinitialspace=True)
            rows = list(reader)
    return rows

defaultData = readCSV(args.INPUT_DEFAULTS)
defaultData = defaultData[0]
quantityData = readCSV(args.INPUT_QUANTITIES)
quantityLookup = {d["Reward ID"]: int(d["Quantity"]) for d in quantityData}

outputRows = []
for f in os.listdir(args.INPUT_DIR):
    if f.endswith(".csv") and not f.startswith("No reward"):
        filepath = os.path.join(args.INPUT_DIR, f)
        data = readCSV(filepath)

        for d in data:

            if len(d["Rewards Sent?"]) > 0:
                continue

            row = []
            for h in HEADERS:
                value = defaultData[h["name"]]

                # mapped values
                if "map" in h:
                    key = h["map"]
                    if len(d[key]):
                        value = d[key]
                        if "prepend" in h:
                            value = h["prepend"] + value

                if h["name"]=="PerUnitDeclaredValue" and d["Shipping Country Code"]=="US":
                    value = ""

                if h["name"]=="AddressPostalCode" and d["Shipping Country Code"]=="US" and len(value) < 5:
                    value = value.zfill(5)

                # quantity lookup
                if h["name"]=="Quantity":
                    value = quantityLookup[value]


                row.append(value)
            outputRows.append(row)

with open(args.OUTPUT_FILE, 'wb') as f:
    writer = csv.writer(f, delimiter="\t", dialect='excel')
    writer.writerow([h["name"] for h in HEADERS])
    writer.writerows(r for r in outputRows)
    print "Wrote %s rows to %s" % (len(outputRows), args.OUTPUT_FILE)
