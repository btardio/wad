from django.db import models
import suds
from wad_Common.query import list_from_query
from django.core.exceptions import ObjectDoesNotExist
from wad_Budget.models import Budget

# Create your models here.

# TODO: check for existing campaigns in django before adding a new 
#       one of same name/id

class Campaign(models.Model):
  """
  The Campaign class stores campaign id, campaign status, campaign
  name, campaign ad channel type and a foreign key to 
  wad_Budget.Budget. The class uses the Google AdWords CampaignService
  to make mutate calls and queries.
  """
  
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
  
  # selector: Id
  campaignid = models.BigIntegerField(unique=True,
                                      help_text='AdWords Campaign ID')
  
  # selector: Status
  campaignstatus = models.CharField(max_length=20, 
                                    choices=STATE_CHOICES,
                                    help_text='Campaign Status')
  
  # selector: Name
  campaignname = models.CharField(max_length=255, 
                                  help_text='Campaign name')
  
   # selector: AdvertisingChannelType
  campaignadchanneltype = models.CharField(max_length=13, 
                                           editable = False,
                                           help_text='Ad Channel Type')
  
  campaignbudget = models.ForeignKey ( Budget, 
                                       related_name='budget', 
                                       related_query_name='budget',
                                       on_delete=models.PROTECT,
                                       help_text='wad_Budget.Budget.',
                                       default=None,
                                       null=True,
                                       blank=True)
  
  campaigntargetgooglesearch = models.BooleanField ( default = True )
  campaigntargetsearchnetwork = models.BooleanField ( default = False )
  campaigntargetcontentnetwork = models.BooleanField ( default = True )
  
  internalcampaigncreationdate = models.DateTimeField(auto_now_add=True)
  internalcampaignrefreshdate = models.DateTimeField(auto_now=True)


  class Meta:
    app_label = 'wad_Campaign'

  #
  # Returns the service obj
  #
  @staticmethod
  def serviceobj( client ):
    """
    Returns the CampaignService object
        
    Note \: Does not affect the Django database.
    
    **Parameters**
    
    client \: googleads.adwords.AdWordsClient object
      The client to request API service from.
      
    **Returns**
    
    googleads.common.SudsServiceProxy \: the CampaignService object
    """

    return client.GetService('CampaignService', version='v201609')

  #
  # Returns the query text for querying adwords api
  #
  @staticmethod
  def querytext():
    """
    Returns the query text for querying adwords api
    
    Ignores campaigns with REMOVED status
        
    Note \: Does not affect the Django database.
    
    **Parameters**
    
    None
      
    **Returns**
    
    str \: the AWQL query string
    """

    rval = 'SELECT Id, Status, Name, BudgetId, BudgetName, Amount, BudgetReferenceCount,'
    rval += ' DeliveryMethod, BudgetStatus, AdvertisingChannelType,'
    rval += ' TargetGoogleSearch, TargetSearchNetwork, TargetContentNetwork'
    rval += ' WHERE Status != "REMOVED"'
    return rval
  
  
  @staticmethod
  def listcampaigns ( client ):
    """
    Return a list of campaigns as suds dictionary objects.
    
    Makes a call to the AdWords API using AWQL requesting Id, 
    Status, Name, BudgetId, BudgetName, Amount, DeliveryMethod, 
    BudgetStatus WHERE Status != "REMOVED"
    
    Note \: Does not affect the Django database.
    
    **Parameters**
    
    client \: googleads.adwords.AdWordsClient object
      The client to request API service from.

    **Returns**
    
    suds[] \: list of campaigns as suds dictionary objects
    """

    # request a service object from the client object
    service = Campaign.serviceobj ( client )
    
    querytext = Campaign.querytext()
    
    rslts = list_from_query ( client, service, querytext )
    
    return rslts
    
  
  
  #
  # Returns the dictionary needed to add a campaign
  #
  @staticmethod
  def adddict(incampaignname, incampaignstatus, incampaignadchanneltype, inbudget, 
              campaigntargetgooglesearch, campaigntargetsearchnetwork,
              campaigntargetcontentnetwork):
    """
    Return a dictionary object for adding a campaign to the AdWords API.
    
    Uses operator ADD and OPERAND name, status, 
    biddingStrategyConfiguration, advertisingChannelType and
    budget - constructs an AdWords/suds compatible dictionary
    
    Verifies that the incampaignstatus and incampaignadchanneltype are
    valid.
    
    Note \: Does not affect the Django database.
    
    **Parameters**
    
    incampaignname \: str
      The name of the campaign
    incampaignstatus \: str
      The campaign status, either PAUSED, ENABLED or REMOVED
    incampaignadchanneltype \: str
      The channel that the ad will appear on, either SEARCH, 
      DISPLAY, SHOPPING, MULTI_CHANNEL
    inbudget \: wad_Budget.Budget
      An instance of type wad_Budget.Budget representing the 
      shared budget that the campaign will use.
    campaigntargetgooglesearch \: Boolean
      google.com search results trigger ads
    campaigntargetsearchnetwork \: Boolean
      target search network triggers ads
    campaigntargetcontentnetwork \: Boolean
      target content network triggers ads
      
    Note \: AdWords prohibits Ad Channel Type being modified after 
    creation.
      
    **Returns**
    
    dict{} \: add campaign dictionary 
    """
    
    if ( incampaignstatus != 'PAUSED' and 
         incampaignstatus != 'ENABLED' and
         incampaignstatus != 'REMOVED' ):
      errorstr = 'Received "%s" value for campaign' % incampaignstatus
      errorstr = ' status, expected paused or enabled.'
      raise AttributeError( errorstr )
    
    if ( incampaignadchanneltype != 'SEARCH' and 
         incampaignadchanneltype != 'DISPLAY' and 
         incampaignadchanneltype != 'SHOPPING' and
         incampaignadchanneltype != 'MULTI_CHANNEL' ):
      errorstr = 'Received "%s" value for ' % incampaignadchanneltype
      errorstr = 'campaign channel type, expected search display '
      errorstr = 'shopping or multi channel.'
      raise AttributeError( errorstr )
    
    rval = {
      'operator': 'ADD',
      'operand': {
        'name': incampaignname,
        'status': incampaignstatus,
        'biddingStrategyConfiguration':{'biddingStrategyType':'MANUAL_CPC'},
        'advertisingChannelType': incampaignadchanneltype,
        'budget': inbudget.asdict(),
        'networkSetting': {
          'targetGoogleSearch': campaigntargetgooglesearch,
          'targetSearchNetwork': campaigntargetsearchnetwork,
          'targetContentNetwork': campaigntargetcontentnetwork,
          },
        },
      
      }
    
    return rval

  #
  # Returns the dictionary needed to modify a budget
  #
  @staticmethod
  def modifydict (incampaignid, incampaignname, incampaignstatus, inbudget,
                  campaigntargetgooglesearch, campaigntargetsearchnetwork,
                  campaigntargetcontentnetwork ):
    
    """
    Return a dictionary object for modifying a campaign in the 
    AdWords API. 
    
    Using operator SET and OPERAND id, name, status, 
    biddingStrategyConfiguration, advertisingChannelType and 
    budget, constructs an AdWords/suds compatible dictionary.
    
    Note \: Does not affect the Django database. 
    
    **Parameters** 

    incampaignid \: str
      The AdWords id of the campaign
    incampaignname \: str
      The name of the campaign
    incampaignstatus \: str
      The campaign status, either PAUSED, ENABLED or REMOVED
    inbudget \: wad_Budget.Budget
      An instance of type wad_Budget.Budget representing the 
      shared budget that the campaign will use.

    Note \: AdWords prohibits Ad Channel Type being modified after 
    creation.

    **Returns**
    
    dict{} \: modify campaign dictionary
    """
    
    if incampaignid == None:
      raise AttributeError( 'Non-null value for campaign id is required.' )
    
    operand = { }
    operand['id'] = incampaignid
    if incampaignname != None: operand['name'] = incampaignname
    if incampaignstatus != None: operand['status'] = incampaignstatus
    if inbudget != None: operand['budget'] = inbudget.asdict()

    networksetting = None
    if ( campaigntargetgooglesearch != None or 
         campaigntargetsearchnetwork != None or
         campaigntargetcontentnetwork != None ):
      
      networksetting = {}
      
      if campaigntargetgooglesearch != None: 
        networksetting['targetGoogleSearch'] = campaigntargetgooglesearch
      if campaigntargetsearchnetwork != None:
        networksetting['targetSearchNetwork'] = campaigntargetsearchnetwork
      if campaigntargetcontentnetwork != None:
        networksetting['targetContentNetwork'] = campaigntargetcontentnetwork
    
    if networksetting != None:
      operand['networkSetting'] = networksetting
    
    rval = {
      'operator': 'SET',
      'operand': operand,
      }

