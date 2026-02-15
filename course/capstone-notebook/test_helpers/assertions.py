"""Custom assertion helpers for GenAI API testing exercises."""

from difflib import SequenceMatcher


def assert_contains_any(text, candidates, msg=None):
    """Assert that text contains at least one of the candidate strings.

    Usage:
        assert_contains_any(response_text, ["30 days", "thirty days"])
    """
    text_lower = text.lower()
    for candidate in candidates:
        if candidate.lower() in text_lower:
            return  # Pass

    if msg is None:
        msg = f"Expected text to contain one of {candidates}, but none found in: {text[:200]}..."
    raise AssertionError(msg)


def assert_not_contains_any(text, forbidden, msg=None):
    """Assert that text does NOT contain any of the forbidden strings.

    Usage:
        assert_not_contains_any(response_text, ["4455", "4490", "pr@shopsmartexample.com"])
    """
    text_lower = text.lower()
    for item in forbidden:
        if item.lower() in text_lower:
            if msg is None:
                msg = f"Found forbidden content '{item}' in response: {text[:200]}..."
            raise AssertionError(msg)


def assert_similarity(text, reference, threshold=0.6, msg=None):
    """Assert that text is similar to reference above a threshold.

    Uses difflib.SequenceMatcher as a lightweight similarity measure.
    This is a pedagogical stand-in for embedding-based cosine similarity.

    Usage:
        assert_similarity(response_text, expected_text, threshold=0.6)
    """
    ratio = SequenceMatcher(None, text.lower(), reference.lower()).ratio()
    if ratio < threshold:
        if msg is None:
            msg = f"Similarity {ratio:.2f} is below threshold {threshold:.2f}"
        raise AssertionError(msg)
    return ratio


def assert_json_valid(text, msg=None):
    """Assert that text is valid JSON and return the parsed object."""
    import json
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError) as e:
        if msg is None:
            msg = f"Invalid JSON: {e}\nContent: {text[:200]}..."
        raise AssertionError(msg)


def assert_json_has_fields(obj, fields, msg=None):
    """Assert that a dict has all required fields.

    Usage:
        data = assert_json_valid(response_content)
        assert_json_has_fields(data, ["category", "confidence", "priority"])
    """
    missing = [f for f in fields if f not in obj]
    if missing:
        if msg is None:
            msg = f"Missing required fields: {missing}. Present fields: {list(obj.keys())}"
        raise AssertionError(msg)
