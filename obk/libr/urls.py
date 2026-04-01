from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('book/add/', views.book_create, name='book_add'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('book/<int:book_id>/edit/', views.book_update, name='book_edit'),
    path('book/<int:book_id>/delete/', views.book_delete, name='book_delete'),
    path('cart/', views.cart, name='cart'),
    path('add/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:book_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('order/', views.place_order, name='order'),
    path('order/<int:order_id>/address/', views.add_address, name='add_address'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
]
