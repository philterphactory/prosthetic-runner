
class UnreportedException(Exception):
    """Raise this exception to prevent the errormon middleware from kicking in."""
    pass
