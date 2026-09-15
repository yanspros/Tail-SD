import unittest

from tailsd.masks import allocate_tail_masks, build_full_sd_labels


RATIOS = {"termination": 0.5, "content": 0.25}


def records():
    return [
        {"record_id": "t0", "source_id": "s0", "branch": "termination", "T_i": 5},
        {"record_id": "c0", "source_id": "s1", "branch": "content", "T_i": 5},
        {"record_id": "t1", "source_id": "s2", "branch": "termination", "T_i": 4},
        {"record_id": "c1", "source_id": "s3", "branch": "content", "T_i": 4},
    ]


class TailMaskBudgetTest(unittest.TestCase):
    def test_branch_aggregate_floor_and_residual_order(self):
        result = allocate_tail_masks(records(), RATIOS)
        by_id = {row["record_id"]: row for row in result["records"]}
        self.assertEqual([by_id["t0"]["K_i"], by_id["t1"]["K_i"]], [2, 2])
        self.assertEqual([by_id["c0"]["K_i"], by_id["c1"]["K_i"]], [1, 1])
        self.assertEqual(by_id["t0"]["active_eos_special_positions"], [5])
        self.assertEqual(by_id["c0"]["active_eos_special_positions"], [])
        self.assertEqual(by_id["t0"]["M_i"], 3)
        self.assertEqual(result["overall"]["active_speech_labels"], 6)
        self.assertEqual(result["overall"]["active_total_ce_labels"], 8)

    def test_earliest_record_gets_residual(self):
        rows = [
            {"record_id": "t0", "branch": "termination", "T_i": 3},
            {"record_id": "t1", "branch": "termination", "T_i": 3},
            {"record_id": "c0", "branch": "content", "T_i": 3},
            {"record_id": "c1", "branch": "content", "T_i": 3},
        ]
        result = allocate_tail_masks(rows, {"termination": 0.5, "content": 0.5})
        by_id = {row["record_id"]: row for row in result["records"]}
        self.assertEqual([by_id["t0"]["K_i"], by_id["t1"]["K_i"]], [2, 1])
        self.assertEqual([by_id["c0"]["K_i"], by_id["c1"]["K_i"]], [2, 1])

    def test_full_sd_uses_all_speech_and_branch_eos_rule(self):
        dense = build_full_sd_labels(records())
        by_id = {row["record_id"]: row for row in dense["records"]}
        self.assertEqual(by_id["t0"]["M_i"], 6)
        self.assertEqual(by_id["c0"]["M_i"], 5)
        self.assertEqual(dense["overall"]["active_total_ce_labels"], 20)
