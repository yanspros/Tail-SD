import unittest

from tailsd.metrics import classify, diagnostics


class MetricsTest(unittest.TestCase):
    def test_strict_complete_contract(self):
        result = classify(True, False, "one two three four", "one two three four")
        self.assertEqual(result["classification"], "COMPLETE")
        self.assertIs(result["strict_complete"], True)
        self.assertEqual(result["text_coverage_ratio"], 1.0)
        self.assertEqual(result["trailing_deleted_words"], 0)

    def test_hc_contract_and_trailing_deletions(self):
        reference = "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi omicron pi rho sigma tau upsilon"
        hypothesis = "alpha beta gamma delta epsilon"
        result = classify(True, False, reference, hypothesis)
        self.assertEqual(result["classification"], "EARLY_EOS")
        self.assertEqual(result["trailing_deleted_words"], 15)
        self.assertIs(result["hc_early_eos"], True)

    def test_non_tail_rate_uses_reference_denominator(self):
        result = diagnostics("alpha beta gamma delta", "alpha wrong gamma")
        self.assertEqual(result["word_error_counts"]["errors"], 2)
        self.assertEqual(result["trailing_deleted_words"], 1)
        self.assertEqual(result["non_tail_error_count"], 1)
        self.assertEqual(result["non_tail_error_rate"], 0.25)

    def test_cap_precedence(self):
        result = classify(True, True, "alpha beta", "alpha beta")
        self.assertEqual(result["classification"], "CAP_TRUNCATED")
