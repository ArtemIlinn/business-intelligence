"""
LinkedIn Interest Extractor Module

A standalone module to extract user interests from LinkedIn profiles.
Takes a LinkedIn profile URL as input and returns a list of interest topics.

Author: Claude
Date: 2025-10-27
"""

import os
import re
import json
from typing import List, Dict, Optional
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import openai


class LinkedInInterestExtractor:
    """
    Extracts topics of interest from LinkedIn profiles using LLM analysis.
    """

    def __init__(self, openai_api_key: Optional[str] = None, anthropic_api_key: Optional[str] = None):
        """
        Initialize the extractor with API keys.

        Args:
            openai_api_key: OpenAI API key (defaults to env variable OPENAI_API_KEY)
            anthropic_api_key: Anthropic API key for Claude (defaults to env variable ANTHROPIC_API_KEY)
        """
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = anthropic_api_key or os.getenv('ANTHROPIC_API_KEY')

        if self.openai_api_key:
            openai.api_key = self.openai_api_key

    def validate_linkedin_url(self, url: str) -> bool:
        """
        Validate if the provided URL is a valid LinkedIn profile URL.

        Args:
            url: LinkedIn profile URL

        Returns:
            bool: True if valid LinkedIn profile URL
        """
        try:
            parsed = urlparse(url)
            return (
                parsed.netloc in ['www.linkedin.com', 'linkedin.com'] and
                '/in/' in parsed.path
            )
        except Exception:
            return False

    def extract_username_from_url(self, url: str) -> Optional[str]:
        """
        Extract LinkedIn username from profile URL.

        Args:
            url: LinkedIn profile URL

        Returns:
            str: Username or None if not found
        """
        if not self.validate_linkedin_url(url):
            return None

        # Extract username from URL like https://www.linkedin.com/in/username/
        match = re.search(r'/in/([^/]+)', url)
        return match.group(1) if match else None

    def scrape_linkedin_profile(self, url: str) -> Dict[str, str]:
        """
        Attempt to scrape LinkedIn profile content.

        Note: LinkedIn has strong anti-scraping measures. This is a basic implementation.
        For production use, consider:
        1. Using LinkedIn API (requires approval)
        2. Using third-party services like Proxycurl
        3. Having users paste their profile text directly

        Args:
            url: LinkedIn profile URL

        Returns:
            dict: Profile data with available fields
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Try to extract basic information
            # Note: This is very limited due to LinkedIn's anti-scraping
            profile_data = {
                'headline': '',
                'about': '',
                'experience': '',
                'skills': '',
                'raw_text': soup.get_text()[:5000]  # Limit to first 5000 chars
            }

            return profile_data

        except Exception as e:
            raise Exception(f"Failed to scrape LinkedIn profile: {str(e)}")

    def extract_interests_from_text(self, profile_text: str, provider: str = "openai") -> List[str]:
        """
        Extract interest topics from profile text using LLM.

        Args:
            profile_text: Text content from LinkedIn profile
            provider: LLM provider to use ("openai" or "anthropic")

        Returns:
            List[str]: List of interest topics
        """
        if provider == "openai":
            return self._extract_with_openai(profile_text)
        elif provider == "anthropic":
            return self._extract_with_anthropic(profile_text)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def _extract_with_openai(self, profile_text: str) -> List[str]:
        """
        Extract interests using OpenAI GPT.

        Args:
            profile_text: Text content from LinkedIn profile

        Returns:
            List[str]: List of interest topics
        """
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not provided")

        prompt = f"""Analyze the following LinkedIn profile content and extract the key topics of interest and professional focus areas.

Profile Content:
{profile_text}

Instructions:
1. Identify 5-10 key professional interests, industries, or topic areas
2. Focus on: industry domains, technologies, methodologies, business areas
3. Be specific but concise (e.g., "FinTech in MENA", "AI Agents", "B2B SaaS")
4. Return ONLY a JSON array of strings, nothing else
5. Example format: ["topic1", "topic2", "topic3"]

