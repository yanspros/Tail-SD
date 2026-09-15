#!/usr/bin/env python3
"""Run a model-specific Tail-SD trainer plugin against frozen manifests.

The backend factory must return an object with ``train(bank, masks, order,
config, output_dir)``. Keeping this adapter external avoids vendoring or
silently patching CosyVoice.
"""
from __future__ import annotations

import argparse
import importlib
from pathlib import Path

from tailsd.io import load_json, load_yaml


def load_factory(spec: str):
    module_name, function_name = spec.split(":", 1)
    return getattr(importlib.import_module(module_name), function_name)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend-factory", required=True, help="importable module:function")
    parser.add_argument("--bank", required=True)
    parser.add_argument("--mask", required=True)
    parser.add_argument("--order", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    backend = load_factory(args.backend_factory)()
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    backend.train(load_json(args.bank), load_json(args.mask), load_json(args.order), load_yaml(args.config), args.output_dir)


if __name__ == "__main__":
    main()
