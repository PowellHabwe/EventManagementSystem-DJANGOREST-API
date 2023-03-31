from rest_framework.response import Response
from rest_framework import permissions, generics, status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
# from blog.models import BlogPost, MpesaPaymentCalls, B2CModel,Ticket,MpesaCode1, MpesaCode2
from blog.models import BlogPost, MpesaPaymentCalls, B2CModel,Ticket,MpesaCode1, MpesaCode2, EventTotals2

from blog.serializers import TicketSerializer, BlogPostSerializer, StkCallSerializer,CreateTicketSerializer, MpesaCode1S, MpesaCode2S

from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404

from . mpesa_credentials import MpesaAccessToken, LipanaMpesaPpassword
import requests
import json
from requests.auth import HTTPBasicAuth
from datetime import datetime
import base64
from django.views.decorators.csrf import csrf_exempt


class BlogPostListView(ListAPIView):
    queryset = BlogPost.objects.order_by('-date_created')
    serializer_class = BlogPostSerializer
    lookup_field = 'slug'
    permission_classes = (permissions.AllowAny, )

class BlogPostDetailView(RetrieveAPIView):
    queryset = BlogPost.objects.order_by('-date_created')
    serializer_class = BlogPostSerializer
    lookup_field = 'slug'
    permission_classes = (permissions.AllowAny, )

class BlogPostFeaturedView(ListAPIView):
    queryset = BlogPost.objects.all().filter(featured=True)
    serializer_class = BlogPostSerializer
    lookup_field = 'slug'
    permission_classes = (permissions.AllowAny, )

class BlogPostCategoryView(APIView):
    serializer_class = BlogPostSerializer
    permission_classes = (permissions.AllowAny, )

    def post(self, request, format=None):
        data = self.request.data
        category =  data['category']
        print(category)
        queryset = BlogPost.objects.order_by('-date_created').filter(category__iexact=category)
        # print(queryset)

        serializer = BlogPostSerializer(queryset, many=True)

        return Response(serializer.data)


# PAYMENT LOGIC

def getAccessToken(request):
    consumer_key = 'SWuCQTpBbVNDjLHiEGd3RvAJ89GPtsWa'
    consumer_secret = 'Ffc2GGWRrwBXCi6S'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token['access_token']
    print('validated token',validated_mpesa_access_token)
    return HttpResponse(validated_mpesa_access_token)



# Stk Push

class StkCallView(APIView):
    serializer_class = StkCallSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data = request.data)

        if serializer.is_valid():
            phone = serializer.data.get('phone_number')
            ticket_title = serializer.data.get('ticket_title')
            paymentResponse = self.make_mpesa_payment_request( phone=phone, ticket_title=ticket_title)
            return Response(paymentResponse)

    
    def make_mpesa_payment_request(self, phone: str, ticket_title:str) -> dict:
        access_token = MpesaAccessToken.validated_mpesa_access_token
        prepopulate = BlogPost.objects.all().filter(title = ticket_title).values()
        print('code', prepopulate[0]['code'])
        price = prepopulate[0]['price']


        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": "Bearer %s" % access_token}

        payload = {
            "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
            "Password": LipanaMpesaPpassword.decode_password,
            "Timestamp": LipanaMpesaPpassword.lipa_time,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": price,
            # "Amount": prepopulate[0]['price'],
            "PartyA": phone,  # replace with your phone number to get stk push
            "PartyB": LipanaMpesaPpassword.Business_short_code,
            "PhoneNumber": 254708294284,  # replace with your phone number to get stk push
            # "CallBackURL": "https://eventmanagementsystem1-production.up.railway.app/",
            "CallBackURL": "https://3850-41-90-62-196.eu.ngrok.io/api/blog/c2b/callback",
            # "CallBackURL": "https://sandbox.safaricom.co.ke/mpesa/",
            "AccountReference": "Powell",
            "TransactionDesc": "Testing stk push"
        }

        BusinessShortCode = payload['BusinessShortCode']
        Timestamp = payload['Timestamp']
        TransactionType = payload['TransactionType']
        Amount = payload['Amount']
        PartyA = payload['PartyA']
        PartyB = payload['PartyB']
        PhoneNumber = payload['PhoneNumber']
        AccountReference = payload['AccountReference']

        response = requests.post(api_url, json=payload, headers=headers)
        response = response.json()
        print('Mpesaresponse :', response)

        MerchantRequestID = response['MerchantRequestID']
        CheckoutRequestID = response['CheckoutRequestID']
        ResponseCode = response['ResponseCode']
        ResponseDescription = response['ResponseDescription']
        CustomerMessage = response['CustomerMessage']

        MpesaPaymentCalls.objects.create(
            BusinessShortCode = BusinessShortCode,
            Timestamp = Timestamp,
            TransactionType = TransactionType,
            Amount = Amount,
            PartyA = PartyA,
            PartyB = PartyB,
            PhoneNumber = PhoneNumber,
            AccountReference = AccountReference,
        
            MerchantRequestID=MerchantRequestID,
            CheckoutRequestID=CheckoutRequestID,
            TransactionStatus1=ResponseCode,
            TransactionDescription1=ResponseDescription,
            CustomerMessage=CustomerMessage,
            
        )

        EventTotals2.objects.create (
            owner = prepopulate[0]['code'],
            checkoutRequestID = CheckoutRequestID
        )
        return print('success')



