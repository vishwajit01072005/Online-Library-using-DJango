from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q

from .models import Book, Order, OrderItem, Address
from .forms import BookForm, AddressForm


# Display the home page and apply optional title/author search filtering.
def home(request):
    query = request.GET.get('q', '').strip()
    books = Book.objects.all()
    if query:
        books = books.filter(Q(title__icontains=query) | Q(author__icontains=query))
    return render(request, 'home.html', {'books': books, 'query': query})


# Handle new user registration by validating credentials and creating a user account.
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            messages.error(request, 'Please enter both username and password.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            User.objects.create_user(username=username, password=password)
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('login')

    return render(request, 'register.html')


# Handle standard user login and redirect to the original destination.
def user_login(request):
    next_url = request.GET.get('next', '')
    if request.method == 'POST':
        next_url = request.POST.get('next', next_url)
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful.')
            return redirect(next_url or 'home')

        messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html', {'next': next_url})


# Authenticate a superuser via a dedicated admin login page.
def admin_login(request):
    next_url = request.GET.get('next', '')
    if request.method == 'POST':
        next_url = request.POST.get('next', next_url)
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_superuser:
                login(request, user)
                messages.success(request, 'Admin login successful.')
                return redirect(next_url or 'home')
            messages.error(request, 'Superuser access required. Please login with superuser credentials.')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'admin_login.html', {'next': next_url})


# Log the current user out and return to the home page.
@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'Logged out successfully.')
    return redirect('home')


# Allow only superusers to display and process the add-book form.
@login_required
def book_create(request):
    if not request.user.is_superuser:
        messages.error(request, 'Superuser access required to add a book.')
        return redirect('admin_login')

    form = BookForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Book added successfully.')
        return redirect('home')
    return render(request, 'book_form.html', {'form': form, 'title': 'Add Book'})


# Show details of a single book selected by its ID.
def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'book_detail.html', {'book': book})


# Allow only superusers to edit an existing book record.
@login_required
def book_update(request, book_id):
    if not request.user.is_superuser:
        messages.error(request, 'Superuser access required to edit a book.')
        return redirect('admin_login')

    book = get_object_or_404(Book, id=book_id)
    form = BookForm(request.POST or None, instance=book)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Book updated successfully.')
        return redirect('home')
    return render(request, 'book_form.html', {'form': form, 'title': 'Edit Book'})


# Allow only superusers to delete a book and confirm the action.
@login_required
def book_delete(request, book_id):
    if not request.user.is_superuser:
        return redirect('admin_login')

    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book deleted successfully.')
        return redirect('home')
    return render(request, 'book_confirm_delete.html', {'book': book})


# Add a selected book to the cart stored in the user's session.
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    cart = request.session.get('cart', {})
    key = str(book_id)
    cart[key] = cart.get(key, 0) + 1
    request.session['cart'] = cart
    messages.success(request, f'Added "{book.title}" to cart.')
    return redirect('home')


# Remove an item from the current session cart.
def remove_from_cart(request, book_id):
    cart = request.session.get('cart', {})
    key = str(book_id)
    if key in cart:
        cart.pop(key)
        request.session['cart'] = cart
        messages.success(request, 'Item removed from your cart.')
    return redirect('cart')


# Render the cart page with selected items and calculated total.
# Render the cart page with selected items and calculated total.
def cart(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0

    for book_id, quantity in cart.items():
        book = get_object_or_404(Book, id=int(book_id))
        subtotal = book.price * quantity
        items.append({'book': book, 'quantity': quantity, 'subtotal': subtotal})
        total += subtotal

    return render(request, 'cart.html', {'items': items, 'total': total})


# Create an order from the current session cart for the logged-in user.
@login_required
def place_order(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.info(request, 'Your cart is empty.')
        return redirect('home')

    order = Order.objects.create(user=request.user, total_price=0)
    total = 0

    for book_id, quantity in cart.items():
        book = get_object_or_404(Book, id=int(book_id))
        line_total = book.price * quantity
        OrderItem.objects.create(order=order, book=book, quantity=quantity, price=line_total)
        total += line_total

    order.total_price = total
    order.save()
    request.session['cart'] = {}

    return redirect('add_address', order_id=order.id)


# Show a logged-in user's past orders in reverse chronological order.
@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order_list.html', {'orders': orders})


# Display the details for a specific order belonging to the user.
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    address = getattr(order, 'shipping_address', None)
    return render(request, 'order.html', {'order': order, 'address': address})


# Collect or update the shipping address for an order and show confirmation.
@login_required
def add_address(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    address_instance = getattr(order, 'shipping_address', None)
    form = AddressForm(request.POST or None, instance=address_instance)

    if request.method == 'POST' and form.is_valid():
        address = form.save(commit=False)
        address.user = request.user
        address.order = order
        address.save()
        messages.success(request, 'Shipping address saved successfully.')
        return redirect('order_detail', order_id=order.id)

    return render(request, 'address_form.html', {'form': form, 'order': order})
