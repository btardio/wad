from googleads import adwords
from time import sleep
from math import ceil
#from wad import settings

#SLEEP_AFTER_API_CALL = 5
SLEEP_AFTER_API_CALL = 1

def list_from_query ( client, service, query ):

  offset = 0

  result_set = []

  PAGE_SIZE = 100

  page = service.query ( query + ' LIMIT %s, %s' % (offset, PAGE_SIZE))
  sleep ( SLEEP_AFTER_API_CALL ) # after a query always have a sleep

  # DEBUG print
  #print ( page )

  # return an empty list if totalNumEntries is not in page
  if ( 'totalNumEntries' not in page ): return []

  # determines number of pages
  number_of_pages = ceil ( (page.totalNumEntries)  / (PAGE_SIZE) )

  # if the query returned a blank set return []
  if ( page.totalNumEntries == 0 ): return []

  # iterates first page, appending results to result_set
  for itemindex in range ( 0, len ( page.entries ) ):
    result_set.append(page.entries[itemindex])

  # if the first query returns entries that exceed one page iterate through
  # subsequent pages
  for pageindex in range ( 0, int(number_of_pages) ):

    # increments the offset by PAGE_SIZE in preparation for the query
    offset += PAGE_SIZE

    page = service.query ( query + ' LIMIT %s, %s' % (offset, PAGE_SIZE))
    sleep ( SLEEP_AFTER_API_CALL ) # after a query always put in a sleep

    # if fixes : AttributeError: 'BudgetPage' object has no attribute 'entries'
    # the only time entries is not in page is if totalnumentries / page_size is divisible without remainder
    if hasattr ( page, 'entries' ):

      # iterates the result of the query using len ( page.entries ) and
      # appends results to result_set
      for itemindex in range ( 0, len ( page.entries ) ):
        result_set.append(page.entries[itemindex])

  return ( result_set )










