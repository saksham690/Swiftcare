from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.validators import EmailValidator, ValidationError
from django.utils.html import strip_tags
from django.template import TemplateDoesNotExist, TemplateSyntaxError
from .models import Medicine, Order, OrderItem
import requests
import urllib.parse
import logging
import smtplib

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def home(request, category='all'):
    query = request.GET.get('q', '')
    medicines = []

    try:
        if category != 'all':
            medicines_qs = Medicine.objects.filter(category=category, name__icontains=query)
        else:
            medicines_qs = Medicine.objects.filter(name__icontains=query)
        
        medicines = [
            {
                'id': med.id,
                'name': med.name,
                'description': med.description,
                'price': float(med.price),
                'image_url': med.image_url,
                'category': med.category,
                'stock_quantity': med.stock_quantity,
                'is_in_stock': med.stock_quantity > 0
            } for med in medicines_qs
        ]
        logger.debug(f"Fetched {len(medicines)} products from local Medicine model")
        
        if medicines:
            return render(request, 'home.html', {'medicines': medicines, 'category': category})
    
    except Exception as e:
        logger.error(f"Error fetching from local Medicine model: {e}")

    try:
        response = requests.get('http://127.0.0.1:5000/api/products')
        response.raise_for_status()
        api_medicines = response.json()
        
        for med in api_medicines:
            try:
                local_med = Medicine.objects.get(name__iexact=med['name'])
                med['stock_quantity'] = local_med.stock_quantity
                med['is_in_stock'] = local_med.stock_quantity > 0
            except Medicine.DoesNotExist:
                med['is_in_stock'] = med.get('stock_quantity', 0) > 0
                Medicine.objects.get_or_create(
                    name=med['name'],
                    defaults={
                        'description': med.get('description', ''),
                        'price': med.get('price', 0.0),
                        'image_url': med.get('image_url', ''),
                        'category': med.get('category', ''),
                        'stock_quantity': med.get('stock_quantity', 0)
                    }
                )
        
        if category != 'all':
            medicines = [med for med in api_medicines if med['category'] == category and query.lower() in med['name'].lower()]
        elif query:
            medicines = [med for med in api_medicines if query.lower() in med['name'].lower()]
        else:
            medicines = api_medicines
        
        logger.debug(f"Fetched {len(medicines)} products from API")
    
    except requests.RequestException as e:
        logger.error(f"Failed to fetch products from API: {e}")
        messages.error(request, "Unable to fetch products. Please try again later.")

    if not medicines:
        messages.warning(request, "No medicines found matching your criteria.")
    
    return render(request, 'home.html', {'medicines': medicines, 'category': category})

def product_description_view(request, product_name):
    logger.debug(f"Received product_name: {product_name}")
    try:
        encoded_product_name = urllib.parse.quote(product_name)
        product_response = requests.get(f'http://127.0.0.1:5000/api/products/{encoded_product_name}/')
        product_response.raise_for_status()
        product = product_response.json()
        try:
            local_med = Medicine.objects.get(name__iexact=product_name)
            product['stock_quantity'] = local_med.stock_quantity
            product['is_in_stock'] = local_med.stock_quantity > 0
        except Medicine.DoesNotExist:
            product['is_in_stock'] = product.get('stock_quantity', 0) > 0
        
        comments_response = requests.get(f'http://127.0.0.1:5000/api/products/{encoded_product_name}/comments')
        comments_response.raise_for_status()
        comments = comments_response.json()
        
        avg_rating = 0
        if comments:
            total_rating = sum(comment['rating'] for comment in comments)
            avg_rating = round(total_rating / len(comments), 1)
        
        return render(request, 'product_description.html', {
            'product': product,
            'comments': comments,
            'avg_rating': avg_rating
        })
    except requests.RequestException as e:
        logger.error(f"API error for {product_name}: {e}")
        try:
            medicine = Medicine.objects.get(name__iexact=product_name)
            product = {
                'id': medicine.id,
                'name': medicine.name,
                'description': medicine.description,
                'price': float(medicine.price),
                'image_url': medicine.image_url,
                'category': medicine.category,
                'stock_quantity': medicine.stock_quantity,
                'is_in_stock': medicine.stock_quantity > 0
            }
            return render(request, 'product_description.html', {
                'product': product,
                'comments': [],
                'avg_rating': 0,
                'warning_message': f"Using local data for '{product_name}' due to API unavailability."
            })
        except Medicine.DoesNotExist:
            return render(request, 'product_description.html', {
                'product': None,
                'comments': [],
                'avg_rating': 0,
                'warning_message': "No product available."
            })



