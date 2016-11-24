from django.test import TestCase
from wad_Campaign.models import Campaign
from wad_Budget.models import Budget
#from wad_Common.query import list_from_query
#from wad_Campaign.management.commands import campaignclear
#from wad_Campaign.management.commands import campaignsync
from googleads import adwords
from unittest import skipIf

# TODO test the return result from Google API

# Create your tests here.


# remove all
excludeset = ['t000', 't001', 't002', 't003', 't004', 't005', 't006', 't007', 't008', 
              't020', 't021', 't022', 't023', 't024', 't025', 't026', 't027']

# run only 1 test
excludeset.remove('t026')
#excludeset.remove('t025')
#excludeset.remove('t027')


# run all tests
#excludeset = ['']



class wad_Campaign_testcases ( TestCase ):
  
  service = None
  query = None
  rslt = None

  n_non_test_campaigns_aw = 0
  n_non_test_campaigns_db = 0
  startingcampaigns = []
  startingcampaignsids = []
  
  # keep track of budgets for noref tests and for docleanups so we 
  # don't have multiple names for budgets when tests fail

  n_non_test_budgets_aw = 0
  n_non_test_budgets_db = 0
  startingbudgets = []
  startingbudgetsids = []

  
  @classmethod
  def setUpClass( self ):
    client = adwords.AdWordsClient.LoadFromStorage()
    
    # keep a list of starting campaigns
    self.startingcampaigns = Campaign.listcampaigns ( client )
    
    # create a list of starting campaign ids
    for campaign in self.startingcampaigns:
      self.startingcampaignsids.append ( campaign['id'] )
    
    # keep track of the len of the starting campaigns list in aw
    self.n_non_test_campaigns_aw = len ( self.startingcampaigns )
    
    # keep track of the len of the starting campaigns list in django
    Campaign.sync ( client )
    self.n_non_test_campaigns_db = len ( Campaign.objects.all() )
    
    # budgets section

    # keep a list of starting budgets
    self.startingbudgets = Budget.listbudgets ( client )
    
    # create a list of starting budget ids
    for budget in self.startingbudgets:
      self.startingbudgetsids.append ( budget['budgetId'] )
    
    # keep track of the len of the starting budgets list in aw
    self.n_non_test_budgets_aw = len ( self.startingbudgets )
    
    # keep track of the len of the starting budgets list in django
    Budget.sync ( client )
    self.n_non_test_budgets_db = len ( Budget.objects.all() )

    
  @classmethod
  def tearDownClass( self ):
    pass

  
  def setUp ( self ):
    
    print ( '\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~' )
    
  def tearDown ( self ):
    client = adwords.AdWordsClient.LoadFromStorage()
    
    
    # get a list of all campaigns
    allcampaigns = Campaign.listcampaigns ( client )
    
    # all tests should return to init state, assert that they do by 
    # checking the len of current campaigns vs len of starting non test
    # campaigns
    self.assertEqual ( len ( allcampaigns ), self.n_non_test_campaigns_aw )

    self.assertEqual ( len ( Campaign.objects.all() ), self.n_non_test_campaigns_db )

    # budgets section
    
    # get a list of all budgets
    allbudgets = Budget.listbudgets ( client )
    
    # all tests should return to init state, assert that they do by 
    # checking the len of current budgets vs len of starting non test
    # budgets
    self.assertEqual ( len ( allbudgets ), self.n_non_test_budgets_aw )

    self.assertEqual ( len ( Budget.objects.all() ), self.n_non_test_budgets_db )


  # this method returns the test system back to its initialization state
  def doCleanups ( self ):

    client = adwords.AdWordsClient.LoadFromStorage()
        
    # create a list of all current campaigns
    allcampaigns = Campaign.listcampaigns ( client )

    # iterate the list of current campaigns
    for campaign in allcampaigns:
      # check if the campaign is in the startingcampaignsids list
      if campaign['id'] not in self.startingcampaignsids:
        # if it is not in the list then remove the campaign
        Campaign.removecampaign ( client, campaign['id'] )


    # budgets section

    # create a list of all current budgets
    allbudgets = Budget.listbudgets ( client )

    # iterate the list of current budgets
    for budget in allbudgets:
      # check if the budget is in the startingbudgetsids list
      if budget['budgetId'] not in self.startingbudgetsids:
        # if it is not in the list then remove the budget
        Budget.removebudget ( client, budget['budgetId'] )



  @skipIf ( 't000' in excludeset, 'Excluding test t000' )
  def test_t000_wad_Campaign_add_remove_usingaddremove(self):
    
    print ( 'wad_Campaign test t000' )
    
    client = adwords.AdWordsClient.LoadFromStorage()
    
    # creates three new campaigns
    campaign0id = Campaign.addcampaign ( client, 'test_t000_campaign0' ).campaignid
    campaign1id = Campaign.addcampaign ( client, 'test_t000_campaign1' ).campaignid
    campaign2id = Campaign.addcampaign ( client, 'test_t000_campaign2' ).campaignid
    
    # gets the lists of all campaigns
    campaignlist = Campaign.listcampaigns ( client )
    
    campaignidlist = []
    
    # builds a list of campaigns with status != REMOVED
    for campaign in campaignlist:
      if campaign['status'] != Campaign.STATE_REMOVED:
        campaignidlist.append ( campaign['id'] )

    # asserts the campaigns added are in the list
    self.assertTrue ( campaign0id in campaignidlist )
    self.assertTrue ( campaign1id in campaignidlist )
    self.assertTrue ( campaign2id in campaignidlist )
    
    # removes the campaigns
    Campaign.removecampaign ( client, campaign0id )
    Campaign.removecampaign ( client, campaign1id )
    Campaign.removecampaign ( client, campaign2id )
    
    # gets the list of all campaigns
    campaignlist = Campaign.listcampaigns ( client )
        
    campaignidlist = []
    
    # builds a list of campaigns with status != REMOVED
    for campaign in campaignlist:
      if campaign['status'] != Campaign.STATE_REMOVED:
        campaignidlist.append ( campaign['campaignId'] )

    # asserts the campaigns added are not in the list
    self.assertFalse ( campaign0id in campaignidlist )
    self.assertFalse ( campaign1id in campaignidlist )
    self.assertFalse ( campaign2id in campaignidlist )

    Budget.removenorefbudgets( client )
    
    
  @skipIf ( 't001' in excludeset, 'Excluding test t001' )
  def test_t001_wad_Campaign_sync_add_remove_usingaddremove ( self ):
    
    print ( 'wad_Campaign test t001' )
    
    client = adwords.AdWordsClient.LoadFromStorage()

    # sync with django db
    Campaign.sync ( client )
    
    # beginning django campaigns queryset
    beginningcampaigns = Campaign.objects.all()
        
    # beginning awcampaignslst
    beginningawcampaignslst = Campaign.listcampaigns ( client )
    
    # assert that the django campaign set and aw campaignset correspond
    self.assertEqual ( len ( beginningcampaigns ), len ( beginningawcampaignslst ) )
        
    # create three new campaigns in aw
    campaign0id = Campaign.addcampaign ( client, 'test_t001_campaign0' ).campaignid
    campaign1id = Campaign.addcampaign ( client, 'test_t001_campaign1' ).campaignid
    campaign2id = Campaign.addcampaign ( client, 'test_t001_campaign2' ).campaignid
    
    # sync with django db
    ###Campaign.sync ( client )
    
    # test if the new campaigns added to aw are in the Django system
    self.assertEqual ( len ( beginningcampaigns ) + 3, len ( Campaign.objects.all() ) )
    self.assertEqual ( len ( beginningawcampaignslst ) + 3, len ( Campaign.objects.all() ) )
    
    self.assertTrue ( Campaign.objects.filter ( campaignname = 'test_t001_campaign0' ).exists() )
    self.assertTrue ( Campaign.objects.filter ( campaignname = 'test_t001_campaign1' ).exists() )
    self.assertTrue ( Campaign.objects.filter ( campaignname = 'test_t001_campaign2' ).exists() )
    
    # removes the campaigns from aw
    Campaign.removecampaign ( client, campaign0id )
    Campaign.removecampaign ( client, campaign1id )
    Campaign.removecampaign ( client, campaign2id )
    
    # sync with django db
    ###Campaign.sync ( client )

    # test if the django campaign set is equal to the aw campaign set after deletions
    self.assertEqual ( len ( beginningcampaigns ), len ( Campaign.objects.all() ) )
    self.assertEqual ( len ( beginningawcampaignslst ), len ( Campaign.objects.all() ) )
    
    self.assertFalse ( Campaign.objects.filter ( campaignname = 'test_t001_campaign0' ).exists() )
    self.assertFalse ( Campaign.objects.filter ( campaignname = 'test_t001_campaign1' ).exists() )
    self.assertFalse ( Campaign.objects.filter ( campaignname = 'test_t001_campaign2' ).exists() )
    
    Budget.removenorefbudgets( client )


  @skipIf ( 't002' in excludeset, 'Excluding test t002' )
  def test_t002_wad_Campaign_add_remove_usingsync(self):
    
    print ( 'wad_Campaign test t002' )
    
    client = adwords.AdWordsClient.LoadFromStorage()
    
    # creates three new campaigns  
    campaign0id = Campaign._aw_addcampaign ( client, 'test_t002_campaign0' )['id']
    campaign1id = Campaign._aw_addcampaign ( client, 'test_t002_campaign1' )['id']
    campaign2id = Campaign._aw_addcampaign ( client, 'test_t002_campaign2' )['id']
    
    # gets the lists of all campaigns
    campaignlist = Campaign.listcampaigns ( client )
    
    campaignidlist = []
    
    # builds a list of campaigns with status != REMOVED
    for campaign in campaignlist:
      if campaign['status'] != Campaign.STATE_REMOVED:
        campaignidlist.append ( campaign['id'] )

    # asserts the campaigns added are in the list
    self.assertTrue ( campaign0id in campaignidlist )
    self.assertTrue ( campaign1id in campaignidlist )
    self.assertTrue ( campaign2id in campaignidlist )
    
    # removes the campaigns
    Campaign.removecampaign ( client, campaign0id )
    Campaign.removecampaign ( client, campaign1id )
    Campaign.removecampaign ( client, campaign2id )
    
    
    
    # gets the list of all campaigns
    campaignlist = Campaign.listcampaigns ( client )
        
    campaignidlist = []
    
    # builds a list of campaigns with status != REMOVED
    for campaign in campaignlist:
      if campaign['status'] != Campaign.STATE_REMOVED:
        campaignidlist.append ( campaign['id'] )

    # asserts the campaigns added are not in the list
    self.assertFalse ( campaign0id in campaignidlist )
    self.assertFalse ( campaign1id in campaignidlist )
    self.assertFalse ( campaign2id in campaignidlist )
    
    #Budget.removenorefbudgets( client )

    removedbudgets = Budget.removenorefbudgets( client )    
    self.assertEqual ( len ( removedbudgets ), 3 )


  @skipIf ( 't003' in excludeset, 'Excluding test t003' )
  def test_t003_wad_Campaign_sync_add_remove_usingsync ( self ):
    
    print ( 'wad_Campaign test t003' )
    
    client = adwords.AdWordsClient.LoadFromStorage()

    # sync with django db
    Campaign.sync ( client )
    
    # beginning django campaigns queryset
    beginningcampaigns = Campaign.objects.all()
        
    # beginning awcampaignslst
    beginningawcampaignslst = Campaign.listcampaigns ( client )
    
    # assert that the django campaign set and aw campaignset correspond
    self.assertEqual ( len ( beginningcampaigns ), len ( beginningawcampaignslst ) )
        
    # create three new campaigns in aw
    campaign0id = Campaign._aw_addcampaign ( client, 'test_t003_campaign0' )['id']
    campaign1id = Campaign._aw_addcampaign ( client, 'test_t003_campaign1' )['id']
    campaign2id = Campaign._aw_addcampaign ( client, 'test_t003_campaign2' )['id']
    
    # sync with django db
    Campaign.sync ( client )
    
    # test if the new campaigns added to aw are in the Django system
    self.assertEqual ( len ( beginningcampaigns ) + 3, len ( Campaign.objects.all() ) )
    self.assertEqual ( len ( beginningawcampaignslst ) + 3, len ( Campaign.objects.all() ) )
    
    self.assertTrue ( Campaign.objects.filter ( campaignname = 'test_t003_campaign0' ).exists() )
    self.assertTrue ( Campaign.objects.filter ( campaignname = 'test_t003_campaign1' ).exists() )
    self.assertTrue ( Campaign.objects.filter ( campaignname = 'test_t003_campaign2' ).exists() )
    
    # removes the campaigns from aw
    Campaign.removecampaign ( client, campaign0id )
    Campaign.removecampaign ( client, campaign1id )
    Campaign.removecampaign ( client, campaign2id )
    
    # sync with django db
    Campaign.sync ( client )

    # test if the django campaign set is equal to the aw campaign set after deletions
    self.assertEqual ( len ( beginningcampaigns ), len ( Campaign.objects.all() ) )
    self.assertEqual ( len ( beginningawcampaignslst ), len ( Campaign.objects.all() ) )
    
    self.assertFalse ( Campaign.objects.filter ( campaignname = 'test_t003_campaign0' ).exists() )
    self.assertFalse ( Campaign.objects.filter ( campaignname = 'test_t003_campaign1' ).exists() )
    self.assertFalse ( Campaign.objects.filter ( campaignname = 'test_t003_campaign2' ).exists() )

    Budget.removenorefbudgets( client )

  @skipIf ( 't020' in excludeset, 'Excluding test t020' )
  def test_t020_wad_Campaign_list_campaigns(self):
    
    client = adwords.AdWordsClient.LoadFromStorage()
    
    campaigns = Campaign.listcampaigns( client )
    
    rslt = Campaign._aw_addcampaign ( client, 'test_t020_campaign0' )
    
    #print ( rslt )

    campaigns = Campaign.listcampaigns( client )

    Campaign.removecampaign ( client, rslt['id'] )



    rslt = Campaign.addcampaign ( client, 'test_t020_campaign1')
    
    print ( rslt )
    
    rslt = Campaign.removecampaign ( client, rslt.campaignid )
    
    #print ( rslt )

    Budget.removenorefbudgets( client )
    

  @skipIf ( 't021' in excludeset, 'Excluding test t021' )
  def test_t021_wad_Campaign_remove_noref_budgets(self):
    
    # this test checks if noref budgets are removed successfully using
    # Budget.removenorefbudgets ( )
    
    client = adwords.AdWordsClient.LoadFromStorage()
    
    campaignnames = ['test_t021_campaign0', 
                   'test_t021_campaign1', 
                   'test_t021_campaign2' ]
    
    # create three campaigns with unspecified budgets, budgets are created
    # for them automatically
    c0 = Campaign.addcampaign ( client, campaignnames[0])
    c1 = Campaign.addcampaign ( client, campaignnames[1])
    c2 = Campaign.addcampaign ( client, campaignnames[2])
    
    # remove the campaigns, budgets are now 0 ref budgets
    Campaign.removecampaign ( client, c0.campaignid )
    Campaign.removecampaign ( client, c1.campaignid )
    Campaign.removecampaign ( client, c2.campaignid )
    
    removedbudgets = Budget.removenorefbudgets( client )
    
    for budget in removedbudgets:
      print ( budget.budgetname[11:] )
      self.assertTrue ( budget.budgetname[11:] in campaignnames )

  
  @skipIf ( 't022' in excludeset, 'Excluding test t022' )
  def test_t022_wad_Campaign_multiple_campaigns_one_budget(self):
    # tests that multiple campaigns can have the same budget
    
    pass






  @skipIf ( 't023' in excludeset, 'Excluding test t023' )
  def test_t023_wad_Campaign_sync_with_existing_budget ( self ):
    
    print ( 'wad_Campaign test t023' )
    
    client = adwords.AdWordsClient.LoadFromStorage()

    # sync with django db
    Campaign.sync ( client )
    
    budget0 = Budget ( budgetname = 't023_budget0', budgetamount = 10000000 )
    budget0.save()
    budget1 = Budget ( budgetname = 't023_budget1', budgetamount = 20000000 )
    budget1.save()
    budget2 = Budget ( budgetname = 't023_budget2', budgetamount = 30000000 )
    budget2.save()
    
    campaign0 = Campaign ( campaignname = 't023_campaign0', campaignbudget = budget0 )
    campaign0.save ()
    campaign1 = Campaign ( campaignname = 't023_campaign1', campaignbudget = budget1 )
    campaign1.save ()
    campaign2 = Campaign ( campaignname = 't023_campaign2', campaignbudget = budget2 )
    campaign2.save ()
    
    allcampaigns = Campaign.listcampaigns ( client )
    
    for campaign in allcampaigns:
      if campaign['budget']['budgetId'] == budget0.budgetid:
        self.assertEqual ( campaign['budget']['amount']['microAmount'], budget0.budgetamount )
      
      if campaign['budget']['budgetId'] == budget1.budgetid:
        self.assertEqual ( campaign['budget']['amount']['microAmount'], budget1.budgetamount )

      if campaign['budget']['budgetId'] == budget2.budgetid:
        self.assertEqual ( campaign['budget']['amount']['microAmount'], budget2.budgetamount )
    
    campaign0.delete()
    campaign1.delete()
    campaign2.delete()
    
    removedbudgets = Budget.removenorefbudgets( client )
    self.assertEqual ( len ( removedbudgets ), 3 )


  @skipIf ( 't024' in excludeset, 'Excluding test t024' )
  def test_t024_wad_Campaign_sync_with_existing_budget2 ( self ):
    
    print ( 'wad_Campaign test t024' )
    
    client = adwords.AdWordsClient.LoadFromStorage()

    # sync with django db
    Campaign.sync ( client )
    
    budget0 = Budget._aw_addbudget ( client, 't024_budget0', 10000000 )
    budget1 = Budget._aw_addbudget ( client, 't024_budget1', 20000000 )
    budget2 = Budget._aw_addbudget ( client, 't024_budget2', 30000000 )
    
    Budget.sync ( client )
    
    campaign0 = Campaign._aw_addcampaign ( client, 't024_campaign0', Budget.objects.get ( budgetamount = 10000000 ) )
    campaign1 = Campaign._aw_addcampaign ( client, 't024_campaign1', Budget.objects.get ( budgetamount = 20000000 ) )
    campaign2 = Campaign._aw_addcampaign ( client, 't024_campaign2', Budget.objects.get ( budgetamount = 30000000 ) )

    allcampaigns = Campaign.listcampaigns ( client )

    #print ( budget0 )
    
    for campaign in allcampaigns:
      if campaign['id'] == campaign0['id']:
        self.assertEqual ( campaign['budget']['amount']['microAmount'], budget0['amount']['microAmount'] )
        
      if campaign['id'] == campaign1['id']:
        self.assertEqual ( campaign['budget']['amount']['microAmount'], budget1['amount']['microAmount'] )

      if campaign['id'] == campaign2['id']:
        self.assertEqual ( campaign['budget']['amount']['microAmount'], budget2['amount']['microAmount'] )
        

      if campaign['budget']['budgetId'] == budget0['budgetId']:
        self.assertEqual ( campaign['budget']['amount']['microAmount'], budget0['amount']['microAmount'] )
      
      if campaign['budget']['budgetId'] == budget1['budgetId']:
        self.assertEqual ( campaign['budget']['amount']['microAmount'], budget1['amount']['microAmount'] )

      if campaign['budget']['budgetId'] == budget2['budgetId']:
        self.assertEqual ( campaign['budget']['amount']['microAmount'], budget2['amount']['microAmount'] )
    
    Campaign.sync ( client )
    
    Campaign.objects.get ( campaignbudget = Budget.objects.get ( budgetid = budget0['budgetId'] ) ).delete()
    Campaign.objects.get ( campaignbudget = Budget.objects.get ( budgetid = budget1['budgetId'] ) ).delete()
    Campaign.objects.get ( campaignbudget = Budget.objects.get ( budgetid = budget2['budgetId'] ) ).delete()
    
    
    #print ( campaign0 )
    
    #campaign0.delete()
    #campaign1.delete()
    #campaign2.delete()
    
    Budget.removenorefbudgets( client )


  @skipIf ( 't025' in excludeset, 'Excluding test t025' )
  def test_t025_wad_Campaign_sync_with_nonexisting_budget ( self ):
    
    print ( 'wad_Campaign test t025' )
    
    client = adwords.AdWordsClient.LoadFromStorage()

    # sync with django db
    Campaign.sync ( client )
        
    campaign0 = Campaign ( campaignname = 't025_campaign0' )
    campaign0.save ()
    campaign1 = Campaign ( campaignname = 't025_campaign1' )
    campaign1.save ()
    campaign2 = Campaign ( campaignname = 't025_campaign2' )
    campaign2.save ()
    
    allcampaigns = Campaign.listcampaigns ( client )
    
    for campaign in allcampaigns:
      if campaign['id'] == campaign0.campaignid:
        self.assertEqual ( campaign['name'], campaign0.campaignname )
      
      if campaign['id'] == campaign1.campaignid:
        self.assertEqual ( campaign['name'], campaign1.campaignname )

      if campaign['id'] == campaign2.campaignid:
        self.assertEqual ( campaign['name'], campaign2.campaignname )
    
    campaign0.delete()
    campaign1.delete()
    campaign2.delete()
    
    removedbudgets = Budget.removenorefbudgets( client )
    
    self.assertEqual ( len ( removedbudgets ), 3 )


  @skipIf ( 't026' in excludeset, 'Excluding test t026' )
  def test_t026_wad_Campaign_modify_sync ( self ):
    
    print ( 'wad_Campaign test t026' )

    client = adwords.AdWordsClient.LoadFromStorage()
    service = Campaign.serviceobj ( client )

    # modify name

    campaign0 = Campaign ( campaignname = 't026_campaign0' )
    campaign0.save ()

    mdict = Campaign.modifydict (campaign0.campaignid, 
                                 't026_campaign0_renamed', 
                                 campaign0.campaignstatus, 
                                 campaign0.campaignbudget,
                                 campaign0.campaigntargetgooglesearch,
                                 campaign0.campaigntargetsearchnetwork,
                                 campaign0.campaigntargetcontentnetwork,
                                 )
    
    service.mutate ( [mdict] )

    campaign0 = Campaign.objects.get ( campaignid = campaign0.campaignid )
    self.assertEqual ( campaign0.campaignname, 't026_campaign0' )

    Campaign.sync( client )

    campaign0 = Campaign.objects.get ( campaignid = campaign0.campaignid )
    self.assertEqual ( campaign0.campaignname, 't026_campaign0_renamed' )


    # modify status

    campaign1 = Campaign ( campaignname = 't026_campaign1' )
    campaign1.save ()

    statusnew = Campaign.objects.get ( campaignid = campaign1.campaignid ).campaignstatus
    
    if campaign1.campaignstatus == Campaign.STATE_ENABLED: 
      statusnew = Campaign.STATE_PAUSED
    else:
      statusnew = Campaign.STATE_ENABLED
    
    mdict = Campaign.modifydict (campaign1.campaignid, 
                                 campaign1.campaignname, 
                                 statusnew, 
                                 campaign1.campaignbudget,
                                 campaign1.campaigntargetgooglesearch,
                                 campaign1.campaigntargetsearchnetwork,
                                 campaign1.campaigntargetcontentnetwork)
    
    service.mutate ( [mdict] )

    if statusnew == Campaign.STATE_ENABLED: 
      statusnew = Campaign.STATE_PAUSED
    else:
      statusnew = Campaign.STATE_ENABLED

    campaign1 = Campaign.objects.get ( campaignid = campaign1.campaignid )
    self.assertEqual ( campaign1.campaignstatus, statusnew )

    Campaign.sync( client )

    if statusnew == Campaign.STATE_ENABLED: 
      statusnew = Campaign.STATE_PAUSED
    else:
      statusnew = Campaign.STATE_ENABLED

    campaign1 = Campaign.objects.get ( campaignid = campaign1.campaignid )
    self.assertEqual ( campaign1.campaignstatus, statusnew )


    # modify budget

    campaign2 = Campaign ( campaignname = 't026_campaign2' )
    campaign2.save ()

    oldbudget = Campaign.objects.get ( campaignid = campaign2.campaignid ).campaignbudget
    
    newbudget = Budget ( client, 'test_t026_budget2', 6000000000 )
    newbudget.save()
    
    mdict = Campaign.modifydict (campaign2.campaignid, 
                                 campaign2.campaignname, 
                                 campaign2.campaignstatus, 
                                 newbudget.asdict(),
                                 campaign2.campaigntargetgooglesearch,
                                 campaign2.campaigntargetsearchnetwork,
                                 campaign2.campaigntargetcontentnetwork)
    
    service.mutate ( [mdict] )


    Campaign.sync( client )

    campaign2 = Campaign.objects.get ( campaignid = campaign2.campaignid )
    self.assertNotEqual ( campaign2.campaignbudget.budgetid, oldbudget.budgetid )
    self.assertEqual ( campaign2.campaignbudget.budgetid, newbudget.budgetid )


    
    
    # modify budget name

    campaign3 = Campaign ( campaignname = 't026_campaign3' )
    campaign3.save ()

    abudget = campaign3.campaignbudget
    
    abudget.budgetname = 'budget_for_t026_new_budget_name'
    
    abudget.save()
    
    #mdict = Campaign.modifydict (campaign3.campaignid, 
                                 #campaign3.campaignname, 
                                 #campaign3.campaignstatus, 
                                 #campaign3.campaignbudget,
                                 #campaign3.campaigntargetgooglesearch,
                                 #campaign3.campaigntargetsearchnetwork,
                                 #campaign3.campaigntargetcontentnetwork,
                                 #)
    
    #service.mutate ( [mdict] )

    campaign3budgetname = Campaign.objects.get ( campaignid = campaign3.campaignid ).campaignbudget.budgetname
    self.assertEqual ( campaign3budgetname, 'budget_for_t026_campaign3' )

    Campaign.sync( client )

    campaign3budgetname = Campaign.objects.get ( campaignid = campaign3.campaignid ).campaignbudget.budgetname
    self.assertEqual ( campaign3budgetname, 'budget_for_t026_new_budget_name' )





    # modify budget 4
    
    
    campaign4 = Campaign ( campaignname = 't026_campaign4' )
    campaign4.save ()

    oldbudget = Campaign.objects.get ( campaignid = campaign4.campaignid ).campaignbudget
    
    newbudget = Budget ( client, 'test_t026_budget4', 6000000000 )
    newbudget.save()
    
    campaign4.campaignbudget = newbudget
    campaign4.save()

    #Campaign.sync( client )

    campaign4 = Campaign.objects.get ( campaignid = campaign4.campaignid )
    self.assertNotEqual ( campaign4.campaignbudget.budgetid, oldbudget.budgetid )
    self.assertEqual ( campaign4.campaignbudget.budgetid, newbudget.budgetid )




    # modify ad channel type

    #campaign2 = Campaign ( campaignname = 't026_campaign2' )
    #campaign2.save ()

    #adchan = Campaign.objects.get ( campaignid = campaign2.campaignid ).campaignadchanneltype
    
    #if campaign2.campaignadchanneltype == Campaign.TYPE_AD_CHAN_SEARCH: 
      #adchan = Campaign.TYPE_AD_CHAN_DISPLAY
    #else:
      #adchan = Campaign.TYPE_AD_CHAN_SEARCH
    
    #mdict = Campaign.modifydict (campaign2.campaignid, 
                                 #campaign2.campaignname, 
                                 #campaign2.campaignstatus, 
                                 #adchan,
                                 #campaign2.campaignbudget )
    #print ( mdict )
    #service.mutate ( [mdict] )

    #if adchan == Campaign.TYPE_AD_CHAN_SEARCH: 
      #adchan = Campaign.TYPE_AD_CHAN_DISPLAY
    #else:
      #adchan = Campaign.TYPE_AD_CHAN_SEARCH

    #campaign2 = Campaign.objects.get ( campaignid = campaign2.campaignid )
    #self.assertEqual ( campaign2.campaignadchanneltype, adchan )

    #Campaign.sync( client )

    #if adchan == Campaign.TYPE_AD_CHAN_SEARCH: 
      #adchan = Campaign.TYPE_AD_CHAN_DISPLAY
    #else:
      #adchan = Campaign.TYPE_AD_CHAN_SEARCH

    #campaign2 = Campaign.objects.get ( campaignid = campaign2.campaignid )
    #self.assertEqual ( campaign2.campaignadchanneltype, adchan )

    campaign0.delete()
    campaign1.delete()
    campaign2.delete()
    campaign3.delete()
    campaign4.delete()

    removedbudgets = Budget.removenorefbudgets( client )
    
    self.assertEqual ( len ( removedbudgets ), 5 )



  #@skipIf ( 't027' in excludeset, 'Excluding test t027' )
  #def test_t027_wad_Campaign ( self ):
    
    #print ( 'wad_Campaign test t027' )

    #client = adwords.AdWordsClient.LoadFromStorage()
    #service = Campaign.serviceobj ( client )

    ## modify name

    #campaign0 = Campaign ( campaignname = 't027_campaign0' )
    #campaign0.save ()



  def test_wad_Campaign_management_command_campaignsync ( self ):
    
    client = adwords.AdWordsClient.LoadFromStorage()
    
    #Campaign.addcampaign ( client, 'new campaign 0' )
    
    
    
    
    return
    
    
    
    commandobj = campaignsync.Command()
    
    # sync to populate
    commandobj.handle()
    
    allentries = Campaign.objects.all()
    
    # modify values and see if they revert back to original
    for entry in allentries:
      entry.campaignname = '%s%s' % ( entry.campaignname, '_modifiedtestring' )
      entry.campaignstatus = Campaign.STATE_TESTING
    
      self.assertEqual ( True, '_modifiedtestring' in entry.campaignname )
      self.assertEqual ( Campaign.STATE_TESTING, entry.campaignstatus )
      
      entry.save()
    
    # sync to test that they return to original, don't have '_modifiedtesting' string
    commandobj.handle()
    
    allentries = Campaign.objects.all()
    
    for entry in allentries:
      self.assertEqual ( False, '_modifiedtesting' in entry.campaignname )
      self.assertNotEqual ( Campaign.STATE_TESTING, entry.campaignstatus )
      
      
    
    # remove a campaign from adwords
    if len(allentries) != 0: # if len of allentries is 0 we have nothing to delete
      Campaign.removecampaign ( client, allentries[0].campaignid )
      
    
  
  #def test_wad_Campaign_management_command_campaignclear ( self ):
    
    #return
    
    #commandobj = campaignclear.Command()
    
    #allentries = Campaign.objects.all()
    
    #commandobj.handle()
    
    #allentries = Campaign.objects.all()
    
    #self.assertEqual ( 0, len ( allentries ) )
    ##campaignclear.Command.handle()
    
    
    
    
    


    