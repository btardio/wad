from django.apps import AppConfig

class wad_CampaignConfig(AppConfig):
  
  name = 'wad_Campaign'
  
  
  def ready(self):
    
    super(wad_CampaignConfig, self).ready()
    
    import signals
  
  

