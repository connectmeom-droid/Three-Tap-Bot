from intent_engine import detect_intent
from csv_engine import search_cutoff
from counselling_engine import (
    rank_counselling,
    extract_percentile,
    percentile_to_rank,
    extract_rank
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

           df, msg = rank_counselling(question)

           if msg:
                return msg

    # get rank for formatting
           rank = extract_rank(question)
           if not rank:
                percentile = extract_percentile(question)
                if percentile:
                    rank = percentile_to_rank(percentile)
                else:
                    rank = 0

           return format_rank_response(df, rank)



        return "Ask about ranks, percentiles, cutoffs, or colleges."

    except Exception as e:
        print("ERROR:", e)
        return "Server error. Please try again."
