from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.template import TemplateDoesNotExist, TemplateSyntaxError
from .models import Order
import logging
import smtplib

# Set up logging
logger = logging.getLogger(__name__)

@receiver(post_save, sender=Order)
def send_delivery_email(sender, instance, created, **kwargs):
    """
    Send an email to the user when the order status changes to 'delivered'.
    """
    logger.debug(f"Signal triggered for Order #{instance.id}: created={created}, status={instance.status}, is_paid={instance.is_paid}")
    
    # Only send email for paid orders with status 'delivered' and not on creation
    if created or instance.status.lower() != 'delivered' or not instance.is_paid:
        logger.debug(f"Skipping email for Order #{instance.id}: created={created}, status={instance.status}, is_paid={instance.is_paid}")
        return

    user = instance.user
    user_name = user.get_full_name() or user.username
    total_price = sum(item.medicine.price * item.quantity for item in instance.items.all())
    subject = f'SwiftCare Delivery Confirmation - Order #{instance.id}'

    try:
        logger.debug(f"Rendering delivery_email.html for Order #{instance.id}")
        html_message = render_to_string('delivery_email.html', {
            'user_name': user_name,
            'order': instance,
            'total_price': total_price
        })
        plain_message = strip_tags(html_message)

        if not user.email:
            logger.warning(f"No email address for user {user.username} for Order #{instance.id}")
            return

        logger.debug(f"Sending delivery email to {user.email} for Order #{instance.id}")
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=None,  # Uses DEFAULT_FROM_EMAIL
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
        logger.info(f"Delivery email sent to {user.email} for Order #{instance.id}")

    except TemplateDoesNotExist as e:
        logger.error(f"Template 'delivery_email.html' not found for Order #{instance.id}: {e}")
    except TemplateSyntaxError as e:
        logger.error(f"Template syntax error in 'delivery_email.html' for Order #{instance.id}: {e}")
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP authentication failed for Order #{instance.id}: {e}")
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error sending delivery email for Order #{instance.id}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error sending delivery email for Order #{instance.id}: {e}")