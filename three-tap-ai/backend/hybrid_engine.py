from backend.intent_engine import detect_intent
from backend.csv_engine import search_cutoff
from backend.counselling_engine import (
    rank_counselling,
    extract_percentile,
    percentile_to_rank,
)



def hybrid_answer(question):
    intent = detect_intent(question)
    q = question.lower()

    # ---------------- CUTOFF ----------------
    if intent == "cutoff":
        df = search_cutoff(question)

        if df.empty:
            return "No cutoff data found."

        reply = "📊 Cutoff Results:\n\n"
        for _, row in df.iterrows():
            reply += (
                f"{row['Institute']}\n"
                f"{row['Branch']}\n"
                f"Category: {row['Category']} | {row['Gender']}\n"
                f"Opening Rank: {row['OpenRank']} | Closing Rank: {row['CloseRank']}\n\n"
            )

        return reply.strip()

    # ---------------- RANK / PERCENTILE ----------------
    if intent == "rank":
        percentile = extract_percentile(q)

        df, msg = rank_counselling(question)

        if msg:
            return msg

        reply = ""

        # show estimated rank if percentile
        if percentile is not None:
            est_rank = percentile_to_rank(percentile)
            reply += f"📊 Estimated Rank for {percentile} percentile: ~{est_rank}\n\n"

        reply += "🎯 Best colleges for your profile:\n\n"

        for _, row in df.iterrows():
            reply += (
                f"{row['Institute']}\n"
                f"Branch: {row['Branch']}\n"
                f"Category: {row['Category']} | {row['Gender']}\n"
                f"Closing Rank: {row['CloseRank']}\n\n"
            )

        return reply.strip()

    return "I only answer JEE counselling and admission related questions."
