import unittest

from tailsd.target_construction import build_content_candidates, build_termination_candidates


def scored(source, seed, classification, coverage, trailing, wer, non_tail):
    return {
        "source_id": source,
        "seed": seed,
        "classification": classification,
        "eos_generated": True,
        "cap_hit": False,
        "text_coverage_ratio": coverage,
        "trailing_deleted_words": trailing,
        "wer": wer,
        "non_tail_error_rate": non_tail,
    }


class TargetConstructionTest(unittest.TestCase):
    def test_termination_first_hc_and_quality_ranking(self):
        natural = [
            scored("s", 2, "EARLY_EOS", 0.7, 12, 0.4, 0.1),
            scored("s", 0, "EARLY_EOS", 0.8, 10, 0.3, 0.1),
        ]
        continuations = [
            scored("s", 1, "COMPLETE", 1.0, 0, 0.05, 0.04),
            scored("s", 0, "COMPLETE", 0.96, 0, 0.06, 0.02),
        ]
        result = build_termination_candidates(natural, continuations, 0.1, 0.1)
        self.assertEqual(result[0]["failed_natural"]["seed"], 0)
        self.assertEqual(result[0]["selected_target"]["seed"], 0)

    def test_content_uses_first_other_failure_and_alternate_success(self):
        natural = [
            scored("s", 0, "OTHER_FAILURE", 0.9, 1, 0.2, 0.2),
            scored("s", 1, "COMPLETE", 1.0, 0, 0.02, 0.02),
            scored("s", 2, "COMPLETE", 1.0, 0, 0.03, 0.03),
        ]
        result = build_content_candidates(natural, 0.1, 0.1)
        self.assertEqual(result[0]["failed_natural"]["seed"], 0)
        self.assertEqual(result[0]["selected_target"]["seed"], 1)

    def test_content_requires_non_tail_improvement(self):
        natural = [
            scored("s", 0, "OTHER_FAILURE", 0.9, 1, 0.1, 0.01),
            scored("s", 1, "COMPLETE", 1.0, 0, 0.02, 0.02),
        ]
        self.assertEqual(build_content_candidates(natural, 0.1, 0.1), [])
