"""
Entry point for the AI-Powered Customer Service Bot.
"""

from src.bot import CustomerServiceBot


def run_demo() -> None:
    bot = CustomerServiceBot()
    sample_queries = [
        ("CUST-101", "Hi, where is my order? It hasn't arrived yet."),
        ("CUST-102", "I was charged twice on my monthly invoice."),
        ("CUST-103", "How can I return a damaged item and get a refund?"),
        ("CUST-104", "The app keeps crashing when I try to reset my password."),
    ]

    print("=== AI-Powered Customer Service Bot Demo ===\n")
    for customer_id, query in sample_queries:
        result = bot.handle_message(customer_id=customer_id, message=query)
        print(f"Customer ({customer_id}): {query}")
        print(f" -> Predicted Intent : {result['intent']} (confidence: {result['confidence']})")
        print(f" -> Automated Reply  : {result['reply']}\n")

    metrics = bot.db.get_summary_metrics()
    print("Operational Summary:", metrics)


if __name__ == "__main__":
    run_demo()
