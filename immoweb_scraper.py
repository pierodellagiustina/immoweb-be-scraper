import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from pandas.io.json import json_normalize

'''
set up: choose below parameters
'''
# select postcodes to search (add them to below list)
postcodes = [1070, 1160,1082,1000,1030,1040,1050,1140,1190,1090,1080,1081,1060,1210,1180,1170,1200,1150]

# choose which type of listings you want to search
sales = True
rental = True

# type of property to search
houses = True
apartments = True

# set min and max floor area
min_floor_area = 50
max_floor_area = 150

# set min and max number of bedrooms
min_num_bedrooms = 1
max_num_bedrooms = 3

# set the number of pages of results you want to scrape (if in doubt, leave unchanged)
max_pages = 1000

'''
Scraper
'''
property_type = ''
if houses & apartments:
    property_type = 'house-and-apartment'
elif houses:
    property_type = 'house'
elif apartments:
    property_type = 'apartment'

transaction_types = []
if sales:
    transaction_types.append('for-sale')
if rental:
    transaction_types.append('for-rent')

# initialize results df
if sales:
    outp_sales = pd.DataFrame()
if rental:
    outp_rental = pd.DataFrame()

for tt in transaction_types:
    print('Processing properties ', tt)

    for pc in postcodes:

        pc = str(pc)
        print('Processing postcode ' + pc)

        for pg in range(1, max_pages):

            if pg % 5 == 0:
                print(pg)

            pg = str(pg)
            min_floor_area = str(min_floor_area)
            max_floor_area = str(max_floor_area)
            min_num_bedrooms = str(min_num_bedrooms)
            max_num_bedrooms = str(max_num_bedrooms)

            # create url
            url = f'https://www.immoweb.be/en/search/{property_type}/{tt}/st-gilles/{pc}?countries=BE&minBedroomCount={min_num_bedrooms}&maxBedroomCount={max_num_bedrooms}&maxSurface={max_floor_area}&minSurface={min_floor_area}&page={pg}&orderBy=relevance'

            # request url and format it
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'html.parser')

            # extract bits I need
            search_res = soup.find('iw-search')
            res_dic = dict(search_res.attrs)

            # get json string from ':results' and put it into a dictionary
            res_json = json.loads(res_dic[':results'])

            # if the page is empty, do not continue running
            if len(res_json) == 0:
                print('Total number of pages processed ', str(int(pg) - 1))
                break

            # loop through the items in the page
            for i in range(len(res_json)):

                elem = res_json[i]

                # keep the keys i'm interested in
                elem_subset = {k: elem[k] for k in ('id', 'flags', 'property', 'transaction', 'price')}

                # flatten the dictionary and append it to df
                df_elem = json_normalize(elem_subset, sep='_')

                if tt == 'for-sale':
                    outp_sales = outp_sales.append(df_elem, ignore_index=True, sort=False)
                elif tt == 'for-rent':
                    outp_rental = outp_rental.append(df_elem, ignore_index=True, sort=False)

# cleanse the dataset - sales first
if sales:
    outp_sales_cleansed = outp_sales.copy()

    # keep standard sales only (get rid of group sales and similar)
    outp_sales_cleansed = outp_sales_cleansed[outp_sales_cleansed.price_type == 'residential_sale']

    # get subset of cols
    cols_subset_sales = [
        "id",
        "property_location_locality",
        "property_location_postalCode",
        "property_location_street",
        "property_location_number",
        "property_location_latitude",
        "property_location_longitude",
        "price_mainValue",
        "property_bedroomCount",
        "property_netHabitableSurface",
        "property_roomCount",
        'property_type'
    ]

    outp_sales_cleansed = outp_sales_cleansed[cols_subset_sales]

    # set new col names
    outp_sales_cleansed.columns = [
        'id',
        'locality',
        'postcode',
        'street',
        'number',
        'lat',
        'long',
        'price',
        'bedroom_count',
        'floor_area',
        'room_count',
        'property_type'
    ]

    # create new cols
    outp_sales_cleansed['price_per_sqm'] = outp_sales_cleansed['price'].astype(
        'float') / outp_sales_cleansed.floor_area.astype('float')
    outp_sales_cleansed['price_per_bedroom'] = outp_sales_cleansed['price'].astype(
        'float') / outp_sales_cleansed.bedroom_count.astype('float')
    outp_sales_cleansed['price_per_room'] = outp_sales_cleansed['price'].astype(
        'float') / outp_sales_cleansed.room_count.astype('float')  # poorly populated

# cleanse rental results
if rental:
    outp_rental_cleansed = outp_rental.copy()

    # get rid of non-standard rental values
    outp_rental_cleansed = outp_rental_cleansed[outp_rental_cleansed.price_type == 'residential_monthly_rent']

    # get subset of cols
    cols_subset_rental = [
        "id",
        "property_location_locality",
        "property_location_postalCode",
        "property_location_street",
        "property_location_number",
        "property_location_latitude",
        "property_location_longitude",
        "transaction_rental_monthlyRentalPrice",
        'transaction_rental_monthlyRentalCosts',
        "property_bedroomCount",
        "property_netHabitableSurface",
        "property_roomCount",
    ]

    outp_rental_cleansed = outp_rental_cleansed[cols_subset_rental]

    # rename columns
    cols_rename_rental = [
        'id',
        'locality',
        'postcode',
        'street',
        'number',
        'lat',
        'long',
        'rent',
        'costs',
        'bedroom_count',
        'floor_area',
        'room_count'
    ]

    outp_rental_cleansed.columns = cols_rename_rental

    # add new cols
    outp_rental_cleansed['rent_incl_costs'] = outp_rental_cleansed.rent.astype(
        'float') + outp_rental_cleansed.costs.astype('float').fillna(0)
    outp_rental_cleansed['rent_per_bedroom'] = outp_rental_cleansed.rent.astype(
        'float') / outp_rental_cleansed.bedroom_count.astype('float')
    outp_rental_cleansed['rent_incl_costs_per_bedroom'] = outp_rental_cleansed.rent_incl_costs.astype(
        'float') / outp_rental_cleansed.bedroom_count.astype('float')

# write to csv
if sales:
    outp_sales_cleansed.to_csv('outp_sales_cleansed.csv')

if rental:
    outp_rental_cleansed.to_csv('outp_rental_cleansed.csv')