from django.db import models
from django.contrib.auth.models import User

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image_url = models.URLField(blank=True, help_text='Optional image URL for the book cover')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Return the book title when this Book object is printed.
    def __str__(self):
        return self.title

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Return a readable label for the order including its ID and owner.
    def __str__(self):
        return f'Order #{self.id} by {self.user.username}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    # Return a quick label for an order item showing quantity and book title.
    def __str__(self):
        return f'{self.quantity} x {self.book.title}'


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipping_address')
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=120)
    state = models.CharField(max_length=120)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=120, default='India')
    created_at = models.DateTimeField(auto_now_add=True)

    # Return the formatted shipping address for display.
    def __str__(self):
        return f'{self.street}, {self.city}'
