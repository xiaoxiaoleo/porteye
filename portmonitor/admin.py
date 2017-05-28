from portmonitor.models import IpRemarks,port_monitor
from django.contrib import admin

# Register your models here.
class IpRemarksAdmin(admin.ModelAdmin):
    list_display = ['ip_addr','create_time','business','own','remarks']
    search_fields =  [ 'ip_addr', 'remarks']   


# Register your models here.
class port_monitorAdmin(admin.ModelAdmin):
    list_display = ['name','ip_range','remarks','fnascan_check','masscan_check']
    search_fields =  [ 'name', 'ip_range']   


admin.site.register(IpRemarks, IpRemarksAdmin)
    
admin.site.register(port_monitor,port_monitorAdmin)
    