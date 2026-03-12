"""Semantic category classifier with LLM support and embedding-based fallback.
Uses zero-shot semantic similarity when LLM is unavailable.
"""

from typing import List, Dict, Optional
import numpy as np
from google import genai
from google.genai import types

import config
from ground_truth import ALL_CATEGORIES


_client: Optional[genai.Client] = None
_semantic_classifier: Optional["SemanticCategoryClassifier"] = None


CATEGORY_DESCRIPTIONS = {
    "Review Comments": "reviewer comments lost not saving disappearing comment box issues text lost during review",
    "Review Recommendation": "recommendation dropdown resets not persisting not visible to editor score rating",
    "File handling": "file upload fails format rejected attachment error document upload pdf image supplementary",
    "Draft management": "autosave not working draft deleted unsaved changes lost cover letter revision uploaded new submission",
    "Email service": "email not delivered notification not sent wrong recipient invitation reminder decision notification",
    "Session management": "session expired logged out keep-alive not working timeout during form upload long form",
    "Data integrity": "data not persisting incorrect value saved field resets after save confidential comments lost",
    "Performance": "slow loading timeout high latency takes too long unresponsive times out seconds spinner",
    "Access control": "permission denied 403 forbidden unauthorized role change breaks access loses access guest reviewer",
    "Status tracking": "status not updated stuck on wrong state workflow not advancing with editor withdrawn active queue",
    "Validation": "invalid format accepted required field not enforced word count limit not checked orcid identifier",
    "UI Preferences": "dark mode resets preference not saved display setting lost theme toggle login",
    "Static content": "wrong text displayed typo incorrect label outdated information impact factor homepage",
}


class SemanticCategoryClassifier:
    """Zero-shot semantic classifier using sentence embeddings.
    Used as fallback when LLM is unavailable, or as primary when LLM is disabled.
    """

    def __init__(self, model=None, categories: List[str] = None):
        self.model = model
        self.categories = categories or config.CATEGORY_LIST

        texts = [CATEGORY_DESCRIPTIONS.get(c, c) for c in self.categories]
        self._category_embeddings: Optional[np.ndarray] = None
        self._category_texts = texts

    def _ensure_embeddings(self):
        if self._category_embeddings is None:
            self._category_embeddings = self.model.encode(
                self._category_texts, show_progress_bar=False
            )

    def classify(self, ticket: Dict) -> str:
        self._ensure_embeddings()

        text = f"{ticket.get('title', '')}. {ticket.get('description', '')}"
        embedding = self.model.encode([text], show_progress_bar=False)[0]

        t_norm = embedding / np.linalg.norm(embedding)
        c_norms = self._category_embeddings / np.linalg.norm(
            self._category_embeddings, axis=1, keepdims=True
        )
        similarities = np.dot(c_norms, t_norm)

        return self.categories[np.argmax(similarities)]

    def classify_batch(self, tickets: List[Dict]) -> List[str]:
        self._ensure_embeddings()

        texts = [f"{t.get('title', '')}. {t.get('description', '')}" for t in tickets]
        embeddings = self.model.encode(texts, show_progress_bar=False)

        t_norms = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        c_norms = self._category_embeddings / np.linalg.norm(
            self._category_embeddings, axis=1, keepdims=True
        )
        similarities = np.dot(t_norms, c_norms.T)

        best_indices = np.argmax(similarities, axis=1)
        return [self.categories[i] for i in best_indices]


def _get_client() -> Optional[genai.Client]:
    global _client
    if _client is None:
        if not config.GEMINI_API_KEY:
            return None
        try:
            _client = genai.Client(api_key=config.GEMINI_API_KEY)
        except Exception:
            return None
    return _client


def get_semantic_classifier(model=None) -> SemanticCategoryClassifier:
    global _semantic_classifier
    if _semantic_classifier is None:
        _semantic_classifier = SemanticCategoryClassifier(model=model)
    elif model is not None and _semantic_classifier.model is None:
        _semantic_classifier.model = model
    return _semantic_classifier


def _build_prompt(ticket: Dict) -> str:
    categories_str = "\n".join(f"- {cat}" for cat in ALL_CATEGORIES)

    title = ticket.get("title", "")
    description = ticket.get("description", "")

    return f"""Classify this support ticket into exactly ONE of the following categories.

Categories:
{categories_str}

Ticket Title: {title}
Ticket Description: {description}

Instructions:
1. Read the ticket title and description carefully
2. Choose the single most appropriate category from the list above
3. Respond with ONLY the category name, nothing else

Category:"""


def classify_ticket(ticket: Dict, model=None) -> str:
    """Classify a single ticket using LLM with semantic fallback.

    Args:
        ticket: Dict with 'title' and 'description' keys
        model: Optional SentenceTransformer model to reuse

    Returns:
        Category string from ALL_CATEGORIES
    """
    if not config.CLASSIFIER_ENABLED:
        return get_semantic_classifier(model).classify(ticket)

    client = _get_client()

    if client is None:
        return get_semantic_classifier(model).classify(ticket)

    prompt = _build_prompt(ticket)

    try:
        response = client.models.generate_content(
            model=config.LLM_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
                max_output_tokens=50,
            ),
        )

        category = response.text.strip()

        if category in ALL_CATEGORIES:
            return category

        for valid_cat in ALL_CATEGORIES:
            if valid_cat.lower() in category.lower():
                return valid_cat

        return get_semantic_classifier(model).classify(ticket)

    except Exception as e:
        print(f"Classification error for ticket {ticket.get('id', 'unknown')}: {e}")
        return get_semantic_classifier(model).classify(ticket)


def classify_tickets_batch(
    tickets: List[Dict], model=None, show_progress: bool = True
) -> Dict[str, str]:
    """Classify multiple tickets.

    Args:
        tickets: List of ticket dicts with 'id', 'title', 'description'
        model: Optional SentenceTransformer model to reuse
        show_progress: Print progress during classification

    Returns:
        Dict mapping ticket_id -> category
    """
    if not config.CLASSIFIER_ENABLED:
        classifier = get_semantic_classifier(model)
        categories = classifier.classify_batch(tickets)
        return {
            t.get("id", f"unknown_{i}"): c
            for i, (t, c) in enumerate(zip(tickets, categories))
        }

    results = {}
    total = len(tickets)

    for i, ticket in enumerate(tickets):
        ticket_id = ticket.get("id", f"unknown_{i}")
        category = classify_ticket(ticket, model)
        results[ticket_id] = category

        if show_progress and (i + 1) % 5 == 0:
            print(f"Classified {i + 1}/{total} tickets...")

    if show_progress:
        print(f"Classification complete: {total} tickets processed")

    return results


def enrich_tickets_with_categories(
    tickets: List[Dict], model=None, show_progress: bool = True
) -> List[Dict]:
    """Add 'category' field to each ticket based on classification.

    Args:
        tickets: List of ticket dicts
        model: Optional SentenceTransformer model to reuse
        show_progress: Print progress during classification

    Returns:
        New list of tickets with 'category' field added
    """
    categories_map = classify_tickets_batch(tickets, model, show_progress)

    enriched = []
    for ticket in tickets:
        ticket_copy = ticket.copy()
        ticket_copy["category"] = categories_map.get(ticket.get("id", ""), "unknown")
        enriched.append(ticket_copy)

    return enriched
