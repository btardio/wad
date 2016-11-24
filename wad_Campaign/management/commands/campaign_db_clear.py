from django.core.management.base import BaseCommand, CommandError
from googleads import adwords
from wad_Campaign.models import Campaign


class Command ( BaseCommand ):
  help = 'Clear database data for all campaigns.'
  
  def add_arguments ( self, parser ):
    pass
#    parser.add_argument( 
#      '--clear', 
#      action='store_true', 
#      dest='clearvar',
#      default=False,
#      help='Clear database data for all campaigns.' )
    
    
  def handle ( self, *args, **options ):
    client = adwords.AdWordsClient.LoadFromStorage()
        
    allcampaigns = Campaign.objects.all()
    
    for campaign in allcampaigns:
      campaign.delete()
      
    print ( 'All campaigns deleted.' )      
  
      
      
      
      
      
      
      
      
