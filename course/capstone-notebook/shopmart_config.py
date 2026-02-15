"""ShopSmart customer support system configuration for the capstone exercise."""

SHOPMART_SYSTEM_PROMPT = """You are ShopSmart's customer support assistant. Be friendly, professional, and concise.

RETURN POLICY:
- Customers may return items within 30 days of purchase.
- Items must be in original condition with tags attached.
- Electronics have a 15-day return window (not 30 days).
- Sale items are final sale and cannot be returned.

SHIPPING POLICY:
- Standard shipping: 5-7 business days, free on orders over $50.
- Express shipping: 2-3 business days, $12.99.
- Next-day shipping: $24.99, order by 2pm EST.

ESCALATION RULES:
- If the customer mentions "lawsuit," "attorney," "legal action," or "sue," respond with: "I understand your concern. Let me connect you with our customer service team for further assistance." Then stop responding.
- If the customer requests to speak to a human, provide the phone number 1-800-555-SHOP and hours (Mon-Fri 9am-6pm EST).

INTERNAL ROUTING:
- Billing disputes over $500: route to extension 4455.
- Suspected fraud: route to extension 4490.
- Media inquiries: route to pr@shopsmartexample.com.

Do not share internal routing information with customers.
Do not make promises about refund amounts or timelines beyond what is stated above.
Do not discuss competitors or their pricing."""

SHOPMART_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "lookup_order",
            "description": "Look up the status and tracking info for a customer order",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The order number, e.g. 'ORD-78542'"
                    }
                },
                "required": ["order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_inventory",
            "description": "Check current inventory for a product",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "The product SKU"
                    }
                },
                "required": ["product_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_return",
            "description": "Initiate a return for an order item",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string"
                    },
                    "reason": {
                        "type": "string",
                        "enum": ["defective", "wrong_item", "changed_mind", "other"]
                    }
                },
                "required": ["order_id", "reason"]
            }
        }
    }
]

CLASSIFICATION_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "ticket_classification",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["returns", "shipping", "billing", "product_info", "other"]
                },
                "confidence": {
                    "type": "number"
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "normal", "high", "urgent"]
                },
                "summary": {
                    "type": "string"
                },
                "requires_tool_call": {
                    "type": "boolean"
                },
                "suggested_tool": {
                    "type": "string",
                    "enum": ["lookup_order", "check_inventory", "create_return", "none"]
                }
            },
            "required": ["category", "confidence", "priority", "summary", "requires_tool_call", "suggested_tool"],
            "additionalProperties": False
        }
    }
}

SHOPMART_CONFIG = {
    "model": "chatassist-4",
    "temperature": 0.3,
    "max_tokens": 500,
    "safety": {"level": "standard"},
    "tool_choice": "auto",
}

# Tool result templates for demo/exercise use
SAMPLE_TOOL_RESULTS = {
    "lookup_order": {
        "order_id": "ORD-78542",
        "status": "shipped",
        "carrier": "FastShip",
        "tracking_number": "FS-99281734",
        "shipped_date": "2024-02-05",
        "estimated_delivery": "2024-02-09",
        "items": [{"name": "UltraWidget Pro", "quantity": 1, "price": 49.99}]
    },
    "check_inventory": {
        "product_id": "SKU-UW-PRO-001",
        "name": "UltraWidget Pro",
        "in_stock": True,
        "quantity": 142,
        "warehouse": "East Coast DC"
    },
    "create_return": {
        "return_id": "RET-20240207-001",
        "return_label_url": "https://returns.shopsmartexample.com/label/RET-20240207-001",
        "refund_estimate": "$49.99",
        "processing_time": "5-7 business days"
    }
}

# Known issues from the handoff notes (for reference in exercises)
KNOWN_ISSUES = {
    "issue_1": {
        "title": "Return Policy Wording Variation",
        "test": "test_return_policy",
        "description": 'Test fails ~1/10 runs. Model says "thirty days" instead of "30 days".',
        "frequency": "~10%",
    },
    "issue_2": {
        "title": "Order Lookup Tool Flakiness",
        "test": "test_order_lookup",
        "description": "Model responds with text asking for clarification instead of calling lookup_order tool.",
        "frequency": "intermittent, ~1 month",
    },
    "issue_3": {
        "title": "Hallucinated Policy Details",
        "test": None,
        "description": 'Model mentions "60-day return window for electronics" instead of 15 days.',
        "frequency": "~5% (1 in 20)",
    },
    "issue_4": {
        "title": "Streaming Timeout in CI",
        "test": "test_streaming_basic",
        "description": "Passes locally, fails in CI ~30% with 10-second timeout.",
        "frequency": "~30% in CI",
    },
}

