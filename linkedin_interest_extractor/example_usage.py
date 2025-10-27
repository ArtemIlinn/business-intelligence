"""
Example usage of LinkedIn Interest Extractor

This script demonstrates how to use the LinkedIn interest extraction module.
"""

import os
from linkedin_extractor import LinkedInInterestExtractor, extract_interests_from_linkedin


def example_1_simple_usage():
    """Example 1: Simple usage with convenience function"""
    print("=" * 60)
    print("Example 1: Simple Usage")
    print("=" * 60)

    linkedin_url = "https://www.linkedin.com/in/example-user/"

    try:
        interests = extract_interests_from_linkedin(
            linkedin_url,
            provider="openai"  # or "anthropic"
        )

        print(f"\nExtracted interests from: {linkedin_url}")
        print("\nTopics of Interest:")
        for i, topic in enumerate(interests, 1):
            print(f"  {i}. {topic}")

    except Exception as e:
        print(f"Error: {e}")


def example_2_advanced_usage():
    """Example 2: Advanced usage with class instance"""
    print("\n" + "=" * 60)
    print("Example 2: Advanced Usage with Class")
    print("=" * 60)

    # Initialize extractor
    extractor = LinkedInInterestExtractor(
        openai_api_key=os.getenv('OPENAI_API_KEY')
    )

    linkedin_url = "https://www.linkedin.com/in/example-user/"

    # Validate URL first
    if not extractor.validate_linkedin_url(linkedin_url):
        print("Invalid LinkedIn URL!")
        return

    # Extract username
    username = extractor.extract_username_from_url(linkedin_url)
    print(f"\nLinkedIn Username: {username}")

    # Extract interests
    try:
        interests = extractor.extract_from_url(linkedin_url, provider="openai")

        print(f"\nExtracted {len(interests)} topics:")
        for topic in interests:
            print(f"  - {topic}")

    except Exception as e:
        print(f"Error: {e}")


def example_3_text_input():
    """Example 3: Using profile text directly (recommended approach)"""
    print("\n" + "=" * 60)
    print("Example 3: Extract from Profile Text Directly")
    print("=" * 60)

    # Sample LinkedIn profile text (user would paste this)
    profile_text = """
    Senior Product Manager at TechCorp | Building AI-Powered Solutions

    About:
    Passionate product leader with 8+ years of experience building fintech solutions
    in the MENA region. Currently focused on AI agents for financial services,
    particularly in B2B payments and banking automation. Strong background in
    machine learning, conversational AI, and enterprise SaaS platforms.

    Experience:
    - Leading product development for AI-powered payment orchestration
    - Built ML models for fraud detection and risk assessment
    - Launched several successful B2B SaaS products in MENA markets
    - Expert in regulatory compliance for financial technology

    Skills:
    Product Management, FinTech, AI/ML, B2B SaaS, MENA Markets,
    Payment Systems, Conversational AI, Enterprise Solutions
    """

    extractor = LinkedInInterestExtractor()

    try:
        interests = extractor.extract_from_text(profile_text, provider="openai")

        print("\nExtracted Topics of Interest:")
        for i, topic in enumerate(interests, 1):
            print(f"  {i}. {topic}")

        # Return as list for integration
        print(f"\nReturned as: {interests}")

    except Exception as e:
        print(f"Error: {e}")


def example_4_multiple_providers():
    """Example 4: Compare results from different LLM providers"""
    print("\n" + "=" * 60)
    print("Example 4: Compare OpenAI vs Anthropic")
    print("=" * 60)

    profile_text = """
    Machine Learning Engineer specializing in NLP and computer vision.
    Currently building healthcare AI solutions for medical imaging analysis.
    Passionate about deep learning, transformers, and edge AI deployment.
    """

    extractor = LinkedInInterestExtractor()

    # Try OpenAI
    try:
        print("\nUsing OpenAI GPT-4o-mini:")
        interests_openai = extractor.extract_from_text(profile_text, provider="openai")
        for topic in interests_openai:
            print(f"  - {topic}")
    except Exception as e:
        print(f"  OpenAI Error: {e}")

    # Try Anthropic
    try:
        print("\nUsing Anthropic Claude Haiku:")
        interests_anthropic = extractor.extract_from_text(profile_text, provider="anthropic")
        for topic in interests_anthropic:
            print(f"  - {topic}")
    except Exception as e:
        print(f"  Anthropic Error: {e}")


def example_5_integration_ready():
    """Example 5: Production-ready integration format"""
    print("\n" + "=" * 60)
    print("Example 5: Integration-Ready Format")
    print("=" * 60)

    def process_linkedin_for_user(user_id: str, linkedin_url: str) -> dict:
        """
        This is how you'd integrate it into your existing system.

        Args:
            user_id: Your internal user ID
            linkedin_url: LinkedIn URL provided by user

        Returns:
            dict: Result with interests and metadata
        """
        extractor = LinkedInInterestExtractor()

        result = {
            'user_id': user_id,
            'linkedin_url': linkedin_url,
            'interests': [],
            'status': 'success',
            'error': None
        }

        try:
            # Validate URL
            if not extractor.validate_linkedin_url(linkedin_url):
                result['status'] = 'error'
                result['error'] = 'Invalid LinkedIn URL'
                return result

            # Extract interests
            interests = extractor.extract_from_url(linkedin_url, provider="openai")
            result['interests'] = interests

        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)

        return result

    # Example usage
    result = process_linkedin_for_user(
        user_id="12345",
        linkedin_url="https://www.linkedin.com/in/test-user/"
    )

    print(f"\nIntegration Result:")
    print(f"  User ID: {result['user_id']}")
    print(f"  Status: {result['status']}")
    print(f"  Interests: {result['interests']}")
    print(f"  Error: {result['error']}")

    print("\n💡 This format can be easily saved to your database!")


if __name__ == "__main__":
    print("LinkedIn Interest Extractor - Example Usage\n")

    # Check for API keys
    if not os.getenv('OPENAI_API_KEY') and not os.getenv('ANTHROPIC_API_KEY'):
        print("⚠️  Warning: No API keys found in environment variables.")
        print("   Set OPENAI_API_KEY or ANTHROPIC_API_KEY to run examples.\n")

    # Run examples
    # Note: Examples 1 and 2 will likely fail due to LinkedIn anti-scraping
    # Example 3 (text input) is the RECOMMENDED approach

    # example_1_simple_usage()  # Will likely fail - LinkedIn blocks scraping
    # example_2_advanced_usage()  # Will likely fail - LinkedIn blocks scraping

    example_3_text_input()  # RECOMMENDED: Use profile text directly
    # example_4_multiple_providers()  # Compare LLM providers
    example_5_integration_ready()  # Production integration example

    print("\n" + "=" * 60)
    print("✅ Examples completed!")
    print("=" * 60)
    print("\n💡 Recommendation: Use Example 3 approach (text input)")
    print("   Have users paste their LinkedIn 'About' section or profile text.")
    print("   This avoids LinkedIn's anti-scraping measures.\n")
