from django.core.management.base import BaseCommand, CommandError
from googleads import adwords
from wad_Budget.models import Budget
import suds

class Command ( BaseCommand ):
  help = 'Clear all shared Budgets from AdWords.'
  
  def add_arguments ( self, parser ):
    pass
#    parser.add_argument( 
#      '--sync',
#      action='store_true',
#      dest='syncvar',
#      default=False,
#      help='Sync database data with AdWords API for all campaigns.')
    
    
  def handle ( self, *args, **options ):

    client = adwords.AdWordsClient.LoadFromStorage()

    client.partial_failure = True

    # request a service object from the client object
    service = Budget.serviceobj ( client )
    
    mutatestring_dellst = []
    
    # get a list of the budgets
    budgets = Budget.listbudgets ( client )
    
    # create a list of delete dictionaries
    for budget in budgets:
      mutatestring_dellst.append ( Budget.deldict ( budget['budgetId'] ) )
    
    # call mutate for the list of deletes
    rslts = service.mutate ( mutatestring_dellst )
    
    # removes partial failure errors from rslts['value']
    rsltsvaluelst = []
    for budgetsuccess in rslts['value']:
      if budgetsuccess != "":
        rsltsvaluelst.append( budgetsuccess )
    rslts['value'] = rsltsvaluelst
    
    # prints the results of the clear operation
    print ( 'Budget clear complete. Removed %s budgets.' % len ( rslts['value'] ) )
    print ( 'Removed: ' )
    
    # prints each budget that was successfully removed
    for budgetsuccess in rslts['value']:
      if budgetsuccess != "":
        print ( '%s %s Status: %s' % ( budgetsuccess['budgetId'],
                                       budgetsuccess['name'],
                                       budgetsuccess['status'] ) )
    
    # prints each budget that threw an error
    print ( 'Failed to remove: ' )
    for budgeterror in rslts['partialFailureErrors']:
      print ( '%s %s Reason: %s' % ( budgets[ int ( budgeterror['fieldPath'][11:12] ) ]['budgetId'],
                          budgets[ int ( budgeterror['fieldPath'][11:12] ) ]['name'],
                          budgeterror['errorString'] ) )
     
            
    
      
      
      
      
      
      
