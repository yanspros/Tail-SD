#!/usr/bin/env python3
"""Read-only checks of published evidence bytes and descriptive rating aggregates."""
import csv
import json
import re
from collections import Counter
from pathlib import Path
from export_submission_evidence import sha, verify_manifest, human_summary

ROOT=Path(__file__).resolve().parents[1]
E=ROOT/"reproduction/evidence/source_data"

def main():
    checks={}
    checks["published_manifest"]=len(verify_manifest(E))
    index=json.loads((E/"index.json").read_text(encoding="utf-8"))
    for item in index["files"]:
        assert sha(E/item["path"])==item["public_sha256"],item["path"]
    checks["indexed_artifacts"]=len(index["files"])
    checks["human_source_manifest"]=len(verify_manifest(E/"human"))
    h=human_summary(E/"human")
    assert h==json.loads((E/"human/summary.json").read_text())
    checks["human_complete_grid_and_summary"]=True
    def csvrows(name):
        with (E/"human"/name).open(encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
    sources=csvrows("source_manifest_120.csv")
    mapping=csvrows("source_system_audio_seed_map.csv")
    assert len(sources)==120 and len({x["source_id"] for x in sources})==120
    assert len(Counter(x["length_bin"] for x in sources))==10
    assert set(Counter(x["length_bin"] for x in sources).values())=={12}
    assert len(mapping)==600 and len({(x["source_id"],x["system"]) for x in mapping})==600
    assert {x["inference_seed"] for x in mapping}=={"0"}
    assert {x["source_id"] for x in mapping}=={x["source_id"] for x in sources}
    assert set(Counter(x["source_id"] for x in mapping).values())=={5}
    assert all(re.fullmatch("[a-f0-9]{64}",x["audio_sha256"]) for x in mapping)
    checks["source_stimulus_mapping"]=True
    def get(name): return json.loads((E/"machine"/name).read_text(encoding="utf-8"))
    table=get("table_values_20260918.json")
    assert table["cv3_primary"]["contrasts"]["tail_vs_full_sd"]["ci95_pp"]==[-1.9,2.7]
    assert table["e13_unopened500"]["primary"]["delta_pp"]==4.7
    assert table["cv2_transfer"]["primary"]["delta_pp"]==2.9
    assert table["e14_position_study"]["aggregates"]["tail_minus_nonterminal_primary"]["delta_fraction"]==0.12975
    checks["frozen_key_results"]=True
    public=json.loads((ROOT/"reproduction/paper_results.json").read_text(encoding="utf-8"))
    assert public["human_evaluation"]==h
    checks["human_public_snapshot_current"]=True
    for filename in ["README.md","docs/reproducibility.md","reproduction/PAPER_RESULTS.md"]:
        text=(ROOT/filename).read_text(encoding="utf-8")
        assert "MUSHRA" not in text and "speaker similarity" not in text
    checks["reader_docs_no_old_human_metrics"]=True
    link_count=0
    for filename in ["README.md","docs/reproducibility.md","reproduction/README.md","reproduction/PAPER_RESULTS.md","reproduction/evidence/README.md"]:
        path=ROOT/filename
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)",path.read_text(encoding="utf-8")):
            target=target.split("#")[0]
            if not target or re.match(r"[a-z]+://",target): continue
            assert (path.parent/target).exists(),(filename,target)
            link_count+=1
    checks["reader_document_relative_links"]=link_count
    forbidden=re.compile(r"/gpfs\d*/|/home/|[A-Z]:\\Users\\|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|BEGIN (?:RSA |OPENSSH )?PRIVATE KEY|gh[pousr]_[A-Za-z0-9]{20}|github_pat_",re.I)
    for path in E.rglob("*"):
        if path.is_file():
            assert not forbidden.search(path.read_text(encoding="utf-8")),"Privacy pattern: "+str(path.relative_to(E))
            assert path.suffix.lower() not in (".wav",".pt",".pth",".ckpt",".safetensors")
    checks["known_private_path_contact_secret_patterns_absent"]=True
    print(json.dumps({"status":"PASS","checks":checks,"scope":"Integrity and document/aggregate consistency; no new experiments, bootstrap, audio authentication, or new open license."},indent=2))

if __name__=="__main__":
    main()
