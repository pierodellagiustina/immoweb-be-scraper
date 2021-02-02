# Immoweb Scraper

Simple no-frills script to scrape immoweb.be - nothing fancy, suggestions are more than welcome.


### Parameters

- Currently floor area and number of bedrooms as search criteria (`min_floor_area`, `max_floor_area`, `min_num_bedrooms`, `max_num_bedrooms`). Could easily adjust the URL to accommodate extra filters.
- `max_pages` sets maximum number of result pages that will be scraped for every search. If in doubt, choose a high number


### Notes

The municipality name in the URL (eg `.../st-gilles/...`) does not seem to matter - what matters is the postcode (postal code). As long as the postcode is set appropriately, the URL will return the right results.

Finally, made this for *personal use* on a *limited number of listings* - scraped data should not be used for commercial purposes. As always, please be sensible!
 
