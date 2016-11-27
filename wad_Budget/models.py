from django.db import models
import suds
from googleads import adwords
from wad_Common.query import list_from_query
from django.core.exceptions import ObjectDoesNotExist
import pickle

class Budget ( models.Model ):
  """The Budget class stores budgetid, budgetname, budgetamount and 
     budgetstatus corresponding to an AdWords Budget object."""

  class Meta:
    app_label = 'Budget'

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
  
  BUDGET_DELIVERY_STANDARD = 'STANDARD'
  BUDGET_DELIVERY_ACCELERATED = 'ACCELERATED'
  BUDGET_DELIVERY_TESTING = 'TESTING'
  BUDGET_DELIVERY_CHOICES = (
    (BUDGET_DELIVERY_STANDARD, 'Standard'),
    (BUDGET_DELIVERY_ACCELERATED, 'Accelerated'),
    (BUDGET_DELIVERY_TESTING, 'Testing'),
    )

  # selector: BudgetId
  budgetid = models.BigIntegerField(unique=True)
  
  # selector: BudgetName
  budgetname = models.CharField(max_length=255, 
                                help_text='Budget name',
                                unique=True)
  
  budgetamount = models.BigIntegerField(default=20000000) # selector: Amount
  
  # budget delivery method is not a part of Budget, and is not 
  # queryable from budget service
  # selector: DeliveryMethod
  budgetdeliverymethod = models.CharField(max_length=20, 
                                          choices=BUDGET_DELIVERY_CHOICES,
                                          default=BUDGET_DELIVERY_ACCELERATED)
                                          
  # selector: BudgetStatus
  budgetstatus = models.CharField(max_length=20, 
                                  choices=STATE_CHOICES,
                                  default=STATE_ENABLED) 
  
  internalbudgetrefreshdate = models.DateTimeField(auto_now_add=True)
  
  internalbudgetcreationdate = models.DateTimeField(auto_now_add=True)
  
  internalbooleansync = models.BooleanField(default=False)
  
  #
  # Returns the service obj
  #
  @staticmethod
  def serviceobj( client ):
    """
    Returns the BudgetService object
        
    Note \: Does not affect the Django database.
    
    **Parameters**
    
    client \: googleads.adwords.AdWordsClient object
      The client to request API service from.
      
    **Returns**
    
    googleads.common.SudsServiceProxy \: the BudgetService object
    """
    
    rval = client.GetService('BudgetService', version='v201609')
    
    return rval
  
  
  
  #
  # Returns the query text for querying adwords api
  #
  @staticmethod
  def querytext( budgetid = None ):
    """
    Returns the query text for querying adwords api
    
    Ignores budgets with REMOVED status
        
    Note \: Does not affect the Django database.
    
    **Parameters**
    
    budgetid \: str 
      Optional budgetid for querying a single budget
      
    **Returns**
    
    str \: the AWQL query string
    """
    rval = ''
    
    if budgetid == None:    
      rval = 'SELECT BudgetId, BudgetName, Amount, BudgetStatus'
      rval += ' WHERE BudgetStatus != "REMOVED"'
    else:
      rval = 'SELECT BudgetId, BudgetName, Amount, BudgetStatus'
      rval += ' WHERE BudgetStatus != "REMOVED" AND BudgetId = "%s"' % budgetid
    
    return rval

  #
  # Returns the query text for querying refcount from adwords api
  #
  @staticmethod
  def querytextref():
    """
    Returns the query text for querying adwords api refcount
    
    Ignores budgets with REMOVED status
    
    **Parameters**
    
    None
    
    **Returns**
    
    str \: the AWQL query string
    """
    
    rval = 'SELECT BudgetId, BudgetReferenceCount'
    rval += ' WHERE BudgetStatus != "REMOVED"'
    
    return rval

  #
  # Returns the query text for querying adwords api
  #
  @staticmethod
  def querytextid( inbudgetid ):
    """
    Returns the query text for querying adwords api for a budget
    specified by inbudgetid
    
    Ignores budgets with REMOVED status
        
    Note \: Does not affect the Django database.
    
    **Parameters**
    
    None
      
    **Returns**
    
    str \: the AWQL query string
    """
    rval = 'SELECT BudgetId, BudgetName, Amount, BudgetStatus'
    rval += ' WHERE BudgetId = "%s"' % inbudgetid
    
    return rval


  #
  # Returns the query text for querying adwords api
  #
  @staticmethod
  def querytext_includeremoved():
    """
    Returns the query text for querying adwords api
        
    Note \: Does not affect the Django database.
    
    **Parameters**
    
    None
      
    **Returns**
    
    str \: the AWQL query string
    """
    return 'SELECT BudgetId, BudgetName, Amount, BudgetStatus'


  def asdict(self):
    """
    Return a dictionary object of the wad_Budget.Budget object
    as it would appear in a Google AdWords query. Constructs an 
    AdWords/suds compatible dictionary.
    
    **Parameters**
    
    None 
    
    **Returns**
    
    dict{} \: the dictionary representation of the wad_Budget.Budget 
    object.
    """
    
    
    rval = {
        'budgetId': self.budgetid,
        'name': self.budgetname,
        'amount': {
          'microAmount': self.budgetamount,
          },
        'deliveryMethod': self.budgetdeliverymethod,
        'status': self.budgetstatus,
        }

    return rval
  
  #
  # Returns the dictionary needed to add a budget
  #
  @staticmethod
  def adddict(inbudgetname, inbudgetamount, inbudgetdeliverymethod, inbudgetstatus):
    """
    Return a dictionary object for adding a budget to the AdWords API.
    
    Uses operator ADD and OPERAND name, amount, deliverymethod, 
    status - constructs an AdWords/suds compatible dictionary
    
    Note \: Does not affect the Django database.
    
    **Parameters**
    
    inbudgetname \: str
      The name of the budget
    inbudgetamount \: int / str
      The budget amount in mirco units.
    inbudgetdeliverymethod \: str
      The delivery method, either STANDARD, ACCELERATED, TESTING
    inbudgetstatus \: str
      The budget status, either ENABLED, PAUSED, REMOVED, TESTING
      
    **Returns**
    
    dict{} \: add budget dictionary 
    """

    # if the input delivery method is None, 
    # set it to BUDGET_DELIVERY_ACCELERATED
    if inbudgetdeliverymethod == None:
      inbudgetdeliverymethod = Budget.BUDGET_DELIVERY_ACCELERATED
    
    # if the input state is None, set it to STATE_PAUSED
    if inbudgetstatus == None:
      inbudgetstatus = Budget.STATE_PAUSED
      
    # if the budget amount is None, set a starting budget amount
    if inbudgetamount == None:
      inbudgetamount = 2000000000

    
    rval = {
      'operator': 'ADD',
      'operand': {
        'name': inbudgetname,
        'amount': {
          'microAmount': inbudgetamount,
          },
        'deliveryMethod': inbudgetdeliverymethod,
        'status': inbudgetstatus,
        }
      }

    return rval
    
    
    
  #
  # Returns the dictionary needed to modify a budget
  #
  @staticmethod
  def modifydict (inbudgetid, inbudgetname, inbudgetamount, inbudgetdeliverymethod, inbudgetstatus ):
    """
    Return a dictionary object for modifying a budget in the 
    AdWords API. 
    
    Using operator SET and OPERAND budgetId, name, amount, 
    deliveryMethod and status, constructs an AdWords/suds 
    compatible dictionary. 
    
    Note \: Does not affect the Django database. 
    
    **Parameters** 

    inbudgetid \: int / str
      The id of the budget to modify.
    inbudgetname \: str
      The name of the budget
    inbudgetamount \: int / str
      The budget amount in mirco units.
    inbudgetdeliverymethod \: str
      The delivery method, either STANDARD, ACCELERATED, TESTING
    inbudgetstatus \: str
      The budget status, either ENABLED, PAUSED, REMOVED, TESTING
      
    **Returns**
    
    dict{} \: modify budget dictionary
    """
    
    rval = {
      'operator': 'SET',
      'operand': {
        'budgetId': inbudgetid,
        'name': inbudgetname,
        'amount': {
          'microAmount': inbudgetamount,
          },
        'deliveryMethod': inbudgetdeliverymethod,
        'status': inbudgetstatus,
        }
      }

    return rval
    
  #
  # Returns the dictionary needed to delete a budget
  #
  @staticmethod
  def deldict ( inbudgetid ):
    """
    Return a dictionary object for deleting a budget from the 
    AdWords API.
    
    Using operator REMOVE and OPERAND inbudgetid, constructs 
    an AdWords/suds compatible dictionary
    
    Note \: Does not affect the Django database.
    
    **Parameters**
    
    inbudgetid \: int / str
      The id of the budget to delete.

    **Returns**
    
    dict{} \: delete budget dictionary 
    """
    
    rval = {
      'operator': 'REMOVE',
      'operand': {
        'budgetId': inbudgetid,
        },
      }
    
    return rval

  @staticmethod
  def getbudget ( client, inbudgetid ):
    """
    Returns the suds object dict representing the budget specified by
    inbudgetid.
    
    **Parameters**
    
    client \: googleads.adwords.AdWordsClient object
      The client to request API service from.
      
    **Returns**
    
    suds{} \: budget as suds dictionary object
    """
    
    # request a service object from the client object
    service = Budget.serviceobj ( client )
    
    querytext = Budget.querytextid ( inbudgetid )
    
    rslts = list_from_query ( client, service, querytext )
    
    return rslts[0]

  @staticmethod
  def listbudgets ( client ):
    """
    Return a list of budgets as suds dictionary objects.
    
    Makes a call to the AdWords API using AWQL requesting BudgetId, 
    BudgetName, Amount, BudgetStatus WHERE BudgetStatus != "REMOVED"
    
    Note \: Does not affect the Django database.
    
    **Parameters**
    
    client \: googleads.adwords.AdWordsClient object
      The client to request API service from.

    **Returns**
    
    suds[] \: list of budgets as suds dictionary objects
    """

    # request a service object from the client object
    service = Budget.serviceobj ( client )
    
    querytext = Budget.querytext()
    
    rslts = list_from_query ( client, service, querytext )
    
    return rslts
    
  @staticmethod
  def listbudgetsincluderemoved ( client ):
    """
    Return a list of ALL budgets as suds dictionary objects.
    
    Makes a call to the AdWords API using AWQL requesting BudgetId, 
    BudgetName, Amount, BudgetStatus 
    
    Note \: Does not affect the Django database.
    
    **Parameters**
    
    client \: googleads.adwords.AdWordsClient object
      The client to request API service from.

    **Returns**
    
    suds[] \: list of budgets as suds dictionary objects
    """

    # request a service object from the client object
    service = Budget.serviceobj ( client )
    
    querytext = Budget.querytext_includeremoved()
    
    rslts = list_from_query ( client, service, querytext )
        
    return rslts


  @staticmethod
  def _aw_addbudget ( client, inbudgetname, inbudgetamount=None, inbudgetdeliverymethod=None, inbudgetstatus=None ):
    """
    Add an AdWords budget entry.
    
    Attempts to add a budget to AdWords. 
    Does not check if the budget exists.
    
    Note \: Does not affect the Django database.
    
    **Parameters**
    
    client \: googleads.adwords.AdWordsClient object
      The client to request API service from.
    inbudgetname \: str
      The budget name.
    inbudgetamount \: int
      The micro value amount. Amount in micros.
    inbudgetdeliverymethod \: str
      Enumerated str type, either STANDARD, ACCELERATED, TESTING
    inbudgetstatus \: str
      Enumerated str type, either REMOVED, PAUSED, ENABLED, TESTING

    **Returns**
    
    suds.sudsobject.Budget \: newly created suds Budget instance
    or
    suds.WebFault \: error message
    
    """

    rval = None
    newbudget = None
    
    # request a service object from the client object
    service = Budget.serviceobj ( client )
    
    # create the mutate string
    mutatestring = Budget.adddict ( inbudgetname, inbudgetamount, 
                                    inbudgetdeliverymethod, 
                                    inbudgetstatus )
    
    
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
      print ( 'Add budget failed: %s' % e )
      return e

    # if the mutate was successful set validate_only to False
    if success: 
      
      client.validate_only = False
      
      # make the mutate call
      rslts = service.mutate ( [mutatestring] )
         
      rval = rslts['value'][0]

      # print the results
      print ( 'Budget %s %s added to AdWords.' % (rval['budgetId'],
                                                  rval['name']) )
    
    return rval


  @staticmethod
  def addbudget ( client, inbudgetname, inbudgetamount=None, inbudgetdeliverymethod=None, inbudgetstatus=None ):
    """
    Add an AdWords budget entry.
    
    Attempts to add a budget to AdWords. 
    Does not check if the budget exists.
    If it is successful adding the budget
    to Ad Words, it also adds a budget to 
    Django DB.
        
    **Parameters**
    
    client \: googleads.adwords.AdWordsClient object
      The client to request API service from.
    inbudgetname \: str
      The budget name.
    inbudgetamount \: int
      The micro value amount. Amount in micros.
    inbudgetdeliverymethod \: str
      Enumerated str type, either STANDARD, ACCELERATED, TESTING
    inbudgetstatus \: str
      Enumerated str type, either REMOVED, PAUSED, ENABLED, TESTING

    **Returns**
    
    wad_Budget.Budget \: newly created Budget instance

    """

    # Add new Django database entry for the newly added AdWords budget
    # add it here because init checks adwords to see if it's possible to
    # enter this item, adwords does not let you ad an item that has same
    # name as their db
    newbudget = Budget(
      budgetid = None,
      budgetdeliverymethod = inbudgetdeliverymethod,
      budgetstatus = inbudgetstatus,
      budgetname = inbudgetname,
      budgetamount = inbudgetamount,
      )
    
    addbudgetobj = Budget._aw_addbudget ( client, inbudgetname, inbudgetamount, 
                                          inbudgetdeliverymethod, inbudgetstatus )
    
    if addbudgetobj != None:

      #print ( newbudget.budgetamount )
      #print ( newbudget.budgetdeliverymethod )
      #print ( newbudget.budgetstatus )
      #print ( newbudget.budgetid )

      # the unsaved db object needs updated after _aw_addbudget if method paramaters were none
      newbudget.budgetdeliverymethod = addbudgetobj['deliveryMethod']
      newbudget.budgetstatus = addbudgetobj['status']
      newbudget.budgetid = addbudgetobj['budgetId']
      newbudget.budgetamount = addbudgetobj['amount']['microAmount']

      
      # finally we are ready to save the database instance
      newbudget.save( sync_aw=False )
    
      print ( 'Budget %s %s added to Django.' % (addbudgetobj['budgetId'],
                                                 addbudgetobj['name']) )

    else:
      
      print ( 'Failed to add Budget ( budgetname="%s" ... )' % inbudgetname )
      
    return newbudget
  
  
  @staticmethod
  def _aw_removebudget ( client, inbudgetid ):
    """
    Remove an AdWords budget entry.
    
    Attempts to remove a budget from AdWords. Does not 
    check if the budget exists.
    
    **Parameters**
    
    client \: googleads.adwords.AdWordsClient object
      The client to request API service from.
    inbudgetid \: int 
      The id of the budget.
    

    **Returns**
    
    <class 'suds.sudsobject.BudgetReturnValue'> \: Returns the 
    results of the delete operation / the deleted Budget object
    or
    suds.WebFault \: error message
    
    """

    # request a service object from the client object
    service = Budget.serviceobj ( client )
    
    # create the mutate string
    mutatestring = Budget.deldict ( inbudgetid )
    
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
      print ( 'Remove budget failed: %s' % e )
      return e

    # if the mutate was successful set validate_only to False
    if success: 
      
      client.validate_only = False
      
      # make the mutate call
      rslts = service.mutate ( [mutatestring] )

      # print the results
      print ( 'Budget %s %s removed from AdWords.' % (rslts['value'][0]['budgetId'],
                                                      rslts['value'][0]['name']) )
      
    return rslts
  
  
  @staticmethod
  def removebudget ( client, inbudgetid ):
    """
    Remove an AdWords budget entry.
    
    Attempts to remove a budget from AdWords. Does not 
    check if the budget exists. If it is successful it
    also tries to remove the budget from Django.
    
    **Parameters**
    
    client \: googleads.adwords.AdWordsClient object
      The client to request API service from.
    inbudgetid \: int 
      The id of the budget.
    

    **Returns**
    
    wad_Budget.Budget \: Returns the deleted Budget instance
    
    """

    djangobudget = None
    
    rslts = Budget._aw_removebudget ( client, inbudgetid )
    
    if 'value' in rslts:
       
      # Delete Django database entry if it exists for the deleted AdWords budget
      try:
        djangobudget = Budget.objects.get(budgetid = rslts['value'][0]['budgetId'])
      except ObjectDoesNotExist:
        print ( 'Tried to remove budget %s %s but it did not exist in Django.' % (rslts['value'][0]['budgetId'],
                                                       rslts['value'][0]['name'] ) )
      
      if djangobudget != None: 
        djangobudget.delete(sync_aw=False)
        print ( 'Budget %s %s removed from Django.' % (rslts['value'][0]['budgetId'],
                                                       rslts['value'][0]['name'] ) )
            
    return djangobudget


  @staticmethod
  def _aw_removenorefbudgets ( client ):
    """
    Removes budgets with 0 reference count. This happens to budgets
    after their associated campaign is removed.
    
    Queries AW API for list of budgets with 0 refcount and deletes
    all occurences of them.
    
    **Parameters**
    
    client \: googleads.adwords.AdWordsClient object
      The client to request API service from.
      
    **Returns**
    
    suds.sudsobject.Budget[] \: list of removed budgets
    
    """

    # request a service object from the client object
    service = Budget.serviceobj ( client )

    querystring = Budget.querytextref ( )
    
    rslts = list_from_query ( client, service, querystring )
    
    dellst = []
    
    rval = []
    
    for item in rslts:
      if item['referenceCount'] == 0:
        dellst.append ( Budget.deldict ( item['budgetId'] ) )
        
    if ( len ( dellst ) != 0 ):   
      # call mutate for the list of deletes
      rval = service.mutate ( dellst )['value']
      
    else:
      rval = []

    return rval


  @staticmethod
  def removenorefbudgets ( client ):
    """
    Removes budgets with 0 reference count. This happens to budgets
    after their associated campaign is removed. If there are budgets
    with 0 reference count, this method also removes them from Django.
    
    Queries AW API for list of budgets with 0 refcount and deletes
    all occurences of them. Also removes Django DB entries for 0
    refcount budgets.
    
    **Parameters**
    
    client \: googleads.adwords.AdWordsClient object
      The client to request API service from.
      
    **Returns**
    
    wad_Budget.models.Budget[] \: list of removed budgets
    
    """

    
    djangobudgets = []
    
    
    rslts = Budget._aw_removenorefbudgets ( client )
    
    for rslt in rslts:
      
      djangobudget = None
      
      # Delete Django database entry if it exists for the deleted AdWords budget
      try:
        djangobudget = Budget.objects.get(budgetid = rslt['budgetId'])
      except ObjectDoesNotExist:
        print ( 'Tried to remove budget %s %s but it did not exist in Django.' % (rslt['budgetId'],
                                                       rslt['name'] ) )
      
      if djangobudget != None: 
        djangobudget.delete(sync_aw=False)
        print ( 'Budget %s %s removed from Django.' % (rslt['budgetId'],
                                                       rslt['name'] ) )
        djangobudgets.append ( djangobudget )
    
    return djangobudgets


  @staticmethod
  def sync ( client, budgetid = None ):
    """
    Synchronize AdWords budgets with Django.
    
    Queries all budgets in AdWords and inserts, deletes or modifies
    Django database entries corresponding to the AdWords entries.
    
    Note \: AdWords budgets with status "REMOVED" are not sychronized.
    
    **Parameters**
    
    client \: googleads.adwords.AdWordsClient object
      The client to request API service from.

    budgetid \: str
      Optional budgetid to sync a single budget

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

    service = Budget.serviceobj( client )
    
    query = Budget.querytext( budgetid )
    
    rslt = list_from_query ( client, service, query )
    
    for awbudgetobj in rslt:      
      
      # if the budget has not been marked as 'REMOVED'
      if awbudgetobj['status'] != 'REMOVED':
      
        try:

          #
          # Update existing Django values from AdWords account.
          #
          # budgetamount, budgetname, budgetstatus

          # get current values from Django database
          obj = Budget.objects.get ( 
            budgetid = awbudgetobj['budgetId'] )
          
          updated = False
          
          # todo: update delivery method
          
          if obj.budgetname != awbudgetobj['name']:

            obj.budgetname = awbudgetobj['name']

            print ( 'Updated budget %s %s name in Django databse.' % 
                     ( obj.budgetid, obj.budgetname ) )

            updated = True          
          
          if obj.budgetstatus != awbudgetobj['status']:
            
            obj.budgetstatus = awbudgetobj['status']
            
            print ( 'Updated budget %s %s status in Django databse.' % 
                    ( obj.budgetid, obj.budgetname ) )
            
            updated = True
                        
          if obj.budgetamount != awbudgetobj['amount']['microAmount']:
            
            obj.budgetamount = awbudgetobj['amount']['microAmount']
            
            print ( 
              'Updated budget %s %s budget amount in Django database.' % 
               (obj.budgetid, obj.budgetamount ) )
            

            updated = True
            
          if updated == True:
            obj.save( sync_aw=False )
            rval.rmodified.append(obj)
        
        except ObjectDoesNotExist:

          #
          # Add new Django values from AdWords account.
          #
          
          newbudget = Budget(
            budgetid = awbudgetobj['budgetId'],
            budgetstatus = awbudgetobj['status'],
            budgetname = awbudgetobj['name'],
            budgetamount = awbudgetobj['amount']['microAmount'],
            )
          
          newbudget.save( sync_aw=False )
          print ( 'Added budget %s %s to Django database.' % 
                  ( newbudget.budgetid, newbudget.budgetname ) )
        
          rval.radded.append(newbudget)
    
    #
    # Remove old Django values according to AdWords account.
    # remove any old campaigns from Django db that don't exist in 
    # adwords anymore
    #
    
    # make a list of awcampaignobj ids
    awbudgetobjids = []
    for awbudgetobj in rslt:
      if awbudgetobj['status'] != 'REMOVED':
        awbudgetobjids.append ( awbudgetobj['budgetId'] )
      
    # iterate Django db entries and check if the entry exists 
    # in adwords, remove the entry if it doesn't exist
    for dbbudgetobj in Budget.objects.all ( ):
      if dbbudgetobj.budgetid not in awbudgetobjids:
        dbbudgetobj.delete()
        print ( 'Deleted budget %s %s from Django database.' % 
                ( dbbudgetobj.budgetid, dbbudgetobj.budgetname ) )
        rval.rremoved.append ( dbbudgetobj )
        
        
    return rval
        
      
      
  def save(self, *args, **kwargs):
    
    # if snyc_aw is in the arguments for save, assign it to a member
    # variable of self for pre_save and pop it
    if 'sync_aw' in kwargs:
      self.sync_aw = kwargs['sync_aw']
      kwargs.pop('sync_aw')
    else:
      self.sync_aw = True
    
    super(Budget, self).save(*args, **kwargs)
      

  def delete(self, *args, **kwargs):
    
    # if snyc_aw is in the arguments for save, assign it to a member
    # variable of self for pre_save and pop it
    if 'sync_aw' in kwargs:
      self.sync_aw = kwargs['sync_aw']
      kwargs.pop('sync_aw')
    else:
      self.sync_aw = True
    
    super(Budget, self).delete(*args, **kwargs)



  #def save(self, *args, **kwargs):
    
    #aw_budget = None
    
    ## before you save the instance, check that the instance has a budgetid
    #if ( self.budgetid == None ):
      
      ## load the client from storage
      #client = adwords.AdWordsClient.LoadFromStorage()
      
      #aw_budget = Budget._aw_addbudget ( client, self.budgetname, self.budgetamount,
                                  #self.budgetdeliverymethod, self.budgetstatus )
      
      #self.budgetid = aw_budget['budgetId']
    
    #super(Budget, self).save(*args, **kwargs)
    
    #return
    










      




  
  
