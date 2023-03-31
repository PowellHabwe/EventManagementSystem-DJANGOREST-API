from rest_framework import serializers
from .models import BlogPost, StkCall,Ticket, MpesaCode1, MpesaCode2, EventTotals2

class BlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = '__all__'
        lookup_field = 'slug'


class StkCallSerializer(serializers.ModelSerializer):
    class Meta:
        model = StkCall
        fields = '__all__'

class AdminWSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventTotals2
        fields = '__all__'

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'

class CreateTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ('title', 'price', 'venue', 'code')

class MpesaCode1S(serializers.ModelSerializer):
    class Meta:
        model = MpesaCode1
        fields = '__all__'

class MpesaCode2S(serializers.ModelSerializer):
    class Meta:
        model = MpesaCode2
        fields = '__all__'