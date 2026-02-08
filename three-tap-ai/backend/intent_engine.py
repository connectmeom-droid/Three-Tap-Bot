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
    if "cutoff" in q or "closing rank" in q or "opening rank" in q:
        return "cutoff"

    # percentile intent
    if "percentile" in q:
        return "rank"

    # rank present → counselling
    rank = extract_rank(q)
    if rank is not None:
        return "rank"

    # common counselling phrases
    if any(x in q for x in [
        "which college",
        "which iit",
        "which nit",
        "which iiit",
        "can i get",
        "best college",
        "college can i get"
    ]):
        return "rank"

    return "general"
