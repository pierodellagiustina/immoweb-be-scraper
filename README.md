# immoweb_be_scraper

Simple no-frills script to scrape immoweb.be - nothing fancy, suggestions are more than welcome.


### Parameters

- Currently using min and max floor area (`min_floor_area` and `max_floor_area`) as search filters for sales, and min and max num of bedrooms (`min_num_bedrooms` and `max_num_bedrooms`) for rental properties.
Could easily adjust the URL to accommodate extra filters.
- `max_pages` sets maximum number of result pages that will be scraped for every search. If in doubt, choose a high number


### Notes

The municipality name in the URL (eg `.../st-gilles/...`) does not seem to matter - what matters is the postcode (postal code). As long as the postcode is set appropriately, the URL will return the right results.

 
