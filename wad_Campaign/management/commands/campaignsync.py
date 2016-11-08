from django.core.management.base import BaseCommand, CommandError
from googleads import adwords
from wad_Campaign.models import Campaign


class Command ( BaseCommand ):
  help = 'Synchronize Campaign models with AdWords account, use AdWords account to overwrite database values.'
  
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
    
    Campaign.sync ( client )
      
    print ( 'Campaign sync complete. Synced %s campaigns.' % len ( Campaign.objects.all() ) )
            
    
      
      
      
      
      
      