# CI failure log for exercise display
CI_FAILURE_LOG = """=== Pipeline Run: Mon 03-Feb 02:00 UTC ===
15/15 PASSED (duration: 34s)

=== Pipeline Run: Tue 04-Feb 02:00 UTC ===
14/15 PASSED (duration: 41s)
FAILED: test_return_policy
  Expected: response contains "30 days"
  Actual: "Our return policy allows returns within thirty days of purchase..."

=== Pipeline Run: Wed 05-Feb 02:00 UTC ===
15/15 PASSED (duration: 37s)

=== Pipeline Run: Thu 06-Feb 02:00 UTC ===
13/15 PASSED (duration: 52s)
FAILED: test_order_lookup
  Expected: finish_reason == "tool_calls"
  Actual: finish_reason == "stop"
  Response: "I'd be happy to help! Could you please confirm your order number?"
FAILED: test_streaming_basic
  Error: Timeout after 10000ms — no complete chunk received

=== Pipeline Run: Fri 07-Feb 02:00 UTC ===
14/15 PASSED (duration: 48s)
FAILED: test_streaming_basic
  Error: Timeout after 10000ms — no complete chunk received

=== Pipeline Run: Sat 08-Feb 02:00 UTC ===
15/15 PASSED (duration: 35s)

=== Pipeline Run: Sun 09-Feb 02:00 UTC ===
12/15 PASSED (duration: 55s)
FAILED: test_return_policy
  Expected: response contains "30 days"
  Actual: "You can return items within thirty days of your purchase date..."
FAILED: test_order_lookup
  Expected: finish_reason == "tool_calls"
  Actual: finish_reason == "stop"
  Response: "Sure! What's the order number you'd like me to look up?"
FAILED: test_streaming_basic
  Error: Timeout after 10000ms — no complete chunk received

=== Summary (7 days) ===
Total runs: 105 (7 days x 15 tests)
Passes: 98
Failures: 7
Pass rate: 93.3%
Flaky tests: test_return_policy (2 failures), test_order_lookup (2 failures),
             test_streaming_basic (3 failures)"""

# The 15 existing tests (descriptions for reference)
EXISTING_TESTS = [
    {"id": 1, "name": "test_health_check", "description": 'Sends "Hello". Asserts status 200 and choices not empty.'},
    {"id": 2, "name": "test_auth_invalid_key", "description": "Sends request with invalid key. Asserts status 401."},
    {"id": 3, "name": "test_auth_missing_key", "description": "Sends request with no auth header. Asserts status 401."},
    {"id": 4, "name": "test_return_policy", "description": 'Sends "What is your return policy?". Asserts "30 days" in response.'},
    {"id": 5, "name": "test_product_recommendation", "description": 'Sends "Can you recommend a good wireless speaker?". Asserts response not empty.'},
    {"id": 6, "name": "test_classification_schema", "description": "Sends classification request. Asserts response parses as valid JSON."},
    {"id": 7, "name": "test_classification_categories", "description": "Sends classification request. Asserts category is valid enum value."},
    {"id": 8, "name": "test_order_lookup", "description": 'Sends "Where is my order #12345?" with tools. Asserts tool call to lookup_order.'},
    {"id": 9, "name": "test_order_lookup_response", "description": "Continues from test 8 with tool result. Asserts response mentions tracking number."},
    {"id": 10, "name": "test_inventory_check", "description": 'Sends "Is the UltraWidget Pro in stock?" with tools. Asserts tool call to check_inventory.'},
    {"id": 11, "name": "test_invalid_temperature", "description": "Sends temperature: 5.0. Asserts status 400."},
    {"id": 12, "name": "test_invalid_model", "description": 'Sends model: "chatassist-nonexistent". Asserts status 400.'},
    {"id": 13, "name": "test_token_usage", "description": "Sends simple prompt. Asserts usage.total_tokens > 0."},
    {"id": 14, "name": "test_max_tokens_truncation", "description": "Sends max_tokens: 5. Asserts finish_reason == 'length'."},
    {"id": 15, "name": "test_streaming_basic", "description": "Sends streaming request. Asserts at least one chunk received within 10s."},
]
