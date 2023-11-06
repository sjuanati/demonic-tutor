class InvalidConfigurationError(Exception):
    """Raised when there's an issue with the configuration."""

class DataExtractionError(Exception):
    """Raised when there's an error during data extraction."""

class FilterCreationError(Exception):
    """Raised when there's an error creating the filter params."""

class BlockUtilsError(Exception):
    """Exceptions in utils.block"""