from django.core.management.base import BaseCommand, CommandError
from googleads import adwords
from wad_Budget.models import Budget


class Command ( BaseCommand ):
  '''Synchronize Budget models with AdWords account, 
     this command uses AdWords account to overwrite database values.'''
  help = 'Synchronize Budget models with AdWords account,'
  help += ' this command uses AdWords account to overwrite'
  help += ' database values. Equivalent to calling Budget.sync()'
  
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
    
    syncobjs = Budget.sync ( client )
    
    print ( 'modified: %s' % syncobjs.rmodified )
    print ( 'added: %s' % syncobjs.radded )
    print ( 'removed: %s' % syncobjs.rremoved )
      
    print ( 'Budget sync complete. Synced %s budgets.' % 
            len ( Budget.objects.all() ) )
            
    
      
      
      
      
      
      
