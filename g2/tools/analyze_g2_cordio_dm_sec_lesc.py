#!/usr/bin/env python3
"""Fail-closed audit for the stock G2 Cordio LE Secure Connections unit."""

from __future__ import annotations

import argparse, hashlib, importlib.util, json, struct, sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
LOAD_BASE = 0x00437FE0
IMAGE_BYTES = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
READINESS_MANIFEST = ROOT / "research/readiness/dm-sec-lesc/SHA256SUMS"
READINESS_BYTES = 1_288
READINESS_SHA256 = "7d77fc0d097ac301fd436c4faa15e27af2997166c6317ac4ee8300f3b35eb05c"
PINNED_INPUTS = {
    ROOT / "tools/manifests/packetcraft-cordio-dm-sec-lesc-function-map.tsv": "9e2ddebc0387c4e381170320ac6204187d5d992df77f2eb492ffc937cee783bf",
    ROOT / "tools/manifests/packetcraft-cordio-dm-sec-lesc-provenance.tsv": "5d74e3449ddadc4b9c5c140c85a7a82198591f73333be4d09efa051823aff2e0",
    ROOT / "tools/manifests/readiness-cordio-dm-sec-lesc-build-results.tsv": "e28da4b9d4bed92d2f1ea73dc4e38d5855e581b9fdc42d4584db6453dd3a94a0",
    ROOT / "tools/manifests/readiness-cordio-dm-sec-lesc-closure-results.tsv": "d04ff9cf2032bf9da0eade43a6234eb8f3809ed74c515cf636a1be23a4d8b4c6",
    ROOT / "tools/manifests/readiness-cordio-dm-sec-lesc-r441-input-identities.tsv": "625d74e61232dcdefc27b26cc586db48ee1ada165e38474fbeaa3c4407ff663d",
    ROOT / "tools/manifests/readiness-cordio-dm-sec-lesc-source-identities.tsv": "b6effb4249d9553f8c578f90c88203d900516fc4adc650b8fb7f12c6f2e700d8",
    ROOT / "tools/manifests/readiness-cordio-dm-sec-lesc-undefined-providers.tsv": "7cb6e00b7565b7aa4ec89701d70cb239f632263abcb1bd0519ea81f354962b30",
}
FUNCTIONS = {
    "dmSecLescMsgHandler": (0x00534894,0x005348EC,"b3aab28cc4bd055dbcf5b16010b31396d3cffa3e75f2d1e337b1618fc3898b86"),
    "DmSecGenerateEccKeyReq": (0x005348EC,0x005348FC,"e0a681608fcc6948727d3aa4198b65fda3c9d016da61decd99452afceba43df2"),
    "DmSecSetEccKey": (0x005348FC,0x0053490C,"73b03a0fbb275ce3ce6b569a48a0227dc11167fbf85f82a503765328dd88a9a8"),
    "DmSecGetEccKey": (0x0053490C,0x00534910,"0ac52db61643d885328c9cb17c794144ed816950ba06f370c923b03a23632ddd"),
    "DmSecCompareRsp": (0x00534910,0x00534948,"7be991a60ff3b8ac5bb7aaaa685b6670b0775dbebfe79fafd63b82b671582ad4"),
    "DmSecGetCompareValue": (0x00534948,0x0053496A,"d63659ebcf0bb523e25b8f109164192d810161bf08c7c00b7405525585ea7f0b"),
    "DmSecLescInit": (0x0053496A,0x00534972,"b34de3b762eb032c1ed5f61a32877392a355ddeac94ae86e0f495c8a28573822"),
}
BODY_CONCAT_SHA256 = "e73da830fc5d5c6649939b48f8a2c800ac479b57c83e052e9a26f2c9dd1cf442"
PHYSICAL = (0x00534894,0x0053498C)
PHYSICAL_SHA256 = "de5c29697f858f7bb0d0b83cacb0722df7d4410e96af85b456044eedfea45eae"
TAIL = (0x00534972,0x0053498C)
TAIL_SHA256 = "1b3780cc2c27fd66045535da3608dc262538006bb4d86623974c6f1c811f0cd0"
TAIL_WORDS = [0x20073B78,0x200744F8,0x200726D0,0x000F4240,0x0078A8A4,0x20000694]
INTERFACE = (0x0078A8A4,0x0078A8B0)
INTERFACE_SHA256 = "ed14ab53083e48de966c42b4f3ca570a421921b41e002c61dec9ddcab49e85d7"
INTERFACE_WORDS = [0x004D29BF,0x004D29C1,0x00534895]
CALLERS = {
    "dmSecLescMsgHandler": [],
    "DmSecGenerateEccKeyReq": [0x004B770C,0x004B78E8,0x004B7A16],
    "DmSecSetEccKey": [0x004B7C1C],
    "DmSecGetEccKey": [0x005E2960,0x005E2972,0x005E298A],
    "DmSecCompareRsp": [0x004BB044],
    "DmSecGetCompareValue": [0x004BB036],
    "DmSecLescInit": [0x004B802A],
}
EXPECTED_STORED = {0x0078A8AC: 0x00534895}
SOURCE_ONLY = ["DmSecKeypressReq","DmSecSetOob","DmSecCalcOobReq","DmSecSetDebugEccKey"]

class AuditError(RuntimeError):
    pass