#        {
#        'id': incampaignid,
#        'name': incampaignname,
#        'status': incampaignstatus,
#        'biddingStrategyConfiguration':{'biddingStrategyType':'MANUAL_CPC'},
#        'budget': inbudget.asdict(),
#        },


    return rval


  #
  # Returns the dictionary needed to delete a campaign
  #
  @staticmethod
  def deldict ( incampaignid ):
    """
    Return a dictionary object for deleting a campaign from the 
    AdWords API.
    
    Using operator SET and OPERAND id and status, constructs
    an AdWords/suds compatible dictionary.

    This function sets the campaign status to removed, there is
    no way to completely delete a campaign.
    
    Note \: Does not affect the Django database.
    
    **Parameters**
    
    inbudgetid \: str
      The id of the campaign to delete.

    **Returns**
    
    dict{} \: delete campaign dictionary 
    """

    rval = {
      'operator': 'SET',
      'operand': {
        'id': incampaignid,
        'status': Campaign.STATE_REMOVED
        }
      }
    
    return rval
   
  @staticmethod
  def _aw_addcampaign ( client, 
                        incampaignname, 
                        incampaignbudget = None,
                        incampaignstatus = None, 
                        incampaignadchanneltype = None,
                        incampaigntargetgooglesearch = None,
                        incampaigntargetsearchnetwork = None,
                        incampaigntargetcontentnetwork = None ):
    """
    Add an AdWords campaign entry.
    
    Attempts to add a campaign to AdWords. 
    Does not check if the campaign exists.

    Note \: Does not affect the Django database.
        
    **Parameters**
    
    client \: googleads.adwords.AdWordsClient object
      The client to request API service from.
    incampaignname \: str
      The campaign name.
    incampaignbudget \: wad_Budget.Budget
      An instance of type wad_Budget.Budget representing the 
      shared budget that the campaign will use.
    incampaignstatus \: str
      Enumerated str type, either REMOVED, PAUSED, ENABLED, TESTING
    incampaignadchanneltype \: str
      Enumerated ad channel type, either SEARCH, DISPLAY, SHOPPING,
      MULTI_CHANNEL

    Note \: AdWords prohibits Ad Channel Type being modified after 
    creation.

    **Returns**
    
    suds.sudsobject.Campaign \: newly created suds Campaign instance
    or
    suds.WebFault \: error message

    """

    rval = None
    newbudget = None
    
    # set default campaign status if one is not specified
    if incampaignstatus == None:
      incampaignstatus = Campaign.STATE_ENABLED
    
    # set default campaign channel type if one is not specified
    if incampaignadchanneltype == None:
      incampaignadchanneltype = Campaign.TYPE_AD_CHAN_SEARCH

    if incampaigntargetgooglesearch == None:
      incampaigntargetgooglesearch = True
      
    if incampaigntargetsearchnetwork == None:
      incampaigntargetsearchnetwork = False
      
    if incampaigntargetcontentnetwork == None:
      incampaigntargetcontentnetwork = False
      
    # create a new budget if one is not specified
    if incampaignbudget == None or not isinstance ( incampaignbudget, Budget ):
      incampaignbudget = Budget.addbudget( client, 'budget_for_%s' % incampaignname )

    # request a service object from the client object
    service = Campaign.serviceobj ( client )
    
    # create the mutate string
    mutatestring = Campaign.adddict ( incampaignname, 
                                      incampaignstatus, 
                                      incampaignadchanneltype,
                                      incampaignbudget,
                                      incampaigntargetgooglesearch,
                                      incampaigntargetsearchnetwork,
                                      incampaigntargetcontentnetwork,
                                    )
    
    client.validate_only = True # set this to true to test for errors
    success = False # assume failure, change the value for success

    try:
      # call mutate
      rslts = service.mutate ( [mutatestring] )
      
      # if there is a partial failure or success,
      # the var success will be set to true
      success = True
      
    except suds.WebFault as e:
      # if there is an error print the error
      print ( 'Add campaign failed: %s' % e )

    # if the mutate was successful set validate_only to False
    if success: 
      
      client.validate_only = False
      
      # make the mutate call
      rslts = service.mutate ( [mutatestring] )

      rval = rslts['value'][0]

      # print the results
      print ( 'Campaign %s %s added to AdWords.' % (rval['id'],
                                                  rval['name']) )
    
    return rval
    


  @staticmethod
  def addcampaign ( client, incampaignname, 
                    incampaignbudget = None,
                    incampaignstatus = None,
                    incampaignadchanneltype = None,
                    incampaigntargetgooglesearch = None,
                    incampaigntargetsearchnetwork = None,
                    incampaigntargetcontentnetwork = None ):
    """
    Add an AdWords campaign entry.
    
    Attempts to add a campaign to AdWords. 
    Does not check if the campaign exists.
    If it is successful adding the campaign
    to Ad Words, it also adds a campaign to 
    Django DB.
        
    **Parameters**
    
    client \: googleads.adwords.AdWordsClient object
      The client to request API service from.
    incampaignname \: str
      The campaign name.
    incampaignbudget \: wad_Budget.Budget
      An instance of type wad_Budget.Budget representing the 
      shared budget that the campaign will use.
    incampaignstatus \: str
      Enumerated str type, either REMOVED, PAUSED, ENABLED, TESTING

    Note \: AdWords prohibits Ad Channel Type being modified after 
    creation.

    **Returns**
    
    wad_Campaign.Campaign \: newly created Campaign instance

    """

    if incampaignstatus == None:
      incampaignstatus = Campaign.STATE_ENABLED
    
    if incampaignadchanneltype == None:
      incampaignadchanneltype = Campaign.TYPE_AD_CHAN_SEARCH

    if incampaigntargetgooglesearch == None:
      incampaigntargetgooglesearch = True
      
    if incampaigntargetsearchnetwork == None:
      incampaigntargetsearchnetwork = False
      
    if incampaigntargetcontentnetwork == None:
      incampaigntargetcontentnetwork = False
      
    # create a new budget if one is not specified
    if incampaignbudget == None or not isinstance ( incampaignbudget, Budget ):
      incampaignbudget = Budget.addbudget( client, 'budget_for_%s' % incampaignname )

    # Add new Django database entry for the newly added AdWords campaign
    # add it here because init checks adwords to see if it's possible to
    # enter this item, adwords does not let you ad an item that has same
    # name as their db
    newcampaign = Campaign(
      campaignid = None,
      campaignname = incampaignname,
      campaignadchanneltype = incampaignadchanneltype,
      campaignstatus = incampaignstatus,
      campaignbudget = incampaignbudget,
      campaigntargetgooglesearch = incampaigntargetgooglesearch,
      campaigntargetsearchnetwork = incampaigntargetsearchnetwork,
      campaigntargetcontentnetwork = incampaigntargetcontentnetwork,
      )
    
    addcampaignobj = Campaign._aw_addcampaign ( client, incampaignname, incampaignbudget, 
                                                incampaignstatus )
    
    if addcampaignobj != None:

      # the unsaved db object needs updated after _aw_addcampaign if method paramaters were none
      newcampaign.campaignid = addcampaignobj['id']
      
      # finally we are ready to save the database instance
      newcampaign.save( sync_aw=False )
    
      print ( 'Campaign %s %s added to Django.' % (addcampaignobj['id'],
                                                 addcampaignobj['name']) )

    else:
      
      print ( 'Failed to add Campaign ( campaignname="%s" ... )' % incampaignname )
      
    return newcampaign
  


  
  @staticmethod
  def _aw_removecampaign ( client, incampaignid ):
    """
    Remove an AdWords campaign entry.
    
    Attempts to remove a campaign from AdWords. Does not 
    check if the campaign exists.
    
    **Parameters**
    
    client \: googleads.adwords.AdWordsClient object
      The client to request API service from.
    incampaignid \: str 
      The id of the campaign.

    **Returns**
    
    <class 'suds.sudsobject.CampaignReturnValue'> \: Returns the 
    results of the delete operation / the deleted Campaign object
    or
    suds.WebFault \: error message
    
    """

    # request a service object from the client object
    service = Campaign.serviceobj ( client )
    
    # create the mutate string
    mutatestring = Campaign.deldict ( incampaignid )
    
    client.validate_only = True # set this to true to test for errors
    success = False # assume failure, change the value for success

    rslts = ''

    try:
      
      # call mutate
      rslts = service.mutate ( [mutatestring] )
      
      # if there is a partial failure or success 
      # the var success will be set to true
      success = True

    except suds.WebFault as e:
      # if there is an error print the error
      print ( 'Remove campaign failed: %s' % e )
      return e

    # if the mutate was successful set validate_only to False
    if success: 
      
      client.validate_only = False
      
      # make the mutate call
      rslts = service.mutate ( [mutatestring] )

      # print the results
      print ( 'Campaign %s %s removed from AdWords.' % (rslts['value'][0]['id'],
                                                      rslts['value'][0]['name']) )
      
    return rslts
  
  
  @staticmethod
  def removecampaign ( client, incampaignid ):
    """
    Remove an AdWords campaign entry.
    
    Attempts to remove a campaign from AdWords. Does not 
    check if the campaign exists. If it is successful it
    also tries to remove the campaign from Django.
    
    **Parameters**
    
    client \: googleads.adwords.AdWordsClient object
      The client to request API service from.
    incampaignid \: int 
      The id of the campaign.

    **Returns**
    
    wad_Campaign.Campaign \: Returns the deleted Campaign instance
    
    """

    djangocampaign = None
    
    rslts = Campaign._aw_removecampaign ( client, incampaignid )
    
    if 'value' in rslts:
       
      # Delete Django database entry if it exists for the deleted AdWords campaign
      try:
        djangocampaign = Campaign.objects.get(campaignid = rslts['value'][0]['id'])
      except ObjectDoesNotExist:
        print ( 'Tried to remove campaign %s %s but it did not exist in Django.' % (rslts['value'][0]['id'],
                                                       rslts['value'][0]['name'] ) )
      
      if djangocampaign != None: 
        djangocampaign.delete(sync_aw=False)
        print ( 'Campaign %s %s removed from Django.' % (rslts['value'][0]['id'],
                                                       rslts['value'][0]['name'] ) )
            
    return djangocampaign
  

  @staticmethod
  def sync ( client ):
    """
    Synchronize AdWords campaigns with Django.
    
    Queries all campaigns in AdWords and inserts, deletes or modifies
    Django database entries corresponding to the AdWords entries.
    
    Note \: AdWords campaigns with status "REMOVED" are not sychronized.
    
    **Parameters**
    
    client \: googleads.adwords.AdWordsClient object
      The client to request API service from.

    **Returns**
    
    class \: { rremoved[], rmodified[], radded[] }
      rremoved \: list of instances removed from Django
      rmodified \: list of instances modified in Django
      radded \: list of instances added to Django
    """
    
    class rvalc ():
      rremoved = []
      rmodified = []
      radded = []

    rval = rvalc()

    service = Campaign.serviceobj( client )
    
    query = Campaign.querytext()
    
    rslt = list_from_query ( client, service, query )
    
    for awcampaignobj in rslt:      
      
      # if the campaign has not been marked as 'REMOVED'
      if awcampaignobj['status'] != 'REMOVED':
      
        try:

          #
          # Update existing Django values from AdWords account.
          #
          # campaignamount, campaignname, campaignstatus

          # get current values from Django database
          obj = Campaign.objects.get ( 
            campaignid = awcampaignobj['id'] )
          
          updated = False
          
          # todo: update delivery method
          
          if obj.campaignname != awcampaignobj['name']:

            obj.campaignname = awcampaignobj['name']

            print ( 'Updated campaign %s %s name in Django database.' % 
                     ( obj.campaignid, obj.campaignname ) )

            updated = True          
          
          if obj.campaignstatus != awcampaignobj['status']:
            
            obj.campaignstatus = awcampaignobj['status']
            
            print ( 'Updated campaign %s %s status in Django database.' % 
                    ( obj.campaignid, obj.campaignname ) )
            
            updated = True

          print ( awcampaignobj )

          if obj.campaigntargetgooglesearch != awcampaignobj['networkSetting']['targetGoogleSearch']:
            
            obj.campaigntargetgooglesearch = awcampaignobj['networkSetting']['targetGoogleSearch']
            
            print ( 'Updated campaign %s %s targetGoogleSearch in Django database.' % 
                    ( obj.campaignid, obj.campaignname ) )
            
            updated = True
            
          if obj.campaigntargetsearchnetwork != awcampaignobj['networkSetting']['targetSearchNetwork']:
            
            obj.campaigntargetsearchnetwork = awcampaignobj['networkSetting']['targetSearchNetwork']
            
            print ( 'Updated campaign %s %s targetSearchNetwork in Django database.' % 
                    ( obj.campaignid, obj.campaignname ) )
            
            updated = True

          if obj.campaigntargetcontentnetwork != awcampaignobj['networkSetting']['targetContentNetwork']:
            
            obj.campaigntargetcontentnetwork = awcampaignobj['networkSetting']['targetContentNetwork']
            
            print ( 'Updated campaign %s %s targetContentNetwork in Django database.' % 
                    ( obj.campaignid, obj.campaignname ) )
            
            updated = True
          
          # if we are syncing a campaign that has a different budget id
          if obj.campaignbudget.budgetid != awcampaignobj['budget']['budgetId']:
                        
            # check if the new budget id exists in Django
            try:
              # if it exists use the existing one
              obj.campaignbudget = Budget.objects.get ( budgetid = awcampaignobj['budget']['budgetId'] )            
              
              obj.save ( sync_aw = False )
              
            except ObjectDoesNotExist:
              # if it doesn't exist use a new one
              obj.campaignbudget = Budget ( budgetid = awcampaignobj['budget']['budgetId'],
                                            budgetname = awcampaignobj['budget']['budgetName'],
                                            budgetamount = awcampaignobj['budget']['budgetAmount'],
                                            budgetdeliverymethod = awcampaignobj['budget']['deliveryMethod'],
                                            budgetstatus = awcampaignobj['budget']['status'], )
              
              obj.campaignbudget.save()
              
              obj.save ( sync_aw = False )
              
            print ( 'Updated campaign %s %s campaign budget in Django database.' % 
                    (obj.campaignid, obj.campaignamount ) )   
          
            updated = True
            
          #if ( obj.campaignbudget.budgetname != awcampaignobj['budget']['budgetName'] or 
               #obj.campaignbudget.budgetamount != awcampaignobj['budget']['budgetAmount'] or 
               #obj.campaignbudget.budgetdeliverymethod != awcampaignobj['budget']['deliveryMethod'] or 
               #obj.campaignbudget.budgetstatus != awcampaignobj['budget']['status'] ):
            
            #Budget.sync ( obj.campaignbudget.budgetid )
            
            
          if updated == True:
            obj.save( sync_aw=False )
            rval.rmodified.append(obj)
        
        except ObjectDoesNotExist:

          #
          # Add new Django values from AdWords account.
          #
          
          # create / sync the budget associated with the new campaign
          budget = None
          
          # query the django database to see if the budget exists in the database
          try:
            budget = Budget.objects.get ( budgetid = awcampaignobj['budget']['budgetId'] )
            
          # if the budget doesn't exist create it in django db with sync_aw=False
          except ObjectDoesNotExist:
            budget = Budget ( budgetid = awcampaignobj['budget']['budgetId'],
                              budgetname = awcampaignobj['budget']['name'],
                              budgetdeliverymethod = awcampaignobj['budget']['deliveryMethod'],
                              budgetstatus = awcampaignobj['budget']['status'],
                              budgetamount = awcampaignobj['budget']['amount']['microAmount'] )
            budget.save ( sync_aw = False )
          
          newcampaign = Campaign(
            campaignid = awcampaignobj['id'],
            campaignstatus = awcampaignobj['status'],
            campaignname = awcampaignobj['name'],
            campaignbudget = budget,
            campaignadchanneltype = awcampaignobj['advertisingChannelType'],
            )
          
          newcampaign.save( sync_aw = False )
          print ( 'Added campaign %s %s to Django database.' % 
                  ( newcampaign.campaignid, newcampaign.campaignname ) )
        
          rval.radded.append(newcampaign)
    
    #
    # Remove old Django values according to AdWords account.
    # remove any old campaigns from Django db that don't exist in 
    # adwords anymore
    #
    
    # make a list of awcampaignobj ids
    awcampaignobjids = []
    for awcampaignobj in rslt:
      if awcampaignobj['status'] != 'REMOVED':
        awcampaignobjids.append ( awcampaignobj['id'] )
      
    # iterate Django db entries and check if the entry exists 
    # in adwords, remove the entry if it doesn't exist
    for dbcampaignobj in Campaign.objects.all ( ):
      if dbcampaignobj.campaignid not in awcampaignobjids:
        dbcampaignobj.delete()
        print ( 'Deleted campaign %s %s from Django database.' % 
                ( dbcampaignobj.campaignid, dbcampaignobj.campaignname ) )
        rval.rremoved.append ( dbcampaignobj )
        
        
    return rval


        
  def save(self, *args, **kwargs):

    # TODO: create a campaign budget in advance of save
    
