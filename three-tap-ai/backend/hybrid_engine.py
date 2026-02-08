from intent_engine import detect_intent
from csv_engine import search_cutoff
from counselling_engine import (
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
            # check percentile
            percentile = extract_percentile(question)
            rank_override = None

            if percentile:
                rank_override = percentile_to_rank(percentile)

            result = rank_counselling(question, rank_override)

            if result is None:
                return "Please provide a valid rank or percentile."

            df, msg = result

            if msg:
                return msg

            reply = ""

            if percentile:
                reply += f"📊 Estimated Rank for {percentile}%ile: ~{rank_override}\n\n"

            reply += "🎯 Best colleges for your profile:\n\n"

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
