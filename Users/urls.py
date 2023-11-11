from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name="user_register"),
    path('forgot/send/', views.ForgotPasswordSendView.as_view(), name="user_Forgot"),
    path('login/', views.LoginView.as_view(), name="user_login"),
    path('token/validate/', views.ValidateToken.as_view(),
         name="user_validate_token"),
    path('token/refresh/', views.TokenRefreshView.as_view(),
         name="user_refresh_token"),
    path('profile/', views.ProfileView.as_view(), name="user_profile"),
    path('verify/', views.RegisterVerifyView.as_view(), name="user_Reset"),
    path('update_profile_photo/', views.UpdateProfilePhoto.as_view(),
         name="update_profile_photo"),
    path('query/', views.QueryView.as_view(), name="user_query"),
    path("reset_password/<str:enc_data>",
         views.reset_password_page, name='user_reset_password_page'),
]