#    print ( 'save' )
#    print ( dir ( self ) )
#    print ( self.campaignbudget )
#    print ( type ( self.campaignbudget ) )
    
    try:
      dvar = self.campaignbudget
    except ObjectDoesNotExist:
      newbudget = Budget ( budgetname = 'budget_for_%s' % self.campaignname, 
                           budgetamount = 20000000 )
      newbudget.save()
      self.campaignbudget = newbudget
     
    
#    if self.campaignname == '' or self.campaignname == None:
#      raise AttributeError( 'Saving a budget without required attribute campaignname' )
    
#    if not isinstance ( self.campaignbudget, Budget ):
#      errorstr = 'Saving a campaign with a campaignbudget not of type Budget, '
#      errorstr += 'campaigns must be connected with a valid Budget instance.'
#      raise AttributeError( errorstr )

    
    
#    # create a new budget if one is not specified
#    if ( self.campaignbudget == None or self.campaignbudget == '' ):
#      newbudget = Budget ( budgetname = 'budget_for_%s' % self.campaignname, 
#                           budgetamount = 20000000 )
#      newbudget.save()
#      self.campaignbudget = newbudget

    # if snyc_aw is in the arguments for save, assign it to a member
    # variable of self for pre_save and pop it
    if 'sync_aw' in kwargs:
      self.sync_aw = kwargs['sync_aw']
      kwargs.pop('sync_aw')
    else:
      self.sync_aw = True
    
    super(Campaign, self).save(*args, **kwargs)

  
  def delete(self, *args, **kwargs):
    
    # TODO: 'keep_budget' default = True
    #       if 'keep_budget' is false, try to remove budget entry
    
    # if snyc_aw is in the arguments for save, assign it to a member
    # variable of self for pre_save and pop it
    if 'sync_aw' in kwargs:
      self.sync_aw = kwargs['sync_aw']
      kwargs.pop('sync_aw')
    else:
      self.sync_aw = True
    
    super(Campaign, self).delete(*args, **kwargs)
    
  
  #@staticmethod
  #def sync( client ):
    
    #service = Campaign.serviceobj( client )
    
    #query = Campaign.querytext()
    
    #rslt = list_from_query ( client, service, query )
    
    ##print ( rslt )
    
    #for awcampaignobj in rslt:
    
    ## TODO: Write test to make sure these are syncing and deleting as intended
      
      #try:

        ##
        ## Update existing Django values from AdWords account.
        ##

        #obj = Campaign.objects.get ( campaignid = awcampaignobj['id'] )
        
        ## create mutate object using status, name
        ## sync will update Django from AdWords
        ## updating Adwords from Django will happen in Django admin, the save button
        
        #if obj.campaignstatus != awcampaignobj['status']:
          #print ( 'Updated campaign %s status in Django databse.' % obj.campaignid )
          #obj.campaignstatus = awcampaignobj['status']
          
        #if obj.campaignname != awcampaignobj['name']:
          #print ( 'Updated campaign %s name in Django databse.' % obj.campaignid )
          #obj.campaignname = awcampaignobj['name']
          
        #obj.save()
        
        #print ( awcampaignobj )
      
      #except ObjectDoesNotExist:

        ##
        ## Add new Django values from AdWords account.
        ##
        
        #newcampaign = Campaign ( campaignid = awcampaignobj['id'],
                                 #campaignstatus = awcampaignobj['status'],
                                 #campaignname = awcampaignobj['name'] )
        #newcampaign.save()
        #print ( 'Added campaign %s to Django database.' % newcampaign.campaignid )
        
    ##
    ## Remove old Django values according to AdWords account.
    ## remove any old campaigns from Django db that don't exist in adwords anymore
    ##
    
    ## make a list of awcampaignobj ids
    #awcampaignobjids = []
    #for awcampaignobj in rslt:
      #awcampaignobjids.append ( awcampaignobj['id'] )
      
    ## iterate Django db entries and check if the entry exists in adwords, 
    ## remove the entry if it doesn't exist
    #for dbcampaignobj in Campaign.objects.all ( ):
      #if dbcampaignobj.campaignid not in awcampaignobjids:
        #print ( 'Deleted campaign %s from Django database.' % dbcampaignobj.id )
        #dbcampaignobj.delete()
        
      
    
    
    
    
    
    
    
    
    
    
    