def add_comment(request, product_name):
    if not request.user.is_authenticated:
        messages.error(request, "Please log in to submit a review.")
        return redirect('login')

    if request.method == 'POST':
        reviewer_name = request.POST.get('reviewer_name')
        reviewer_email = request.POST.get('reviewer_email')
        rating = request.POST.get('rating')
        comment_text = request.POST.get('comment_text')

        # Validate input
        if not all([reviewer_name, reviewer_email, rating, comment_text]):
            messages.error(request, "All fields are required.")
            return redirect('product_description', product_name=product_name)

        # Validate email format
        validator = EmailValidator()
        try:
            validator(reviewer_email)
        except ValidationError:
            messages.error(request, "Invalid email format.")
            return redirect('product_description', product_name=product_name)

        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError("Rating must be between 1 and 5")
        except (ValueError, TypeError):
            messages.error(request, "Invalid rating.")
            return redirect('product_description', product_name=product_name)

        # Check if product exists in Flask API
        try:
            encoded_product_name = urllib.parse.quote(product_name)
            product_response = requests.get(f'http://127.0.0.1:5000/api/products/{encoded_product_name}/')
            product_response.raise_for_status()
        except requests.RequestException:
            messages.error(request, "Product not found.")
            return redirect('product_description', product_name=product_name)

        # Send comment to Flask API
        data = {
            'reviewer_name': reviewer_name,
            'reviewer_email': reviewer_email,
            'rating': rating,
            'comment_text': comment_text
        }
        try:
            response = requests.post(
                f'http://127.0.0.1:5000/api/products/{encoded_product_name}/comments',
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            messages.success(request, "Review submitted successfully.")
        except requests.RequestException as e:
            logger.error(f"Failed to submit comment for {product_name}: {e}")
            messages.error(request, "Failed to submit review. Please try again later.")

        return redirect('product_description', product_name=product_name)
    
    messages.error(request, "Invalid request.")
    return redirect('product_description', product_name=product_name)

# ... other views ...


@transaction.atomic
def add_to_cart(request):
    if not request.user.is_authenticated:
        logger.debug("User not authenticated, redirecting to login")
        messages.error(request, "Please log in to add items to your cart.")
        return redirect('login')

    if request.method != 'POST':
        logger.warning("Invalid request method for add_to_cart")
        messages.error(request, "Invalid request. Please use the add to cart button.")
        return redirect('home')

    product_name = request.POST.get('product_name')
    product_price = request.POST.get('product_price')
    product_image_url = request.POST.get('product_image_url')
    product_category = request.POST.get('product_category')
    quantity = request.POST.get('quantity', '1')

    logger.debug(f"Add to cart: product_name={product_name}, quantity={quantity}")

    if not all([product_name, product_price, product_image_url, product_category]):
        logger.error("Missing required form fields")
        messages.error(request, "Invalid product data. Please try again.")
        return redirect('product_description', product_name=product_name or 'unknown')

    try:
        product_price = float(product_price)
        quantity = int(quantity)
        if quantity < 1 or quantity > 10:
            raise ValueError("Quantity must be between 1 and 10")
    except (ValueError, TypeError) as e:
        logger.error(f"Invalid price or quantity: {e}")
        messages.error(request, f"Invalid price or quantity: {e}.")
        return redirect('product_description', product_name=product_name)

    try:
        medicine = Medicine.objects.get(name__iexact=product_name)
        if medicine.stock_quantity < quantity:
            logger.warning(f"Insufficient stock for {product_name}: requested={quantity}, available={medicine.stock_quantity}")
            messages.error(request, f"Only {medicine.stock_quantity} {product_name} available.")
            return redirect('product_description', product_name=product_name)
    except Medicine.DoesNotExist:
        try:
            encoded_product_name = urllib.parse.quote(product_name)
            response = requests.get(f'http://127.0.0.1:5000/api/products/{encoded_product_name}/')
            response.raise_for_status()
            product = response.json()
            if product.get('stock_quantity', 0) < quantity:
                logger.warning(f"Insufficient API stock for {product_name}: requested={quantity}, available={product.get('stock_quantity', 0)}")
                messages.error(request, f"Only {product.get('stock_quantity', 0)} {product_name} available.")
                return redirect('product_description', product_name=product_name)
            medicine = Medicine.objects.create(
                name=product_name,
                price=product_price,
                image_url=product_image_url,
                category=product_category,
                description=product.get('description', ''),
                stock_quantity=product.get('stock_quantity', 0)
            )
            logger.info(f"Created Medicine: {product_name}")
        except requests.RequestException as e:
            logger.error(f"API unavailable for {product_name}: {e}")
            messages.error(request, f"Cannot add {product_name} to cart: Product not found.")
            return redirect('product_description', product_name=product_name)

    medicine.stock_quantity -= quantity
    medicine.save()
    logger.debug(f"Updated stock for {product_name}: new stock={medicine.stock_quantity}")

    try:
        encoded_name = urllib.parse.quote(product_name)
        response = requests.patch(
            f'http://127.0.0.1:5000/api/products/{encoded_name}/',
            json={'stock_quantity': medicine.stock_quantity}
        )
        response.raise_for_status()
        logger.info(f"Synced stock for {product_name}: {medicine.stock_quantity}")
    except requests.RequestException as e:
        logger.error(f"Failed to sync stock for {product_name}: {e}")
        messages.warning(request, f"Added to cart, but stock sync failed.")

    try:
        order, created = Order.objects.get_or_create(
            user=request.user,
            is_paid=False,
            defaults={'status': 'ordered'}
        )
        order_item, created = OrderItem.objects.get_or_create(
            order=order,
            medicine=medicine,
            defaults={'quantity': quantity}
        )
        if not created:
            order_item.quantity += quantity
            order_item.save()
            logger.debug(f"Updated OrderItem: {order_item.medicine.name}, quantity={order_item.quantity}")
        else:
            logger.debug(f"Created OrderItem: {order_item.medicine.name}, quantity={quantity}")

        messages.success(request, f"{product_name} (x{quantity}) added to cart.")
        logger.info(f"Added {product_name} (x{quantity}) to cart for {request.user.username}")
        return redirect('my_orders')
    except Exception as e:
        logger.error(f"Failed to add {product_name} to cart: {e}")
        messages.error(request, f"Failed to add {product_name} to cart.")
        return redirect('product_description', product_name=product_name)

def my_orders(request):
    if not request.user.is_authenticated:
        logger.debug("User not authenticated, redirecting to login")
        return redirect('login')
    
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    orders_data = []
    for order in orders:
        total_price = sum(item.medicine.price * item.quantity for item in order.items.all())
        orders_data.append({
            'order': order,
            'total_price': total_price,
            'items': order.items.all()
        })
    
    if not orders:
        logger.debug(f"No orders found for {request.user.username}")
    
    return render(request, 'myorders.html', {
        'orders_data': orders_data
    })

def update_quantity(request, item_id):
    if not request.user.is_authenticated:
        return redirect('login')

    item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)
    action = request.POST.get('action')

    if action == 'increase':
        if item.medicine.stock_quantity < 1:
            messages.error(request, f"Cannot add more {item.medicine.name}: Out of stock.")
            return redirect('my_orders')
        item.quantity += 1
        item.medicine.stock_quantity -= 1
        item.medicine.save()
    elif action == 'decrease' and item.quantity > 1:
        item.quantity -= 1
        item.medicine.stock_quantity += 1
        item.medicine.save()

    item.save()

    try:
        encoded_name = urllib.parse.quote(item.medicine.name)
        response = requests.patch(
            f'http://127.0.0.1:5000/api/products/{encoded_name}/',
            json={'stock_quantity': item.medicine.stock_quantity}
        )
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to sync stock for {item.medicine.name}: {e}")
        messages.warning(request, f"Quantity updated, but stock sync failed.")

    messages.success(request, f"Updated quantity for {item.medicine.name} to {item.quantity}.")
    return redirect('my_orders')

