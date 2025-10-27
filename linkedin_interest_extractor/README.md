# LinkedIn Interest Extractor

A standalone Python module that extracts user interests and professional focus areas from LinkedIn profiles using AI/LLM analysis.

## Features

- Extract interests from LinkedIn profile URLs
- **Recommended**: Extract interests from pasted profile text (bypasses LinkedIn scraping issues)
- Support for multiple LLM providers (OpenAI GPT, Anthropic Claude)
- Low-temperature LLM calls for consistent, accurate extraction
- Returns clean list of topic strings ready for database integration
- Modular and standalone design for easy integration

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Set up API keys

```bash
export OPENAI_API_KEY="your-openai-api-key"
# or
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

### Basic Usage

```python
from linkedin_extractor import extract_interests_from_linkedin

# Simple usage
interests = extract_interests_from_linkedin(
    linkedin_url="https://www.linkedin.com/in/username/",
    provider="openai"
)

print(interests)
# Output: ['FinTech in MENA', 'AI Agents', 'B2B SaaS', 'Payment Systems', ...]
```

### Recommended Usage (Profile Text Input)

Due to LinkedIn's anti-scraping measures, the **recommended approach** is to have users paste their profile text:

```python
from linkedin_extractor import LinkedInInterestExtractor

profile_text = """
Senior Product Manager at TechCorp | Building AI-Powered Solutions

About:
Passionate product leader with 8+ years of experience building fintech solutions
in the MENA region. Currently focused on AI agents for financial services...
"""

extractor = LinkedInInterestExtractor()
interests = extractor.extract_from_text(profile_text, provider="openai")

print(interests)
# Output: ['FinTech', 'MENA Markets', 'AI Agents', 'Financial Services', ...]
```

## API Reference

### `LinkedInInterestExtractor` Class

#### Constructor

```python
extractor = LinkedInInterestExtractor(
    openai_api_key=None,      # Optional, defaults to OPENAI_API_KEY env var
    anthropic_api_key=None    # Optional, defaults to ANTHROPIC_API_KEY env var
)
```

#### Methods

**`extract_from_url(linkedin_url, provider="openai")`**
- Extracts interests from LinkedIn profile URL
- **Note**: May fail due to LinkedIn anti-scraping measures
- Returns: `List[str]` of interest topics

**`extract_from_text(profile_text, provider="openai")`** ⭐ **RECOMMENDED**
- Extracts interests from profile text directly
- More reliable than URL scraping
- Returns: `List[str]` of interest topics

**`validate_linkedin_url(url)`**
- Validates if URL is a proper LinkedIn profile
- Returns: `bool`

**`extract_username_from_url(url)`**
- Extracts username from LinkedIn URL
- Returns: `str` or `None`

### Convenience Function

```python
extract_interests_from_linkedin(
    linkedin_url: str,
    openai_api_key: Optional[str] = None,
    anthropic_api_key: Optional[str] = None,
    provider: str = "openai"
) -> List[str]
```

## Integration Examples

### Example 1: Telegram Bot Integration

```python
from linkedin_extractor import LinkedInInterestExtractor

def handle_linkedin_command(user_id: int, linkedin_url: str):
    extractor = LinkedInInterestExtractor()

    try:
        # Validate URL
        if not extractor.validate_linkedin_url(linkedin_url):
            return "Please provide a valid LinkedIn URL"

        # Extract interests
        interests = extractor.extract_from_url(linkedin_url)

        # Save to database (your implementation)
        save_user_interests(user_id, interests)

        return f"Extracted {len(interests)} topics: {', '.join(interests)}"

    except Exception as e:
        return f"Error: {str(e)}"
```

### Example 2: Database Integration

```python
def process_and_save_interests(user_id: str, profile_text: str, db_connection):
    extractor = LinkedInInterestExtractor()

    try:
        # Extract interests
        interests = extractor.extract_from_text(profile_text)

        # Save to database
        for topic in interests:
            db_connection.execute(
                "INSERT INTO user_interests (user_id, topic) VALUES (?, ?)",
                (user_id, topic)
            )

        db_connection.commit()
        return True, interests

    except Exception as e:
        return False, str(e)
```

### Example 3: API Endpoint

```python
from flask import Flask, request, jsonify
from linkedin_extractor import LinkedInInterestExtractor

