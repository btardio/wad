from django.db import models
from wad_Common.query import list_from_query
from django.core.exceptions import ObjectDoesNotExist
from wad_Budget.models import Budget

# Create your models here.

class Campaign ( models.Model ):

  STATE_ENABLED = 'ENABLED'
  STATE_PAUSED = 'PAUSED'
  STATE_REMOVED = 'REMOVED'
  STATE_TESTING = 'TESTING'
  STATE_CHOICES = (
      (STATE_ENABLED, 'Enabled'),
      (STATE_PAUSED, 'Paused'),
      (STATE_REMOVED, 'Removed'),
      (STATE_TESTING, 'Testing'),
  )
  
  TYPE_AD_CHAN_SEARCH = 'SEARCH'
  TYPE_AD_CHAN_DISPLAY = 'DISPLAY'
  TYPE_AD_CHAN_SHOPPING = 'SHOPPING'
  TYPE_AD_CHAN_MULTI_CHANNEL = 'MULTI_CHANNEL'
  AD_CHAN_CHOICES = (
    (TYPE_AD_CHAN_SEARCH, 'Search Network'),
    (TYPE_AD_CHAN_DISPLAY, 'Display Network'),
    (TYPE_AD_CHAN_SHOPPING, 'Shopping Network'),
    (TYPE_AD_CHAN_MULTI_CHANNEL, 'Multi-Channel Network')
    )
  
  campaignid = models.BigIntegerField(unique=True) # selector: Id
  campaignstatus = models.CharField(max_length=20, choices=STATE_CHOICES) # selector: Status
  campaignname = models.CharField(max_length=255, help_text='Campaign name') # selector: Name
  campaignadchanneltype = models.CharField(max_length=13, help_text='Ad Channel Type') # selector: AdvertisingChannelSubType
  campaignbudget = models.ForeignKey ( Budget, 
                                       related_name='budget', 
                                       related_query_name='budget', 
                                       null = True, on_delete=models.SET_NULL )
  internalcampaigncreationdate = models.DateTimeField(auto_now_add=True)
  internalcampaignrefreshdate = models.DateTimeField(auto_now=True)

  #
  # Returns the service obj
  #
  @staticmethod
  def serviceobj( client ):
    return client.GetService('CampaignService', version='v201609')

  #
  # Returns the query text for querying adwords api
  #
  @staticmethod
  def querytext():
    return 'SELECT Id, Status, Name'
  
  #
  # Returns the dictionary needed to add a campaign
  #
  @staticmethod
  def adddict(incampaignname, incampaignstatus, incampaignadchanneltype):
    
    incampaignstatus = incampaignstatus.upper()
    
    if incampaignstatus != 'PAUSED' and incampaignstatus != 'ENABLED' and incampaignstatus != 'REMOVED':
      raise AttributeError('Received "%s" value for campaign status, expected paused or enabled.' % incampaignstatus)
    
    if ( incampaignadchanneltype != 'SEARCH' and 
         incampaignadchanneltype != 'DISPLAY' and 
         incampaignadchanneltype != 'SHOPPING' and
         incampaignadchanneltype != 'MULTI_CHANNEL' ):
      raise AttributeError('Received "%s" value for campaign channel type, expected search display shopping or multi channel.' % 
                           incampaignadchanneltype)
    
    rval = {
      'operator': 'ADD',
      'operand': {
        'name': incampaignname,
        'status': incampaignstatus,
        'biddingStrategyConfiguration':{'biddingStrategyType':'MANUAL_CPC'},
        'advertisingChannelType': incampaignadchanneltype,
        },
      
      }
    
    return rval
    
  #
  # Returns the dictionary needed to delete a campaign
  #
  @staticmethod
  def deldict ( incampaignid ):
    
    rval = {
      'operator': 'SET',
      'operand': {
        'id': incampaignid,
        'status': Campaign.STATE_REMOVED
        }
      }
    
    return rval
    
  @staticmethod
  def addcampaign ( client, incampaignname, incampaignstatus=None, incampaignchanneltype=None ):

    if incampaignstatus == None:
      incampaignstatus = Campaign.STATE_ENABLED
    
    if incampaignchanneltype == None:
      incampaignchanneltype = Campaign.TYPE_AD_CHAN_SEARCH
    
    service = Campaign.serviceobj ( client )
    
    mutatestring = Campaign.adddict ( incampaignname, incampaignstatus, incampaignchanneltype )
    
    rslts = service.mutate ( [mutatestring] )
    
    print ( rslts )
    
    for rslt in rslts.value:
      print ( 'Campaign %s added.' % rslt['id'] )
    
  
  @staticmethod
  def removecampaign ( client, incampaignid ):
    
    service = Campaign.serviceobj ( client )
    
    mutatestring = Campaign.deldict ( incampaignid )
    
    rslt = service.mutate ( mutatestring )
    
    print ( rslt )
    print ( 'Campaign %s removed.' % incampaignid )
    
    return rslt
    
  
  @staticmethod
  def sync( client ):
    
    service = Campaign.serviceobj( client )
    
    query = Campaign.querytext()
    
    rslt = list_from_query ( client, service, query )
    
    #print ( rslt )
    
    for awcampaignobj in rslt:
    
    # TODO: Write test to make sure these are syncing and deleting as intended
      
      try:

        #
        # Update existing Django values from AdWords account.
        #

        obj = Campaign.objects.get ( campaignid = awcampaignobj['id'] )
        
        # create mutate object using status, name
        # sync will update Django from AdWords
        # updating Adwords from Django will happen in Django admin, the save button
        
        if obj.campaignstatus != awcampaignobj['status']:
          print ( 'Updated campaign %s status in Django databse.' % obj.campaignid )
          obj.campaignstatus = awcampaignobj['status']
          
        if obj.campaignname != awcampaignobj['name']:
          print ( 'Updated campaign %s name in Django databse.' % obj.campaignid )
          obj.campaignname = awcampaignobj['name']
          
        obj.save()
        
        print ( awcampaignobj )
      
      except ObjectDoesNotExist:

        #
        # Add new Django values from AdWords account.
        #
        
        newcampaign = Campaign ( campaignid = awcampaignobj['id'],
                                 campaignstatus = awcampaignobj['status'],
                                 campaignname = awcampaignobj['name'] )
        newcampaign.save()
        print ( 'Added campaign %s to Django database.' % newcampaign.campaignid )
        
    #
    # Remove old Django values according to AdWords account.
    # remove any old campaigns from Django db that don't exist in adwords anymore
    #
    
    # make a list of awcampaignobj ids
    awcampaignobjids = []
    for awcampaignobj in rslt:
      awcampaignobjids.append ( awcampaignobj['id'] )
      
    # iterate Django db entries and check if the entry exists in adwords, 
    # remove the entry if it doesn't exist
    for dbcampaignobj in Campaign.objects.all ( ):
      if dbcampaignobj.campaignid not in awcampaignobjids:
        print ( 'Deleted campaign %s from Django database.' % dbcampaignobj.id )
        dbcampaignobj.delete()
        
      
    
    
    
    
    
    
    
    
    
    
    