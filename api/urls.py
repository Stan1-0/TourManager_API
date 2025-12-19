from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()    
router.register(r'tourist-sites', TouristSiteViewSet, basename='touristsite')
router.register(r'hotels', HotelViewSet, basename='hotel')  
router.register(r'users', UserViewSet, basename='user')
router.register(r'favorites', FavoriteViewSet, basename='favorite')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'user-registration', UserRegistrationViewSet, basename='userregistration')
router.register(r'user-profile', UserProfileViewSet, basename='userprofile')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user-login/', UserLoginViewSet.as_view({'post': 'create'}), name='user-login'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),    
]
