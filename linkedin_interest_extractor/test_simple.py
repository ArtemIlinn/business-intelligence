"""
Simple Test Script for LinkedIn Interest Extractor

Quick test to verify the module works correctly.
"""

import os
from linkedin_extractor import LinkedInInterestExtractor


def test_with_sample_profile():
    """Test extraction with a sample LinkedIn profile text"""

    # Sample profile text
    sample_profile = """
    Product Manager at FinTech Startup | Building AI Solutions for Financial Services

    About:
    Experienced product manager specializing in fintech and AI agents. Currently building
    intelligent automation solutions for banking in the MENA region. Passionate about
    B2B SaaS, conversational AI, and payment orchestration platforms.

    Previously led product teams at major tech companies, launching several successful
    enterprise solutions. Strong technical background in machine learning, natural
    language processing, and distributed systems.

    Focus Areas:
    - FinTech innovation in emerging markets
    - AI-powered banking automation
    - B2B SaaS product development
    - Payment systems and compliance
    - Enterprise software architecture

    Skills:
    Product Management, FinTech, AI/ML, B2B SaaS, MENA Markets, Payment Systems,
    Machine Learning, Enterprise Solutions, Conversational AI, Banking Technology
    """

    print("=" * 70)
    print("LinkedIn Interest Extractor - Simple Test")
    print("=" * 70)

    # Check for API key
    if not os.getenv('OPENAI_API_KEY') and not os.getenv('ANTHROPIC_API_KEY'):
        print("\n❌ Error: No API keys found!")
        print("Please set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable.")
        print("\nExample:")
        print("  export OPENAI_API_KEY='your-key-here'")
        return

    # Initialize extractor
    print("\n✓ Initializing extractor...")
    extractor = LinkedInInterestExtractor()

    # Determine provider
    provider = "openai" if os.getenv('OPENAI_API_KEY') else "anthropic"
    print(f"✓ Using provider: {provider}")

    # Extract interests
    print("\n⏳ Extracting interests from sample profile...")

    try:
        interests = extractor.extract_from_text(sample_profile, provider=provider)

        print(f"\n✅ Success! Extracted {len(interests)} topics:\n")

        for i, topic in enumerate(interests, 1):
            print(f"  {i}. {topic}")

        print("\n" + "=" * 70)
        print("Test completed successfully!")
        print("=" * 70)

        print("\n📦 Output format (ready for integration):")
        print(f"  Type: {type(interests)}")
        print(f"  Value: {interests}")

        print("\n💡 Next steps:")
        print("  1. Review the extracted topics above")
        print("  2. Check example_usage.py for integration patterns")
        print("  3. Integrate into your database/application")

        return interests

    except Exception as e:
        print(f"\n❌ Error during extraction: {e}")
        print("\nTroubleshooting:")
        print("  - Check your API key is valid")
        print("  - Verify you have internet connection")
        print("  - Try with a different provider")
        return None


if __name__ == "__main__":
    test_with_sample_profile()
