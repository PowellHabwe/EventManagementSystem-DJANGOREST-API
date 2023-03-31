from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import BlogPost
from .models import MpesaPaymentCalls
from .models import B2CModel
from .models import EventTotals2
from .models import Ticket
from .models import MpesaCode1
from .models import MpesaCode2

class BlogPostAdmin(SummernoteModelAdmin):
    exclude = ('slug', )
    list_display = ('id', 'title', 'category', 'date_created')
    list_display_links = ('id', 'title')
    search_fields = ('title', )
    list_per_page = 25
    summernote_fields = ('content', )

admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(MpesaPaymentCalls)   
admin.site.register(B2CModel)   
admin.site.register(EventTotals2)   
admin.site.register(Ticket)   
admin.site.register(MpesaCode1)   
admin.site.register(MpesaCode2)   
