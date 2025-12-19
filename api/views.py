from django.shortcuts import render
from .serializers import *
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .pagination import CustomPageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin

# Create your views here.
class TouristSiteViewSet(viewsets.ModelViewSet):
    queryset = TouristSite.objects.all()
    serializer_class = TouristSiteSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'history', 'region_or_city']
    filterset_fields = ['region_or_city']
    ordering_fields = ['name', 'created_at']
    permission_classes = [IsAdminOrReadOnly]
    
class HotelViewSet(viewsets.ModelViewSet):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'address']
    filterset_fields = ['tourist_site', 'price_per_night', 'availability']
    ordering_fields = ['price_per_night', 'distance_from_site']
    permission_classes = [IsAdminOrReadOnly]
    
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    
class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        if user and (getattr(user, 'is_admin', False) or user.is_superuser):
            return self.queryset
        return self.queryset.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        if user and (getattr(user, 'is_admin', False) or user.is_superuser):
            return self.queryset
        return self.queryset.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        if user and (getattr(user, 'is_admin', False) or user.is_superuser):
            return self.queryset
        return self.queryset.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
class UserRegistrationViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer   
    permission_classes = [AllowAny]
    
class UserLoginViewSet(viewsets.ViewSet):
    serializer_class = UserLoginSerializer  
    permission_classes = [AllowAny]

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer    
    lookup_field = 'pk'
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'is_admin', False) or user.is_superuser:
            return User.objects.all()
        return User.objects.filter(pk=user.pk)

    def perform_create(self, serializer):
        # Prevent creation via this endpoint unless admin
        user = self.request.user
        if not (getattr(user, 'is_admin', False) or user.is_superuser):
            raise PermissionError("Only admins can create users here")
        serializer.save()
    
    
