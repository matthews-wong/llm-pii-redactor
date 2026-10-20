# llm-pii-redactor

Strip PII and secrets from a prompt before it leaves the process, then put the
original values back into the model's reply. Stdlib Python, no network, no
dependencies.

```
"Mail ana@example.com"  ->  "Mail [EMAIL_1]"  ->  model  ->  "Sent to [EMAIL_1]"  ->  "Sent to ana@example.com"
```

## Usage

```python
from pii_redactor import RedactingGateway, FakeProvider

gateway = RedactingGateway(FakeProvider())
reply = gateway.complete("Summarise the ticket from ana@example.com")
```

Run the demo and the tests:

```
PYTHONPATH=. python3 examples/demo.py
python3 -m unittest -v
```

## Design notes

- Placeholders are stable within one request: the same value always maps to the
  same `[KIND_n]`, so the model can still reason about "the same person".
- The mapping lives only in memory for the duration of one call and is never
  logged or sent upstream.
- Model output is untrusted. Only placeholders that were issued for this request
  are restored; anything else that looks like a placeholder is left as text.
- Detection is regex based and deliberately conservative. It is a safety net, not
  a guarantee: names and free-form addresses are not detected.
