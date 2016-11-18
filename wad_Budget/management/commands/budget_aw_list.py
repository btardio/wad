from django.core.management.base import BaseCommand, CommandError
from googleads import adwords
from wad_Budget.models import Budget


class Command ( BaseCommand ):
  help = 'List all Budget models from database.'
  
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

    rslts = Budget.listbudgets ( client )
    
    for item in rslts:
      print ( item )
          
    print ( 'Budget list complete. Listed %s budgets.' % len ( rslts ) )
            
    
      
      
      
      
      
      
