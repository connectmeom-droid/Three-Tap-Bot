from backend.intent_engine import detect_intent
from backend.csv_engine import search_cutoff
from backend.counselling_engine import (
    rank_counselling,
    extract_percentile,
    percentile_to_rank
)


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
    # detect percentile
            import re
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

            if msg:
                return msg

            reply = "🎯 Best colleges for your profile:\n\n"
            for _, row in df.iterrows():
                reply += (
                    f"{row['Institute']}\n"
                    f"Branch: {row['Branch']}\n"
                    f"Category: {row['Category']} | {row['Gender']}\n"
                    f"Closing Rank: {row['CloseRank']}\n\n"
              )

            return reply.strip()


        return "Ask about ranks, percentiles, cutoffs, or colleges."

    except Exception as e:
        print("ERROR:", e)
        return "Server error. Please try again."
