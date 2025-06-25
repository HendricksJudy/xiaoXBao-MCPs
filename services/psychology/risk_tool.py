"""Risk assessment stub for PHQ-9 and GAD-7."""


async def phq_gad_classifier(phq9: int | None, gad7: int | None) -> str:
    """Classify risk level based on PHQ-9 and GAD-7 scores."""
    # TODO integrate real model
    score = (phq9 or 0) + (gad7 or 0)
    if score > 20:
        return "high"
    if score > 10:
        return "moderate"
    return "low"
