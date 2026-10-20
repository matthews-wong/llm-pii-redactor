import unittest

from pii_redactor import Redactor, restore


class RedactorTest(unittest.TestCase):
    def setUp(self):
        self.redactor = Redactor()

    def test_email_round_trip(self):
        r = self.redactor.redact("Mail ana@example.com now")
        self.assertEqual(r.text, "Mail [EMAIL_1] now")
        self.assertEqual(restore(r.text, r.mapping), "Mail ana@example.com now")

    def test_same_value_same_placeholder(self):
        r = self.redactor.redact("a@x.io b@x.io a@x.io")
        self.assertEqual(r.text, "[EMAIL_1] [EMAIL_2] [EMAIL_1]")

    def test_card_requires_luhn(self):
        self.assertEqual(self.redactor.redact("4111 1111 1111 1111").text, "[CARD_1]")
        # Fails Luhn, so it is not a card; the loose phone pattern may still claim
        # part of it, which over-redacts but never leaks.
        self.assertNotIn("[CARD_", self.redactor.redact("4111 1111 1111 1112").text)

    def test_ip_octet_range(self):
        self.assertEqual(self.redactor.redact("host 10.0.0.7").text, "host [IP_1]")
        self.assertNotIn("[IP_", self.redactor.redact("v 999.1.1.1").text)

    def test_api_key(self):
        r = self.redactor.redact("key sk-abcdefghijklmnop1234")
        self.assertEqual(r.text, "key [API_KEY_1]")

    def test_unissued_placeholder_not_restored(self):
        self.assertEqual(restore("see [EMAIL_9]", {"[EMAIL_1]": "a@x.io"}), "see [EMAIL_9]")

    def test_shared_mapping_continues_numbering(self):
        first = self.redactor.redact("a@x.io")
        second = self.redactor.redact("b@x.io a@x.io", first.mapping)
        self.assertEqual(second.text, "[EMAIL_2] [EMAIL_1]")


if __name__ == "__main__":
    unittest.main()
