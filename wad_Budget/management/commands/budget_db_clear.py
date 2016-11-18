from django.core.management.base import BaseCommand, CommandError
from googleads import adwords
from wad_Budget.models import Budget


class Command ( BaseCommand ):
  help = 'Clear all Budget models from database.'
  
  def add_arguments ( self, parser ):
    pass
#    parser.add_argument( 
#      '--sync',
#      action='store_true',
#      dest='syncvar',
#      default=False,
#      help='Sync database data with AdWords API for all campaigns.')
    
    
  def handle ( self, *args, **options ):

    allbudgets = Budget.objects.all()
    
    for budget in allbudgets:
      budget.delete()
          
    print ( 'Budget clear complete. Cleared %s budgets.' % len ( allbudgets ) )
            
    
      
      
      
      
      
      
