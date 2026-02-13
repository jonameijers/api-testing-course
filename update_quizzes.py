#!/usr/bin/env python3
"""
Update specific quiz questions on existing Google Forms to reflect reviewer feedback.

Affected forms:
- Session 1 (Q4, Q8): Scoped strict schema and cost claims to course context
- Session 3 (Q9): Replaced subjective stem with concrete streaming gap scenario
- Session 4 (Q3): Corrected 429 triage category to Infrastructure/transport

This script updates questions in-place so form URLs are preserved.
"""

import json
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/drive.file",
]

BASE_DIR = Path(__file__).parent
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"


def authenticate():
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())
    return creds


def get_item_id(forms_service, form_id, question_index):
    """Get the item ID for a question at the given index (0-based)."""
    form = forms_service.forms().get(formId=form_id).execute()
    items = form.get("items", [])
    if question_index >= len(items):
        raise ValueError(f"Question index {question_index} out of range (form has {len(items)} items)")
    return items[question_index]["itemId"]


def build_update_request(item_id, index, question_text, options, correct_idx, feedback):
    """Build an updateItem request for a radio-button question."""
    return {
        "updateItem": {
            "item": {
                "itemId": item_id,
                "title": question_text,
                "questionItem": {
                    "question": {
                        "required": True,
                        "grading": {
                            "pointValue": 1,
                            "correctAnswers": {"answers": [{"value": options[correct_idx]}]},
                            "whenRight": {"text": feedback},
                            "whenWrong": {"text": feedback},
                        },
                        "choiceQuestion": {
                            "type": "RADIO",
                            "options": [{"value": opt} for opt in options],
                        },
                    }
                },
            },
            "location": {"index": index},
            "updateMask": "title,questionItem",
        }
    }


def build_tf_update_request(item_id, index, question_text, correct_bool, feedback):
    """Build an updateItem request for a true/false question."""
    options = ["True", "False"]
    correct_idx = 0 if correct_bool else 1
    return build_update_request(item_id, index, question_text, options, correct_idx, feedback)


# ---------------------------------------------------------------------------
# Define the 4 question updates
# ---------------------------------------------------------------------------

UPDATES = {
    "Session 1": {
        "form_id": "1j5u4WjsfwzvGCxpxdn0ss4bF9UKMkyFeaICelpWcJaE",
        "questions": [
            {
                "index": 3,  # Q4 (0-based)
                "type": "tf",
                "text": "In the ChatAssist API used in this course, structured output mode with strict: true is designed to enforce schema conformance.",
                "correct": True,
                "feedback": "For this course's ChatAssist spec, strict: true constrains responses to valid JSON matching your schema. This is the first line of defense for testability.",
            },
            {
                "index": 7,  # Q8 (0-based)
                "type": "tf",
                "text": "In this course's cost model, failed API requests can still consume input tokens and incur cost.",
                "correct": True,
                "feedback": "Prompt processing can still consume tokens even when a request fails. This is a common hidden cost in GenAI API testing.",
            },
        ],
    },
    "Session 3": {
        "form_id": "1On8kLKjz6qoT40vWi9Wguwgj6s-e8rUkv0MMoULC8NQ",
        "questions": [
            {
                "index": 8,  # Q9 (0-based)
                "type": "mc",
                "text": "A team has tests for completion and structured output, but no tests for streaming chunks, mid-stream errors, or chunk assembly. Which coverage gap is this?",
                "options": [
                    "Basic authentication testing",
                    "Streaming mode and partial failure handling",
                    "Testing that the API returns JSON",
                    "Checking HTTP status codes",
                ],
                "correct": 1,
                "feedback": "This is a response-mode coverage gap: streaming behavior (including partial and error scenarios) is untested.",
            },
        ],
    },
    "Session 4": {
        "form_id": "1_v4tW83wULEsyiOy6h_u0KByR_JY5VyFYiQGY_qyB_s",
        "questions": [
            {
                "index": 2,  # Q3 (0-based)
                "type": "mc",
                "text": "In this course's triage model, a 429 'Too Many Requests' error is first classified under which broad failure category?",
                "options": [
                    "Infrastructure/transport",
                    "Capacity/quota",
                    "Contract/schema break",
                    "Model drift",
                ],
                "correct": 0,
                "feedback": "In the triage model, 429 is an infrastructure/transport-path error first; then you narrow root cause to capacity/quota (rate or token limits).",
            },
        ],
    },
}


def main():
    print("Authenticating with Google...")
    creds = authenticate()
    forms_service = build("forms", "v1", credentials=creds)

    for session_name, data in UPDATES.items():
        form_id = data["form_id"]
        print(f"\nUpdating {session_name} (form: {form_id})...")

        requests = []
        for q in data["questions"]:
            item_id = get_item_id(forms_service, form_id, q["index"])
            print(f"  Q{q['index'] + 1} (item {item_id}): {q['text'][:60]}...")

            if q["type"] == "tf":
                req = build_tf_update_request(
                    item_id, q["index"], q["text"], q["correct"], q["feedback"]
                )
            else:
                req = build_update_request(
                    item_id, q["index"], q["text"], q["options"], q["correct"], q["feedback"]
                )
            requests.append(req)

        forms_service.forms().batchUpdate(
            formId=form_id,
            body={"requests": requests},
        ).execute()
        print(f"  {session_name} updated successfully ({len(requests)} question(s))")

    print("\n" + "=" * 70)
    print("ALL UPDATES APPLIED SUCCESSFULLY")
    print("=" * 70)
    print("\nForm URLs are unchanged. Updated questions:")
    print("  - Session 1 Q4: Scoped strict schema claim to course context")
    print("  - Session 1 Q8: Scoped cost behavior to course's cost model")
    print("  - Session 3 Q9: Concrete streaming gap scenario (replaces subjective stem)")
    print("  - Session 4 Q3: 429 → Infrastructure/transport (corrected category + answer)")


if __name__ == "__main__":
    main()
