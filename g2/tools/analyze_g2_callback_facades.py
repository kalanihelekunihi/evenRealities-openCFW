#!/usr/bin/env python3
"""Fail-closed audits for the G2 charge and message callback facades."""

import csv
import hashlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
from apollo_artifact_consistency import validate_apollo_main_artifacts

IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM = ROOT / "tools/manifests/g2-callback-facades-function-map.tsv"
CL = ROOT / "tools/manifests/g2-callback-facades-closure.tsv"
PM = ROOT / "tools/manifests/g2-callback-facades-provider-map.tsv"
PROD_PROVENANCE = ROOT / "tools/manifests/g2-callback-facades-provenance.tsv"
PINS = {
    FM: "4d11d389f901edf623b62617276d92c841958700afa5cd16a4582a4054c40d7b",
    CL: "04952e059d1ba61d04bb7201f522ed3c256c3e92c1a27511138eaf3f6ee5d63f",
    PM: "a8ca5915dd36070f0d2c0556b2529b40cf1ab3c5a57a3c20deed43c1defd47c2",
    PROD_PROVENANCE: "66eef42f979123f22ebadea62af73d18c79ea5a4d7610d98e7c4ccec8d3b74bb",
}
SOURCE = ROOT / "components/apollo_main/core_overlay/callback_facades.c"
SOURCE_PATH = "components/apollo_main/core_overlay/callback_facades.c"
SOURCE_PIN = (4936, "bf72af23a2b7d6ce22fac7f9c11eca909133e6ef541b75e122fa61dfdbdfb9c5")
LEAF_NAMES = (
    "open_cfw_cb_charge_init", "open_cfw_cb_charge_deinit",
    "open_cfw_cb_charge_register", "open_cfw_cb_charge_unregister",
    "open_cfw_cb_charge_notify", "open_cfw_cb_msg_init",
    "open_cfw_cb_msg_deinit", "open_cfw_cb_msg_register",
    "open_cfw_cb_msg_unregister", "open_cfw_cb_msg_notify",
)
LEAF_DIGEST = "ce47ce4a560f9c4046d1982d5d9fec7f1431efabda1bbdb93248d991ba209324"
PATCH_DIGEST = "f383e040a7e15e42df5431ad688455c6cce2440f81f4908261eaaab46fb87ae8"
BUILT_DIGEST = "3a3f4a5d64b24c179cebab0d9a046555efa65dda940fd3c63de88a1291ad5199"
REGION_DIGEST = "f24da68c16f4a3d1d9f29199baf1f4c3f25e707a57bd3dd32d43c5aed6556da3"
EASY = {0x43CE9E, 0x43D0CE, 0x43D574}
CALLBACK = {0x510108, 0x5101AE, 0x510240, 0x5103C4, 0x5105BC}
TARGET_COUNTS = {
    0x43CE9E: 2, 0x43D0CE: 6, 0x43D574: 2,
    0x510108: 1, 0x5101AE: 1, 0x510240: 1,
    0x5103C4: 1, 0x5105BC: 1,
}
MODULES = {
    "charge": {
        "path": r"platform\service\callback_mgr\cb_charge.c",
        "functions": ((0x4AEA40, 0x4AEA4C), (0x4AEA4C, 0x4AEA56),
                      (0x4AEA56, 0x4AEAA4), (0x4AEAA4, 0x4AEAF0),
                      (0x4AEAF0, 0x4AEAFE)),
        "physical": (0x4AEA40, 0x4AEB20), "pool": (0x4AEAFE, 0x4AEB20),
        "body_sha": "c5a5970f443c148f7fe7c51aa66676325a6978974f8bd196cc65f44f7c67d65a",
        "physical_sha": "bdaa0638fc92b8cb84fc8853137538fa9b0a486af7167fa285fc54f2253a1189",
        "pool_sha": "4dd99a216ee516fc862a6ae7a2d5f42ec3dabbe1e473bd4753736517a76fe6e9",
        "instruction_digest": "4db06912003adf8ce3003d9a4cbf8a0940dff6aeb045a4b04b7c567dd059df3e",
        "call_digest": "de5e4955b6ae5c474d3c966d4fd2093a77769df614f943e495faf2496a5e30a0",
        "entry_digest": "36e06e5d81f03934a7df887aaace72793cd5c104d7d1708fc788e936336d26de",
        "entries": [(0x46BE5A,0x4AEA56),(0x49E730,0x4AEA56),(0x49E9E0,0x4AEAA4),
                    (0x4AD066,0x4AEA40),(0x4AD0C4,0x4AEA4C),
                    (0x4AD292,0x4AEAF0),(0x4AD454,0x4AEAF0)],
        "path_cell": 0x4AEB10, "path_refs": [0x4AEA70, 0x4AEABE],
        "list": 0x20073F78, "type": "BAT_INFO",
        "before_sha": "9478fc16a8b63900098e98eb2c8fbf806c18d1cc4f3d485eebcc074bb0bf6ef3",
        "after_sha": "28c8ce6eeb627d148f766ce6b52acc06cc37709f0743609a23bcef82bb1074b5",
        "strings": {0x4AEB00:"BAT_INFO",0x4AEB08:"Invalid callback function",
                    0x4AEB0C:"CB_CHG_RegisterBatInfoCallback",
                    0x4AEB10:r"D:\01_workspace\s200_ap510b_iar_git\platform\service\callback_mgr\cb_charge.c",
                    0x4AEB14:"cb.charge",0x4AEB18:"[cb.charge]Invalid callback function",
                    0x4AEB1C:"CB_CHG_UnregisterBatInfoCallback"},
    },
    "msg_notif": {
        "path": r"platform\service\callback_mgr\cb_msg_notif.c",
        "functions": ((0x4E1A48, 0x4E1A54), (0x4E1A54, 0x4E1A5E),
                      (0x4E1A5E, 0x4E1AAC), (0x4E1AAC, 0x4E1AF8),
                      (0x4E1AF8, 0x4E1B06)),
        "physical": (0x4E1A48, 0x4E1B28), "pool": (0x4E1B06, 0x4E1B28),
        "body_sha": "9da6e9e819095403295e77b9fa356fb3e6469a655a183314c104ceaf78f1c3e5",
        "physical_sha": "6f2d7ba1abfd285b34ef101c857ba0687eca83a1e18a580bcd0bc2060383ab77",
        "pool_sha": "46055b78c37ca551168e825606c6756372720c76b6e8f9b7311f0cc97bf131fe",
        "instruction_digest": "a00ca7dc3e9739e4e4f321811b745008ed7f62b1a03deafa301c2bcb351c6396",
        "call_digest": "60f8b93ade1bdec2e0c50cc660b651bb5a13a66e0b58f615dd1c85be7935ce5e",
        "entry_digest": "1e38353110532d72368150abf4b3dccf18e4e1401070a9e7bbe79815335467a9",
        "entries": [(0x497398,0x4E1A48),(0x4973EE,0x4E1A54),(0x4974CE,0x4E1AF8),
                    (0x4977C8,0x4E1AF8),(0x49792A,0x4E1AF8),
                    (0x49E728,0x4E1A5E),(0x49E9DA,0x4E1AAC)],
        "path_cell": 0x4E1B18, "path_refs": [0x4E1A78, 0x4E1AC6],
        "list": 0x20073F84, "type": "MSG_COUNT",
        "before_sha": "73acba294f22cc5269e99502955ac114341ab82f2bf2c6c643ff7f94932949c2",
        "after_sha": "8a7d4fce61b0aaff929f5a64e7b8d32fb109cd1171ed604260cd532830fb5d56",
        "strings": {0x4E1B08:"MSG_COUNT",0x4E1B10:"Invalid callback function",
                    0x4E1B14:"CB_ANCC_RegisterMsgCountCallback",
                    0x4E1B18:r"D:\01_workspace\s200_ap510b_iar_git\platform\service\callback_mgr\cb_msg_notif.c",
                    0x4E1B1C:"cb.msg_notif",0x4E1B20:"[cb.msg_notif]Invalid callback function",
                    0x4E1B24:"CB_ANCC_UnregisterMsgCountCallback"},
    },
}


