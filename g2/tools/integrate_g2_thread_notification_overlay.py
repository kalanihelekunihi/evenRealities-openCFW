#!/usr/bin/env python3
"""Prepare and promote the clean-room G2 notification-thread overlay."""

import argparse
import copy
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "tools/integrate_g2_lvgl_font_manager_overlay.py"
SPEC = importlib.util.spec_from_file_location("g2_thread_notification_base", HELPER)
base = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(base)

ADMISSION_HELPER = ROOT / "tools/apply_g2_canonical_observations.py"
ADMISSION_SPEC = importlib.util.spec_from_file_location(
    "g2_thread_notification_admission", ADMISSION_HELPER)
admission = importlib.util.module_from_spec(ADMISSION_SPEC)
assert ADMISSION_SPEC.loader is not None
ADMISSION_SPEC.loader.exec_module(admission)

base.SOURCE = ROOT / "components/apollo_main/core_overlay/thread_notification.c"
base.RECORDER = "apple-thread-notification-record"
base.LEAF_DEFINE_PREFIX = "OPEN_CFW_THREAD_NOTIFICATION_"
base.PATCH_PREFIX = "replace_thread_notification_"
base.EVIDENCE = "docs/research/g2-thread-notification-recovery.md"
base.ORIGIN = "clean-room G2 CMSIS notification-thread orchestration and record dispatch"
base.LICENSE = "MIT"
base.SELECTORS = (
    ("ENTRY", "open_cfw_thread_notification_entry", 0x0048E154, 0x0048E1CC),
    ("INIT_HOOK", "open_cfw_thread_notification_init_hook", 0x0048E1CC, 0x0048E1CE),
    ("QUEUE_INIT", "open_cfw_thread_notification_queue_init", 0x0048E1CE, 0x0048E1F6),
    ("WHITELIST_INIT", "open_cfw_thread_notification_whitelist_init", 0x0048E1F6, 0x0048E1FE),
    ("STATE_ENTER", "open_cfw_thread_notification_state_enter", 0x0048E1FE, 0x0048E208),
    ("STATE_READY", "open_cfw_thread_notification_state_ready", 0x0048E208, 0x0048E212),
    ("CREATE", "open_cfw_thread_notification_create", 0x0048E212, 0x0048E242),
    ("DESTROY", "open_cfw_thread_notification_destroy", 0x0048E242, 0x0048E25E),
    ("DRAIN_QUEUE", "open_cfw_thread_notification_drain_queue", 0x0048E25E, 0x0048E2B8),
    ("EVENT_HANDLER", "open_cfw_thread_notification_event_handler", 0x0048E2B8, 0x0048E34E),
    ("EXIT", "open_cfw_thread_notification_exit", 0x0048E34E, 0x0048E3E2),
    ("SEND_EVENT", "open_cfw_thread_notification_send_event", 0x0048E3E2, 0x0048E42E),
)
base.PROVIDERS = {
    "open_cfw_thread_notification_thread_new": 0x004490E2,
    "open_cfw_thread_notification_thread_terminate": 0x004491FE,
    "open_cfw_thread_notification_flags_set": 0x00449238,
    "open_cfw_thread_notification_flags_wait": 0x004492C2,
    "open_cfw_thread_notification_delay": 0x00449376,
    "open_cfw_thread_notification_queue_new": 0x00449A32,
    "open_cfw_thread_notification_queue_get": 0x00449B3C,
    "open_cfw_thread_notification_queue_delete": 0x00449BEC,
    "open_cfw_thread_notification_free": 0x00474D16,
    "open_cfw_thread_notification_register": 0x004972C2,
    "open_cfw_thread_notification_unregister": 0x0049739E,
    "open_cfw_thread_notification_dispatch_message": 0x00497960,
    "open_cfw_thread_notification_mark_enter": 0x004C9B86,
    "open_cfw_thread_notification_mark_ready": 0x004C9BE2,
    "open_cfw_thread_notification_mark_exit": 0x004C9C3C,
    "open_cfw_thread_notification_whitelist_reload": 0x004D6A5C,
    "open_cfw_thread_notification_dispatch_whitelist": 0x004D6BA8,
    "open_cfw_thread_notification_panic_prepare": 0x005FA0A4,
}


