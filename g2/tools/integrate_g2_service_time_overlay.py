#!/usr/bin/env python3
"""Prepare and promote the clean-room G2 calendar/time-service overlay."""

import argparse
import copy
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "tools/integrate_g2_lvgl_font_manager_overlay.py"
SPEC = importlib.util.spec_from_file_location("g2_service_time_base", HELPER)
base = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(base)

ADMISSION_HELPER = ROOT / "tools/apply_g2_canonical_observations.py"
ADMISSION_SPEC = importlib.util.spec_from_file_location(
    "g2_service_time_admission", ADMISSION_HELPER
)
admission = importlib.util.module_from_spec(ADMISSION_SPEC)
assert ADMISSION_SPEC.loader is not None
ADMISSION_SPEC.loader.exec_module(admission)

base.SOURCE = ROOT / "components/apollo_main/core_overlay/service_time.c"
base.RECORDER = "apple-service-time-record"
base.LEAF_DEFINE_PREFIX = "OPEN_CFW_SERVICE_TIME_"
base.PATCH_PREFIX = "replace_service_time_"
base.EVIDENCE = "docs/research/g2-service-time-recovery.md"
base.ORIGIN = (
    "clean-room G2 Gregorian calendar, timezone, RTC synchronization, peer "
    "time-message, and retry-lifecycle service"
)
base.LICENSE = "MIT"
base.SELECTORS = (
    ("EPOCH24", "open_cfw_service_time_epoch_to_calendar24",
     0x00449ED4, 0x00449FDA),
    ("EPOCH_CONFIGURED", "open_cfw_service_time_epoch_to_calendar_configured",
     0x00449FDA, 0x0044A100),
    ("EPOCH_WRAPPER", "open_cfw_service_time_epoch_to_calendar",
     0x0044A100, 0x0044A108),
    ("CALENDAR_TO_EPOCH", "open_cfw_service_time_calendar_to_epoch",
     0x0044A108, 0x0044A192),
    ("CALENDAR_WRAPPER", "open_cfw_service_time_calendar_to_epoch_wrapper",
     0x0044A192, 0x0044A19A),
    ("CURRENT_CALENDAR", "open_cfw_service_time_current_calendar_get",
     0x0044A19A, 0x0044A1C6),
    ("CURRENT_EPOCH", "open_cfw_service_time_current_epoch_get",
     0x0044A1C6, 0x0044A1EA),
    ("RTC_REFRESH", "open_cfw_service_time_rtc_refresh",
     0x0044A1EA, 0x0044A1FE),
    ("SVC_SYNC", "SVC_SystemTimeSync", 0x0044A1FE, 0x0044A2B2),
    ("RPC_SYNC", "RPC_SystemTimeSync", 0x0044A2B2, 0x0044A3B4),
    ("SYNC_CALLBACK", "open_cfw_service_time_sync_callback",
     0x0044A3B4, 0x0044A3F0),
)
base.PROVIDERS = {
    "open_cfw_service_time_format_mode": 0x0046650C,
    "open_cfw_rtc_time_get": 0x0047EF10,
    "open_cfw_rtc_time_set": 0x0047EE78,
    "open_cfw_service_time_role": 0x0045A568,
    "open_cfw_service_time_sync_send": 0x004651E0,
    "open_cfw_service_time_remove_delayed": 0x00476ACE,
    "open_cfw_service_time_push_delayed": 0x0047697E,
}


def prepare() -> None:
    base.prepare()
    config = json.loads(base.CONFIG.read_text())
    config.get("toolchain_profiles", {}).pop(base.RECORDER, None)
    functions = {item[1] for item in base.SELECTORS}
    for key in ("isolated_leaves", "relocated_leaves", "in_place_leaves"):
        for leaf in config.get(key, []):
            allowed = leaf.get("profiles")
            if isinstance(allowed, list):
                leaf["profiles"] = [
                    profile for profile in allowed if profile != base.RECORDER
                ]
            profiles = leaf.get("toolchain_profiles")
            if isinstance(profiles, dict):
                profiles.pop(base.RECORDER, None)
                if not profiles:
                    leaf.pop("toolchain_profiles", None)
            if leaf.get("function") in functions:
                leaf["profiles"] = ["apple-clang", "linux-clang"]
                if leaf.get("function") == "open_cfw_service_time_sync_callback":
                    for relocation in leaf.get("relocations", []):
                        if (relocation.get("symbol") == "RPC_SystemTimeSync" and
                                relocation.get("type") in (
                                    "R_ARM_THM_MOVW_PREL_NC",
                                    "R_ARM_THM_MOVT_PREL",
                                )):
                            relocation.pop("target_function", None)
                            relocation["target_address"] = 0x0044A2B2
                            relocation["symbol_type"] = "STT_NOTYPE"
    for site in config.get("patch_sites", []):
        allowed = site.get("profiles")
        if isinstance(allowed, list):
            site["profiles"] = [
                profile for profile in allowed if profile != base.RECORDER
            ]
        if site.get("name", "").startswith(base.PATCH_PREFIX):
            site["profiles"] = ["apple-clang", "linux-clang"]

    header = ROOT / "components/apollo_main/core_overlay/service_time.h"
    relative = header.relative_to(ROOT).as_posix()
    config["sources"] = [
        item for item in config.get("sources", [])
        if item.get("path") != relative
    ]
    payload = header.read_bytes()
    config["sources"].append({
        "evidence": base.EVIDENCE,
        "license": "MIT",
        "origin": "public ABI for the clean-room G2 calendar/time service",
        "path": relative,
        "sha256": base.sha(payload),
        "size": len(payload),
    })
    base.CONFIG.write_text(json.dumps(config, indent=2) + "\n")


