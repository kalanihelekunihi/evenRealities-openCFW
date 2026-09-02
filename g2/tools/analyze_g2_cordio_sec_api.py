#!/usr/bin/env python3
"""Fail-closed stock-boundary and production-route audit for Cordio sec_api."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
SOURCE = ROOT / "components/apollo_main/core_overlay/cordio_sec_api.c"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
OVERLAY_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
PACKAGE = ROOT / "build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
PACKAGE_REPORT = ROOT / "build/source/build-report.json"
FLASH_PLAN = ROOT / "build/source/flash-plan.json"
BASE = 0x00437FE0
IMAGE_SIZE = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
SOURCE_SHA256 = "fdfe93f8ec34dad9deea2ce5e4f5571bf53672cda202b87a2a04a3c60832634e"
PACKAGE_SIZE = 4_750_576
PACKAGE_SHA256 = "56f3c555b58099e0a744905856cc803c9aa681bdffc2b2ad8b4f61141ff8c1e6"
FLASH_PLAN_SIZE = 4_881_053
FLASH_PLAN_SHA256 = "e540570208e616cc3de20af268da55d17fbf59f918aee143be8a902449253262"
EXPECTED_OVERLAY = {
    "overlay_size": 362_272,
    "overlay_sha256": "8c80c3fa53a89c77d145533f59f63389dfa31f968642f783323ed81ac81be5ae",
    "component_size": 3_956_468,
    "component_sha256": "aa3dbf59ad8912a92fcd9ea6e1ce33834da51989f5fb19257e7064871fb6a3b2",
}
FUNCTIONS = (
    ("open_cfw_cordio_sec_hci_callback", 0x00536234, 0x00536324, "da8ebedf91cd554eae5a19134ec01fd47b991e76d0e8666365b8e662dca7f89c"),
    ("open_cfw_cordio_sec_init", 0x00536324, 0x0053634E, "b7a64ba8e0c0b12b96a83304c91c5e5330c5aa34f09f3ef04e06b402284cf045"),
    ("open_cfw_cordio_sec_random", 0x0053634E, 0x005363AE, "e9fbe9a104896249e6a859995592f43f3d54407b396bb96e4320102c4ff405a8"),
    ("open_cfw_cordio_sec_le_encrypt", 0x005363AE, 0x005363E4, "9065ee64c03ed123480a63d34c72585ab8a56d281646e489c6755ae555a98169"),
    ("open_cfw_cordio_sec_next_token", 0x005363FC, 0x00536426, "d86e0da9f1e312038afe83ceafbdfc74333a09b58d7d5cc6512b09f7075f81c9"),
    ("open_cfw_cordio_sec_aes", 0x00536426, 0x00536470, "c255d36546a3d98d8fc49bb0a8b027a058e81ea3f36b25cbfaa0e1dad41a18f2"),
    ("open_cfw_cordio_sec_aes_callback", 0x00536470, 0x0053648E, "80e4ad0117e7f338ed365daa8286beeb47e402cf7cdd6c6a3c60c12f96860de9"),
    ("open_cfw_cordio_sec_aes_init", 0x0053648E, 0x00536496, "e867ad68047d9b51eb0ad7b0dec6a16acd28e12346fadd57e7589301ba572ae9"),
    ("open_cfw_cordio_sec_cmac_block", 0x005364A4, 0x0053653A, "91d07d6701dd97eef6d0ad5828ba731c7f2c71950e434efaa2f5cd9b4b63e246"),
    ("open_cfw_cordio_sec_cmac_subkey1", 0x0053653A, 0x0053655C, "143ee0f25135e515416565ad3323d0666d3c34186a6bcad72b676f75a7748514"),
    ("open_cfw_cordio_sec_cmac_shift", 0x0053655C, 0x005365A6, "b03ea4506c0b6253de28af495b9790e0d7216204c21a894b423e3b216ec82afd"),
    ("open_cfw_cordio_sec_cmac_subkey2", 0x005365A6, 0x00536608, "ab2dec8da9ca7821bc49b4568a7c647ddc1ab30e80bad21099470618dbca5785"),
    ("open_cfw_cordio_sec_cmac_complete", 0x00536608, 0x00536620, "f965a56845a2eb172cc714eafd0e18a1bf9b2df49cdc92223ac858fb6dfe0c77"),
    ("open_cfw_cordio_sec_cmac_callback", 0x00536620, 0x0053665C, "436c5eb2beecb4524677dec2c24ca4eef9a70fb2d080e53b9934c17c47dfcc74"),
    ("open_cfw_cordio_sec_cmac", 0x0053665C, 0x005366CC, "d9ee565794b96f4a791e3ec90cb9016c2ed552c1648f6d9458ef74b0dc8d223b"),
    ("open_cfw_cordio_sec_cmac_init", 0x005366CC, 0x005366D4, "33617b99ecbfa824e1ce308e4afb03216f9d8f7689bc2578b59a46cb81a579ce"),
    ("open_cfw_cordio_sec_ecc_callback", 0x005366DC, 0x0053673E, "4cf8515818d055788cb660c3d5232846ecc72f39855813c1b700188c1753c8aa"),
    ("open_cfw_cordio_sec_ecc_key", 0x0053673E, 0x00536774, "7f66cb89b639e02e0650a3d9e910c497ca03d14432585df727a83a12c7e8b07b"),
    ("open_cfw_cordio_sec_ecc_secret", 0x00536774, 0x005367CA, "49fa1119e50381737b3c53452dcfb9caaec3958c3ce8d6e0e3d94be4971a2f9f"),
    ("open_cfw_cordio_sec_ecc_init", 0x005367CA, 0x005367D2, "7b0ae9b4a3c2997d2e6038af50efb5af59472e31d3b5ab16aee6b230eddacd9d"),
)


class AuditError(RuntimeError):
    pass


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def checked(path: Path, size: int, digest: str) -> bytes:
    data = path.read_bytes()
    if len(data) != size or sha(data) != digest:
        raise AuditError(f"artifact changed: {path}")
    return data


def analyze() -> dict:
    image = checked(IMAGE, IMAGE_SIZE, IMAGE_SHA256)
    checked(SOURCE, 17_182, SOURCE_SHA256)
    for _name, start, end, digest in FUNCTIONS:
        body = image[start - BASE:end - BASE]
        if len(body) != end - start or sha(body) != digest:
            raise AuditError(f"stock function changed at 0x{start:08X}")
    physical = image[FUNCTIONS[0][1] - BASE:FUNCTIONS[-1][2] - BASE]
    if len(physical) != 1_438 or sha(physical) != "dd287edbb64ea9b9ebaa36705e9a6cf30624552bd38167801e8ada461a6c7b8b":
        raise AuditError("stock physical boundary changed")

    overlay = json.loads(OVERLAY.read_text())
    if overlay.get("expected") != EXPECTED_OVERLAY:
        raise AuditError("canonical overlay/component pins changed")
    leaves = [x for x in overlay["relocated_leaves"] if x.get("source", {}).get("path", "").endswith("cordio_sec_api.c")]
    names = {x["function"] for x in leaves}
    if len(leaves) != 20 or names != {x[0] for x in FUNCTIONS}:
        raise AuditError("security leaf inventory changed")
    if any(x.get("source", {}).get("license") != "Apache-2.0" for x in leaves):
        raise AuditError("security source license changed")
    if any(not x.get("strict_relocation_contract") for x in leaves):
        raise AuditError("security relocation contract weakened")
    if sum(x["expected"]["size"] for x in leaves) != 1_952:
        raise AuditError("compiled security text changed")
    if sum(len(x["relocations"]) for x in leaves) != 65:
        raise AuditError("security relocation census changed")
    sites = [x for x in overlay["patch_sites"] if x.get("name", "").startswith("replace_cordio_sec_api_")]
    if len(sites) != 20 or {x["runtime_address"] for x in sites} != {x[1] for x in FUNCTIONS}:
        raise AuditError("security production routing changed")
    report = json.loads(OVERLAY_REPORT.read_text())
    built = [x for x in report["relocated_leaves"] if x.get("source", {}).get("path", "").endswith("cordio_sec_api.c")]
    alignment = sum(x["placement"]["padding_before"] for x in built)
    if len(built) != 20 or alignment != 16:
        raise AuditError("security placement changed")

    checked(PACKAGE, PACKAGE_SIZE, PACKAGE_SHA256)
    checked(FLASH_PLAN, FLASH_PLAN_SIZE, FLASH_PLAN_SHA256)
    package_report = json.loads(PACKAGE_REPORT.read_text())
    expected_report = {
        "size": PACKAGE_SIZE,
        "sha256": PACKAGE_SHA256,
        "reference_sha256": PACKAGE_SHA256,
        "byte_identical_to_reference": True,
    }
    if any(package_report["package"].get(k) != v for k, v in expected_report.items()):
        raise AuditError("package replay changed")
    if package_report.get("placed_region_count") != 7_006 or package_report.get("unresolved_region_count") != 0:
        raise AuditError("package region census changed")
    return {
        "schema_version": 1,
        "identity": {
            "component": "Packetcraft Cordio sec_api",
            "release": "r20.05c",
            "commit": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
            "license": "Apache-2.0",
            "disposition": "implemented-in-source; hardware-validation-deferred",
            "first_party_even_backend": False,
        },
        "stock": {"functions": 20, "body_bytes": 1_392, "retained_gap_bytes": 46, "physical_bytes": 1_438},
        "production": {
            "production_routed": True,
            "source_functions": 20,
            "compiled_text_bytes": 1_952,
            "alignment_bytes": 16,
            "strict_relocations": 65,
            "package_byte_identical": True,
            "placed_regions": 7_006,
            "unresolved_regions": 0,
            "primitive_provider": "retained HCI/controller boundary",
            "hardware_validation": "blocked by unavailable physical evidence",
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
