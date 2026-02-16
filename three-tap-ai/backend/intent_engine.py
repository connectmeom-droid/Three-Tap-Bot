import re


def extract_rank(q):
    nums = re.findall(r"\d{1,7}", q)
    for n in nums:
        n = int(n)

        # ignore years like 2020–2030
        if 2020 <= n <= 2030:
            continue

        if n > 0:
            return n
    return None


def extract_percentile(q):
    match = re.search(r"(\d{1,3}\.?\d*)\s*percentile", q.lower())
    if match:
        return float(match.group(1))
    return None


def detect_intent(query):
    q = query.lower()

    # cutoff intent
    if any(x in q for x in [
        "cutoff",
        "closing rank",
        "opening rank"
    ]):
        return "cutoff"

    # rank / percentile intent
    if any(x in q for x in [
        "percentile",
        "rank",
        "air",
        "all india rank",
        "what can i get",
        "which college",
        "which nit",
        "which iiit",
        "which iit",
        "options",
        "can i get",
        "expected rank",
        "expected air",
        "strategy",
        "counselling"
    ]):
        return "rank"

    return "general"