def clear_orders(request):
    if not request.user.is_authenticated:
        return redirect('login')

    orders = Order.objects.filter(user=request.user, is_paid=False)
    for order in orders:
        for item in order.items.all():
            item.medicine.stock_quantity += item.quantity
            item.medicine.save()
            try:
                encoded_name = urllib.parse.quote(item.medicine.name)
                response = requests.patch(
                    f'http://127.0.0.1:5000/api/products/{encoded_name}/',
                    json={'stock_quantity': item.medicine.stock_quantity}
                )
                response.raise_for_status()
            except requests.RequestException as e:
                logger.error(f"Failed to sync stock for {item.medicine.name}: {e}")

    orders.delete()
    messages.success(request, "Cart cleared successfully.")
    return redirect('my_orders')

def checkout(request, order_id):
    if not request.user.is_authenticated:
        logger.debug("User not authenticated, redirecting to login")
        return redirect('login')
    
    order = get_object_or_404(Order, id=order_id, user=request.user, is_paid=False)
    total_price = sum(item.medicine.price * item.quantity for item in order.items.all())
    logger.debug(f"Checkout for {request.user.username}: Order ID={order.id}, Total Price={total_price}")
    
    return render(request, 'checkout.html', {
        'order': order,
        'total_price': total_price,
        'payment_success': False
    })

