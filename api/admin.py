from django.contrib import admin
from .models import User, TouristSite, Hotel, Booking, Review, Favorite


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
	list_display = ('email', 'full_name', 'is_admin', 'is_superuser', 'is_active', 'created_at')
	search_fields = ('email', 'full_name')
	list_filter = ('is_admin', 'is_superuser', 'is_active')
	ordering = ('email',)


@admin.register(TouristSite)
class TouristSiteAdmin(admin.ModelAdmin):
	list_display = ('name', 'region_or_city', 'opening_hours', 'created_at')
	search_fields = ('name', 'region_or_city')
	list_filter = ('region_or_city',)


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
	list_display = ('name', 'tourist_site', 'price_per_night', 'distance_from_site', 'availability')
	search_fields = ('name', 'address')
	list_filter = ('availability', 'tourist_site')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
	list_display = ('user', 'hotel', 'check_in_date', 'check_out_date', 'total_cost', 'status', 'created_at')
	search_fields = ('user__email', 'hotel__name')
	list_filter = ('status',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
	list_display = ('user', 'rating', 'tourist_site', 'hotel', 'created_at')
	search_fields = ('user__email', 'comment')
	list_filter = ('rating',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
	list_display = ('user', 'tourist_site', 'created_at')
	search_fields = ('user__email', 'tourist_site__name')

