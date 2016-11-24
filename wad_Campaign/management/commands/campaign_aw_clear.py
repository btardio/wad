from django.core.management.base import BaseCommand, CommandError
from googleads import adwords
from wad_Campaign.models import Campaign
import suds

class Command ( BaseCommand ):
  help = 'Clear all shared Campaigns from AdWords.'
  
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
    service = Campaign.serviceobj ( client )
    
    mutatestring_dellst = []
    
    # get a list of the campaigns
    campaigns = Campaign.listcampaigns ( client )
    
    # create a list of delete dictionaries
    for campaign in campaigns:
      mutatestring_dellst.append ( Campaign.deldict ( campaign['id'] ) )
    
    # if there are no campaigns in aw with status != remove, return
    if ( len ( mutatestring_dellst ) == 0 ):
      print ( 'Nothing to delete.' )
      return
    
    # call mutate for the list of deletes
    rslts = service.mutate ( mutatestring_dellst )
    
    # removes partial failure errors from rslts['value']
    rsltsvaluelst = []
    for campaignsuccess in rslts['value']:
      if campaignsuccess != "":
        rsltsvaluelst.append( campaignsuccess )
    rslts['value'] = rsltsvaluelst
    
    # prints the results of the clear operation
    print ( 'Campaign clear complete. Removed %s campaigns.' % len ( rslts['value'] ) )
    print ( 'Removed: ' )
    
    # prints each campaign that was successfully removed
    for campaignsuccess in rslts['value']:
      if campaignsuccess != "":
        print ( '%s %s Status: %s' % ( campaignsuccess['id'],
                                       campaignsuccess['name'],
                                       campaignsuccess['status'] ) )
    
    if 'partialFailureErrors' in rslts:
      # prints each campaign that threw an error
      print ( 'Failed to remove: ' )
      for campaignerror in rslts['partialFailureErrors']:
        print ( '%s %s Reason: %s' % ( campaigns[ int ( campaignerror['fieldPath'][11:12] ) ]['campaignId'],
                            campaigns[ int ( campaignerror['fieldPath'][11:12] ) ]['name'],
                            campaignerror['errorString'] ) )
     
            
    
      
      
      
      
      
      
