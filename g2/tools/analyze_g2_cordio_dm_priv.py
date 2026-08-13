#!/usr/bin/env python3
"""Fail-closed audit for the stock G2 Cordio privacy manager."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import struct
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
LOAD_BASE = 0x00437FE0
IMAGE_BYTES = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
READINESS_MANIFEST = ROOT / "research/readiness/dm-priv/SHA256SUMS"
READINESS_BYTES = 1_288
READINESS_SHA256 = "7abd169dd71d2d56090ddc3e202dcbb193146e9a7851e40633f66779b096eca4"
PINNED_INPUTS = {
    ROOT / "tools/manifests/packetcraft-cordio-dm-priv-function-map.tsv": "1f7c994323fcf72ebb28a36098072f47c94e9660557d973dbd983862b6a402e7",
    ROOT / "tools/manifests/packetcraft-cordio-dm-priv-provenance.tsv": "74e83c609de0c33e178c548c440a3dad77a2e47edec1e8e5968cdb413b8af127",
    ROOT / "tools/manifests/readiness-cordio-dm-priv-build-results.tsv": "150ebb16389f07b1680413abe22ab93adb994da075e202d147fedb4e3da89426",
    ROOT / "tools/manifests/readiness-cordio-dm-priv-closure-results.tsv": "f6c35789ee9172dae6d3ba4d4140186eaee874da0e5f9e915cfb73da3b0aa87a",
    ROOT / "tools/manifests/readiness-cordio-dm-priv-include-closure.tsv": "ea8bcb81209e4d23f43898615af173d5e2fca3f050368780e6e6a49e2dc1a65d",
    ROOT / "tools/manifests/readiness-cordio-dm-priv-r441-input-identities.tsv": "c46abba49789032d571304d88f8cdd4abbb973745cbb5dfa124d68e4e143833f",
    ROOT / "tools/manifests/readiness-cordio-dm-priv-source-identities.tsv": "b3ccecaac4f62096e0de25905cb2d4f076e5b6702381c2de0cad2e8c14f42219",
    ROOT / "tools/manifests/readiness-cordio-dm-priv-undefined-providers.tsv": "c916ed96b9e7ac46bb19352b07373a84ade3d51fd9d7c0a9d2b8caa7697712d8",
}

FUNCTIONS = {
    "dmPrivActResolveAddr": (0x004D254C,0x004D25BA,"58c2f189974ee9293da1f0ab264af4dcdd782952a2b2a6daee76446ad833c139"),
    "dmPrivAesActResAddrAesCmpl": (0x004D25BA,0x004D25F2,"edb50d8f35f4f656f3e05595ac05c7355233cd3a2446cd12198a6623a2c832b2"),
    "dmPrivActAddDevToResList": (0x004D25F2,0x004D2616,"55d27fc254b3be5bcf226acec0d1b3205b98259b51eac1e57087c75bb532f123"),
    "dmPrivActRemDevFromResList": (0x004D2616,0x004D262C,"b911c36e8f1dc6af78eb7d59439044c94a08cba84ae54aec27fc078fc490203e"),
    "dmPrivActClearResList": (0x004D262C,0x004D2634,"314424ed8146bb2ea4ba2cc9b0a103ddfd0f4ca0f3be870ea50549c76fc5e407"),
    "dmPrivActSetAddrResEnable": (0x004D2634,0x004D263E,"39b50c99d12b898d44bfde60e27306eac16b948d4242ed8e8e303db3428b4680"),
    "dmPrivActSetPrivacyMode": (0x004D263E,0x004D264C,"b243826e87009968c943bf9ec401ce391c7d091ce136f52ecbce6f997b475841"),
    "dmPrivActGenAddr": (0x004D264C,0x004D26AC,"9d523582ef60bc24f8f2e298b4128d66a5fa096ea5103bee79b67913dd991b43"),
    "dmPrivAesActGenAddrAesCmpl": (0x004D26AC,0x004D26E8,"4a082cbd709d25c36f6fb0849e72afa2dd7937e0fe0c39adea52a2b186c1db30"),
    "dmPrivHciHandler": (0x004D26E8,0x004D27A0,"f73e84caa9d33689116ff20642a69d1285afca352d184798fd7b29f8a25b43f5"),
    "dmPrivSetAddrResEnable": (0x004D27A0,0x004D27AE,"9ba5ab091b59142afe99d1f11572f4d04453f4cdefd51154bcf0c58bf06c3871"),
    "dmPrivMsgHandler": (0x004D27AE,0x004D27C0,"34aba8e55549136f12db3abd31f7f0cc0461b52f8c521137faf82421ecd23a84"),
    "dmPrivReset": (0x004D27C0,0x004D27CE,"24bf9e97ee263308ead811e75df8d3c5907c60c3d89da1002f8a0de082b68a87"),
    "dmPrivAesMsgHandler": (0x004D27CE,0x004D27E0,"a2031e99f1faff651aa9478f2d8647e5cc2b6b69fb5c381185c365ee9b3ca008"),
    "DmPrivInit": (0x004D27E0,0x004D27F6,"31fd63b3efba40b80325bb073009d1d6eca6c5fa5d03d5ae345d472fcce14c77"),
    "DmPrivResolveAddr": (0x004D27F6,0x004D282E,"fe8340abeb33b9a03f4a6e025ffbb4097205f82fdbd9cea5fe221e368dbda953"),
    "DmPrivAddDevToResList": (0x004D282E,0x004D2880,"01c08bc91310bab9acafca11926082f0365790f0881ea5e919e62da392e2bce7"),
    "DmPrivRemDevFromResList": (0x004D2880,0x004D28B0,"725e3d9eecfcdb860a60a0a2b1fa74cdf279fcfdf31096edd0fb7193597d3f75"),
    "DmPrivClearResList": (0x004D28B0,0x004D28CC,"7e39268f87a3a322a4b03fcc831bcb56f77ab089dcbad2617eb75ee6d961987c"),
    "DmPrivSetAddrResEnable": (0x004D28CC,0x004D28F0,"02442ee8e8d7389f2e2d13fe4a2a8c72ee7527cfb1b1fcd785d24b738acb5105"),
    "DmPrivSetPrivacyMode": (0x004D28F0,0x004D2920,"3d0dd38186a46afd7883d16a58232a8ec53fb533245143c5445a991067dd3973"),
}
BODY_CONCAT_SHA256 = "bc451db75e61a0c8eea314a9652ab33f3817395413bcc868e693ddde8cec3a9b"
PHYSICAL = (0x004D254C, 0x004D293C)
PHYSICAL_SHA256 = "749b2dab02c3e494d31a9c5b09da54bb026f13f698a0ad16d0971a4d41c22509"
POOL = (0x004D2920, 0x004D293C)
POOL_SHA256 = "aafcbe1dbb9208889a7e9279e05943585e6ce72f68e13ed1c09eb0918226c4eb"
POOL_WORDS = [0x20073A58,0x20073B78,0x0076AF6C,0x0078D454,0x20000694,0x0078A868,0x0078A874]

TABLES = {
    (0x0076AF6C,0x0076AF88): ("cc0a59500ccf4bb1ca931d4ee0a65a3baf810bca499b899fd8d11721364fe12c", [0x004D254D,0x004D25F3,0x004D2617,0x004D262D,0x004D2635,0x004D263F,0x004D264D]),
    (0x0078D454,0x0078D45C): ("0b4418241c4a15ed8eb3f5cdca2585b5cd114465eaa91ca5e0933e9c7f1799ba", [0x004D25BB,0x004D26AD]),
    (0x0078A868,0x0078A874): ("0a828f9f2f60975a2bfcd05cfab0165ef8345846053d2eb4e4ae7de5bf5ddb2d", [0x004D27C1,0x004D26E9,0x004D27AF]),
    (0x0078A874,0x0078A880): ("92413ce5091a3431cfd9a81ad3214a19228dae374292f6a84a063c79c00d809a", [0x004D29BF,0x004D29C1,0x004D27CF]),
}
CALLERS = {
    "dmPrivActResolveAddr": [], "dmPrivAesActResAddrAesCmpl": [],
    "dmPrivActAddDevToResList": [], "dmPrivActRemDevFromResList": [],
    "dmPrivActClearResList": [], "dmPrivActSetAddrResEnable": [],
    "dmPrivActSetPrivacyMode": [], "dmPrivActGenAddr": [],
    "dmPrivAesActGenAddrAesCmpl": [], "dmPrivHciHandler": [],
    "dmPrivSetAddrResEnable": [0x004D2638,0x004D2726,0x004D2754],
    "dmPrivMsgHandler": [], "dmPrivReset": [], "dmPrivAesMsgHandler": [],
    "DmPrivInit": [0x004B802E],
    "DmPrivResolveAddr": [0x0047AA26,0x004B36A4,0x004B38C4,0x0050403C,0x0050404E,0x00504098,0x005040A4],
    "DmPrivAddDevToResList": [0x0047950A,0x004BB20A],
    "DmPrivRemDevFromResList": [0x0047A7AC,0x0047B648],
    "DmPrivClearResList": [0x0047B51A,0x004B46D4],
    "DmPrivSetAddrResEnable": [0x00479524],
    "DmPrivSetPrivacyMode": [0x004BB24E],
}
EXPECTED_STORED = {
    0x0076AF6C:0x004D254D,0x0076AF70:0x004D25F3,0x0076AF74:0x004D2617,
    0x0076AF78:0x004D262D,0x0076AF7C:0x004D2635,0x0076AF80:0x004D263F,
    0x0076AF84:0x004D264D,0x0078D454:0x004D25BB,0x0078D458:0x004D26AD,
    0x0078A868:0x004D27C1,0x0078A86C:0x004D26E9,0x0078A870:0x004D27AF,
    0x0078A87C:0x004D27CF,
}
SOURCE_ONLY = ["DmPrivReadPeerResolvableAddr","DmPrivReadLocalResolvableAddr","DmPrivSetResolvablePrivateAddrTimeout","DmPrivGenerateAddr"]


class AuditError(RuntimeError):
    """Raised when authenticated DM-privacy evidence changes."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - LOAD_BASE:end - LOAD_BASE]


