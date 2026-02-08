import re

# realistic percentile → rank mapping
# based on real JEE Main 2023–2024 trends
def percentile_to_rank(percentile):
    # Approx JEE Main mapping
    if percentile >= 99.9:
        return 100
    if percentile >= 99:
        return 1000
    if percentile >= 98:
        return 5000
    if percentile >= 95:
        return 20000
    if percentile >= 92:
        return 80000
    if percentile >= 90:
        return 100000
    if percentile >= 85:
        return 150000
    return 300000


def extract_percentile(query):
    nums = re.findall(r"\d{1,3}\.?\d*", query)
    for n in nums:
        val = float(n)
        if 50 <= val <= 100:
            return val
    return None