app = Flask(__name__)
extractor = LinkedInInterestExtractor()

@app.route('/extract-interests', methods=['POST'])
def extract_interests():
    data = request.json
    profile_text = data.get('profile_text', '')

    if not profile_text:
        return jsonify({'error': 'profile_text is required'}), 400

    try:
        interests = extractor.extract_from_text(profile_text)
        return jsonify({
            'success': True,
            'interests': interests,
            'count': len(interests)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

## LLM Providers

### OpenAI (Recommended for Speed)

- Model: `gpt-4o-mini` (fast and cost-effective)
- Temperature: 0.1 (low for consistent extraction)
- Cost: ~$0.00015 per request (very cheap)

```python
interests = extractor.extract_from_text(text, provider="openai")
```

### Anthropic Claude

- Model: `claude-3-haiku-20240307` (fast and accurate)
- Temperature: 0.1
- Cost: ~$0.00025 per request

```python
interests = extractor.extract_from_text(text, provider="anthropic")
```

## Important Notes

### LinkedIn Scraping Limitations

LinkedIn has strong anti-scraping measures:
- Blocks automated requests
- Requires authentication for full profiles
- Frequently changes HTML structure

**Recommended Solutions:**

1. **Profile Text Input** (Best) - Have users paste their profile content
2. **LinkedIn API** - Use official API (requires approval)
3. **Third-party services** - Use services like Proxycurl, PhantomBuster
4. **Browser automation** - Use Selenium with authenticated session (complex)

### For Production Use

```python
# Option 1: User pastes profile text (RECOMMENDED)
def get_interests_from_pasted_text(text):
    extractor = LinkedInInterestExtractor()
    return extractor.extract_from_text(text)

# Option 2: Use third-party service (e.g., Proxycurl)
def get_interests_from_proxycurl(linkedin_url):
    # Fetch profile using Proxycurl API
    profile_data = proxycurl_client.get_profile(linkedin_url)

    # Combine relevant fields
    profile_text = f"{profile_data['headline']} {profile_data['summary']}"

    # Extract interests
    extractor = LinkedInInterestExtractor()
    return extractor.extract_from_text(profile_text)
```

## Output Format

The extractor returns a list of strings:

```python
[
    "FinTech in MENA",
    "AI Agents",
    "B2B SaaS",
    "Payment Systems",
    "Machine Learning",
    "Enterprise Solutions",
    "Regulatory Compliance"
]
```

These can be directly saved to your database as user interests/topics.

## Error Handling

```python
from linkedin_extractor import LinkedInInterestExtractor

extractor = LinkedInInterestExtractor()

try:
    interests = extractor.extract_from_url(linkedin_url)
except ValueError as e:
    print(f"Invalid input: {e}")
except Exception as e:
    print(f"Extraction failed: {e}")
```

## Testing

Run the example script:

```bash
python example_usage.py
```

This demonstrates:
- Simple usage
- Advanced usage with class
- Text input (recommended)
- Multiple provider comparison
- Integration-ready format

## Configuration

Set environment variables:

```bash
# .env file
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=your-key-here
```

Or pass directly:

```python
extractor = LinkedInInterestExtractor(
    openai_api_key="your-key",
    anthropic_api_key="your-key"
)
```

## Dependencies

- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `openai` - OpenAI API client
- `anthropic` - Anthropic API client
- `lxml` - Fast HTML parser

## Roadmap

- [ ] Add support for more LLM providers (Cohere, Mistral)
- [ ] Implement caching for repeated extractions
- [ ] Add confidence scores for extracted topics
- [ ] Support batch processing of multiple profiles
- [ ] Add topic categorization (tech, business, industry)

## License

MIT License - Feel free to use and modify

## Support

For issues or questions, refer to the example_usage.py file for detailed usage patterns.

## Integration Checklist

- [ ] Install dependencies (`pip install -r requirements.txt`)
- [ ] Set up API keys (OPENAI_API_KEY or ANTHROPIC_API_KEY)
- [ ] Choose input method (URL or text - text recommended)
- [ ] Test with example_usage.py
- [ ] Integrate into your existing codebase
- [ ] Add database saving logic
- [ ] Handle errors appropriately
- [ ] Monitor API costs

---

**Last Updated:** 2025-10-27
**Author:** Claude
**Version:** 1.0.0
