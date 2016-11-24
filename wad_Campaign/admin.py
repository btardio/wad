from django.contrib import admin
from wad_Campaign.models import Campaign


# Register your models here.

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
  
  
  
  list_display = ( 'campaignname', 'campaignid', 'id',)
  
  readonly_fields = ( 'campaignid', 'campaignstatus', 'campaignname', 
                      'campaignadchanneltype', 'campaignbudget' )
  
  def save_model ( self, request, obj, form, change ):
    
    obj.save()
    
    # write google API mutate here
    
    # if obj has id of None, we are adding a new model
    #if obj.id == None:
      
    #  adddict ( obj.campaignname, obj.campaignstatus )
    
    #print ( '%s' % obj.id )
    
    #print ( 'saving model' )
    
    #obj.save() # objects don't have id's until they are saved

#    try:
#      Campaign.objects.get ( id = obj.id )
#    except:      
      
      
#    adddict ( obj.campaignname, obj.campaignstatus )


#admin.site.register ( Campaign, CampaignAdmin )









