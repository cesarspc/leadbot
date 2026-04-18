from leadbot.models import LeadClassification


HIGH_INTENT_KEYWORDS = {
    "buy",
    "price",
    "budget",
    "need",
    "order",
    "purchase",
    "delivery",
    "quote",
    "today",
    "urgent",
}


class LeadClassifier:
    def __init__(self, products: list[dict]) -> None:
        self.products = products

    def classify(self, analyzed_message: str) -> LeadClassification:
        words = set(analyzed_message.split())
        score = len(words.intersection(HIGH_INTENT_KEYWORDS))

        for product in self.products:
            name = str(product.get("name", "")).lower()
            category = str(product.get("category", "")).lower()
            if name and name in analyzed_message:
                score += 1
            if category and category in analyzed_message:
                score += 1

        quality = "high" if score >= 2 else "low"
        confidence = min(0.99, 0.45 + (score * 0.15))
        reason = (
            "Detected purchase intent, budget or product specificity"
            if quality == "high"
            else "No strong buying intent indicators"
        )
        return LeadClassification(quality=quality, confidence=round(confidence, 2), reason=reason)
