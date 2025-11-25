# Known Issue: Safety Filters on Educational Security Content

## Problem Summary

Even with Vertex AI and `BLOCK_NONE` safety settings, some educational security content (specifically phishing email generation) is still being blocked with:
- Finish Reason: 2 (MAX_TOKENS but actually blocked)
- HARM_CATEGORY_DANGEROUS_CONTENT: HIGH probability

## Why This Happens

Google has implemented server-side safety policies that override client-side `BLOCK_NONE` settings for certain types of content, particularly:
- Phishing/scam email generation
- Malware descriptions
- Social engineering tactics

This applies to **both** the consumer Gemini API and Vertex AI.

## Current Status

✅ **Working:**
- General conversation and training scenarios
- Security awareness questions and answers
- Threat recognition training (non-generative)
- Educational content about security concepts

❌ **Blocked:**
- Generating realistic phishing email bodies
- Creating malicious-looking URLs
- Detailed social engineering attack scenarios

## Workarounds & Solutions

### Option 1: Use Pre-Generated Content (Recommended for MVP)
Instead of generating phishing emails on-the-fly, use a curated database of real-world examples:

```python
PHISHING_TEMPLATES = [
    {
        "subject": "URGENT: Verify your account",
        "from": "security@paypa1-verify.com",
        "body": "...",
        "red_flags": ["urgency", "misspelled_domain", "generic_greeting"]
    },
    # ... more templates
]
```

**Pros:**
- No API restrictions
- Faster (no API calls)
- More controlled red flags for learning
- Can be reviewed for quality

**Cons:**
- Less dynamic/adaptive
- Requires manual curation

### Option 2: Hybrid Approach (Best for Production)
- Use templates for phishing email **structure**
- Use Gemini for **personalization** and **explanations**:

```python
# Template provides structure
template = get_phishing_template(difficulty, user_role)

# AI personalizes the narrative and provides hints
narrative = await GeminiClient.generate_text(
    prompt=f"You're narrating a training scenario where the user received this phishing email: {template}. "
           f"Describe the situation naturally without revealing it's a test.",
    model_type="flash"
)
```

**Pros:**
- Keeps AI for what it's good at (narrative, explanations, debriefs)
- Avoids safety filter issues
- Still adaptive and engaging

**Cons:**
- Requires building template library

### Option 3: Alternative AI Models
Consider using models with more permissive policies for security training:

**OpenAI GPT-4:**
- Has enterprise tier with custom safety policies
- Can be configured for educational security content
- Cost: ~$0.01-0.03 per 1K tokens

**Anthropic Claude:**
- Generally more permissive for educational content
- Strong at nuanced understanding of context
- Cost: Similar to GPT-4

**Self-Hosted Models (Llama 3, Mistral):**
- Complete control over safety settings
- Requires infrastructure (GPU hosting)
- Cost: Infrastructure only

### Option 4: Request Enterprise Access
Google Cloud offers enterprise-level Vertex AI with custom safety policies:

1. Contact Google Cloud sales
2. Explain the educational use case
3. Request custom safety policy configuration

**Pros:**
- Official solution
- Keeps Vertex AI benefits

**Cons:**
- Requires sales process
- May require enterprise contract
- Unknown timeline

## Recommendation

For CyberGuard Academy MVP, I recommend **Option 2 (Hybrid Approach)**:

1. Create a library of 20-30 curated phishing email templates
2. Categorize by:
   - Difficulty (1-5)
   - User role (executive, finance, IT, general)
   - Social engineering pattern (urgency, authority, curiosity, fear)
3. Use Gemini for:
   - Natural narrative flow
   - Personalized hints when users struggle
   - Detailed debriefs explaining red flags
   - Adaptive difficulty adjustments

This approach:
- Avoids all safety filter issues
- Provides better quality control
- Is actually faster and cheaper
- Still feels dynamic and adaptive

## Implementation Path

1. **Phase 1 (Immediate):** Basic template system
   - Create `data/phishing_templates.json`
   - Implement template selection logic
   - Use Gemini only for narration/hints/debriefs

2. **Phase 2 (After MVP):** Enhanced templates
   - Add more variety and personalization variables
   - Implement template mixing/variation
   - A/B test effectiveness

3. **Phase 3 (Future):** Explore alternatives
   - Evaluate Claude/GPT-4 for specific scenarios
   - Consider self-hosted models for full control
   - Reassess Vertex AI enterprise options

## Testing the Current Setup

Despite the phishing generation blocks, the migration to Vertex AI is **successful** for:
- ✅ General conversation
- ✅ Scenario narration
- ✅ Educational explanations
- ✅ Debrief generation
- ✅ Hint provision
- ✅ Security concept teaching

The core Game Master functionality will work fine with the hybrid approach.

## Next Steps

1. Accept that generated phishing content has limitations
2. Build the template library (I can help with this)
3. Adjust architecture to use hybrid approach
4. Test end-to-end scenario with templates + AI narration

Would you like me to help create the initial template library structure?