@csrf_exempt
def register_urls(request):
    access_token = MpesaAccessToken.validated_mpesa_access_token
    api_url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl"
    headers = {"Authorization": "Bearer %s" % access_token}
    options = {"ShortCode": LipanaMpesaPpassword.Business_short_code,
               "ResponseType": "Completed",
               "ConfirmationURL": "https://3850-41-90-62-196.eu.ngrok.io/api/blog/c2b/confirmation",
               "ValidationURL": "https://3850-41-90-62-196.eu.ngrok.io/api/blog/c2b/validation"}
    response = requests.post(api_url, json=options, headers=headers)
    return HttpResponse(response.text)



# b2c callback
@csrf_exempt
def call_back(request):
    mpesaresponse1 = request.body.decode('utf-8')
    mpesaresponse2 = json.loads(mpesaresponse1)
    print('mpesaresponse2 :', mpesaresponse2)

    # result = mpesaresponse2['Result']
    # reqid = B2CModel.objects.all().filter(ConversationID =  mpesaresponse2['Result']['ConversationID']).values()

    # if mpesaresponse2['Result']['ResultDesc'] == "The initiator information is invalid.":
    #     reqid.update(
    #         ResultType = mpesaresponse2['Result']['ResultType'],
    #         ResultCode = mpesaresponse2['Result']['ResultCode'],
    #         ResultDesc = mpesaresponse2['Result']['ResultDesc'],
    #         OriginatorConversationID2 = mpesaresponse2['Result']['OriginatorConversationID'],
    #         ConversationID2 = mpesaresponse2['Result']['ConversationID'],
    #         TransactionID =  mpesaresponse2['Result']['TransactionID'],
    #     )

    # elif mpesaresponse2['Result']['ResultDesc'] == "The service request is processed successfully.":
    #     reqid.update(
    #         ResultType = mpesaresponse2['Result']['ResultType'],
    #         ResultCode = mpesaresponse2['Result']['ResultCode'],
    #         ResultDesc = mpesaresponse2['Result']['ResultDesc'],
    #         OriginatorConversationID2 = mpesaresponse2['Result']['OriginatorConversationID'],
    #         ConversationID2 = mpesaresponse2['Result']['ConversationID'],
    #         TransactionID =  mpesaresponse2['Result']['TransactionID'],
    #         TransactionAmount =  mpesaresponse2['Result']['ResultParameters']['ResultParameter'][0]['Value'],
    #         TransactionReceipt =  mpesaresponse2['Result']['ResultParameters']['ResultParameter'][1]['Value'],
    #         B2CRecipientIsRegisteredCustomer =  mpesaresponse2['Result']['ResultParameters']['ResultParameter'][2]['Value'],
    #         B2CChargesPaidAccountAvailableFunds =  mpesaresponse2['Result']['ResultParameters']['ResultParameter'][3]['Value'],
    #         ReceiverPartyPublicName =  mpesaresponse2['Result']['ResultParameters']['ResultParameter'][4]['Value'],
    #         TransactionCompletedDateTime =  mpesaresponse2['Result']['ResultParameters']['ResultParameter'][5]['Value'],
    #         B2CUtilityAccountAvailableFunds =  mpesaresponse2['Result']['ResultParameters']['ResultParameter'][6]['Value'],
    #         B2CWorkingAccountAvailableFunds =  mpesaresponse2['Result']['ResultParameters']['ResultParameter'][7]['Value'],
    #     )

    return HttpResponse("Payment Initiated")


