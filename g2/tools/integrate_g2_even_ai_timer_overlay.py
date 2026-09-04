#!/usr/bin/env python3
"""Prepare and promote the clean-room G2 EvenAI timer overlay."""

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "tools/integrate_g2_lvgl_font_manager_overlay.py"
SPEC = importlib.util.spec_from_file_location("g2_even_ai_timer_base", HELPER)
base = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(base)

base.SOURCE = ROOT / "components/apollo_main/core_overlay/even_ai_timer.c"
base.RECORDER = "apple-even-ai-timer-record"
base.LEAF_DEFINE_PREFIX = "OPEN_CFW_EVEN_AI_"
base.PATCH_PREFIX = "replace_even_ai_timer_"
base.EVIDENCE = "docs/research/g2-even-ai-timer-recovery.md"
base.ORIGIN = "clean-room G2 EvenAI unsigned tick/deadline state machines"
base.LICENSE = "MIT"
base.SELECTORS = (
    ("COMMON_DEINIT", "open_cfw_even_ai_common_timer_mgr_deinit", 0x004E2E10, 0x004E2E62),
    ("COMMON_START", "open_cfw_even_ai_common_timer_mgr_start", 0x004E2E62, 0x004E2E86),
    ("COMMON_STOP", "open_cfw_even_ai_common_timer_mgr_stop", 0x004E2E86, 0x004E2ED2),
    ("COMMON_CHECK", "open_cfw_even_ai_common_timer_mgr_check_timeout", 0x004E2ED2, 0x004E2EFE),
    ("COMMON_PROCESS", "open_cfw_even_ai_common_timer_mgr_process_timeout", 0x004E2EFE, 0x004E3006),
    ("HEARTBEAT_DEINIT", "open_cfw_even_ai_heartbeat_timer_mgr_deinit", 0x004E3006, 0x004E304C),
    ("HEARTBEAT_START", "open_cfw_even_ai_heartbeat_timer_mgr_start", 0x004E304C, 0x004E306E),
    ("HEARTBEAT_STOP", "open_cfw_even_ai_heartbeat_timer_mgr_stop", 0x004E306E, 0x004E30B4),
    ("HEARTBEAT_CHECK", "open_cfw_even_ai_heartbeat_timer_mgr_check_timeout", 0x004E30B4, 0x004E30E0),
    ("HEARTBEAT_PROCESS", "open_cfw_even_ai_heartbeat_timer_mgr_process_timeout", 0x004E30E0, 0x004E3130),
    ("DEINIT_ALL", "open_cfw_even_ai_timer_deinit_all", 0x004E3194, 0x004E31A0),
    ("START_ALL", "open_cfw_even_ai_timer_start_all", 0x004E31A0, 0x004E31B0),
    ("PROCESS_ALL", "open_cfw_even_ai_timer_process_all", 0x004E31B0, 0x004E31CC),
)
base.PROVIDERS = {
    "open_cfw_even_ai_tick_now": 0x004490CC,
    "open_cfw_even_ai_role": 0x0045A568,
    "open_cfw_even_ai_sync": 0x00464F76,
    "open_cfw_even_ai_set_state": 0x0049832E,
    "open_cfw_even_ai_send_control": 0x00498528,
}


def prepare() -> None:
    base.prepare()
    config = json.loads(base.CONFIG.read_text())
    functions = {item[1] for item in base.SELECTORS}
    for leaf in config.get("relocated_leaves", []):
        if leaf.get("function") in functions:
            profiles = leaf.setdefault("profiles", [])
            if "linux-clang" not in profiles:
                profiles.append("linux-clang")
    for site in config.get("patch_sites", []):
        if site.get("name", "").startswith(base.PATCH_PREFIX):
            profiles = site.setdefault("profiles", [])
            if "linux-clang" not in profiles:
                profiles.append("linux-clang")

    header = ROOT / "components/apollo_main/core_overlay/even_ai_timer.h"
    relative = header.relative_to(ROOT).as_posix()
    config["sources"] = [
        item for item in config.get("sources", [])
        if item.get("path") != relative
    ]
    payload = header.read_bytes()
    config["sources"].append({
        "evidence": base.EVIDENCE,
        "license": "MIT",
        "origin": "public ABI for the clean-room G2 EvenAI timer manager",
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
        == "components/apollo_main/core_overlay/even_ai_timer.c"
    }
    expected_names = {item[1] for item in base.SELECTORS}
    if set(observed) != expected_names:
        raise SystemExit("Linux EvenAI timer observation is incomplete")
    core_expected = (
        report.get("canonical_observation", {})
        .get("core_stage", {})
        .get("expected")
    )
    liblc3 = (
        report.get("canonical_observation", {})
        .get("liblc3_ltpf")
    )
    if not isinstance(core_expected, dict):
        raise SystemExit("Linux EvenAI timer core-stage observation is absent")
    if not isinstance(liblc3, dict):
        raise SystemExit("Linux EvenAI timer liblc3 observation is absent")
    config["core_stage_expected"] = dict(config["expected"])
    config["toolchain_profiles"]["linux-clang"]["expected"] = core_expected
    config["toolchain_profiles"]["linux-clang"]["core_stage_expected"] = (
        dict(core_expected)
    )
    provider = config["post_link_providers"]["liblc3_ltpf"]["profiles"][
        "linux-clang"
    ]
    provider["overlay"] = {
        "size": liblc3["payload_size"],
        "sha256": liblc3["payload_sha256"],
    }
    provider["component"] = {
        "size": liblc3["component_size"],
        "sha256": liblc3["component_sha256"],
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("prepare", "promote", "linux-pins"))
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if args.action == "prepare":
        prepare()
    elif args.action == "promote":
        base.promote()
    else:
        if args.report is None:
            raise SystemExit("linux-pins requires --report")
        admit_linux(args.report)


if __name__ == "__main__":
    main()
