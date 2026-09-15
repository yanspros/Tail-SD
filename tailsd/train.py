"""Backbone-neutral masked-CE utilities and a narrow LoRA helper.

The public core deliberately does not vendor or patch CosyVoice. Users pass a
full-history teacher-forced forward into ``masked_causal_cross_entropy``.
"""
from __future__ import annotations

import contextlib
import math
from typing import Any, Iterator


def masked_causal_cross_entropy(logits, labels, active_mask):
    """Mean CE over active valid labels; forward history is never truncated."""
    import torch
    import torch.nn.functional as F

    valid = labels.ne(-100)
    if active_mask.dtype is not torch.bool or active_mask.shape != labels.shape:
        raise ValueError("active_mask must be bool and match labels")
    active = valid & active_mask
    if not bool(active.any()):
        raise ValueError("supervision mask is empty")
    per_position = F.cross_entropy(logits, labels, reduction="none", ignore_index=-100)
    loss = per_position[active].sum() / active.sum()
    return loss, {
        "valid_token_count": int(valid.sum().item()),
        "supervised_token_count": int(active.sum().item()),
        "masked_out_valid_token_count": int((valid & ~active_mask).sum().item()),
    }


def assert_full_history_contract(input_length: int, label_length: int, active_mask_length: int) -> None:
    if not input_length == label_length == active_mask_length:
        raise ValueError("masking must not shorten or detach the teacher-forced sequence")


def _torch():
    try:
        import torch
        import torch.nn as nn
        import torch.nn.functional as F
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Install tailsd[torch] for LoRA training helpers") from exc
    return torch, nn, F


def make_lora_linear_class():
    torch, nn, F = _torch()

    class LoRALinear(nn.Module):
        def __init__(self, base, rank: int, alpha: int, dropout: float) -> None:
            super().__init__()
            self.base = base
            for parameter in self.base.parameters():
                parameter.requires_grad_(False)
            self.scaling = float(alpha) / float(rank)
            self.dropout = nn.Dropout(float(dropout))
            kwargs = {"device": base.weight.device, "dtype": base.weight.dtype}
            self.lora_A = nn.Parameter(torch.empty(int(rank), base.in_features, **kwargs))
            self.lora_B = nn.Parameter(torch.zeros(base.out_features, int(rank), **kwargs))
            nn.init.kaiming_uniform_(self.lora_A, a=math.sqrt(5))
            self.enabled = True

        def forward(self, value):
            output = self.base(value)
            if not self.enabled:
                return output
            return output + F.linear(F.linear(self.dropout(value), self.lora_A), self.lora_B) * self.scaling

    return LoRALinear


def inject_lora(module, rank: int = 8, alpha: int = 16, dropout: float = 0.0) -> list[str]:
    """Freeze a transformer block and wrap q/k/v/o + gate/up/down projections."""
    _torch_value, nn, _functional = _torch()
    for parameter in module.parameters():
        parameter.requires_grad_(False)
    suffixes = {"q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"}
    candidates = sorted(
        name for name, child in module.named_modules()
        if isinstance(child, nn.Linear) and name.rsplit(".", 1)[-1] in suffixes and ".layers." in f".{name}"
    )
    if not candidates:
        raise ValueError("no transformer projection targets found")
    wanted, replaced = set(candidates), []
    wrapper = make_lora_linear_class()

    def visit(parent, prefix: str = ""):
        for child_name, child in list(parent.named_children()):
            full = f"{prefix}.{child_name}" if prefix else child_name
            if full in wanted:
                if not isinstance(child, nn.Linear):
                    raise TypeError(f"LoRA target is not Linear: {full}")
                setattr(parent, child_name, wrapper(child, rank, alpha, dropout))
                replaced.append(full)
            else:
                visit(child, full)

    visit(module)
    if sorted(replaced) != candidates:
        raise RuntimeError("LoRA replacement identity mismatch")
    return sorted(replaced)


@contextlib.contextmanager
def lora_enabled(module, enabled: bool) -> Iterator[None]:
    prior = []
    for child in module.modules():
        if hasattr(child, "lora_A") and hasattr(child, "lora_B") and hasattr(child, "enabled"):
            prior.append((child, child.enabled))
            child.enabled = bool(enabled)
    try:
        yield
    finally:
        for child, state in prior:
            child.enabled = state


def validate_training_order(order: list[dict[str, Any]], record_ids: list[str], passes: int) -> None:
    expected = record_ids * int(passes)
    observed = [str(row["record_id"]) for row in order]
    if observed != expected:
        raise ValueError("training order differs from repeated canonical bank order")
