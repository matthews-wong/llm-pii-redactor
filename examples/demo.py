"""Show what the provider receives versus what the caller gets back."""

from pii_redactor import FakeProvider, Message, RedactingGateway, Request

PROMPT = (
    "Customer ana@example.com (card 4111 1111 1111 1111, ip 10.0.0.7) "
    "reports that key sk-abcdefghijklmnop1234 stopped working."
)

provider = FakeProvider()
reply = RedactingGateway(provider).complete(Request([Message("user", PROMPT)]))

print("sent to provider:", provider.seen[0].messages[0].content)
print("returned to caller:", reply.content)
