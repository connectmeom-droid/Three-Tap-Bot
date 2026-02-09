import re
from counselling_engine import rank_counselling

TOTAL_CANDIDATES = 1100000


def extract_percentile(query):
    nums = re.findall(r"\d{1,3}\.?\d*", query)
    for n in nums:
        val = float(n)
        if 50 <= val <= 100:
            return val
    return None


def percentile_to_rank(percentile):
    rank = int((100 - percentile) * TOTAL_CANDIDATES / 100)
    if rank < 1:
        rank = 1
    return rank


def percentile_counselling(query):
    percentile = extract_percentile(query)

    if not percentile:
        return None, "Please provide your percentile."

    rank = percentile_to_rank(percentile)

    df, msg = rank_counselling(query, rank_override=rank)

    if msg:
        return None, msg

    return df, f"Estimated rank for {percentile}%ile is around {rank}."
