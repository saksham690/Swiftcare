import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)

class SwiftCartConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'SwiftCart'

    def ready(self):
        logger.info("SwiftCart AppConfig ready: Loading signals")
        try:
            import SwiftCart.signals  # Import signals to register them
            logger.debug("Successfully imported SwiftCart.signals")
        except ImportError as e:
            logger.error(f"Failed to import SwiftCart.signals: {e}")