def admit_linux(report_path: Path) -> None:
    config = json.loads(base.CONFIG.read_text())
    report = json.loads(report_path.read_text())
    observed = {
        item["extraction"]["function"]: item["pins"]
        for item in report.get("relocated_leaves", [])
        if item.get("source", {}).get("path")
        == "components/apollo_main/core_overlay/service_time.c"
    }
    expected_names = {item[1] for item in base.SELECTORS}
    if set(observed) != expected_names:
        raise SystemExit("Linux service-time observation is incomplete")
    canonical = report.get("canonical_observation", {})
    core_expected = canonical.get("core_stage", {}).get("expected")
    liblc3 = canonical.get("liblc3_ltpf")
    if not isinstance(core_expected, dict) or not isinstance(liblc3, dict):
        raise SystemExit("Linux service-time stage observation is absent")
    config["core_stage_expected"] = dict(config["expected"])
    config["toolchain_profiles"]["linux-clang"]["expected"] = core_expected
    config["toolchain_profiles"]["linux-clang"]["core_stage_expected"] = dict(
        core_expected
    )
    provider = config["post_link_providers"]["liblc3_ltpf"]["profiles"][
        "linux-clang"
    ]
    provider["overlay"] = {
        "size": liblc3["payload_size"], "sha256": liblc3["payload_sha256"]
    }
    provider["component"] = {
        "size": liblc3["component_size"], "sha256": liblc3["component_sha256"]
    }
    for leaf in config.get("relocated_leaves", []):
        function = leaf.get("function")
        if function not in observed:
            continue
        pins = dict(observed[function])
        relocations = pins.pop("relocations", [])
        leaf.setdefault("toolchain_profiles", {})["linux-clang"] = {
            "reviewed_version_prefix": "Homebrew clang version 22.1.8",
            "expected": pins,
            "relocations": relocations,
        }
    base.CONFIG.write_text(json.dumps(config, indent=2) + "\n")


def review_observations(paths: list[Path]) -> None:
    apple_pair = admission.admit_reproducible_pair(paths[:2], "apple-clang")
    linux_pair = admission.admit_reproducible_pair(paths[2:], "linux-clang")
    admission.validate_observation_independence((*apple_pair, *linux_pair))
    admission.validate_generation(apple_pair[0], linux_pair[0])
    observations = {
        "apple-clang": apple_pair[0]["observation"],
        "linux-clang": linux_pair[0]["observation"],
    }
    config = json.loads(base.CONFIG.read_text())
    functions = {item[1] for item in base.SELECTORS}
    indexed = {}
    for profile, observation in observations.items():
        rows = admission._indexed_leaves(
            observation["core_stage"], "relocated_leaves"
        )
        indexed[profile] = {
            function: copy.deepcopy(rows[function]["pins"])
            for function in functions if function in rows
        }
        if set(indexed[profile]) != functions:
            raise SystemExit(f"{profile} service-time leaf observation is incomplete")

    for leaf in config.get("relocated_leaves", []):
        function = leaf.get("function")
        if function not in functions:
            continue
        apple = indexed["apple-clang"][function]
        leaf["relocations"] = apple.pop("relocations")
        leaf["expected"] = apple
        linux = indexed["linux-clang"][function]
        leaf.setdefault("toolchain_profiles", {})["linux-clang"] = {
            "reviewed_version_prefix": "Homebrew clang version 22.1.8",
            "relocations": linux.pop("relocations"),
            "expected": linux,
        }

    for profile, observation in observations.items():
        if profile == "apple-clang":
            config["core_stage_expected"] = copy.deepcopy(
                observation["core_stage"]["expected"]
            )
        else:
            config["toolchain_profiles"][profile]["core_stage_expected"] = (
                copy.deepcopy(observation["core_stage"]["expected"])
            )
        provider = config["post_link_providers"]["liblc3_ltpf"]["profiles"][
            profile
        ]
        liblc3 = observation["liblc3_ltpf"]
        provider["overlay"] = {
            "size": liblc3["payload_size"],
            "sha256": liblc3["payload_sha256"],
        }
        provider["component"] = {
            "size": liblc3["component_size"],
            "sha256": liblc3["component_sha256"],
        }

    for profile, observation in observations.items():
        admission._require_reviewed_core_leaf_pins(
            config, profile, observation
        )
        admission.update_profile_pins(config, profile, observation)
    admission.atomic_write(
        base.CONFIG, (json.dumps(config, indent=2) + "\n").encode()
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action", choices=("prepare", "promote", "linux-pins", "review")
    )
    parser.add_argument("--report", type=Path)
    parser.add_argument("--reports", nargs=4, type=Path)
    args = parser.parse_args()
    if args.action == "prepare":
        prepare()
    elif args.action == "promote":
        base.promote()
    elif args.action == "linux-pins":
        if args.report is None:
            raise SystemExit("linux-pins requires --report")
        admit_linux(args.report)
    else:
        if args.reports is None:
            raise SystemExit("review requires four --reports")
        review_observations(args.reports)


if __name__ == "__main__":
    main()
