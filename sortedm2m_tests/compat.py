try:
    from unittest import skipIf
except ImportError:
    # Will raise deprecation warning in Django >= 1.8
    from django.utils.unittest import skipIf
