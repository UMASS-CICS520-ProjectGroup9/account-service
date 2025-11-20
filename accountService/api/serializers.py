from rest_framework import serializers
from base.models import Account

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'
        # read_only_fields = ["creator_id", "created_at"]
        