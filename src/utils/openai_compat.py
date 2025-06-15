"""Compatibility layer for OpenAI API to handle different library versions.

This module provides compatibility between different versions of the OpenAI Python library,
particularly between v0.x.x and v1.x.x which had significant API changes.
"""

import inspect
import sys
import importlib

# Import OpenAI
import openai

# Determine OpenAI version
OPENAI_V1 = hasattr(openai, "__version__") and openai.__version__.startswith("1.")

# Define error classes for v1 compatibility
class OpenAIError(Exception):
    """Base exception class for OpenAI errors"""
    pass

class APIError(OpenAIError):
    """Exception raised when the API responds with an error"""
    pass

class RateLimitError(OpenAIError):
    """Exception raised when rate limit is exceeded"""
    pass

class APIConnectionError(OpenAIError):
    """Exception raised when connection to OpenAI API fails"""
    pass

class InvalidRequestError(OpenAIError):
    """Exception raised when request is invalid"""
    pass

class AuthenticationError(OpenAIError):
    """Exception raised when authentication fails"""
    pass

class Timeout(OpenAIError):
    """Exception raised when request times out"""
    pass

class ServiceUnavailableError(OpenAIError):
    """Exception raised when service is unavailable"""
    pass

class TryAgain(OpenAIError):
    """Exception raised when a request should be retried"""
    pass

class PermissionError(OpenAIError):
    """Exception raised when user doesn't have permission"""
    pass

class InvalidAPIType(OpenAIError):
    """Exception raised when the wrong type of API is used"""
    pass

# Create compatibility error module
class ErrorModule:
    def __init__(self):
        self.APIError = APIError
        self.RateLimitError = RateLimitError
        self.APIConnectionError = APIConnectionError
        self.InvalidRequestError = InvalidRequestError
        self.AuthenticationError = AuthenticationError
        self.Timeout = Timeout
        self.ServiceUnavailableError = ServiceUnavailableError
        self.TryAgain = TryAgain
        self.PermissionError = PermissionError
        self.InvalidAPIType = InvalidAPIType
        self.OpenAIError = OpenAIError

# Attach error module to OpenAI if it doesn't exist
if not hasattr(openai, "error"):
    openai.error = ErrorModule()

# Function to map OpenAI v1 errors to v0 style errors
def map_openai_error(error):
    """Map OpenAI v1 errors to v0 style errors for compatibility"""
    if OPENAI_V1:
        error_type = type(error).__name__
        if error_type == "APIError":
            return openai.error.APIError(str(error))
        elif error_type == "RateLimitError":
            return openai.error.RateLimitError(str(error))
        elif error_type == "APIConnectionError":
            return openai.error.APIConnectionError(str(error))
        elif error_type == "InvalidRequestError":
            return openai.error.InvalidRequestError(str(error))
        elif error_type == "AuthenticationError":
            return openai.error.AuthenticationError(str(error))
        elif error_type == "Timeout" or "TimeoutError" in error_type:
            return openai.error.Timeout(str(error))
        elif error_type == "ServiceUnavailableError":
            return openai.error.ServiceUnavailableError(str(error))
        elif error_type == "TryAgain":
            return openai.error.TryAgain(str(error))
        elif error_type == "PermissionError":
            return openai.error.PermissionError(str(error))
        elif error_type == "InvalidAPIType":
            return openai.error.InvalidAPIType(str(error))
        else:
            return openai.error.OpenAIError(str(error))
    return error
