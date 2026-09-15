"""Public, manifest-driven implementation of Tail-SD and its controls."""

from .masks import allocate_tail_masks, build_full_sd_labels
from .random_pr import build_random_pr_masks
from .metrics import classify, diagnostics, paired_bootstrap

__all__ = [
    "allocate_tail_masks",
    "build_full_sd_labels",
    "build_random_pr_masks",
    "classify",
    "diagnostics",
    "paired_bootstrap",
]

__version__ = "0.1.0rc1"
