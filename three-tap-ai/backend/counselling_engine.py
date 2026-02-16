import re
from csv_engine import cutoff_df


# -------------------- MARKS HANDLING --------------------

def extract_marks(q):
    q = q.lower()

    # detect marks keywords
    if any(x in q for x in ["marks", "score", "out of"]):
        nums = re.findall(r"\d{2,3}", q)
        if nums:
            return int(nums[0])

    return None


def mains_marks_to_rank(marks):
    # rough mapping
    if marks >= 280:
        return 100
    elif marks >= 250:
        return 1000
    elif marks >= 220:
        return 3000
    elif marks >= 200:
        return 7000
    elif marks >= 180:
        return 15000
    elif marks >= 150:
        return 30000
    elif marks >= 120:
        return 60000
    elif marks >= 100:
        return 90000
    else:
        return 150000


# -------------------- EXAM TYPE --------------------

def extract_exam_type(q):
    q = q.lower()
    if "advanced" in q:
        return "advanced"
    if "mains" in q:
        return "mains"
    return "unknown"


# -------------------- RANK / PERCENTILE --------------------

def extract_rank(q):
    q = q.lower()

    # detect lakh
    lakh_match = re.search(r"(\d+)\s*lakh", q)
    if lakh_match:
        return int(lakh_match.group(1)) * 100000

    # detect AIR
    air_match = re.search(r"(air|all india rank)\s*(\d{1,7})", q)
    if air_match:
        return int(air_match.group(2))

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
    q = q.lower()

    match = re.search(r"(\d{1,3}(\.\d+)?)\s*(%|percentile)", q)
    if match:
        val = float(match.group(1))
        if 0 < val <= 100:
            return val

    return None



TOTAL_CANDIDATES = 1100000

def percentile_to_rank(percentile):
    rank = int((100 - percentile) * TOTAL_CANDIDATES / 100)
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
    q = q.lower()
    if "iiit" in q:
        return "iiit"
    if "nit" in q:
        return "nit"
    if "iit" in q:
        return "iit"
    return None


# -------------------- INSTITUTE PRIORITY --------------------

def institute_priority(name):
    name = name.lower()

    # Top IITs
    if "bombay" in name or "delhi" in name or "madras" in name or "kanpur" in name or "kharagpur" in name:
        return 1

    # Other IITs
    if "indian institute of technology" in name:
        return 2

    # Top NITs
    if "trichy" in name or "warangal" in name or "surathkal" in name:
        return 3

    # Other NITs
    if "national institute of technology" in name:
        return 4

    # IIITs
    if "information technology" in name:
        return 5

    return 6



# -------------------- MAIN COUNSELLING FUNCTION --------------------

def rank_counselling(query, rank_override=None):

    # 1. detect marks
    marks = extract_marks(query)
    percentile = extract_percentile(query)
    exam = extract_exam_type(query)

    if marks:
        rank = mains_marks_to_rank(marks)
        exam = "mains"

    elif percentile:
        rank = percentile_to_rank(percentile)
        exam = "mains"   # force mains for percentile


    else:
        rank = rank_override if rank_override else extract_rank(query)


    if not rank:
        return None, "Please tell me your rank or marks."

    branch = extract_branch(query)
    category = extract_category(query)
    gender = extract_gender(query)
    inst_type = extract_institute_type(query)
    

    df = cutoff_df.copy()

    # ---------------- CLEAN RANK COLUMNS ----------------

    df["CloseRank"] = df["CloseRank"].astype(str)
    df["CloseRank"] = df["CloseRank"].str.replace(r"\D", "", regex=True)
    df = df[df["CloseRank"].str.isnumeric()]
    df["CloseRank"] = df["CloseRank"].astype(int)

    df["OpenRank"] = df["OpenRank"].astype(str)
    df["OpenRank"] = df["OpenRank"].str.replace(r"\D", "", regex=True)
    df = df[df["OpenRank"].str.isnumeric()]
    df["OpenRank"] = df["OpenRank"].astype(int)

    # ---------------- FILTERS ----------------

    if branch:
        df = df[df["Branch"].str.lower().str.contains(branch, na=False)]

    if category:
        df = df[df["Category"].str.contains(category, na=False)]

    
    # always remove PwD unless explicitly requested
    if "pwd" not in query.lower():
        df = df[~df["Category"].str.contains("PwD", case=False, na=False)]



    if gender == "Female":
        df = df[df["Gender"].str.contains("Female", na=False)]
    else:
        df = df[df["Gender"].str.contains("Gender-Neutral", na=False)]

    # ---------------- EXAM BASED FILTER ----------------

    # STRICT exam filtering
    # ---------------- EXAM BASED FILTER ----------------

    if exam == "mains":
    # Remove all IITs completely
       df = df[~df["Institute"].str.contains(
        "Indian Institute of Technology",
        case=False,
        na=False
    )]

    elif exam == "advanced":
    # Keep only IITs
       df = df[df["Institute"].str.contains(
        "Indian Institute of Technology",
        case=False,
        na=False
    )]



    # ---------------- INSTITUTE TYPE FILTER ----------------

    if inst_type == "iit":
        df = df[df["Institute"].str.contains("Indian Institute of Technology", na=False)]
    elif inst_type == "nit":
        df = df[df["Institute"].str.contains("National Institute of Technology", na=False)]
    elif inst_type == "iiit":
        df = df[df["Institute"].str.contains("Information Technology", na=False)]

    # ---------------- FINAL COUNSELLING CONDITION ----------------

    df = df[df["CloseRank"] >= rank]


    if df.empty:
        if inst_type:
            return None, f"No {inst_type.upper()} available for this rank."
        return None, "No colleges found for your profile."

    # remove duplicates
    df = df.drop_duplicates(subset=["Institute", "Branch", "Category", "Gender"])

    # apply institute priority
    df["priority"] = df["Institute"].apply(institute_priority)

    # sort: best institute first
    df = df.sort_values(
    by=["priority", "CloseRank"],
    ascending=[True, True]
)



    return df.head(10), None