def _sha256(data: bytes) -> str: return hashlib.sha256(data).hexdigest()
def _slice(blob: bytes, start: int, end: int) -> bytes: return blob[start-LOAD_BASE:end-LOAD_BASE]
def _load_decoder():
    tools = str(ROOT / "tools")
    if tools not in sys.path: sys.path.insert(0, tools)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("dm_sec_lesc_thumb", path)
    if spec is None or spec.loader is None: raise AuditError("cannot load Thumb decoder")
    module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module; spec.loader.exec_module(module)
    return module

def analyze(image: Path = IMAGE) -> dict[str, Any]:
    if image.stat().st_size != IMAGE_BYTES: raise AuditError("official G2 image size changed")
    blob = image.read_bytes()
    if _sha256(blob) != IMAGE_SHA256: raise AuditError("official G2 image SHA-256 changed")
    if READINESS_MANIFEST.stat().st_size != READINESS_BYTES or _sha256(READINESS_MANIFEST.read_bytes()) != READINESS_SHA256: raise AuditError("Lorelei dm_sec_lesc artifact changed")
    for path, expected in PINNED_INPUTS.items():
        if _sha256(path.read_bytes()) != expected: raise AuditError(f"pinned dm_sec_lesc input changed: {path}")
    bodies = []
    for name,(start,end,expected) in FUNCTIONS.items():
        data = _slice(blob,start,end)
        if _sha256(data) != expected: raise AuditError(f"stock dm_sec_lesc body changed: {name}")
        bodies.append(data)
    if _sha256(b"".join(bodies)) != BODY_CONCAT_SHA256: raise AuditError("dm_sec_lesc body concat changed")
    if _sha256(_slice(blob,*PHYSICAL)) != PHYSICAL_SHA256: raise AuditError("dm_sec_lesc physical interval changed")
    tail = _slice(blob,*TAIL)
    if _sha256(tail) != TAIL_SHA256 or tail[:2] != b"\0\0" or list(struct.unpack("<6I",tail[2:])) != TAIL_WORDS: raise AuditError("dm_sec_lesc tail changed")
    interface = _slice(blob,*INTERFACE)
    if _sha256(interface) != INTERFACE_SHA256 or list(struct.unpack("<3I",interface)) != INTERFACE_WORDS: raise AuditError("dm_sec_lesc interface changed")
    decoder = _load_decoder(); starts = {s:n for n,(s,_,_) in FUNCTIONS.items()}; callers = {n:[] for n in FUNCTIONS}
    for address in range(LOAD_BASE,LOAD_BASE+len(blob)-3,2):
        target = decoder._thumb_bl_target(blob,address)
        if target in starts: callers[starts[target]].append(address)
    if callers != CALLERS: raise AuditError("dm_sec_lesc caller closure changed")
    entries=set(starts); interiors=set()
    for start,end,_ in FUNCTIONS.values(): interiors.update(range(start+2,end,2))
    stored={}; interior=[]
    for address in range(LOAD_BASE,LOAD_BASE+len(blob)-3,4):
        value=struct.unpack("<I",_slice(blob,address,address+4))[0]; target=value&~1
        if target in entries: stored[address]=value
        elif target in interiors: interior.append((address,value))
    if stored != EXPECTED_STORED or interior: raise AuditError("dm_sec_lesc stored/interior ingress changed")
    return {
        "schema_version":1,"image":{"path":str(image),"sha256":IMAGE_SHA256},
        "module":{"start":PHYSICAL[0],"end_exclusive":PHYSICAL[1],"physical_bytes":PHYSICAL[1]-PHYSICAL[0],"linked_function_count":len(FUNCTIONS),"linked_function_bytes":sum(e-s for s,e,_ in FUNCTIONS.values()),"source_inventory_functions":11,"source_only_functions":SOURCE_ONLY,"direct_bl_ingress_sites":sum(len(v) for v in callers.values()),"registered_function_pointers":len(stored),"strict_interior_pointers":len(interior)},
        "architecture":{"lesc_component_id":8,"message_events":[0x40,0x41],"message_ordinal_mask":7,"source_bodies_release_invariant":True},
        "abi":{"dm_cb":0x20073B78,"oob_random_pointer":0x200744F8,"local_ecc_key":0x200726D0,"local_ecc_key_bytes":96},
        "lineage":{"selected_source_interval":"Packetcraft r20.05 through r20.05c / AmbiqSuite R4.4.1","selected_blob":"a8790951d69484687728d74669888931a9aa2971","selected_sha256":"a8bd51525ec11fa7f5ea8c2aee5c76ed8885aa191cb76fcfcb54ddf72e886e8d","historical_generating_commit_resolved":False,"license":"Apache-2.0"},
        "readiness":{"archive":str(READINESS_MANIFEST),"archive_sha256":READINESS_SHA256,"compiler_profiles":2,"source_functions_built":11,"provider_seams":18,"valid_non_vacuous_closure_profiles":2,"linked_unresolved_symbols":0},
        "production":{"source_owned_bytes_added":0,"stock_bytes_replaced":0},
    }

def main() -> int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("--image",type=Path,default=IMAGE); p.add_argument("--json",action="store_true"); a=p.parse_args(); r=analyze(a.image)
    print(json.dumps(r,indent=2,sort_keys=True) if a.json else f"Cordio dm_sec_lesc closed: {r['module']['linked_function_count']} linked / {len(r['module']['source_only_functions'])} source-only")
    return 0
if __name__ == "__main__": raise SystemExit(main())
