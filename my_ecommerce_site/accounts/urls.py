from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.sign_up, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('userprofile/', views.user_profile, name='user_profile'),
    path('updateinfo/', views.update_info, name='update_info'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('verify-signup-otp/', views.verify_signup_otp, name='verify_signup_otp'),

]
