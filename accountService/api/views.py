from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from .serializers import AccountSerializer
from .permissions import IsAdmin, IsStudent, IsStaff, IsOwnerOrAdmin
from rest_framework.exceptions import PermissionDenied
from base.models import Account 
from django.utils.dateparse import parse_datetime

print("request.user")
@api_view(['GET'])
@permission_classes([IsStudent])
def getAccount(request, email):
    
    try:
        account = Account.objects.get(email=email)
    except Account.DoesNotExist:
        return Response({'error': 'Account not found'}, status=404)

    serializer = AccountSerializer(account)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAdmin])
def getAllAccounts(request):
    accounts = Account.objects.all()
    serializer = AccountSerializer(accounts, many=True)
    account = serializer.data
    return Response(account)

@api_view(['POST'])
@permission_classes([IsStudent])
def createAccount(request):
    print("34request.data", request.data)
    print("35request.user", request.user)
    
    serializer = AccountSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(
            creator_id=request.user.id,
            role=getattr(request.user, "role", None),
            email=getattr(request.user, "email", None),
        )  # fields derived from JWT
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsStudent])
def updateAccount(request):
    email = request.data.get('email')
    try:
        account = Account.objects.get(email=email)
        perm = IsOwnerOrAdmin()
        if not perm.has_object_permission(request, view=updateAccount, obj=account):
            raise PermissionDenied("You are not allowed to access this event.")
    except PermissionDenied :
        return Response({"delete": "Not allow"}, status=status.HTTP_404_NOT_FOUND)
    except Account.DoesNotExist:
        return Response({'error': 'Account not found'}, status=404)

    serializer = AccountSerializer(account, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

@api_view(['DELETE'])
@permission_classes([IsStudent])
def deleteAccount(request):
    email = request.data.get('email')
    try:
        account = Account.objects.get(email=email)
        perm = IsOwnerOrAdmin()
        if not perm.has_object_permission(request, view=updateAccount, obj=account):
            raise PermissionDenied("You are not allowed to access this event.")
    except PermissionDenied :
        return Response({"delete": "Not allow"}, status=status.HTTP_404_NOT_FOUND)
    except Account.DoesNotExist:
        return Response({'error': 'Account not found'}, status=404)

    account.delete()
    return Response({'message': 'Account deleted successfully'})

@api_view(['DELETE'])
@permission_classes([IsAdmin])
def deleteAllAccounts(request):
    count, _ = Account.objects.all().delete()
    return Response({'message': f'{count} Accounts were deleted successfully!'})

@api_view(['GET'])
@permission_classes([IsAdmin])
def countAccounts(request):
    count = Account.objects.count()
    return Response({'count': count})

@api_view(['GET'])
def healthCheck(request):
    return Response({'status': 'Account Service is healthy'})

@api_view(['GET'])
def welcome(request):
    return Response({'message': 'Welcome to the Account Service API'})

@api_view(['GET'])
def apiOverview(request):
    api_urls = {
        'Get All Accounts': '/api/accounts/',
        'Get Account by Email': '/api/account/<str:email>/',
        'Create Account': '/api/account/create/',
        'Update Account': '/api/account/update/',
        'Delete Account': '/api/account/delete/',
        'Delete All Accounts': '/api/accounts/delete_all/',
        'Count Accounts': '/api/accounts/count/',
        'Health Check': '/api/health/',
        'Welcome': '/api/welcome/',
    }
    return Response(api_urls)

@api_view(['GET'])
@permission_classes([IsAdmin])
def getActiveAccounts(request):
    active_accounts = Account.objects.filter(is_active=True)
    serializer = AccountSerializer(active_accounts, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAdmin])
def getInactiveAccounts(request):
    inactive_accounts = Account.objects.filter(is_active=False)
    serializer = AccountSerializer(inactive_accounts, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAdmin])
def activateAccount(request):
    email = request.data.get('email')
    try:
        account = Account.objects.get(email=email)
    except Account.DoesNotExist:
        return Response({'error': 'Account not found'}, status=404)

    account.is_active = True
    account.save()
    serializer = AccountSerializer(account)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAdmin])
def deactivateAccount(request):
    email = request.data.get('email')
    try:
        account = Account.objects.get(email=email)
    except Account.DoesNotExist:
        return Response({'error': 'Account not found'}, status=404)

    account.is_active = False
    account.save()
    serializer = AccountSerializer(account)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAdmin])
def getAccountsByRole(request, role):
    accounts = Account.objects.filter(role=role)
    serializer = AccountSerializer(accounts, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAdmin])
def countAccountsByRole(request, role):
    count = Account.objects.filter(role=role).count()
    return Response({'role': role, 'count': count})

@api_view(['GET'])
@permission_classes([IsAdmin])
def getAccountsCreatedAfter(request, date_str):
    date = parse_datetime(date_str)
    if not date:
        return Response({'error': 'Invalid date format. Use ISO 8601 format.'}, status=400)

    accounts = Account.objects.filter(created_at__gt=date)
    serializer = AccountSerializer(accounts, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAdmin])
def getAccountsUpdatedBefore(request, date_str):
    
    date = parse_datetime(date_str)
    if not date:
        return Response({'error': 'Invalid date format. Use ISO 8601 format.'}, status=400)

    accounts = Account.objects.filter(updated_at__lt=date)
    serializer = AccountSerializer(accounts, many=True)
    return Response(serializer.data)

# @api_view(['GET'])
# @permission_classes([IsAdmin])
# def authenticateAccount(request):
#     email = request.query_params.get('email')
#     password = request.query_params.get('password')
#     try:
#         account = Account.objects.get(email=email, password=password)
#         serializer = AccountSerializer(account)
#         return Response(serializer.data)
#     except Account.DoesNotExist:
#         return Response({'error': 'Invalid email or password'}, status=401)
    
# @api_view(['PUT'])
# @permission_classes([IsAdmin])
# def changeAccountPassword(request):
#     email = request.data.get('email')
#     old_password = request.data.get('old_password')
#     new_password = request.data.get('new_password')
#     try:
#         account = Account.objects.get(email=email, password=old_password)
#     except Account.DoesNotExist:
#         return Response({'error': 'Invalid email or password'}, status=401)

#     account.password = new_password
#     account.save()
#     serializer = AccountSerializer(account)
#     return Response(serializer.data)

# @api_view(['PUT'])
# @permission_classes([IsAdmin])
# def changeAccountRole(request):
#     email = request.data.get('email')
#     new_role = request.data.get('new_role')
#     try:
#         account = Account.objects.get(email=email)
#     except Account.DoesNotExist:
#         return Response({'error': 'Account not found'}, status=404)

#     account.role = new_role
#     account.save()
#     serializer = AccountSerializer(account)
#     return Response(serializer.data)

# @api_view(['PUT']) 
# @permission_classes([IsAdmin])
# def toggleAccountActiveStatus(request):
#     email = request.data.get('email')
#     try:
#         account = Account.objects.get(email=email)
#     except Account.DoesNotExist:
#         return Response({'error': 'Account not found'}, status=404)

#     account.is_active = not account.is_active
#     account.save()
#     serializer = AccountSerializer(account)
#     return Response(serializer.data)


      