def make_payment(request, order_id):
    if not request.user.is_authenticated:
        logger.debug("User not authenticated, redirecting to login")
        return redirect('login')
    
    if request.method != 'POST':
        messages.error(request, "Invalid request.")
        return redirect('my_orders')
    
    order = get_object_or_404(Order, id=order_id, user=request.user, is_paid=False)
    total_price = sum(item.medicine.price * item.quantity for item in order.items.all())
    
    # Mark order as paid and update status
    order.is_paid = True
    order.status = 'processing'
    order.save()
    
    # Prepare email
    user_name = request.user.get_full_name() or request.user.username
    subject = f'SwiftCare Invoice - Order #{order.id}'
    try:
        html_message = render_to_string('invoice_email.html', {
            'user_name': user_name,
            'order': order,
            'total_price': total_price
        })
        plain_message = strip_tags(html_message)
        
        if not request.user.email:
            logger.warning(f"No email address for user {request.user.username} for Order #{order.id}")
            messages.warning(request, "Payment successful, but no email address is set. Invoice could not be sent.")
        else:
            try:
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=None,  # Uses DEFAULT_FROM_EMAIL
                    recipient_list=[request.user.email],
                    html_message=html_message,
                    fail_silently=False
                )
                logger.info(f"Invoice email sent to {request.user.email} for Order #{order.id}")
                messages.success(request, "Payment successful. Your order is in processing. A copy of the invoice has been sent to your email.")
            except smtplib.SMTPAuthenticationError as e:
                logger.error(f"SMTP authentication failed for Order #{order.id}: {e}")
                messages.warning(request, "Payment successful, but failed to send invoice email due to authentication error. Please check your email settings.")
            except smtplib.SMTPException as e:
                logger.error(f"SMTP error sending email for Order #{order.id}: {e}")
                messages.warning(request, "Payment successful, but failed to send invoice email due to server issues. Please try again later.")
            except Exception as e:
                logger.error(f"Unexpected error sending email for Order #{order.id}: {e}")
                messages.warning(request, "Payment successful, but failed to send invoice email. Please check your email settings.")
    
    except TemplateDoesNotExist as e:
        logger.error(f"Template 'invoice_email.html' not found for Order #{order.id}: {e}")
        messages.warning(request, "Payment successful, but failed to generate invoice email. Please ensure the email template exists.")
    except TemplateSyntaxError as e:
        logger.error(f"Template syntax error in 'invoice_email.html' for Order #{order.id}: {e}")
        messages.warning(request, "Payment successful, but failed to generate invoice email due to template syntax error. Please check the template.")
    except Exception as e:
        logger.error(f"Unexpected error rendering invoice email template for Order #{order.id}: {e}")
        messages.warning(request, "Payment successful, but failed to generate invoice email. Please check the template configuration.")
    
    logger.info(f"Payment completed for {request.user.username}: Order ID={order.id}, Status={order.status}")
    
    return render(request, 'checkout.html', {
        'order': order,
        'total_price': total_price,
        'payment_success': True
    })

def invoice(request, order_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    order = get_object_or_404(Order, id=order_id, user=request.user)
    total_price = sum(item.medicine.price * item.quantity for item in order.items.all())
    logger.debug(f"Invoice fetched for {request.user.username}: Order ID={order.id}, Total Price={total_price}")
    
    return render(request, 'invoice.html', {
        'order': order,
        'total_price': total_price
    })