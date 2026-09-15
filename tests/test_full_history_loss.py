import unittest

try:
    import torch
except ImportError:  # pragma: no cover
    torch = None

from tailsd.train import assert_full_history_contract, masked_causal_cross_entropy


@unittest.skipUnless(torch is not None, "PyTorch is not installed")
class FullHistoryLossTest(unittest.TestCase):
    def test_masked_prefix_stays_in_causal_graph_without_direct_ce(self):
        inputs = torch.tensor([[0.2], [0.3], [0.4]], requires_grad=True)
        hidden = torch.cumsum(inputs, dim=0)
        logits = torch.cat([hidden, -hidden], dim=1)
        labels = torch.tensor([0, 1, 0])
        active = torch.tensor([False, False, True])
        loss, audit = masked_causal_cross_entropy(logits, labels, active)
        loss.backward()
        self.assertEqual(audit["supervised_token_count"], 1)
        self.assertEqual(audit["masked_out_valid_token_count"], 2)
        self.assertTrue(bool(torch.isfinite(loss)))
        self.assertIsNotNone(inputs.grad)
        self.assertTrue(bool(torch.all(inputs.grad[:2] != 0)))

    def test_history_length_cannot_be_shortened(self):
        assert_full_history_contract(5, 5, 5)
        with self.assertRaisesRegex(ValueError, "must not shorten"):
            assert_full_history_contract(4, 5, 5)
