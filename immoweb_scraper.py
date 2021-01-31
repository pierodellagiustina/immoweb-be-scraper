import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from pandas.io.json import json_normalize

# initialize results df
outp_capital = pd.DataFrame()
outp_rental = pd.DataFrame()

# select postcodes
postcodes = [1070, 1160,1082,1000,1030,1040,1050,1140,1190,1090,1080,1081,1060,1210,1180,1170,1200,1150]

# select max number of pages to scrape (if in doubt, set it to a high number)
max_pages = 1000 

# for sales, set min and max floor area
min_floor_area = 50
max_floor_area = 150

# for rental properties, set min and max number of bedrooms
min_num_bedrooms = 1
max_num_bedrooms = 3

# comment out if not interested in either one
transaction_types = ['for_sale', 'for_rent']   

# loop through selected transaction types
for tt in transaction_types:
    print('Processing properties ',tt)
    
    # loop through postcodes
    for pc in postcodes:

        pc=str(pc)
        print('Processing postcode '+pc)

        # loop through pages
        for pg in range(1,max_pages):

            pg = str(pg)
            min_floor_area = str(min_floor_area)
            max_floor_area = str(max_floor_area)
            min_num_bedrooms = str(min_num_bedrooms)
            max_num_bedrooms = str(max_num_bedrooms)

            # create url
            if tt=='for_sale':
                url = f'https://www.immoweb.be/en/search/apartment/for_sale/st-gilles/{pc}?countries=BE&maxSurface={max_floor_area}&minSurface={min_floor_area}&page={pg}&orderBy=relevance'
            elif tt=='for_rent':
                url = f'https://www.immoweb.be/en/search/apartment/for-rent/woluwe-st-pierre/{pc}?countries=BE&minBedroomCount={min_num_bedrooms}&maxBedroomCount={max_num_bedrooms}&page={pg}&orderBy=relevance'

            # request url and extraxt soup
            r = requests.get(url)
            soup = BeautifulSoup(r.text,'html.parser')

            # extract bits I need
            search_res = soup.find('iw-search')
            res_dic = dict(search_res.attrs)
            res_json = json.loads(res_dic[':results'])

            # if the page is empty, do not continue running
            if len(res_json)==0:
                print('Total number of pages processed ',str(int(pg)-1))
                break

            # loop through items in page
            for i in range(len(res_json)):

                elem = res_json[i]

                # keep the keys i'm interested in 
                elem_subset = {k: elem[k] for k in ('id','flags','property','transaction','price')}

                # flatten the dictionary and append it to df
                df_elem = json_normalize(elem_subset, sep='_')
                
                if tt=='for_sale':
                    outp_capital = outp_capital.append(df_elem, ignore_index=True)
                elif tt=='for_rent':
                    outp_rental = outp_rental.append(df_elem, ignore_index=True)


# done, results are in outp_capital and outp_rental - go and do some cool analysis with it
