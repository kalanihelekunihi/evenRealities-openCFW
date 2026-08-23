#!/usr/bin/env python3
"""Fail-closed audit for the stock G2 Cordio SMP common action unit."""

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
MAP = ROOT / "tools/manifests/packetcraft-cordio-smp-act-function-map.tsv"
PRODUCTION_SOURCE = ROOT / "components/apollo_main/core_overlay/cordio_smp_act.c"
PRODUCTION_SOURCE_SIZE = 35_811
PRODUCTION_SOURCE_SHA256 = "f73e9d76970e3e66009d82c75bf07b3e2c8a2c1602ad76f52af024af40014bde"
PRODUCTION_ROUTES = {
    "open_cfw_cordio_smp_act_start_response_timer": (173040, 12, "b39277ff5cd7503b1bc3849a1f89b90195d7b8230f63280e6babb64294fbab3e", "smpStartRspTimer"),
    "open_cfw_cordio_smp_act_cleanup_core": (173052, 60, "b0c30725d332ddba00e98be6c69828f47a667502d10b63c8bb4f4b5f9fdc0a45", "smpCleanup"),
    "open_cfw_cordio_smp_act_cleanup": (173112, 4, "9f55df6d28ca20571e0a8c6a8466f4ccbc476981a4304d8a74cc612327f1c457", "smpActCleanup"),
    "open_cfw_cordio_smp_act_send_pairing_failed": (173116, 36, "0174621055070c9d8aa5a5157c05c49b7680bd719823bb790aaedcae874390ae", "smpSendPairingFailed"),
    "open_cfw_cordio_smp_act_pairing_failed": (173152, 36, "606a8d1ce6c1589d95710f338554a5945d277ec66c621619db0c048834e0bda1", "smpActPairingFailed"),
    "open_cfw_cordio_smp_act_security_request_timeout": (173188, 44, "d6bb9176064f114c6399ec3a3916d6485c90f01b282c32521aad7e2c77a73370", "smpActSecReqTimeout"),
    "open_cfw_cordio_smp_act_pairing_cancel": (173232, 24, "21c69b6ea8a4387a94a06d02a78e31a43a3ee43a0779b73765ddccda631b7fb1", "smpActPairingCancel"),
    "open_cfw_cordio_smp_act_store_pin": (173256, 38, "434ebcc198391963563042b68a7f22f4b2bae0a638c9e16b603de5637a8ecc98", "smpActStorePin"),
    "open_cfw_cordio_smp_act_process_pairing": (173296, 280, "456a494d54745fa33d3d1f600bdbababd2eba827adedaae92be4efcf596867a0", "smpProcPairing"),
    "open_cfw_cordio_smp_act_authentication_request": (173576, 78, "b1fc7fe7ed61bad2fdf99e13dc7c296977dfc8294a0f363b7c35b7f296a19400", "smpAuthReq"),
    "open_cfw_cordio_smp_act_confirm_calculate_one": (173656, 34, "4dd0fb4317168280d6ef4f3f74cf0ac01fe867e5c51c975201e9f2179a265641", "smpActPairCnfCalc1"),
    "open_cfw_cordio_smp_act_confirm_calculate_two": (173692, 10, "38a3507b6f65ecd797f69f4523df2f80e058e6bdf5d8dffa28ee18f60a6d7ada", "smpActPairCnfCalc2"),
    "open_cfw_cordio_smp_act_send_confirm": (173704, 74, "227c1d2a8c1769fafbb9f655bf6523d6865cc933b232421a8af034bb686ffd46", "smpActSendPairCnf"),
    "open_cfw_cordio_smp_act_verify_calculate_one": (173780, 38, "c3128a559d06860301ad77f14ae1b02bb623981d9023e5ce8da895e6b9fa9262", "smpActPairCnfVerCalc1"),
    "open_cfw_cordio_smp_act_verify_calculate_two": (173820, 10, "2b90f5cd8e4be5e9f49fd0242c370c162749b18a0bfd10920ea1932f71d85b8c", "smpActPairCnfVerCalc2"),
    "open_cfw_cordio_smp_act_send_key": (173832, 444, "4b2906249efe0c632c93233d3a68706f5f0571502a33703ae4d9eef1371566b3", "smpSendKey"),
    "open_cfw_cordio_smp_act_receive_key": (174276, 202, "a559b9d39735122774d8da5830ab0cfba9fb72703b1367db5f03ec3e5b97a41e", "smpProcRcvKey"),
    "open_cfw_cordio_smp_act_max_attempts": (174480, 38, "cc6468c0811ea815cf8eb7d5fdfda14abafbbdc3b9bd39289b0ca28f9655cc1f", "smpActMaxAttempts"),
    "open_cfw_cordio_smp_act_attempt_received": (174520, 8, "32bb35189452cd383790f5f0b6b31c8b3b0db4e8aff434b5d39012ce1ae981ae", "smpActAttemptRcvd"),
    "open_cfw_cordio_smp_act_notify_attempts_failure": (174528, 12, "0894326cacfa6274b1bdc1721533ab5d5b2ae97f01f0be7d1ede78160b93ca66", "smpActNotifyDmAttemptsFailure"),
    "open_cfw_cordio_smp_act_notify_timeout_failure": (174540, 12, "3f598a8d3da4480cc046c0a947d74219c3b0e59eea7b5a6dbd1eb310c4d01bf4", "smpActNotifyDmRspToFailure"),
    "open_cfw_cordio_smp_act_check_attempts": (174552, 46, "80f18f2d1bd69aa59aa24cac8ed6ed1d80f7d748fe7e164ea2085211c9e9b60e", "smpActCheckAttempts"),
    "open_cfw_cordio_smp_act_pairing_complete": (174600, 56, "48a404ad5d8ef322bf0d6f6942b06159c28df88568177e0e8362a09e61590414", "smpActPairingCmpl"),
    "open_cfw_cordio_smp_act_execute": (174656, 160, "53f87b2b20be8309134e80cf40f97610c9bcfcfcf9646caccdd7edcda6b0d738", "smpSmExecute"),
}
IN_PLACE_ROUTE = (
    "open_cfw_cordio_smp_act_none",
    0x56E5DE,
    2,
    "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8",
)
PINS = {
    MAP: "fddbf7bc6c8c6108d5a847e63aa562e7f68a14efec239543c7a59cb70afa13b0",
    ROOT / "tools/manifests/packetcraft-cordio-smp-act-provenance.tsv": (
        "00aa11ad083a2c3192557b1fd34effed8c2fb54467a653fd5fbd6131f80b2098"
    ),
}
CALLS = {
    "smpStartRspTimer": [0x56D000, 0x56D06A, 0x56D0BE, 0x56D112, 0x56E8F0, 0x5E2DD8, 0x5E3132, 0x5E3264, 0x5E3364, 0x5E38D0, 0x5E3AE2, 0x5E3C1E, 0x5E3C5E],
    "smpActNone": [],
    "smpCleanup": [0x56E624, 0x56E65A, 0x56EE28, 0x56EE34],
    "smpActCleanup": [0x5E2B32],
    "smpSendPairingFailed": [0x56E6AA, 0x56EE1A, 0x5E2B60, 0x5E31AA],
    "smpActPairingFailed": [0x56E68C, 0x56E6B2, 0x5E2B50],
    "smpActSecReqTimeout": [],
    "smpActPairingCancel": [0x56EDB4],
    "smpActStorePin": [0x56E8AC],
    "smpProcPairing": [],
    "smpAuthReq": [],
    "smpActPairCnfCalc1": [],
    "smpActPairCnfCalc2": [],
    "smpActSendPairCnf": [],
    "smpActPairCnfVerCalc1": [],
    "smpActPairCnfVerCalc2": [],
    "smpSendKey": [0x5E345C, 0x5E3CBE],
    "smpProcRcvKey": [0x5E3424, 0x5E3D64],
    "smpActMaxAttempts": [],
    "smpActAttemptRcvd": [],
    "smpActNotifyDmAttemptsFailure": [0x56EE22],
    "smpActNotifyDmRspToFailure": [],
    "smpActCheckAttempts": [],
    "smpActPairingCmpl": [],
    "smpSmExecute": [0x5372F0, 0x537496, 0x5375AC, 0x53785A, 0x53798E, 0x5379E8, 0x537E94, 0x56CEFE, 0x56CF24, 0x56D04E, 0x56D0A2, 0x56D0F6, 0x56D14A, 0x56D318, 0x56E69A, 0x56E806, 0x56E840, 0x56E89E, 0x5E28A4, 0x5E29B6, 0x5E29E0, 0x5E2A00, 0x5E2A72, 0x5E2AAE, 0x5E2B24, 0x5E2BD8, 0x5E2D78, 0x5E2DC0, 0x5E2E0A, 0x5E2E6A, 0x5E2ED2, 0x5E3218, 0x5E32E0, 0x5E33FE, 0x5E343A, 0x5E346C, 0x5E36C6, 0x5E372E, 0x5E389A, 0x5E3920, 0x5E3BAA, 0x5E3D26, 0x5E3D74, 0x5E3FFA, 0x5E407A, 0x5E4200],
}
POINTER_TABLES = [
    (0x6D0B64, 0x6D0C40, "bbcc96d09c9c3d6842797ab8c9c61604dca828aaaf230fba8e5df96d77245718"),
    (0x6D1214, 0x6D12E0, "2f7d77ff2105f2a6153d40c15bff8ed0ee8197df738ea1547ff57a023185dd01"),
    (0x6D7E7C, 0x6D7EE8, "f98a484ebaee566eda7ad88adbadd10b8e2670de97b1370e35783fea117143cc"),
    (0x6DBAC4, 0x6DBB28, "2b2fd073285f4dae0973e64cfe07b3d68c4c119797401b2d2d8f932a2250150f"),
    (0x537F0C, 0x537F14, "4d8b1beb82a46bb326b15971561970a81b66444e6c5f050be4bf981f86dd776e"),
    (0x5380FC, 0x538104, "4d8b1beb82a46bb326b15971561970a81b66444e6c5f050be4bf981f86dd776e"),
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - BASE:end - BASE]