@csrf_exempt
def validation(request):
    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }
    return JsonResponse(dict(context))

@csrf_exempt
def confirmation(request):
    print('has reached confirmation')
    mpesaresponse1 = request.body.decode('utf-8')
    mpesaresponse2 = json.loads(mpesaresponse1)
    print('mpesaresponse2 :', mpesaresponse2)

    trialResponse = mpesaresponse2['Body']
    stkCallback = trialResponse['stkCallback']
    stk = mpesaresponse2['Body']['stkCallback']

    reqid2 = EventTotals2.objects.all().filter(checkoutRequestID =  mpesaresponse2['Body']['stkCallback']['CheckoutRequestID']).values()
    reqid = MpesaPaymentCalls.objects.all().filter(CheckoutRequestID =  mpesaresponse2['Body']['stkCallback']['CheckoutRequestID']).values()
    if mpesaresponse2['Body']['stkCallback']['ResultDesc'] == 'Request cancelled by user':
        reqid.update(
            MerchantRequestID = mpesaresponse2['Body']['stkCallback']['MerchantRequestID'],
            CheckoutRequestID = mpesaresponse2['Body']['stkCallback']['CheckoutRequestID'],
            TransactionStatus2 = mpesaresponse2['Body']['stkCallback']['ResultCode'],
            TransactionDescription2 = mpesaresponse2['Body']['stkCallback']['ResultDesc'],
            ItemAmountPaid = '0',
            ItemReceipt =  'No Receipt due to cancellation',
            PhoneNumber2 =  'Phone Number',
            
        )

        reqid2.update (
            receipts2 = 'hbvawub1',
            proceeding = '56',
        )
        print('failed')
    elif mpesaresponse2['Body']['stkCallback']['ResultDesc'] == "The service request is processed successfully.":

        reqid.update(
            MerchantRequestID = mpesaresponse2['Body']['stkCallback']['MerchantRequestID'],
            CheckoutRequestID = mpesaresponse2['Body']['stkCallback']['CheckoutRequestID'],
            TransactionStatus2 = mpesaresponse2['Body']['stkCallback']['ResultCode'],
            TransactionDescription2 = mpesaresponse2['Body']['stkCallback']['ResultDesc'],
            ItemAmountPaid = mpesaresponse2['Body']['stkCallback']['CallbackMetadata']['Item'][0]['Value'],
            ItemReceipt =  mpesaresponse2['Body']['stkCallback']['CallbackMetadata']['Item'][1]['Value'],
            PhoneNumber2 =  mpesaresponse2['Body']['stkCallback']['CallbackMetadata']['Item'][3]['Value'],
            CompanyAmount = (0.1 * (mpesaresponse2['Body']['stkCallback']['CallbackMetadata']['Item'][0]['Value'])),
            OrganisersAmount = (0.9 * (mpesaresponse2['Body']['stkCallback']['CallbackMetadata']['Item'][0]['Value'])),
        ) 

        MpesaCode1.objects.create(
            code = mpesaresponse2['Body']['stkCallback']['CallbackMetadata']['Item'][1]['Value']
        )
        reqid2 = EventTotals2.all().filter(checkoutRequestID =  mpesaresponse2['Body']['stkCallback']['CheckoutRequestID']).values()
        reqid2.objects.create (
            receipts2 = mpesaresponse2['Body']['stkCallback']['CallbackMetadata']['Item'][1]['Value'],
            proceeding = (0.9 * (mpesaresponse2['Body']['stkCallback']['CallbackMetadata']['Item'][0]['Value'])),
        )
        print('success')
    else:
        reqid.update(
            MerchantRequestID = mpesaresponse2['Body']['stkCallback']['MerchantRequestID'],
            CheckoutRequestID = mpesaresponse2['Body']['stkCallback']['CheckoutRequestID'],
            TransactionStatus2 = mpesaresponse2['Body']['stkCallback']['ResultCode'],
            TransactionDescription2 = mpesaresponse2['Body']['stkCallback']['ResultDesc'],
            ItemAmountPaid = "0",
            ItemReceipt = "No receipt due to late response",
            PhoneNumber2 =  "No number due to late response",
        ) 


        print('No success')

    return HttpResponse('payment successful')


