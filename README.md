# radio-parser
Use wikipedia's [lists of radio stations](https://en.wikipedia.org/wiki/Category:Lists_of_radio_stations_by_country) pages to retrieve email contact of radios. Use wikipedia's list, retrieve available radio's wiki, and find their website through radio station infobox. For each search, generate 2 csv file, a `*.template` with wikipedia search of website, and a `*.csv`, which store search result of radio websites parsing.

## Installation
***Warning:*** Use python 3.6 or higher.  
`pip install -r requirements.txt`

## Syntax
`radio_parser.py [-h] (--wiki-title title | --csv filename | --site site) [--verbose] [--workdir dir]`
Program perform a search from a wikipedia page title, a csv file (`*.template`), or a radio website.

#### Examples
`./radio_parser.py --wiki-title "List of radio stations in the United Kingdom"`
--> Perform search of "List of radio stations in the United Kingdom" page, search radios website and store resulte in `.template`,
and use this template to search radio's contact.

`./radio_parser.py --csv "List of radio stations in the United Kingddom.template"`
--> Perform search of radio's contact on already parsed wikipedia list of radio stations.
