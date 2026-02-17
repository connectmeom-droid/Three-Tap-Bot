import re
from csv_engine import cutoff_df


# -------------------- BASIC EXTRACTORS --------------------

def extract_marks(q):
    q = q.lower()
    if any(x in q for x in ["marks", "score", "out of"]):
        nums = re.findall(r"\d{2,3}", q)
        if nums:
            return int(nums[0])
    return None


def extract_percentile(q):
    q = q.lower()
    match = re.search(r"(\d{1,3}(\.\d+)?)\s*(%|percentile)", q)
    if match:
        val = float(match.group(1))
        if 0 < val <= 100:
            return val
    return None


def extract_rank(q):
    q = q.lower()

    # lakh handling
    lakh_match = re.search(r"(\d+)\s*lakh", q)
    if lakh_match:
        return int(lakh_match.group(1)) * 100000

    # AIR handling
    air_match = re.search(r"(air|all india rank)\s*(\d{1,7})", q)
    if air_match:
        return int(air_match.group(2))

    # generic numbers
    nums = re.findall(r"\d{1,7}", q)
    for n in nums:
        n = int(n)
        if 2020 <= n <= 2030:
            continue
        if n > 0:
            return n

    return None


YEARLY_CANDIDATES = {
    2022: 905000,
    2023: 940000,
    2024: 1170000,
    2025: 1200000,  # update when official data comes
}

DEFAULT_YEAR = 2025


def extract_year(query):
    import re
    match = re.search(r"(20\d{2})", query)
    if match:
        return int(match.group(1))
    return DEFAULT_YEAR


def percentile_to_rank(percentile, year=DEFAULT_YEAR):
    total = YEARLY_CANDIDATES.get(year, YEARLY_CANDIDATES[DEFAULT_YEAR])
    rank = int((100 - percentile) * total / 100)
    return max(rank, 1)


# -------------------- QUERY FEATURES --------------------

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
    q = " " + q.lower() + " "

    if " iiit " in q:
        return "iiit"
    if " nit " in q:
        return "nit"
    if " iit " in q:
        return "iit"

    return None


# -------------------- INSTITUTE PRIORITY --------------------

def institute_priority(name):
    name = name.lower()

    if "bombay" in name or "delhi" in name or "madras" in name:
        return 1

    if "indian institute of technology" in name:
        return 2

    if "trichy" in name or "warangal" in name or "surathkal" in name:
        return 3

    if "national institute of technology" in name:
        return 4

    if "information technology" in name:
        return 5

    return 6


# -------------------- MAIN COUNSELLING FUNCTION --------------------

def rank_counselling(query, rank_override=None):

    marks = extract_marks(query)
    percentile = extract_percentile(query)

    # ---------------- DETERMINE RANK ----------------

    if marks:
        # rough mapping
        if marks >= 280:
            rank = 100
        elif marks >= 250:
            rank = 1000
        elif marks >= 220:
            rank = 3000
        elif marks >= 200:
            rank = 7000
        elif marks >= 180:
            rank = 15000
        elif marks >= 150:
            rank = 30000
        elif marks >= 120:
            rank = 60000
        elif marks >= 100:
            rank = 90000
        else:
            rank = 150000
        exam = "mains"

    elif percentile:
        year = extract_year(query)
        rank = percentile_to_rank(percentile, year)
        exam = "mains"

    else:
      rank = rank_override if rank_override else extract_rank(query)

    # default exam
      exam = "mains"

    # only treat as advanced if explicitly mentioned
      if "advanced" in query.lower():
        exam = "advanced"


    if not rank:
        return None, "Please tell me your rank, marks, or percentile."

    # ---------------- EXTRACT OTHER FEATURES ----------------

    branch = extract_branch(query)
    category = extract_category(query)
    gender = extract_gender(query)
    inst_type = extract_institute_type(query)

    df = cutoff_df.copy()

    # clean rank columns
    df["CloseRank"] = df["CloseRank"].astype(str).str.replace(r"\D", "", regex=True)
    df = df[df["CloseRank"].str.isnumeric()]
    df["CloseRank"] = df["CloseRank"].astype(int)

    # ---------------- FILTERS ----------------

    # strict category
    df = df[df["Category"] == category]

    # remove PwD always unless asked
    if "pwd" not in query.lower():
        df = df[~df["Category"].str.contains("PwD", case=False, na=False)]

    # gender
    if gender == "Female":
        df = df[df["Gender"].str.contains("Female", na=False)]
    else:
        df = df[df["Gender"].str.contains("Gender-Neutral", na=False)]

    # branch
    if branch:
        df = df[df["Branch"].str.lower().str.contains(branch, na=False)]

    # ---------------- EXAM FILTER ----------------

    if exam == "mains":
        df = df[
            df["Institute"].str.contains(
                "National Institute of Technology|Information Technology",
                case=False,
                na=False
            )
        ]

    elif exam == "advanced":
        df = df[
            df["Institute"].str.contains(
                "Indian Institute of Technology",
                case=False,
                na=False
            )
        ]

    # ---------------- FINAL RANK FILTER ----------------

    # allow only colleges within realistic range
    df = df[df["CloseRank"] >= rank * 0.8]


    if df.empty:
        return None, "No colleges found for your profile."

    # remove duplicates
    df = df.drop_duplicates(subset=["Institute", "Branch", "Category", "Gender"])

    # priority sort
    df["priority"] = df["Institute"].apply(institute_priority)
    df = df.sort_values(by=["priority", "CloseRank"])

    return df.head(10), None
