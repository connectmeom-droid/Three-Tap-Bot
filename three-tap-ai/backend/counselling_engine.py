import re
from csv_engine import cutoff_df





def extract_rank(q):
    q = q.lower()

    # handle lakh
    lakh_match = re.search(r"(\d+)\s*lakh", q)
    if lakh_match:
        return int(lakh_match.group(1)) * 100000

    # normal numbers
    nums = re.findall(r"\d{1,7}", q)
    for n in nums:
        n = int(n)

        # ignore years
        if 2020 <= n <= 2030:
            continue

        if n > 0:
            return n
    return None


def extract_percentile(q):
    match = re.search(r"(\d{1,2}(\.\d+)?)\s*%|percentile", q)
    if match:
        return float(match.group(1))
    return None


def percentile_to_rank(percentile):
    # rough JEE approximation
    return int((100 - percentile) * 10000)


def extract_branch(q):
    q = q.lower()
    if "cse" in q or "computer" in q or "cs" in q:
        return "computer"
    if "ece" in q or "electronics" in q:
        return "electronics"
    if "electrical" in q:
        return "electrical"
    if "mechanical" in q or "mech" in q:
        return "mechanical"
    if "civil" in q:
        return "civil"
    return None


def extract_category(q):
    q = q.lower()
    if "obc" in q:
        return "OBC"
    if "ews" in q:
        return "EWS"
    if "sc" in q:
        return "SC"
    if "st" in q:
        return "ST"
    return "OPEN"


def extract_gender(q):
    q = q.lower()
    if "female" in q or "girl" in q:
        return "Female"
    return "Gender-Neutral"


def extract_institute_type(q):
    q = q.lower()
    if "iiit" in q:
        return "iiit"
    if "nit" in q:
        return "nit"
    if "iit" in q:
        return "iit"
    return None


def institute_priority(name):
    name = name.lower()
    if "indian institute of technology" in name:
        return 1
    if "national institute of technology" in name:
        return 2
    if "information technology" in name:
        return 3
    return 4


def rank_counselling(query, rank_override=None):
    rank = rank_override if rank_override else extract_rank(query)

    if not rank:
        return None, "Please tell me your rank."

    branch = extract_branch(query)
    category = extract_category(query)
    gender = extract_gender(query)
    inst_type = extract_institute_type(query)

    df = cutoff_df.copy()

    # clean rank column
    # clean rank column safely
    df["CloseRank"] = df["CloseRank"].astype(str)

# remove non-numeric characters
    df["CloseRank"] = df["CloseRank"].str.replace(r"\D", "", regex=True)

# remove empty or invalid rows
    df = df[df["CloseRank"].str.isnumeric()]

# convert to integer
    df["CloseRank"] = df["CloseRank"].astype(int)

    # branch filter
    if branch:
        df = df[df["Branch"].str.lower().str.contains(branch, na=False)]

    # category filter
    if category:
        df = df[df["Category"].str.contains(category, na=False)]

    # gender filter
    if gender == "Female":
        df = df[df["Gender"].str.contains("Female", na=False)]
    else:
        df = df[df["Gender"].str.contains("Gender-Neutral", na=False)]

    # institute type filter
    if inst_type == "iit":
        df = df[df["Institute"].str.contains("Indian Institute of Technology", na=False)]
    elif inst_type == "nit":
        df = df[df["Institute"].str.contains("National Institute of Technology", na=False)]
    elif inst_type == "iiit":
        df = df[df["Institute"].str.contains("Information Technology", na=False)]

    # rank filter
    df = df[df["CloseRank"] >= rank]

    if df.empty:
        if inst_type:
            return None, f"No {inst_type.upper()} available for this rank."
        return None, "No colleges found for your rank."

    df = df.drop_duplicates(subset=["Institute", "Branch", "Category", "Gender"])
    df = df.sort_values("CloseRank")

    return df.head(10), None
