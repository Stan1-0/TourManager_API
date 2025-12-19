from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)
    
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    profile_picture = models.CharField(max_length=500, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)  # for admin panel
    is_superuser = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
    
    @property
    def is_staff(self):
        """Compatibility property for Django admin: treat `is_admin` or `is_superuser` as staff."""
        return bool(self.is_admin or self.is_superuser)

class TouristSite(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    history = models.TextField()
    region_or_city = models.CharField(max_length=150)
    gps_coordinates = models.CharField(max_length=200, blank=True, null=True)
    opening_hours = models.CharField(max_length=150)
    images = models.JSONField(default=list)  # store list of image URLs

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class Hotel(models.Model):
    tourist_site = models.ForeignKey(TouristSite, on_delete=models.CASCADE, related_name="hotels")
    name = models.CharField(max_length=255)
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    distance_from_site = models.DecimalField(max_digits=5, decimal_places=2)
    address = models.CharField(max_length=255)
    images = models.JSONField(default=list)
    availability = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class Booking(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="bookings")

    check_in_date = models.DateField()
    check_out_date = models.DateField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.hotel.name}"
    
    def save(self, *args, **kwargs):
        # Automatically calculate total_cost based on number of nights and hotel's price_per_night
        if self.check_in_date and self.check_out_date:
            nights = (self.check_out_date - self.check_in_date).days
            if nights <= 0:
                raise ValidationError("`check_out_date` must be after `check_in_date`")
            if self.hotel and self.hotel.price_per_night is not None:
                # Ensure Decimal multiplication
                self.total_cost = Decimal(self.hotel.price_per_night) * Decimal(nights)
        super().save(*args, **kwargs)
    
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    tourist_site = models.ForeignKey(TouristSite, on_delete=models.CASCADE, related_name="reviews", null=True, blank=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="reviews", null=True, blank=True)

    rating = models.IntegerField()
    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review by {self.user.email}"
    
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    tourist_site = models.ForeignKey(TouristSite, on_delete=models.CASCADE, related_name="favorited_by")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} favorited {self.tourist_site.name}"