Topics:"""

        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",  # Fast and cost-effective
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing professional profiles and extracting key interests and focus areas. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for consistent extraction
                max_tokens=500
            )

            content = response.choices[0].message.content.strip()

            # Try to parse JSON response
            try:
                interests = json.loads(content)
                if isinstance(interests, list):
                    return [str(item) for item in interests]
            except json.JSONDecodeError:
                # Fallback: try to extract topics from text
                return self._parse_topics_from_text(content)

            return []

        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    def _extract_with_anthropic(self, profile_text: str) -> List[str]:
        """
        Extract interests using Anthropic Claude.

        Args:
            profile_text: Text content from LinkedIn profile

        Returns:
            List[str]: List of interest topics
        """
        if not self.anthropic_api_key:
            raise ValueError("Anthropic API key not provided")

        try:
            from anthropic import Anthropic

            client = Anthropic(api_key=self.anthropic_api_key)

            prompt = f"""Analyze the following LinkedIn profile content and extract the key topics of interest and professional focus areas.

Profile Content:
{profile_text}

Instructions:
1. Identify 5-10 key professional interests, industries, or topic areas
2. Focus on: industry domains, technologies, methodologies, business areas
3. Be specific but concise (e.g., "FinTech in MENA", "AI Agents", "B2B SaaS")
4. Return ONLY a JSON array of strings, nothing else
5. Example format: ["topic1", "topic2", "topic3"]"""

            response = client.messages.create(
                model="claude-3-haiku-20240307",  # Fast and cost-effective
                max_tokens=500,
                temperature=0.1,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            content = response.content[0].text.strip()

            # Try to parse JSON response
            try:
                interests = json.loads(content)
                if isinstance(interests, list):
                    return [str(item) for item in interests]
            except json.JSONDecodeError:
                return self._parse_topics_from_text(content)

            return []

        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")

    def _parse_topics_from_text(self, text: str) -> List[str]:
        """
        Fallback parser to extract topics from non-JSON text.

        Args:
            text: Text response from LLM

        Returns:
            List[str]: Extracted topics
        """
        # Try to find quoted strings
        quoted = re.findall(r'"([^"]+)"', text)
        if quoted:
            return quoted

        # Try to find bullet points or numbered lists
        lines = text.split('\n')
        topics = []
        for line in lines:
            # Remove common list markers
            cleaned = re.sub(r'^[\d\.\-\*\•]\s*', '', line.strip())
            if cleaned and len(cleaned) > 3:
                topics.append(cleaned)

        return topics[:10]  # Limit to 10 topics

    def extract_from_url(self, linkedin_url: str, provider: str = "openai") -> List[str]:
        """
        Main method: Extract interests from LinkedIn profile URL.

        Args:
            linkedin_url: LinkedIn profile URL
            provider: LLM provider ("openai" or "anthropic")

        Returns:
            List[str]: List of interest topics

        Raises:
            ValueError: If URL is invalid
            Exception: If scraping or extraction fails
        """
        # Validate URL
        if not self.validate_linkedin_url(linkedin_url):
            raise ValueError("Invalid LinkedIn profile URL. Expected format: https://www.linkedin.com/in/username")

        # Scrape profile
        try:
            profile_data = self.scrape_linkedin_profile(linkedin_url)
            profile_text = profile_data.get('raw_text', '')

            if not profile_text or len(profile_text) < 50:
                raise Exception("Unable to extract sufficient content from LinkedIn profile. LinkedIn may be blocking scraping.")

        except Exception as e:
            raise Exception(f"Failed to access LinkedIn profile: {str(e)}")

        # Extract interests using LLM
        interests = self.extract_interests_from_text(profile_text, provider=provider)

        return interests

    def extract_from_text(self, profile_text: str, provider: str = "openai") -> List[str]:
        """
        Extract interests from profile text directly (alternative to URL scraping).

        Args:
            profile_text: LinkedIn profile content as text
            provider: LLM provider ("openai" or "anthropic")

        Returns:
            List[str]: List of interest topics
        """
        if not profile_text or len(profile_text) < 20:
            raise ValueError("Profile text is too short or empty")

        return self.extract_interests_from_text(profile_text, provider=provider)


# Convenience function for simple usage
def extract_interests_from_linkedin(
    linkedin_url: str,
    openai_api_key: Optional[str] = None,
    anthropic_api_key: Optional[str] = None,
    provider: str = "openai"
) -> List[str]:
    """
    Convenience function to extract interests from LinkedIn URL.

    Args:
        linkedin_url: LinkedIn profile URL
        openai_api_key: OpenAI API key (optional, uses env var if not provided)
        anthropic_api_key: Anthropic API key (optional)
        provider: LLM provider to use

    Returns:
        List[str]: List of interest topics
    """
    extractor = LinkedInInterestExtractor(openai_api_key, anthropic_api_key)
    return extractor.extract_from_url(linkedin_url, provider=provider)
