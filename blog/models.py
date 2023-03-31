from django.db import models
from datetime import datetime
from django.template.defaultfilters import slugify
import string
import random


class Categories(models.TextChoices):
    PARTIES = 'parties'
    TOURS = 'tours'
    CORPORATE_EVENTS = 'corporate_events'
    CHARITIES = 'charities'
    NETWORKING_EVENTS = 'networking_events'
    TRADE = 'trade'
    GET_TOGETHERS = 'get_togethers'
    CONFERENCES = 'conferences'
    # SCIENCE = 'science'
    # HEALTH = 'health'
    # STYLE = 'style'
    # TRAVEL = 'travel'

def generate_w_code():
    length = 8

    while True:
        code = ''.join(random.choices(string.ascii_uppercase, k=length))
        if BlogPost.objects.filter(code=code).count() == 0:
            break
    return code

class BlogPost(models.Model):
    title = models.CharField(max_length=50)
    code = models.CharField(default=generate_w_code, max_length=8, unique=True)
    slug = models.SlugField()
    category = models.CharField(max_length=50, choices=Categories.choices, default=Categories.PARTIES)
    thumbnail = models.ImageField(upload_to='photos/%Y/%m/%d/')
    excerpt = models.CharField(max_length=150)
    month = models.CharField(max_length=3)
    day = models.CharField(max_length=2)
    content = models.TextField()
    price = models.PositiveIntegerField(default=0)
    event_organiser = models.CharField(max_length=50) 
    featured = models.BooleanField(default=False)
    date_created = models.DateTimeField(default=datetime.now, blank=True)

    def save(self, *args, **kwargs):
        original_slug = slugify(self.title)
        queryset = BlogPost.objects.all().filter(slug__iexact=original_slug).count()

        count = 1
        slug = original_slug
        while(queryset):
            slug = original_slug + '-' + str(count)
            count += 1
            queryset = BlogPost.objects.all().filter(slug__iexact=slug).count()

        self.slug = slug

        if self.featured:
            try:
                temp = BlogPost.objects.get(featured=True)
                if self != temp:
                    temp.featured = False
                    temp.save()
            except BlogPost.DoesNotExist:
                pass
        
        super(BlogPost, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

class StkCall(models.Model):
    phone_number = models.CharField( max_length=50)
    ticket_title = models.CharField( max_length=50)


    def __str__(self):
        return self.phone_number


# M-pesa Payment models

class MpesaPaymentCalls(models.Model):
    Event_title = models.TextField()
    Event_price = models.TextField()
    Withdrawal_code = models.TextField()

    BusinessShortCode = models.TextField()
    Timestamp = models.TextField()
    TransactionType = models.TextField()
    Amount = models.TextField()
    PartyA = models.TextField()
    PartyB = models.TextField()
    PhoneNumber = models.TextField()
    PhoneNumber2 = models.TextField()
    AccountReference = models.TextField()

    MerchantRequestID = models.TextField()
    CheckoutRequestID = models.TextField()
    TransactionStatus1 = models.IntegerField() #TRANSACTION STATUS1
    TransactionDescription1 = models.TextField() #TRANSACTION Description1
    CustomerMessage = models.TextField()

    TransactionStatus2 = models.TextField() #TRANSACTION STATUS2
    TransactionDescription2 = models.TextField() #TRANSACTION Description2
    ItemAmountPaid = models.TextField()
    ItemReceipt = models.TextField()
    PhoneNumber2 = models.TextField()
    ItemDate = models.TextField()

    CompanyAmount = models.TextField()
    OrganisersAmount = models.TextField()

    mpesa_receipt = models.CharField(max_length = 10000000)
    ticket_no = models.IntegerField(null=True)

    ticket_title = models.CharField(max_length = 10000000)
    phone_number = models.CharField(max_length = 10000000)


    def __str__(self):
        return self.ItemReceipt

class B2CModel(models.Model):
    phone_no = models.CharField(max_length = 10000000)
    amount = models.CharField(max_length = 10000000)
    withdrawal_id = models.CharField(max_length = 10000000)
    ConversationID = models.TextField()
    OriginatorConversationID = models.TextField()
    ResponseCode = models.TextField()
    ResponseDescription = models.TextField()
    ResultType = models.TextField()
    ResultCode = models.TextField()
    ResultDesc = models.TextField()
    OriginatorConversationID2 = models.TextField()
    ConversationID2 = models.TextField()
    ConversationID = models.TextField()
    TransactionAmount = models.TextField()
    TransactionReceipt = models.TextField()
    TransactionID = models.TextField()
    B2CRecipientIsRegisteredCustomer = models.TextField()
    B2CChargesPaidAccountAvailableFunds = models.TextField()
    ReceiverPartyPublicName = models.TextField()
    B2CUtilityAccountAvailableFunds = models.TextField()
    B2CWorkingAccountAvailableFunds = models.TextField()
    TransactionCompletedDateTime = models.TextField()


    def __str__(self):
        return self.ResponseDescription

class EventTotals2(models.Model):
    receipts2 = models.TextField()
    proceeding = models.TextField()
    owner = models.TextField()
    checkoutRequestID = models.TextField()


def generate_unique_code():
    length = 8

    while True:
        code = ''.join(random.choices(string.ascii_uppercase, k=length))
        if Ticket.objects.filter(code=code).count() == 0:
            break
    return code



class Ticket(models.Model):
    code = models.CharField(default=generate_unique_code, max_length=8, unique=True)
    title = models.CharField(max_length=50)
    price = models.PositiveIntegerField(default = 0)
    venue = models.CharField( max_length=50)

class MpesaCode1(models.Model):
    code = models.CharField( max_length=50)

class MpesaCode2(models.Model):
    codecopy = models.CharField( max_length=50)

class EventTotals2(models.Model):
    receipts2 = models.CharField( max_length=50)
    proceeding = models.CharField( max_length=50)
    owner = models.CharField( max_length=50)
    checkoutRequestID = models.CharField( max_length=50)