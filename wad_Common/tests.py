# todo : query fails sporadically, 0 len list error, write a test



#======================================================================
#ERROR: test_t010_wad_Campaign_list_campaigns (wad_Campaign.tests.wad_Campaign_testcases)
#----------------------------------------------------------------------
#Traceback (most recent call last):
  #File "/home/btardio/projects/adwords/django-wad-git-master/wad/wad_Campaign/tests.py", line 106, in test_t010_wad_Campaign_list_campaigns
    #campaigns = Campaign.listcampaigns( client )
  #File "/home/btardio/projects/adwords/django-wad-git-master/wad/wad_Campaign/models.py", line 92, in listcampaigns
    #rslts = list_from_query ( client, service, querytext )
  #File "/home/btardio/projects/adwords/django-wad-git-master/wad/wad_Common/query.py", line 24, in list_from_query
    #number_of_pages = ceil ( (page.totalNumEntries)  / (PAGE_SIZE) )
#AttributeError: 'NoneType' object has no attribute 'totalNumEntries'

#----------------------------------------------------------------------
#Ran 2 tests in 31.348s
