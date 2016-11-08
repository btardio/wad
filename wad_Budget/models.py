from django.db import models
import suds
from googleads import adwords
from wad.query import list_from_query
from django.core.exceptions import ObjectDoesNotExist


class Budget ( models.Model ):
  """The Budget class stores budgetid, budgetname, budgetamount and 
     budgetstatus corresponding to an AdWords Budget object."""

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
                                help_text='Budget name')
  
  budgetamount = models.BigIntegerField() # selector: Amount
  
  # budget delivery method is not a part of Budget, and is not 
  # queryable from budget service
  # selector: DeliveryMethod
  budgetdeliverymethod = models.CharField(
                          max_length=20, 
                          choices=BUDGET_DELIVERY_CHOICES)
  
  # selector: BudgetStatus
  budgetstatus = models.CharField(max_length=20, 
                                  choices=STATE_CHOICES) 
  
  internalbudgetrefreshdate = models.DateTimeField(auto_now_add=True)
  
  internalbudgetcreationdate = models.DateTimeField(auto_now_add=True)
  
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
  def querytext():
    """
    Returns the query text for querying adwords api
    
    Ignores budgets with REMOVED status
        
    Note \: Does not affect the Django database.
    
    **Parameters**
    
    None
      
    **Returns**
    
    str \: the AWQL query string
    """
    rval = 'SELECT BudgetId, BudgetName, Amount, BudgetStatus'
    rval += ' WHERE BudgetStatus != "REMOVED"'
    
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



  #
  # Returns the dictionary needed to add a budget
  #
  @staticmethod
  def adddict(inbudgetname, inbudgetamount, 
              inbudgetdeliverymethod, inbudgetstatus):
    """
    Return a dictionary object for adding a budget to the AdWords API.
    
    Uses operator ADD and OPERAND name, amount, deliverymethod, 
    status - constructs an AdWords/suds compatable dictionary
    
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
  # Returns the dictionary needed to delete a budget
  #
  @staticmethod
  def deldict ( inbudgetid ):
    """
    Return a dictionary object for deleting a budget from the 
    AdWords API.
    
    Using operator REMOVE and OPERAND inbudgetid, constructs 
    an AdWords/suds compatable dictionary
    
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
  def addbudget ( client, inbudgetname, inbudgetamount, 
                  inbudgetdeliverymethod=None, inbudgetstatus=None ):
    """
    Add an AdWords budget entry.
    
    Attempts to add a budget from AdWords. 
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
    
    int \: newly created budget id

    """

    rval = None

    # if the input delivery method is None, 
    # set it to BUDGET_DELIVERY_ACCELERATED
    if inbudgetdeliverymethod == None:
      inbudgetdeliverymethod = Budget.BUDGET_DELIVERY_ACCELERATED
    
    # if the input state is None, set it to STATE_PAUSED
    if inbudgetstatus == None:
      inbudgetstatus = Budget.STATE_PAUSED
    
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

    # if the mutate was successful set validate_only to False
    if success: 
      
      client.validate_only = False
      
      # make the mutate call
      rslts = service.mutate ( [mutatestring] )

      rval = rslts['value'][0]['budgetId']

      # print the results
      print ( 'Budget %s added.' % rslts['value'][0]['budgetId'] )
    
    return rval
  
  
  @staticmethod
  def removebudget ( client, inbudgetid ):
    """
    Remove an AdWords budget entry.
    
    Attempts to remove a budget from AdWords. Does not 
    check if the budget exists.
    
    Note \: Does not affect the Django database.
    
    **Parameters**
    
    client \: googleads.adwords.AdWordsClient object
      The client to request API service from.
    inbudgetid \: int 
      The id of the budget.
    

    **Returns**
    
    class \: { rremoved[], rmodified[], radded[] }
      rremoved \: list of instances removed from Django
      rmodified \: list of instances modified in Django
      radded \: list of instances added to Django
    """

    
    rlst = []
    
    # request a service object from the client object
    service = Budget.serviceobj ( client )
    
    # create the mutate string
    mutatestring = Budget.deldict ( inbudgetid )
    
    client.validate_only = True # set this to true to test for errors
    success = False # assume failure, change the value for success

    try:
      
      # call mutate
      rslts = service.mutate ( [mutatestring] )
      
      # if there is a partial failure or success 
      # the var success will be set to true
      success = True

    except suds.WebFault as e:
      # if there is an error print the error
      print ( 'Remove budget failed: %s' % e )

    # if the mutate was successful set validate_only to False
    if success: 
      
      client.validate_only = False
      
      # make the mutate call
      rslts = service.mutate ( [mutatestring] )

      # print the results
      for rslt in rslts.value:
        print ( 'Budget %s removed.' % rslt['budgetId'] )
        rlst.append(rslt['budgetId'])
    
    return rlst


  @staticmethod
  def sync ( client ):
    """
    Synchronize AdWords budgets with Django.
    
    Queries all budgets in AdWords and inserts, deletes or modifies
    Django database entries corresponding to the AdWords entries.
    
    Note \: AdWords budgets with status "REMOVED" are not sychronized.
    
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

    service = Budget.serviceobj( client )
    
    query = Budget.querytext()
    
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
          
          if obj.budgetstatus != awbudgetobj['status']:
            print ( 'Updated budget %s status in Django databse.' % 
                    obj.budgetid )
            obj.budgetstatus = awbudgetobj['status']
            updated = True
            
          if obj.budgetname != awbudgetobj['name']:
            print ( 'Updated budget %s name in Django databse.' % 
                     obj.budgetid )
            obj.budgetname = awbudgetobj['name']
            updated = True
            
          if obj.budgetamount != awbudgetobj['amount']['microAmount']:
            
            print ( 
              'Updated budget %s budget amount in Django database.' % 
               obj.budgetid )
            
            obj.budgetamount = awbudgetobj['amount']['microAmount']
            updated = True
            
          if updated == True:
            obj.save()
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
          
          newbudget.save()
          print ( 'Added budget %s to Django database.' % 
                  newbudget.budgetid )
        
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
        print ( 'Deleted budget %s from Django database.' % 
                dbbudgetobj.budgetid )
        dbbudgetobj.delete()
        rval.rremoved.append ( dbbudgetobj )
        
        
    return rval
        
      








  
  
