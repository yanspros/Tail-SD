import unittest

from tailsd.metrics import paired_bootstrap


def row(source, seed, complete):
    return {
        "source_id": source,
        "seed": seed,
        "classification": "COMPLETE" if complete else "OTHER_FAILURE",
        "hc_early_eos": False,
        "wer": 0.0 if complete else 1.0,
        "text_coverage_ratio": 1.0 if complete else 0.5,
        "non_tail_error_rate": 0.0,
    }


class BootstrapTest(unittest.TestCase):
    def test_two_seeds_are_aggregated_inside_source_cluster(self):
        left = [row("a", 0, True), row("a", 1, False), row("b", 0, True), row("b", 1, True)]
        right = [row("a", 0, False), row("a", 1, False), row("b", 0, True), row("b", 1, False)]
        result = paired_bootstrap(left, right, resamples=1000, seed=11)
        self.assertEqual(result["source_count"], 2)
        self.assertEqual(result["point_estimate"], 0.5)
        self.assertEqual(result["ci95"], [0.5, 0.5])

    def test_pairing_identity_must_match(self):
        with self.assertRaisesRegex(ValueError, "paired source identities differ"):
            paired_bootstrap([row("a", 0, True)], [row("b", 0, True)])
