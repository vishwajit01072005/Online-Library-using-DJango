from django.contrib import admin
from .models import Book, Order, OrderItem, Address

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('book', 'quantity', 'price')
    extra = 0
    can_delete = False

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'price', 'created_at')
    search_fields = ('title', 'author')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'total_price')
    readonly_fields = ('user', 'created_at', 'total_price')
    inlines = [OrderItemInline]
    search_fields = ('user__username',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'book', 'quantity', 'price')
    readonly_fields = ('order', 'book', 'quantity', 'price')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('order', 'user', 'street', 'city', 'postal_code', 'country')
    search_fields = ('street', 'city', 'state', 'postal_code', 'country', 'user__username')
