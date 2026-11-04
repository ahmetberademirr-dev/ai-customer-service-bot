# AI-Powered Customer Service Bot

An intelligent customer support automation system designed to classify incoming customer inquiries, prioritize support tickets, and generate automated responses using natural language processing and machine learning.

> **Status:** In Progress (Active Development)

## Overview

Customer service teams handle large volumes of repetitive inquiries daily. This project automates the initial triage and response workflow by combining a machine learning intent classifier with a structured SQL backend and an LLM-assisted response generator.

### Key Capabilities
- **Intent Classification:** Categorizes incoming messages (e.g., *Order Status*, *Refund Request*, *Technical Support*, *Billing Inquiry*) using TF-IDF vectorization and Scikit-Learn classifiers.
- **Automated Ticket Triage:** Assigns priority scores and routes complex queries to human agents while resolving standard requests automatically.
- **SQL Data Pipeline:** Logs interactions, response times, and resolution metrics into a relational database for operational analytics.
- **Response Generation:** Produces context-aware replies using predefined templates and OpenAI API integration.

## Tech Stack
- **Language:** Python 3.11+
- **Machine Learning:** Scikit-Learn, Pandas, NumPy
- **Database:** SQLite / PostgreSQL (SQL)
- **LLM Integration:** OpenAI API
- **Data Pipeline:** Automated ETL logging for support metrics

## Project Structure

```text
ai-customer-service-bot/
├── src/
│   ├── __init__.py
│   ├── classifier.py      # TF-IDF + Scikit-Learn intent classification pipeline
│   ├── database.py        # SQL database schema and ticket logging queries
│   └── bot.py             # Core customer service response engine
├── main.py                # CLI & webhook entry point
├── requirements.txt       # Project dependencies
└── .env.example           # Environment variable template
```

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ahmetberademirr-dev/ai-customer-service-bot.git
   cd ai-customer-service-bot
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```

4. **Run the bot in interactive demo mode:**
   ```bash
   python main.py
   ```

## Roadmap
- [x] SQL database schema for ticket tracking and analytics
- [x] Baseline intent classifier with Scikit-Learn (TF-IDF + Logistic Regression)
- [x] Core automated response pipeline
- [ ] Multi-channel webhook integration (WhatsApp / Telegram / Web Chat)
- [ ] Analytics dashboard for resolution rate and response time metrics

## Author
**Ahmet Bera Demir**  
Management Engineering, Istanbul Technical University (ITU)
