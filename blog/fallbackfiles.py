
# class StkCallView(APIView):
#     serializer_class = StkCallSerializer

#     def post(self, request, *args, **kwargs):
#         requestData = request.data
#         serializer = self.serializer_class(data = request.data)

#         amount = requestData["amount"]
#         phone = requestData["phone_number"]

#         paymentResponse = self.make_mpesa_payment_request(amount = amount, phone=phone)
#         return Response(paymentResponse)

    
#     def make_mpesa_payment_request(self, amount:str, phone: str) -> dict:
#         access_token = MpesaAccessToken.validated_mpesa_access_token
#         api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
#         headers = {"Authorization": "Bearer %s" % access_token}

#         payload = {
#             "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
#             "Password": LipanaMpesaPpassword.decode_password,
#             "Timestamp": LipanaMpesaPpassword.lipa_time,
#             "TransactionType": "CustomerPayBillOnline",
#             "Amount": amount,
#             # "Amount": prepopulate[0]['price'],
#             "PartyA": phone,  # replace with your phone number to get stk push
#             "PartyB": LipanaMpesaPpassword.Business_short_code,
#             "PhoneNumber": 254708294284,  # replace with your phone number to get stk push
#             "CallBackURL": "https://e020-154-122-163-40.sa.ngrok.io/api/blog/c2b/callback",
#             "AccountReference": "Powell",
#             "TransactionDesc": "Testing stk push"
#         }

#         BusinessShortCode = payload['BusinessShortCode']
#         Timestamp = payload['Timestamp']
#         TransactionType = payload['TransactionType']
#         Amount = payload['Amount']
#         PartyA = payload['PartyA']
#         PartyB = payload['PartyB']
#         PhoneNumber = payload['PhoneNumber']
#         AccountReference = payload['AccountReference']

#         response = requests.post(api_url, json=payload, headers=headers)
#         response = response.json()
#         # print('Mpesaresponse :', response)

#         MerchantRequestID = response['MerchantRequestID']
#         CheckoutRequestID = response['CheckoutRequestID']
#         ResponseCode = response['ResponseCode']
#         ResponseDescription = response['ResponseDescription']
#         CustomerMessage = response['CustomerMessage']

#         MpesaPaymentCalls.objects.create(
#             BusinessShortCode = BusinessShortCode,
#             Timestamp = Timestamp,
#             TransactionType = TransactionType,
#             Amount = Amount,
#             PartyA = PartyA,
#             PartyB = PartyB,
#             PhoneNumber = PhoneNumber,
#             AccountReference = AccountReference,
        
#             MerchantRequestID=MerchantRequestID,
#             CheckoutRequestID=CheckoutRequestID,
#             TransactionStatus1=ResponseCode,
#             TransactionDescription1=ResponseDescription,
#             CustomerMessage=CustomerMessage,
            
#         )

#         EventTotals2.objects.create (
#             # owner = prepopulate[0]['author_id'],
#             checkoutRequestID = CheckoutRequestID
#         )
#         return print('success')
