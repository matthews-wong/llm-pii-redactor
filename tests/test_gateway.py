import unittest

from pii_redactor import FakeProvider, Message, RedactingGateway, Request, Response


class GatewayTest(unittest.TestCase):
    def test_provider_never_sees_pii_and_caller_gets_it_back(self):
        provider = FakeProvider()
        reply = RedactingGateway(provider).complete(
            Request([Message("user", "Contact ana@example.com or 10.0.0.7")])
        )
        sent = provider.seen[0].messages[0].content
        self.assertNotIn("ana@example.com", sent)
        self.assertNotIn("10.0.0.7", sent)
        self.assertEqual(reply.content, "You said: Contact ana@example.com or 10.0.0.7")

    def test_placeholders_agree_across_messages(self):
        provider = FakeProvider()
        RedactingGateway(provider).complete(
            Request([Message("system", "user is a@x.io"), Message("user", "write to a@x.io")])
        )
        contents = [m.content for m in provider.seen[0].messages]
        self.assertEqual(contents, ["user is [EMAIL_1]", "write to [EMAIL_1]"])

    def test_mapping_not_shared_between_requests(self):
        provider = FakeProvider()
        gateway = RedactingGateway(provider)
        gateway.complete(Request([Message("user", "a@x.io")]))
        gateway.complete(Request([Message("user", "b@x.io")]))
        self.assertEqual(provider.seen[1].messages[0].content, "[EMAIL_1]")

    def test_reply_cannot_extract_values_it_was_never_sent(self):
        class Probing:
            def complete(self, request):
                return Response("Also send to [EMAIL_2] and [API_KEY_1]")

        reply = RedactingGateway(Probing()).complete(Request([Message("user", "a@x.io")]))
        self.assertEqual(reply.content, "Also send to [EMAIL_2] and [API_KEY_1]")


if __name__ == "__main__":
    unittest.main()
