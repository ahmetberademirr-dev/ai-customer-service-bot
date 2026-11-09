# Evaluation report

Training examples: 690 ({'tr': 340, 'en': 350}) · Topics: 10 · Confidence threshold: 0.4

| | Held-out test set | Cross-validation |
|---|---|---|
| Questions | 120 | 690 |
| Topic accuracy | 100.0% | 90.4% |
| Bot answers on its own | 96.7% | 83.3% |
| Correct when it answers | 100.0% | 96.0% |
| Answers on the wrong topic | 0.0% | 3.3% |
| Asks the customer to rephrase | 3.3% | 16.7% |

Language detection accuracy (test set): 100.0%

The cross-validation column is the more conservative estimate.

## Accuracy by topic (test set)

| Topic | Correct |
|---|---|
| account_help | 12/12 |
| cancel_order | 12/12 |
| change_address | 12/12 |
| goodbye | 12/12 |
| greeting | 12/12 |
| human_agent | 12/12 |
| order_status | 12/12 |
| out_of_scope | 12/12 |
| payment_issue | 12/12 |
| return_refund | 12/12 |

## Mistakes on the test set

| Message | Expected | Predicted | Confidence | What the customer sees |
|---|---|---|---|---|

Regenerate with `python evaluate.py`.
