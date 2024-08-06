from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.views import APIView

from .models import Subscription, UserSubscription
from .serializers import SubscriptionSerializer, UserSubscriptionSerializer, CreateUserSubscriptionSerializer, \
    RenewSubscriptionSerializer
from django.shortcuts import get_object_or_404
from django.utils import timezone
# from .decorators import subscription_required



# Create your views here.


@login_required
def subscribe(request, subscription_id):
    subscription = get_object_or_404(Subscription, pk=subscription_id)
    user_subscription = UserSubscription(user=request.user, subscription=subscription)
    user_subscription.save()
    return redirect('subscription_success')


@login_required
# @subscription_required
def subscription_success(request):
    return render(request, 'subscription_success.html')


class SubscriptionListView(generics.ListAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [AllowAny]
    # permission_classes = [IsAdminUser]


class UserSubscriptionCreateView(generics.CreateAPIView):
    serializer_class = CreateUserSubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        subscription_name = request.data.get('subscription_name')
        subscription = get_object_or_404(Subscription, name=subscription_name)
        user_subscription = UserSubscription(
            user=request.user,
            subscription=subscription,
            start_date=timezone.now()
        )
        user_subscription.save()
        return Response(UserSubscriptionSerializer(user_subscription).data, status=status.HTTP_201_CREATED)


class UserSubscriptionListView(generics.ListAPIView):
    serializer_class = UserSubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserSubscription.objects.filter(user=self.request.user)


def subscription_required(request):
    return render(request, 'subscription_required.html')


class RenewSubscriptionView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RenewSubscriptionSerializer(data=request.data)
        if serializer.is_valid():
            user_subscription = UserSubscription.objects.get(user=request.user)
            # Check if the current subscription is expired
            if user_subscription.is_active:
                return Response({"message": "Your subscription is still active."}, status=status.HTTP_400_BAD_REQUEST)

            # Get new subscription ID from the validated data
            new_subscription_id = serializer.validated_data['subscription_id']
            new_subscription = Subscription.objects.get(id=new_subscription_id)

            # Renew the subscription
            user_subscription.renew(new_subscription)

            return Response({"message": "Subscription renewed successfully"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # try:
        #     user_subscription = UserSubscription.objects.get(user=request.user)
        # except UserSubscription.DoesNotExist:
        #     return Response({"error": "Subscription not found"}, status=status.HTTP_404_NOT_FOUND)
        #
        # # Check if the current subscription is expired
        # if user_subscription.is_active:
        #     return Response({"message": "Your subscription is still active."}, status=status.HTTP_400_BAD_REQUEST)
        #
        # # Get new subscription ID from the request
        # new_subscription_id = request.data.get('subscription_id')
        # try:
        #     new_subscription = Subscription.objects.get(id=new_subscription_id)
        # except Subscription.DoesNotExist:
        #     return Response({"error": "Invalid subscription plan"}, status=status.HTTP_400_BAD_REQUEST)
        #
        # # Renew the subscription
        # user_subscription.renew(new_subscription)
        #
        # return Response({"message": "Subscription renewed successfully"}, status=status.HTTP_200_OK)