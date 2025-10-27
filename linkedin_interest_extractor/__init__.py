"""
LinkedIn Interest Extractor Package

A standalone module for extracting user interests from LinkedIn profiles using LLM analysis.
"""

from .linkedin_extractor import (
    LinkedInInterestExtractor,
    extract_interests_from_linkedin
)

__version__ = "1.0.0"
__author__ = "Claude"

__all__ = [
    'LinkedInInterestExtractor',
    'extract_interests_from_linkedin'
]
