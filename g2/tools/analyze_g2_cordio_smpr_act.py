#!/usr/bin/env python3
"""Fail-closed audit for the stock G2 Cordio SMP responder actions."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x437FE0
IMAGE_BYTES = 3_523_396
IMAGE_SHA = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
MAP = ROOT / "tools/manifests/packetcraft-cordio-smpr-act-function-map.tsv"
PROVENANCE = ROOT / "tools/manifests/packetcraft-cordio-smpr-act-provenance.tsv"
PRODUCTION_SOURCE = ROOT / "components/apollo_main/core_overlay/cordio_smpr_act.c"
PRODUCTION_SOURCE_SIZE = 16_630
PRODUCTION_SOURCE_SHA256 = "f01027a9e7bc6e6af2bf4add1838cf873e1e90b6c2ee57e419e3a82f02dac5ed"
PRODUCTION_ROUTES = {
    "open_cfw_cordio_smpr_send_security_request": (181612, 42, "8145633aee9c76d6f428e85289f0eadb3bb240599d5804b897c7f63f678f8480"),
    "open_cfw_cordio_smpr_process_pair_request": (181656, 118, "78d4c842ec1ecd4d57d588f46db9b5959beb50e047aa79a073f5cc096757315a"),
    "open_cfw_cordio_smpr_send_pair_response": (181776, 166, "4de5d4afa39545e68c3972fcd2fd39fe3586c2dcfbe486cd7000c94bf8144c47"),
    "open_cfw_cordio_smpr_process_pair_confirm": (181944, 26, "50e377679eb18e4b24fbdc293216f23a8468b1e186c8b6de7589dc8fd17041a5"),
    "open_cfw_cordio_smpr_process_pair_confirm_calculate": (181972, 34, "f1ddbe8e1666bc07274b2d715e4686215f5deeb2a6a10c614c1cf1e9b32d399a"),
    "open_cfw_cordio_smpr_confirm_verify": (182008, 100, "fd6cb0e9c532e94235dc2314e474aa2106c80749bd5bc68a0a9ae7e4d47b1fb6"),
    "open_cfw_cordio_smpr_send_pair_random": (182108, 102, "58797ba463ae3ca568ddd8568954b1f17f81cd20cdfca264b98944c405feba41"),
    "open_cfw_cordio_smpr_send_key": (182212, 126, "634dda84a5dbdbc7d28ddb2a94ba4c124e1ce8f2c91dbce189a6c4f4ee7804d4"),
    "open_cfw_cordio_smpr_setup_key_distribution": (182340, 76, "94a70f8c2d58d57725803e173048ca840112c03a879990b3134e797b70c8b4b5"),
    "open_cfw_cordio_smpr_receive_key": (182416, 48, "b20a7aba419d6b88b735d8b8fb596905d7278699c7de94b5f3341735fd0c1992"),
}
PINS = {
    MAP: "5b7e323ec3578163bf269e8eb680386ccf73a2fedc30ab570099d74aec713019",
    PROVENANCE: "d2caaeb42a9b779369aa87563fd8df65d6ef5be23a0f90fe9123e454a29fa01e",
}

CALLERS = {
    "smprActSendSecurityReq": [],
    "smprActProcPairReq": [],
    "smprActSendPairRsp": [],
    "smprActProcPairCnf": [0x5E3B42],
    "smprActProcPairCnfCalc1": [],
    "smprActCnfVerify": [],
    "smprActSendPairRandom": [],
    "smprActSetupKeyDist": [],
    "smprActSendKey": [0x5E3C9C],
    "smprActRcvKey": [],
}

ACTION_TABLES = [
    (0x6D0B64, 0x6D0C40, "bbcc96d09c9c3d6842797ab8c9c61604dca828aaaf230fba8e5df96d77245718"),
    (0x6D7E7C, 0x6D7EE8, "f98a484ebaee566eda7ad88adbadd10b8e2670de97b1370e35783fea117143cc"),
]

EXPECTED_STORED_ENTRIES = [
    (0x6D0BB0, 0x5E38C9),
    (0x6D0BB4, 0x5E38F9),
    (0x6D0BB8, 0x5E3A79),
    (0x6D0BBC, 0x5E3B1D),
    (0x6D0C28, 0x5E3B3D),
    (0x6D0C2C, 0x5E3B61),
    (0x6D0C30, 0x5E3BD1),
    (0x6D0C34, 0x5E3C51),
    (0x6D0C38, 0x5E3D4D),
    (0x6D0C3C, 0x5E3CA3),
    (0x6D7EC0, 0x5E38C9),
    (0x6D7EC4, 0x5E38F9),
    (0x6D7EC8, 0x5E3A79),
    (0x6D7ECC, 0x5E3B1D),
    (0x6D7ED0, 0x5E3B3D),
    (0x6D7ED4, 0x5E3B61),
    (0x6D7ED8, 0x5E3BD1),
    (0x6D7EDC, 0x5E3C51),
    (0x6D7EE0, 0x5E3CA3),
    (0x6D7EE4, 0x5E3D4D),
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - BASE : end - BASE]


def load_decoder():
    tools_path = str(ROOT / "tools")
    if tools_path not in sys.path:
        sys.path.insert(0, tools_path)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("smpr_act_thumb", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Thumb decoder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_rows() -> list[tuple[str, int, int, str]]:
    rows = []
    with MAP.open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["stock_status"] != "linked":
                raise RuntimeError("unexpected source-only responder action")
            rows.append(
                (
                    row["function"],
                    int(row["stock_start"], 0),
                    int(row["stock_end_exclusive"], 0),
                    row["stock_sha256"],
                )
            )
    return rows


def production_report(linked: list[tuple[str, int, int, str]]) -> dict:
    source = PRODUCTION_SOURCE.read_bytes()
    if len(source) != PRODUCTION_SOURCE_SIZE or sha(source) != PRODUCTION_SOURCE_SHA256:
        raise RuntimeError("Cordio legacy responder production source identity changed")
    text = source.decode("utf-8")
    if "ccb->key_ready = 1U;" not in text or "OPEN_CFW_SMPR_SEND_PAIR_RANDOM_ONLY" not in text:
        raise RuntimeError("Cordio legacy responder r20/R4 behavior changed")
    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    leaves = {x["function"]: x for x in overlay.get("relocated_leaves", [])
              if x.get("function") in PRODUCTION_ROUTES}
    patches = {x["target_function"]: x for x in overlay.get("patch_sites", [])
               if x.get("target_function") in PRODUCTION_ROUTES}
    if set(leaves) != set(PRODUCTION_ROUTES) or set(patches) != set(PRODUCTION_ROUTES):
        raise RuntimeError("Cordio legacy responder production routing is incomplete")
    source_path = PRODUCTION_SOURCE.relative_to(ROOT).as_posix()
    stock_by_start = {start: (name, end, digest) for name, start, end, digest in linked}
    for function, (offset, size, digest) in PRODUCTION_ROUTES.items():
        leaf = leaves[function]; record = leaf.get("source", {}); patch = patches[function]
        start = patch.get("runtime_address"); stock = stock_by_start.get(start)
        if (leaf.get("profiles") != ["apple-clang"] or record.get("path") != source_path
                or record.get("size") != PRODUCTION_SOURCE_SIZE
                or record.get("sha256") != PRODUCTION_SOURCE_SHA256
                or record.get("license") != "Apache-2.0"
                or record.get("upstream_commit") != "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6"
                or leaf.get("expected", {}).get("offset") != offset
                or leaf.get("expected", {}).get("size") != size
                or leaf.get("expected", {}).get("sha256") != digest
                or leaf.get("strict_relocation_contract") is not True):
            raise RuntimeError(f"Cordio legacy responder production leaf changed: {function}")
        if (stock is None or patch.get("profiles") != ["apple-clang"]
                or patch.get("expected_size") != stock[1] - start
                or patch.get("expected_sha256") != stock[2]
                or patch.get("branch") != "b_w"):
            raise RuntimeError(f"Cordio legacy responder stock patch changed: {function}")
    return {
        "status": "production-routed authenticated Packetcraft r20.05c legacy responder actions",
        "candidate": source_path,
        "production_routed": True,
        "live_functions": len(PRODUCTION_ROUTES),
        "relocated_functions": len(PRODUCTION_ROUTES),
        "compiled_leaf_bytes": sum(route[1] for route in PRODUCTION_ROUTES.values()),
        "source_owned_bytes_added": 852,
        "stock_bytes_replaced": sum(end - start for _, start, end, _ in linked),
        "hardware_validation": (
            "blocked by unavailable authorized G2/EM9305 legacy responder pairing, "
            "confirm/random, STK handling, key distribution, retry, and interoperability physical evidence"
        ),
    }


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != IMAGE_BYTES or sha(blob) != IMAGE_SHA:
        raise RuntimeError("official image changed")
    for path, digest in PINS.items():
        if not path.is_file() or sha(path.read_bytes()) != digest:
            raise RuntimeError(f"pinned input changed: {path}")

    rows = load_rows()
    if len(rows) != 10:
        raise RuntimeError("source inventory changed")

    bodies = []
    for name, start, end, digest in rows:
        body = image_slice(blob, start, end)
        if len(body) != end - start or sha(body) != digest:
            raise RuntimeError(f"body changed: {name}")
        bodies.append(body)
    if sha(b"".join(bodies)) != "61d343559a58cb00766599071ad054ab33df207b999e43be5d4830c8cc9e6663":
        raise RuntimeError("body concatenation changed")
    if sha(image_slice(blob, 0x5E38C8, 0x5E3D7C)) != "4bf1a9f59712e18f019e3bfb7a6345b05a5def9124d334765ba8961b36c08355":
        raise RuntimeError("physical object changed")
    expected_gaps = [
        (0x5E3BC6, 0x5E3BD0, "6b3226163ef035339be479b5ff5bc3cb20acf87764a4d80c037545bf760ff517"),
        (0x5E3D2C, 0x5E3D4C, "ddb009cea80bc107019d11e26b4e5ee50938ceae1fca96f07919e910ed1f15d4"),
        (0x5E3D7A, 0x5E3D7C, "96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7"),
    ]
    for start, end, digest in expected_gaps:
        if sha(image_slice(blob, start, end)) != digest:
            raise RuntimeError(f"owned non-code range changed at {start:#x}")

    path_bytes = image_slice(blob, 0x6DE914, 0x6DE971)
    if sha(path_bytes) != "bfea2e9051b44585bf386ee838267b00da784fe8748b0f8de1c2aa451fd8b0af":
        raise RuntimeError("retained source path changed")
    path_cells = []
    for offset in range(len(blob) - 3):
        if struct.unpack_from("<I", blob, offset)[0] == 0x6DE914:
            path_cells.append(BASE + offset)
    if path_cells != [0x5E3D38]:
        raise RuntimeError("retained source-path pointer closure changed")
    if struct.unpack_from("<I", blob, 0x5E3D44 - BASE)[0] != 0x200004B8:
        raise RuntimeError("pSmpCfg literal changed")
    if struct.unpack_from("<I", blob, 0x5E3D48 - BASE)[0] != 0x20070AEC:
        raise RuntimeError("smpCb literal changed")

    # r20 added keyReady=TRUE immediately after saving/zero-padding the STK.
    if image_slice(blob, 0x5E3C16, 0x5E3C1C) != bytes.fromhex("012085f84400"):
        raise RuntimeError("r20 responder keyReady assignment changed")

    decoder = load_decoder()
    starts = {start: name for name, start, _, _ in rows}
    calls = {name: [] for name, _, _, _ in rows}
    for address in range(BASE, BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in starts:
            calls[starts[target]].append(address)
    if calls != CALLERS:
        raise RuntimeError("direct-entry call closure changed")

    for start, end, digest in ACTION_TABLES:
        if sha(image_slice(blob, start, end)) != digest:
            raise RuntimeError(f"responder action table changed at {start:#x}")

    interiors = set()
    for _, start, end, _ in rows:
        interiors.update(range(start + 2, end, 2))
    stored_entries = []
    stored_interiors = []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        target = value & ~1
        if target in starts:
            stored_entries.append((BASE + offset, value))
        elif target in interiors:
            stored_interiors.append((BASE + offset, value))
    if stored_entries != EXPECTED_STORED_ENTRIES:
        raise RuntimeError("stored entry-pointer closure changed")
    if stored_interiors:
        raise RuntimeError("stored strict-interior pointer found")

    return {
        "schema_version": 1,
        "module": {
            "start": 0x5E38C8,
            "end_exclusive": 0x5E3D7C,
            "physical_bytes": 1204,
            "linked_function_count": 10,
            "linked_function_bytes": 1160,
            "owned_noncode_bytes": 44,
            "source_inventory_functions": 10,
            "source_only_functions": [],
            "direct_bl_ingress_sites": 2,
            "external_direct_bl_ingress_sites": 0,
            "registered_function_pointers": 20,
            "strict_interior_pointers": 0,
            "decoded_outbound_bl_sites": 50,
        },
        "architecture": {
            "retained_source_path": 0x6DE914,
            "retained_source_path_pointer": 0x5E3D38,
            "smp_control_block": 0x20070AEC,
            "smp_config_pointer": 0x200004B8,
            "ccb_key_ready_offset": 0x44,
            "legacy_action_roots": 10,
            "secure_connections_action_roots": 10,
            "next_unit_entry": 0x5E3D7C,
        },
        "lineage": {
            "selected_public_oracle": "Packetcraft r20.05 through r20.05c",
            "selected_commit": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
            "selected_blob": "086a013a445e9222a367fb3eb5383beead662af2",
            "selected_sha256": "9dde00f83bdadb7445935522fad83a86a48b75be220f877ab94a9a483736ba05",
            "official_later_oracle": "AmbiqSuite R4.4.1 import at 4264b930",
            "license": "Apache-2.0",
            "independent_release_discriminator": True,
            "discriminator": "stock writes smpCcb.keyReady at +0x44; r19/AmbiqSuite 2.x lacks that assignment",
            "historical_generating_commit_resolved": False,
        },
        "production": production_report(rows),
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
        print("Cordio smpr_act closed: 10/10 linked; 20 table roots; r20 keyReady path")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