def prepare() -> None:
    prior = json.loads(base.CONFIG.read_text())
    prior["in_place_leaves"] = [
        leaf for leaf in prior.get("in_place_leaves", [])
        if leaf.get("function") != "open_cfw_thread_notification_init_hook"
    ]
    base.CONFIG.write_text(json.dumps(prior, indent=2) + "\n")
    base.prepare()
    config = json.loads(base.CONFIG.read_text())
    config.get("toolchain_profiles", {}).pop(base.RECORDER, None)
    functions = {
        item[1] for item in base.SELECTORS
        if item[1] != "open_cfw_thread_notification_init_hook"
    }
    init_name = "open_cfw_thread_notification_init_hook"
    init_leaf = next(
        leaf for leaf in config["relocated_leaves"]
        if leaf.get("function") == init_name
    )
    config["relocated_leaves"] = [
        leaf for leaf in config["relocated_leaves"]
        if leaf.get("function") != init_name
    ]
    config["patch_sites"] = [
        site for site in config["patch_sites"]
        if not (
            site.get("name", "").startswith(base.PATCH_PREFIX)
            and site.get("runtime_address") == 0x0048E1CC
        )
    ]
    compiled = init_leaf["expected"]
    init_leaf["expected"] = {
        "size": compiled["size"],
        "sha256": compiled["unrelocated_sha256"],
    }
    init_leaf["runtime_address"] = 0x0048E1CC
    init_leaf["stock"] = {
        "size": 2,
        "sha256": "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8",
    }
    init_leaf["allow_halfword_placement"] = True
    init_leaf["toolchain_profiles"] = {
        "linux-clang": {
            "reviewed_version_prefix": "Homebrew clang version 22.1.8"
        }
    }
    init_leaf.pop("profiles", None)
    config["in_place_leaves"].append(init_leaf)
    config["functions"] = [
        function for function in config["functions"] if function != init_name
    ]
    for key in ("isolated_leaves", "relocated_leaves", "in_place_leaves"):
        for leaf in config.get(key, []):
            allowed = leaf.get("profiles")
            if isinstance(allowed, list):
                leaf["profiles"] = [
                    profile for profile in allowed
                    if profile != base.RECORDER
                ]
            profiles = leaf.get("toolchain_profiles")
            if isinstance(profiles, dict):
                profiles.pop(base.RECORDER, None)
                if not profiles:
                    leaf.pop("toolchain_profiles", None)
            if leaf.get("function") in functions:
                leaf["profiles"] = ["apple-clang", "linux-clang"]
                if leaf.get("function") == "open_cfw_thread_notification_entry":
                    for relocation in leaf.get("relocations", []):
                        if (relocation.get("symbol") == init_name and
                                relocation.get("type") == "R_ARM_THM_CALL"):
                            relocation.pop("target_function", None)
                            relocation["target_address"] = 0x0048E1CC
                if leaf.get("function") == "open_cfw_thread_notification_create":
                    for relocation in leaf.get("relocations", []):
                        if (relocation.get("symbol") ==
                                "open_cfw_thread_notification_entry" and
                                relocation.get("type") in (
                                    "R_ARM_THM_MOVW_PREL_NC",
                                    "R_ARM_THM_MOVT_PREL",
                                )):
                            relocation.pop("target_function", None)
                            relocation["target_address"] = 0x0048E154
                            relocation["symbol_type"] = "STT_NOTYPE"
    init_leaf.pop("profiles", None)
    for site in config.get("patch_sites", []):
        allowed = site.get("profiles")
        if isinstance(allowed, list):
            site["profiles"] = [
                profile for profile in allowed if profile != base.RECORDER]
        if site.get("name", "").startswith(base.PATCH_PREFIX):
            site["profiles"] = ["apple-clang", "linux-clang"]

    header = ROOT / "components/apollo_main/core_overlay/thread_notification.h"
    relative = header.relative_to(ROOT).as_posix()
    config["sources"] = [
        item for item in config.get("sources", [])
        if item.get("path") != relative
    ]
    payload = header.read_bytes()
    config["sources"].append({
        "evidence": base.EVIDENCE,
        "license": "MIT",
        "origin": "public ABI for the clean-room G2 notification thread",
        "path": relative,
        "sha256": base.sha(payload),
        "size": len(payload),
    })
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
    functions = {
        item[1] for item in base.SELECTORS
        if item[1] != "open_cfw_thread_notification_init_hook"
    }
    indexed = {}
    for profile, observation in observations.items():
        rows = admission._indexed_leaves(
            observation["core_stage"], "relocated_leaves")
        indexed[profile] = {
            function: copy.deepcopy(rows[function]["pins"])
            for function in functions if function in rows
        }
        if set(indexed[profile]) != functions:
            raise SystemExit(
                f"{profile} notification-thread leaf observation is incomplete")

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
                observation["core_stage"]["expected"])
        else:
            config["toolchain_profiles"][profile]["core_stage_expected"] = (
                copy.deepcopy(observation["core_stage"]["expected"]))
        provider = config["post_link_providers"]["liblc3_ltpf"]["profiles"][
            profile]
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
            config, profile, observation)
        admission.update_profile_pins(config, profile, observation)
    admission.atomic_write(
        base.CONFIG, (json.dumps(config, indent=2) + "\n").encode())


def admit_linux(report_path: Path) -> None:
    config = json.loads(base.CONFIG.read_text())
    report = json.loads(report_path.read_text())
    observed = {
        item["extraction"]["function"]: item["pins"]
        for item in report.get("relocated_leaves", [])
        if item.get("source", {}).get("path")
        == "components/apollo_main/core_overlay/thread_notification.c"
    }
    expected_names = {
        item[1] for item in base.SELECTORS
        if item[1] != "open_cfw_thread_notification_init_hook"
    }
    if set(observed) != expected_names:
        raise SystemExit("Linux notification-thread observation is incomplete")
    core_expected = report.get("canonical_observation", {}).get(
        "core_stage", {}).get("expected")
    liblc3 = report.get("canonical_observation", {}).get("liblc3_ltpf")
    if not isinstance(core_expected, dict) or not isinstance(liblc3, dict):
        raise SystemExit("Linux notification-thread canonical observation is absent")
    config["core_stage_expected"] = dict(config["expected"])
    config["toolchain_profiles"]["linux-clang"]["expected"] = core_expected
    config["toolchain_profiles"]["linux-clang"]["core_stage_expected"] = dict(
        core_expected)
    provider = config["post_link_providers"]["liblc3_ltpf"]["profiles"][
        "linux-clang"]
    provider["overlay"] = {
        "size": liblc3["payload_size"], "sha256": liblc3["payload_sha256"]}
    provider["component"] = {
        "size": liblc3["component_size"], "sha256": liblc3["component_sha256"]}
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action", choices=("prepare", "promote", "linux-pins", "review"))
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
