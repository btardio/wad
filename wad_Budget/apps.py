from django.apps import AppConfig

class wad_BudgetConfig(AppConfig):
  
  name = 'wad_Budget'
  
  
  def ready(self):
    
    super(wad_BudgetConfig, self).ready()
    
    import signals
  
  