def load_decoder():
    tools_path = str(ROOT / "tools")
    if tools_path not in sys.path:
        sys.path.insert(0, tools_path)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("smp_act_thumb", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Thumb decoder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_rows():
    linked, source_only = [], []
    with MAP.open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["stock_status"] == "linked":
                linked.append((row["function"], int(row["stock_start"], 0), int(row["stock_end_exclusive"], 0), row["stock_sha256"]))
            else:
                source_only.append(row["function"])
    return linked, source_only


def production_report(linked: list[tuple[str, int, int, str]]) -> dict:
    source = PRODUCTION_SOURCE.read_bytes()
    if len(source) != PRODUCTION_SOURCE_SIZE or sha(source) != PRODUCTION_SOURCE_SHA256:
        raise RuntimeError("Cordio SMP action production source identity changed")
    overlay = json.loads(
        (ROOT / "components/apollo_main/core_overlay/overlay.json").read_text()
    )
    leaves = {
        row["function"]: row for row in overlay.get("relocated_leaves", [])
        if row.get("function") in PRODUCTION_ROUTES
    }
    patches = {
        row["target_function"]: row for row in overlay.get("patch_sites", [])
        if row.get("target_function") in PRODUCTION_ROUTES
    }
    if set(leaves) != set(PRODUCTION_ROUTES) or set(patches) != set(PRODUCTION_ROUTES):
        raise RuntimeError("Cordio SMP action production routing is incomplete")
    stock = {name: (start, end - start, digest) for name, start, end, digest in linked}
    source_path = PRODUCTION_SOURCE.relative_to(ROOT).as_posix()
    for function, (offset, size, digest, stock_name) in PRODUCTION_ROUTES.items():
        leaf = leaves[function]
        source_record = leaf.get("source", {})
        if (
            leaf.get("profiles") != ["apple-clang"]
            or source_record.get("path") != source_path
            or source_record.get("size") != PRODUCTION_SOURCE_SIZE
            or source_record.get("sha256") != PRODUCTION_SOURCE_SHA256
            or source_record.get("license") != "Apache-2.0"
            or source_record.get("upstream_commit")
            != "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6"
            or leaf.get("expected", {}).get("offset") != offset
            or leaf.get("expected", {}).get("size") != size
            or leaf.get("expected", {}).get("sha256") != digest
            or leaf.get("strict_relocation_contract") is not True
        ):
            raise RuntimeError(f"Cordio SMP action production leaf changed: {function}")
        patch = patches[function]
        stock_start, stock_size, stock_digest = stock[stock_name]
        if (
            patch.get("profiles") != ["apple-clang"]
            or patch.get("runtime_address") != stock_start
            or patch.get("expected_size") != stock_size
            or patch.get("expected_sha256") != stock_digest
            or patch.get("branch") != "b_w"
        ):
            raise RuntimeError(f"Cordio SMP action stock patch changed: {function}")

    function, runtime_address, size, digest = IN_PLACE_ROUTE
    in_place = {
        row["function"]: row for row in overlay.get("in_place_leaves", [])
        if row.get("function") == function
    }
    if set(in_place) != {function}:
        raise RuntimeError("Cordio SMP action no-op in-place route is incomplete")
    leaf = in_place[function]
    source_record = leaf.get("source", {})
    if (
        leaf.get("runtime_address") != runtime_address
        or leaf.get("stock") != {"size": size, "sha256": digest}
        or leaf.get("expected") != {"size": size, "sha256": digest}
        or leaf.get("relocations") != []
        or leaf.get("allow_halfword_placement") is not True
        or source_record.get("path") != source_path
        or source_record.get("size") != PRODUCTION_SOURCE_SIZE
        or source_record.get("sha256") != PRODUCTION_SOURCE_SHA256
        or source_record.get("license") != "Apache-2.0"
    ):
        raise RuntimeError("Cordio SMP action no-op in-place route changed")

    return {
        "status": "production-routed authenticated Packetcraft r20.05c definitions with the G2 SRAM ABI",
        "candidate": source_path,
        "production_routed": True,
        "live_functions": len(PRODUCTION_ROUTES) + 1,
        "relocated_functions": len(PRODUCTION_ROUTES),
        "in_place_functions": 1,
        "compiled_leaf_bytes": sum(route[1] for route in PRODUCTION_ROUTES.values()) + size,
        "source_owned_bytes_added": 1778,
        "stock_bytes_replaced": sum(end - start for _, start, end, _ in linked),
        "hardware_validation": (
            "blocked by unavailable authorized G2/EM9305 legacy and Secure "
            "Connections pairing, key distribution, timeout, cancellation, "
            "and repeated-attempt physical evidence"
        ),
    }


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != IMAGE_BYTES or sha(blob) != IMAGE_SHA:
        raise RuntimeError("official image changed")
    for path, digest in PINS.items():
        if not path.is_file() or sha(path.read_bytes()) != digest:
            raise RuntimeError(f"pinned input changed: {path}")

    linked, source_only = load_rows()
    if source_only or len(linked) != 25:
        raise RuntimeError("source inventory changed")
    bodies = []
    for name, start, end, digest in linked:
        body = image_slice(blob, start, end)
        if len(body) != end - start or sha(body) != digest:
            raise RuntimeError(f"body changed: {name}")
        bodies.append(body)
    if sha(b"".join(bodies)) != "244fee09f0e392daff7b57a6ca8803bc60c784a01e27375ea3b63bfb0d3b19df":
        raise RuntimeError("body concat changed")
    if sha(image_slice(blob, 0x56E5CC, 0x56F178)) != "b872ffd10869a0b17635f46054fb106161af819661ec5b6bbea597a55320e45d":
        raise RuntimeError("physical object changed")
    if sha(image_slice(blob, 0x56EC88, 0x56EC94)) != "6c1a8fad54f6cdabbb8e894f6f6b75f849457f936b1313d8f003faa9f5648407":
        raise RuntimeError("inline category data changed")
    if sha(image_slice(blob, 0x56F144, 0x56F178)) != "4d6851b63a9458707c02e1d89ae26e9a5f7d3f127442e34610bb797dc3c06206":
        raise RuntimeError("literal tail changed")
    path_bytes = image_slice(blob, 0x6E1994, 0x6E19F0)
    if sha(path_bytes) != "b9846d4a2ad49ef1c5462588bbc825739f9d256ead9cb12f532de0bbe07740b3":
        raise RuntimeError("retained path changed")
    if struct.unpack_from("<I", blob, 0x56F164 - BASE)[0] != 0x6E1994:
        raise RuntimeError("retained path pointer changed")
    if struct.unpack_from("<I", blob, 0x56F150 - BASE)[0] != 0x200004B8:
        raise RuntimeError("pSmpCfg literal changed")
    if struct.unpack_from("<I", blob, 0x56F154 - BASE)[0] != 0x20070AEC:
        raise RuntimeError("smpCb literal changed")

    decoder = load_decoder()
    starts = {start: name for name, start, _, _ in linked}
    calls = {name: [] for name, _, _, _ in linked}
    for address in range(BASE, BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in starts:
            calls[starts[target]].append(address)
    if calls != CALLS:
        raise RuntimeError("direct ingress changed")

    expected_entries = []
    for start, end, digest in POINTER_TABLES:
        data = image_slice(blob, start, end)
        if sha(data) != digest:
            raise RuntimeError(f"pointer table changed at {start:#x}")
        for address in range(start, end, 4):
            value = struct.unpack_from("<I", blob, address - BASE)[0]
            if (value & ~1) in starts:
                expected_entries.append((address, value))
    interior = set()
    for _, start, end, _ in linked:
        interior.update(range(start + 2, end, 2))
    entry_values, interior_values = [], []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        target = value & ~1
        if target in starts:
            entry_values.append((BASE + offset, value))
        elif target in interior:
            interior_values.append((BASE + offset, value))
    if entry_values != sorted(expected_entries) or len(entry_values) != 62:
        raise RuntimeError("stored entry-pointer closure changed")
    if interior_values:
        raise RuntimeError("stored strict-interior pointer found")

    return {
        "schema_version": 1,
        "module": {
            "start": 0x56E5CC,
            "end_exclusive": 0x56F178,
            "physical_bytes": 2988,
            "linked_function_count": 25,
            "linked_function_bytes": 2924,
            "source_inventory_functions": 25,
            "source_only_functions": [],
            "direct_bl_ingress_sites": 78,
            "registered_function_pointers": 62,
            "strict_interior_pointers": 0,
        },
        "architecture": {
            "retained_source_path": 0x6E1994,
            "smp_control_block": 0x20070AEC,
            "smp_config_pointer": 0x200004B8,
            "cleanup_event": 0x1F,
            "next_unit_entry": 0x56F178,
        },
        "lineage": {
            "selected_public_oracle": "Packetcraft r20.05 through r20.05c",
            "selected_commit": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
            "selected_blob": "3c1ac36652243add46ba812e45e62555a5668ba3",
            "selected_sha256": "5149ca2e6feb98157b3a5fe7d2061c5eba1e09d3bc8f7d9ee666ec4478849f4f",
            "license": "Apache-2.0",
            "independent_release_discriminator": True,
            "discriminator": "linked r20-only security-request-timeout action and guarded SC trace path",
        },
        "production": production_report(linked),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=Path, default=IMAGE)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = analyze(args.image)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("Cordio smp_act closed: 25/25 linked; 78 BL + 62 stored ingress")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