# TICKETING

def index(request, *args, **kwargs):
    return HttpResponse("<h1>Hello</h1>")

class TicketCreateView(APIView):
    serializer_class = CreateTicketSerializer

    def post(self, request, format=None):
        serializer = CreateTicketSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class GetTicket(APIView):
class TicketDetail(generics.RetrieveAPIView):

    serializer_class = TicketSerializer

    def get_object(self, queryset=None, **kwargs):
        item = self.kwargs.get('ticketCode')
        return get_object_or_404(Ticket, code=item)

class GetTicket(APIView):
    lookup_url_kwarg = 'code'

    def post(self, request, format=None):
        ticketCode = request.data.get(self.lookup_url_kwarg)
        if ticketCode != None:
            ticket_result = Ticket.objects.filter(code=ticketCode)
            if len(ticket_result) > 0:
                ticket = ticket_result[0]
                return Response({'message': 'Success!'}, status=status.HTTP_200_OK)

            return Response({'Bad Request': 'Invalid Code'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'Bad Request': 'Invalid post data, did not find a code key'}, status=status.HTTP_400_BAD_REQUEST)


class MpesaCodeValid(APIView):
    serializer_class = MpesaCode1S
    serializer_class2 = MpesaCode2S

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            code = serializer.data.get('code')
            exists = MpesaCode1.objects.filter(code = code).exists()

            check_existing = MpesaCode2.objects.filter(codecopy= code).exists()

            if exists and not check_existing:
                MpesaCode2.objects.create(
                    codecopy = code
                )
                print('success')
                return Response(status = status.HTTP_200_OK)
            else:
                print('fail')
                return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response({'Bad Request': 'Invalid data...'}, status=status.HTTP_400_BAD_REQUEST)



def b2c(request):
    access_token = MpesaAccessToken.validated_mpesa_access_token
    headers = {"Authorization": "Bearer %s" % access_token}
    api_url = 'https://sandbox.safaricom.co.ke/mpesa/b2c/v1/paymentrequest'

    payload = {
        "InitiatorName": "testapi",
        "SecurityCredential": "a/mXV7+Lko9U7WRFhB8u80rSHz8FcVm1L6LpW1J8VsERNdXJBrI9izos8Ua97yrGwQSaOHbvzYZKXGa4f+5046MCLdEeo8hw3VaDRwps7U8WlEEQsgOzJnRyCVB0XfuE7+TwwX6BC/wHXryQpw4OfCCrue7K31xaP+WhlRzBcmmvDhgbpNlMj6Qm0kDjM20nKsjnBM3ryvxtcdxiRoKM3LV1LfUJxjAdPJSR3mER/FIx/XP5gq84VAwrjcSNxpFL0QQ09ZSRZ6ncgDRkNAm4CYZgmpe2mSuE4fWuQErsazDI03AXXSG9RarkRUhfZqfGZc6C0a9KaandCK9VRSUKdw==",
        "CommandID": "BusinessPayment",
        "Amount": 1,
        "PartyA": 600986,
        "PartyB": 254708294284,
        "Remarks": "Test remarks",
        "QueueTimeOutURL": "https://8897-41-90-62-196.eu.ngrok.io/b2c/queue",
        "ResultURL": "https://8897-41-90-62-196.eu.ngrok.io/b2c/result",
        "Occassion": "Trial",
    }
    response = requests.post(api_url, json=payload, headers=headers)
                
    print(response.text.encode('utf8'))
    response = response.json()


    return HttpResponse('This is a successfull b2c payment')