def sh(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def jsh(value: object) -> str:
    return sh(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def cstring(blob: bytes, address: int) -> str:
    offset = address - c.BASE
    end = blob.find(b"\0", offset)
    if offset < 0 or end < 0:
        raise c.AuditError("unterminated string")
    return blob[offset:end].decode("ascii")


def analyze(image: Path = IMAGE) -> dict:
    blob = image.read_bytes()
    if len(blob) != c.IMAGE_SIZE or sh(blob) != c.IMAGE_SHA256:
        raise c.AuditError("image changed")
    for path, expected in PINS.items():
        if sh(path.read_bytes()) != expected:
            raise c.AuditError(f"manifest changed: {path.name}")
    easy = json.loads((ROOT / "third_party/easylogger/PROVENANCE.json").read_text())
    if easy["upstream"]["selected_commit"] != "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":
        raise c.AuditError("EasyLogger source selection changed")
    with FM.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 10:
        raise c.AuditError("function inventory changed")

    reports = {}
    for name, spec in MODULES.items():
        module_rows = [row for row in rows if row["module"] == name]
        if len(module_rows) != 5:
            raise c.AuditError("module inventory changed")
        starts, interiors, instructions = set(), set(), {}
        body, calls, indirect, anchored = b"", [], [], 0
        for row, bounds in zip(module_rows, spec["functions"]):
            start, end = int(row["stock_start"], 0), int(row["stock_end_exclusive"], 0)
            raw = c._slice(blob, start, end)
            if (start, end) != bounds or len(raw) != int(row["stock_bytes"]) or sh(raw) != row["stock_sha256"]:
                raise c.AuditError(f"{name} function changed")
            decoded, direct, dynamic = q._recover_function(blob, start, end)
            if c._uncovered(bounds, decoded):
                raise c.AuditError(f"{name} function has uncovered bytes")
            starts.add(start); interiors.update(range(start + 2, end, 2))
            instructions.update(decoded); body += raw; calls.extend(direct); indirect.extend(dynamic)
            anchored += row["source_path_anchor"] == "yes"
        calls.sort()
        code = b"".join(c._slice(blob, address, address + item.size) for address, item in sorted(instructions.items()))
        if anchored != 2 or len(body) != 190 or code != body or sh(body) != spec["body_sha"]:
            raise c.AuditError(f"{name} body closure changed")
        if len(instructions) != 78 or c._instruction_digest(sorted((a, i.size) for a, i in instructions.items())) != spec["instruction_digest"] or indirect:
            raise c.AuditError(f"{name} instruction closure changed")
        if sh(c._slice(blob, *spec["physical"])) != spec["physical_sha"] or sh(c._slice(blob, *spec["pool"])) != spec["pool_sha"]:
            raise c.AuditError(f"{name} physical object changed")
        start, end = spec["physical"]
        if sh(c._slice(blob, start - 16, start)) != spec["before_sha"] or sh(c._slice(blob, end, end + 16)) != spec["after_sha"]:
            raise c.AuditError(f"{name} boundary changed")

        external = Counter(target for _, target in calls)
        if len(calls) != 15 or c._pair_digest(calls) != spec["call_digest"] or external != Counter(TARGET_COUNTS):
            raise c.AuditError(f"{name} call topology changed")
        entries, strict = [], []
        for address in range(c.BASE, c.BASE + len(blob) - 3, 2):
            target = t._thumb_bl_target(blob, address)
            if target in starts: entries.append((address, target))
            elif target in interiors: strict.append((address, target))
        if entries != spec["entries"] or c._pair_digest(entries) != spec["entry_digest"] or strict:
            raise c.AuditError(f"{name} entry topology changed")
        encoded = starts | {item | 1 for item in starts}
        if any(struct.unpack_from("<I", blob, offset)[0] in encoded for offset in range(len(blob) - 3)):
            raise c.AuditError(f"{name} unexpected stored entry")
        if t.literal_references(blob, spec["path_cell"]) != spec["path_refs"]:
            raise c.AuditError(f"{name} path references changed")
        if struct.unpack("<I", c._slice(blob, spec["pool"][0] + 6, spec["pool"][0] + 10))[0] != spec["list"]:
            raise c.AuditError(f"{name} callback-list address changed")
        for pool_address, expected in spec["strings"].items():
            target = struct.unpack("<I", c._slice(blob, pool_address, pool_address + 4))[0]
            if cstring(blob, target) != expected:
                raise c.AuditError(f"{name} string changed")
        reports[name] = {
            "retained_path": spec["path"], "linked_functions": 5,
            "ghidra_discovered_functions": 2, "restored_functions": 3,
            "path_anchored_functions": 2, "body_bytes": 190,
            "physical_bytes": 224, "outer_pool_and_alignment_bytes": 34,
            "reachable_instructions": 78, "direct_body_calls": 15,
            "direct_bl_entry_sites": 7, "indirect_body_calls": 0,
            "stored_entry_pointers": 0, "callback_list_address": spec["list"],
            "callback_type": spec["type"], "easylogger_calls": 10,
            "generic_callback_manager_calls": 5,
            "direct_cmsis_freertos_calls": 0,
            "embedded_third_party_definitions": [],
        }

    source = SOURCE.read_bytes()
    if (len(source), sh(source)) != SOURCE_PIN:
        raise c.AuditError("callback-facade production source changed")
    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    leaves = [leaf for leaf in overlay["relocated_leaves"]
              if leaf.get("source", {}).get("path") == SOURCE_PATH]
    if tuple(leaf.get("function") for leaf in leaves) != LEAF_NAMES or \
            jsh(leaves) != LEAF_DIGEST or not set(LEAF_NAMES) <= set(overlay["functions"]):
        raise c.AuditError("callback-facade leaf closure changed")
    if any(leaf.get("profiles") != ["apple-clang"] or
           not leaf.get("strict_relocation_contract") or
           leaf.get("source", {}).get("license") != "MIT"
           for leaf in leaves):
        raise c.AuditError("callback-facade leaf policy changed")
    if sum(leaf["expected"]["size"] for leaf in leaves) != 208 or \
            sum(len(leaf["relocations"]) for leaf in leaves) != 10:
        raise c.AuditError("callback-facade compiled census changed")
    previous = 192852
    alignment = 0
    for leaf in leaves:
        alignment += leaf["expected"]["offset"] - previous
        previous = leaf["expected"]["offset"] + leaf["expected"]["size"]
    if alignment != 6 or previous != 193066:
        raise c.AuditError("callback-facade placement changed")
    patches = [patch for patch in overlay["patch_sites"]
               if patch.get("target_function") in set(LEAF_NAMES)]
    if len(patches) != 10 or jsh(patches) != PATCH_DIGEST or \
            sum(patch["expected_size"] for patch in patches) != 380:
        raise c.AuditError("callback-facade redirect closure changed")
    build = json.loads((ROOT / "components/apollo_main/core_overlay/build/build-report.json").read_text())
    validate_apollo_main_artifacts(ROOT, c.AuditError, "callback facades")
    built = [leaf for leaf in build["relocated_leaves"]
             if leaf.get("source", {}).get("path") == SOURCE_PATH]
    normalized = [{"function": leaf["extraction"]["function"],
                   "size": leaf["placement"]["size"],
                   "padding_before": leaf["placement"]["padding_before"],
                   "offset": leaf["placement"]["offset"],
                   "runtime_address": leaf["placement"]["runtime_address"],
                   "relocation_count": leaf["extraction"]["relocation_count"]}
                  for leaf in built]
    if len(built) != 10 or jsh(normalized) != BUILT_DIGEST:
        raise c.AuditError("callback-facade built closure changed")
    manifest = json.loads((ROOT / "manifests/g2-2.2.6.10-core-source.json").read_text())
    main = manifest["component_overrides"]["apollo_main"]
    region_names = {name for name in (
        "opaque_cb_charge_literal_pool", "opaque_cb_msg_notif_literal_pool")}
    region_names |= {region["name"] for region in main["regions"]
                     if region["name"].startswith("cb_charge_") or
                     region["name"].startswith("cb_msg_")}
    regions = [region for region in main["regions"] if region["name"] in region_names]
    if len(regions) != 25 or jsh(regions) != REGION_DIGEST:
        raise c.AuditError("callback-facade manifest regions changed")
    return {
        "schema_version": 1,
        "analysis_mode": "read-only raw-image closure; corpus-independent",
        "identity": {"image_sha256": c.IMAGE_SHA256, "embedded_third_party_definitions": []},
        "modules": reports,
        "aggregate": {
            "linked_functions": 10, "restored_functions": 6,
            "body_bytes": 380, "physical_bytes": 448,
            "direct_body_calls": 30, "easylogger_calls": 20,
            "generic_callback_manager_calls": 10,
            "direct_cmsis_freertos_calls": 0,
            "easylogger_commit": "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24",
            "new_version_discriminator": False,
            "private_generating_commit_recoverable": False,
        },
        "production": {
            "production_routed": True,
            "candidate": SOURCE_PATH,
            "source_functions": 10,
            "compiled_text_bytes": 208,
            "alignment_bytes": 6,
            "stock_replaced_bytes": 380,
            "strict_relocations": 10,
            "retained_literal_pool_bytes": 68,
            "software_functional_gap": False,
            "hardware_validation": "blocked by unavailable physical evidence",
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
