import pandas as pd
import os
import re

# safer absolute path
BASE = os.path.join(os.path.dirname(__file__), "../data/csv")

all_rows = []

# Load all CSV files
if os.path.exists(BASE):
    for year in os.listdir(BASE):
        year_path = os.path.join(BASE, year)
        if not os.path.isdir(year_path):
            continue

        for rnd in os.listdir(year_path):
            round_path = os.path.join(year_path, rnd)
            if not os.path.isdir(round_path):
                continue

            for file in os.listdir(round_path):
                if file.endswith(".csv"):
                    full_path = os.path.join(round_path, file)
                    df = pd.read_csv(full_path)
                    df["Year"] = year
                    df["Round"] = rnd
                    all_rows.append(df)

if all_rows:
    cutoff_df = pd.concat(all_rows, ignore_index=True)
else:
    cutoff_df = pd.DataFrame()

print("Loaded rows:", len(cutoff_df))


# -------------------------
# Extraction helpers
# -------------------------

def normalize(text):
    return str(text).lower().strip()


def extract_branch(query):
    q = query.lower()

    if "civil" in q:
        return "civil"
    if "ece" in q or "electronics" in q:
        return "electronics"
    if "electrical" in q:
        return "electrical"
    if "mech" in q or "mechanical" in q:
        return "mechanical"
    if "cse" in q or "computer" in q or "cs" in q:
        return "computer"

    return None


def extract_year(query):
    match = re.search(r"(20\d{2})", query)
    return match.group(1) if match else None


def extract_category(query):
    q = query.lower()
    if "obc" in q:
        return "OBC"
    if "ews" in q:
        return "EWS"
    if "sc" in q:
        return "SC"
    if "st" in q:
        return "ST"
    return "OPEN"


def extract_gender(query):
    q = query.lower()
    if "female" in q or "girl" in q or "women" in q:
        return "Female"
    return "Gender-Neutral"


def extract_institute(query):
    q = query.lower()

    # specific IITs
    iit_map = {
        "bombay": "bombay",
        "delhi": "delhi",
        "kanpur": "kanpur",
        "madras": "madras",
        "kharagpur": "kharagpur",
        "roorkee": "roorkee",
        "guwahati": "guwahati",
        "hyderabad": "hyderabad",
        "indore": "indore",
        "varanasi": "varanasi",
    }

    for key in iit_map:
        if key in q:
            return key

    # general types
    if "iiit" in q:
        return "iiit"
    if "iit" in q:
        return "iit"
    if "nit" in q:
        return "nit"

    return None


    # fallback to type
    if "iit" in q:
        return "iit"
    if "nit" in q:
        return "nit"
    if "iiit" in q:
        return "iiit"

    return None


# -------------------------
# Main search
# -------------------------

def search_cutoff(query):
    q = normalize(query)

    branch = extract_branch(q)
    year = extract_year(q)
    institute = extract_institute(q)

    df = cutoff_df.copy()

    # branch filter
    if branch:
        df = df[df["Branch"].str.lower().str.contains(branch, na=False)]

    # year filter
    if year:
        df = df[df["Year"].astype(str) == str(year)]

    # institute filter
    if institute:
        if institute == "iit":
            df = df[df["Institute"].str.contains("Indian Institute of Technology", case=False, na=False)]

        elif institute == "nit":
            df = df[df["Institute"].str.contains("National Institute of Technology", case=False, na=False)]

        elif institute == "iiit":
            df = df[df["Institute"].str.contains("Information Technology", case=False, na=False)]

        else:
            # loose matching for exact IIT name
            df = df[df["Institute"].str.lower().str.contains(institute.lower(), na=False)]

        # clean CloseRank before sorting
    df["CloseRank"] = df["CloseRank"].astype(str)
    df["CloseRank"] = df["CloseRank"].str.replace(r"\D", "", regex=True)
    df = df[df["CloseRank"] != ""]
    df["CloseRank"] = df["CloseRank"].astype(int)

    return df.sort_values("CloseRank").head(10)


