from django.urls import path
from . import views
from .views import SubscriptionListView, UserSubscriptionCreateView, UserSubscriptionListView, subscription_required, \
    RenewSubscriptionView

urlpatterns = [
    path('subscribe/<int:subscription_id>/', views.subscribe, name='subscribe'),
    path('subscription_success/', views.subscription_success, name='subscription_success'),
    path('', SubscriptionListView.as_view(), name='subscription_list'),
    path('user-subscription/', UserSubscriptionCreateView.as_view(), name='user_subscription_create'),
    path('my-subscriptions/', UserSubscriptionListView.as_view(), name='my_subscriptions'),
    path('subscription_required/', subscription_required, name='subscription_required'),
    path('renew-subscription/', RenewSubscriptionView.as_view(), name='renew-subscription'),

    # path('subscription_pack/', subscription_required, name='subscription_pack'),

    # path('create_checkout_session/<int:subscription_id>/', views.create_checkout_session, name='create_checkout_session'),
]
