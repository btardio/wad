from django.dispatch import receiver
from django.db.models.signals import pre_init, pre_save, pre_delete
from googleads import adwords
from wad_Budget.models import Budget
from django.core.signals import request_finished





@receiver(pre_save, sender=Budget)
def receiver_pre_save ( **kwargs ):

  #print ( kwargs )

  client = adwords.AdWordsClient.LoadFromStorage()
  service = Budget.serviceobj ( client )

  instance = kwargs['instance']
  
  # save updates an existing item or instantiates a new item
  # save determines which one based on whether the object
  # has a budgetid != None
  
  #print ( instance.budgetid )
  #print ( instance.budgetname )
  #print ( instance.budgetamount )
  #print ( instance.budgetdeliverymethod )
  #print ( instance.budgetstatus )
  #print ( instance.id )
  
  #print ( "sync_aw: %s" % instance.sync_aw )
  
  # this variable is set in the overridden save method, if it is set to
  # false save is probably being called from Budget.addbudget 
  # or Budget.removebudget
  if ( instance.sync_aw ) :
  
    # we are adding a new item
    if ( instance.id == None ):
      
      # create the mutate string
      mutatestring = Budget.adddict ( instance.budgetname, 
                                      instance.budgetamount, 
                                      instance.budgetdeliverymethod, 
                                      instance.budgetstatus )
          
      rslts = service.mutate ( [mutatestring] )
      
      instance.budgetid = rslts['value'][0]['budgetId']
      
    # we are modifying an item
    else:
      
      # create the mutate string
      mutatestring = Budget.modifydict ( instance.budgetid,
                                         instance.budgetname, 
                                         instance.budgetamount, 
                                         instance.budgetdeliverymethod, 
                                         instance.budgetstatus )
      
      rslts = service.mutate ( [mutatestring] )
    



    
request_finished.connect(receiver_pre_save, dispatch_uid="receiver_pre_save_unique_identifier")


@receiver(pre_delete, sender=Budget)
def receiver_pre_delete ( **kwargs ):

  client = adwords.AdWordsClient.LoadFromStorage()
  service = Budget.serviceobj ( client )

  instance = kwargs['instance']
  
  mutatestring = Budget.deldict ( instance.budgetid )
  
  rslts = service.mutate ( [mutatestring] )
  
  if ( rslts['value'][0]['status'] != 'REMOVED' ):
    raise IOError('Django Adwords did not successfully set the item to "REMOVED"')

  
    
request_finished.connect(receiver_pre_delete, dispatch_uid="receiver_pre_delete_unique_identifier")
    









# variable that describes the upcoming save operation
# contains:
#   budgetname
#   add new (requires budgetid) | modify (requires nothing)
#   
#   variable that describes what further operations are required to meet the save state
#   note: for Campaign, we will require campaignid, budget
#operationdesc = []




#@receiver(pre_init, sender=Budget)
#def receiver_pre_init ( **kwargs ):

  #print ( kwargs )
  ##print ( kwargs['sender'] )
  
  #sender = kwargs['sender']
  
  #if 'budgetid' in kwargs['kwargs']:
    #print ( kwargs['kwargs']['budgetid'] )
  ##print ( 'preinitcalled:%s' % kwargs['kwargs'] )

  #client = adwords.AdWordsClient.LoadFromStorage()

  ## request a service object from the client object
  #service = Budget.serviceobj ( client )
  
  #inbudgetid = None
  #inbudgetname = None
  #inbudgetamount = None
  #inbudgetdeliverymethod = None
  #inbudgetstatus = None

  #if 'budgetid' in kwargs['kwargs']:
    #inbudgetid = kwargs['kwargs']['budgetid']

  #if 'budgetname' in kwargs['kwargs']:
    #inbudgetname = kwargs['kwargs']['budgetname']
    
  #if 'budgetamount' in kwargs['kwargs']:
    #inbudgetamount = kwargs['kwargs']['budgetamount']
    
  #if 'budgetdeliverymethod' in kwargs['kwargs']:
    #inbudgetdeliverymethod = kwargs['kwargs']['budgetdeliverymethod']
    
  #if 'budgetstatus' in kwargs['kwargs']:
    #inbudgetstatus = kwargs['kwargs']['budgetstatus']

  ## 3 cases
  ##   case 1: we are modifying
  ##   case 2: we are adding
  ##   case 3: we are making up values

  ## case 3
  #if ( inbudgetname == None and inbudgetamount == None and 
       #inbudgetdeliverymethod == None and inbudgetstatus == None ):
    #return

  ## case 1
  ## if inbudgetid is not equal to none, the system is assumed to be
  ## syncing and checking the aw db for that name will always return
  ## a duplicate, when we sync we don't enter values into aw
  #if ( inbudgetid != None ):
    
    ## if we are syncing a save operation doesn't need to add the 
    ## initialized instance to aw, track that we are syncing by setting
    ## internalbooleansync to true
    ##sender.internalbooleansync = True
    
    ## we are modifying
    
    ## mutatestring = Budget.modifydict ( )
    
    #return
  
    
  ## case 2
  ## create the mutate string
  #mutatestring = Budget.adddict ( inbudgetname, 
                                  #inbudgetamount, 
                                  #inbudgetdeliverymethod,
                                  #inbudgetstatus )
  
  #####print ( 'mutatestring:%s' % mutatestring )
  
  #client.validate_only = True # set this to true to test for errors
  
  #rslts = service.mutate ( [mutatestring] )
  
  ##try:
    
    ### call mutate
    ##rslts = service.mutate ( [mutatestring] )
          
  ##except suds.WebFault as e:
    ### if there is an error print the error
    ##print ( 'Add budget failed: %s' % e )



#request_finished.connect(receiver_pre_init, dispatch_uid="receiver_pre_init_unique_identifier")







    
    
      #if 'budgetid' in kwargs['kwargs']:
  #  print ( kwargs['kwargs']['budgetid'] )

  # if instance.budgetid is None we must be adding a new value
  #if ( instance.budgetid == None ):
    
    # request a service object from the client object
    #service = Budget.serviceobj ( client )
    
    # create the mutate string
    #mutatestring = Budget.adddict ( inbudgetname, inbudgetamount, 
    #                                inbudgetdeliverymethod, 
    #                                inbudgetstatus )

  # pre_save calls init again to ensure that if there were values changed,
  # these values are checked
  #receiver_pre_init ( kwargs )

  
  #print ( kwargs )
  
  
  
  #addbudgetobj = Budget._aw_addbudget ( client, inbudgetname, inbudgetamount, 
  #                                    inbudgetdeliverymethod, inbudgetstatus )