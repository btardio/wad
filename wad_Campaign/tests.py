from django.test import TestCase
from wad_Campaign.models import Campaign
from wad.query import list_from_query
from wad_Campaign.management.commands import campaignclear
from wad_Campaign.management.commands import campaignsync
from googleads import adwords

# TODO test the return result from Google API

# Create your tests here.
class wad_Campaign_testcases ( TestCase ):
  
  service = None
  query = None
  rslt = None
  
  def setUp ( self ):
    pass

  

  def test_wad_Campaign_management_command_campaignsync ( self ):
    
    client = adwords.AdWordsClient.LoadFromStorage()
    
    #Campaign.addcampaign ( client, 'new campaign 0' )
    
    
    
    
    return
    
    
    
    commandobj = campaignsync.Command()
    
    # sync to populate
    commandobj.handle()
    
    allentries = Campaign.objects.all()
    
    # modify values and see if they revert back to original
    for entry in allentries:
      entry.campaignname = '%s%s' % ( entry.campaignname, '_modifiedtestring' )
      entry.campaignstatus = Campaign.STATE_TESTING
    
      self.assertEqual ( True, '_modifiedtestring' in entry.campaignname )
      self.assertEqual ( Campaign.STATE_TESTING, entry.campaignstatus )
      
      entry.save()
    
    # sync to test that they return to original, don't have '_modifiedtesting' string
    commandobj.handle()
    
    allentries = Campaign.objects.all()
    
    for entry in allentries:
      self.assertEqual ( False, '_modifiedtesting' in entry.campaignname )
      self.assertNotEqual ( Campaign.STATE_TESTING, entry.campaignstatus )
      
      
    
    # remove a campaign from adwords
    if len(allentries) != 0: # if len of allentries is 0 we have nothing to delete
      Campaign.removecampaign ( client, allentries[0].campaignid )
      
    
  
  def test_wad_Campaign_management_command_campaignclear ( self ):
    
    return
    
    commandobj = campaignclear.Command()
    
    allentries = Campaign.objects.all()
    
    commandobj.handle()
    
    allentries = Campaign.objects.all()
    
    self.assertEqual ( 0, len ( allentries ) )
    #campaignclear.Command.handle()
    
    
    
    
    


    