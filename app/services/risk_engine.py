import re
from rapidfuzz import fuzz


def normalize_name(name: str) -> str:
    """
    Normalize a brand or suspicious name by:
    - converting to lowercase
    - removing spaces
    - removing special characters
    """

    return re.sub(
        r"[^a-z0-9]",
        "",
        name.lower()
    )


def calculate_name_similarity(
    brand_name: str,
    suspicious_name: str
) -> float:

    normal_brand = normalize_name(brand_name)
    normal_suspicious = normalize_name(suspicious_name)

    score = fuzz.ratio(
        normal_brand,
        normal_suspicious
    )

    return round(score, 2)


def calculate_risk_score(
    brand_name: str,
    suspicious_name: str,
    suspicious_url: str | None = None,
    official_url: str | None = None,
    source_type: str | None = None
):

    name_similarity = calculate_name_similarity(
        brand_name,
        suspicious_name
    )

    score = name_similarity * 0.50

    reasons = []

    # Highly similar name
    if name_similarity >= 90:
        score += 20
        reasons.append(
            "Highly similar brand name"
        )

    # Similar name
    elif name_similarity >= 70:
        score += 10
        reasons.append(
            "Similar brand name"
        )

    # Suspicious URL
    if suspicious_url and official_url:

        official_domain = (
            official_url.lower()
            .replace("https://", "")
            .replace("http://", "")
            .split("/")[0]
        )

        suspicious_domain = (
            suspicious_url.lower()
            .replace("https://", "")
            .replace("http://", "")
            .split("/")[0]
        )

        if official_domain != suspicious_domain:

            score += 20

            reasons.append(
                "Different or suspicious domain"
            )

    # Source risk
    if source_type == "social":

        score += 10

        reasons.append(
            "Suspicious social account"
        )

    elif source_type == "app":

        score += 15

        reasons.append(
            "Suspicious mobile application"
        )

    # Limit score
    score = min(
        round(score),
        100
    )

    # Severity
    if score >= 81:

        severity = "Critical"

    elif score >= 61:

        severity = "High"

    elif score >= 31:

        severity = "Medium"

    else:

        severity = "Low"

    return {
        "score": score,
        "severity": severity,
        "reasons": reasons,
        "name_similarity": name_similarity
    }