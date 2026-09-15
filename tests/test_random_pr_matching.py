import unittest

from tailsd.random_pr import audit_random_pr_match, build_random_pr_masks


def tails():
    return [
        {
            "record_index": index,
            "record_id": f"r{index}",
            "source_id": f"s{index}",
            "branch": "termination" if index == 0 else "content",
            "T_i": length,
            "K_i": k_i,
            "tail_start": length - k_i,
            "tail_end_exclusive": length,
            "active_speech_positions": list(range(length - k_i, length)),
            "active_eos_special_positions": [length] if index == 0 else [],
            "M_i": k_i + (index == 0),
            "target_history_identity": f"target-{index}",
        }
        for index, (length, k_i) in enumerate(((8, 3), (10, 4), (7, 2)))
    ]


class RandomPRMatchingTest(unittest.TestCase):
    def test_random_pr_is_deterministic_and_per_record_matched(self):
        first = build_random_pr_masks(tails(), seed=20260915)
        second = build_random_pr_masks(tails(), seed=20260915)
        self.assertEqual(first, second)
        self.assertEqual(first["rng"]["draw_count"], 3)
        self.assertIs(first["rng"]["no_redraw"], True)
        self.assertIs(first["audit"]["all_match"], True)
        self.assertTrue(all(0 <= row["sampled_start"] <= row["T_i"] - row["K_i"] for row in first["records"]))

    def test_audit_rejects_modified_budget(self):
        result = build_random_pr_masks(tails(), seed=7)
        result["records"][1]["M_i"] += 1
        audit = audit_random_pr_match(tails(), result["records"])
        self.assertIs(audit["all_match"], False)
        self.assertEqual(audit["match_counts"]["M_i"], 2)

    def test_illegal_k_is_rejected(self):
        rows = tails()
        rows[0]["K_i"] = 0
        with self.assertRaisesRegex(ValueError, "illegal K_i"):
            build_random_pr_masks(rows, seed=1)
