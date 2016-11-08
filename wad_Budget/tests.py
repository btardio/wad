from django.test import TestCase
from wad_Budget.models import Budget
from googleads import adwords

# Create your tests here.





class wad_Budget_testcases ( TestCase ):
  
  service = None
  query = None
  rslt = None
  
  def setUp ( self ):
    
    print ()
    
    client = adwords.AdWordsClient.LoadFromStorage()
    
    self.testbudgetid0 = Budget.addbudget ( client, 'newabudget0', 2000000000 )
    self.testbudgetid1 = Budget.addbudget ( client, 'newabudget1', 2000000000 )
    self.testbudgetid2 = Budget.addbudget ( client, 'newabudget2', 2000000000 )

  
  def tearDown ( self ):
    
    client = adwords.AdWordsClient.LoadFromStorage()
    
    Budget.removebudget ( client, self.testbudgetid0 )
    Budget.removebudget ( client, self.testbudgetid1 )
    Budget.removebudget ( client, self.testbudgetid2 )

  
  def test_wad_Budget_add_remove(self):
    
    return
    
    client = adwords.AdWordsClient.LoadFromStorage()
    
    # creates three new budgets
    budget0id = Budget.addbudget ( client, 'newdbudget0', 6000000000 )
    budget1id = Budget.addbudget ( client, 'newdbudget1', 6000000000 )
    budget2id = Budget.addbudget ( client, 'newdbudget2', 6000000000 )
    
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
    


  def test_wad_Budget_sync_add_remove ( self ):
    
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
    budget0id = Budget.addbudget ( client, 'newbbudget0', 7000000000 )
    budget1id = Budget.addbudget ( client, 'newbbudget1', 7000000000 )
    budget2id = Budget.addbudget ( client, 'newbbudget2', 7000000000 )
    
    # sync with django db
    Budget.sync ( client )
    
    # test if the new budgets added to aw are in the Django system
    self.assertEqual ( len ( beginningbudgets ) + 3, len ( Budget.objects.all() ) )
    self.assertEqual ( len ( beginningawbudgetslst ) + 3, len ( Budget.objects.all() ) )
    
    self.assertTrue ( Budget.objects.filter ( budgetname = 'newbbudget0' ).exists() )
    self.assertTrue ( Budget.objects.filter ( budgetname = 'newbbudget1' ).exists() )
    self.assertTrue ( Budget.objects.filter ( budgetname = 'newbbudget2' ).exists() )
    
    # removes the budgets from aw
    Budget.removebudget ( client, budget0id )
    Budget.removebudget ( client, budget1id )
    Budget.removebudget ( client, budget2id )
    
    # sync with django db
    Budget.sync ( client )

    # test if the django budget set is equal to the aw budget set after deletions
    self.assertEqual ( len ( beginningbudgets ), len ( Budget.objects.all() ) )
    self.assertEqual ( len ( beginningawbudgetslst ), len ( Budget.objects.all() ) )
    
    self.assertFalse ( Budget.objects.filter ( budgetname = 'newbbudget0' ).exists() )
    self.assertFalse ( Budget.objects.filter ( budgetname = 'newbbudget1' ).exists() )
    self.assertFalse ( Budget.objects.filter ( budgetname = 'newbbudget2' ).exists() )
    
    
    
  def test_wad_Budget_sync_modify ( self ):
    
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
    
      budget.save()
    
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
      
      
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    