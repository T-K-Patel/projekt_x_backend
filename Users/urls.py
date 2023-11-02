from django.urls import path
from . import views

urlpatterns = [
	path('massreg/', views.MassRegisterUsers.as_view(), name="MassReg"),
	path('register/', views.RegisterView.as_view(), name="Register"),
	path('forgot/send/', views.ForgotPasswordSendView.as_view(), name="Forgot"),
	path('forgot/verify/', views.ForgotPasswordVerifyView.as_view(), name="Forgot verify"),
	path('login/', views.LoginView.as_view(), name="Login"),
	path('token/validate/', views.ValidateToken.as_view(), name="Validate_Token"),
	path('token/refresh/', views.TokenRefreshView.as_view(), name="Refresh"),
	path('profile/', views.ProfileView.as_view(), name="Profile"),
	path('resetpassword/', views.ResetPasswordView.as_view(), name="Reset"),
	path('verify/', views.RegisterVerifyView.as_view(), name="Reset"),
	path('update_profile_photo/', views.UpdateProfilePhoto.as_view(), name="update_profile_photo"),
	path('query/', views.QueryView.as_view(), name="Query"),
	path('leaderboard/', views.LeaderboardView.as_view(), name="Leaderboard"),
]
