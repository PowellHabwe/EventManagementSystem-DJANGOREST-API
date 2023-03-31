from rest_framework.response import Response
from rest_framework import permissions, generics, status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from blog.models import BlogPost, MpesaPaymentCalls, B2CModel, EventTotals2,Ticket,MpesaCode1, MpesaCode2
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

  
def lipa_na_mpesa_online(request):
    access_token = MpesaAccessToken.validated_mpesa_access_token
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": "Bearer %s" % access_token}

    payload = {
        "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
        "Password": LipanaMpesaPpassword.decode_password,
        "Timestamp": LipanaMpesaPpassword.lipa_time,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": 1,
        # "Amount": prepopulate[0]['price'],
        "PartyA": 254708294284,  # replace with your phone number to get stk push
        "PartyB": LipanaMpesaPpassword.Business_short_code,
        "PhoneNumber": 254708294284,  # replace with your phone number to get stk push
        # "CallBackURL": "https://eventmanagementsystem1-production.up.railway.app/",
        "CallBackURL": "https://7122-41-90-62-196.eu.ngrok.io/stkinfo",
        # "CallBackURL": "https://sandbox.safaricom.co.ke/mpesa/",
        "AccountReference": "Powell",
        "TransactionDesc": "Testing stk push"
        }
    response = requests.post(api_url, json=payload, headers=headers)
    response = response.json()
    print(response)
    return HttpResponse('success')



@csrf_exempt
def register_urls(request):
    access_token = MpesaAccessToken.validated_mpesa_access_token
    api_url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl"
    headers = {"Authorization": "Bearer %s" % access_token}
    options = {"ShortCode": LipanaMpesaPpassword.Test_c2b_shortcode,
               "ResponseType": "Completed",
               "ConfirmationURL": "https://7122-41-90-62-196.eu.ngrok.io/api/blog/c2b/confirmation",
               "ValidationURL": "https://7122-41-90-62-196.eu.ngrok.io/api/blog/c2b/validation"}
    response = requests.post(api_url, json=options, headers=headers)
    return HttpResponse(response.text)


@csrf_exempt
def call_back(request):
    pass


@csrf_exempt
def validation(request):
    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }
    return JsonResponse(dict(context))


@csrf_exempt
def confirmation(request):
    mpesa_body =request.body.decode('utf-8')
    mpesa_payment = json.loads(mpesa_body)
    print('mpesa_payment', mpesa_payment)

    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }


    return JsonResponse(dict(context))

# TICKETING
# class TicketView(generics.CreateAPIView):
#     queryset = Ticket.objects.all()
#     serializer_class = TicketSerializer

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
                return Response({'message': 'Room Joined!'}, status=status.HTTP_200_OK)

            return Response({'Bad Request': 'Invalid Room Code'}, status=status.HTTP_400_BAD_REQUEST)

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


