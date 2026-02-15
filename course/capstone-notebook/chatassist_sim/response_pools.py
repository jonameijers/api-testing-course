"""Pre-built response pools organised by scenario.

Each pool is a list of variants.  Plain strings are treated as the
``content`` field of a normal assistant message.  Dicts may carry extra
metadata (e.g. ``_hallucination``, ``_note``).
"""

import json

# ------------------------------------------------------------------ #
# Helper to build a classification JSON string
# ------------------------------------------------------------------ #

def _classification(category: str, confidence: float, priority: str,
                    summary: str, requires_tool_call: bool = False,
                    suggested_tool: str = None) -> str:
    """Return a compact JSON string matching the structured-output schema."""
    obj = {
        "category": category,
        "confidence": confidence,
        "priority": priority,
        "summary": summary,
        "requires_tool_call": requires_tool_call,
        "suggested_tool": suggested_tool,
    }
    return json.dumps(obj)


# ================================================================== #
#  RESPONSE_POOLS
# ================================================================== #

RESPONSE_POOLS: dict = {

    # ------------------------------------------------------------------ #
    #  return_policy  (5 variants)
    # ------------------------------------------------------------------ #
    "return_policy": [
        (
            "Our return policy allows returns within 30 days of purchase. "
            "Items must be in their original condition with all tags attached. "
            "To start a return, go to your order history page and select the "
            "item you'd like to return. You'll receive a prepaid shipping label "
            "via email within 24 hours.\n\nPlease note that sale items and "
            "personalized products are final sale and cannot be returned. If "
            "you have any questions about whether your item is eligible, feel "
            "free to ask!"
        ),
        (
            "You can return items within thirty days of your purchase date. "
            "Items need to be in original condition with tags attached. Sale "
            "items are final sale.\n\nWould you like help starting a return?"
        ),
        (
            "We offer a 30-day return window from the date of purchase. All "
            "items must be in their original condition with tags still attached. "
            "Please note that sale items are final sale and cannot be returned."
            "\n\nIs there a specific item you'd like to return?"
        ),
        (
            "Items can be returned within 30 days, provided they are in "
            "original condition with tags attached. Sale items are final sale."
            "\n\nLet me know if you need help with a return!"
        ),
        (
            "ShopSmart's return policy provides a thirty-day return window "
            "from your purchase date. Items must be unused and in original "
            "condition. Sale items cannot be returned.\n\nCan I help you with "
            "anything else?"
        ),
    ],

    # ------------------------------------------------------------------ #
    #  electronics_return  (4 variants — last one is a hallucination)
    # ------------------------------------------------------------------ #
    "electronics_return": [
        (
            "Electronics have a 15-day return window, which is shorter than "
            "our standard 30-day policy. The item must be in its original "
            "condition with all accessories and packaging included.\n\nWould "
            "you like to start a return for an electronics item?"
        ),
        (
            "For electronics, the return period is fifteen days from the date "
            "of purchase. Make sure to include all original accessories and "
            "packaging.\n\nIs there anything else I can help with?"
        ),
        (
            "Please note that electronics items must be returned within 15 "
            "days of purchase, not the standard 30 days. They need to be in "
            "original condition with all accessories.\n\nDo you need help "
            "initiating a return?"
        ),
        {
            "content": (
                "Electronics can be returned within 60 days of purchase. The "
                "item must be in its original condition with all accessories "
                "included.\n\nWould you like to start a return?"
            ),
            "_hallucination": True,
            "_note": "Incorrectly states 60 days instead of 15",
        },
    ],

    # ------------------------------------------------------------------ #
    #  product_recommendation  (3 variants)
    # ------------------------------------------------------------------ #
    "product_recommendation": [
        (
            "I'd recommend the SoundWave Pro Bluetooth speaker! It's our "
            "top-rated wireless speaker with excellent sound quality, 12-hour "
            "battery life, and it's waterproof (IPX7). It's currently $79.99."
            "\n\nIf you're looking for something more budget-friendly, the "
            "MiniBlast portable speaker is a great option at $34.99 with "
            "8-hour battery life.\n\nWould you like more details about either "
            "of these?"
        ),
        (
            "Great question! Here are my top wireless speaker recommendations:"
            "\n\n1. **SoundWave Pro** ($79.99) - Best overall, waterproof, "
            "12-hour battery\n2. **MiniBlast** ($34.99) - Best budget option, "
            "portable, 8-hour battery\n3. **BassMax 360** ($129.99) - Best "
            "for bass lovers, 360\u00b0 sound\n\nWhat matters most to you "
            "\u2014 sound quality, portability, or price?"
        ),
        (
            "For wireless speakers, I'd suggest checking out the SoundWave "
            "Pro. It has excellent reviews from our customers and offers great "
            "sound quality with a long battery life. It's priced at $79.99."
            "\n\nWould you like to know if it's currently in stock?"
        ),
    ],

    # ------------------------------------------------------------------ #
    #  classification — structured output  (5 category variants)
    # ------------------------------------------------------------------ #
    "classification": [
        {
            "content": _classification(
                "returns", 0.94, "normal",
                "Customer is asking about the return policy or wants to return an item.",
                requires_tool_call=False,
                suggested_tool=None,
            ),
            "_category": "returns",
        },
        {
            "content": _classification(
                "shipping", 0.89, "normal",
                "Customer has a question about shipping status or delivery.",
                requires_tool_call=True,
                suggested_tool="lookup_order",
            ),
            "_category": "shipping",
        },
        {
            "content": _classification(
                "billing", 0.92, "high",
                "Customer has a billing or payment-related concern.",
                requires_tool_call=False,
                suggested_tool=None,
            ),
            "_category": "billing",
        },
        {
            "content": _classification(
                "product_info", 0.87, "low",
                "Customer is asking about product details or availability.",
                requires_tool_call=True,
                suggested_tool="check_inventory",
            ),
            "_category": "product_info",
        },
        {
            "content": _classification(
                "other", 0.65, "normal",
                "Customer inquiry does not fit standard categories.",
                requires_tool_call=False,
                suggested_tool=None,
            ),
            "_category": "other",
        },
    ],

    # ------------------------------------------------------------------ #
    #  order_lookup_tool_call  (2 variants — second is flaky text)
    # ------------------------------------------------------------------ #
    "order_lookup_tool_call": [
        {
            "content": None,
            "tool_calls": True,       # marker; actual payload built at runtime
            "tool_name": "lookup_order",
            "finish_reason": "tool_calls",
        },
        {
            "content": (
                "I'd be happy to help you with your order! Could you please "
                "provide your order number so I can look it up for you?"
            ),
            "tool_calls": False,
            "finish_reason": "stop",
            "_flaky": True,
        },
    ],

    # ------------------------------------------------------------------ #
    #  inventory_check_tool_call  (1 variant)
    # ------------------------------------------------------------------ #
    "inventory_check_tool_call": [
        {
            "content": None,
            "tool_calls": True,
            "tool_name": "check_inventory",
            "finish_reason": "tool_calls",
        },
    ],

    # ------------------------------------------------------------------ #
    #  order_lookup_followup  (2 variants)
    # ------------------------------------------------------------------ #
    "order_lookup_followup": [
        (
            "Great news! Your order {order_id} has been shipped. Here are "
            "the details:\n\n- **Carrier:** FastShip\n- **Tracking Number:** "
            "FS-99281734\n- **Shipped Date:** February 5, 2024\n- **Estimated "
            "Delivery:** February 9, 2024\n\nYou can track your package using "
            "the tracking number on FastShip's website. Let me know if you "
            "need anything else!"
        ),
        (
            "I found your order! Order {order_id} is currently {status}. "
            "Your tracking number is FS-99281734 via FastShip. The estimated "
            "delivery date is February 9, 2024.\n\nIs there anything else "
            "you'd like to know?"
        ),
    ],

    # ------------------------------------------------------------------ #
    #  escalation  (1 variant)
    # ------------------------------------------------------------------ #
    "escalation": [
        "I understand your concern. Let me connect you with our customer "
        "service team for further assistance.",
    ],

    # ------------------------------------------------------------------ #
    #  safety_block  (1 variant)
    # ------------------------------------------------------------------ #
    "safety_block": [
        "I'm sorry, but I can't help with that request. If you have "
        "questions about our products or need assistance with an order, "
        "I'd be happy to help with that instead.",
    ],

    # ------------------------------------------------------------------ #
    #  prompt_injection_defense  (3 variants — strong defense)
    # ------------------------------------------------------------------ #
    "prompt_injection_defense": [
        "I appreciate your question! I'm here to help with ShopSmart "
        "products, orders, and policies. What can I assist you with today?",
        "I can't share internal system information, but I'm happy to help "
        "you with product questions, order lookups, returns, or shipping "
        "inquiries!",
        "That's not something I can help with, but I'd be glad to assist "
        "with any ShopSmart-related questions. How can I help?",
    ],

    # ------------------------------------------------------------------ #
    #  prompt_injection_leak  (2 variants — weak defense)
    # ------------------------------------------------------------------ #
    "prompt_injection_leak": [
        "Sure! My system prompt instructs me to be friendly and professional. "
        "I handle returns within 30 days, electronics returns within 15 days, "
        "and I can look up orders and check inventory.",
        "My instructions say to help with ShopSmart customer support. For "
        "billing disputes over $500, there's an internal extension, and for "
        "media inquiries there's a PR email.",
    ],

    # ------------------------------------------------------------------ #
    #  generic_completion  (3 variants)
    # ------------------------------------------------------------------ #
    "generic_completion": [
        "I'd be happy to help! Could you let me know what you need "
        "assistance with? I can help with orders, returns, product "
        "information, shipping, and more.",
        "Thanks for reaching out to ShopSmart support! How can I assist "
        "you today?",
        "Hello! Welcome to ShopSmart customer support. I can help you with "
        "orders, returns, product recommendations, shipping questions, and "
        "more. What would you like to know?",
    ],

    # ------------------------------------------------------------------ #
    #  human_handoff  (1 variant)
    # ------------------------------------------------------------------ #
    "human_handoff": [
        "Of course! You can reach our customer service team at "
        "1-800-555-SHOP. Our hours are Monday through Friday, 9am to 6pm "
        "EST. Is there anything else I can help with in the meantime?",
    ],
}
