#!/usr/bin/env python3
"""Export frozen result/protocol JSON and de-identified human records; never run experiments."""
import argparse
import csv
import hashlib
import json
import re
import shutil
from collections import Counter, defaultdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verify_manifest(root):
    rows = []
    for line in (root / "SHA256SUMS").read_text(encoding="utf-8-sig").splitlines():
        digest, name = line.split(None, 1)
        name = name.lstrip("* ")
        path = (root / name).resolve()
        if not path.is_relative_to(root.resolve()) or sha(path) != digest:
            raise ValueError("Manifest mismatch: " + name)
        rows.append(name)
    return rows

PRIVATE_PATH = re.compile(r"(?:/(?:gpfs\d*|home|root|workspace|mnt|tmp)/|[A-Za-z]:[\\/])[^\s\"'<>;,)}\]]+")
def redact(value):
    if isinstance(value, dict):
        return {k: redact(v) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    if isinstance(value, str):
        return PRIVATE_PATH.sub(lambda m: "[private-path]/" + m.group().replace("\\", "/").rstrip("/").split("/")[-1], value)
    return value

def numbers(value, path=""):
    if isinstance(value, dict):
        return {p: n for k,v in value.items() for p,n in numbers(v,path+"/"+k).items()}
    if isinstance(value, list):
        return {p: n for i,v in enumerate(value) for p,n in numbers(v,path+"/"+str(i)).items()}
    if isinstance(value,(int,float,bool)):
        return {path:value}
    return {}

def dump(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8")

def human_summary(root):
    with (root/"raw_log.csv").open(encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        assert reader.fieldnames==["listener_id","source_id","system","completion","major_error","mos"]
        rows=list(reader)
    assert len(rows)==6000
    assert len({(r["listener_id"],r["source_id"],r["system"]) for r in rows})==6000
    listeners={r["listener_id"] for r in rows}; sources={r["source_id"] for r in rows}
    assert len(listeners)==10 and all(re.fullmatch(r"L\d{2}",x) for x in listeners)
    assert len(sources)==120 and all(re.fullmatch(r"S\d{3}",x) for x in sources)
    assert set(Counter((r["source_id"],r["system"]) for r in rows).values())=={10}
    assert set(Counter((r["listener_id"],r["system"]) for r in rows).values())=={120}
    grouped=defaultdict(list)
    for r in rows:
        assert int(r["completion"]) in (0,1) and int(r["major_error"]) in (0,1) and 1<=int(r["mos"])<=5
        grouped[r["system"]].append(r)
    with (root/"platform_summary_export.csv").open(encoding="utf-8-sig",newline="") as f:
        exported={r["system"]:r for r in csv.DictReader(f)}
    result={}
    for name in ["Base","Full-SD","Random-Local","Tail-30","Tail-SD"]:
        rr=grouped[name]; n=len(rr)
        c=sum(int(r["completion"]) for r in rr)
        e=sum(int(r["major_error"]) for r in rr)
        mos=sum(int(r["mos"]) for r in rr)
        assert n==1200
        for k,v in [("n_ratings",n),("completion_count",c),("major_error_count",e),("mos_sum",mos)]:
            assert Decimal(exported[name][k])==v,(name,k)
        round_to=lambda a,d: str((Decimal(a)/Decimal(n)).quantize(Decimal(d),rounding=ROUND_HALF_UP))
        result[name]={"n_ratings":n,"completion_count":c,"major_error_count":e,"mos_sum":mos,
                      "completion_percent":round_to(c*100,"0.1"),"major_error_percent":round_to(e*100,"0.1"),
                      "mos":round_to(mos,"0.01")}
    return {"status":"DESCRIPTIVE_EXPORT_CHECKED","listeners":10,"sources":120,"systems":5,
            "records":6000,"ratings_per_system":1200,"aggregation":"pooled rating proportions / arithmetic MOS",
            "systems_summary":result,"raw_sha256":sha(root/"raw_log.csv"),
            "scope":"Original five CV3 systems; not direct validation of the new-text Random-PR comparison.",
            "verification_scope":"File integrity, complete rating grid, sums and paper rounding only; not independent verification of listening sessions or audio."}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-package",type=Path,required=True)
    parser.add_argument("--human-package",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--capability-package",type=Path,help="Optional frozen Evidence_v2 package for capability support")
    a=parser.parse_args()
    machine_names=verify_manifest(a.evidence_package)
    human_names=verify_manifest(a.human_package)
    manifest=json.loads((a.evidence_package/"MANIFEST.json").read_text(encoding="utf-8"))
    for row in manifest["files"]:
        assert sha(a.evidence_package/row["path"])==row["sha256"],row["path"]
    records=[]
    for src in sorted(a.evidence_package.rglob("*.json")):
        if src.name=="MANIFEST.json": continue
        rel=src.relative_to(a.evidence_package)
        original=json.loads(src.read_text(encoding="utf-8")); public=redact(original)
        assert numbers(original)==numbers(public)
        dst=a.output/"machine"/rel
        dump(dst,public)
        records.append({"path":dst.relative_to(a.output).as_posix(),"source_relative_path":rel.as_posix(),
                        "source_sha256":sha(src),"public_sha256":sha(dst),
                        "transformation":"JSON formatting and private absolute-path redaction only; all numeric/boolean leaves unchanged"})
    if a.capability_package:
        known={line.split(None,1)[1].lstrip('* '):line.split(None,1)[0] for line in (a.capability_package/'checksums/SHA256SUMS').read_text().splitlines()}
        for name in ['capability_summary.json','capability_gate.json']:
            rel='capability_human/'+name
            src=a.capability_package/rel
            assert sha(src)==known[rel],rel
            original=json.loads(src.read_text(encoding='utf-8')); public=redact(original)
            assert numbers(original)==numbers(public)
            dst=a.output/'capability'/name
            dump(dst,public)
            records.append({'path':dst.relative_to(a.output).as_posix(),'source_relative_path':'Evidence_v2/'+rel,
                            'source_sha256':sha(src),'public_sha256':sha(dst),'transformation':'JSON formatting and private absolute-path redaction only; numeric/boolean leaves unchanged'})
    hsummary=human_summary(a.human_package)
    for name in human_names+["SHA256SUMS"]:
        src=a.human_package/name; dst=a.output/"human"/name
        dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
        assert sha(src)==sha(dst)
        records.append({"path":dst.relative_to(a.output).as_posix(),"source_sha256":sha(src),
                        "public_sha256":sha(dst),"transformation":"byte-identical"})
    dump(a.output/"human/summary.json",hsummary)
    records.append({"path":"human/summary.json","public_sha256":sha(a.output/"human/summary.json"),
                    "transformation":"read-only aggregation consistency check; not a new inferential analysis"})
    index={"version":"2026-09-24","machine_package":"TailSD_ICASSP2027_FinalEvidence_20260918",
           "machine_checksum_entries_verified":len(machine_names),"machine_manifest_entries_verified":len(manifest["files"]),
           "human_checksum_entries_verified":len(human_names),"machine_numeric_leaves_unchanged":True,
           "files":records,"excluded_assets":["model weights","checkpoints","audio","Wikipedia reference text","participant identity/contact mapping"],
           "scope":"Frozen exported records and protocol/audit outputs, not a rerun or independent attestation of experiment execution.",
           "hash_policy":"public_sha256 verifies published bytes; source_sha256 binds the unchanged local source. Embedded historical payload hashes still refer to their original payloads.",
           "rights":"No new license is granted; see repository LICENSE_NOTICE.md."}
    dump(a.output/"index.json",index)
    entries=[p for p in a.output.rglob("*") if p.is_file() and p.name!="SHA256SUMS"]
    (a.output/"SHA256SUMS").write_text("".join(sha(p)+"  "+p.relative_to(a.output).as_posix()+"\n" for p in sorted(entries)),encoding="utf-8")
    print(json.dumps({"machine_json_files":sum(x["path"].startswith("machine/") for x in records),
                      "machine_checksums":len(machine_names),"machine_manifest":len(manifest["files"]),
                      "human_checksums":len(human_names),"human":hsummary,"files":len(records)},indent=2))

if __name__=="__main__":
    main()
