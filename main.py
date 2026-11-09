"""
Try the bot from the terminal.

    python main.py          # chat with the bot (type 'quit' to exit, 'stats' for the summary)
    python main.py --demo   # run a scripted Turkish + English demo conversation

Demo order numbers: 100231 (on the way), 100245 (being prepared),
100262 (delivered 5 days ago), 100278 (delivered 30 days ago),
100290 (late), 100301 (cancelled).
"""

import json
import sys

from src.bot import CustomerServiceBot

DEMO = [
    ("CUST-TR", "Merhaba"),
    ("CUST-TR", "Siparişim nerede?"),
    ("CUST-TR", "100231"),
    ("CUST-TR", "İptal edebilir miyim?"),
    ("CUST-TR", "Kartımdan iki kere para çekildi, rezalet!"),
    ("CUST-EN", "Hi, I want to return my coffee machine, order 100262"),
    ("CUST-EN", "Also, where is order 100290?"),
    ("CUST-EN", "I forgot my password"),
    ("CUST-EN", "What's the weather like?"),
    ("CUST-EN", "Thanks, bye"),
]


def show(customer_id: str, message: str, result: dict) -> None:
    print(f"\n[{customer_id}] {message}")
    print(f"  topic: {result['intent']} ({result['confidence']:.2f}) · language: {result['language']}"
          f" · outcome: {result['outcome']} · priority: {result['priority']}")
    print(f"  bot: {result['reply']}")


def run_demo(bot: CustomerServiceBot) -> None:
    print("=== ShopNova customer service bot: demo ===")
    for customer_id, message in DEMO:
        show(customer_id, message, bot.handle_message(customer_id, message))
    print("\n=== Operations summary ===")
    print(json.dumps(bot.db.get_summary_metrics(), indent=2, ensure_ascii=False))


def run_chat(bot: CustomerServiceBot) -> None:
    print("ShopNova customer service bot. Type 'stats' for the summary, 'quit' to exit.")
    print("Demo order numbers: 100231, 100245, 100262, 100278, 100290, 100301\n")
    while True:
        try:
            message = input("you: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not message:
            continue
        if message.lower() in {"quit", "exit", "q"}:
            break
        if message.lower() == "stats":
            print(json.dumps(bot.db.get_summary_metrics(), indent=2, ensure_ascii=False))
            continue
        result = bot.handle_message("CLI-USER", message)
        print(f"bot: {result['reply']}")
        print(f"     [{result['intent']} {result['confidence']:.2f} · {result['outcome']} · {result['priority']}]\n")


if __name__ == "__main__":
    bot = CustomerServiceBot(db_path=":memory:")
    if "--demo" in sys.argv:
        run_demo(bot)
    else:
        run_chat(bot)
