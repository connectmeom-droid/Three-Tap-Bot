from intent_engine import detect_intent
from csv_engine import search_cutoff
from counselling_engine import (
    rank_counselling,
    extract_percentile,
    percentile_to_rank
)

def format_rank_response(df, rank):
    if df is None or df.empty:
        return "No colleges found for this rank."

    safe = []
    moderate = []
    dream = []

    for _, row in df.iterrows():
        closing = int(row["CloseRank"])

        if closing >= rank * 1.5:
            safe.append(row)
        elif closing >= rank:
            moderate.append(row)
        else:
            dream.append(row)

    def build_section(title, data):
        text = f"{title}:\n"
        for r in data[:3]:
            text += f"- {r['Institute']} {r['Branch']}\n"
        return text

    reply = f"Based on your rank ({rank}):\n\n"

    if safe:
        reply += build_section("Safe options", safe)
    if moderate:
        reply += build_section("Moderate options", moderate)
    if dream:
        reply += build_section("Dream options", dream)

    return reply.strip()


def hybrid_answer(question):
    try:
        intent = detect_intent(question)
        q = question.lower()

        # ---------------- CUTOFF ----------------
        if intent == "cutoff":
            df = search_cutoff(question)

            if df is None or df.empty:
                return "No cutoff data found."

            reply = "📊 Cutoff Results:\n\n"
            for _, row in df.iterrows():
                reply += (
                    f"{row['Institute']}\n"
                    f"{row['Branch']}\n"
                    f"Category: {row['Category']} | {row['Gender']}\n"
                    f"Opening Rank: {row['OpenRank']} | "
                    f"Closing Rank: {row['CloseRank']}\n\n"
                )

            return reply.strip()

        # ---------------- RANK / PERCENTILE ----------------
        if intent == "rank":
            import re

    # check for percentile
            p_match = re.search(r"(\d{2,3})\s*percentile", question.lower())

            if p_match:
                percentile = int(p_match.group(1))

        # rough percentile → rank mapping
                if percentile >= 99:
                    rank = 1000
                elif percentile >= 97:
                    rank = 5000
                elif percentile >= 95:
                    rank = 10000
                elif percentile >= 90:
                    rank = 30000
                elif percentile >= 80:
                    rank = 80000
                else:
                    rank = 150000

                df, msg = rank_counselling(question, rank_override=rank)

            else:
                df, msg = rank_counselling(question)

        # extract rank for formatting
                nums = re.findall(r"\d{1,7}", question)
                rank = int(nums[0]) if nums else 0

            if msg:
               return msg

            return format_rank_response(df, rank)


        return "Ask about ranks, percentiles, cutoffs, or colleges."

    except Exception as e:
        print("ERROR:", e)
        return "Server error. Please try again."
