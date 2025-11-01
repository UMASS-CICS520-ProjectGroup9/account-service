from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import AccountSerializer
from base.models import Account 


@api_view(['GET'])
def getAllAccounts(request):
    accounts = Account.objects.all()
    serializer = AccountSerializer(accounts, many=True)
    account = serializer.data
    return Response(account)

@api_view(['POST'])
def createAccount(request):
    serializer = AccountSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

@api_view(['PUT'])
def updateAccount(request):
    email = request.data.get('email')
    try:
        account = Account.objects.get(email=email)
    except Account.DoesNotExist:
        return Response({'error': 'Account not found'}, status=404)

    serializer = AccountSerializer(account, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

@api_view(['DELETE'])
def deleteAccount(request):
    email = request.data.get('email')
    try:
        account = Account.objects.get(email=email)
    except Account.DoesNotExist:
        return Response({'error': 'Account not found'}, status=404)

    account.delete()
    return Response({'message': 'Account deleted successfully'})