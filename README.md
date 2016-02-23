# jess

All scrapers have two layers, the layer which extracts data from individual
pages, and the layer which controls moving through many pages. jess is concerned
with the former. jess uses the fact that many web pages are structured around the css 
used to style them to create a web page scraping class class which is incredibly easy 
to configure and extremely flexible.

Big Picture

At a high level, the process jess uses to scrape a page is the following:
jess consumes a configuration file, which tells jess how to construct keys and values
from the html page. The configuration file is composed of rules attached to CSS selectors.
For each selector, jess grabs all of the tags satisfying to that selector and applies 
the corresponding rules to each tag to create a single key and, optionally, a value. 
These keys and values are stored in a dictionary composed of those keys and, for each key, 
a list of the values assigned to that key.

To use jess the user creates the aforementioned configuration file and
the functions that will be used to extract data from individual tags. jess will
then use these two components to extract data from the entire page. Once the user has given 
both of these parts to jess' Action class, as well as the page to be scraped, it only takes a 
single method call for jess to have the page scraped and in key value form.

