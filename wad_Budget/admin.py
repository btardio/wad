from django.contrib import admin
from wad_Budget.models import Budget

# Register your models here.


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    
  list_display = ( 'budgetname', 'budgetid', 'id',)
  
  readonly_fields = ( 'budgetid', 'budgetstatus', 'budgetname', 'budgetamount' )
  
#  def save_model ( self, request, obj, form, change ):
#    
#    obj.save()
