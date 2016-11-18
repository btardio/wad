from django.test import TestCase
from unittest import skipIf
from wad_Budget.models import Budget
from googleads import adwords

import suds

# Create your tests here.

# remove all
excludeset = ['t000', 't001', 't002', 't003', 't004', 't005', 't006', 't007']

# run only 1 test
excludeset.remove('t005')

# run all tests
excludeset = ['']

class wad_Budget_testcases ( TestCase ):
  
#  service = None
#  query = None
#  rslt = None
#  client = None
  n_non_test_budgets_aw = 0
  n_non_test_budgets_db = 0
  startingbudgets = []
  startingbudgetsids = []
  
  #cleanupbudgets = []
  
  @classmethod
  def setUpClass( self ):
    client = adwords.AdWordsClient.LoadFromStorage()
    
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
    
    client = adwords.AdWordsClient.LoadFromStorage()
    
    # set up three test budgets
    #self.testbudgetid0 = Budget.addbudget ( client, 'test_setup_budget0', 2000000000 ).budgetid
    #self.testbudgetid1 = Budget.addbudget ( client, 'test_setup_budget1', 2000000000 ).budgetid
    #self.testbudgetid2 = Budget.addbudget ( client, 'test_setup_budget2', 2000000000 ).budgetid

    
  
  def tearDown ( self ):
    
    client = adwords.AdWordsClient.LoadFromStorage()
    
    # remove the three set up test budgets
    #Budget.removebudget ( client, self.testbudgetid0 )
    #Budget.removebudget ( client, self.testbudgetid1 )
    #Budget.removebudget ( client, self.testbudgetid2 )
    
    # get a list of all budgets
    allbudgets = Budget.listbudgets ( client )
    
    # all tests should return to init state, assert that they do by 
    # checking the len of current budgets vs len of starting non test
    # budgets
    self.assertEqual ( len ( allbudgets ), self.n_non_test_budgets_aw )

    self.assertEqual ( len ( Budget.objects.all() ), self.n_non_test_budgets_db )

  # this method returns the test system back to its initialization state
  def doCleanups ( self ):
    
    return
    
    client = adwords.AdWordsClient.LoadFromStorage()
        
    # create a list of all current budgets
    allbudgets = Budget.listbudgets ( client )

    # iterate the list of current budgets
    for budget in allbudgets:
      # check if the budget is in the startingbudgetsids list
      if budget['budgetId'] not in self.startingbudgetsids:
        # if it is not in the list then remove the budget
        Budget.removebudget ( client, budget['budgetId'] )
        
        
    

  @skipIf ( 't000' in excludeset, 'Excluding test t000' )
  def test_t000_wad_Budget_add_remove_usingaddremove(self):
    
    
    
    client = adwords.AdWordsClient.LoadFromStorage()
    
    # creates three new budgets
    budget0id = Budget.addbudget ( client, 'test_t000_budget0', 6000000000 ).budgetid
    budget1id = Budget.addbudget ( client, 'test_t000_budget1', 6000000000 ).budgetid
    budget2id = Budget.addbudget ( client, 'test_t000_budget2', 6000000000 ).budgetid
    
    # gets the lists of all budgets
    budgetlist = Budget.listbudgets ( client )
    
    budgetidlist = []
    
    # builds a list of budgets with status != REMOVED
    for budget in budgetlist:
      if budget['status'] != Budget.STATE_REMOVED:
        budgetidlist.append ( budget['budgetId'] )

    # asserts the budgets added are in the list
    self.assertTrue ( budget0id in budgetidlist )
    self.assertTrue ( budget1id in budgetidlist )
    self.assertTrue ( budget2id in budgetidlist )
    
    # removes the budgets
    Budget.removebudget ( client, budget0id )
    Budget.removebudget ( client, budget1id )
    Budget.removebudget ( client, budget2id )
    
    # gets the list of all budgets
    budgetlist = Budget.listbudgets ( client )
        
    budgetidlist = []
    
    # builds a list of budgets with status != REMOVED
    for budget in budgetlist:
      if budget['status'] != Budget.STATE_REMOVED:
        budgetidlist.append ( budget['budgetId'] )

    # asserts the budgets added are not in the list
    self.assertFalse ( budget0id in budgetidlist )
    self.assertFalse ( budget1id in budgetidlist )
    self.assertFalse ( budget2id in budgetidlist )
    

  @skipIf ( 't001' in excludeset, 'Excluding test t001' )
  def test_t001_wad_Budget_sync_add_remove_usingaddremove ( self ):
    
    client = adwords.AdWordsClient.LoadFromStorage()

    # sync with django db
    Budget.sync ( client )
    
    # beginning django budgets queryset
    beginningbudgets = Budget.objects.all()
        
    # beginning awbudgetslst
    beginningawbudgetslst = Budget.listbudgets ( client )
    
    # assert that the django budget set and aw budgetset correspond
    self.assertEqual ( len ( beginningbudgets ), len ( beginningawbudgetslst ) )
        
    # create three new budgets in aw
    budget0id = Budget.addbudget ( client, 'test_t001_budget0', 7000000000 ).budgetid
    budget1id = Budget.addbudget ( client, 'test_t001_budget1', 7000000000 ).budgetid
    budget2id = Budget.addbudget ( client, 'test_t001_budget2', 7000000000 ).budgetid
    
    # sync with django db
    ###Budget.sync ( client )
    
    # test if the new budgets added to aw are in the Django system
    self.assertEqual ( len ( beginningbudgets ) + 3, len ( Budget.objects.all() ) )
    self.assertEqual ( len ( beginningawbudgetslst ) + 3, len ( Budget.objects.all() ) )
    
    self.assertTrue ( Budget.objects.filter ( budgetname = 'test_t001_budget0' ).exists() )
    self.assertTrue ( Budget.objects.filter ( budgetname = 'test_t001_budget1' ).exists() )
    self.assertTrue ( Budget.objects.filter ( budgetname = 'test_t001_budget2' ).exists() )
    
    # removes the budgets from aw
    Budget.removebudget ( client, budget0id )
    Budget.removebudget ( client, budget1id )
    Budget.removebudget ( client, budget2id )
    
    # sync with django db
    ###Budget.sync ( client )

    # test if the django budget set is equal to the aw budget set after deletions
    self.assertEqual ( len ( beginningbudgets ), len ( Budget.objects.all() ) )
    self.assertEqual ( len ( beginningawbudgetslst ), len ( Budget.objects.all() ) )
    
    self.assertFalse ( Budget.objects.filter ( budgetname = 'test_t001_budget0' ).exists() )
    self.assertFalse ( Budget.objects.filter ( budgetname = 'test_t001_budget1' ).exists() )
    self.assertFalse ( Budget.objects.filter ( budgetname = 'test_t001_budget2' ).exists() )
    


  @skipIf ( 't002' in excludeset, 'Excluding test t002' )
  def test_t002_wad_Budget_add_remove_usingsync(self):
    
    client = adwords.AdWordsClient.LoadFromStorage()
    
    # creates three new budgets  
    budget0id = Budget._aw_addbudget ( client, 'test_t002_budget0', 6000000000 )['budgetId']
    budget1id = Budget._aw_addbudget ( client, 'test_t002_budget1', 6000000000 )['budgetId']
    budget2id = Budget._aw_addbudget ( client, 'test_t002_budget2', 6000000000 )['budgetId']
    
    # gets the lists of all budgets
    budgetlist = Budget.listbudgets ( client )
    
    budgetidlist = []
    
    # builds a list of budgets with status != REMOVED
    for budget in budgetlist:
      if budget['status'] != Budget.STATE_REMOVED:
        budgetidlist.append ( budget['budgetId'] )

    # asserts the budgets added are in the list
    self.assertTrue ( budget0id in budgetidlist )
    self.assertTrue ( budget1id in budgetidlist )
    self.assertTrue ( budget2id in budgetidlist )
    
    # removes the budgets
    Budget.removebudget ( client, budget0id )
    Budget.removebudget ( client, budget1id )
    Budget.removebudget ( client, budget2id )
    
    
    
    # gets the list of all budgets
    budgetlist = Budget.listbudgets ( client )
        
    budgetidlist = []
    
    # builds a list of budgets with status != REMOVED
    for budget in budgetlist:
      if budget['status'] != Budget.STATE_REMOVED:
        budgetidlist.append ( budget['budgetId'] )

    # asserts the budgets added are not in the list
    self.assertFalse ( budget0id in budgetidlist )
    self.assertFalse ( budget1id in budgetidlist )
    self.assertFalse ( budget2id in budgetidlist )
    

  @skipIf ( 't003' in excludeset, 'Excluding test t003' )
  def test_t003_wad_Budget_sync_add_remove_usingsync ( self ):
    
    client = adwords.AdWordsClient.LoadFromStorage()

    # sync with django db
    Budget.sync ( client )
    
    # beginning django budgets queryset
    beginningbudgets = Budget.objects.all()
        
    # beginning awbudgetslst
    beginningawbudgetslst = Budget.listbudgets ( client )
    
    # assert that the django budget set and aw budgetset correspond
    self.assertEqual ( len ( beginningbudgets ), len ( beginningawbudgetslst ) )
        
    # create three new budgets in aw
    budget0id = Budget._aw_addbudget ( client, 'test_t003_budget0', 7000000000 )['budgetId']
    budget1id = Budget._aw_addbudget ( client, 'test_t003_budget1', 7000000000 )['budgetId']
    budget2id = Budget._aw_addbudget ( client, 'test_t003_budget2', 7000000000 )['budgetId']
    
    # sync with django db
    Budget.sync ( client )
    
    # test if the new budgets added to aw are in the Django system
    self.assertEqual ( len ( beginningbudgets ) + 3, len ( Budget.objects.all() ) )
    self.assertEqual ( len ( beginningawbudgetslst ) + 3, len ( Budget.objects.all() ) )
    
    self.assertTrue ( Budget.objects.filter ( budgetname = 'test_t003_budget0' ).exists() )
    self.assertTrue ( Budget.objects.filter ( budgetname = 'test_t003_budget1' ).exists() )
    self.assertTrue ( Budget.objects.filter ( budgetname = 'test_t003_budget2' ).exists() )
    
    # removes the budgets from aw
    Budget.removebudget ( client, budget0id )
    Budget.removebudget ( client, budget1id )
    Budget.removebudget ( client, budget2id )
    
    # sync with django db
    Budget.sync ( client )

    # test if the django budget set is equal to the aw budget set after deletions
    self.assertEqual ( len ( beginningbudgets ), len ( Budget.objects.all() ) )
    self.assertEqual ( len ( beginningawbudgetslst ), len ( Budget.objects.all() ) )
    
    self.assertFalse ( Budget.objects.filter ( budgetname = 'test_t003_budget0' ).exists() )
    self.assertFalse ( Budget.objects.filter ( budgetname = 'test_t003_budget1' ).exists() )
    self.assertFalse ( Budget.objects.filter ( budgetname = 'test_t003_budget2' ).exists() )
    



  @skipIf ( 't004' in excludeset, 'Excluding test t004' )
  def test_t004_wad_Budget_sync_modify ( self ):
    
    client = adwords.AdWordsClient.LoadFromStorage()
    
    # initial sync
    Budget.sync ( client )
    
    # control will be used to check if the values return to original after modifications
    beginningbudgets_control = Budget.objects.all()
    # queryset used to modify values
    beginningbudgets = Budget.objects.all()
    
    # make sure we are working with querysets that aren't empty, should be at least 3 b/c of SetUp
    self.assertTrue ( len ( beginningbudgets ) >= 3 )
    self.assertTrue ( len ( beginningbudgets_control ) >= 3 )
    
    # change values in the django database
    for budget in beginningbudgets:

      budget.budgetstatus = Budget.STATE_TESTING
      budget.budgetname = budget.budgetname + '_testing'
      budget.budgetamount = budget.budgetamount + 10000000
    
      budget.save( sync_aw=False )
    
    # sync
    Budget.sync ( client )
    
    
    # queryset used to test if values revert to original values
    postmodifybudgets = Budget.objects.all()
    
    # make sure we are working with querysets that aren't empty, should be at least 3 b/c of SetUp
    self.assertTrue ( len ( postmodifybudgets ) >= 3 )
    
    # iterate budgets in database to check if values returned to original
    for budget in postmodifybudgets:
      
      controlbudget = beginningbudgets_control.get(id = budget.id)
      
      self.assertEqual ( controlbudget.budgetstatus, budget.budgetstatus )
      self.assertEqual ( controlbudget.budgetname, budget.budgetname )
      self.assertEqual ( controlbudget.budgetamount, budget.budgetamount )
      
      
    
  @skipIf ( 't005' in excludeset, 'Excluding test t005' )
  def test_t005_wad_Budget_create_remove_sync( self ):
    
    client = adwords.AdWordsClient.LoadFromStorage()
    
    # create the budgets in aw and django
    newbudget0 = Budget ( budgetname='test005_budget0name0' )
    newbudget1 = Budget ( budgetname='test005_budget1name1' )
    newbudget2 = Budget ( budgetname='test005_budget2name2' )
    
    newbudget0.save(  )
    newbudget1.save(  )
    newbudget2.save(  )
    
    # remove the budgets from aw
    Budget._aw_removebudget ( client, newbudget0.budgetid )
    Budget._aw_removebudget ( client, newbudget1.budgetid )
    Budget._aw_removebudget ( client, newbudget2.budgetid )
    
    #Budget.removebudget ( client, newbudget0.budgetid )
    #Budget.removebudget ( client, newbudget1.budgetid )
    #Budget.removebudget ( client, newbudget2.budgetid )
    
    
    # sync with django db
    Budget.sync ( client )
    
    
    return
    
    
  @skipIf ( 't006' in excludeset, 'Excluding test t006' )
  def test_t006_wad_Budget_pre_init ( self ):
    
    return
    
    # try to init a new budget with the same name as the setup/teardown budget   
    with self.assertRaises ( suds.WebFault ):
      newbudget0 = Budget ( budgetname='test_setup_budget0' )
    
    
    
#    try:
#      budget0 = Budget ( )
#    except Error as e:
#      print ( e )
    
  @skipIf ( 't007' in excludeset, 'Excluding test t007' )
  def test_t007_wad_Budget_save ( self ):
    
    # save a new instance
    
    newbudget0 = Budget ( budgetname='test007_budget0name0' )
    newbudget0.save(  )
    
    newbudget0.delete()
    
    # modify an existing instance
    
    
    
    
    
#    try:
#      newbudget0 = Budget ( budgetname='test_setup_budget0' )
#    except:
#      pass
    
    
                          
                          
    
    
    
    
    
    
    
    
    