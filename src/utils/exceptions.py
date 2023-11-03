class InvalidConfigurationError(Exception):
    """Raised when there's an issue with the configuration."""


class DataExtractionError(Exception):
    """Raised when there's an error during data extraction."""


class FilterCreationError(Exception):
    """Raised when there's an error creating the filter params."""


class TooManyResultsError(Exception):
    """Raised when there are more than 10000 results getting logs"""

    print(Exception)