def _load_decoder():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("dm_priv_thumb", path)
    if spec is None or spec.loader is None:
        raise AuditError("cannot load Thumb decoder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def analyze(image: Path = IMAGE) -> dict[str, Any]:
    if image.stat().st_size != IMAGE_BYTES:
        raise AuditError("official G2 image size changed")
    blob = image.read_bytes()
    if _sha256(blob) != IMAGE_SHA256:
        raise AuditError("official G2 image SHA-256 changed")
    if READINESS_MANIFEST.stat().st_size != READINESS_BYTES or _sha256(READINESS_MANIFEST.read_bytes()) != READINESS_SHA256:
        raise AuditError("Lorelei dm_priv readiness artifact changed")
    for path, expected in PINNED_INPUTS.items():
        if _sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned dm_priv input changed: {path}")

    bodies = []
    for name, (start, end, expected) in FUNCTIONS.items():
        data = _slice(blob, start, end)
        if _sha256(data) != expected:
            raise AuditError(f"stock dm_priv body changed: {name}")
        bodies.append(data)
    if _sha256(b"".join(bodies)) != BODY_CONCAT_SHA256:
        raise AuditError("dm_priv body concatenation changed")
    if _sha256(_slice(blob, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("dm_priv physical interval changed")
    pool = _slice(blob, *POOL)
    if _sha256(pool) != POOL_SHA256 or list(struct.unpack("<7I", pool)) != POOL_WORDS:
        raise AuditError("dm_priv literal pool changed")

    table_values = {}
    for bounds, (expected_hash, expected_values) in TABLES.items():
        data = _slice(blob, *bounds)
        values = list(struct.unpack(f"<{len(data)//4}I", data))
        if _sha256(data) != expected_hash or values != expected_values:
            raise AuditError(f"dm_priv table changed at 0x{bounds[0]:08x}")
        table_values[f"0x{bounds[0]:08x}"] = values

    decoder = _load_decoder()
    starts = {start: name for name, (start, _, _) in FUNCTIONS.items()}
    callers = {name: [] for name in FUNCTIONS}
    for address in range(LOAD_BASE, LOAD_BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in starts:
            callers[starts[target]].append(address)
    if callers != CALLERS:
        raise AuditError("dm_priv direct caller closure changed")

    entries = set(starts)
    interiors = set()
    for start, end, _ in FUNCTIONS.values():
        interiors.update(range(start + 2, end, 2))
    stored = {}
    interior_pointers = []
    for address in range(LOAD_BASE, LOAD_BASE + len(blob) - 3, 4):
        value = struct.unpack("<I", _slice(blob, address, address + 4))[0]
        target = value & ~1
        if target in entries:
            stored[address] = value
        elif target in interiors:
            interior_pointers.append((address, value))
    if stored != EXPECTED_STORED or interior_pointers:
        raise AuditError("dm_priv stored entry/interior pointer closure changed")

    return {
        "schema_version": 1,
        "image": {"path": str(image), "sha256": IMAGE_SHA256},
        "module": {
            "start": PHYSICAL[0], "end_exclusive": PHYSICAL[1],
            "physical_bytes": PHYSICAL[1] - PHYSICAL[0],
            "linked_function_count": len(FUNCTIONS),
            "linked_function_bytes": sum(end-start for start,end,_ in FUNCTIONS.values()),
            "source_inventory_functions": 25, "source_only_functions": SOURCE_ONLY,
            "direct_bl_ingress_sites": sum(len(v) for v in callers.values()),
            "registered_function_pointers": len(stored),
            "strict_interior_pointers": len(interior_pointers),
        },
        "architecture": {
            "privacy_component_id": 6, "privacy_aes_component_id": 15,
            "main_action_count": 7, "aes_action_count": 2,
            "main_events": [0x30,0x31,0x32,0x33,0x34,0x35,0x36],
            "aes_events": [0x78,0x79], "message_ordinal_mask": 7,
            "task_locked_dual_interface_install": True,
        },
        "abi": {
            "dm_priv_cb": 0x20073A58, "dm_priv_cb_bytes": 0x1A,
            "dm_cb": 0x20073B78, "hash_bytes": 3, "prand_bytes": 3,
            "aes_bytes": 16,
        },
        "lineage": {
            "selected_source_interval": "Packetcraft r20.05 through r20.05c / AmbiqSuite R4.4.1",
            "selected_blob": "45966dc6bfcf77162b37695ba821eff78c1c551c",
            "selected_sha256": "13f285c4bf2d03744cd7f2665e465ed03f33491fd88cec001a303a04334b24ac",
            "historical_generating_commit_resolved": False, "license": "Apache-2.0",
        },
        "readiness": {
            "archive": str(READINESS_MANIFEST), "archive_sha256": READINESS_SHA256,
            "compiler_profiles": 2, "source_functions_built": 25,
            "provider_seams": 24, "valid_non_vacuous_closure_profiles": 2,
            "linked_unresolved_symbols": 0,
        },
        "production": {"source_owned_bytes_added": 0, "stock_bytes_replaced": 0},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, default=IMAGE)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = analyze(args.image)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        module = report["module"]
        print(f"Cordio dm_priv closed: {module['linked_function_count']} linked / {len(module['source_only_functions'])} source-only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
