from django.dispatch import receiver
from django.db.models.signals import pre_init, pre_save, pre_delete
from googleads import adwords
from wad_Campaign.models import Campaign
from wad_Budget.models import Budget
from django.core.signals import request_finished


# TODO: Write debug text for save and delete: ie:
#       Budget 981029927 budget_for_t026_campaign0 removed from Django



@receiver(pre_save, sender=Campaign)
def receiver_pre_save ( **kwargs ):

  #print ( kwargs )

  client = adwords.AdWordsClient.LoadFromStorage()
  service = Campaign.serviceobj ( client )

  instance = kwargs['instance']
  
  # save updates an existing item or instantiates a new item
  # save determines which one based on whether the object
  # has a campaignid != None
  
  
  # this variable is set in the overridden save method, if it is set to
  # false save is probably being called from Campaign.addcampaign 
  # or Campaign.removecampaign, or specified by kwargs
  if ( instance.sync_aw ) :
  
    # set defaults if values are not entered for campaignstatus
    if instance.campaignstatus == None or instance.campaignstatus == '':
      instance.campaignstatus = Campaign.STATE_ENABLED
    
    # set defaults if values are not entered for campaignadchanneltype
    if instance.campaignadchanneltype == None or instance.campaignadchanneltype == '':
      instance.campaignadchanneltype = Campaign.TYPE_AD_CHAN_SEARCH

  
    # we are adding a new item
    if ( instance.id == None ):
      
      # create the mutate string
      mutatestring = Campaign.adddict ( instance.campaignname,
                                        instance.campaignstatus,
                                        instance.campaignadchanneltype,
                                        instance.campaignbudget,
                                        instance.campaigntargetgooglesearch,
                                        instance.campaigntargetsearchnetwork,
                                        instance.campaigntargetcontentnetwork )
          
      rslts = service.mutate ( [mutatestring] )
      
      instance.campaignid = rslts['value'][0]['id']
      
    # we are modifying an item
    else:
      
      # check if the campaignbudget is None, if so raise an error
      if instance.campaignbudget == None:
        errorstr = 'Updating a campaign with a NULL Budget, '
        errorstr += 'campaigns must be connected with a valid Budget instance.'
        raise AttributeError( errorstr )
      
      # check if the campaignbudget is valid, if not raise an error
      if not isinstance ( instance.campaignbudget, Budget ):
        errorstr = 'Updating a campaign with a campaignbudget not of type Budget, '
        errorstr += 'campaigns must be connected with a valid Budget instance.'
        raise AttributeError( errorstr )
      
      # create the mutate string
      mutatestring = Campaign.modifydict ( instance.campaignid,
                                           instance.campaignname,
                                           instance.campaignstatus,
                                           instance.campaignbudget,
                                           instance.campaigntargetgooglesearch,
                                           instance.campaigntargetsearchnetwork,
                                           instance.campaigntargetcontentnetwork )
      
      rslts = service.mutate ( [mutatestring] )
    



    
request_finished.connect(receiver_pre_save, dispatch_uid="campaign_receiver_pre_save_unique_identifier")


@receiver(pre_delete, sender=Campaign)
def receiver_pre_delete ( **kwargs ):

  client = adwords.AdWordsClient.LoadFromStorage()
  service = Campaign.serviceobj ( client )

  instance = kwargs['instance']
  
  # this variable is set in the overridden delete method, if it is set to
  # false save is probably being called from Campaign.addcampaign 
  # or Campaign.removecampaign, or specified by kwargs
  if ( instance.sync_aw ) :
  
    mutatestring = Campaign.deldict ( instance.campaignid )
    
    rslts = service.mutate ( [mutatestring] )
    
    if ( rslts['value'][0]['status'] != 'REMOVED' ):
      raise IOError('Django Adwords did not successfully set the item to "REMOVED"')

  
    
request_finished.connect(receiver_pre_delete, dispatch_uid="campaign_receiver_pre_delete_unique_identifier")
    


