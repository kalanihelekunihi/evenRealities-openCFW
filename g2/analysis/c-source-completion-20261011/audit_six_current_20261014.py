#!/usr/bin/env python3
"""Reconcile current six-image C evidence without promoting candidate links to firmware."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
G2 = ROOT / "g2"
BUILD = G2 / "build/c-firmware/20261014"
OUT = G2 / "analysis/c-source-completion-20261011/six-current-20261014.json"
TARGET_SHA = "7312f4b855ff41ec823cc977485a8cc5e59a7235f834880b2217bf1f3ab138ff"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def receipt(path):
    data = json.loads(path.read_text())
    return data, {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def file_checked(name, expected):
    path = ROOT / name
    actual = sha(path)
    if actual != expected:
        raise RuntimeError(f"stale artifact: {name}: {actual}")
    return {"path": name, "sha256": actual}


def undefined(path):
    output = subprocess.check_output(["arm-none-eabi-nm", "-u", str(path)], text=True)
    return sorted({line.split()[-1] for line in output.splitlines()
                   if line.strip() and line.split()[0] == "U"})


def main():
    images = {}
    for directory, name in (("codec-source-refresh", "codec"),
                            ("em9305-source-refresh", "ble_em9305"),
                            ("bootloader-root-refresh", "apollo_bootloader")):
        path = BUILD / directory / "receipt.json"
        data, ref = receipt(path)
        if data["target_sha256"] != TARGET_SHA or data["complete_source_payloads"] != 0:
            raise RuntimeError(f"stale six-image target/source gate: {directory}")
        item = data["images"][name]
        if not item["candidate_compilation_passed"] or item["source_complete"] or item["full_payload_linked"]:
            raise RuntimeError(f"component evidence classification changed: {name}")
        output = BUILD / directory / name / "candidate.o"
        expected = item["relocatable_link"].get("output_sha256", item.get("output_sha256"))
        artifact = file_checked(str(output.relative_to(ROOT)), expected)
        images[name] = {
            "receipt": ref, "candidate": artifact,
            "candidate_compilation_passed": True,
            "recorded_unresolved": item["relocatable_link"]["unresolved_symbols"],
            "source_complete": False, "full_payload_linked": False,
            "remaining_gate": item["source_gates"],
        }
    debug_release_path = G2 / "build/c-firmware/20261016/boot-shutdown-debug-release-42252e/oracle-receipt.json"
    debug_release, debug_release_ref = receipt(debug_release_path)
    debug_release_source = ROOT / debug_release["source"]
    if debug_release["status"] != "PASS_NATIVE_BOOT_SHUTDOWN_DEBUG_RELEASE_42252E" or \
            debug_release["cases"] != 90 or \
            debug_release["source_sha256"] != sha(debug_release_source) or \
            debug_release["official_bootloader_sha256"] != "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5":
        raise RuntimeError("Bootloader shutdown debug-release oracle changed")
    images["apollo_bootloader"]["shutdown_debug_release_42252e"] = debug_release_ref
    images["apollo_bootloader"]["remaining_gate"].append(
        "Shutdown debug-release 0x42252e passes 90 bounded native/C cases; its critical-save and delay children are controlled in that isolated receipt.")
    info_cache_path = G2 / "build/c-firmware/20261016/boot-startup-info-cache-41c320/oracle-receipt.json"
    info_cache, info_cache_ref = receipt(info_cache_path)
    info_cache_source = ROOT / info_cache["source"]
    if info_cache["status"] != "PASS_NATIVE_BOOT_STARTUP_INFO_CACHE_41C320" or \
            info_cache["cases"] != 180 or \
            info_cache["source_sha256"] != sha(info_cache_source) or \
            info_cache["official_bootloader_sha256"] != "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5":
        raise RuntimeError("Bootloader startup information-cache oracle changed")
    images["apollo_bootloader"]["startup_info_cache_41c320"] = info_cache_ref
    images["apollo_bootloader"]["remaining_gate"].append(
        "Startup information-cache 0x41c320 passes 180 bounded native/C guard, read-chain, failure and record cases; its downstream device read remains controlled.")
    root_composed_path = G2 / "build/c-firmware/20261016/boot-root-with-debug-info/receipt.json"
    root_composed, root_composed_ref = receipt(root_composed_path)
    root_composed_runner = G2 / "analysis/c-source-completion-20261011/apollo/verify_boot_root_with_debug_info_20261016.py"
    root_composed_elf = G2 / "build/c-source-completion-20261011/apollo/bootloader_m33_query_oracle.elf"
    coverage = root_composed["composed_child_coverage"]
    if root_composed["status"] != "PASS_NATIVE_BOOT_ROOT_DEBUG_INFO_COMPOSED" or \
            root_composed["cases"] != 1388 or \
            root_composed["runner_sha256"] != sha(root_composed_runner) or \
            root_composed["elf_sha256"] != sha(root_composed_elf) or \
            root_composed["original_sha256"] != "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5" or \
            root_composed["visited_body_bytes"]["init"] != 810 or \
            coverage["debug_release_native_bytes_70"] != 60 or \
            coverage["info_cache_native_bytes_352"] != 352 or \
            coverage["fixtures_with_info_reads"] != 6 or \
            coverage["controlled_info_read_calls"] != 40 or \
            coverage["fixtures_with_debug_delay"] != 1374:
        raise RuntimeError("Bootloader composed root/debug/info comparison changed")
    images["apollo_bootloader"]["root_debug_info_composed"] = root_composed_ref
    root_trim_path = G2 / "build/c-firmware/20261016/boot-root-with-debug-info-trim/receipt.json"
    root_trim, root_trim_ref = receipt(root_trim_path)
    root_trim_runner = G2 / "analysis/c-source-completion-20261011/apollo/verify_boot_root_with_debug_info_trim_20261016.py"
    trim_coverage = root_trim["composed_child_coverage"]
    if root_trim["status"] != "PASS_NATIVE_BOOT_ROOT_DEBUG_INFO_TRIM_COMPOSED" or \
            root_trim["cases"] != 1396 or \
            root_trim["runner_sha256"] != sha(root_trim_runner) or \
            root_trim["elf_sha256"] != sha(root_composed_elf) or \
            root_trim["original_sha256"] != "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5" or \
            root_trim["visited_body_bytes"]["init"] != 810 or \
            trim_coverage["trim_version_native_bytes_60"] != 58 or \
            trim_coverage["info_cache_native_bytes_352"] != 352 or \
            trim_coverage["fixtures_with_trim_provider_read"] != 8 or \
            trim_coverage["controlled_info_read_calls"] != 76:
        raise RuntimeError("Bootloader composed root/debug/info/trim comparison changed")
    images["apollo_bootloader"]["root_debug_info_trim_composed"] = root_trim_ref
    images["apollo_bootloader"]["remaining_gate"].append(
        "The earlier root/debug/info/trim comparison passes 1396 cases; its device reads and clock lower contracts are controlled, and two trim bytes were not visited in that replay.")
    root_spot_path = G2 / "build/c-firmware/20261016/boot-root-with-debug-info-trim-spot-m4/receipt.json"
    root_spot, root_spot_ref = receipt(root_spot_path)
    root_spot_runner = G2 / "analysis/c-source-completion-20261011/apollo/verify_boot_root_with_debug_info_trim_spot_m4_20261016.py"
    root_spot_elf = G2 / "analysis/c-source-completion-20261011/apollo/spot-m4-oracle/startup_runtime.elf"
    root_spot_source = G2 / "components/bootloader/initializer_callbacks/startup_runtime.c"
    spot_coverage = root_spot["composed_child_coverage"]
    if root_spot["status"] != "PASS_NATIVE_BOOT_ROOT_DEBUG_INFO_TRIM_SPOT_M4_COMPOSED" or \
            root_spot["cases"] != 1396 or \
            root_spot["runner_sha256"] != sha(root_spot_runner) or \
            root_spot["elf_sha256"] != sha(root_composed_elf) or \
            root_spot["isolated_spot_elf_sha256"] != sha(root_spot_elf) or \
            root_spot["spot_source_sha256"] != sha(root_spot_source) or \
            root_spot["original_sha256"] != "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5" or \
            root_spot["visited_body_bytes"]["init"] != 810 or \
            spot_coverage["spot_dispatch_native_bytes"] != 668 or \
            spot_coverage["fixtures_with_spot_installed"] != 1056 or \
            spot_coverage["info_cache_native_bytes_352"] != 352 or \
            spot_coverage["trim_version_native_bytes_60"] != 58:
        raise RuntimeError("Bootloader composed root/debug/info/trim/SPOT comparison changed")
    images["apollo_bootloader"]["root_debug_info_trim_spot_composed"] = root_spot_ref
    images["apollo_bootloader"]["remaining_gate"].append(
        "The earlier root/debug/info/trim/SPOT comparison passes 1396 cases, covering all 668 stock SPOT bytes and 1056 installed-slot fixtures. Its SPOT source is an isolated Cortex-M4 build with stock-bound named callbacks.")
    shared_path = G2 / "build/c-firmware/20261016/boot-shared-memory-41be36/receipt.json"
    shared, shared_ref = receipt(shared_path)
    shared_runner = G2 / "analysis/c-source-completion-20261011/apollo/verify_boot_shared_memory_41be36_20261016.py"
    shared_source = G2 / "components/bootloader/initializer_callbacks/startup_memory_config.c"
    memory_overlay_path = G2 / "build/c-firmware/20261016/boot-memory-m33-overlay/build-receipt.json"
    memory_overlay, memory_overlay_ref = receipt(memory_overlay_path)
    memory_overlay_runner = G2 / "analysis/c-source-completion-20261011/apollo/build_boot_memory_m33_overlay_20261016.py"
    memory_overlay_elf = G2 / "build/c-firmware/20261016/boot-memory-m33-overlay/memory.elf"
    memory_m55_object = G2 / "build/c-firmware/20261016/boot-memory-m33-overlay/startup_memory_config_m55.o"
    if memory_overlay["status"] != "PASS_M33_MEMORY_SOURCE_OVERLAY_LINKED" or \
            memory_overlay["source_sha256"] != sha(shared_source) or \
            memory_overlay["elf_sha256"] != sha(memory_overlay_elf) or \
            memory_overlay["m55_object_sha256"] != sha(memory_m55_object) or \
            memory_overlay["builder_sha256"] != sha(memory_overlay_runner):
        raise RuntimeError("Bootloader M33 memory overlay changed")
    images["apollo_bootloader"]["memory_m33_overlay"] = memory_overlay_ref
    if shared["status"] != "PASS_NATIVE_BOOT_SHARED_MEMORY_41BE36" or \
            shared["cases"] != 576 or shared["stock_body_bytes_260"] != 260 or \
            shared["runner_sha256"] != sha(shared_runner) or \
            shared["source_sha256"] != sha(shared_source) or \
            shared["selected_elf_sha256"] != sha(root_composed_elf) or \
            shared["overlay_elf_sha256"] != sha(memory_overlay_elf) or \
            shared["stock_sha256"] != "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5":
        raise RuntimeError("Bootloader shared-memory body comparison changed")
    images["apollo_bootloader"]["shared_memory_41be36"] = shared_ref
    root_shared_path = G2 / "build/c-firmware/20261016/boot-root-with-spot-shared-m4/receipt.json"
    root_shared, root_shared_ref = receipt(root_shared_path)
    root_shared_runner = G2 / "analysis/c-source-completion-20261011/apollo/verify_boot_root_with_debug_info_trim_spot_shared_m4_20261016.py"
    shared_coverage = root_shared["composed_child_coverage"]
    if root_shared["status"] != "PASS_NATIVE_BOOT_ROOT_DEBUG_INFO_TRIM_SPOT_SHARED_M4_COMPOSED" or \
            root_shared["cases"] != 1420 or \
            root_shared["runner_sha256"] != sha(root_shared_runner) or \
            root_shared["elf_sha256"] != sha(root_composed_elf) or \
            root_shared["isolated_spot_elf_sha256"] != sha(root_spot_elf) or \
            root_shared["memory_overlay_elf_sha256"] != sha(memory_overlay_elf) or \
            root_shared["spot_source_sha256"] != sha(root_spot_source) or \
            root_shared["shared_source_sha256"] != sha(shared_source) or \
            root_shared["original_sha256"] != "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5" or \
            shared_coverage["shared_memory_native_bytes"] != 210 or \
            shared_coverage["spot_dispatch_native_bytes"] != 668 or \
            shared_coverage["fixtures_with_shared_match"] != 16 or \
            shared_coverage["fixtures_with_shared_poll_mirror"] != 8:
        raise RuntimeError("Bootloader composed shared-memory comparison changed")
    images["apollo_bootloader"]["root_with_shared_memory_composed"] = root_shared_ref
    images["apollo_bootloader"]["remaining_gate"].append(
        "Shared-memory 0x41be36 passes 576 direct cases with 260/260 stock bytes visited, and 1420 composed startup fixtures reach 210/260 bytes. Its power callback and status poll remain controlled.")
    mcu_path = G2 / "build/c-firmware/20261016/boot-mcu-memory-41bbd0/receipt.json"
    mcu, mcu_ref = receipt(mcu_path)
    mcu_runner = G2 / "analysis/c-source-completion-20261011/apollo/verify_boot_mcu_memory_41bbd0_20261016.py"
    if mcu["status"] != "PASS_NATIVE_BOOT_MCU_MEMORY_41BBD0" or \
            mcu["cases"] != 2304 or mcu["stock_body_bytes_450"] != 450 or \
            mcu["unvisited_stock_bytes"] or \
            mcu["runner_sha256"] != sha(mcu_runner) or \
            mcu["source_sha256"] != sha(shared_source) or \
            mcu["selected_elf_sha256"] != sha(root_composed_elf) or \
            mcu["overlay_elf_sha256"] != sha(memory_overlay_elf) or \
            mcu["stock_sha256"] != "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5":
        raise RuntimeError("Bootloader MCU-memory body comparison changed")
    images["apollo_bootloader"]["mcu_memory_41bbd0"] = mcu_ref
    root_mcu_path = G2 / "build/c-firmware/20261016/boot-root-with-spot-shared-mcu-m4/receipt.json"
    root_mcu, root_mcu_ref = receipt(root_mcu_path)
    root_mcu_runner = G2 / "analysis/c-source-completion-20261011/apollo/verify_boot_root_with_spot_shared_mcu_m4_20261016.py"
    mcu_coverage = root_mcu["composed_child_coverage"]
    if root_mcu["status"] != "PASS_NATIVE_BOOT_ROOT_DEBUG_INFO_TRIM_SPOT_SHARED_MCU_M4_COMPOSED" or \
            root_mcu["cases"] != 1420 or \
            root_mcu["runner_sha256"] != sha(root_mcu_runner) or \
            root_mcu["elf_sha256"] != sha(root_composed_elf) or \
            root_mcu["isolated_spot_elf_sha256"] != sha(root_spot_elf) or \
            root_mcu["memory_overlay_elf_sha256"] != sha(memory_overlay_elf) or \
            root_mcu["shared_source_sha256"] != sha(shared_source) or \
            root_mcu["original_sha256"] != "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5" or \
            mcu_coverage["mcu_memory_native_bytes"] != 318 or \
            mcu_coverage["shared_memory_native_bytes"] != 210 or \
            mcu_coverage["spot_dispatch_native_bytes"] != 668:
        raise RuntimeError("Bootloader composed MCU-memory comparison changed")
    images["apollo_bootloader"]["root_with_mcu_memory_composed"] = root_mcu_ref
    images["apollo_bootloader"]["remaining_gate"].append(
        "MCU-memory 0x41bbd0 passes 2304 direct cases with 450/450 stock bytes visited, after fixing its high return word. The 1420-case composed startup replay reaches 318/450 bytes; its lower calls remain controlled.")
    device_gate_path = G2 / "build/c-firmware/20261016/boot-device-mode-421548/receipt.json"
    device_gate, device_gate_ref = receipt(device_gate_path)
    device_gate_runner = G2 / "analysis/c-source-completion-20261011/apollo/verify_boot_device_mode_421548_20261016.py"
    device_gate_source = G2 / "components/bootloader/application_storage/device_mode_wait.c"
    if device_gate["status"] != "PASS_NATIVE_BOOT_DEVICE_MODE_421548" or \
            device_gate["cases"] != 520 or device_gate["stock_body_bytes_38"] != 38 or \
            device_gate["unvisited_stock_bytes"] or \
            device_gate["runner_sha256"] != sha(device_gate_runner) or \
            device_gate["source_sha256"] != sha(device_gate_source) or \
            device_gate["selected_elf_sha256"] != sha(root_composed_elf) or \
            device_gate["stock_sha256"] != "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5":
        raise RuntimeError("Bootloader device-mode selector comparison changed")
    images["apollo_bootloader"]["device_mode_gate_421548"] = device_gate_ref
    root_device_path = G2 / "build/c-firmware/20261016/boot-root-with-device-gate/receipt.json"
    root_device, root_device_ref = receipt(root_device_path)
    root_device_runner = G2 / "analysis/c-source-completion-20261011/apollo/verify_boot_root_with_device_gate_20261016.py"
    device_coverage = root_device["composed_child_coverage"]
    if root_device["status"] != "PASS_NATIVE_BOOT_ROOT_WITH_DEVICE_GATE_COMPOSED" or \
            root_device["cases"] != 1420 or \
            root_device["runner_sha256"] != sha(root_device_runner) or \
            root_device["elf_sha256"] != sha(root_composed_elf) or \
            root_device["memory_overlay_elf_sha256"] != sha(memory_overlay_elf) or \
            root_device["device_mode_source_sha256"] != sha(device_gate_source) or \
            root_device["original_sha256"] != "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5" or \
            device_coverage["device_mode_native_bytes"] != 34 or \
            device_coverage["controlled_device_dispatch_calls"] < 1000 or \
            device_coverage["mcu_memory_native_bytes"] != 318 or \
            device_coverage["shared_memory_native_bytes"] != 210:
        raise RuntimeError("Bootloader composed device-mode selector comparison changed")
    images["apollo_bootloader"]["root_with_device_mode_gate"] = root_device_ref
    images["apollo_bootloader"]["remaining_gate"].append(
        "Device-mode selector 0x421548 passes 520 direct cases with 38/38 stock bytes and 1420 composed fixtures reaching 34/38 bytes. Its downstream read dispatcher remains controlled.")
    mspi_overlay_path = G2 / "build/c-firmware/20261016/boot-mspi-m33-overlay/build-receipt.json"
    mspi_overlay, mspi_overlay_ref = receipt(mspi_overlay_path)
    mspi_builder = G2 / "analysis/c-source-completion-20261011/apollo/build_boot_mspi_m33_overlay_20261016.py"
    mspi_source = G2 / "components/bootloader/platform_control/power_domains.c"
    mspi_elf = G2 / "build/c-firmware/20261016/boot-mspi-m33-overlay/mspi.elf"
    mspi_m55_object = G2 / "build/c-firmware/20261016/boot-mspi-m33-overlay/power_domains_m55.o"
    if mspi_overlay["status"] != "PASS_M33_MSPI_SOURCE_OVERLAY_LINKED" or \
            mspi_overlay["builder_sha256"] != sha(mspi_builder) or \
            mspi_overlay["source_sha256"] != sha(mspi_source) or \
            mspi_overlay["elf_sha256"] != sha(mspi_elf) or \
            mspi_overlay["m55_object_sha256"] != sha(mspi_m55_object):
        raise RuntimeError("Bootloader MSPI comparison overlay changed")
    images["apollo_bootloader"]["mspi_m33_overlay"] = mspi_overlay_ref
    root_mspi_path = G2 / "build/c-firmware/20261016/boot-root-with-both-mspi-modes/receipt.json"
    root_mspi, root_mspi_ref = receipt(root_mspi_path)
    root_mspi_runner = G2 / "analysis/c-source-completion-20261011/apollo/verify_boot_root_with_both_mspi_modes_20261016.py"
    mspi_coverage = root_mspi["composed_child_coverage"]
    if root_mspi["status"] != "PASS_NATIVE_BOOT_ROOT_WITH_BOTH_MSPI_MODES_COMPOSED" or \
            root_mspi["cases"] != 1420 or \
            root_mspi["runner_sha256"] != sha(root_mspi_runner) or \
            root_mspi["elf_sha256"] != sha(root_composed_elf) or \
            root_mspi["memory_overlay_elf_sha256"] != sha(memory_overlay_elf) or \
            root_mspi["mspi_overlay_elf_sha256"] != sha(mspi_elf) or \
            root_mspi["mspi_source_sha256"] != sha(mspi_source) or \
            root_mspi["original_sha256"] != "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5" or \
            root_mspi["visited_body_bytes"]["init"] != 810 or \
            mspi_coverage["mode_enter_native_bytes"] != 188 or \
            mspi_coverage["mode_leave_native_bytes"] != 230 or \
            mspi_coverage["device_mode_native_bytes"] != 34 or \
            mspi_coverage["mcu_memory_native_bytes"] != 318:
        raise RuntimeError("Bootloader composed MSPI mode comparison changed")
    images["apollo_bootloader"]["root_with_both_mspi_modes"] = root_mspi_ref
    images["apollo_bootloader"]["remaining_gate"].append(
        "All eleven root child entries execute in a 1420-case stock/C startup replay. Mode-enter reaches 188/314 and mode-leave 230/350 stock bytes; their other branches and lower provider/ROM timing contracts, production M55 execution and whole-image gates remain open.")
    mspi_enter_path = G2 / "build/c-firmware/20261016/boot-mspi-enter-41bf84/receipt.json"
    mspi_enter, mspi_enter_ref = receipt(mspi_enter_path)
    mspi_enter_runner = G2 / "analysis/c-source-completion-20261011/apollo/verify_boot_mspi_enter_41bf84_20261016.py"
    if mspi_enter["status"] != "PASS_NATIVE_BOOT_MSPI_ENTER_41BF84" or \
            mspi_enter["cases"] != 3590 or mspi_enter["stock_body_bytes_314"] != 314 or \
            mspi_enter["unvisited_stock_bytes"] or \
            mspi_enter["runner_sha256"] != sha(mspi_enter_runner) or \
            mspi_enter["source_sha256"] != sha(mspi_source) or \
            mspi_enter["base_elf_sha256"] != sha(root_composed_elf) or \
            mspi_enter["overlay_elf_sha256"] != sha(mspi_elf) or \
            mspi_enter["stock_sha256"] != "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5":
        raise RuntimeError("Bootloader MSPI mode-enter comparison changed")
    images["apollo_bootloader"]["mspi_mode_enter_41bf84"] = mspi_enter_ref
    mspi_leave_path = G2 / "build/c-firmware/20261016/boot-mspi-leave-41c17a/receipt.json"
    mspi_leave, mspi_leave_ref = receipt(mspi_leave_path)
    mspi_leave_runner = G2 / "analysis/c-source-completion-20261011/apollo/verify_boot_mspi_leave_41c17a_20261016.py"
    if mspi_leave["status"] != "PASS_NATIVE_BOOT_MSPI_LEAVE_41C17A" or \
            mspi_leave["cases"] != 7234 or mspi_leave["stock_body_bytes_350"] != 350 or \
            mspi_leave["unvisited_stock_bytes"] or \
            mspi_leave["runner_sha256"] != sha(mspi_leave_runner) or \
            mspi_leave["source_sha256"] != sha(mspi_source) or \
            mspi_leave["base_elf_sha256"] != sha(root_composed_elf) or \
            mspi_leave["overlay_elf_sha256"] != sha(mspi_elf) or \
            mspi_leave["stock_sha256"] != "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5":
        raise RuntimeError("Bootloader MSPI mode-leave comparison changed")
    images["apollo_bootloader"]["mspi_mode_leave_41c17a"] = mspi_leave_ref
    images["apollo_bootloader"]["remaining_gate"].append(
        "Direct MSPI enter/leave comparisons visit 314/314 and 350/350 stock bytes across 3590 and 7234 cases. Descriptor, clock, power, poll, delay and callback lower contracts are controlled; production M55 and whole-image gates remain open.")
    info_dispatch_path = G2 / "build/c-firmware/20261016/boot-info-dispatch-4213e6/receipt.json"
    info_dispatch, info_dispatch_ref = receipt(info_dispatch_path)
    info_dispatch_runner = G2 / "analysis/c-source-completion-20261011/apollo/verify_boot_info_dispatch_4213e6_20261016.py"
    info_dispatch_source = G2 / "components/bootloader/application_storage/device_wait_service.c"
    if info_dispatch["status"] != "PASS_NATIVE_BOOT_INFO_DISPATCH_4213E6" or \
            info_dispatch["cases"] != 7200 or info_dispatch["stock_body_bytes_354"] != 350 or \
            info_dispatch["unvisited_stock_bytes"] != ["0x42149c", "0x42149d", "0x421532", "0x421533"] or \
            info_dispatch["runner_sha256"] != sha(info_dispatch_runner) or \
            info_dispatch["source_sha256"] != sha(info_dispatch_source) or \
            info_dispatch["selected_elf_sha256"] != sha(root_composed_elf) or \
            info_dispatch["stock_sha256"] != "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5":
        raise RuntimeError("Bootloader INFO dispatcher comparison changed")
    images["apollo_bootloader"]["info_dispatch_4213e6"] = info_dispatch_ref
    info_fallback_path = G2 / "build/c-firmware/20261016/boot-info-dispatch-fallback/receipt.json"
    info_fallback, info_fallback_ref = receipt(info_fallback_path)
    if info_fallback["status"] != "PASS_STOCK_BOOT_INFO_DISPATCH_FALLBACK_UNREACHABLE" or \
            info_fallback["prior_oracle_sha256"] != sha(info_dispatch_path) or \
            info_fallback["stock_sha256"] != info_dispatch["stock_sha256"] or \
            info_fallback["selector_domain_after_first_gate"] != [0, 1, 2, 3, 4, 5] or \
            info_fallback["unvisited_instruction_addresses"] != ["0x42149c", "0x421532"]:
        raise RuntimeError("Bootloader INFO fallback control-flow proof changed")
    images["apollo_bootloader"]["info_dispatch_unreachable_fallback"] = info_fallback_ref
    root_info_path = G2 / "build/c-firmware/20261016/boot-root-with-info-dispatch/receipt.json"
    root_info, root_info_ref = receipt(root_info_path)
    root_info_runner = G2 / "analysis/c-source-completion-20261011/apollo/verify_boot_root_with_info_dispatch_20261016.py"
    info_coverage = root_info["composed_child_coverage"]
    if root_info["status"] != "PASS_NATIVE_BOOT_ROOT_WITH_INFO_DISPATCH_COMPOSED" or \
            root_info["cases"] != 1420 or \
            root_info["runner_sha256"] != sha(root_info_runner) or \
            root_info["elf_sha256"] != sha(root_composed_elf) or \
            root_info["memory_overlay_elf_sha256"] != sha(memory_overlay_elf) or \
            root_info["mspi_overlay_elf_sha256"] != sha(mspi_elf) or \
            root_info["info_dispatch_source_sha256"] != sha(info_dispatch_source) or \
            root_info["original_sha256"] != "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5" or \
            root_info["visited_body_bytes"]["init"] != 788 or \
            info_coverage["info_dispatch_native_bytes"] != 224 or \
            info_coverage["controlled_info_rom_calls"] != 1762 or \
            info_coverage["mode_enter_native_bytes"] != 188 or \
            info_coverage["mode_leave_native_bytes"] != 190:
        raise RuntimeError("Bootloader composed INFO dispatcher comparison changed")
    images["apollo_bootloader"]["root_with_info_dispatch"] = root_info_ref
    images["apollo_bootloader"]["remaining_gate"].append(
        "INFO dispatcher 0x4213e6 passes 7200 direct cases visiting 350/354 stock bytes; pinned control-flow proof establishes that the four unvisited bytes are unreachable fallback instructions after the invalid-space gate. A 1420-case composed replay reaches 224/354 dispatcher and 788/810 root bytes with resident ROM read controlled. Production M55 and whole-image behavior remain open.")
    em_path = BUILD / "em9305-source-refresh/resident-rom-bindings-receipt.json"
    em, em_ref = receipt(em_path)
    if em["unresolved_before"] != 12 or em["unresolved_after"] != 0 or em["whole_image_complete"]:
        raise RuntimeError("EM resident ROM classification changed")
    images["ble_em9305"]["resident_rom_binding"] = {
        "receipt": em_ref,
        "object": file_checked(em["bound_object"], em["bound_object_sha256"]),
        "external_entries": 12, "unresolved_after_external_binding": 0,
    }
    touch_path = BUILD / "touch-default-enum-providers/receipt.json"
    touch, touch_ref = receipt(touch_path)
    if touch["strong_unresolved"] or len(touch["weak_unresolved"]) != 4 or touch["whole_image_complete"]:
        raise RuntimeError("Touch experimental link classification changed")
    images["touch"] = {
        "receipt": touch_ref,
        "candidate": file_checked(touch["linked_object"], touch["linked_object_sha256"]),
        "strong_unresolved": [], "optional_weak_unresolved": touch["weak_unresolved"],
        "lp_history_capacity_proven": False, "source_complete": False,
        "full_payload_linked": False, "remaining_gate": touch["limits"],
    }
    case_path = G2 / "analysis/c-source-completion-20261011/m0/case_current_20261014.elf.receipt.json"
    case, case_ref = receipt(case_path)
    if case["status"] != "EXPERIMENTAL_ABSOLUTE_C_ELF_LINKED" or case["undefined_symbols"]:
        raise RuntimeError("CASE experimental ELF classification changed")
    images["case"] = {
        "receipt": case_ref,
        "experimental_elf": file_checked(case["output"], case["output_sha256"]),
        "experimental_undefined": [], "source_complete": False,
        "full_payload_linked": False, "remaining_gate": case["limits"],
    }
    case_gc_path = G2 / "build/c-firmware/20261015/case-gc-size-frontier/receipt.json"
    case_gc, case_gc_ref = receipt(case_gc_path)
    if (case_gc["status"] != "PASS_EXPERIMENTAL_CASE_GC_SIZE_FRONTIER" or
            case_gc["source_receipt_sha256"] != case_ref["sha256"] or
            case_gc["gc_overflow_bytes"] != 10680 or case_gc["undefined_symbols"]):
        raise RuntimeError("CASE size frontier changed")
    images["case"]["gc_size_frontier"] = {
        "receipt": case_gc_ref,
        "experimental_elf": file_checked(case_gc["gc_elf"], case_gc["gc_elf_sha256"]),
        "stock_payload_bytes": case_gc["stock_payload_bytes"],
        "gc_load_bytes": case_gc["gc_load_bytes"],
        "overflow_bytes": case_gc["gc_overflow_bytes"],
        "native_reset_entry": case_gc["stock_reset_entry"],
        "gc_reset_entry": case_gc["gc_entry"],
    }
    case_reset_path = G2 / "build/c-firmware/20261015/case-gc-size-frontier/reset-size-receipt.json"
    case_reset, case_reset_ref = receipt(case_reset_path)
    if (case_reset["status"] != "PASS_EXPERIMENTAL_CASE_RESET_SIZE_FRONTIER" or
            case_reset["gc_receipt_sha256"] != case_gc_ref["sha256"] or
            case_reset["variants"][-1]["overflow_bytes"] != 10719 or
            len(case_reset["variants"][-1]["matching_vector_words"]) != 13):
        raise RuntimeError("CASE fixed-reset size frontier changed")
    images["case"]["fixed_reset_size_frontier"] = {
        "receipt": case_reset_ref,
        "experimental_elf": file_checked(case_reset["variants"][-1]["elf"],
                                         case_reset["variants"][-1]["elf_sha256"]),
        "entry": case_reset["variants"][-1]["entry"],
        "matching_vector_words": len(case_reset["variants"][-1]["matching_vector_words"]),
        "vector_words": 46,
        "overflow_bytes": case_reset["variants"][-1]["overflow_bytes"],
    }
    case_oz_path = G2 / "build/c-firmware/20261015/case-gc-size-frontier/mixed-oz-receipt.json"
    case_oz, case_oz_ref = receipt(case_oz_path)
    if (case_oz["status"] != "PASS_EXPERIMENTAL_CASE_MIXED_OZ_FIXED_RESET_FRONTIER" or
            case_oz["reset_frontier_receipt_sha256"] != case_reset_ref["sha256"] or
            case_oz["overflow_bytes"] != 7851 or case_oz["native_pointer_leads_present"] != 39):
        raise RuntimeError("CASE mixed -Oz frontier changed")
    images["case"]["mixed_oz_size_frontier"] = {
        "receipt": case_oz_ref,
        "experimental_elf": file_checked(case_oz["elf"], case_oz["elf_sha256"]),
        "load_bytes": case_oz["load_bytes"], "overflow_bytes": case_oz["overflow_bytes"],
        "entry": case_oz["entry"], "matching_vector_words": len(case_oz["matching_vector_words"]),
        "native_pointer_leads_present": case_oz["native_pointer_leads_present"],
    }
    case_named_path = G2 / "build/c-firmware/20261016/case-named-function-size/receipt.json"
    case_named, case_named_ref = receipt(case_named_path)
    if case_named["status"] != "PASS_EXPERIMENTAL_CASE_NAMED_FUNCTION_SIZE_TRIAGE" or \
            case_named["baseline_receipt_sha256"] != case_oz_ref["sha256"] or \
            case_named["experimental_elf_sha256"] != case_oz["elf_sha256"] or \
            case_named["matched_function_count"] != 38 or \
            case_named["matched_net_delta_bytes"] != -4898 or \
            case_named["native_catalogue_functions"] != 428 or \
            case_named["candidate_function_union_bytes"] != 54320 or \
            case_named["candidate_text_bytes_outside_function_symbols"] != 8951 or \
            case_named["experimental_payload_overflow_bytes"] != 7851:
        raise RuntimeError("CASE named function size triage changed")
    file_checked(case_named["catalogue"], case_named["catalogue_sha256"])
    images["case"]["named_function_size_triage"] = case_named_ref
    images["case"]["remaining_gate"].append(
        "The 38 C symbols with explicit stock address suffixes total 4,898 bytes less than their Ghidra function envelopes, while the mixed -Oz CASE load exceeds stock by 7,851 bytes. The candidate .text has 54,320 unique function bytes and 8,951 bytes outside function symbols; the 428-entry native catalogue has 40,664 envelope bytes but may be incomplete. Unmatched code and linker placement require review before assigning the overflow to specific bodies.")
    main_path = BUILD / "main-post-tail-c-replay/receipt.json"
    main, main_ref = receipt(main_path)
    if main["status"] != "PASS_EXPERIMENTAL_MAIN_POST_TAIL_C_REPLAY" or main["unresolved_after"] != 183:
        raise RuntimeError("Apollo Main current replay changed")
    main_obj = file_checked(main["linked_object"], main["linked_object_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 183:
        raise RuntimeError("Apollo Main unresolved set changed")
    ram_path = G2 / "build/c-firmware/settings-live-buffers-round1007/receipt.json"
    ram, ram_ref = receipt(ram_path)
    ram_source = ROOT / "g2/components/audio/uart_thread_source_candidate/settings_live_buffers.c"
    if ram["status"] != "PASS_SETTINGS_LIVE_BUFFER_MINIMA_BINDING" or \
            ram["source_sha256"] != sha(ram_source) or \
            ram["native_minimum_spans"]["audio_settings_last_message_state"]["minimum_size"] != 104:
        raise RuntimeError("Apollo Main settings RAM extent evidence changed")
    ram_rows = [line.split() for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-S", str(ROOT / main_obj["path"])], text=True).splitlines()
        if line.endswith(" audio_settings_last_message_state")]
    if len(ram_rows) != 1:
        raise RuntimeError("Apollo Main settings RAM symbol missing")
    selected_ram_bytes = int(ram_rows[0][1], 16)
    if selected_ram_bytes != 104:
        raise RuntimeError("Apollo Main still lacks the stock-evidenced 104-byte settings RAM span")
    for symbol, minimum in (("audio_dm_connection_records", 196),
                            ("audio_ble_dm_adv_control", 0x34)):
        rows = [line.split() for line in subprocess.check_output(
            ["arm-none-eabi-nm", "-S", str(ROOT / main_obj["path"])], text=True).splitlines()
            if line.endswith(" " + symbol)]
        if len(rows) != 1 or int(rows[0][1], 16) != minimum:
            raise RuntimeError("Apollo Main bounded RAM source size changed: " + symbol)
    registry_path = G2 / "build/c-firmware/20261015/main-dm-registry-extent-gate/receipt.json"
    registry, registry_ref = receipt(registry_path)
    if registry["status"] != "PASS_BOUNDED_MAIN_DM_REGISTRY_EXTENT_GATE" or \
            registry["defined_ccb_bytes"] != 144 or registry["alias_safe"]:
        raise RuntimeError("Apollo Main prior DM registry extent gate changed")
    storage_path = G2 / "build/c-firmware/20261015/main-dm-conn-cb-storage-200712a4/receipt.json"
    storage, storage_ref = receipt(storage_path)
    pair_path = G2 / "build/c-firmware/20261014/main-master-pair-runtime-state/receipt.json"
    pair, pair_ref = receipt(pair_path)
    if pair["status"] != "PASS_EXPERIMENTAL_MAIN_MASTER_PAIR_RUNTIME_STATE_C" or \
            pair["dm_cb_storage_bytes"] != 196 or \
            storage["status"] != "PASS_EXPERIMENTAL_MAIN_DM_CONN_CB_STORAGE_ALIAS_C" or \
            storage["pair_receipt_sha256"] != pair_ref["sha256"] or \
            storage["shared_bss_bytes"] != 196 or \
            storage["alias_target"] != "audio_dm_connection_records" or \
            storage["imports_resolved"] != ["audio_ble_dm_connection_registry"] or \
            "audio_ble_dm_connection_registry" in actual:
        raise RuntimeError("Apollo Main C-owned DM registry alias changed")
    stack_path = G2 / "build/c-firmware/20261015/main-dm-stack-interface-78a88c/receipt.json"
    stack, stack_ref = receipt(stack_path)
    if stack["status"] != "PASS_EXPERIMENTAL_MAIN_DM_STACK_INTERFACE_C" or \
            stack["base_sha256"] != storage["linked_sha256"] or \
            len(stack["imports_added"]) != 8:
        raise RuntimeError("Apollo Main DM dispatch table changed")
    scan_path = G2 / "build/c-firmware/20261015/main-dm-dispatch-scan-stop-536896/receipt.json"
    scan, scan_ref = receipt(scan_path)
    if scan["status"] != "PASS_EXPERIMENTAL_MAIN_DM_DISPATCH_SCAN_STOP_C" or \
            scan["base_sha256"] != stack["linked_sha256"] or \
            scan["imports_resolved"] != ["audio_ble_dm_dispatch_536896"]:
        raise RuntimeError("Apollo Main DM scan-stop dispatch changed")
    wrapper_path = G2 / "build/c-firmware/20261015/main-dm-dispatch-scan-stop-wrapper-5368ae/receipt.json"
    wrapper, wrapper_ref = receipt(wrapper_path)
    if wrapper["status"] != "PASS_EXPERIMENTAL_MAIN_DM_DISPATCH_SCAN_STOP_WRAPPER_C" or \
            wrapper["base_sha256"] != scan["linked_sha256"] or \
            wrapper["imports_resolved"] != ["audio_ble_dm_dispatch_5368ae"]:
        raise RuntimeError("Apollo Main DM scan-stop wrapper changed")
    msg_path = G2 / "build/c-firmware/20261015/main-dm-stack-msg-handler-5369d8/receipt.json"
    msg, msg_ref = receipt(msg_path)
    if msg["status"] != "PASS_EXPERIMENTAL_MAIN_DM_STACK_MSG_HANDLER_C" or \
            msg["base_sha256"] != wrapper["linked_sha256"] or \
            msg["imports_resolved"] != ["audio_ble_dm_stack_msg_handler_5369d8"]:
        raise RuntimeError("Apollo Main DM message dispatcher changed")
    forward_path = G2 / "build/c-firmware/20261015/main-dm-dispatch-4d2544/receipt.json"
    forward, forward_ref = receipt(forward_path)
    if forward["status"] != "PASS_EXPERIMENTAL_MAIN_DM_DISPATCH_4D2544_C" or \
            forward["base_sha256"] != msg["linked_sha256"] or \
            forward["imports_resolved"] != ["audio_ble_dm_dispatch_4d2544"] or \
            forward["imports_added"] != []:
        raise RuntimeError("Apollo Main DM dispatch forwarder changed")
    reset_path = G2 / "build/c-firmware/20261015/main-dm-stack-reset-536918/receipt.json"
    reset, reset_ref = receipt(reset_path)
    if reset["status"] != "PASS_EXPERIMENTAL_MAIN_DM_STACK_RESET_C" or \
            reset["base_sha256"] != forward["linked_sha256"] or \
            reset["imports_resolved"] != ["audio_ble_dm_stack_reset_536918"]:
        raise RuntimeError("Apollo Main DM stack reset changed")
    hci_path = G2 / "build/c-firmware/20261015/main-dm-stack-hci-handler-53694c/receipt.json"
    hci, hci_ref = receipt(hci_path)
    if hci["status"] != "PASS_EXPERIMENTAL_MAIN_DM_STACK_HCI_HANDLER_C" or \
            hci["base_sha256"] != reset["linked_sha256"] or \
            hci["imports_added"] != ["audio_ble_dm_stack_hci_scan_complete_5368b6"]:
        raise RuntimeError("Apollo Main DM HCI dispatcher changed")
    complete_path = G2 / "build/c-firmware/20261015/main-dm-stack-hci-scan-complete-5368b6/receipt.json"
    complete, complete_ref = receipt(complete_path)
    if complete["status"] != "PASS_EXPERIMENTAL_MAIN_DM_STACK_HCI_SCAN_COMPLETE_C" or \
            complete["base_sha256"] != hci["linked_sha256"] or \
            complete["imports_resolved"] != ["audio_ble_dm_stack_hci_scan_complete_5368b6"]:
        raise RuntimeError("Apollo Main DM scan-complete child changed")
    scan_start_path = G2 / "build/c-firmware/20261015/main-dm-dispatch-scan-start-536820/receipt.json"
    scan_start, scan_start_ref = receipt(scan_start_path)
    if scan_start["status"] != "PASS_EXPERIMENTAL_MAIN_DM_DISPATCH_SCAN_START_C" or \
            scan_start["base_sha256"] != complete["linked_sha256"] or \
            scan_start["imports_resolved"] != ["audio_ble_dm_dispatch_536820"]:
        raise RuntimeError("Apollo Main DM scan-start dispatch changed")
    sec_path = G2 / "build/c-firmware/20261015/main-dm-sec-hci-handler-4d2364/receipt.json"
    sec, sec_ref = receipt(sec_path)
    if sec["status"] != "PASS_EXPERIMENTAL_MAIN_DM_SEC_HCI_HANDLER_C" or \
            sec["base_sha256"] != scan_start["linked_sha256"] or \
            len(sec["imports_added"]) != 5:
        raise RuntimeError("Apollo Main DM security HCI dispatch changed")
    lesc_path = G2 / "build/c-firmware/20261015/main-dm-sec-lesc-neg-ltk/receipt.json"
    lesc, lesc_ref = receipt(lesc_path)
    if lesc["status"] != "PASS_EXPERIMENTAL_MAIN_DM_SEC_LESC_NEG_LTK_C" or \
            lesc["base_sha256"] != sec["linked_sha256"] or \
            len(lesc["imports_resolved"]) != 2:
        raise RuntimeError("Apollo Main LESC/negative LTK children changed")
    ltk_path = G2 / "build/c-firmware/20261015/main-hci-ltk-reply-52b2ce/receipt.json"
    ltk, ltk_ref = receipt(ltk_path)
    if ltk["status"] != "PASS_EXPERIMENTAL_MAIN_HCI_LTK_REPLY_C" or \
            ltk["base_sha256"] != lesc["linked_sha256"] or \
            ltk["imports_resolved"] != ["HciLeLtkReqReplCmd"]:
        raise RuntimeError("Apollo Main positive LTK child changed")
    encrypt_path = G2 / "build/c-firmware/20261015/main-smp-encrypt-ind-537be6/receipt.json"
    encrypt, encrypt_ref = receipt(encrypt_path)
    if encrypt["status"] != "PASS_EXPERIMENTAL_MAIN_SMP_ENCRYPT_IND_C" or \
            encrypt["base_sha256"] != ltk["linked_sha256"] or \
            encrypt["imports_resolved"] != ["audio_ble_smp_encrypt_ind_537be6"]:
        raise RuntimeError("Apollo Main SMP encrypt-indication child changed")
    stk_path = G2 / "build/c-firmware/20261015/main-smp-get-stk-537c4c/receipt.json"
    stk, stk_ref = receipt(stk_path)
    if stk["status"] != "PASS_EXPERIMENTAL_MAIN_SMP_GET_STK_C" or \
            stk["base_sha256"] != encrypt["linked_sha256"] or \
            stk["imports_resolved"] != ["audio_ble_smp_get_stk_537c4c"]:
        raise RuntimeError("Apollo Main SMP STK getter changed")
    sec_interface_path = G2 / "build/c-firmware/20261015/main-dm-sec-interface-78a898/receipt.json"
    sec_interface, sec_interface_ref = receipt(sec_interface_path)
    if sec_interface["status"] != "PASS_EXPERIMENTAL_MAIN_DM_SEC_INTERFACE_C" or \
            sec_interface["base_sha256"] != stk["linked_sha256"] or \
            sec_interface["imports_resolved"] != ["audio_ble_dm_security_table"]:
        raise RuntimeError("Apollo Main DM security interface changed")
    phy_interface_path = G2 / "build/c-firmware/20261015/main-dm-phy-interface-78a85c/receipt.json"
    phy_interface, phy_interface_ref = receipt(phy_interface_path)
    if phy_interface["status"] != "PASS_EXPERIMENTAL_MAIN_DM_PHY_INTERFACE_C" or \
            phy_interface["base_sha256"] != sec_interface["linked_sha256"] or \
            phy_interface["imports_resolved"] != ["audio_ble_dm_phy_table"]:
        raise RuntimeError("Apollo Main DM PHY interface changed")
    lesc_interface_path = G2 / "build/c-firmware/20261015/main-dm-lesc-interface-78a8a4/receipt.json"
    lesc_interface, lesc_interface_ref = receipt(lesc_interface_path)
    if lesc_interface["status"] != "PASS_EXPERIMENTAL_MAIN_DM_LESC_INTERFACE_C" or \
            lesc_interface["base_sha256"] != phy_interface["linked_sha256"] or \
            lesc_interface["imports_resolved"] != ["audio_ble_dm_lesc_table"]:
        raise RuntimeError("Apollo Main DM LESC interface changed")
    priv_aes_interface_path = G2 / "build/c-firmware/20261015/main-dm-priv-aes-interface-78a874/receipt.json"
    priv_aes_interface, priv_aes_interface_ref = receipt(priv_aes_interface_path)
    if priv_aes_interface["status"] != "PASS_EXPERIMENTAL_MAIN_DM_PRIV_AES_INTERFACE_C" or \
            priv_aes_interface["base_sha256"] != lesc_interface["linked_sha256"] or \
            priv_aes_interface["imports_resolved"] != ["audio_ble_dm_priv_table_b"]:
        raise RuntimeError("Apollo Main DM privacy AES interface changed")
    mram_path = G2 / "build/c-firmware/20261015/main-mram-records-7ff000/receipt.json"
    mram, mram_ref = receipt(mram_path)
    if mram["status"] != "PASS_EXPERIMENTAL_MAIN_MRAM_RECORDS_C" or \
            mram["base_sha256"] != priv_aes_interface["linked_sha256"] or \
            mram["imports_resolved"] != ["audio_ble_mram_records_7ff000", "audio_ble_privacy_nvm_records"] or \
            mram["section_type"] != "NOBITS" or mram["section_bytes"] != 2560:
        raise RuntimeError("Apollo Main MRAM record binding changed")
    priv_interface_path = G2 / "build/c-firmware/20261015/main-dm-priv-interface-78a868/receipt.json"
    priv_interface, priv_interface_ref = receipt(priv_interface_path)
    if priv_interface["status"] != "PASS_EXPERIMENTAL_MAIN_DM_PRIV_INTERFACE_C" or \
            priv_interface["base_sha256"] != mram["linked_sha256"] or \
            priv_interface["imports_resolved"] != ["audio_ble_dm_priv_table_a"] or \
            len(priv_interface["imports_added"]) != 6:
        raise RuntimeError("Apollo Main primary privacy interface changed")
    addr_enable_path = G2 / "build/c-firmware/20261015/main-hci-addr-resolution-enable-52b7f6/receipt.json"
    addr_enable, addr_enable_ref = receipt(addr_enable_path)
    if addr_enable["status"] != "PASS_EXPERIMENTAL_MAIN_HCI_ADDR_RES_ENABLE_C" or \
            addr_enable["base_sha256"] != priv_interface["linked_sha256"] or \
            addr_enable["imports_resolved"] != ["HciLeSetAddrResolutionEnable"]:
        raise RuntimeError("Apollo Main address resolution command changed")
    hci_priv_path = G2 / "build/c-firmware/20261015/main-hci-privacy-commands-52b744/receipt.json"
    hci_priv, hci_priv_ref = receipt(hci_priv_path)
    if hci_priv["status"] != "PASS_EXPERIMENTAL_MAIN_HCI_PRIVACY_COMMANDS_C" or \
            hci_priv["base_sha256"] != addr_enable["linked_sha256"] or \
            len(hci_priv["imports_resolved"]) != 4:
        raise RuntimeError("Apollo Main privacy HCI commands changed")
    dev_priv_path = G2 / "build/c-firmware/20261015/main-dm-dev-priv-forward-4b2ea6/receipt.json"
    dev_priv, dev_priv_ref = receipt(dev_priv_path)
    if dev_priv["status"] != "PASS_EXPERIMENTAL_MAIN_DM_DEV_PRIV_FORWARD_C" or \
            dev_priv["base_sha256"] != hci_priv["linked_sha256"] or \
            dev_priv["imports_resolved"] != ["dmDevPassEvtToDevPriv"]:
        raise RuntimeError("Apollo Main device privacy forwarding changed")
    adv_reset_path = G2 / "build/c-firmware/20261015/main-dm-adv-reset-4ba45c/receipt.json"
    adv_reset, adv_reset_ref = receipt(adv_reset_path)
    if adv_reset["status"] != "PASS_EXPERIMENTAL_MAIN_DM_ADV_RESET_C" or \
            adv_reset["base_sha256"] != dev_priv["linked_sha256"] or \
            adv_reset["source_owned_symbols"] != ["audio_ble_dm_adv_reset_4ba45c"] or \
            adv_reset["imports_added"] or adv_reset["imports_resolved"]:
        raise RuntimeError("Apollo Main advertising reset changed")
    adv_msg_path = G2 / "build/c-firmware/20261015/main-dm-adv-msg-4ba6ac/receipt.json"
    adv_msg, adv_msg_ref = receipt(adv_msg_path)
    if adv_msg["status"] != "PASS_EXPERIMENTAL_MAIN_DM_ADV_MSG_C" or \
            adv_msg["base_sha256"] != adv_reset["linked_sha256"] or \
            adv_msg["unresolved_after"] != 196 or len(adv_msg["imports_added"]) != 4:
        raise RuntimeError("Apollo Main advertising message stage changed")
    hci_adv_path = G2 / "build/c-firmware/20261015/main-hci-adv-commands-52b3b0/receipt.json"
    hci_adv, hci_adv_ref = receipt(hci_adv_path)
    if hci_adv["status"] != "PASS_EXPERIMENTAL_MAIN_HCI_ADV_COMMANDS_C" or \
            hci_adv["base_sha256"] != adv_msg["linked_sha256"] or \
            hci_adv["unresolved_after"] != 193 or len(hci_adv["imports_resolved"]) != 3:
        raise RuntimeError("Apollo Main advertising HCI commands changed")
    adv_config_path = G2 / "build/c-firmware/20261015/main-dm-adv-config-lower-4b9a80/receipt.json"
    adv_config, adv_config_ref = receipt(adv_config_path)
    if adv_config["status"] != "PASS_EXPERIMENTAL_MAIN_DM_ADV_CONFIG_LOWER_C" or \
            adv_config["base_sha256"] != hci_adv["linked_sha256"] or \
            adv_config["unresolved_after"] != 192 or \
            adv_config["imports_resolved"] != ["audio_ble_dm_adv_config_lower_4b9a80"]:
        raise RuntimeError("Apollo Main advertising configuration changed")
    adv_extent_path = G2 / "build/c-firmware/20261015/main-dm-adv-control-extent-34/receipt.json"
    adv_extent, adv_extent_ref = receipt(adv_extent_path)
    if adv_extent["status"] != "PASS_EXPERIMENTAL_MAIN_DM_ADV_CONTROL_ALREADY_C_OWNED" or \
            adv_extent["base_sha256"] != adv_config["linked_sha256"] or \
            adv_extent["old_size"] != 0x34 or adv_extent["new_size"] != 0x34 or \
            adv_extent["relocations_verified"] != 24:
        raise RuntimeError("Apollo Main advertising control extent changed")
    adv_hci_path = G2 / "build/c-firmware/20261015/main-dm-adv-hci-4ba4b0/receipt.json"
    adv_hci, adv_hci_ref = receipt(adv_hci_path)
    if adv_hci["status"] != "PASS_EXPERIMENTAL_MAIN_DM_ADV_HCI_C" or \
            adv_hci["base_sha256"] != adv_extent["linked_sha256"] or \
            adv_hci["unresolved_after"] != 192 or \
            adv_hci["imports_resolved"] != ["audio_ble_dm_adv_table"] or \
            adv_hci["imports_added"] != ["audio_ble_dm_adv_gen_conn_complete_4b310a"]:
        raise RuntimeError("Apollo Main advertising HCI handler changed")
    adv_gen_path = G2 / "build/c-firmware/20261015/main-dm-adv-gen-conn-4b310a/receipt.json"
    adv_gen, adv_gen_ref = receipt(adv_gen_path)
    if adv_gen["status"] != "PASS_EXPERIMENTAL_MAIN_DM_ADV_GEN_CONN_C" or \
            adv_gen["base_sha256"] != adv_hci["linked_sha256"] or \
            adv_gen["unresolved_after"] != 192 or \
            adv_gen["imports_resolved"] != ["audio_ble_dm_adv_gen_conn_complete_4b310a"] or \
            adv_gen["imports_added"] != ["audio_ble_dm_dev_pass_hci_conn_4d29c2"]:
        raise RuntimeError("Apollo Main synthetic advertising connection completion changed")
    dev_conn_path = G2 / "build/c-firmware/20261015/main-dm-dev-pass-hci-conn-4d29c2/receipt.json"
    dev_conn, dev_conn_ref = receipt(dev_conn_path)
    if dev_conn["status"] != "PASS_EXPERIMENTAL_MAIN_DM_DEV_PASS_HCI_CONN_C" or \
            dev_conn["base_sha256"] != adv_gen["linked_sha256"] or \
            dev_conn["unresolved_after"] != 191 or \
            dev_conn["imports_resolved"] != ["audio_ble_dm_dev_pass_hci_conn_4d29c2"]:
        raise RuntimeError("Apollo Main connection callback bridge changed")
    flag_path = G2 / "build/c-firmware/20261015/main-bootloader-flag-7fe000/receipt.json"
    flag, flag_ref = receipt(flag_path)
    if flag["status"] != "PASS_EXPERIMENTAL_MAIN_BOOTLOADER_FLAG_C" or \
            flag["base_sha256"] != dev_conn["linked_sha256"] or \
            flag["unresolved_before"] != 191 or flag["unresolved_after"] != 190 or \
            flag["imports_resolved"] != ["audio_ble_bootloader_flag"] or \
            flag["placement_address"] != "0x007fe000" or flag["section_bytes"] != 16:
        raise RuntimeError("Apollo Main OTA bootloader flag reservation changed")
    als_path = G2 / "build/c-firmware/20261015/main-als-sync-registry-4ae73c/receipt.json"
    als, als_ref = receipt(als_path)
    if als["status"] != "PASS_EXPERIMENTAL_MAIN_ALS_SYNC_REGISTRY_C" or \
            als["base_sha256"] != flag["linked_sha256"] or \
            als["native_c_cases"] != 100 or \
            als["unresolved_before"] != 190 or als["unresolved_after"] != 189 or \
            als["imports_resolved"] != ["audio_uart_registry_callback_4ae73c"]:
        raise RuntimeError("Apollo Main ALS sync registry callback changed")
    display_table_path = G2 / "build/c-firmware/20261015/main-display-manager-state-table-776a3c/receipt.json"
    display_table, display_table_ref = receipt(display_table_path)
    if display_table["status"] != "PASS_EXPERIMENTAL_MAIN_DISPLAY_MANAGER_TABLE_C" or \
            display_table["base_sha256"] != als["linked_sha256"] or \
            display_table["native_c_cases"] != 60 or \
            display_table["interface_words"] != 6 or \
            display_table["unresolved_before"] != 189 or \
            display_table["unresolved_after"] != 188 or \
            display_table["imports_resolved"] != ["g2_display_state_table"]:
        raise RuntimeError("Apollo Main display manager interface changed")
    tracepoint_path = G2 / "build/c-firmware/20261015/main-tracepoint-registry-5eeec4/receipt.json"
    tracepoint, tracepoint_ref = receipt(tracepoint_path)
    if tracepoint["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_REGISTRY_C" or \
            tracepoint["base_sha256"] != display_table["linked_sha256"] or \
            tracepoint["native_c_cases"] != 160 or \
            tracepoint["unresolved_before"] != 188 or \
            tracepoint["unresolved_after"] != 189 or \
            tracepoint["imports_resolved"] != ["audio_uart_registry_callback_5eeec4"] or \
            tracepoint["imports_added"] != ["audio_tracepoint_handle_ble_data_5ee8bc", "audio_tracepoint_handle_slave_file_list_5eeb98"]:
        raise RuntimeError("Apollo Main tracepoint registry callback changed")
    trace_ble_path = G2 / "build/c-firmware/20261015/main-tracepoint-ble-data-5ee8bc/receipt.json"
    trace_ble, trace_ble_ref = receipt(trace_ble_path)
    if trace_ble["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_BLE_DATA_C" or \
            trace_ble["base_sha256"] != tracepoint["linked_sha256"] or \
            trace_ble["native_c_cases"] != 280 or \
            trace_ble["unresolved_before"] != 189 or \
            trace_ble["unresolved_after"] != 193 or \
            trace_ble["imports_resolved"] != ["audio_tracepoint_handle_ble_data_5ee8bc"]:
        raise RuntimeError("Apollo Main tracepoint BLE-data child changed")
    trace_ram_path = G2 / "build/c-firmware/20261015/main-tracepoint-decode-buffer-2037b9c0/receipt.json"
    trace_ram, trace_ram_ref = receipt(trace_ram_path)
    if trace_ram["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_DECODE_RAM_C" or \
            trace_ram["base_sha256"] != trace_ble["linked_sha256"] or \
            trace_ram["placement_address"] != "0x2037b9c0" or \
            trace_ram["section_bytes"] != 0x206 or \
            trace_ram["unresolved_before"] != 193 or \
            trace_ram["unresolved_after"] != 192 or \
            trace_ram["imports_resolved"] != ["audio_tracepoint_decode_buffer"]:
        raise RuntimeError("Apollo Main tracepoint decode RAM reservation changed")
    delete_all_path = G2 / "build/c-firmware/20261015/main-tracepoint-delete-all-5ee7b4/receipt.json"
    delete_all, delete_all_ref = receipt(delete_all_path)
    if delete_all["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_DELETE_ALL_C" or \
            delete_all["base_sha256"] != trace_ram["linked_sha256"] or \
            delete_all["native_c_cases"] != 90 or \
            delete_all["unresolved_before"] != 192 or \
            delete_all["unresolved_after"] != 194 or \
            delete_all["imports_resolved"] != ["audio_tracepoint_delete_all_5ee7b4"]:
        raise RuntimeError("Apollo Main tracepoint delete-all handler changed")
    reply_ram_path = G2 / "build/c-firmware/20261015/main-tracepoint-reply-buffer-2037bbc8/receipt.json"
    reply_ram, reply_ram_ref = receipt(reply_ram_path)
    if reply_ram["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_REPLY_RAM_C" or \
            reply_ram["base_sha256"] != delete_all["linked_sha256"] or \
            reply_ram["placement_address"] != "0x2037bbc8" or \
            reply_ram["section_bytes"] != 0x206 or \
            reply_ram["unresolved_before"] != 194 or \
            reply_ram["unresolved_after"] != 193 or \
            reply_ram["imports_resolved"] != ["audio_tracepoint_reply_buffer"]:
        raise RuntimeError("Apollo Main tracepoint reply RAM reservation changed")
    reply_route_path = G2 / "build/c-firmware/20261015/main-tracepoint-reply-result-5ee134/receipt.json"
    reply_route, reply_route_ref = receipt(reply_route_path)
    if reply_route["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_REPLY_ROUTING_C" or \
            reply_route["base_sha256"] != reply_ram["linked_sha256"] or \
            reply_route["native_c_cases"] != 240 or \
            reply_route["unresolved_before"] != 193 or \
            reply_route["unresolved_after"] != 194 or \
            reply_route["imports_resolved"] != ["audio_tracepoint_reply_result_5ee134"] or \
            set(reply_route["imports_added"]) != {"audio_tracepoint_send_to_master_5ee066", "audio_tracepoint_send_to_phone_5edfd8"}:
        raise RuntimeError("Apollo Main tracepoint reply routing changed")
    send_reply_path = G2 / "build/c-firmware/20261015/main-tracepoint-send-reply-5edfd8-5ee066/receipt.json"
    send_reply, send_reply_ref = receipt(send_reply_path)
    if send_reply["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_SEND_REPLY_C" or \
            send_reply["base_sha256"] != reply_route["linked_sha256"] or \
            send_reply["native_c_cases"] != 540 or \
            send_reply["unresolved_before"] != 194 or \
            send_reply["unresolved_after"] != 194 or \
            set(send_reply["imports_resolved"]) != {"audio_tracepoint_send_to_master_5ee066", "audio_tracepoint_send_to_phone_5edfd8"} or \
            set(send_reply["imports_added"]) != {"audio_tracepoint_encode_response_5eded0", "audio_tracepoint_encoded_buffer"}:
        raise RuntimeError("Apollo Main tracepoint send-reply children changed")
    encoder_path = G2 / "build/c-firmware/20261015/main-tracepoint-encode-response-5eded0/receipt.json"
    encoder, encoder_ref = receipt(encoder_path)
    if encoder["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_ENCODER_C" or \
            encoder["base_sha256"] != send_reply["linked_sha256"] or \
            encoder["native_c_cases"] != 180 or \
            encoder["placement_address"] != "0x2037b6c0" or \
            encoder["section_bytes"] != 0x300 or \
            encoder["unresolved_before"] != 194 or \
            encoder["unresolved_after"] != 192 or \
            set(encoder["imports_resolved"]) != {"audio_tracepoint_encode_response_5eded0", "audio_tracepoint_encoded_buffer"} or \
            encoder["imports_added"]:
        raise RuntimeError("Apollo Main tracepoint response encoder changed")
    trace_desc_path = G2 / "build/c-firmware/20261015/main-tracepoint-pb-descriptor-77cd84/receipt.json"
    trace_desc, trace_desc_ref = receipt(trace_desc_path)
    if trace_desc["status"] != "PASS_AUTHENTICATED_MAIN_TRACEPOINT_PB_DESCRIPTOR_C" or \
            trace_desc["base_sha256"] != encoder["linked_sha256"] or \
            trace_desc["authenticated_relocations"] != 11 or \
            len(trace_desc["descriptors"]) != 4 or \
            trace_desc["unresolved_before"] != 192 or \
            trace_desc["unresolved_after"] != 191 or \
            trace_desc["imports_resolved"] != ["audio_tracepoint_message_descriptor"] or \
            trace_desc["imports_added"]:
        raise RuntimeError("Apollo Main tracepoint nanopb descriptor changed")
    trace_delete_path = G2 / "build/c-firmware/20261015/main-tracepoint-delete-file-5ee488/receipt.json"
    trace_delete, trace_delete_ref = receipt(trace_delete_path)
    if trace_delete["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_DELETE_FILE_C" or \
            trace_delete["base_sha256"] != trace_desc["linked_sha256"] or \
            trace_delete["native_c_cases"] != 120 or \
            trace_delete["unresolved_before"] != 191 or \
            trace_delete["unresolved_after"] != 194 or \
            trace_delete["imports_resolved"] != ["audio_tracepoint_delete_file_5ee488"] or \
            set(trace_delete["imports_added"]) != {"audio_tracepoint_validate_file_name_5ede30", "audio_tracepoint_resolve_file_path_5eddf6", "audio_tracepoint_storage_lock_47e088", "audio_tracepoint_storage_unlink_47498c"}:
        raise RuntimeError("Apollo Main tracepoint single-file deletion changed")
    trace_resolve_path = G2 / "build/c-firmware/20261015/main-tracepoint-resolve-file-path-5eddf6/receipt.json"
    trace_resolve, trace_resolve_ref = receipt(trace_resolve_path)
    if trace_resolve["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_PATH_RESOLVER_C" or \
            trace_resolve["base_sha256"] != trace_delete["linked_sha256"] or \
            trace_resolve["native_c_cases"] != 48 or \
            trace_resolve["unresolved_before"] != 194 or \
            trace_resolve["unresolved_after"] != 194 or \
            trace_resolve["imports_resolved"] != ["audio_tracepoint_resolve_file_path_5eddf6"] or \
            trace_resolve["imports_added"] != ["audio_tracepoint_parse_sequence_5edaf0"]:
        raise RuntimeError("Apollo Main tracepoint pathname resolver changed")
    trace_parse_path = G2 / "build/c-firmware/20261015/main-tracepoint-parse-sequence-5edaf0/receipt.json"
    trace_parse, trace_parse_ref = receipt(trace_parse_path)
    if trace_parse["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_SEQUENCE_PARSER_C" or \
            trace_parse["base_sha256"] != trace_resolve["linked_sha256"] or \
            trace_parse["native_c_cases"] != 45 or \
            trace_parse["unresolved_before"] != 194 or \
            trace_parse["unresolved_after"] != 193 or \
            trace_parse["imports_resolved"] != ["audio_tracepoint_parse_sequence_5edaf0"] or \
            trace_parse["imports_added"]:
        raise RuntimeError("Apollo Main tracepoint sequence parser changed")
    trace_validate_path = G2 / "build/c-firmware/20261015/main-tracepoint-validate-file-name-5ede30/receipt.json"
    trace_validate, trace_validate_ref = receipt(trace_validate_path)
    if trace_validate["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_FILENAME_VALIDATOR_C" or \
            trace_validate["base_sha256"] != trace_parse["linked_sha256"] or \
            trace_validate["native_c_cases"] != 264 or \
            trace_validate["unresolved_before"] != 193 or \
            trace_validate["unresolved_after"] != 193 or \
            trace_validate["imports_resolved"] != ["audio_tracepoint_validate_file_name_5ede30"] or \
            trace_validate["imports_added"] != ["audio_tracepoint_format_file_path_5edba2"]:
        raise RuntimeError("Apollo Main tracepoint filename validator changed")
    trace_format_path = G2 / "build/c-firmware/20261015/main-tracepoint-format-file-path-5edba2/receipt.json"
    trace_format, trace_format_ref = receipt(trace_format_path)
    if trace_format["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_PATH_FORMAT_C" or \
            trace_format["base_sha256"] != trace_validate["linked_sha256"] or \
            trace_format["native_c_cases"] != 25 or \
            trace_format["unresolved_before"] != 193 or \
            trace_format["unresolved_after"] != 192 or \
            trace_format["imports_resolved"] != ["audio_tracepoint_format_file_path_5edba2"] or \
            trace_format["imports_added"]:
        raise RuntimeError("Apollo Main tracepoint filename path formatter changed")
    trace_active_path = G2 / "build/c-firmware/20261015/main-tracepoint-close-active-file-47e06a/receipt.json"
    trace_active, trace_active_ref = receipt(trace_active_path)
    if trace_active["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_ACTIVE_FILE_C" or \
            trace_active["base_sha256"] != trace_format["linked_sha256"] or \
            trace_active["native_c_cases"] != 8 or \
            trace_active["placement_address"] != "0x20074ae0" or \
            trace_active["section_bytes"] != 4 or \
            trace_active["unresolved_before"] != 192 or \
            trace_active["unresolved_after"] != 191 or \
            trace_active["imports_resolved"] != ["audio_tracepoint_storage_lock_47e088"] or \
            trace_active["imports_added"]:
        raise RuntimeError("Apollo Main tracepoint active-file close path changed")
    trace_unlink_path = G2 / "build/c-firmware/20261015/main-tracepoint-storage-unlink-47498c/receipt.json"
    trace_unlink, trace_unlink_ref = receipt(trace_unlink_path)
    if trace_unlink["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_UNLINK_FACADE_C" or \
            trace_unlink["base_sha256"] != trace_active["linked_sha256"] or \
            trace_unlink["native_c_cases"] != 72 or \
            trace_unlink["placement_address"] != "0x200746a8" or \
            trace_unlink["section_bytes"] != 4 or \
            trace_unlink["unresolved_before"] != 191 or \
            trace_unlink["unresolved_after"] != 192 or \
            trace_unlink["imports_resolved"] != ["audio_tracepoint_storage_unlink_47498c"] or \
            set(trace_unlink["imports_added"]) != {"audio_file_errno_location_439cc4", "audio_file_lfs_remove_4cfa76"}:
        raise RuntimeError("Apollo Main unlink facade changed")
    file_errno_path = G2 / "build/c-firmware/20261015/main-file-errno-location-439cc4/receipt.json"
    file_errno, file_errno_ref = receipt(file_errno_path)
    if file_errno["status"] != "PASS_EXPERIMENTAL_MAIN_FILE_ERRNO_LOCATION_C" or \
            file_errno["base_sha256"] != trace_unlink["linked_sha256"] or \
            file_errno["native_c_cases"] != 4 or \
            file_errno["unresolved_before"] != 192 or \
            file_errno["unresolved_after"] != 191 or \
            file_errno["imports_resolved"] != ["audio_file_errno_location_439cc4"] or \
            file_errno["imports_added"]:
        raise RuntimeError("Apollo Main errno location changed")
    lfs_remove_path = G2 / "build/c-firmware/20261015/main-file-lfs-remove-wrapper-4cfa76/receipt.json"
    lfs_remove, lfs_remove_ref = receipt(lfs_remove_path)
    if lfs_remove["status"] != "PASS_EXPERIMENTAL_MAIN_FILE_LFS_REMOVE_WRAPPER_C" or \
            lfs_remove["base_sha256"] != file_errno["linked_sha256"] or \
            lfs_remove["native_c_cases"] != 4 or \
            lfs_remove["unresolved_before"] != 191 or \
            lfs_remove["unresolved_after"] != 191 or \
            lfs_remove["imports_resolved"] != ["audio_file_lfs_remove_4cfa76"] or \
            lfs_remove["imports_added"] != ["audio_file_lfs_remove_core_4ce4dc"]:
        raise RuntimeError("Apollo Main LittleFS remove wrapper changed")
    lfs_remove_core_path = G2 / "build/c-firmware/20261015/main-file-lfs-remove-core-4ce4dc/receipt.json"
    lfs_remove_core, lfs_remove_core_ref = receipt(lfs_remove_core_path)
    if lfs_remove_core["status"] != "PASS_EXPERIMENTAL_MAIN_FILE_LFS_REMOVE_CORE_C" or \
            lfs_remove_core["base_sha256"] != lfs_remove["linked_sha256"] or \
            lfs_remove_core["native_c_cases"] != 40 or \
            lfs_remove_core["unresolved_before"] != 191 or \
            lfs_remove_core["unresolved_after"] != 191 or \
            lfs_remove_core["imports_resolved"] != ["audio_file_lfs_remove_core_4ce4dc"] or \
            lfs_remove_core["imports_added"] != ["audio_file_lfs_dir_drop_4cc5a2"]:
        raise RuntimeError("Apollo Main LittleFS remove core changed")
    lfs_dir_drop_path = G2 / "build/c-firmware/20261015/main-file-lfs-dir-drop-4cc5a2/receipt.json"
    lfs_dir_drop, lfs_dir_drop_ref = receipt(lfs_dir_drop_path)
    if lfs_dir_drop["status"] != "PASS_EXPERIMENTAL_MAIN_FILE_LFS_DIR_DROP_C" or \
            lfs_dir_drop["base_sha256"] != lfs_remove_core["linked_sha256"] or \
            lfs_dir_drop["native_c_cases"] != 8 or \
            lfs_dir_drop["unresolved_before"] != 191 or \
            lfs_dir_drop["unresolved_after"] != 190 or \
            lfs_dir_drop["imports_resolved"] != ["audio_file_lfs_dir_drop_4cc5a2"] or \
            lfs_dir_drop["imports_added"]:
        raise RuntimeError("Apollo Main LittleFS directory drop changed")
    trace_inventory_path = G2 / "build/c-firmware/20261015/main-tracepoint-insert-file-sorted-5edbb0/receipt.json"
    trace_inventory, trace_inventory_ref = receipt(trace_inventory_path)
    if trace_inventory["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_SORTED_INSERT_C" or \
            trace_inventory["base_sha256"] != lfs_dir_drop["linked_sha256"] or \
            trace_inventory["native_c_cases"] != 50 or \
            trace_inventory["placement_address"] != "0x2037cd24" or \
            trace_inventory["section_bytes"] != 0x88 or \
            trace_inventory["unresolved_before"] != 190 or \
            trace_inventory["unresolved_after"] != 190 or \
            trace_inventory["imports_resolved"] or trace_inventory["imports_added"]:
        raise RuntimeError("Apollo Main tracepoint sorted inventory changed")
    for entry in trace_inventory["sources"]:
        if sha(ROOT / entry["path"]) != entry["sha256"]:
            raise RuntimeError("Apollo Main tracepoint inventory source changed")
    request_path = G2 / "build/c-firmware/20261015/main-tracepoint-request-file-name-5ee1f8/receipt.json"
    request, request_ref = receipt(request_path)
    if request["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_REQUEST_FILE_NAME_C" or \
            request["base_sha256"] != trace_inventory["linked_sha256"] or \
            request["native_c_cases"] != 64 or request["format_native_c_cases"] != 64 or \
            request["placement_address"] != "0x20074ae4" or request["section_bytes"] != 1 or \
            request["unresolved_before"] != 190 or request["unresolved_after"] != 192 or \
            request["imports_resolved"] != ["audio_tracepoint_request_file_name_5ee1f8"] or \
            set(request["imports_added"]) != {"audio_tracepoint_reset_pull_478110", "audio_tracepoint_prepare_pull_48ec9e", "audio_tracepoint_scan_files_5edc5a"}:
        raise RuntimeError("Apollo Main tracepoint file-list request changed")
    for entry in request["sources"]:
        if sha(ROOT / entry["path"]) != entry["sha256"]:
            raise RuntimeError("Apollo Main tracepoint request source changed")
    scan_path = G2 / "build/c-firmware/20261015/main-tracepoint-scan-files-5edc5a/receipt.json"
    scan, scan_ref = receipt(scan_path)
    if scan["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_SCAN_FILES_C" or \
            scan["base_sha256"] != request["linked_sha256"] or scan["native_c_cases"] != 32 or \
            scan["unresolved_before"] != 192 or scan["unresolved_after"] != 195 or \
            scan["imports_resolved"] != ["audio_tracepoint_scan_files_5edc5a"] or \
            set(scan["imports_added"]) != {"audio_tracepoint_dir_open_474b02", "audio_tracepoint_dir_read_474bb8", "audio_tracepoint_dir_close_474c66", "audio_tracepoint_file_size_5edb68"}:
        raise RuntimeError("Apollo Main tracepoint file scan changed")
    file_size_path = G2 / "build/c-firmware/20261015/main-tracepoint-file-size-5edb68/receipt.json"
    file_size, file_size_ref = receipt(file_size_path)
    if file_size["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_FILE_SIZE_C" or \
            file_size["base_sha256"] != scan["linked_sha256"] or \
            file_size["native_c_cases"] != 30 or \
            file_size["unresolved_before"] != 195 or file_size["unresolved_after"] != 194 or \
            file_size["imports_resolved"] != ["audio_tracepoint_file_size_5edb68"] or \
            file_size["imports_added"]:
        raise RuntimeError("Apollo Main tracepoint file size changed")
    prepare_path = G2 / "build/c-firmware/20261015/main-tracepoint-prepare-pull-48ec9e/receipt.json"
    prepare, prepare_ref = receipt(prepare_path)
    if prepare["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_PREPARE_PULL_C" or \
            prepare["base_sha256"] != file_size["linked_sha256"] or \
            prepare["native_c_cases"] != 15 or \
            prepare["unresolved_before"] != 194 or prepare["unresolved_after"] != 195 or \
            prepare["imports_resolved"] != ["audio_tracepoint_prepare_pull_48ec9e"] or \
            set(prepare["imports_added"]) != {"audio_tracepoint_pull_ready_48eb90", "audio_tracepoint_pull_initialize_47e1ec"}:
        raise RuntimeError("Apollo Main tracepoint pull preparation changed")
    reset_path = G2 / "build/c-firmware/20261015/main-tracepoint-reset-pull-478110/receipt.json"
    reset, reset_ref = receipt(reset_path)
    if reset["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_RESET_PULL_C" or \
            reset["base_sha256"] != prepare["linked_sha256"] or \
            reset["native_c_cases"] != 12 or \
            reset["placement_address"] != "0x20074f8f" or reset["section_bytes"] != 1 or \
            reset["unresolved_before"] != 195 or reset["unresolved_after"] != 194 or \
            reset["imports_resolved"] != ["audio_tracepoint_reset_pull_478110"] or reset["imports_added"]:
        raise RuntimeError("Apollo Main tracepoint pull reset changed")
    dir_facade_path = G2 / "build/c-firmware/20261015/main-tracepoint-dir-facade-474b02/receipt.json"
    dir_facade, dir_facade_ref = receipt(dir_facade_path)
    if dir_facade["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_DIR_FACADE_C" or \
            dir_facade["base_sha256"] != reset["linked_sha256"] or \
            dir_facade["native_c_cases"] != 162 or \
            dir_facade["placement_address"] != "0x200701e8" or dir_facade["section_bytes"] != 0x101 or \
            dir_facade["unresolved_before"] != 194 or dir_facade["unresolved_after"] != 191 or \
            set(dir_facade["imports_resolved"]) != {"audio_tracepoint_dir_open_474b02", "audio_tracepoint_dir_read_474bb8", "audio_tracepoint_dir_close_474c66"} or \
            dir_facade["imports_added"]:
        raise RuntimeError("Apollo Main tracepoint directory facade changed")
    pull_init_path = G2 / "build/c-firmware/20261015/main-tracepoint-pull-initialize-47e1ec/receipt.json"
    pull_init, pull_init_ref = receipt(pull_init_path)
    if pull_init["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_PULL_INITIALIZE_C" or \
            pull_init["base_sha256"] != dir_facade["linked_sha256"] or \
                        pull_init["native_c_cases"] != 36 or \
            pull_init["placement_addresses"] != {"pending": "0x20074ad8", "enabled": "0x20075038"} or \
            pull_init["section_bytes"] != {"pending": 8, "enabled": 1} or \
            pull_init["unresolved_before"] != 191 or pull_init["unresolved_after"] != 190 or \
            pull_init["imports_resolved"] != ["audio_tracepoint_pull_initialize_47e1ec"] or pull_init["imports_added"]:
        raise RuntimeError("Apollo Main tracepoint pull initialization changed")
    pull_ready_path = G2 / "build/c-firmware/20261015/main-tracepoint-pull-ready-48eb90/receipt.json"
    pull_ready, pull_ready_ref = receipt(pull_ready_path)
    if pull_ready["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_PULL_READY_C" or \
            pull_ready["base_sha256"] != pull_init["linked_sha256"] or \
                        pull_ready["native_c_cases"] != 256 or \
            pull_ready["placement_addresses"] != {"failure_count": "0x20074ac0", "backend_ready": "0x20075035"} or \
            pull_ready["section_bytes"] != {"failure_count": 4, "backend_ready": 1} or \
            pull_ready["unresolved_before"] != 190 or pull_ready["unresolved_after"] != 192 or \
            pull_ready["imports_resolved"] != ["audio_tracepoint_pull_ready_48eb90"] or \
            set(pull_ready["imports_added"]) != {"audio_tracepoint_pull_backend_init_47dfec", "audio_tracepoint_pull_write_batch_47e178", "audio_tracepoint_pull_complete_47e220"}:
        raise RuntimeError("Apollo Main tracepoint pull readiness changed")
    pull_complete_path = G2 / "build/c-firmware/20261015/main-tracepoint-pull-complete-47e220/receipt.json"
    pull_complete, pull_complete_ref = receipt(pull_complete_path)
    if pull_complete["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_PULL_COMPLETE_C" or \
            pull_complete["base_sha256"] != pull_ready["linked_sha256"] or \
                        pull_complete["native_c_cases"] != 5 or \
            pull_complete["unresolved_before"] != 192 or pull_complete["unresolved_after"] != 192 or \
            pull_complete["imports_resolved"] != ["audio_tracepoint_pull_complete_47e220"] or \
            pull_complete["imports_added"] != ["audio_tracepoint_file_close_474910"]:
        raise RuntimeError("Apollo Main tracepoint pull completion changed")
    pull_write_path = G2 / "build/c-firmware/20261015/main-tracepoint-pull-write-batch-47e178/receipt.json"
    pull_write, pull_write_ref = receipt(pull_write_path)
    if pull_write["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_PULL_WRITE_BATCH_C" or \
            pull_write["base_sha256"] != pull_complete["linked_sha256"] or \
                        pull_write["native_c_cases"] != 144 or \
            pull_write["unresolved_before"] != 192 or pull_write["unresolved_after"] != 194 or \
            pull_write["imports_resolved"] != ["audio_tracepoint_pull_write_batch_47e178"] or \
            set(pull_write["imports_added"]) != {"audio_tracepoint_open_new_file_47e0c8", "audio_tracepoint_reopen_pending_file_47e144", "audio_tracepoint_file_write_474682"}:
        raise RuntimeError("Apollo Main tracepoint batch writer changed")
    reopen_path = G2 / "build/c-firmware/20261015/main-tracepoint-reopen-pending-file-47e144/receipt.json"
    reopen, reopen_ref = receipt(reopen_path)
    if reopen["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_REOPEN_PENDING_C" or \
            reopen["base_sha256"] != pull_write["linked_sha256"] or \
                        reopen["native_c_cases"] != 8 or \
            reopen["unresolved_before"] != 194 or reopen["unresolved_after"] != 195 or \
            reopen["imports_resolved"] != ["audio_tracepoint_reopen_pending_file_47e144"] or \
            set(reopen["imports_added"]) != {"audio_tracepoint_format_pull_path_47de0a", "audio_tracepoint_file_open_474550"}:
        raise RuntimeError("Apollo Main tracepoint pending reopen changed")
    pull_path_format_path = G2 / "build/c-firmware/20261015/main-tracepoint-format-pull-path-47de0a/receipt.json"
    pull_path_format, pull_path_format_ref = receipt(pull_path_format_path)
    if pull_path_format["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_FORMAT_PULL_PATH_C" or \
            pull_path_format["base_sha256"] != reopen["linked_sha256"] or \
                        pull_path_format["native_c_cases"] != 16 or \
            pull_path_format["unresolved_before"] != 195 or pull_path_format["unresolved_after"] != 194 or \
            pull_path_format["imports_resolved"] != ["audio_tracepoint_format_pull_path_47de0a"] or pull_path_format["imports_added"]:
        raise RuntimeError("Apollo Main tracepoint pull path formatter changed")
    open_new_path = G2 / "build/c-firmware/20261015/main-tracepoint-open-new-file-47e0c8/receipt.json"
    open_new, open_new_ref = receipt(open_new_path)
    if open_new["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_OPEN_NEW_FILE_C" or \
            open_new["base_sha256"] != pull_path_format["linked_sha256"] or \
                        open_new["native_c_cases"] != 144 or \
            open_new["placement_addresses"] != {"next_sequence": "0x20004188", "session_generation": "0x20074ad4"} or \
            open_new["section_bytes"] != {"next_sequence": 4, "session_generation": 4} or \
            open_new["unresolved_before"] != 194 or open_new["unresolved_after"] != 196 or \
            open_new["imports_resolved"] != ["audio_tracepoint_open_new_file_47e0c8"] or \
            set(open_new["imports_added"]) != {"audio_tracepoint_trim_old_files_47e090", "audio_tracepoint_write_state_47df28", "audio_tracepoint_build_header_48ed00"}:
        raise RuntimeError("Apollo Main tracepoint new-file creation changed")
    header_path = G2 / "build/c-firmware/20261015/main-tracepoint-build-header-48ed00/receipt.json"
    header, header_ref = receipt(header_path)
    if header["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_TPF1_HEADER_C" or \
            header["base_sha256"] != open_new["linked_sha256"] or \
            header["native_c_cases"] != 42 or \
            header["unresolved_before"] != 196 or header["unresolved_after"] != 196 or \
            header["imports_resolved"] != ["audio_tracepoint_build_header_48ed00"] or \
            header["imports_added"] != ["audio_tracepoint_version_47dd08"]:
        raise RuntimeError("Apollo Main TPF1 header changed")
    version_path = G2 / "build/c-firmware/20261015/main-tracepoint-version-47dd08/receipt.json"
    version, version_ref = receipt(version_path)
    if version["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_VERSION_C" or \
            version["base_sha256"] != header["linked_sha256"] or \
                        version["native_c_cases"] != 9 or \
            version["placement_address"] != "0x78c740" or version["section_bytes"] != 9 or \
            version["unresolved_before"] != 196 or version["unresolved_after"] != 195 or \
            version["imports_resolved"] != ["audio_tracepoint_version_47dd08"] or version["imports_added"]:
        raise RuntimeError("Apollo Main tracepoint version changed")
    trim_path = G2 / "build/c-firmware/20261015/main-tracepoint-trim-old-files-47e090/receipt.json"
    trim, trim_ref = receipt(trim_path)
    if trim["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_TRIM_OLD_FILES_C" or \
            trim["base_sha256"] != version["linked_sha256"] or \
                        trim["native_c_cases"] != 21 or \
            trim["unresolved_before"] != 195 or trim["unresolved_after"] != 195 or \
            trim["imports_resolved"] != ["audio_tracepoint_trim_old_files_47e090"] or \
            set(trim["imports_added"]) != {"audio_tracepoint_list_files_47deb4"}:
        raise RuntimeError("Apollo Main tracepoint retention changed")
    listing_path = G2 / "build/c-firmware/20261015/main-tracepoint-list-files-47deb4/receipt.json"
    listing, listing_ref = receipt(listing_path)
    if listing["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_LIST_FILES_C" or \
            listing["base_sha256"] != trim["linked_sha256"] or \
                        listing["native_c_cases"] != 14 or \
            listing["unresolved_before"] != 195 or listing["unresolved_after"] != 195 or \
            listing["imports_resolved"] != ["audio_tracepoint_list_files_47deb4"] or \
            listing["imports_added"] != ["audio_tracepoint_parse_file_entry_47de18"]:
        raise RuntimeError("Apollo Main tracepoint listing changed")
    entry_parser_path = G2 / "build/c-firmware/20261015/main-tracepoint-parse-file-entry-47de18/receipt.json"
    entry_parser, entry_parser_ref = receipt(entry_parser_path)
    if entry_parser["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_PARSE_FILE_ENTRY_C" or \
            entry_parser["base_sha256"] != listing["linked_sha256"] or \
                        entry_parser["native_c_cases"] != 16 or \
            entry_parser["unresolved_before"] != 195 or entry_parser["unresolved_after"] != 194 or \
            entry_parser["imports_resolved"] != ["audio_tracepoint_parse_file_entry_47de18"] or entry_parser["imports_added"]:
        raise RuntimeError("Apollo Main tracepoint file-entry parser changed")
    state_write_path = G2 / "build/c-firmware/20261015/main-tracepoint-write-state-47df28/receipt.json"
    state_write, state_write_ref = receipt(state_write_path)
    if state_write["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_WRITE_STATE_C" or \
            state_write["base_sha256"] != entry_parser["linked_sha256"] or \
                        state_write["native_c_cases"] != 54 or \
            state_write["unresolved_before"] != 194 or state_write["unresolved_after"] != 193 or \
            state_write["imports_resolved"] != ["audio_tracepoint_write_state_47df28"] or state_write["imports_added"]:
        raise RuntimeError("Apollo Main TPS1 state writer changed")
    backend_init_path = G2 / "build/c-firmware/20261015/main-tracepoint-pull-backend-init-47dfec/receipt.json"
    backend_init, backend_init_ref = receipt(backend_init_path)
    if backend_init["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_PULL_BACKEND_INIT_C" or \
            backend_init["base_sha256"] != state_write["linked_sha256"] or \
                        backend_init["native_c_cases"] != 216 or \
            backend_init["unresolved_before"] != 193 or backend_init["unresolved_after"] != 195 or \
            backend_init["imports_resolved"] != ["audio_tracepoint_pull_backend_init_47dfec"] or \
            set(backend_init["imports_added"]) != {"audio_tracepoint_storage_mkdir_474a76", "audio_tracepoint_read_state_47df8a", "audio_tracepoint_file_size_47de7a"}:
        raise RuntimeError("Apollo Main tracepoint backend initialization changed")
    pull_size_path = G2 / "build/c-firmware/20261015/main-tracepoint-file-size-47de7a/receipt.json"
    pull_size, pull_size_ref = receipt(pull_size_path)
    if pull_size["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_FILE_SIZE_C" or \
            pull_size["base_sha256"] != backend_init["linked_sha256"] or \
            pull_size["native_c_cases"] != 32 or \
            pull_size["unresolved_before"] != 195 or pull_size["unresolved_after"] != 194 or \
            pull_size["imports_resolved"] != ["audio_tracepoint_file_size_47de7a"] or pull_size["imports_added"]:
        raise RuntimeError("Apollo Main tracepoint file size changed")
    state_read_path = G2 / "build/c-firmware/20261015/main-tracepoint-read-state-47df8a/receipt.json"
    state_read, state_read_ref = receipt(state_read_path)
    if state_read["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_READ_STATE_C" or \
            state_read["base_sha256"] != pull_size["linked_sha256"] or \
                        state_read["native_c_cases"] != 60 or \
            state_read["unresolved_before"] != 194 or state_read["unresolved_after"] != 193 or \
            state_read["imports_resolved"] != ["audio_tracepoint_read_state_47df8a"] or state_read["imports_added"]:
        raise RuntimeError("Apollo Main TPS1 state reader changed")
    mkdir_path = G2 / "build/c-firmware/20261015/main-tracepoint-storage-mkdir-474a76/receipt.json"
    mkdir, mkdir_ref = receipt(mkdir_path)
    if mkdir["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_STORAGE_MKDIR_C" or \
            mkdir["base_sha256"] != state_read["linked_sha256"] or \
            mkdir["native_c_cases"] != 60 or \
            mkdir["unresolved_before"] != 193 or mkdir["unresolved_after"] != 193 or \
            mkdir["imports_resolved"] != ["audio_tracepoint_storage_mkdir_474a76"] or \
            mkdir["imports_added"] != ["audio_file_lfs_mkdir_4cfc5c"]:
        raise RuntimeError("Apollo Main tracepoint mkdir facade changed")
    lfs_mkdir_path = G2 / "build/c-firmware/20261015/main-file-lfs-mkdir-4cfc5c/receipt.json"
    lfs_mkdir, lfs_mkdir_ref = receipt(lfs_mkdir_path)
    if lfs_mkdir["status"] != "PASS_EXPERIMENTAL_MAIN_FILE_LFS_MKDIR_WRAPPER_C" or \
            lfs_mkdir["base_sha256"] != mkdir["linked_sha256"] or \
            lfs_mkdir["native_c_cases"] != 20 or \
            lfs_mkdir["unresolved_before"] != 193 or lfs_mkdir["unresolved_after"] != 193 or \
            lfs_mkdir["imports_resolved"] != ["audio_file_lfs_mkdir_4cfc5c"] or \
            lfs_mkdir["imports_added"] != ["audio_file_lfs_mkdir_core_4cd3aa"]:
        raise RuntimeError("Apollo Main LittleFS mkdir wrapper changed")
    file_open_path = G2 / "build/c-firmware/20261015/main-tracepoint-file-open-474550/receipt.json"
    file_open, file_open_ref = receipt(file_open_path)
    if file_open["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_FILE_OPEN_C" or \
            file_open["base_sha256"] != lfs_mkdir["linked_sha256"] or \
            file_open["native_c_cases"] != 48 or \
            file_open["unresolved_before"] != 193 or file_open["unresolved_after"] != 192 or \
            file_open["imports_resolved"] != ["audio_tracepoint_file_open_474550"] or \
            file_open["imports_added"]:
        raise RuntimeError("Apollo Main tracepoint file-open facade changed")
    file_sync_path = G2 / "build/c-firmware/20261015/main-tracepoint-file-sync-474910/receipt.json"
    file_sync, file_sync_ref = receipt(file_sync_path)
    if file_sync["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_FILE_SYNC_C" or \
            file_sync["base_sha256"] != file_open["linked_sha256"] or \
            file_sync["native_c_cases"] != 30 or \
            file_sync["unresolved_before"] != 192 or file_sync["unresolved_after"] != 192 or \
            file_sync["imports_resolved"] != ["audio_tracepoint_file_close_474910"] or \
            file_sync["imports_added"] != ["audio_file_lfs_sync_4cfb08"]:
        raise RuntimeError("Apollo Main tracepoint stream-sync facade changed")
    lfs_sync_path = G2 / "build/c-firmware/20261015/main-file-lfs-sync-4cfb08/receipt.json"
    lfs_sync, lfs_sync_ref = receipt(lfs_sync_path)
    if lfs_sync["status"] != "PASS_EXPERIMENTAL_MAIN_FILE_LFS_SYNC_C" or \
            lfs_sync["base_sha256"] != file_sync["linked_sha256"] or \
            lfs_sync["native_c_cases"] != 32 or \
            lfs_sync["unresolved_before"] != 192 or lfs_sync["unresolved_after"] != 191 or \
            lfs_sync["imports_resolved"] != ["audio_file_lfs_sync_4cfb08"] or \
            lfs_sync["imports_added"]:
        raise RuntimeError("Apollo Main LittleFS sync wrapper changed")
    file_write_path = G2 / "build/c-firmware/20261015/main-tracepoint-file-write-474682/receipt.json"
    file_write, file_write_ref = receipt(file_write_path)
    if file_write["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_FILE_WRITE_C" or \
            file_write["base_sha256"] != lfs_sync["linked_sha256"] or \
            file_write["native_c_cases"] != 75 or \
            file_write["unresolved_before"] != 191 or file_write["unresolved_after"] != 190 or \
            file_write["imports_resolved"] != ["audio_tracepoint_file_write_474682"] or \
            file_write["imports_added"]:
        raise RuntimeError("Apollo Main tracepoint file-write facade changed")
    mkdir_core_path = G2 / "build/c-firmware/20261015/main-file-lfs-mkdir-core-4cd3aa/receipt.json"
    mkdir_core, mkdir_core_ref = receipt(mkdir_core_path)
    if mkdir_core["status"] != "PASS_EXPERIMENTAL_MAIN_FILE_LFS_MKDIR_CORE_C" or \
            mkdir_core["base_sha256"] != file_write["linked_sha256"] or \
            mkdir_core["native_c_cases"] != 16 or \
            mkdir_core["unresolved_before"] != 190 or mkdir_core["unresolved_after"] != 189 or \
            mkdir_core["imports_resolved"] != ["audio_file_lfs_mkdir_core_4cd3aa"] or \
            mkdir_core["imports_added"]:
        raise RuntimeError("Apollo Main LittleFS mkdir core changed")
    delete_all_files_path = G2 / "build/c-firmware/20261015/main-tracepoint-delete-all-files-5ee650/receipt.json"
    delete_all_files, delete_all_files_ref = receipt(delete_all_files_path)
    if delete_all_files["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_DELETE_ALL_FILES_C" or \
            delete_all_files["base_sha256"] != mkdir_core["linked_sha256"] or \
            delete_all_files["native_c_cases"] != 70 or \
            delete_all_files["unresolved_before"] != 189 or delete_all_files["unresolved_after"] != 188 or \
            delete_all_files["imports_resolved"] != ["audio_tracepoint_delete_all_files_5ee650"] or \
            delete_all_files["imports_added"]:
        raise RuntimeError("Apollo Main tracepoint delete-all files changed")
    setting_common_path = G2 / "build/c-firmware/20261015/main-setting-common-data-4668ae/receipt.json"
    setting_common, setting_common_ref = receipt(setting_common_path)
    if setting_common["status"] != "PASS_EXPERIMENTAL_MAIN_SETTING_COMMON_DATA_C" or \
            setting_common["base_sha256"] != delete_all_files["linked_sha256"] or \
            setting_common["oracle_cases"] != 360 or \
            setting_common["unresolved_before"] != 188 or setting_common["unresolved_after"] != 190 or \
            setting_common["imports_resolved"] != ["audio_uart_registry_callback_4668ae"] or \
            len(setting_common["imports_added"]) != 3:
        raise RuntimeError("Apollo Main Setting common-data callback changed")
    setting_recv_path = G2 / "build/c-firmware/20261015/main-setting-data-recv-466976/receipt.json"
    setting_recv, setting_recv_ref = receipt(setting_recv_path)
    if setting_recv["status"] != "PASS_EXPERIMENTAL_MAIN_SETTING_DATA_RECV_C" or \
            setting_recv["base_sha256"] != setting_common["linked_sha256"] or \
            setting_recv["oracle_cases"] != 180 or \
            setting_recv["unresolved_before"] != 190 or setting_recv["unresolved_after"] != 192 or \
            setting_recv["imports_resolved"] != ["audio_setting_process_data_466976"] or \
            len(setting_recv["imports_added"]) != 3:
        raise RuntimeError("Apollo Main Setting data-receive handler changed")
    setting_response_path = G2 / "build/c-firmware/20261015/main-setting-response-49b900/receipt.json"
    setting_response, setting_response_ref = receipt(setting_response_path)
    if setting_response["status"] != "PASS_EXPERIMENTAL_MAIN_SETTING_RESPONSE_C" or \
            setting_response["base_sha256"] != setting_recv["linked_sha256"] or \
            setting_response["oracle_cases"] != 180 or \
            setting_response["unresolved_before"] != 192 or setting_response["unresolved_after"] != 192 or \
            setting_response["imports_resolved"] != ["audio_setting_serialize_response_49b900"] or \
            setting_response["imports_added"] != ["audio_setting_response_encode_49b3d4"]:
        raise RuntimeError("Apollo Main Setting response serializer changed")
    setting_encoder_path = G2 / "build/c-firmware/20261015/main-setting-response-encode-49b3d4/receipt.json"
    setting_encoder, setting_encoder_ref = receipt(setting_encoder_path)
    if setting_encoder["status"] != "PASS_EXPERIMENTAL_MAIN_SETTING_RESPONSE_ENCODER_C" or \
            setting_encoder["base_sha256"] != setting_response["linked_sha256"] or \
            setting_encoder["oracle_cases"] != 480 or \
            setting_encoder["unresolved_before"] != 192 or setting_encoder["unresolved_after"] != 191 or \
            setting_encoder["imports_resolved"] != ["audio_setting_response_encode_49b3d4"] or \
            setting_encoder["imports_added"]:
        raise RuntimeError("Apollo Main Setting response encoder changed")
    setting_local_path = G2 / "build/c-firmware/20261015/main-setting-local-response-49ba58/receipt.json"
    setting_local, setting_local_ref = receipt(setting_local_path)
    if setting_local["status"] != "PASS_EXPERIMENTAL_MAIN_SETTING_LOCAL_RESPONSE_C" or \
            setting_local["base_sha256"] != setting_encoder["linked_sha256"] or \
            setting_local["oracle_cases"] != 180 or \
            setting_local["unresolved_before"] != 191 or setting_local["unresolved_after"] != 191 or \
            setting_local["imports_resolved"] != ["audio_setting_serialize_local_response_49ba58"] or \
            setting_local["imports_added"] != ["audio_setting_local_response_encode_49b7c4"]:
        raise RuntimeError("Apollo Main Setting local-data response changed")
    setting_local_encoder_path = G2 / "build/c-firmware/20261015/main-setting-local-response-encode-49b7c4/receipt.json"
    setting_local_encoder, setting_local_encoder_ref = receipt(setting_local_encoder_path)
    if setting_local_encoder["status"] != "PASS_EXPERIMENTAL_MAIN_SETTING_LOCAL_RESPONSE_ENCODER_C" or \
            setting_local_encoder["base_sha256"] != setting_local["linked_sha256"] or \
            setting_local_encoder["oracle_cases"] != 960 or \
            setting_local_encoder["unresolved_before"] != 191 or setting_local_encoder["unresolved_after"] != 190 or \
            setting_local_encoder["imports_resolved"] != ["audio_setting_local_response_encode_49b7c4"] or \
            setting_local_encoder["imports_added"]:
        raise RuntimeError("Apollo Main Setting local-data encoder changed")
    setting_parse_path = G2 / "build/c-firmware/20261015/main-setting-parse-49b1f8/receipt.json"
    setting_parse, setting_parse_ref = receipt(setting_parse_path)
    if setting_parse["status"] != "PASS_EXPERIMENTAL_MAIN_SETTING_PARSE_C" or \
            setting_parse["base_sha256"] != setting_local_encoder["linked_sha256"] or \
            [item["cases"] for item in setting_parse["oracles"]] != [320, 128] or \
            setting_parse["unresolved_before"] != 190 or setting_parse["unresolved_after"] != 189 or \
            setting_parse["imports_resolved"] != ["audio_setting_parse_data_package_49b1f8"] or \
            setting_parse["imports_added"]:
        raise RuntimeError("Apollo Main Setting parser changed")
    setting_dispatch_path = G2 / "build/c-firmware/20261015/main-setting-dispatch-466abc/receipt.json"
    setting_dispatch, setting_dispatch_ref = receipt(setting_dispatch_path)
    if setting_dispatch["status"] != "PASS_EXPERIMENTAL_MAIN_SETTING_DISPATCH_C" or \
            setting_dispatch["base_sha256"] != setting_parse["linked_sha256"] or \
            setting_dispatch["oracle_cases"] != 150 or \
            setting_dispatch["unresolved_before"] != 189 or setting_dispatch["unresolved_after"] != 199 or \
            setting_dispatch["imports_resolved"] != ["audio_setting_dispatch_message_466abc"] or \
            len(setting_dispatch["imports_added"]) != 11:
        raise RuntimeError("Apollo Main Setting dispatch changed")
    setting_type5_path = G2 / "build/c-firmware/20261015/main-setting-type5-467134/receipt.json"
    setting_type5, setting_type5_ref = receipt(setting_type5_path)
    if setting_type5["status"] != "PASS_EXPERIMENTAL_MAIN_SETTING_TYPE5_C" or \
            setting_type5["base_sha256"] != setting_dispatch["linked_sha256"] or \
            setting_type5["oracle_cases"] != 10 or \
            setting_type5["unresolved_before"] != 199 or setting_type5["unresolved_after"] != 199 or \
            setting_type5["imports_resolved"] != ["audio_setting_dispatch_type5_467134"] or \
            setting_type5["imports_added"] != ["audio_wear_detect_set_enable_49eb1e"]:
        raise RuntimeError("Apollo Main Setting type-5 handler changed")
    wear_enable_path = G2 / "build/c-firmware/20261015/main-wear-detect-enable-49eb1e/receipt.json"
    wear_enable, wear_enable_ref = receipt(wear_enable_path)
    if wear_enable["status"] != "PASS_EXPERIMENTAL_MAIN_WEAR_DETECT_ENABLE_C" or \
            wear_enable["base_sha256"] != setting_type5["linked_sha256"] or \
            wear_enable["oracle_cases"] != 200 or \
            wear_enable["unresolved_before"] != 199 or wear_enable["unresolved_after"] != 199 or \
            wear_enable["imports_resolved"] != ["audio_wear_detect_set_enable_49eb1e"] or \
            wear_enable["imports_added"] != ["audio_wear_detect_handle_status_change_49ebb6"]:
        raise RuntimeError("Apollo Main wear-detect enable changed")
    wear_status_path = G2 / "build/c-firmware/20261015/main-wear-detect-status-49ebb6/receipt.json"
    wear_status, wear_status_ref = receipt(wear_status_path)
    if wear_status["status"] != "PASS_EXPERIMENTAL_MAIN_WEAR_DETECT_STATUS_C" or \
            wear_status["base_sha256"] != wear_enable["linked_sha256"] or \
            wear_status["oracle_cases"] != 420 or \
            wear_status["unresolved_before"] != 199 or wear_status["unresolved_after"] != 204 or \
            wear_status["imports_resolved"] != ["audio_wear_detect_handle_status_change_49ebb6"] or \
            len(wear_status["imports_added"]) != 6:
        raise RuntimeError("Apollo Main wear-detect status changed")
    onboarding_start_path = G2 / "build/c-firmware/20261015/main-onboarding-start-46805a/receipt.json"
    onboarding_start, onboarding_start_ref = receipt(onboarding_start_path)
    if onboarding_start["status"] != "PASS_EXPERIMENTAL_MAIN_ONBOARDING_START_C" or \
            onboarding_start["base_sha256"] != wear_status["linked_sha256"] or \
            onboarding_start["oracle_cases"] != 84 or \
            onboarding_start["unresolved_before"] != 204 or onboarding_start["unresolved_after"] != 203 or \
            onboarding_start["imports_resolved"] != ["audio_wear_child_46805a"] or \
            onboarding_start["imports_added"]:
        raise RuntimeError("Apollo Main onboarding startup changed")
    wear_wrapper_path = G2 / "build/c-firmware/20261015/main-wear-child-502bf0/receipt.json"
    wear_wrapper, wear_wrapper_ref = receipt(wear_wrapper_path)
    if wear_wrapper["status"] != "PASS_EXPERIMENTAL_MAIN_WEAR_CHILD_502BF0_C" or \
            wear_wrapper["base_sha256"] != onboarding_start["linked_sha256"] or \
            wear_wrapper["oracle_cases"] != 10 or \
            wear_wrapper["unresolved_before"] != 203 or wear_wrapper["unresolved_after"] != 203 or \
            wear_wrapper["imports_resolved"] != ["audio_wear_child_502bf0"] or \
            wear_wrapper["imports_added"] != ["audio_wear_child_51308a"]:
        raise RuntimeError("Apollo Main wear forwarding wrapper changed")
    wear_request_path = G2 / "build/c-firmware/20261015/main-wear-child-51308a/receipt.json"
    wear_request, wear_request_ref = receipt(wear_request_path)
    if wear_request["status"] != "PASS_EXPERIMENTAL_MAIN_WEAR_CHILD_51308A_C" or \
            wear_request["base_sha256"] != wear_wrapper["linked_sha256"] or \
            wear_request["oracle_cases"] != 10 or \
            wear_request["unresolved_before"] != 203 or wear_request["unresolved_after"] != 202 or \
            wear_request["imports_resolved"] != ["audio_wear_child_51308a"] or \
            wear_request["imports_added"] or \
            wear_request["provider_source_sha256"] != sha(ROOT / wear_request["provider_source"]):
        raise RuntimeError("Apollo Main wear request wrapper changed")
    settings_input_path = G2 / "build/c-firmware/20261015/main-settings-input-check-46b0ec/receipt.json"
    settings_input, settings_input_ref = receipt(settings_input_path)
    if settings_input["status"] != "PASS_EXPERIMENTAL_MAIN_SETTINGS_INPUT_CHECK_C" or \
            settings_input["base_sha256"] != wear_request["linked_sha256"] or \
            settings_input["oracle_cases"] != 252 or \
            settings_input["unresolved_before"] != 202 or settings_input["unresolved_after"] != 201 or \
            settings_input["imports_resolved"] != ["audio_wear_child_46b0ec"] or \
            settings_input["imports_added"]:
        raise RuntimeError("Apollo Main settings input check changed")
    setting_type6_path = G2 / "build/c-firmware/20261015/main-setting-type6-46713e/receipt.json"
    setting_type6, setting_type6_ref = receipt(setting_type6_path)
    if setting_type6["status"] != "PASS_EXPERIMENTAL_MAIN_SETTING_TYPE6_C" or \
            setting_type6["base_sha256"] != settings_input["linked_sha256"] or \
            setting_type6["oracle_cases"] != 30 or \
            setting_type6["unresolved_before"] != 201 or setting_type6["unresolved_after"] != 201 or \
            setting_type6["imports_resolved"] != ["audio_setting_dispatch_type6_46713e"] or \
            setting_type6["imports_added"] != ["audio_silent_mode_set_from_app_46921c"]:
        raise RuntimeError("Apollo Main setting type-6 route changed")
    setting_type8_path = G2 / "build/c-firmware/20261015/main-setting-type8-4671a2/receipt.json"
    setting_type8, setting_type8_ref = receipt(setting_type8_path)
    if setting_type8["status"] != "PASS_EXPERIMENTAL_MAIN_SETTING_TYPE8_C" or \
            setting_type8["base_sha256"] != setting_type6["linked_sha256"] or \
            setting_type8["oracle_cases"] != 120 or \
            setting_type8["unresolved_before"] != 201 or setting_type8["unresolved_after"] != 200 or \
            setting_type8["imports_resolved"] != ["audio_setting_dispatch_type8_4671a2"] or \
            setting_type8["imports_added"]:
        raise RuntimeError("Apollo Main setting type-8 route changed")
    setting_type9_path = G2 / "build/c-firmware/20261015/main-setting-type9-467206/receipt.json"
    setting_type9, setting_type9_ref = receipt(setting_type9_path)
    if setting_type9["status"] != "PASS_EXPERIMENTAL_MAIN_SETTING_TYPE9_C" or \
            setting_type9["base_sha256"] != setting_type8["linked_sha256"] or \
            setting_type9["oracle_cases"] != 30 or \
            setting_type9["unresolved_before"] != 200 or setting_type9["unresolved_after"] != 199 or \
            setting_type9["imports_resolved"] != ["audio_setting_dispatch_type9_467206"] or \
            setting_type9["imports_added"]:
        raise RuntimeError("Apollo Main setting type-9 route changed")
    setting_display_start_path = G2 / "build/c-firmware/20261015/main-setting-display-start-466890/receipt.json"
    setting_display_start, setting_display_start_ref = receipt(setting_display_start_path)
    if setting_display_start["status"] != "PASS_EXPERIMENTAL_MAIN_SETTING_DISPLAY_START_C" or \
            setting_display_start["base_sha256"] != setting_type9["linked_sha256"] or \
            setting_display_start["oracle_cases"] != 6 or \
            setting_display_start["unresolved_before"] != 199 or setting_display_start["unresolved_after"] != 199 or \
            setting_display_start["imports_resolved"] or setting_display_start["imports_added"]:
        raise RuntimeError("Apollo Main setting display-start selector changed")
    dashboard_reset_path = G2 / "build/c-firmware/20261015/main-dashboard-auto-close-reset-49c0dc/receipt.json"
    dashboard_reset, dashboard_reset_ref = receipt(dashboard_reset_path)
    if dashboard_reset["status"] != "PASS_EXPERIMENTAL_MAIN_DASHBOARD_AUTO_CLOSE_RESET_C" or \
            dashboard_reset["base_sha256"] != setting_display_start["linked_sha256"] or \
            dashboard_reset["oracle_cases"] != 90 or \
            dashboard_reset["unresolved_before"] != 199 or dashboard_reset["unresolved_after"] != 199 or \
            dashboard_reset["imports_resolved"] or dashboard_reset["imports_added"]:
        raise RuntimeError("Apollo Main dashboard timeout reset changed")
    setting_coordinates_path = G2 / "build/c-firmware/20261015/main-setting-coordinates-466e1c-466ea2/receipt.json"
    setting_coordinates, setting_coordinates_ref = receipt(setting_coordinates_path)
    if setting_coordinates["status"] != "PASS_EXPERIMENTAL_MAIN_SETTING_COORDINATES_C" or \
            setting_coordinates["base_sha256"] != dashboard_reset["linked_sha256"] or \
            setting_coordinates["oracle_cases"] != 480 or \
            setting_coordinates["unresolved_before"] != 199 or setting_coordinates["unresolved_after"] != 197 or \
            setting_coordinates["imports_resolved"] != ["audio_setting_dispatch_type2_466e1c", "audio_setting_dispatch_type3_466ea2"] or \
            setting_coordinates["imports_added"]:
        raise RuntimeError("Apollo Main setting coordinate routes changed")
    setting_type12_path = G2 / "build/c-firmware/20261015/main-setting-type12-467c34/receipt.json"
    setting_type12, setting_type12_ref = receipt(setting_type12_path)
    if setting_type12["status"] != "PASS_EXPERIMENTAL_MAIN_SETTING_TYPE12_C" or \
            setting_type12["base_sha256"] != setting_coordinates["linked_sha256"] or \
            setting_type12["oracle_cases"] != 225 or \
            setting_type12["unresolved_before"] != 197 or setting_type12["unresolved_after"] != 196 or \
            setting_type12["imports_resolved"] != ["audio_setting_dispatch_type12_467c34"] or \
            setting_type12["imports_added"]:
        raise RuntimeError("Apollo Main setting type-12 route changed")
    gesture_apptype_path = G2 / "build/c-firmware/20261015/main-setting-gesture-apptype-46658e/receipt.json"
    gesture_apptype, gesture_apptype_ref = receipt(gesture_apptype_path)
    if gesture_apptype["status"] != "PASS_EXPERIMENTAL_MAIN_SETTING_GESTURE_APPTYPE_C" or \
            gesture_apptype["base_sha256"] != setting_type12["linked_sha256"] or \
            gesture_apptype["oracle_cases"] != 270 or \
            gesture_apptype["unresolved_before"] != 196 or gesture_apptype["unresolved_after"] != 196 or \
            gesture_apptype["imports_resolved"] or gesture_apptype["imports_added"]:
        raise RuntimeError("Apollo Main gesture application-type setter changed")
    setting_type10_path = G2 / "build/c-firmware/20261015/main-setting-type10-467308/receipt.json"
    setting_type10, setting_type10_ref = receipt(setting_type10_path)
    if setting_type10["status"] != "PASS_EXPERIMENTAL_MAIN_SETTING_TYPE10_C" or \
            setting_type10["base_sha256"] != gesture_apptype["linked_sha256"] or \
            setting_type10["oracle_cases"] != 45 or \
            setting_type10["unresolved_before"] != 196 or setting_type10["unresolved_after"] != 195 or \
            setting_type10["imports_resolved"] != ["audio_setting_dispatch_type10_467308"] or \
            setting_type10["imports_added"]:
        raise RuntimeError("Apollo Main setting type-10 route changed")
    brightness_refresh_path = G2 / "build/c-firmware/20261015/main-setting-brightness-refresh-46c18c/receipt.json"
    brightness_refresh, brightness_refresh_ref = receipt(brightness_refresh_path)
    if brightness_refresh["status"] != "PASS_EXPERIMENTAL_MAIN_SETTING_BRIGHTNESS_REFRESH_C" or \
            brightness_refresh["base_sha256"] != setting_type10["linked_sha256"] or \
            brightness_refresh["oracle_cases"] != 27 or \
            brightness_refresh["unresolved_before"] != 195 or brightness_refresh["unresolved_after"] != 195 or \
            brightness_refresh["imports_resolved"] or brightness_refresh["imports_added"]:
        raise RuntimeError("Apollo Main setting brightness refresh changed")
    manual_brightness_path = G2 / "build/c-firmware/20261015/main-setting-manual-brightness-46c1c8/receipt.json"
    manual_brightness, manual_brightness_ref = receipt(manual_brightness_path)
    if manual_brightness["status"] != "PASS_EXPERIMENTAL_MAIN_SETTING_MANUAL_BRIGHTNESS_C" or \
            manual_brightness["base_sha256"] != brightness_refresh["linked_sha256"] or \
            manual_brightness["oracle_cases"] != 147 or \
            manual_brightness["unresolved_before"] != 195 or manual_brightness["unresolved_after"] != 196 or \
            manual_brightness["imports_resolved"] or \
            manual_brightness["imports_added"] != ["audio_als_manual_set_brightness_4ae81c"]:
        raise RuntimeError("Apollo Main setting manual brightness changed")
    als_manual_path = G2 / "build/c-firmware/20261015/main-als-manual-brightness-4ae81c/receipt.json"
    als_manual, als_manual_ref = receipt(als_manual_path)
    if als_manual["status"] != "PASS_EXPERIMENTAL_MAIN_ALS_MANUAL_BRIGHTNESS_C" or \
            als_manual["base_sha256"] != manual_brightness["linked_sha256"] or \
            als_manual["oracle_cases"] != 240 or \
            als_manual["unresolved_before"] != 196 or als_manual["unresolved_after"] != 197 or \
            als_manual["imports_resolved"] != ["audio_als_manual_set_brightness_4ae81c"] or \
            als_manual["imports_added"] != ["audio_als_manual_recalculate_4adcd8", "audio_als_manual_set_target_4ade36"]:
        raise RuntimeError("Apollo Main ALS manual brightness changed")
    als_recalculate_path = G2 / "build/c-firmware/20261015/main-als-manual-recalculate-4adcd8/receipt.json"
    als_recalculate, als_recalculate_ref = receipt(als_recalculate_path)
    if als_recalculate["status"] != "PASS_EXPERIMENTAL_MAIN_ALS_MANUAL_RECALCULATE_C" or \
            als_recalculate["base_sha256"] != als_manual["linked_sha256"] or \
            als_recalculate["oracle_cases"] != 81 or \
            als_recalculate["unresolved_before"] != 197 or als_recalculate["unresolved_after"] != 196 or \
            als_recalculate["imports_resolved"] != ["audio_als_manual_recalculate_4adcd8"] or \
            als_recalculate["imports_added"]:
        raise RuntimeError("Apollo Main ALS manual recalculate changed")
    als_target_path = G2 / "build/c-firmware/20261015/main-als-manual-target-4ade36/receipt.json"
    als_target, als_target_ref = receipt(als_target_path)
    if als_target["status"] != "PASS_EXPERIMENTAL_MAIN_ALS_MANUAL_TARGET_C" or \
            als_target["base_sha256"] != als_recalculate["linked_sha256"] or \
            als_target["oracle_cases"] != 625 or \
            als_target["unresolved_before"] != 196 or als_target["unresolved_after"] != 197 or \
            als_target["imports_resolved"] != ["audio_als_manual_set_target_4ade36"] or \
            als_target["imports_added"] != ["audio_als_first_curve_percent_4ad9e2", "audio_als_manual_target_scale_4addb6"]:
        raise RuntimeError("Apollo Main ALS manual target changed")
    als_curve_path = G2 / "build/c-firmware/20261015/main-als-curve-first-percent-4ad9e2/receipt.json"
    als_curve, als_curve_ref = receipt(als_curve_path)
    if als_curve["status"] != "PASS_EXPERIMENTAL_MAIN_ALS_CURVE_FIRST_PERCENT_C" or \
            als_curve["base_sha256"] != als_target["linked_sha256"] or \
            als_curve["oracle_cases"] != 1 or \
            als_curve["unresolved_before"] != 197 or als_curve["unresolved_after"] != 196 or \
            als_curve["imports_resolved"] != ["audio_als_first_curve_percent_4ad9e2"] or \
            als_curve["imports_added"]:
        raise RuntimeError("Apollo Main ALS first curve getter changed")
    als_target_scale_path = G2 / "build/c-firmware/20261015/main-als-manual-target-scale-4addb6/receipt.json"
    als_target_scale, als_target_scale_ref = receipt(als_target_scale_path)
    if als_target_scale["status"] != "PASS_EXPERIMENTAL_MAIN_ALS_MANUAL_TARGET_SCALE_C" or \
            als_target_scale["base_sha256"] != als_curve["linked_sha256"] or \
            als_target_scale["oracle_cases"] != 336 or \
            als_target_scale["unresolved_before"] != 196 or als_target_scale["unresolved_after"] != 195 or \
            als_target_scale["imports_resolved"] != ["audio_als_manual_target_scale_4addb6"] or \
            als_target_scale["imports_added"]:
        raise RuntimeError("Apollo Main ALS manual target scale changed")
    setting_type1_path = G2 / "build/c-firmware/20261015/main-setting-type1-brightness-466bec/receipt.json"
    setting_type1, setting_type1_ref = receipt(setting_type1_path)
    if setting_type1["status"] != "PASS_EXPERIMENTAL_MAIN_SETTING_TYPE1_BRIGHTNESS_C" or \
            setting_type1["base_sha256"] != als_target_scale["linked_sha256"] or \
            setting_type1["oracle_cases"] != 200 or \
            setting_type1["unresolved_before"] != 195 or setting_type1["unresolved_after"] != 194 or \
            setting_type1["imports_resolved"] != ["audio_setting_dispatch_type1_466bec"] or \
            setting_type1["imports_added"]:
        raise RuntimeError("Apollo Main setting type-1 brightness changed")
    setting_type4_path = G2 / "build/c-firmware/20261015/main-setting-type4-head-up-466f28/receipt.json"
    setting_type4, setting_type4_ref = receipt(setting_type4_path)
    if setting_type4["status"] != "PASS_EXPERIMENTAL_MAIN_SETTING_TYPE4_HEAD_UP_C" or \
            setting_type4["base_sha256"] != setting_type1["linked_sha256"] or \
            setting_type4["oracle_cases"] != 1260 or \
            setting_type4["unresolved_before"] != 194 or setting_type4["unresolved_after"] != 194 or \
            setting_type4["imports_resolved"] != ["audio_setting_dispatch_type4_466f28"] or \
            setting_type4["imports_added"] != ["audio_setting_head_up_configure_46c524"]:
        raise RuntimeError("Apollo Main setting type-4 head-up changed")
    head_up_config_path = G2 / "build/c-firmware/20261015/main-setting-head-up-configure-46c524/receipt.json"
    head_up_config, head_up_config_ref = receipt(head_up_config_path)
    if head_up_config["status"] != "PASS_EXPERIMENTAL_MAIN_SETTING_HEAD_UP_CONFIGURE_C" or \
            head_up_config["base_sha256"] != setting_type4["linked_sha256"] or \
            head_up_config["oracle_cases"] != 1260 or \
            head_up_config["unresolved_before"] != 194 or head_up_config["unresolved_after"] != 194 or \
            head_up_config["imports_resolved"] != ["audio_setting_head_up_configure_46c524"] or \
            head_up_config["imports_added"] != ["audio_hub_parameter_config_4a6e3c"]:
        raise RuntimeError("Apollo Main head-up configuration changed")
    hub_parameter_path = G2 / "build/c-firmware/20261015/main-hub-parameter-config-4a6e3c/receipt.json"
    hub_parameter, hub_parameter_ref = receipt(hub_parameter_path)
    if hub_parameter["status"] != "PASS_EXPERIMENTAL_MAIN_HUB_PARAMETER_CONFIG_C" or \
            hub_parameter["base_sha256"] != head_up_config["linked_sha256"] or \
            hub_parameter["oracle_cases"] != 405 or \
            hub_parameter["unresolved_before"] != 194 or hub_parameter["unresolved_after"] != 196 or \
            hub_parameter["imports_resolved"] != ["audio_hub_parameter_config_4a6e3c"] or \
            hub_parameter["imports_added"] != ["audio_hub_imu_accel_config_4a52a2", "audio_hub_semantic_motion_period_4a4ec0", "audio_hub_semantic_motion_threshold_4a4e8c"]:
        raise RuntimeError("Apollo Main HUB parameter configuration changed")
    hub_period_path = G2 / "build/c-firmware/20261015/main-hub-semantic-motion-period-4a4ec0/receipt.json"
    hub_period, hub_period_ref = receipt(hub_period_path)
    if hub_period["status"] != "PASS_EXPERIMENTAL_MAIN_HUB_SEMANTIC_MOTION_PERIOD_C" or \
            hub_period["base_sha256"] != hub_parameter["linked_sha256"] or \
            hub_period["oracle_cases"] != 32 or \
            hub_period["unresolved_before"] != 196 or hub_period["unresolved_after"] != 195 or \
            hub_period["imports_resolved"] != ["audio_hub_semantic_motion_period_4a4ec0"] or \
            hub_period["imports_added"]:
        raise RuntimeError("Apollo Main HUB motion period changed")
    hub_imu_path = G2 / "build/c-firmware/20261015/main-hub-imu-accel-config-4a52a2/receipt.json"
    hub_imu, hub_imu_ref = receipt(hub_imu_path)
    if hub_imu["status"] != "PASS_EXPERIMENTAL_MAIN_HUB_IMU_ACCEL_CONFIG_C" or \
            hub_imu["base_sha256"] != hub_period["linked_sha256"] or \
            hub_imu["oracle_cases"] != 80 or \
            hub_imu["unresolved_before"] != 195 or hub_imu["unresolved_after"] != 194 or \
            hub_imu["imports_resolved"] != ["audio_hub_imu_accel_config_4a52a2"] or \
            hub_imu["imports_added"]:
        raise RuntimeError("Apollo Main HUB IMU acceleration configuration changed")
    hub_threshold_path = G2 / "build/c-firmware/20261015/main-hub-semantic-motion-threshold-4a4e8c/receipt.json"
    hub_threshold, hub_threshold_ref = receipt(hub_threshold_path)
    if hub_threshold["status"] != "PASS_EXPERIMENTAL_MAIN_HUB_SEMANTIC_MOTION_THRESHOLD_C" or \
            hub_threshold["base_sha256"] != hub_imu["linked_sha256"] or \
            hub_threshold["oracle_cases"] != 22 or \
            hub_threshold["unresolved_before"] != 194 or hub_threshold["unresolved_after"] != 193 or \
            hub_threshold["imports_resolved"] != ["audio_hub_semantic_motion_threshold_4a4e8c"] or \
            hub_threshold["imports_added"]:
        raise RuntimeError("Apollo Main HUB semantic motion threshold changed")
    deinit_path = G2 / "build/c-firmware/20261015/main-display-deinit-force-47432c/receipt.json"
    deinit, deinit_ref = receipt(deinit_path)
    if deinit["status"] != "PASS_EXPERIMENTAL_MAIN_DISPLAY_DEINIT_FORCE_C" or \
            deinit["base_sha256"] != hub_threshold["linked_sha256"] or \
            deinit["oracle_cases"] != 40 or \
            deinit["unresolved_before"] != 193 or deinit["unresolved_after"] != 192 or \
            deinit["imports_resolved"] != ["audio_wear_child_47432c"] or \
            deinit["imports_added"]:
        raise RuntimeError("Apollo Main display force-deinit changed")
    init_path = G2 / "build/c-firmware/20261015/main-display-init-force-474100/receipt.json"
    init, init_ref = receipt(init_path)
    if init["status"] != "PASS_EXPERIMENTAL_MAIN_DISPLAY_INIT_FORCE_C" or \
            init["base_sha256"] != deinit["linked_sha256"] or \
            init["oracle_cases"] != 160 or \
            init["unresolved_before"] != 192 or init["unresolved_after"] != 191 or \
            init["imports_resolved"] != ["audio_wear_child_474100"] or \
            init["imports_added"]:
        raise RuntimeError("Apollo Main display force-init changed")
    wear_notify_path = G2 / "build/c-firmware/20261015/main-onboarding-wear-notify-47e320/receipt.json"
    wear_notify, wear_notify_ref = receipt(wear_notify_path)
    if wear_notify["status"] != "PASS_EXPERIMENTAL_MAIN_ONBOARDING_WEAR_NOTIFY_C" or \
            wear_notify["base_sha256"] != init["linked_sha256"] or \
            wear_notify["oracle_cases"] != 360 or \
            wear_notify["unresolved_before"] != 191 or wear_notify["unresolved_after"] != 191 or \
            wear_notify["imports_resolved"] != ["audio_wear_child_47e320"] or \
            wear_notify["imports_added"] != ["audio_onboarding_event_encode_4a8368"]:
        raise RuntimeError("Apollo Main onboarding wear notification changed")
    event_encode_path = G2 / "build/c-firmware/20261015/main-onboarding-event-encode-4a8368/receipt.json"
    event_encode, event_encode_ref = receipt(event_encode_path)
    if event_encode["status"] != "PASS_EXPERIMENTAL_MAIN_ONBOARDING_EVENT_ENCODE_C" or \
            event_encode["base_sha256"] != wear_notify["linked_sha256"] or \
            event_encode["oracle_cases"] != 120 or \
            event_encode["unresolved_before"] != 191 or event_encode["unresolved_after"] != 190 or \
            event_encode["imports_resolved"] != ["audio_onboarding_event_encode_4a8368"] or \
            event_encode["imports_added"]:
        raise RuntimeError("Apollo Main onboarding event encoder changed")
    silent_app_path = G2 / "build/c-firmware/20261015/main-silent-mode-set-from-app-46921c/receipt.json"
    silent_app, silent_app_ref = receipt(silent_app_path)
    if silent_app["status"] != "PASS_EXPERIMENTAL_MAIN_SILENT_MODE_SET_FROM_APP_C" or \
            silent_app["base_sha256"] != event_encode["linked_sha256"] or \
            silent_app["oracle_cases"] != 1920 or \
            silent_app["unresolved_before"] != 190 or silent_app["unresolved_after"] != 190 or \
            silent_app["imports_resolved"] != ["audio_silent_mode_set_from_app_46921c"] or \
            silent_app["imports_added"] != ["audio_sync_send_to_both_ext_464f76"]:
        raise RuntimeError("Apollo Main silent-mode app command changed")
    send_both_path = G2 / "build/c-firmware/20261015/main-sync-send-to-both-ext-464f76/receipt.json"
    send_both, send_both_ref = receipt(send_both_path)
    if send_both["status"] != "PASS_EXPERIMENTAL_MAIN_SYNC_SEND_TO_BOTH_EXT_C" or \
            send_both["base_sha256"] != silent_app["linked_sha256"] or \
            send_both["oracle_cases"] != 500 or \
            send_both["unresolved_before"] != 190 or send_both["unresolved_after"] != 189 or \
            send_both["imports_resolved"] != ["audio_sync_send_to_both_ext_464f76"] or \
            send_both["imports_added"]:
        raise RuntimeError("Apollo Main sync send-to-both changed")
    dominant_path = G2 / "build/c-firmware/20261015/main-setting-dominant-hand-467540/receipt.json"
    dominant, dominant_ref = receipt(dominant_path)
    if dominant["status"] != "PASS_EXPERIMENTAL_MAIN_SETTING_DOMINANT_HAND_C" or \
            dominant["base_sha256"] != send_both["linked_sha256"] or \
            dominant["oracle_cases"] != 960 or \
            dominant["unresolved_before"] != 189 or dominant["unresolved_after"] != 192 or \
            dominant["imports_resolved"] != ["audio_setting_dispatch_type11_467540"] or \
            dominant["imports_added"] != ["audio_ble_master_hand_changed_4a2948", "audio_ble_master_set_target_hand_4a2068", "audio_ring_address_is_unset_4a26e8", "audio_ring_connect_policy_on_hand_49f15a"]:
        raise RuntimeError("Apollo Main dominant-hand handler changed")
    ring_unset_path = G2 / "build/c-firmware/20261015/main-ring-address-is-unset-4a26e8/receipt.json"
    ring_unset, ring_unset_ref = receipt(ring_unset_path)
    if ring_unset["status"] != "PASS_EXPERIMENTAL_MAIN_RING_ADDRESS_IS_UNSET_C" or \
            ring_unset["base_sha256"] != dominant["linked_sha256"] or \
            ring_unset["oracle_cases"] != 91 or \
            ring_unset["unresolved_before"] != 192 or ring_unset["unresolved_after"] != 191 or \
            ring_unset["imports_resolved"] != ["audio_ring_address_is_unset_4a26e8"] or \
            ring_unset["imports_added"]:
        raise RuntimeError("Apollo Main ring address sentinel changed")
    ring_policy_path = G2 / "build/c-firmware/20261015/main-ring-connect-policy-on-hand-49f15a/receipt.json"
    ring_policy, ring_policy_ref = receipt(ring_policy_path)
    if ring_policy["status"] != "PASS_EXPERIMENTAL_MAIN_RING_CONNECT_POLICY_ON_HAND_C" or \
            ring_policy["base_sha256"] != ring_unset["linked_sha256"] or \
            ring_policy["oracle_cases"] != 270 or \
            ring_policy["unresolved_before"] != 191 or ring_policy["unresolved_after"] != 191 or \
            ring_policy["imports_resolved"] != ["audio_ring_connect_policy_on_hand_49f15a"] or \
            ring_policy["imports_added"] != ["audio_ble_ring_policy_get_state_49f05c"]:
        raise RuntimeError("Apollo Main dominant-hand ring policy changed")
    ring_get_path = G2 / "build/c-firmware/20261015/main-ring-policy-get-state-49f05c/receipt.json"
    ring_get, ring_get_ref = receipt(ring_get_path)
    if ring_get["status"] != "PASS_EXPERIMENTAL_MAIN_RING_POLICY_GET_STATE_C" or \
            ring_get["base_sha256"] != ring_policy["linked_sha256"] or \
            ring_get["oracle_cases"] != 256 or \
            ring_get["unresolved_before"] != 191 or ring_get["unresolved_after"] != 190 or \
            ring_get["imports_resolved"] != ["audio_ble_ring_policy_get_state_49f05c"] or \
            ring_get["imports_added"]:
        raise RuntimeError("Apollo Main ring policy GetState changed")
    master_target_path = G2 / "build/c-firmware/20261015/main-ble-master-set-target-hand-4a2068/receipt.json"
    master_target, master_target_ref = receipt(master_target_path)
    if master_target["status"] != "PASS_EXPERIMENTAL_MAIN_BLE_MASTER_SET_TARGET_HAND_C" or \
            master_target["base_sha256"] != ring_get["linked_sha256"] or \
            master_target["oracle_cases"] != 80 or \
            master_target["unresolved_before"] != 190 or master_target["unresolved_after"] != 189 or \
            master_target["imports_resolved"] != ["audio_ble_master_set_target_hand_4a2068"] or \
            master_target["imports_added"]:
        raise RuntimeError("Apollo Main dominant-hand target setter changed")
    hand_changed_path = G2 / "build/c-firmware/20261015/main-ble-master-hand-changed-4a2948/receipt.json"
    hand_changed, hand_changed_ref = receipt(hand_changed_path)
    if hand_changed["status"] != "PASS_EXPERIMENTAL_MAIN_BLE_MASTER_HAND_CHANGED_C" or \
            hand_changed["base_sha256"] != master_target["linked_sha256"] or \
            hand_changed["oracle_cases"] != 280 or \
            hand_changed["unresolved_before"] != 189 or hand_changed["unresolved_after"] != 194 or \
            hand_changed["imports_resolved"] != ["audio_ble_master_hand_changed_4a2948"] or \
            hand_changed["imports_added"] != ["audio_ble_master_begin_failure_notify_4a1546", "audio_ble_master_reset_scene_pending_4a2658", "audio_ble_peer_ring_status_47d8f0", "audio_ble_ring_policy_cancel_connect_timeout_49f5f8", "audio_ble_ring_policy_schedule_connect_timeout_49f4a8", "audio_ble_ring_policy_schedule_reconnect_timeout_49f552"]:
        raise RuntimeError("Apollo Main dominant-hand master handler changed")
    peer_ring_path = G2 / "build/c-firmware/20261015/main-ble-peer-ring-status-47d8f0/receipt.json"
    peer_ring, peer_ring_ref = receipt(peer_ring_path)
    if peer_ring["status"] != "PASS_EXPERIMENTAL_MAIN_BLE_PEER_RING_STATUS_C" or \
            peer_ring["base_sha256"] != hand_changed["linked_sha256"] or \
            peer_ring["oracle_cases"] != 256 or \
            peer_ring["unresolved_before"] != 194 or peer_ring["unresolved_after"] != 193 or \
            peer_ring["imports_resolved"] != ["audio_ble_peer_ring_status_47d8f0"] or \
            peer_ring["imports_added"]:
        raise RuntimeError("Apollo Main peer ring status changed")
    scene_pending_path = G2 / "build/c-firmware/20261015/main-ble-master-reset-scene-pending-4a2658/receipt.json"
    scene_pending, scene_pending_ref = receipt(scene_pending_path)
    if scene_pending["status"] != "PASS_EXPERIMENTAL_MAIN_BLE_MASTER_RESET_SCENE_PENDING_C" or \
            scene_pending["base_sha256"] != peer_ring["linked_sha256"] or \
            scene_pending["oracle_cases"] != 24 or \
            scene_pending["unresolved_before"] != 193 or scene_pending["unresolved_after"] != 192 or \
            scene_pending["imports_resolved"] != ["audio_ble_master_reset_scene_pending_4a2658"] or \
            scene_pending["imports_added"]:
        raise RuntimeError("Apollo Main scene-pending reset changed")
    begin_notify_path = G2 / "build/c-firmware/20261015/main-ble-master-begin-failure-notify-4a1546/receipt.json"
    begin_notify, begin_notify_ref = receipt(begin_notify_path)
    if begin_notify["status"] != "PASS_EXPERIMENTAL_MAIN_BLE_MASTER_BEGIN_FAILURE_NOTIFY_C" or \
            begin_notify["base_sha256"] != scene_pending["linked_sha256"] or \
            begin_notify["oracle_cases"] != 54 or \
            begin_notify["unresolved_before"] != 192 or begin_notify["unresolved_after"] != 191 or \
            begin_notify["imports_resolved"] != ["audio_ble_master_begin_failure_notify_4a1546"] or \
            begin_notify["imports_added"]:
        raise RuntimeError("Apollo Main failure-notify arming changed")
    cancel_timeout_path = G2 / "build/c-firmware/20261015/main-ring-policy-cancel-connect-timeout-49f5f8/receipt.json"
    cancel_timeout, cancel_timeout_ref = receipt(cancel_timeout_path)
    if cancel_timeout["status"] != "PASS_EXPERIMENTAL_MAIN_RING_POLICY_CANCEL_CONNECT_TIMEOUT_C" or \
            cancel_timeout["base_sha256"] != begin_notify["linked_sha256"] or \
            cancel_timeout["oracle_cases"] != 18 or \
            cancel_timeout["unresolved_before"] != 191 or cancel_timeout["unresolved_after"] != 190 or \
            cancel_timeout["imports_resolved"] != ["audio_ble_ring_policy_cancel_connect_timeout_49f5f8"] or \
            cancel_timeout["imports_added"]:
        raise RuntimeError("Apollo Main ring timeout cancellation changed")
    schedule_timeouts_path = G2 / "build/c-firmware/20261015/main-ring-policy-schedule-timeouts-49f4a8-49f552/receipt.json"
    schedule_timeouts, schedule_timeouts_ref = receipt(schedule_timeouts_path)
    if schedule_timeouts["status"] != "PASS_EXPERIMENTAL_MAIN_RING_POLICY_SCHEDULE_TIMEOUTS_C" or \
            schedule_timeouts["base_sha256"] != cancel_timeout["linked_sha256"] or \
            schedule_timeouts["oracle_cases"] != 36 or \
            schedule_timeouts["unresolved_before"] != 190 or schedule_timeouts["unresolved_after"] != 188 or \
            schedule_timeouts["imports_resolved"] != ["audio_ble_ring_policy_schedule_connect_timeout_49f4a8", "audio_ble_ring_policy_schedule_reconnect_timeout_49f552"] or \
            schedule_timeouts["imports_added"]:
        raise RuntimeError("Apollo Main ring timeout scheduling changed")
    system_close_path = G2 / "build/c-firmware/20261015/main-system-close-common-data-469d48/receipt.json"
    system_close, system_close_ref = receipt(system_close_path)
    if system_close["status"] != "PASS_EXPERIMENTAL_MAIN_SYSTEM_CLOSE_COMMON_DATA_C" or \
            system_close["base_sha256"] != schedule_timeouts["linked_sha256"] or \
            system_close["oracle_cases"] != 768 or \
            system_close["unresolved_before"] != 188 or system_close["unresolved_after"] != 188 or \
            system_close["imports_resolved"] != ["audio_uart_registry_callback_469d48"] or \
            system_close["imports_added"] != ["audio_system_close_active_app_get_443504"]:
        raise RuntimeError("Apollo Main system-close common-data handler changed")
    active_app_path = G2 / "build/c-firmware/20261015/main-system-close-active-app-get-443504/receipt.json"
    active_app, active_app_ref = receipt(active_app_path)
    if active_app["status"] != "PASS_EXPERIMENTAL_MAIN_SYSTEM_CLOSE_ACTIVE_APP_GET_C" or \
            active_app["base_sha256"] != system_close["linked_sha256"] or \
            active_app["oracle_cases"] != 192 or \
            active_app["unresolved_before"] != 188 or active_app["unresolved_after"] != 187 or \
            active_app["imports_resolved"] != ["audio_system_close_active_app_get_443504"] or \
            active_app["imports_added"]:
        raise RuntimeError("Apollo Main system-close active-app getter changed")
    production_path = G2 / "build/c-firmware/20261015/main-production-test-screen-event-5cf7f2/receipt.json"
    production, production_ref = receipt(production_path)
    if production["status"] != "PASS_EXPERIMENTAL_MAIN_PRODUCTION_TEST_SCREEN_EVENT_C" or \
            production["base_sha256"] != active_app["linked_sha256"] or \
            production["oracle_cases"] != 28 or \
            production["unresolved_before"] != 187 or production["unresolved_after"] != 187 or \
            production["imports_resolved"] != ["audio_uart_registry_callback_5cf7f2"] or \
            production["imports_added"] != ["audio_uart_page_441068"]:
        raise RuntimeError("Apollo Main production-test screen event changed")
    color_path = G2 / "build/c-firmware/20261015/main-lv-color-make-441068/receipt.json"
    color, color_ref = receipt(color_path)
    if color["status"] != "PASS_EXPERIMENTAL_MAIN_LV_COLOR_MAKE_C" or \
            color["base_sha256"] != production["linked_sha256"] or \
            color["oracle_cases"] != 216 or \
            color["unresolved_before"] != 187 or color["unresolved_after"] != 186 or \
            color["imports_resolved"] != ["audio_uart_page_441068"] or color["imports_added"]:
        raise RuntimeError("Apollo Main LV RGB888 constructor changed")
    gray_path = G2 / "build/c-firmware/20261015/main-gray-screen-event-5cf67e/receipt.json"
    gray, gray_ref = receipt(gray_path)
    if gray["status"] != "PASS_EXPERIMENTAL_MAIN_GRAY_SCREEN_EVENT_C" or \
            gray["base_sha256"] != color["linked_sha256"] or \
            gray["oracle_cases"] != 28 or \
            gray["unresolved_before"] != 186 or gray["unresolved_after"] != 185 or \
            gray["imports_resolved"] != ["audio_uart_registry_callback_5cf67e"] or gray["imports_added"]:
        raise RuntimeError("Apollo Main gray-screen event changed")
    test_context_path = G2 / "build/c-firmware/20261015/main-test-screen-registry-context-min/receipt.json"
    test_context, test_context_ref = receipt(test_context_path)
    if test_context["status"] != "PASS_EXPERIMENTAL_MAIN_TEST_SCREEN_REGISTRY_CONTEXT_MIN_C" or \
            test_context["base_sha256"] != gray["linked_sha256"] or \
            test_context["linked_sha256"] != main_obj["sha256"] or \
            test_context["observed_minimum_bytes_per_context"] != 8 or \
            test_context["unresolved_before"] != 185 or test_context["unresolved_after"] != 183 or \
            test_context["imports_resolved"] != ["audio_uart_registry_context_20003080", "audio_uart_registry_context_200030a0"] or \
            test_context["imports_added"]:
        raise RuntimeError("Apollo Main UI test context minima changed")
    distortion_path = G2 / "build/c-firmware/20261016/main-distortion-screen-event-5cf330/oracle-receipt.json"
    distortion, distortion_ref = receipt(distortion_path)
    distortion_source = ROOT / distortion["source"]
    if distortion["status"] != "PASS_NATIVE_MAIN_DISTORTION_SCREEN_EVENT_5CF330" or \
            distortion["cases"] != 28 or distortion["visited_stock_instruction_addresses"] != 276 or \
            distortion["official_payload_sha256"] != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701" or \
            distortion["source_sha256"] != sha(distortion_source):
        raise RuntimeError("Apollo Main distortion-screen callback oracle changed")
    distortion_style_path = G2 / "build/c-firmware/20261016/main-distortion-style-wrappers/oracle-receipt.json"
    distortion_style, distortion_style_ref = receipt(distortion_style_path)
    if distortion_style["status"] != "PASS_NATIVE_MAIN_DISTORTION_STYLE_WRAPPERS" or \
            distortion_style["cases"] != 48 or distortion_style["controlled_style_apply_calls"] != 80 or \
            distortion_style["source_sha256"] != sha(ROOT / distortion_style["source"]):
        raise RuntimeError("Apollo Main distortion style oracle changed")
    distortion_closure_path = G2 / "build/c-firmware/20261016/main-distortion-screen-closure/receipt.json"
    distortion_closure, distortion_closure_ref = receipt(distortion_closure_path)
    if distortion_closure["status"] != "PASS_EXPERIMENTAL_MAIN_DISTORTION_SCREEN_C_CLOSURE" or \
            distortion_closure["base_sha256"] != main_obj["sha256"] or \
            distortion_closure["callback_oracle_sha256"] != distortion_ref["sha256"] or \
            distortion_closure["style_oracle_sha256"] != distortion_style_ref["sha256"] or \
            distortion_closure["unresolved_before"] != 183 or \
            distortion_closure["unresolved_after"] != 182 or \
            distortion_closure["imports_resolved"] != ["audio_uart_registry_callback_5cf330"] or \
            distortion_closure["imports_added"] or \
            distortion_closure["asset"]["pixel_bytes"] != 576:
        raise RuntimeError("Apollo Main distortion closure changed")
    main_obj = file_checked(distortion_closure["linked_object"], distortion_closure["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 182:
        raise RuntimeError("Apollo Main distortion closure import count changed")
    legal_path = G2 / "build/c-firmware/20261016/main-legal-regulatory-event-5bf7b8/oracle-receipt.json"
    legal, legal_ref = receipt(legal_path)
    if legal["status"] != "PASS_NATIVE_MAIN_LEGAL_REGULATORY_EVENT_5BF7B8" or \
            legal["cases"] != 140 or legal["visited_stock_instruction_addresses"] != 98 or \
            legal["source_sha256"] != sha(ROOT / legal["source"]) or \
            legal["official_payload_sha256"] != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo Main legal-regulatory callback oracle changed")
    legal_fade_path = G2 / "build/c-firmware/20261016/main-legal-fade-in-58c238/oracle-receipt.json"
    legal_fade, legal_fade_ref = receipt(legal_fade_path)
    if legal_fade["status"] != "PASS_NATIVE_MAIN_LEGAL_FADE_IN_58C238" or \
            legal_fade["cases"] != 300 or legal_fade["visited_stock_instruction_addresses"] != 92 or \
            legal_fade["source_sha256"] != sha(ROOT / legal_fade["source"]):
        raise RuntimeError("Apollo Main legal fade-in oracle changed")
    legal_helpers_path = G2 / "build/c-firmware/20261016/main-legal-fade-helpers/oracle-receipt.json"
    legal_helpers, legal_helpers_ref = receipt(legal_helpers_path)
    if legal_helpers["status"] != "PASS_NATIVE_MAIN_LEGAL_FADE_HELPERS" or \
            legal_helpers["cases"] != 64 or \
            legal_helpers["source_sha256"] != sha(ROOT / legal_helpers["source"]):
        raise RuntimeError("Apollo Main legal fade helper oracle changed")
    legal_chain_path = G2 / "build/c-firmware/20261016/main-legal-regulatory-chain/receipt.json"
    legal_chain, legal_chain_ref = receipt(legal_chain_path)
    if legal_chain["status"] != "PASS_EXPERIMENTAL_MAIN_LEGAL_REGULATORY_CHAIN_C" or \
            legal_chain["base_sha256"] != main_obj["sha256"] or \
            legal_chain["unresolved_before"] != 182 or legal_chain["unresolved_after"] != 182 or \
            legal_chain["imports_resolved"] != ["audio_uart_registry_callback_5bf7b8"] or \
            legal_chain["imports_added"] != ["audio_legal_regulatory_build_5bf332"] or \
            [x["sha256"] for x in legal_chain["oracles"]] != \
                [legal_ref["sha256"], legal_fade_ref["sha256"], legal_helpers_ref["sha256"]]:
        raise RuntimeError("Apollo Main legal-regulatory chain changed")
    main_obj = file_checked(legal_chain["linked_object"], legal_chain["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 182 or "audio_legal_regulatory_build_5bf332" not in actual:
        raise RuntimeError("Apollo Main legal-regulatory chain import count changed")
    legal_page_helpers_path = G2 / "build/c-firmware/20261016/main-legal-page-helpers/oracle-receipt.json"
    legal_page_helpers, legal_page_helpers_ref = receipt(legal_page_helpers_path)
    if legal_page_helpers["status"] != "PASS_NATIVE_MAIN_LEGAL_PAGE_HELPERS" or \
            legal_page_helpers["cases"] != 112 or \
            legal_page_helpers["controlled_lower_calls"] != 496 or \
            legal_page_helpers["source_sha256"] != sha(ROOT / legal_page_helpers["source"]):
        raise RuntimeError("Apollo Main legal page helper oracle changed")
    legal_assets_path = G2 / "build/c-firmware/20261016/main-legal-assets/receipt.json"
    legal_assets, legal_assets_ref = receipt(legal_assets_path)
    if legal_assets["status"] != "PASS_SOURCE_OWNED_MAIN_LEGAL_ASSETS" or \
            legal_assets["rows"] != 38 or legal_assets["images"] != 10 or \
            legal_assets["texts"] != 28 or legal_assets["pixel_bytes"] != 40596 or \
            legal_assets["relocations"] != 48 or \
            legal_assets["source_sha256"] != sha(ROOT / legal_assets["source"]):
        raise RuntimeError("Apollo Main legal resource object changed")
    legal_assets_bound_path = G2 / "build/c-firmware/20261016/main-legal-assets-bound/receipt.json"
    legal_assets_bound, legal_assets_bound_ref = receipt(legal_assets_bound_path)
    if legal_assets_bound["status"] != "PASS_EXPERIMENTAL_MAIN_LEGAL_ASSETS_BOUND" or \
            legal_assets_bound["base_sha256"] != main_obj["sha256"] or \
            legal_assets_bound["asset_oracle_sha256"] != legal_assets_ref["sha256"] or \
            legal_assets_bound["unresolved_before"] != 182 or \
            legal_assets_bound["unresolved_after"] != 182 or \
            legal_assets_bound["imports_resolved"] or legal_assets_bound["imports_added"]:
        raise RuntimeError("Apollo Main legal asset binding changed")
    main_obj = file_checked(legal_assets_bound["linked_object"], legal_assets_bound["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 182 or "audio_legal_regulatory_build_5bf332" not in actual:
        raise RuntimeError("Apollo Main legal asset link import count changed")
    legal_builder_path = G2 / "build/c-firmware/20261016/main-legal-page-build-5bf332/oracle-receipt.json"
    legal_builder, legal_builder_ref = receipt(legal_builder_path)
    if legal_builder["status"] != "PASS_NATIVE_MAIN_LEGAL_PAGE_BUILD_5BF332" or \
            legal_builder["cases"] != 3 or legal_builder["controlled_lower_calls"] != 333 or \
            legal_builder["visited_stock_instruction_addresses"] != 446 or \
            legal_builder["source_sha256"] != sha(ROOT / legal_builder["source"]):
        raise RuntimeError("Apollo Main legal page builder oracle changed")
    legal_builder_bound_path = G2 / "build/c-firmware/20261016/main-legal-page-builder-bound/receipt.json"
    legal_builder_bound, legal_builder_bound_ref = receipt(legal_builder_bound_path)
    if legal_builder_bound["status"] != "PASS_EXPERIMENTAL_MAIN_LEGAL_PAGE_BUILDER_C" or \
            legal_builder_bound["base_sha256"] != main_obj["sha256"] or \
            legal_builder_bound["helper_oracle_sha256"] != legal_page_helpers_ref["sha256"] or \
            legal_builder_bound["builder_oracle_sha256"] != legal_builder_ref["sha256"] or \
            legal_builder_bound["asset_receipt_sha256"] != legal_assets_ref["sha256"] or \
            legal_builder_bound["unresolved_before"] != 182 or \
            legal_builder_bound["unresolved_after"] != 182 or \
            legal_builder_bound["imports_resolved"] != ["audio_legal_regulatory_build_5bf332"] or \
            legal_builder_bound["imports_added"] != ["audio_uart_page_43f6d6"]:
        raise RuntimeError("Apollo Main legal page builder closure changed")
    main_obj = file_checked(legal_builder_bound["linked_object"], legal_builder_bound["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 182 or "audio_uart_page_43f6d6" not in actual:
        raise RuntimeError("Apollo Main legal page builder link import count changed")
    align_oracle_path = G2 / "build/c-firmware/20261016/main-align-to-43f6d6/oracle-receipt.json"
    align_oracle, align_oracle_ref = receipt(align_oracle_path)
    if align_oracle["status"] != "PASS_NATIVE_MAIN_ALIGN_TO_43F6D6" or \
            align_oracle["cases"] != 230 or \
            align_oracle["source_sha256"] != sha(ROOT / align_oracle["source"]):
        raise RuntimeError("Apollo Main alignment oracle changed")
    align_bound_path = G2 / "build/c-firmware/20261016/main-align-to-bound/receipt.json"
    align_bound, align_bound_ref = receipt(align_bound_path)
    if align_bound["status"] != "PASS_EXPERIMENTAL_MAIN_ALIGN_TO_C" or \
            align_bound["base_sha256"] != main_obj["sha256"] or \
            align_bound["oracle_sha256"] != align_oracle_ref["sha256"] or \
            align_bound["unresolved_before"] != 182 or \
            align_bound["unresolved_after"] != 181 or \
            align_bound["imports_resolved"] != ["audio_uart_page_43f6d6"] or \
            align_bound["imports_added"]:
        raise RuntimeError("Apollo Main alignment binding changed")
    main_obj = file_checked(align_bound["linked_object"], align_bound["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 181 or "audio_uart_page_43f6d6" in actual:
        raise RuntimeError("Apollo Main alignment link import count changed")
    even_ai_oracle_path = G2 / "build/c-firmware/20261016/main-even-ai-common-4e2976/oracle-receipt.json"
    even_ai_oracle, even_ai_oracle_ref = receipt(even_ai_oracle_path)
    if even_ai_oracle["status"] != "PASS_NATIVE_MAIN_EVEN_AI_COMMON_4E2976" or \
            even_ai_oracle["cases"] != 90 or \
            even_ai_oracle["source_sha256"] != sha(ROOT / even_ai_oracle["source"]):
        raise RuntimeError("Apollo Main EvenAI common-data oracle changed")
    even_ai_bound_path = G2 / "build/c-firmware/20261016/main-even-ai-common-bound/receipt.json"
    even_ai_bound, even_ai_bound_ref = receipt(even_ai_bound_path)
    if even_ai_bound["status"] != "PASS_EXPERIMENTAL_MAIN_EVEN_AI_COMMON_C" or \
            even_ai_bound["base_sha256"] != main_obj["sha256"] or \
            even_ai_bound["oracle_sha256"] != even_ai_oracle_ref["sha256"] or \
            even_ai_bound["unresolved_before"] != 181 or \
            even_ai_bound["unresolved_after"] != 184 or \
            even_ai_bound["imports_resolved"] != ["audio_uart_registry_callback_4e2976"] or \
            len(even_ai_bound["imports_added"]) != 4:
        raise RuntimeError("Apollo Main EvenAI common-data binding changed")
    main_obj = file_checked(even_ai_bound["linked_object"], even_ai_bound["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 184 or "audio_uart_registry_callback_4e2976" in actual:
        raise RuntimeError("Apollo Main EvenAI common-data link import count changed")
    even_ai_prepare_oracle_path = G2 / "build/c-firmware/20261016/main-even-ai-prepare-4e1f7c/oracle-receipt.json"
    even_ai_prepare_oracle, even_ai_prepare_oracle_ref = receipt(even_ai_prepare_oracle_path)
    if even_ai_prepare_oracle["status"] != "PASS_NATIVE_MAIN_EVEN_AI_PREPARE_4E1F7C" or \
            even_ai_prepare_oracle["cases"] != 4 or \
            even_ai_prepare_oracle["ram_cell"] != "0x20074580" or \
            even_ai_prepare_oracle["source_sha256"] != sha(ROOT / even_ai_prepare_oracle["source"]):
        raise RuntimeError("Apollo Main EvenAI prepare oracle changed")
    even_ai_prepare_bound_path = G2 / "build/c-firmware/20261016/main-even-ai-prepare-bound/receipt.json"
    even_ai_prepare_bound, even_ai_prepare_bound_ref = receipt(even_ai_prepare_bound_path)
    if even_ai_prepare_bound["status"] != "PASS_EXPERIMENTAL_MAIN_EVEN_AI_PREPARE_C" or \
            even_ai_prepare_bound["base_sha256"] != main_obj["sha256"] or \
            even_ai_prepare_bound["oracle_sha256"] != even_ai_prepare_oracle_ref["sha256"] or \
            even_ai_prepare_bound["unresolved_before"] != 184 or \
            even_ai_prepare_bound["unresolved_after"] != 186 or \
            even_ai_prepare_bound["imports_resolved"] != ["audio_even_ai_prepare_4e1f7c"] or \
            len(even_ai_prepare_bound["imports_added"]) != 3:
        raise RuntimeError("Apollo Main EvenAI prepare binding changed")
    main_obj = file_checked(even_ai_prepare_bound["linked_object"], even_ai_prepare_bound["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 186 or "audio_even_ai_prepare_4e1f7c" in actual:
        raise RuntimeError("Apollo Main EvenAI prepare link import count changed")
    mutex_oracle_path = G2 / "build/c-firmware/20261016/main-os-mutex-new-44971c/oracle-receipt.json"
    mutex_oracle, mutex_oracle_ref = receipt(mutex_oracle_path)
    if mutex_oracle["status"] != "PASS_NATIVE_MAIN_OS_MUTEX_NEW_44971C" or \
            mutex_oracle["cases"] != 128 or \
            mutex_oracle["source_sha256"] != sha(ROOT / mutex_oracle["source"]) or \
            mutex_oracle["attributed_upstream_sha256"] != sha(ROOT / mutex_oracle["attributed_upstream"]) or \
            mutex_oracle["attributed_upstream_commit"] != "d213f261b5be6bb29a7cce8b84071706b72f4d53":
        raise RuntimeError("Apollo Main osMutexNew oracle changed")
    mutex_bound_path = G2 / "build/c-firmware/20261016/main-os-mutex-new-bound/receipt.json"
    mutex_bound, mutex_bound_ref = receipt(mutex_bound_path)
    if mutex_bound["status"] != "PASS_EXPERIMENTAL_MAIN_OS_MUTEX_NEW_C" or \
            mutex_bound["base_sha256"] != main_obj["sha256"] or \
            mutex_bound["oracle_sha256"] != mutex_oracle_ref["sha256"] or \
            mutex_bound["unresolved_before"] != 186 or \
            mutex_bound["unresolved_after"] != 188 or \
            mutex_bound["imports_resolved"] != ["audio_even_ai_mutex_create_44971c"] or \
            len(mutex_bound["imports_added"]) != 3:
        raise RuntimeError("Apollo Main osMutexNew binding changed")
    main_obj = file_checked(mutex_bound["linked_object"], mutex_bound["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 188 or "audio_even_ai_mutex_create_44971c" in actual:
        raise RuntimeError("Apollo Main osMutexNew link import count changed")
    alloc_wrappers_oracle_path = G2 / "build/c-firmware/20261016/main-os-mutex-alloc-wrappers-4416d6/oracle-receipt.json"
    alloc_wrappers_oracle, alloc_wrappers_oracle_ref = receipt(alloc_wrappers_oracle_path)
    if alloc_wrappers_oracle["status"] != "PASS_NATIVE_MAIN_OS_MUTEX_ALLOC_WRAPPERS_4416D6" or \
            alloc_wrappers_oracle["cases"] != 40 or \
            alloc_wrappers_oracle["source_sha256"] != sha(ROOT / alloc_wrappers_oracle["source"]):
        raise RuntimeError("Apollo Main mutex allocation wrapper oracle changed")
    alloc_wrappers_bound_path = G2 / "build/c-firmware/20261016/main-os-mutex-alloc-wrappers-bound/receipt.json"
    alloc_wrappers_bound, alloc_wrappers_bound_ref = receipt(alloc_wrappers_bound_path)
    if alloc_wrappers_bound["status"] != "PASS_EXPERIMENTAL_MAIN_OS_MUTEX_ALLOC_WRAPPERS_C" or \
            alloc_wrappers_bound["base_sha256"] != main_obj["sha256"] or \
            alloc_wrappers_bound["oracle_sha256"] != alloc_wrappers_oracle_ref["sha256"] or \
            alloc_wrappers_bound["unresolved_before"] != 188 or \
            alloc_wrappers_bound["unresolved_after"] != 189 or \
            len(alloc_wrappers_bound["imports_resolved"]) != 2 or \
            len(alloc_wrappers_bound["imports_added"]) != 3:
        raise RuntimeError("Apollo Main mutex allocation wrapper binding changed")
    main_obj = file_checked(alloc_wrappers_bound["linked_object"], alloc_wrappers_bound["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 189 or "audio_os_mutex_alloc_dynamic_4416d6" in actual or \
            "audio_os_mutex_alloc_static_4416f0" in actual:
        raise RuntimeError("Apollo Main mutex allocation wrapper link count changed")
    mutex_register_oracle_path = G2 / "build/c-firmware/20261016/main-os-mutex-register-4416b8/oracle-receipt.json"
    mutex_register_oracle, mutex_register_oracle_ref = receipt(mutex_register_oracle_path)
    if mutex_register_oracle["status"] != "PASS_NATIVE_MAIN_OS_MUTEX_REGISTER_4416B8" or \
            mutex_register_oracle["cases"] != 6 or \
            mutex_register_oracle["source_sha256"] != sha(ROOT / mutex_register_oracle["source"]):
        raise RuntimeError("Apollo Main mutex register oracle changed")
    mutex_register_bound_path = G2 / "build/c-firmware/20261016/main-os-mutex-register-bound/receipt.json"
    mutex_register_bound, mutex_register_bound_ref = receipt(mutex_register_bound_path)
    if mutex_register_bound["status"] != "PASS_EXPERIMENTAL_MAIN_OS_MUTEX_REGISTER_C" or \
            mutex_register_bound["base_sha256"] != main_obj["sha256"] or \
            mutex_register_bound["oracle_sha256"] != mutex_register_oracle_ref["sha256"] or \
            mutex_register_bound["unresolved_before"] != 189 or \
            mutex_register_bound["unresolved_after"] != 188 or \
            mutex_register_bound["imports_resolved"] != ["audio_os_mutex_register_4416b8"] or \
            mutex_register_bound["imports_added"]:
        raise RuntimeError("Apollo Main mutex register binding changed")
    main_obj = file_checked(mutex_register_bound["linked_object"], mutex_register_bound["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 188 or "audio_os_mutex_register_4416b8" in actual:
        raise RuntimeError("Apollo Main mutex register link import count changed")
    irq_oracle_path = G2 / "build/c-firmware/20261016/main-os-irq-context-44900e/oracle-receipt.json"
    irq_oracle, irq_oracle_ref = receipt(irq_oracle_path)
    if irq_oracle["status"] != "PASS_NATIVE_MAIN_OS_IRQ_CONTEXT_44900E" or \
            irq_oracle["cases"] != 36 or \
            irq_oracle["source_sha256"] != sha(ROOT / irq_oracle["source"]) or \
            irq_oracle["attributed_upstream_sha256"] != sha(ROOT / irq_oracle["attributed_upstream"]) or \
            irq_oracle["attributed_upstream_commit"] != "d213f261b5be6bb29a7cce8b84071706b72f4d53":
        raise RuntimeError("Apollo Main IRQ_Context oracle or upstream changed")
    irq_bound_path = G2 / "build/c-firmware/20261016/main-os-irq-context-bound/receipt.json"
    irq_bound, irq_bound_ref = receipt(irq_bound_path)
    if irq_bound["status"] != "PASS_EXPERIMENTAL_MAIN_OS_IRQ_CONTEXT_C" or \
            irq_bound["base_sha256"] != main_obj["sha256"] or \
            irq_bound["oracle_sha256"] != irq_oracle_ref["sha256"] or \
            irq_bound["unresolved_before"] != 188 or \
            irq_bound["unresolved_after"] != 188 or \
            irq_bound["imports_resolved"] != ["audio_os_irq_context_44900e"] or \
            irq_bound["imports_added"] != ["audio_os_scheduler_state_4558a4"]:
        raise RuntimeError("Apollo Main IRQ_Context binding changed")
    main_obj = file_checked(irq_bound["linked_object"], irq_bound["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 188 or "audio_os_irq_context_44900e" in actual:
        raise RuntimeError("Apollo Main IRQ_Context link import count changed")
    scheduler_oracle_path = G2 / "build/c-firmware/20261016/main-os-scheduler-state-4558a4/oracle-receipt.json"
    scheduler_oracle, scheduler_oracle_ref = receipt(scheduler_oracle_path)
    if scheduler_oracle["status"] != "PASS_NATIVE_MAIN_OS_SCHEDULER_STATE_4558A4" or \
            scheduler_oracle["cases"] != 9 or \
            scheduler_oracle["source_sha256"] != sha(ROOT / scheduler_oracle["source"]) or \
            scheduler_oracle["attributed_upstream_sha256"] != sha(ROOT / scheduler_oracle["attributed_upstream"]) or \
            scheduler_oracle["attributed_upstream_commit"] != "d213f261b5be6bb29a7cce8b84071706b72f4d53":
        raise RuntimeError("Apollo Main scheduler state oracle or upstream changed")
    scheduler_bound_path = G2 / "build/c-firmware/20261016/main-os-scheduler-state-bound/receipt.json"
    scheduler_bound, scheduler_bound_ref = receipt(scheduler_bound_path)
    if scheduler_bound["status"] != "PASS_EXPERIMENTAL_MAIN_OS_SCHEDULER_STATE_C" or \
            scheduler_bound["base_sha256"] != main_obj["sha256"] or \
            scheduler_bound["oracle_sha256"] != scheduler_oracle_ref["sha256"] or \
            scheduler_bound["unresolved_before"] != 188 or \
            scheduler_bound["unresolved_after"] != 189 or \
            scheduler_bound["imports_resolved"] != ["audio_os_scheduler_state_4558a4"] or \
            len(scheduler_bound["imports_added"]) != 2:
        raise RuntimeError("Apollo Main scheduler state binding changed")
    main_obj = file_checked(scheduler_bound["linked_object"], scheduler_bound["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 189 or "audio_os_scheduler_state_4558a4" in actual:
        raise RuntimeError("Apollo Main scheduler state link import count changed")
    mask_oracle_path = G2 / "build/c-firmware/20261016/main-os-interrupt-mask-5fa0a4/oracle-receipt.json"
    mask_oracle, mask_oracle_ref = receipt(mask_oracle_path)
    if mask_oracle["status"] != "PASS_NATIVE_MAIN_OS_INTERRUPT_MASK_5FA0A4" or \
            mask_oracle["cases"] != 6 or \
            mask_oracle["source_sha256"] != sha(ROOT / mask_oracle["source"]):
        raise RuntimeError("Apollo Main interrupt mask oracle changed")
    mask_bound_path = G2 / "build/c-firmware/20261016/main-os-interrupt-mask-bound/receipt.json"
    mask_bound, mask_bound_ref = receipt(mask_bound_path)
    if mask_bound["status"] != "PASS_EXPERIMENTAL_MAIN_OS_INTERRUPT_MASK_C" or \
            mask_bound["base_sha256"] != main_obj["sha256"] or \
            mask_bound["oracle_sha256"] != mask_oracle_ref["sha256"] or \
            mask_bound["unresolved_before"] != 189 or \
            mask_bound["unresolved_after"] != 188 or \
            mask_bound["imports_resolved"] != ["audio_os_interrupt_mask_5fa0a4"] or \
            mask_bound["imports_added"]:
        raise RuntimeError("Apollo Main interrupt mask binding changed")
    main_obj = file_checked(mask_bound["linked_object"], mask_bound["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 188 or "audio_os_interrupt_mask_5fa0a4" in actual:
        raise RuntimeError("Apollo Main interrupt mask link import count changed")
    queue_cores_oracle_path = G2 / "build/c-firmware/20261016/main-os-queue-create-cores-4415ca/oracle-receipt.json"
    queue_cores_oracle, queue_cores_oracle_ref = receipt(queue_cores_oracle_path)
    if queue_cores_oracle["status"] != "PASS_NATIVE_MAIN_OS_QUEUE_CREATE_CORES_4415CA" or \
            queue_cores_oracle["cases"] != 96 or \
            queue_cores_oracle["source_sha256"] != sha(ROOT / queue_cores_oracle["source"]) or \
            queue_cores_oracle["attributed_upstream_sha256"] != sha(ROOT / queue_cores_oracle["attributed_upstream"]) or \
            queue_cores_oracle["attributed_upstream_commit"] != "d213f261b5be6bb29a7cce8b84071706b72f4d53":
        raise RuntimeError("Apollo Main queue creation core oracle or upstream changed")
    queue_cores_bound_path = G2 / "build/c-firmware/20261016/main-os-queue-create-cores-bound/receipt.json"
    queue_cores_bound, queue_cores_bound_ref = receipt(queue_cores_bound_path)
    if queue_cores_bound["status"] != "PASS_EXPERIMENTAL_MAIN_OS_QUEUE_CREATE_CORES_C" or \
            queue_cores_bound["base_sha256"] != main_obj["sha256"] or \
            queue_cores_bound["oracle_sha256"] != queue_cores_oracle_ref["sha256"] or \
            queue_cores_bound["unresolved_before"] != 188 or \
            queue_cores_bound["unresolved_after"] != 187 or \
            len(queue_cores_bound["imports_resolved"]) != 2 or \
            queue_cores_bound["imports_added"] != ["audio_os_queue_initialize_441696"]:
        raise RuntimeError("Apollo Main queue creation core binding changed")
    main_obj = file_checked(queue_cores_bound["linked_object"], queue_cores_bound["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 187 or "audio_os_mutex_static_core_4415ca" in actual or \
            "audio_os_mutex_dynamic_core_441636" in actual:
        raise RuntimeError("Apollo Main queue creation core link import count changed")
    queue_init_oracle_path = G2 / "build/c-firmware/20261016/main-os-queue-initialize-441696/oracle-receipt.json"
    queue_init_oracle, queue_init_oracle_ref = receipt(queue_init_oracle_path)
    if queue_init_oracle["status"] != "PASS_NATIVE_MAIN_OS_QUEUE_INITIALIZE_441696" or \
            queue_init_oracle["cases"] != 54 or \
            queue_init_oracle["source_sha256"] != sha(ROOT / queue_init_oracle["source"]) or \
            queue_init_oracle["attributed_upstream_sha256"] != sha(ROOT / queue_init_oracle["attributed_upstream"]) or \
            queue_init_oracle["attributed_upstream_commit"] != "d213f261b5be6bb29a7cce8b84071706b72f4d53":
        raise RuntimeError("Apollo Main queue initializer oracle or upstream changed")
    queue_init_bound_path = G2 / "build/c-firmware/20261016/main-os-queue-initialize-bound/receipt.json"
    queue_init_bound, queue_init_bound_ref = receipt(queue_init_bound_path)
    if queue_init_bound["status"] != "PASS_EXPERIMENTAL_MAIN_OS_QUEUE_INITIALIZE_C" or \
            queue_init_bound["base_sha256"] != main_obj["sha256"] or \
            queue_init_bound["oracle_sha256"] != queue_init_oracle_ref["sha256"] or \
            queue_init_bound["unresolved_before"] != 187 or \
            queue_init_bound["unresolved_after"] != 187 or \
            queue_init_bound["imports_resolved"] != ["audio_os_queue_initialize_441696"] or \
            queue_init_bound["imports_added"] != ["audio_os_queue_reset_441516"]:
        raise RuntimeError("Apollo Main queue initializer binding changed")
    main_obj = file_checked(queue_init_bound["linked_object"], queue_init_bound["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 187 or "audio_os_queue_initialize_441696" in actual:
        raise RuntimeError("Apollo Main queue initializer link import count changed")
    queue_reset_oracle_path = G2 / "build/c-firmware/20261016/main-os-queue-reset-441516/oracle-receipt.json"
    queue_reset_oracle, queue_reset_oracle_ref = receipt(queue_reset_oracle_path)
    if queue_reset_oracle["status"] != "PASS_NATIVE_MAIN_OS_QUEUE_RESET_441516" or \
            queue_reset_oracle["cases"] != 80 or \
            queue_reset_oracle["source_sha256"] != sha(ROOT / queue_reset_oracle["source"]) or \
            queue_reset_oracle["attributed_upstream_sha256"] != sha(ROOT / queue_reset_oracle["attributed_upstream"]) or \
            queue_reset_oracle["attributed_upstream_commit"] != "d213f261b5be6bb29a7cce8b84071706b72f4d53":
        raise RuntimeError("Apollo Main queue reset oracle or upstream changed")
    queue_reset_bound_path = G2 / "build/c-firmware/20261016/main-os-queue-reset-bound/receipt.json"
    queue_reset_bound, queue_reset_bound_ref = receipt(queue_reset_bound_path)
    if queue_reset_bound["status"] != "PASS_EXPERIMENTAL_MAIN_OS_QUEUE_RESET_C" or \
            queue_reset_bound["base_sha256"] != main_obj["sha256"] or \
            queue_reset_bound["oracle_sha256"] != queue_reset_oracle_ref["sha256"] or \
            queue_reset_bound["unresolved_before"] != 187 or \
            queue_reset_bound["unresolved_after"] != 187 or \
            queue_reset_bound["imports_resolved"] != ["audio_os_queue_reset_441516"] or \
            queue_reset_bound["imports_added"] != ["audio_os_list_initialize_45607c"] or \
            queue_reset_bound["existing_event_removal_review_sha256"] != sha(ROOT / queue_reset_bound["existing_event_removal_review"]):
        raise RuntimeError("Apollo Main queue reset binding changed")
    main_obj = file_checked(queue_reset_bound["linked_object"], queue_reset_bound["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 187 or "audio_os_queue_reset_441516" in actual:
        raise RuntimeError("Apollo Main queue reset link import count changed")
    list_init_oracle_path = G2 / "build/c-firmware/20261016/main-os-list-initialize-45607c/oracle-receipt.json"
    list_init_oracle, list_init_oracle_ref = receipt(list_init_oracle_path)
    if list_init_oracle["status"] != "PASS_NATIVE_MAIN_OS_LIST_INITIALIZE_45607C" or \
            list_init_oracle["cases"] != 9 or \
            list_init_oracle["source_sha256"] != sha(ROOT / list_init_oracle["source"]) or \
            list_init_oracle["attributed_upstream_sha256"] != sha(ROOT / list_init_oracle["attributed_upstream"]) or \
            list_init_oracle["attributed_upstream_commit"] != "d213f261b5be6bb29a7cce8b84071706b72f4d53":
        raise RuntimeError("Apollo Main list initializer oracle or upstream changed")
    list_init_bound_path = G2 / "build/c-firmware/20261016/main-os-list-initialize-bound/receipt.json"
    list_init_bound, list_init_bound_ref = receipt(list_init_bound_path)
    if list_init_bound["status"] != "PASS_EXPERIMENTAL_MAIN_OS_LIST_INITIALIZE_C" or \
            list_init_bound["base_sha256"] != main_obj["sha256"] or \
            list_init_bound["oracle_sha256"] != list_init_oracle_ref["sha256"] or \
            list_init_bound["unresolved_before"] != 187 or \
            list_init_bound["unresolved_after"] != 186 or \
            list_init_bound["imports_resolved"] != ["audio_os_list_initialize_45607c"] or \
            list_init_bound["imports_added"]:
        raise RuntimeError("Apollo Main list initializer binding changed")
    main_obj = file_checked(list_init_bound["linked_object"], list_init_bound["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 186 or "audio_os_list_initialize_45607c" in actual:
        raise RuntimeError("Apollo Main list initializer link import count changed")
    even_ai_chain_path = G2 / "build/c-firmware/20261016/main-even-ai-frame-chain-bound/receipt.json"
    even_ai_chain, even_ai_chain_ref = receipt(even_ai_chain_path)
    if even_ai_chain["status"] != "PASS_EXPERIMENTAL_MAIN_EVEN_AI_FRAME_CHAIN_C" or \
            even_ai_chain["base_sha256"] != main_obj["sha256"] or \
            even_ai_chain["unresolved_before"] != 186 or \
            even_ai_chain["unresolved_after"] != 191 or \
            even_ai_chain["imports_resolved"] != ["audio_even_ai_frame_process_4e31cc"] or \
            len(even_ai_chain["imports_added"]) != 6:
        raise RuntimeError("Apollo Main EvenAI frame chain binding changed")
    main_obj = file_checked(even_ai_chain["linked_object"], even_ai_chain["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 191 or "audio_even_ai_frame_process_4e31cc" in actual:
        raise RuntimeError("Apollo Main EvenAI frame chain frontier changed")
    even_ai_ram_path = G2 / "build/c-firmware/20261016/main-even-ai-ram-state-bound/receipt.json"
    even_ai_ram, even_ai_ram_ref = receipt(even_ai_ram_path)
    if even_ai_ram["status"] != "PASS_EXPERIMENTAL_MAIN_EVEN_AI_RAM_STATE_C" or \
            even_ai_ram["base_sha256"] != main_obj["sha256"] or \
            even_ai_ram["unresolved_before"] != 191 or \
            even_ai_ram["unresolved_after"] != 184 or \
            len(even_ai_ram["imports_resolved"]) != 7 or \
            even_ai_ram["imports_added"] or \
            even_ai_ram["other_fixed_ram_sections_checked"] != 149:
        raise RuntimeError("Apollo Main EvenAI RAM binding changed")
    main_obj = file_checked(even_ai_ram["linked_object"], even_ai_ram["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 184 or "audio_even_ai_mutex_20074580" in actual:
        raise RuntimeError("Apollo Main EvenAI RAM frontier changed")
    scheduler_ram_path = G2 / "build/c-firmware/20261016/main-os-scheduler-state-ram-bound/receipt.json"
    scheduler_ram, scheduler_ram_ref = receipt(scheduler_ram_path)
    if scheduler_ram["status"] != "PASS_EXPERIMENTAL_MAIN_OS_SCHEDULER_STATE_RAM_C" or \
            scheduler_ram["base_sha256"] != main_obj["sha256"] or \
            scheduler_ram["unresolved_before"] != 184 or \
            scheduler_ram["unresolved_after"] != 182 or \
            scheduler_ram["imports_resolved"] != ["audio_os_scheduler_running_20074a3c",
                                                  "audio_os_scheduler_suspended_20074a58"] or \
            scheduler_ram["imports_added"]:
        raise RuntimeError("Apollo Main scheduler RAM binding changed")
    main_obj = file_checked(scheduler_ram["linked_object"], scheduler_ram["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 182 or "audio_os_scheduler_running_20074a3c" in actual or \
            "audio_os_scheduler_suspended_20074a58" in actual:
        raise RuntimeError("Apollo Main scheduler RAM frontier changed")
    dashboard_ram_path = G2 / "build/c-firmware/20261016/main-dashboard-layout-current-ram-bound/receipt.json"
    dashboard_ram, dashboard_ram_ref = receipt(dashboard_ram_path)
    if dashboard_ram["status"] != "PASS_EXPERIMENTAL_MAIN_DASHBOARD_LAYOUT_CURRENT_RAM_C" or \
            dashboard_ram["base_sha256"] != main_obj["sha256"] or \
            dashboard_ram["unresolved_before"] != 182 or \
            dashboard_ram["unresolved_after"] != 181 or \
            dashboard_ram["imports_resolved"] != ["audio_dashboard_layout_current"] or \
            dashboard_ram["imports_added"] or \
            dashboard_ram["address"] != "0x200e7934" or dashboard_ram["bytes"] != 128:
        raise RuntimeError("Apollo Main dashboard layout RAM binding changed")
    main_obj = file_checked(dashboard_ram["linked_object"], dashboard_ram["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 181 or "audio_dashboard_layout_current" in actual:
        raise RuntimeError("Apollo Main dashboard layout RAM frontier changed")
    efs_ram_path = G2 / "build/c-firmware/20261016/main-efs-transfer-state-ram-bound/receipt.json"
    efs_ram, efs_ram_ref = receipt(efs_ram_path)
    if efs_ram["status"] != "PASS_EXPERIMENTAL_MAIN_EFS_TRANSFER_STATE_RAM_C" or \
            efs_ram["base_sha256"] != main_obj["sha256"] or \
            efs_ram["unresolved_before"] != 181 or \
            efs_ram["unresolved_after"] != 180 or \
            efs_ram["imports_resolved"] != ["audio_efs_transfer_state"] or \
            efs_ram["imports_added"] or \
            efs_ram["address"] != "0x20071cc8" or efs_ram["bytes"] != 0x76:
        raise RuntimeError("Apollo Main EFS transfer RAM binding changed")
    main_obj = file_checked(efs_ram["linked_object"], efs_ram["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 180 or "audio_efs_transfer_state" in actual:
        raise RuntimeError("Apollo Main EFS transfer RAM frontier changed")
    flash_staging_path = G2 / "build/c-firmware/20261016/main-ble-flash-staging-ram-bound/receipt.json"
    flash_staging, flash_staging_ref = receipt(flash_staging_path)
    if flash_staging["status"] != "PASS_EXPERIMENTAL_MAIN_BLE_FLASH_STAGING_RAM_C" or \
            flash_staging["base_sha256"] != main_obj["sha256"] or \
            flash_staging["unresolved_before"] != 180 or \
            flash_staging["unresolved_after"] != 179 or \
            flash_staging["imports_resolved"] != ["audio_ble_flash_staging_200636a0"] or \
            flash_staging["imports_added"] or \
            flash_staging["address"] != "0x200636a0" or flash_staging["bytes"] != 0x0a00:
        raise RuntimeError("Apollo Main BLE flash staging RAM binding changed")
    main_obj = file_checked(flash_staging["linked_object"], flash_staging["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 179 or "audio_ble_flash_staging_200636a0" in actual:
        raise RuntimeError("Apollo Main BLE flash staging RAM frontier changed")
    battery_manager_path = G2 / "build/c-firmware/20261016/main-battery-callback-manager-ram-bound/receipt.json"
    battery_manager, battery_manager_ref = receipt(battery_manager_path)
    if battery_manager["status"] != "PASS_EXPERIMENTAL_MAIN_BATTERY_CALLBACK_MANAGER_RAM_C" or \
            battery_manager["base_sha256"] != main_obj["sha256"] or \
            battery_manager["unresolved_before"] != 179 or \
            battery_manager["unresolved_after"] != 177 or \
            battery_manager["imports_resolved"] != ["audio_charge_callback_manager",
                                                    "audio_ring_battery_callback_manager"] or \
            battery_manager["imports_added"] or len(battery_manager["spans"]) != 2:
        raise RuntimeError("Apollo Main battery callback manager RAM binding changed")
    main_obj = file_checked(battery_manager["linked_object"], battery_manager["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 177 or "audio_charge_callback_manager" in actual or \
            "audio_ring_battery_callback_manager" in actual:
        raise RuntimeError("Apollo Main battery callback manager RAM frontier changed")
    ble_callbacks_path = G2 / "build/c-firmware/20261016/main-ble-flash-callbacks-ram-bound/receipt.json"
    ble_callbacks, ble_callbacks_ref = receipt(ble_callbacks_path)
    if ble_callbacks["status"] != "PASS_EXPERIMENTAL_MAIN_BLE_FLASH_CALLBACKS_RAM_C" or \
            ble_callbacks["base_sha256"] != main_obj["sha256"] or \
            ble_callbacks["unresolved_before"] != 177 or \
            ble_callbacks["unresolved_after"] != 176 or \
            ble_callbacks["imports_resolved"] != ["audio_ble_flash_callbacks"] or \
            ble_callbacks["imports_added"] or \
            ble_callbacks["address"] != "0x20073270" or ble_callbacks["bytes"] != 60:
        raise RuntimeError("Apollo Main BLE flash callbacks RAM binding changed")
    main_obj = file_checked(ble_callbacks["linked_object"], ble_callbacks["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 176 or "audio_ble_flash_callbacks" in actual:
        raise RuntimeError("Apollo Main BLE flash callbacks RAM frontier changed")
    tpl_buffer_path = G2 / "build/c-firmware/20261016/main-tpl-response-buffer-ram-bound/receipt.json"
    tpl_buffer, tpl_buffer_ref = receipt(tpl_buffer_path)
    if tpl_buffer["status"] != "PASS_EXPERIMENTAL_MAIN_TPL_RESPONSE_BUFFER_RAM_C" or \
            tpl_buffer["base_sha256"] != main_obj["sha256"] or \
            tpl_buffer["unresolved_before"] != 176 or \
            tpl_buffer["unresolved_after"] != 175 or \
            tpl_buffer["imports_resolved"] != ["audio_tpl_response_buffer"] or \
            tpl_buffer["imports_added"] or \
            tpl_buffer["address"] != "0x20004204" or tpl_buffer["bytes"] != 8:
        raise RuntimeError("Apollo Main TPL response buffer RAM binding changed")
    main_obj = file_checked(tpl_buffer["linked_object"], tpl_buffer["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 175 or "audio_tpl_response_buffer" in actual:
        raise RuntimeError("Apollo Main TPL response buffer RAM frontier changed")
    tpl_timeout_path = G2 / "build/c-firmware/20261016/main-tpl-timeout-ids-ram-bound/receipt.json"
    tpl_timeout, tpl_timeout_ref = receipt(tpl_timeout_path)
    if tpl_timeout["status"] != "PASS_EXPERIMENTAL_MAIN_TPL_TIMEOUT_IDS_RAM_C" or \
            tpl_timeout["base_sha256"] != main_obj["sha256"] or \
            tpl_timeout["unresolved_before"] != 175 or \
            tpl_timeout["unresolved_after"] != 174 or \
            tpl_timeout["imports_resolved"] != ["audio_tpl_timeout_ids"] or \
            tpl_timeout["imports_added"] or \
            tpl_timeout["address"] != "0x20074b04" or tpl_timeout["bytes"] != 3:
        raise RuntimeError("Apollo Main TPL timeout IDs RAM binding changed")
    main_obj = file_checked(tpl_timeout["linked_object"], tpl_timeout["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 174 or "audio_tpl_timeout_ids" in actual:
        raise RuntimeError("Apollo Main TPL timeout IDs RAM frontier changed")
    tpl_row_path = G2 / "build/c-firmware/20261016/main-tpl-service-row0-ram-bound/receipt.json"
    tpl_row, tpl_row_ref = receipt(tpl_row_path)
    if tpl_row["status"] != "PASS_EXPERIMENTAL_MAIN_TPL_SERVICE_ROW0_RAM_C" or \
            tpl_row["base_sha256"] != main_obj["sha256"] or \
            tpl_row["unresolved_before"] != 174 or \
            tpl_row["unresolved_after"] != 173 or \
            tpl_row["imports_resolved"] != ["audio_tpl_service_table"] or \
            tpl_row["imports_added"] or \
            tpl_row["address"] != "0x20071414" or tpl_row["bytes"] != 20:
        raise RuntimeError("Apollo Main TPL service row RAM binding changed")
    main_obj = file_checked(tpl_row["linked_object"], tpl_row["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 173 or "audio_tpl_service_table" in actual:
        raise RuntimeError("Apollo Main TPL service row RAM frontier changed")
    local_decode_path = G2 / "build/c-firmware/20261016/main-even-ai-local-decode/receipt.json"
    local_decode, local_decode_ref = receipt(local_decode_path)
    if local_decode["status"] != "PASS_EXPERIMENTAL_MAIN_EVEN_AI_LOCAL_DECODE_C" or \
            local_decode["base_sha256"] != main_obj["sha256"] or \
            local_decode["unresolved_before"] != 173 or \
            local_decode["unresolved_after"] != 174 or \
            local_decode["imports_resolved"] != ["audio_even_ai_local_decode_498092"] or \
            local_decode["imports_added"] != ["audio_even_ai_encode_ctrl_4e3788",
                                               "audio_even_ai_encode_vad_4e3b80"]:
        raise RuntimeError("Apollo Main EvenAI local decode binding changed")
    main_obj = file_checked(local_decode["linked_object"], local_decode["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 174 or "audio_even_ai_local_decode_498092" in actual or \
            "audio_even_ai_encode_ctrl_4e3788" not in actual or \
            "audio_even_ai_encode_vad_4e3b80" not in actual:
        raise RuntimeError("Apollo Main EvenAI local decode frontier changed")
    notify_path = G2 / "build/c-firmware/20261016/main-even-ai-notify-encoders-bound/receipt.json"
    notify, notify_ref = receipt(notify_path)
    if notify["status"] != "PASS_EXPERIMENTAL_MAIN_EVEN_AI_NOTIFY_ENCODERS_C" or \
            notify["base_sha256"] != main_obj["sha256"] or \
            notify["unresolved_before"] != 174 or \
            notify["unresolved_after"] != 172 or \
            notify["imports_resolved"] != ["audio_even_ai_encode_ctrl_4e3788",
                                           "audio_even_ai_encode_vad_4e3b80"] or \
            notify["imports_added"] or \
            notify["sequence_address"] != "0x20074ff9" or \
            notify["sequence_bytes"] != 1:
        raise RuntimeError("Apollo Main EvenAI notification encoders binding changed")
    main_obj = file_checked(notify["linked_object"], notify["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 172 or "audio_even_ai_encode_ctrl_4e3788" in actual or \
            "audio_even_ai_encode_vad_4e3b80" in actual:
        raise RuntimeError("Apollo Main EvenAI notification encoder frontier changed")
    ready_ram_path = G2 / "build/c-firmware/20261016/main-even-ai-ready-ram-bound/receipt.json"
    ready_ram, ready_ram_ref = receipt(ready_ram_path)
    if ready_ram["status"] != "PASS_EXPERIMENTAL_MAIN_EVEN_AI_READY_RAM_C" or \
            ready_ram["base_sha256"] != main_obj["sha256"] or \
            ready_ram["unresolved_before"] != 172 or \
            ready_ram["unresolved_after"] != 172 or \
            ready_ram["imports_resolved"] or ready_ram["imports_added"] or \
            [(span["address"], span["bytes"]) for span in ready_ram["spans"]] != [
                ("0x2006f138", 0x218), ("0x20074c04", 4),
                ("0x200f39b4", 0x400), ("0x200f3db4", 0x400)]:
        raise RuntimeError("Apollo Main EvenAI ready RAM binding changed")
    main_obj = file_checked(ready_ram["linked_object"], ready_ram["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 172 or "audio_even_ai_ready_4e20f2" not in actual:
        raise RuntimeError("Apollo Main EvenAI ready RAM frontier changed")
    ready_simple_path = G2 / "build/c-firmware/20261016/main-even-ai-ready-simple-oracle/oracle-receipt.json"
    ready_simple, ready_simple_ref = receipt(ready_simple_path)
    if ready_simple["status"] != "PASS_EXPERIMENTAL_EVEN_AI_READY_SIMPLE_C_ORACLE" or \
            ready_simple["cases"] != 84 or \
            ready_simple["source_sha256"] != sha(ROOT / ready_simple["source"]) or \
            ready_simple["payload_sha256"] != ready_ram["payload_sha256"]:
        raise RuntimeError("Apollo Main EvenAI ready simple candidate oracle changed")
    ready_bound_path = G2 / "build/c-firmware/20261016/main-even-ai-ready-bound/receipt.json"
    ready_bound, ready_bound_ref = receipt(ready_bound_path)
    if ready_bound["status"] != "PASS_EXPERIMENTAL_MAIN_EVEN_AI_READY_C" or \
            ready_bound["base_sha256"] != main_obj["sha256"] or \
            ready_bound["unresolved_before"] != 172 or \
            ready_bound["unresolved_after"] != 183 or \
            ready_bound["imports_resolved"] != ["audio_even_ai_ready_4e20f2"] or \
            len(ready_bound["imports_added"]) != 12 or \
            ready_bound["oracle_receipt_sha256"] != ready_simple_ref["sha256"]:
        raise RuntimeError("Apollo Main EvenAI ready binding changed")
    main_obj = file_checked(ready_bound["linked_object"], ready_bound["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 183 or "audio_even_ai_ready_4e20f2" in actual or \
            not set(ready_bound["imports_added"]) <= set(actual):
        raise RuntimeError("Apollo Main EvenAI ready frontier changed")
    accessors_path = G2 / "build/c-firmware/20261016/main-even-ai-ready-accessors/receipt.json"
    accessors, accessors_ref = receipt(accessors_path)
    if accessors["status"] != "PASS_EXPERIMENTAL_MAIN_EVEN_AI_READY_ACCESSORS_C" or \
            accessors["base_sha256"] != main_obj["sha256"] or \
            accessors["unresolved_before"] != 183 or \
            accessors["unresolved_after"] != 181 or \
            accessors["imports_resolved"] != ["audio_even_ai_stream_interval_get_4e550a",
                                              "audio_text_stream_pending_text_552ce8"] or \
            accessors["imports_added"] or \
            accessors["empty_string_stock_address"] != "0x552cf4":
        raise RuntimeError("Apollo Main EvenAI ready accessor binding changed")
    main_obj = file_checked(accessors["linked_object"], accessors["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 181 or any(x in actual for x in accessors["imports_resolved"]):
        raise RuntimeError("Apollo Main EvenAI ready accessor frontier changed")
    timer_path = G2 / "build/c-firmware/20261016/main-even-ai-common-timer/receipt.json"
    timer, timer_ref = receipt(timer_path)
    if timer["status"] != "PASS_EXPERIMENTAL_MAIN_EVEN_AI_COMMON_TIMER_START_C" or \
            timer["base_sha256"] != main_obj["sha256"] or \
            timer["unresolved_before"] != 181 or timer["unresolved_after"] != 180 or \
            timer["imports_resolved"] != ["audio_even_ai_timer_start_all_4e31a0"] or \
            timer["imports_added"]:
        raise RuntimeError("Apollo Main EvenAI common timer binding changed")
    main_obj = file_checked(timer["linked_object"], timer["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 180 or "audio_even_ai_timer_start_all_4e31a0" in actual:
        raise RuntimeError("Apollo Main EvenAI common timer frontier changed")
    timer_stop_path = G2 / "build/c-firmware/20261016/main-even-ai-common-timer-stop/receipt.json"
    timer_stop, timer_stop_ref = receipt(timer_stop_path)
    if timer_stop["status"] != "PASS_EXPERIMENTAL_MAIN_EVEN_AI_COMMON_TIMER_STOP_C" or \
            timer_stop["base_sha256"] != main_obj["sha256"] or \
            timer_stop["unresolved_before"] != 180 or timer_stop["unresolved_after"] != 179 or \
            timer_stop["imports_resolved"] != ["audio_even_ai_common_timer_stop_4e2e86"] or \
            timer_stop["imports_added"]:
        raise RuntimeError("Apollo Main EvenAI common timer stop binding changed")
    main_obj = file_checked(timer_stop["linked_object"], timer_stop["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 179 or "audio_even_ai_common_timer_stop_4e2e86" in actual:
        raise RuntimeError("Apollo Main EvenAI common timer stop frontier changed")
    text_init_path = G2 / "build/c-firmware/20261016/main-even-ai-init-text-stream/receipt.json"
    text_init, text_init_ref = receipt(text_init_path)
    if text_init["status"] != "PASS_EXPERIMENTAL_MAIN_EVEN_AI_INIT_TEXT_STREAM_C" or \
            text_init["base_sha256"] != main_obj["sha256"] or \
            text_init["unresolved_before"] != 179 or text_init["unresolved_after"] != 179 or \
            text_init["imports_resolved"] != ["audio_even_ai_init_text_stream_4e551e"] or \
            text_init["imports_added"] != ["audio_text_stream_create_552b30"]:
        raise RuntimeError("Apollo Main EvenAI text initializer binding changed")
    main_obj = file_checked(text_init["linked_object"], text_init["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 179 or "audio_even_ai_init_text_stream_4e551e" in actual or \
            "audio_text_stream_create_552b30" not in actual:
        raise RuntimeError("Apollo Main EvenAI text initializer frontier changed")
    text_create_path = G2 / "build/c-firmware/20261016/main-text-stream-create/receipt.json"
    text_create, text_create_ref = receipt(text_create_path)
    if text_create["status"] != "PASS_EXPERIMENTAL_MAIN_TEXT_STREAM_CREATE_C" or \
            text_create["base_sha256"] != main_obj["sha256"] or \
            text_create["unresolved_before"] != 179 or text_create["unresolved_after"] != 179 or \
            text_create["imports_resolved"] != ["audio_text_stream_create_552b30"] or \
            text_create["imports_added"] != ["audio_text_stream_buffer_create_553338"]:
        raise RuntimeError("Apollo Main text-stream allocator binding changed")
    main_obj = file_checked(text_create["linked_object"], text_create["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 179 or "audio_text_stream_create_552b30" in actual or \
            "audio_text_stream_buffer_create_553338" not in actual:
        raise RuntimeError("Apollo Main text-stream allocator frontier changed")
    text_buffer_path = G2 / "build/c-firmware/20261016/main-text-stream-buffer-create/receipt.json"
    text_buffer, text_buffer_ref = receipt(text_buffer_path)
    if text_buffer["status"] != "PASS_EXPERIMENTAL_MAIN_TEXT_STREAM_BUFFER_CREATE_C" or \
            text_buffer["base_sha256"] != main_obj["sha256"] or \
            text_buffer["unresolved_before"] != 179 or text_buffer["unresolved_after"] != 179 or \
            text_buffer["imports_resolved"] != ["audio_text_stream_buffer_create_553338"] or \
            text_buffer["imports_added"] != ["audio_file_heap_realloc"]:
        raise RuntimeError("Apollo Main text-stream buffer binding changed")
    main_obj = file_checked(text_buffer["linked_object"], text_buffer["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 179 or "audio_text_stream_buffer_create_553338" in actual or \
            "audio_file_heap_realloc" not in actual:
        raise RuntimeError("Apollo Main text-stream buffer frontier changed")
    heap_realloc_path = G2 / "build/c-firmware/20261016/main-file-heap-realloc/receipt.json"
    heap_realloc, heap_realloc_ref = receipt(heap_realloc_path)
    if heap_realloc["status"] != "PASS_EXPERIMENTAL_MAIN_FILE_HEAP_REALLOC_C" or \
            heap_realloc["base_sha256"] != main_obj["sha256"] or \
            heap_realloc["unresolved_before"] != 179 or heap_realloc["unresolved_after"] != 178 or \
            heap_realloc["imports_resolved"] != ["audio_file_heap_realloc"] or \
            heap_realloc["imports_added"]:
        raise RuntimeError("Apollo Main file-heap realloc binding changed")
    main_obj = file_checked(heap_realloc["linked_object"], heap_realloc["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 178 or "audio_file_heap_realloc" in actual:
        raise RuntimeError("Apollo Main file-heap realloc frontier changed")
    heap_ram_path = G2 / "build/c-firmware/20261016/main-file-heap-ram-cells/receipt.json"
    heap_ram, heap_ram_ref = receipt(heap_ram_path)
    if heap_ram["status"] != "PASS_EXPERIMENTAL_MAIN_FILE_HEAP_RAM_CELLS" or \
            heap_ram["base_sha256"] != main_obj["sha256"] or \
            heap_ram["unresolved_before"] != 178 or heap_ram["unresolved_after"] != 176 or \
            heap_ram["imports_resolved"] != ["g2_codec_heap_mutex", "g2_codec_heap_pool"] or \
            heap_ram["imports_added"] or \
            heap_ram["placements"] != {"g2_codec_heap_mutex": "0x200748f8",
                                       "g2_codec_heap_pool": "0x20074abc"}:
        raise RuntimeError("Apollo Main file-heap RAM binding changed")
    main_obj = file_checked(heap_ram["linked_object"], heap_ram["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 176 or any(x in actual for x in heap_ram["imports_resolved"]):
        raise RuntimeError("Apollo Main file-heap RAM frontier changed")
    pool_init_path = G2 / "build/c-firmware/20261016/main-file-tlsf-pool-init/receipt.json"
    pool_init, pool_init_ref = receipt(pool_init_path)
    if pool_init["status"] != "PASS_EXPERIMENTAL_MAIN_FILE_TLSF_POOL_INIT_C" or \
            pool_init["base_sha256"] != main_obj["sha256"] or \
            pool_init["unresolved_before"] != 176 or pool_init["unresolved_after"] != 176 or \
            pool_init["provider_linked"] != "audio_file_tlsf_pool_init_5eda64" or \
            pool_init["startup_wired"] or pool_init["imports_resolved"] or pool_init["imports_added"]:
        raise RuntimeError("Apollo Main TLSF pool initializer binding changed")
    main_obj = file_checked(pool_init["linked_object"], pool_init["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 176:
        raise RuntimeError("Apollo Main TLSF pool initializer frontier changed")
    backing_path = G2 / "build/c-firmware/20261016/main-file-tlsf-backing-ram/receipt.json"
    backing, backing_ref = receipt(backing_path)
    if backing["status"] != "PASS_EXPERIMENTAL_MAIN_FILE_TLSF_BACKING_RAM" or \
            backing["base_sha256"] != main_obj["sha256"] or \
            backing["unresolved_before"] != 176 or backing["unresolved_after"] != 176 or \
            backing["stock_address"] != "0x20208e70" or backing["size"] != "0x70800" or \
            backing["end_exclusive"] != "0x20279670" or \
            backing["startup_wired"] or backing["imports_resolved"] or backing["imports_added"]:
        raise RuntimeError("Apollo Main TLSF backing RAM binding changed")
    main_obj = file_checked(backing["linked_object"], backing["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 176:
        raise RuntimeError("Apollo Main TLSF backing RAM frontier changed")
    redirect_path = G2 / "build/c-firmware/20261016/main-file-redirect-init/receipt.json"
    redirect, redirect_ref = receipt(redirect_path)
    if redirect["status"] != "PASS_EXPERIMENTAL_MAIN_FILE_REDIRECT_INIT_C" or \
            redirect["base_sha256"] != main_obj["sha256"] or \
            redirect["unresolved_before"] != 176 or redirect["unresolved_after"] != 176 or \
            redirect["provider_linked"] != "audio_file_redirect_init_474d9c" or \
            redirect["ram_address"] != "0x200748f4" or redirect["startup_wired"] or \
            redirect["imports_resolved"] or redirect["imports_added"]:
        raise RuntimeError("Apollo Main redirect initializer binding changed")
    main_obj = file_checked(redirect["linked_object"], redirect["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 176:
        raise RuntimeError("Apollo Main redirect initializer frontier changed")
    stream_stop_path = G2 / "build/c-firmware/20261016/main-even-ai-stop-streaming/receipt.json"
    stream_stop, stream_stop_ref = receipt(stream_stop_path)
    if stream_stop["status"] != "PASS_EXPERIMENTAL_MAIN_EVEN_AI_STOP_STREAMING_C" or \
            stream_stop["base_sha256"] != main_obj["sha256"] or \
            stream_stop["unresolved_before"] != 176 or stream_stop["unresolved_after"] != 177 or \
            stream_stop["imports_resolved"] != ["audio_even_ai_stop_current_streaming_4e557c"] or \
            stream_stop["imports_added"] != ["audio_text_stream_pause_552d40",
                                              "audio_text_stream_stop_552d10"]:
        raise RuntimeError("Apollo Main EvenAI stop-stream binding changed")
    main_obj = file_checked(stream_stop["linked_object"], stream_stop["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 177 or "audio_even_ai_stop_current_streaming_4e557c" in actual or \
            not set(stream_stop["imports_added"]) <= set(actual):
        raise RuntimeError("Apollo Main EvenAI stop-stream frontier changed")
    stop_pause_path = G2 / "build/c-firmware/20261016/main-text-stream-stop-pause/receipt.json"
    stop_pause, stop_pause_ref = receipt(stop_pause_path)
    if stop_pause["status"] != "PASS_EXPERIMENTAL_MAIN_TEXT_STREAM_STOP_PAUSE_C" or \
            stop_pause["base_sha256"] != main_obj["sha256"] or \
            stop_pause["unresolved_before"] != 177 or stop_pause["unresolved_after"] != 175 or \
            stop_pause["imports_resolved"] != ["audio_text_stream_pause_552d40",
                                                "audio_text_stream_stop_552d10"] or \
            stop_pause["imports_added"]:
        raise RuntimeError("Apollo Main text-stream stop/pause binding changed")
    main_obj = file_checked(stop_pause["linked_object"], stop_pause["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 175 or any(x in actual for x in stop_pause["imports_resolved"]):
        raise RuntimeError("Apollo Main text-stream stop/pause frontier changed")
    text_copy_path = G2 / "build/c-firmware/20261016/main-text-stream-copy-bytes/receipt.json"
    text_copy, text_copy_ref = receipt(text_copy_path)
    if text_copy["status"] != "PASS_EXPERIMENTAL_MAIN_TEXT_STREAM_COPY_BYTES_C" or \
            text_copy["base_sha256"] != main_obj["sha256"] or \
            text_copy["unresolved_before"] != 175 or text_copy["unresolved_after"] != 174 or \
            text_copy["imports_resolved"] != ["audio_text_stream_copy_bytes_553274"] or \
            text_copy["imports_added"]:
        raise RuntimeError("Apollo Main text-stream copy binding changed")
    main_obj = file_checked(text_copy["linked_object"], text_copy["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 174 or "audio_text_stream_copy_bytes_553274" in actual:
        raise RuntimeError("Apollo Main text-stream copy frontier changed")
    set_text_path = G2 / "build/c-firmware/20261016/main-text-stream-set-text/receipt.json"
    set_text, set_text_ref = receipt(set_text_path)
    if set_text["status"] != "PASS_EXPERIMENTAL_MAIN_TEXT_STREAM_SET_TEXT_C" or \
            set_text["base_sha256"] != main_obj["sha256"] or \
            set_text["unresolved_before"] != 174 or set_text["unresolved_after"] != 177 or \
            set_text["imports_resolved"] != ["audio_text_stream_set_text_552c20"] or \
            set_text["imports_added"] != ["audio_text_stream_dispatch_552df0",
                                          "audio_text_stream_next_interval_5532f8",
                                          "audio_text_stream_restart_552db2",
                                          "audio_text_stream_validate_5533cc"]:
        raise RuntimeError("Apollo Main text-stream set-text binding changed")
    main_obj = file_checked(set_text["linked_object"], set_text["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 177 or "audio_text_stream_set_text_552c20" in actual or \
            not set(set_text["imports_added"]) <= set(actual):
        raise RuntimeError("Apollo Main text-stream set-text frontier changed")
    decision_path = G2 / "build/c-firmware/20261016/main-text-stream-decision-helpers/receipt.json"
    decision, decision_ref = receipt(decision_path)
    if decision["status"] != "PASS_EXPERIMENTAL_MAIN_TEXT_STREAM_DECISION_HELPERS_C" or \
            decision["base_sha256"] != main_obj["sha256"] or \
            decision["unresolved_before"] != 177 or decision["unresolved_after"] != 175 or \
            decision["imports_resolved"] != ["audio_text_stream_next_interval_5532f8",
                                              "audio_text_stream_validate_5533cc"] or \
            decision["imports_added"]:
        raise RuntimeError("Apollo Main text-stream decision binding changed")
    main_obj = file_checked(decision["linked_object"], decision["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 175 or any(x in actual for x in decision["imports_resolved"]):
        raise RuntimeError("Apollo Main text-stream decision frontier changed")
    restart_path = G2 / "build/c-firmware/20261016/main-text-stream-restart/receipt.json"
    restart, restart_ref = receipt(restart_path)
    if restart["status"] != "PASS_EXPERIMENTAL_MAIN_TEXT_STREAM_RESTART_C" or \
            restart["base_sha256"] != main_obj["sha256"] or \
            restart["unresolved_before"] != 175 or restart["unresolved_after"] != 174 or \
            restart["imports_resolved"] != ["audio_text_stream_restart_552db2"] or \
            restart["imports_added"]:
        raise RuntimeError("Apollo Main text-stream restart binding changed")
    main_obj = file_checked(restart["linked_object"], restart["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 174 or "audio_text_stream_restart_552db2" in actual:
        raise RuntimeError("Apollo Main text-stream restart frontier changed")
    dispatch_path = G2 / "build/c-firmware/20261016/main-text-stream-dispatch/receipt.json"
    dispatch, dispatch_ref = receipt(dispatch_path)
    if dispatch["status"] != "PASS_EXPERIMENTAL_MAIN_TEXT_STREAM_DISPATCH_C" or \
            dispatch["base_sha256"] != main_obj["sha256"] or \
            dispatch["unresolved_before"] != 174 or dispatch["unresolved_after"] != 175 or \
            dispatch["imports_resolved"] != ["audio_text_stream_dispatch_552df0"] or \
            dispatch["imports_added"] != ["audio_text_stream_begin_552f0a", "audio_text_stream_finish_552f14"]:
        raise RuntimeError("Apollo Main text-stream dispatch binding changed")
    main_obj = file_checked(dispatch["linked_object"], dispatch["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 175 or "audio_text_stream_dispatch_552df0" in actual or \
            "audio_text_stream_begin_552f0a" not in actual or "audio_text_stream_finish_552f14" not in actual:
        raise RuntimeError("Apollo Main text-stream dispatch frontier changed")
    begin_path = G2 / "build/c-firmware/20261016/main-text-stream-begin/receipt.json"
    begin, begin_ref = receipt(begin_path)
    if begin["status"] != "PASS_EXPERIMENTAL_MAIN_TEXT_STREAM_BEGIN_C" or \
            begin["base_sha256"] != main_obj["sha256"] or \
            begin["unresolved_before"] != 175 or begin["unresolved_after"] != 175 or \
            begin["imports_resolved"] != ["audio_text_stream_begin_552f0a"] or \
            begin["imports_added"] != ["audio_text_stream_schedule_552f6a"]:
        raise RuntimeError("Apollo Main text-stream begin binding changed")
    main_obj = file_checked(begin["linked_object"], begin["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 175 or "audio_text_stream_begin_552f0a" in actual or \
            "audio_text_stream_schedule_552f6a" not in actual:
        raise RuntimeError("Apollo Main text-stream begin frontier changed")
    finish_path = G2 / "build/c-firmware/20261016/main-text-stream-finish/receipt.json"
    finish, finish_ref = receipt(finish_path)
    if finish["status"] != "PASS_EXPERIMENTAL_MAIN_TEXT_STREAM_FINISH_C" or \
            finish["base_sha256"] != main_obj["sha256"] or \
            finish["unresolved_before"] != 175 or finish["unresolved_after"] != 174 or \
            finish["imports_resolved"] != ["audio_text_stream_finish_552f14"] or \
            finish["imports_added"]:
        raise RuntimeError("Apollo Main text-stream finish binding changed")
    main_obj = file_checked(finish["linked_object"], finish["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 174 or "audio_text_stream_finish_552f14" in actual:
        raise RuntimeError("Apollo Main text-stream finish frontier changed")
    schedule_path = G2 / "build/c-firmware/20261016/main-text-stream-schedule/receipt.json"
    schedule, schedule_ref = receipt(schedule_path)
    if schedule["status"] != "PASS_EXPERIMENTAL_MAIN_TEXT_STREAM_SCHEDULE_C" or \
            schedule["base_sha256"] != main_obj["sha256"] or \
            schedule["unresolved_before"] != 174 or schedule["unresolved_after"] != 174 or \
            schedule["imports_resolved"] != ["audio_text_stream_schedule_552f6a"] or \
            schedule["imports_added"] != ["audio_text_stream_tick_553054"]:
        raise RuntimeError("Apollo Main text-stream schedule binding changed")
    main_obj = file_checked(schedule["linked_object"], schedule["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 174 or "audio_text_stream_schedule_552f6a" in actual or \
            "audio_text_stream_tick_553054" not in actual:
        raise RuntimeError("Apollo Main text-stream schedule frontier changed")
    tick_path = G2 / "build/c-firmware/20261016/main-text-stream-tick/receipt.json"
    tick, tick_ref = receipt(tick_path)
    if tick["status"] != "PASS_EXPERIMENTAL_MAIN_TEXT_STREAM_TICK_C" or \
            tick["base_sha256"] != main_obj["sha256"] or \
            tick["unresolved_before"] != 174 or tick["unresolved_after"] != 173 or \
            tick["imports_resolved"] != ["audio_text_stream_tick_553054"] or \
            tick["imports_added"]:
        raise RuntimeError("Apollo Main text-stream tick binding changed")
    main_obj = file_checked(tick["linked_object"], tick["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 173 or "audio_text_stream_tick_553054" in actual:
        raise RuntimeError("Apollo Main text-stream tick frontier changed")
    app_acquire_path = G2 / "build/c-firmware/20261016/main-even-ai-app-acquire/receipt.json"
    app_acquire, app_acquire_ref = receipt(app_acquire_path)
    if app_acquire["status"] != "PASS_EXPERIMENTAL_MAIN_EVEN_AI_APP_ACQUIRE_C" or \
            app_acquire["base_sha256"] != main_obj["sha256"] or \
            app_acquire["unresolved_before"] != 173 or app_acquire["unresolved_after"] != 176 or \
            app_acquire["imports_resolved"] != ["audio_even_ai_app_acquire_54f380"] or \
            app_acquire["imports_added"] != ["audio_app_codec_enable_53ca32",
                                             "audio_app_first_hardware_prepare_57a926",
                                             "audio_app_stream_enable_53ca10",
                                             "g2_audio_first_hardware_context_20108948"]:
        raise RuntimeError("Apollo Main EvenAI app acquire binding changed")
    main_obj = file_checked(app_acquire["linked_object"], app_acquire["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 176 or "audio_even_ai_app_acquire_54f380" in actual or \
            not set(app_acquire["imports_added"]).issubset(actual):
        raise RuntimeError("Apollo Main EvenAI app acquire frontier changed")
    app_setup_path = G2 / "build/c-firmware/20261016/main-audio-app-setup-children/receipt.json"
    app_setup, app_setup_ref = receipt(app_setup_path)
    if app_setup["status"] != "PASS_EXPERIMENTAL_MAIN_AUDIO_APP_SETUP_CHILDREN_C" or \
            app_setup["base_sha256"] != main_obj["sha256"] or \
            app_setup["unresolved_before"] != 176 or app_setup["unresolved_after"] != 174 or \
            app_setup["imports_resolved"] != app_acquire["imports_added"] or \
            app_setup["imports_added"] != ["audio_app_control_packet_53c638",
                                           "audio_app_hardware_open_591374"]:
        raise RuntimeError("Apollo Main audio app setup binding changed")
    main_obj = file_checked(app_setup["linked_object"], app_setup["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 174 or set(app_setup["imports_resolved"]) & set(actual) or \
            not set(app_setup["imports_added"]).issubset(actual):
        raise RuntimeError("Apollo Main audio app setup frontier changed")
    app_control_path = G2 / "build/c-firmware/20261016/main-audio-app-control-and-open/receipt.json"
    app_control, app_control_ref = receipt(app_control_path)
    if app_control["status"] != "PASS_EXPERIMENTAL_MAIN_AUDIO_APP_CONTROL_AND_OPEN_C" or \
            app_control["base_sha256"] != main_obj["sha256"] or \
            app_control["unresolved_before"] != 174 or app_control["unresolved_after"] != 173 or \
            app_control["imports_resolved"] != app_setup["imports_added"] or \
            app_control["imports_added"] != ["audio_app_hardware_core_59123a"]:
        raise RuntimeError("Apollo Main audio app control binding changed")
    main_obj = file_checked(app_control["linked_object"], app_control["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 173 or set(app_control["imports_resolved"]) & set(actual) or \
            "audio_app_hardware_core_59123a" not in actual:
        raise RuntimeError("Apollo Main audio app control frontier changed")
    hardware_core_path = G2 / "build/c-firmware/20261016/main-audio-app-hardware-core/receipt.json"
    hardware_core, hardware_core_ref = receipt(hardware_core_path)
    if hardware_core["status"] != "PASS_EXPERIMENTAL_MAIN_AUDIO_APP_HARDWARE_CORE_C" or \
            hardware_core["base_sha256"] != main_obj["sha256"] or \
            hardware_core["unresolved_before"] != 173 or hardware_core["unresolved_after"] != 175 or \
            hardware_core["imports_resolved"] != ["audio_app_hardware_core_59123a"] or \
            hardware_core["imports_added"] != ["audio_app_format_index_590d74",
                                               "audio_app_rate_index_590d3c",
                                               "audio_app_zero_tail_4d4ccc"]:
        raise RuntimeError("Apollo Main audio hardware core binding changed")
    main_obj = file_checked(hardware_core["linked_object"], hardware_core["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 175 or "audio_app_hardware_core_59123a" in actual or \
            not set(hardware_core["imports_added"]).issubset(actual):
        raise RuntimeError("Apollo Main audio hardware core frontier changed")
    hardware_indices_path = G2 / "build/c-firmware/20261016/main-audio-app-hardware-indices/receipt.json"
    hardware_indices, hardware_indices_ref = receipt(hardware_indices_path)
    if hardware_indices["status"] != "PASS_EXPERIMENTAL_MAIN_AUDIO_APP_HARDWARE_INDICES_C" or \
            hardware_indices["base_sha256"] != main_obj["sha256"] or \
            hardware_indices["unresolved_before"] != 175 or hardware_indices["unresolved_after"] != 172 or \
            hardware_indices["imports_resolved"] != hardware_core["imports_added"] or \
            hardware_indices["imports_added"]:
        raise RuntimeError("Apollo Main audio hardware indices binding changed")
    main_obj = file_checked(hardware_indices["linked_object"], hardware_indices["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 172 or set(hardware_indices["imports_resolved"]) & set(actual):
        raise RuntimeError("Apollo Main audio hardware indices frontier changed")
    sync_remote_path = G2 / "build/c-firmware/20261016/main-even-ai-sync-remote/receipt.json"
    sync_remote, sync_remote_ref = receipt(sync_remote_path)
    if sync_remote["status"] != "PASS_EXPERIMENTAL_MAIN_EVEN_AI_SYNC_REMOTE_C" or \
            sync_remote["base_sha256"] != main_obj["sha256"] or \
            sync_remote["unresolved_before"] != 172 or sync_remote["unresolved_after"] != 172 or \
            sync_remote["imports_resolved"] != ["audio_even_ai_sync_remote_4973f4"] or \
            sync_remote["imports_added"] != ["audio_even_ai_ancc_display_clear_4e1af8"]:
        raise RuntimeError("Apollo Main EvenAI sync remote binding changed")
    main_obj = file_checked(sync_remote["linked_object"], sync_remote["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 172 or "audio_even_ai_sync_remote_4973f4" in actual or \
            "audio_even_ai_ancc_display_clear_4e1af8" not in actual:
        raise RuntimeError("Apollo Main EvenAI sync remote frontier changed")
    ancc_display_path = G2 / "build/c-firmware/20261016/main-even-ai-ancc-display-clear/receipt.json"
    ancc_display, ancc_display_ref = receipt(ancc_display_path)
    if ancc_display["status"] != "PASS_EXPERIMENTAL_MAIN_EVEN_AI_ANCC_DISPLAY_CLEAR_C" or \
            ancc_display["base_sha256"] != main_obj["sha256"] or \
            ancc_display["unresolved_before"] != 172 or ancc_display["unresolved_after"] != 173 or \
            ancc_display["imports_resolved"] != ["audio_even_ai_ancc_display_clear_4e1af8"] or \
            ancc_display["imports_added"] != ["audio_even_ai_ancc_display_send_5105bc",
                                              "g2_audio_ancc_display_context_20073f84"]:
        raise RuntimeError("Apollo Main ANCC display wrapper binding changed")
    main_obj = file_checked(ancc_display["linked_object"], ancc_display["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 173 or "audio_even_ai_ancc_display_clear_4e1af8" in actual or \
            not set(ancc_display["imports_added"]).issubset(actual):
        raise RuntimeError("Apollo Main ANCC display wrapper frontier changed")
    ancc_send_path = G2 / "build/c-firmware/20261016/main-even-ai-ancc-display-send/receipt.json"
    ancc_send, ancc_send_ref = receipt(ancc_send_path)
    if ancc_send["status"] != "PASS_EXPERIMENTAL_MAIN_EVEN_AI_ANCC_DISPLAY_SEND_C" or \
            ancc_send["base_sha256"] != main_obj["sha256"] or \
            ancc_send["unresolved_before"] != 173 or ancc_send["unresolved_after"] != 171 or \
            ancc_send["imports_resolved"] != ancc_display["imports_added"] or \
            ancc_send["imports_added"]:
        raise RuntimeError("Apollo Main ANCC display send binding changed")
    main_obj = file_checked(ancc_send["linked_object"], ancc_send["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 171 or set(ancc_send["imports_resolved"]) & set(actual):
        raise RuntimeError("Apollo Main ANCC display send frontier changed")
    ancc_state_path = G2 / "build/c-firmware/20261016/main-even-ai-ancc-state-sync/receipt.json"
    ancc_state, ancc_state_ref = receipt(ancc_state_path)
    if ancc_state["status"] != "PASS_EXPERIMENTAL_MAIN_EVEN_AI_ANCC_STATE_SYNC_C" or \
            ancc_state["base_sha256"] != main_obj["sha256"] or \
            ancc_state["unresolved_before"] != 171 or ancc_state["unresolved_after"] != 170 or \
            ancc_state["imports_resolved"] != ["audio_even_ai_ancc_state_sync_497cf0"] or \
            ancc_state["imports_added"]:
        raise RuntimeError("Apollo Main ANCC state sync binding changed")
    main_obj = file_checked(ancc_state["linked_object"], ancc_state["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 170 or "audio_even_ai_ancc_state_sync_497cf0" in actual:
        raise RuntimeError("Apollo Main ANCC state sync frontier changed")
    display_ctrl_path = G2 / "build/c-firmware/20261016/main-even-ai-display-ctrl/receipt.json"
    display_ctrl, display_ctrl_ref = receipt(display_ctrl_path)
    if display_ctrl["status"] != "PASS_EXPERIMENTAL_MAIN_EVEN_AI_DISPLAY_CTRL_C" or \
            display_ctrl["base_sha256"] != main_obj["sha256"] or \
            display_ctrl["unresolved_before"] != 170 or display_ctrl["unresolved_after"] != 169 or \
            display_ctrl["imports_resolved"] != ["audio_even_ai_display_ctrl_4e1fd2"] or \
            display_ctrl["imports_added"]:
        raise RuntimeError("Apollo Main EvenAI display control binding changed")
    main_obj = file_checked(display_ctrl["linked_object"], display_ctrl["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 169 or "audio_even_ai_display_ctrl_4e1fd2" in actual:
        raise RuntimeError("Apollo Main EvenAI display control frontier changed")
    message_notify_path = G2 / "build/c-firmware/20261016/main-message-notify-common/receipt.json"
    message_notify, message_notify_ref = receipt(message_notify_path)
    if message_notify["status"] != "PASS_EXPERIMENTAL_MAIN_MESSAGE_NOTIFY_COMMON_C" or \
            message_notify["base_sha256"] != main_obj["sha256"] or \
            message_notify["unresolved_before"] != 169 or message_notify["unresolved_after"] != 169 or \
            message_notify["imports_resolved"] != ["audio_uart_registry_callback_4e1b30"] or \
            message_notify["imports_added"] != ["audio_message_notify_frame_process_4d6ba8"]:
        raise RuntimeError("Apollo Main MessageNotify callback binding changed")
    main_obj = file_checked(message_notify["linked_object"], message_notify["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 169 or "audio_uart_registry_callback_4e1b30" in actual or \
            "audio_message_notify_frame_process_4d6ba8" not in actual:
        raise RuntimeError("Apollo Main MessageNotify frontier changed")
    message_frame_path = G2 / "build/c-firmware/20261016/main-message-notify-frame/receipt.json"
    message_frame, message_frame_ref = receipt(message_frame_path)
    if message_frame["status"] != "PASS_EXPERIMENTAL_MAIN_MESSAGE_NOTIFY_FRAME_C" or \
            message_frame["base_sha256"] != main_obj["sha256"] or \
            message_frame["unresolved_before"] != 169 or message_frame["unresolved_after"] != 175 or \
            message_frame["imports_resolved"] != ["audio_message_notify_frame_process_4d6ba8"] or \
            len(message_frame["imports_added"]) != 7:
        raise RuntimeError("Apollo Main MessageNotify frame binding changed")
    main_obj = file_checked(message_frame["linked_object"], message_frame["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 175 or "audio_message_notify_frame_process_4d6ba8" in actual or \
            not set(message_frame["imports_added"]).issubset(actual):
        raise RuntimeError("Apollo Main MessageNotify frame frontier changed")
    whitelist_check_path = G2 / "build/c-firmware/20261016/main-message-notify-whitelist-check/receipt.json"
    whitelist_check, whitelist_check_ref = receipt(whitelist_check_path)
    if whitelist_check["status"] != "PASS_EXPERIMENTAL_MAIN_MESSAGE_NOTIFY_WHITELIST_CHECK_C" or \
            whitelist_check["base_sha256"] != main_obj["sha256"] or \
            whitelist_check["unresolved_before"] != 175 or whitelist_check["unresolved_after"] != 174 or \
            whitelist_check["imports_resolved"] != ["audio_message_notify_rx_whitelist_check_4d7624"] or \
            whitelist_check["imports_added"]:
        raise RuntimeError("Apollo Main MessageNotify whitelist-check binding changed")
    main_obj = file_checked(whitelist_check["linked_object"], whitelist_check["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 174 or "audio_message_notify_rx_whitelist_check_4d7624" in actual:
        raise RuntimeError("Apollo Main MessageNotify whitelist-check frontier changed")
    whitelist_ctrl_path = G2 / "build/c-firmware/20261016/main-message-notify-whitelist-ctrl/receipt.json"
    whitelist_ctrl, whitelist_ctrl_ref = receipt(whitelist_ctrl_path)
    if whitelist_ctrl["status"] != "PASS_EXPERIMENTAL_MAIN_MESSAGE_NOTIFY_WHITELIST_CTRL_C" or \
            whitelist_ctrl["base_sha256"] != main_obj["sha256"] or \
            whitelist_ctrl["unresolved_before"] != 174 or whitelist_ctrl["unresolved_after"] != 173 or \
            whitelist_ctrl["imports_resolved"] != ["audio_message_notify_rx_whitelist_ctrl_4d73d6"] or \
            whitelist_ctrl["imports_added"]:
        raise RuntimeError("Apollo Main MessageNotify whitelist-control binding changed")
    main_obj = file_checked(whitelist_ctrl["linked_object"], whitelist_ctrl["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 173 or "audio_message_notify_rx_whitelist_ctrl_4d73d6" in actual:
        raise RuntimeError("Apollo Main MessageNotify whitelist-control frontier changed")
    notify_ctrl_path = G2 / "build/c-firmware/20261016/main-message-notify-ctrl/receipt.json"
    notify_ctrl, notify_ctrl_ref = receipt(notify_ctrl_path)
    if notify_ctrl["status"] != "PASS_EXPERIMENTAL_MAIN_MESSAGE_NOTIFY_CTRL_C" or \
            notify_ctrl["base_sha256"] != main_obj["sha256"] or \
            notify_ctrl["unresolved_before"] != 173 or notify_ctrl["unresolved_after"] != 172 or \
            notify_ctrl["imports_resolved"] != ["audio_message_notify_rx_ctrl_4d6db0"] or \
            notify_ctrl["imports_added"]:
        raise RuntimeError("Apollo Main MessageNotify notification-control binding changed")
    main_obj = file_checked(notify_ctrl["linked_object"], notify_ctrl["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 172 or "audio_message_notify_rx_ctrl_4d6db0" in actual:
        raise RuntimeError("Apollo Main MessageNotify notification-control frontier changed")
    notify_tx_common_path = G2 / "build/c-firmware/20261016/main-message-notify-tx-common/receipt.json"
    notify_tx_common, notify_tx_common_ref = receipt(notify_tx_common_path)
    if notify_tx_common["status"] != "PASS_EXPERIMENTAL_MAIN_MESSAGE_NOTIFY_TX_COMMON_C" or \
            notify_tx_common["base_sha256"] != main_obj["sha256"] or \
            notify_tx_common["unresolved_before"] != 172 or notify_tx_common["unresolved_after"] != 171 or \
            notify_tx_common["imports_resolved"] != ["audio_message_notify_tx_common_response_4d7038"] or \
            notify_tx_common["imports_added"]:
        raise RuntimeError("Apollo Main MessageNotify common response binding changed")
    main_obj = file_checked(notify_tx_common["linked_object"], notify_tx_common["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 171 or "audio_message_notify_tx_common_response_4d7038" in actual:
        raise RuntimeError("Apollo Main MessageNotify common response frontier changed")
    notify_tx_ctrl_path = G2 / "build/c-firmware/20261016/main-message-notify-tx-ctrl/receipt.json"
    notify_tx_ctrl, notify_tx_ctrl_ref = receipt(notify_tx_ctrl_path)
    if notify_tx_ctrl["status"] != "PASS_EXPERIMENTAL_MAIN_MESSAGE_NOTIFY_TX_CTRL_C" or \
            notify_tx_ctrl["base_sha256"] != main_obj["sha256"] or \
            notify_tx_ctrl["unresolved_before"] != 171 or notify_tx_ctrl["unresolved_after"] != 170 or \
            notify_tx_ctrl["imports_resolved"] != ["audio_message_notify_tx_ctrl_4d6ea2"] or \
            notify_tx_ctrl["imports_added"]:
        raise RuntimeError("Apollo Main MessageNotify control response binding changed")
    main_obj = file_checked(notify_tx_ctrl["linked_object"], notify_tx_ctrl["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 170 or "audio_message_notify_tx_ctrl_4d6ea2" in actual:
        raise RuntimeError("Apollo Main MessageNotify control response frontier changed")
    notify_tx_whitelist_path = G2 / "build/c-firmware/20261016/main-message-notify-tx-whitelist-ctrl/receipt.json"
    notify_tx_whitelist, notify_tx_whitelist_ref = receipt(notify_tx_whitelist_path)
    if notify_tx_whitelist["status"] != "PASS_EXPERIMENTAL_MAIN_MESSAGE_NOTIFY_TX_WHITELIST_CTRL_C" or \
            notify_tx_whitelist["base_sha256"] != main_obj["sha256"] or \
            notify_tx_whitelist["unresolved_before"] != 170 or notify_tx_whitelist["unresolved_after"] != 169 or \
            notify_tx_whitelist["imports_resolved"] != ["audio_message_notify_tx_whitelist_ctrl_4d749a"] or \
            notify_tx_whitelist["imports_added"]:
        raise RuntimeError("Apollo Main MessageNotify whitelist-control response binding changed")
    main_obj = file_checked(notify_tx_whitelist["linked_object"], notify_tx_whitelist["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 169 or "audio_message_notify_tx_whitelist_ctrl_4d749a" in actual:
        raise RuntimeError("Apollo Main MessageNotify whitelist-control response frontier changed")
    notify_tx_check_path = G2 / "build/c-firmware/20261016/main-message-notify-tx-whitelist-check/receipt.json"
    notify_tx_check, notify_tx_check_ref = receipt(notify_tx_check_path)
    if notify_tx_check["status"] != "PASS_EXPERIMENTAL_MAIN_MESSAGE_NOTIFY_TX_WHITELIST_CHECK_C" or \
            notify_tx_check["base_sha256"] != main_obj["sha256"] or \
            notify_tx_check["unresolved_before"] != 169 or notify_tx_check["unresolved_after"] != 168 or \
            notify_tx_check["imports_resolved"] != ["audio_message_notify_tx_whitelist_check_4d76cc"] or \
            notify_tx_check["imports_added"]:
        raise RuntimeError("Apollo Main MessageNotify whitelist-check response binding changed")
    main_obj = file_checked(notify_tx_check["linked_object"], notify_tx_check["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 168 or any(name.startswith("audio_message_notify_") for name in actual):
        raise RuntimeError("Apollo Main MessageNotify encoder frontier changed")
    ready_word_path = G2 / "build/c-firmware/20261016/main-tracepoint-ready-word/receipt.json"
    ready_word, ready_word_ref = receipt(ready_word_path)
    if ready_word["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_READY_WORD_EXTENT_C" or \
            ready_word["base_sha256"] != main_obj["sha256"] or \
            ready_word["unresolved_before"] != 168 or ready_word["unresolved_after"] != 168 or \
            ready_word["section_bytes"] != 4 or ready_word["imports_resolved"] or \
            ready_word["imports_added"]:
        raise RuntimeError("Apollo Main tracepoint ready-word extent binding changed")
    main_obj = file_checked(ready_word["linked_object"], ready_word["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 168:
        raise RuntimeError("Apollo Main tracepoint ready-word frontier changed")
    slave_file_list_path = G2 / "build/c-firmware/20261016/main-tracepoint-slave-file-list/receipt.json"
    slave_file_list, slave_file_list_ref = receipt(slave_file_list_path)
    if slave_file_list["status"] != "PASS_EXPERIMENTAL_MAIN_TRACEPOINT_SLAVE_FILE_LIST_C" or \
            slave_file_list["base_sha256"] != main_obj["sha256"] or \
            slave_file_list["unresolved_before"] != 168 or \
            slave_file_list["unresolved_after"] != 167 or \
            slave_file_list["imports_resolved"] != ["audio_tracepoint_handle_slave_file_list_5eeb98"] or \
            slave_file_list["imports_added"]:
        raise RuntimeError("Apollo Main tracepoint slave file-list binding changed")
    main_obj = file_checked(slave_file_list["linked_object"], slave_file_list["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 167 or "audio_tracepoint_handle_slave_file_list_5eeb98" in actual:
        raise RuntimeError("Apollo Main tracepoint slave file-list frontier changed")
    fault_lookup_path = G2 / "build/c-firmware/20261016/main-fault-lookup-overrun/receipt.json"
    fault_lookup, fault_lookup_ref = receipt(fault_lookup_path)
    if fault_lookup["status"] != "PASS_EXPERIMENTAL_MAIN_FAULT_LOOKUP_OVERRUN_C" or \
            fault_lookup["base_sha256"] != main_obj["sha256"] or \
            fault_lookup["unresolved_before"] != 167 or \
            fault_lookup["unresolved_after"] != 166 or \
            fault_lookup["imports_resolved"] != ["audio_fault_unmapped_code_message_509b48"] or \
            fault_lookup["imports_added"]:
        raise RuntimeError("Apollo Main fault lookup binding changed")
    main_obj = file_checked(fault_lookup["linked_object"], fault_lookup["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 166 or "audio_fault_unmapped_code_message_509b48" in actual:
        raise RuntimeError("Apollo Main fault lookup frontier changed")
    terminal_names_path = G2 / "build/c-firmware/20261016/main-terminal-event-names-ram/receipt.json"
    terminal_names, terminal_names_ref = receipt(terminal_names_path)
    if terminal_names["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_EVENT_NAMES_RAM_C" or \
            terminal_names["base_sha256"] != main_obj["sha256"] or \
            terminal_names["unresolved_before"] != 166 or \
            terminal_names["unresolved_after"] != 165 or \
            terminal_names["section_bytes"] != 52 or \
            terminal_names["placement_address"] != "0x20003e6c" or \
            terminal_names["imports_resolved"] != ["audio_terminal_event_names"] or \
            terminal_names["imports_added"]:
        raise RuntimeError("Apollo Main terminal event-name RAM binding changed")
    main_obj = file_checked(terminal_names["linked_object"], terminal_names["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 165 or "audio_terminal_event_names" in actual:
        raise RuntimeError("Apollo Main terminal event-name frontier changed")
    terminal_ui_path = G2 / "build/c-firmware/20261016/main-terminal-ui-event-5e44f6/receipt.json"
    terminal_ui, terminal_ui_ref = receipt(terminal_ui_path)
    terminal_children = {"audio_terminal_ui_status_5e7b74", "audio_terminal_ui_tick_5e8008",
                         "audio_terminal_ui_stop_5e720c", "audio_terminal_ui_start_5e716c",
                         "audio_terminal_ui_exit_sync_5e42ec"}
    if terminal_ui["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_EVENT_C" or \
            terminal_ui["base_sha256"] != main_obj["sha256"] or \
            terminal_ui["unresolved_before"] != 165 or terminal_ui["unresolved_after"] != 169 or \
            terminal_ui["imports_resolved"] != ["audio_uart_registry_callback_5e44f6"] or \
            set(terminal_ui["imports_added"]) != terminal_children:
        raise RuntimeError("Apollo Main terminal UI callback binding changed")
    main_obj = file_checked(terminal_ui["linked_object"], terminal_ui["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 169 or "audio_uart_registry_callback_5e44f6" in actual:
        raise RuntimeError("Apollo Main terminal UI callback frontier changed")
    terminal_exit_path = G2 / "build/c-firmware/20261016/main-terminal-ui-exit-sync-5e42ec/receipt.json"
    terminal_exit, terminal_exit_ref = receipt(terminal_exit_path)
    if terminal_exit["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_EXIT_SYNC_C" or \
            terminal_exit["base_sha256"] != main_obj["sha256"] or \
            terminal_exit["unresolved_before"] != 169 or terminal_exit["unresolved_after"] != 168 or \
            terminal_exit["imports_resolved"] != ["audio_terminal_ui_exit_sync_5e42ec"] or \
            terminal_exit["imports_added"]:
        raise RuntimeError("Apollo Main terminal exit-sync binding changed")
    main_obj = file_checked(terminal_exit["linked_object"], terminal_exit["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 168 or "audio_terminal_ui_exit_sync_5e42ec" in actual:
        raise RuntimeError("Apollo Main terminal exit-sync frontier changed")
    terminal_stop_path = G2 / "build/c-firmware/20261016/main-terminal-ui-stop-5e720c/receipt.json"
    terminal_stop, terminal_stop_ref = receipt(terminal_stop_path)
    terminal_stop_children = {"audio_terminal_ui_stop_voice_5896b4",
                              "audio_terminal_ui_stop_timer_5e7ec4",
                              "audio_terminal_ui_stop_service_a_5eceb2",
                              "audio_terminal_ui_stop_service_b_5ec268",
                              "audio_terminal_ui_stop_service_c_5ebbc6",
                              "audio_terminal_ui_stop_service_d_5ec770",
                              "audio_terminal_ui_stop_service_e_5ec9c0",
                              "audio_terminal_ui_state_base"}
    if terminal_stop["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_STOP_C" or \
            terminal_stop["base_sha256"] != main_obj["sha256"] or \
            terminal_stop["unresolved_before"] != 168 or terminal_stop["unresolved_after"] != 175 or \
            terminal_stop["imports_resolved"] != ["audio_terminal_ui_stop_5e720c"] or \
            set(terminal_stop["imports_added"]) != terminal_stop_children:
        raise RuntimeError("Apollo Main terminal stop binding changed")
    main_obj = file_checked(terminal_stop["linked_object"], terminal_stop["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 175 or "audio_terminal_ui_stop_5e720c" in actual:
        raise RuntimeError("Apollo Main terminal stop frontier changed")
    terminal_stop_e_path = G2 / "build/c-firmware/20261016/main-terminal-ui-stop-e-5ec9c0/receipt.json"
    terminal_stop_e, terminal_stop_e_ref = receipt(terminal_stop_e_path)
    if terminal_stop_e["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_STOP_E_C" or \
            terminal_stop_e["base_sha256"] != main_obj["sha256"] or \
            terminal_stop_e["unresolved_before"] != 175 or \
            terminal_stop_e["unresolved_after"] != 174 or \
            terminal_stop_e["imports_resolved"] != ["audio_terminal_ui_stop_service_e_5ec9c0"] or \
            terminal_stop_e["imports_added"]:
        raise RuntimeError("Apollo Main terminal result cleanup binding changed")
    main_obj = file_checked(terminal_stop_e["linked_object"], terminal_stop_e["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 174 or "audio_terminal_ui_stop_service_e_5ec9c0" in actual:
        raise RuntimeError("Apollo Main terminal result cleanup frontier changed")
    terminal_stop_a_path = G2 / "build/c-firmware/20261016/main-terminal-ui-stop-a-5eceb2/receipt.json"
    terminal_stop_a, terminal_stop_a_ref = receipt(terminal_stop_a_path)
    if terminal_stop_a["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_STOP_A_C" or \
            terminal_stop_a["base_sha256"] != main_obj["sha256"] or \
            terminal_stop_a["unresolved_before"] != 174 or \
            terminal_stop_a["unresolved_after"] != 174 or \
            terminal_stop_a["imports_resolved"] != ["audio_terminal_ui_stop_service_a_5eceb2"] or \
            terminal_stop_a["imports_added"] != ["audio_terminal_ui_object_valid_43e2ea"]:
        raise RuntimeError("Apollo Main terminal timer cleanup binding changed")
    main_obj = file_checked(terminal_stop_a["linked_object"], terminal_stop_a["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 174 or "audio_terminal_ui_stop_service_a_5eceb2" in actual:
        raise RuntimeError("Apollo Main terminal timer cleanup frontier changed")
    object_valid_path = G2 / "build/c-firmware/20261016/main-terminal-ui-object-valid-43e2ea/receipt.json"
    object_valid, object_valid_ref = receipt(object_valid_path)
    if object_valid["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_OBJECT_VALID_C" or \
            object_valid["base_sha256"] != main_obj["sha256"] or \
            object_valid["unresolved_before"] != 174 or \
            object_valid["unresolved_after"] != 174 or \
            object_valid["imports_resolved"] != ["audio_terminal_ui_object_valid_43e2ea"] or \
            object_valid["imports_added"] != ["audio_terminal_ui_object_descendant_43ee54"]:
        raise RuntimeError("Apollo Main terminal object membership binding changed")
    main_obj = file_checked(object_valid["linked_object"], object_valid["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 174 or "audio_terminal_ui_object_valid_43e2ea" in actual:
        raise RuntimeError("Apollo Main terminal object membership frontier changed")
    descendant_path = G2 / "build/c-firmware/20261016/main-terminal-ui-object-descendant-43ee54/receipt.json"
    descendant, descendant_ref = receipt(descendant_path)
    if descendant["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_OBJECT_DESCENDANT_C" or \
            descendant["base_sha256"] != main_obj["sha256"] or \
            descendant["unresolved_before"] != 174 or descendant["unresolved_after"] != 173 or \
            descendant["imports_resolved"] != ["audio_terminal_ui_object_descendant_43ee54"] or \
            descendant["imports_added"]:
        raise RuntimeError("Apollo Main terminal descendant binding changed")
    main_obj = file_checked(descendant["linked_object"], descendant["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 173 or "audio_terminal_ui_object_descendant_43ee54" in actual:
        raise RuntimeError("Apollo Main terminal descendant frontier changed")
    list_anim_path = G2 / "build/c-firmware/20261016/main-terminal-list-anim-stop-5896b4/receipt.json"
    list_anim, list_anim_ref = receipt(list_anim_path)
    if list_anim["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_LIST_ANIM_STOP_C" or \
            list_anim["base_sha256"] != main_obj["sha256"] or \
            list_anim["unresolved_before"] != 173 or list_anim["unresolved_after"] != 172 or \
            list_anim["imports_resolved"] != ["audio_terminal_ui_stop_voice_5896b4"] or \
            list_anim["imports_added"] or list_anim["ram_base"] != "0x20070ea8" or \
            list_anim["ram_extent"] != "0xd0":
        raise RuntimeError("Apollo Main list animation stop binding changed")
    main_obj = file_checked(list_anim["linked_object"], list_anim["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 172 or "audio_terminal_ui_stop_voice_5896b4" in actual:
        raise RuntimeError("Apollo Main list animation stop frontier changed")
    timer_path = G2 / "build/c-firmware/20261016/main-terminal-ui-stop-timer-5e7ec4/receipt.json"
    timer, timer_ref = receipt(timer_path)
    if timer["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_STOP_TIMER_C" or \
            timer["base_sha256"] != main_obj["sha256"] or \
            timer["unresolved_before"] != 172 or timer["unresolved_after"] != 171 or \
            timer["imports_resolved"] != ["audio_terminal_ui_stop_timer_5e7ec4"] or \
            timer["imports_added"] or timer["ram_base"] != "0x20073c38" or \
            timer["ram_extent"] != "0x18":
        raise RuntimeError("Apollo Main terminal timer stop binding changed")
    main_obj = file_checked(timer["linked_object"], timer["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 171 or "audio_terminal_ui_stop_timer_5e7ec4" in actual:
        raise RuntimeError("Apollo Main terminal timer stop frontier changed")
    services_bcd_path = G2 / "build/c-firmware/20261016/main-terminal-ui-stop-services-bcd/receipt.json"
    services_bcd, services_bcd_ref = receipt(services_bcd_path)
    if services_bcd["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_STOP_SERVICES_BCD_C" or \
            services_bcd["base_sha256"] != main_obj["sha256"] or \
            services_bcd["unresolved_before"] != 171 or services_bcd["unresolved_after"] != 169 or \
            set(services_bcd["imports_resolved"]) != {
                "audio_terminal_ui_stop_service_b_5ec268",
                "audio_terminal_ui_stop_service_c_5ebbc6",
                "audio_terminal_ui_stop_service_d_5ec770"} or \
            services_bcd["imports_added"] != ["audio_terminal_ui_event_5e5484"]:
        raise RuntimeError("Apollo Main terminal cleanup children binding changed")
    main_obj = file_checked(services_bcd["linked_object"], services_bcd["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 169 or "audio_terminal_ui_event_5e5484" not in actual:
        raise RuntimeError("Apollo Main terminal cleanup children frontier changed")
    display_notify_path = G2 / "build/c-firmware/20261016/main-terminal-display-state-notify/receipt.json"
    display_notify, display_notify_ref = receipt(display_notify_path)
    if display_notify["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_DISPLAY_STATE_NOTIFY_C" or \
            display_notify["base_sha256"] != main_obj["sha256"] or \
            display_notify["unresolved_before"] != 169 or display_notify["unresolved_after"] != 168 or \
            display_notify["imports_resolved"] != ["audio_terminal_ui_event_5e5484"] or \
            display_notify["imports_added"]:
        raise RuntimeError("Apollo Main Terminal display-state notify binding changed")
    main_obj = file_checked(display_notify["linked_object"], display_notify["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 168 or "audio_terminal_ui_event_5e5484" in actual:
        raise RuntimeError("Apollo Main Terminal display-state notify frontier changed")
    terminal_start_path = G2 / "build/c-firmware/20261016/main-terminal-ui-start-5e716c/receipt.json"
    terminal_start, terminal_start_ref = receipt(terminal_start_path)
    if terminal_start["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_START_C" or \
            terminal_start["base_sha256"] != main_obj["sha256"] or \
            terminal_start["unresolved_before"] != 168 or terminal_start["unresolved_after"] != 169 or \
            terminal_start["imports_resolved"] != ["audio_terminal_ui_start_5e716c"] or \
            set(terminal_start["imports_added"]) != {
                "audio_terminal_ui_theme_5e47cc", "audio_terminal_list_anim_init_58966c"}:
        raise RuntimeError("Apollo Main Terminal UI start binding changed")
    main_obj = file_checked(terminal_start["linked_object"], terminal_start["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 169 or "audio_terminal_ui_start_5e716c" in actual:
        raise RuntimeError("Apollo Main Terminal UI start frontier changed")
    list_anim_init_path = G2 / "build/c-firmware/20261016/main-terminal-list-anim-init-58966c/receipt.json"
    list_anim_init, list_anim_init_ref = receipt(list_anim_init_path)
    if list_anim_init["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_LIST_ANIM_INIT_C" or \
            list_anim_init["base_sha256"] != main_obj["sha256"] or \
            list_anim_init["unresolved_before"] != 169 or list_anim_init["unresolved_after"] != 168 or \
            list_anim_init["imports_resolved"] != ["audio_terminal_list_anim_init_58966c"] or \
            list_anim_init["imports_added"]:
        raise RuntimeError("Apollo Main list animation init binding changed")
    main_obj = file_checked(list_anim_init["linked_object"], list_anim_init["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 168 or "audio_terminal_list_anim_init_58966c" in actual:
        raise RuntimeError("Apollo Main list animation init frontier changed")
    theme_path = G2 / "build/c-firmware/20261016/main-terminal-ui-theme-5e47cc/receipt.json"
    theme, theme_ref = receipt(theme_path)
    if theme["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_THEME_C" or \
            theme["base_sha256"] != main_obj["sha256"] or \
            theme["unresolved_before"] != 168 or theme["unresolved_after"] != 167 or \
            theme["imports_resolved"] != ["audio_terminal_ui_theme_5e47cc"] or theme["imports_added"]:
        raise RuntimeError("Apollo Main Terminal theme binding changed")
    main_obj = file_checked(theme["linked_object"], theme["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 167 or "audio_terminal_ui_theme_5e47cc" in actual:
        raise RuntimeError("Apollo Main Terminal theme frontier changed")
    terminal_tick_path = G2 / "build/c-firmware/20261016/main-terminal-ui-tick-5e8008/receipt.json"
    terminal_tick, terminal_tick_ref = receipt(terminal_tick_path)
    if terminal_tick["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_TICK_C" or \
            terminal_tick["base_sha256"] != main_obj["sha256"] or \
            terminal_tick["unresolved_before"] != 167 or terminal_tick["unresolved_after"] != 166 or \
            terminal_tick["imports_resolved"] != ["audio_terminal_ui_tick_5e8008"] or \
            terminal_tick["imports_added"] or len(terminal_tick["sources"]) != 4:
        raise RuntimeError("Apollo Main Terminal tick binding changed")
    main_obj = file_checked(terminal_tick["linked_object"], terminal_tick["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 166 or "audio_terminal_ui_tick_5e8008" in actual:
        raise RuntimeError("Apollo Main Terminal tick frontier changed")
    terminal_fsm_path = G2 / "build/c-firmware/20261016/main-terminal-ui-status-5e7b74/receipt.json"
    terminal_fsm, terminal_fsm_ref = receipt(terminal_fsm_path)
    fsm_added = set(terminal_fsm["imports_added"])
    if terminal_fsm["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_STATUS_C" or \
            terminal_fsm["base_sha256"] != main_obj["sha256"] or \
            terminal_fsm["unresolved_before"] != 166 or terminal_fsm["unresolved_after"] != 217 or \
            terminal_fsm["imports_resolved"] != ["audio_terminal_ui_status_5e7b74"] or \
            len({name for name in fsm_added if name.startswith("audio_terminal_ui_action_")}) != 50 or \
            terminal_fsm["table_base"] != "0x650430" or terminal_fsm["table_extent"] != "0x1040":
        raise RuntimeError("Apollo Main Terminal FSM binding changed")
    main_obj = file_checked(terminal_fsm["linked_object"], terminal_fsm["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 217 or "audio_terminal_ui_status_5e7b74" in actual or \
            not fsm_added <= set(actual):
        raise RuntimeError("Apollo Main Terminal FSM frontier changed")
    fsm_names_path = G2 / "build/c-firmware/20261016/main-terminal-ui-fsm-names-5e7b10/receipt.json"
    fsm_names, fsm_names_ref = receipt(fsm_names_path)
    if fsm_names["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_FSM_NAMES_C" or \
            fsm_names["base_sha256"] != main_obj["sha256"] or \
            fsm_names["unresolved_before"] != 217 or fsm_names["unresolved_after"] != 215 or \
            set(fsm_names["imports_resolved"]) != {
                "audio_terminal_ui_state_name_5e7b10", "audio_terminal_ui_event_name_5e7b2a"} or \
            fsm_names["imports_added"] or fsm_names["state_names_ram"] != "0x20003ea4" or \
            fsm_names["event_names_ram"] != "0x20003edc":
        raise RuntimeError("Apollo Main Terminal FSM name binding changed")
    main_obj = file_checked(fsm_names["linked_object"], fsm_names["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 215 or "audio_terminal_ui_state_name_5e7b10" in actual or \
            "audio_terminal_ui_event_name_5e7b2a" in actual:
        raise RuntimeError("Apollo Main Terminal FSM name frontier changed")
    asr_actions_path = G2 / "build/c-firmware/20261016/main-terminal-ui-action-asr-start-5e5a7e/receipt.json"
    asr_actions, asr_actions_ref = receipt(asr_actions_path)
    if asr_actions["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_ACTION_ASR_START_C" or \
            asr_actions["base_sha256"] != main_obj["sha256"] or \
            asr_actions["unresolved_before"] != 215 or asr_actions["unresolved_after"] != 214 or \
            set(asr_actions["imports_resolved"]) != {
                "audio_terminal_ui_action_5e5a7e", "audio_terminal_ui_action_5e5a94"} or \
            asr_actions["imports_added"] != ["audio_terminal_ui_notification_restore_5ebfae"]:
        raise RuntimeError("Apollo Main Terminal ASR actions binding changed")
    main_obj = file_checked(asr_actions["linked_object"], asr_actions["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 214 or "audio_terminal_ui_notification_restore_5ebfae" not in actual:
        raise RuntimeError("Apollo Main Terminal ASR actions frontier changed")
    notification_restore_path = G2 / "build/c-firmware/20261016/main-terminal-ui-notification-restore-5ebfae/receipt.json"
    notification_restore, notification_restore_ref = receipt(notification_restore_path)
    if notification_restore["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_NOTIFICATION_RESTORE_C" or \
            notification_restore["base_sha256"] != main_obj["sha256"] or \
            notification_restore["unresolved_before"] != 214 or \
            notification_restore["unresolved_after"] != 213 or \
            notification_restore["imports_resolved"] != ["audio_terminal_ui_notification_restore_5ebfae"] or \
            notification_restore["imports_added"] or len(notification_restore["sources"]) != 2:
        raise RuntimeError("Apollo Main Terminal notification restore binding changed")
    main_obj = file_checked(notification_restore["linked_object"], notification_restore["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 213 or "audio_terminal_ui_notification_restore_5ebfae" in actual:
        raise RuntimeError("Apollo Main Terminal notification restore frontier changed")
    exit_actions_path = G2 / "build/c-firmware/20261016/main-terminal-ui-action-notification-exit-5e5442/receipt.json"
    exit_actions, exit_actions_ref = receipt(exit_actions_path)
    if exit_actions["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_ACTION_NOTIFICATION_EXIT_C" or \
            exit_actions["base_sha256"] != main_obj["sha256"] or \
            exit_actions["unresolved_before"] != 213 or exit_actions["unresolved_after"] != 211 or \
            set(exit_actions["imports_resolved"]) != {
                "audio_terminal_ui_action_5e5442", "audio_terminal_ui_action_5ed748"} or \
            exit_actions["imports_added"] or len(exit_actions["sources"]) != 2:
        raise RuntimeError("Apollo Main Terminal notification exit actions binding changed")
    main_obj = file_checked(exit_actions["linked_object"], exit_actions["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 211 or "audio_terminal_ui_action_5e5442" in actual or \
            "audio_terminal_ui_action_5ed748" in actual:
        raise RuntimeError("Apollo Main Terminal notification exit actions frontier changed")
    payload_actions_path = G2 / "build/c-firmware/20261016/main-terminal-ui-action-payload-5e6400/receipt.json"
    payload_actions, payload_actions_ref = receipt(payload_actions_path)
    if payload_actions["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_ACTION_PAYLOAD_C" or \
            payload_actions["base_sha256"] != main_obj["sha256"] or \
            payload_actions["unresolved_before"] != 211 or payload_actions["unresolved_after"] != 211 or \
            set(payload_actions["imports_resolved"]) != {
                "audio_terminal_ui_action_5e6400", "audio_terminal_ui_action_5e6410"} or \
            set(payload_actions["imports_added"]) != {
                "audio_terminal_control_flags_5e4a6e", "audio_terminal_elapsed_text_5e48b8"}:
        raise RuntimeError("Apollo Main Terminal payload actions binding changed")
    main_obj = file_checked(payload_actions["linked_object"], payload_actions["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 211 or any(name in actual for name in payload_actions["imports_resolved"]):
        raise RuntimeError("Apollo Main Terminal payload actions frontier changed")
    elapsed_text_path = G2 / "build/c-firmware/20261016/main-terminal-elapsed-text-5e48b8/receipt.json"
    elapsed_text, elapsed_text_ref = receipt(elapsed_text_path)
    if elapsed_text["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_ELAPSED_TEXT_C" or \
            elapsed_text["base_sha256"] != main_obj["sha256"] or \
            elapsed_text["unresolved_before"] != 211 or elapsed_text["unresolved_after"] != 212 or \
            elapsed_text["imports_resolved"] != ["audio_terminal_elapsed_text_5e48b8"] or \
            set(elapsed_text["imports_added"]) != {
                "audio_lv_label_set_text_fmt_49954c", "audio_lv_obj_invalidate_43dfa4"}:
        raise RuntimeError("Apollo Main Terminal elapsed-text binding changed")
    main_obj = file_checked(elapsed_text["linked_object"], elapsed_text["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 212 or "audio_terminal_elapsed_text_5e48b8" in actual:
        raise RuntimeError("Apollo Main Terminal elapsed-text frontier changed")
    control_flags_path = G2 / "build/c-firmware/20261016/main-terminal-control-flags-5e4a6e/receipt.json"
    control_flags, control_flags_ref = receipt(control_flags_path)
    if control_flags["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_CONTROL_FLAGS_C" or \
            control_flags["base_sha256"] != main_obj["sha256"] or \
            control_flags["unresolved_before"] != 212 or control_flags["unresolved_after"] != 213 or \
            control_flags["imports_resolved"] != ["audio_terminal_control_flags_5e4a6e"] or \
            set(control_flags["imports_added"]) != {
                "audio_terminal_output_start_5e4920", "audio_terminal_set_output_5e49b0"}:
        raise RuntimeError("Apollo Main Terminal control-flags binding changed")
    main_obj = file_checked(control_flags["linked_object"], control_flags["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 213 or "audio_terminal_control_flags_5e4a6e" in actual:
        raise RuntimeError("Apollo Main Terminal control-flags frontier changed")
    output_start_path = G2 / "build/c-firmware/20261016/main-terminal-output-start-5e4920/receipt.json"
    output_start, output_start_ref = receipt(output_start_path)
    if output_start["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_OUTPUT_START_C" or \
            output_start["base_sha256"] != main_obj["sha256"] or \
            output_start["unresolved_before"] != 213 or output_start["unresolved_after"] != 216 or \
            output_start["imports_resolved"] != ["audio_terminal_output_start_5e4920"] or \
            set(output_start["imports_added"]) != {
                "audio_terminal_processing_prepare_5ea30c", "audio_terminal_processing_hide_5e4878",
                "audio_lv_anim_start_49942e", "audio_terminal_elapsed_refresh_5e4902"}:
        raise RuntimeError("Apollo Main Terminal output-start binding changed")
    main_obj = file_checked(output_start["linked_object"], output_start["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 216 or "audio_terminal_output_start_5e4920" in actual:
        raise RuntimeError("Apollo Main Terminal output-start frontier changed")
    processing_hide_path = G2 / "build/c-firmware/20261016/main-terminal-processing-hide-5e4878/receipt.json"
    processing_hide, processing_hide_ref = receipt(processing_hide_path)
    if processing_hide["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_PROCESSING_HIDE_C" or \
            processing_hide["base_sha256"] != main_obj["sha256"] or \
            processing_hide["unresolved_before"] != 216 or processing_hide["unresolved_after"] != 217 or \
            processing_hide["imports_resolved"] != ["audio_terminal_processing_hide_5e4878"] or \
            set(processing_hide["imports_added"]) != {
                "audio_lv_object_call_450500", "audio_lv_object_call_441488"}:
        raise RuntimeError("Apollo Main Terminal processing wrapper binding changed")
    main_obj = file_checked(processing_hide["linked_object"], processing_hide["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 217 or "audio_terminal_processing_hide_5e4878" in actual:
        raise RuntimeError("Apollo Main Terminal processing wrapper frontier changed")
    processing_prepare_path = G2 / "build/c-firmware/20261016/main-terminal-processing-prepare-5ea30c/receipt.json"
    processing_prepare, processing_prepare_ref = receipt(processing_prepare_path)
    if processing_prepare["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_PROCESSING_PREPARE_C" or \
            processing_prepare["base_sha256"] != main_obj["sha256"] or \
            processing_prepare["unresolved_before"] != 217 or processing_prepare["unresolved_after"] != 217 or \
            processing_prepare["imports_resolved"] != ["audio_terminal_processing_prepare_5ea30c"] or \
            processing_prepare["imports_added"] != ["audio_lv_object_release_44d7b8"]:
        raise RuntimeError("Apollo Main Terminal processing clear binding changed")
    main_obj = file_checked(processing_prepare["linked_object"], processing_prepare["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 217 or "audio_terminal_processing_prepare_5ea30c" in actual:
        raise RuntimeError("Apollo Main Terminal processing clear frontier changed")
    elapsed_refresh_path = G2 / "build/c-firmware/20261016/main-terminal-elapsed-refresh-5e4902/receipt.json"
    elapsed_refresh, elapsed_refresh_ref = receipt(elapsed_refresh_path)
    if elapsed_refresh["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_ELAPSED_REFRESH_C" or \
            elapsed_refresh["base_sha256"] != main_obj["sha256"] or \
            elapsed_refresh["unresolved_before"] != 217 or elapsed_refresh["unresolved_after"] != 217 or \
            elapsed_refresh["imports_resolved"] != ["audio_terminal_elapsed_refresh_5e4902"] or \
            elapsed_refresh["imports_added"] != ["audio_terminal_elapsed_clear_5e4894"]:
        raise RuntimeError("Apollo Main Terminal elapsed-refresh binding changed")
    main_obj = file_checked(elapsed_refresh["linked_object"], elapsed_refresh["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 217 or "audio_terminal_elapsed_refresh_5e4902" in actual:
        raise RuntimeError("Apollo Main Terminal elapsed-refresh frontier changed")
    elapsed_clear_path = G2 / "build/c-firmware/20261016/main-terminal-elapsed-clear-5e4894/receipt.json"
    elapsed_clear, elapsed_clear_ref = receipt(elapsed_clear_path)
    if elapsed_clear["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_ELAPSED_CLEAR_C" or \
            elapsed_clear["base_sha256"] != main_obj["sha256"] or \
            elapsed_clear["unresolved_before"] != 217 or elapsed_clear["unresolved_after"] != 217 or \
            elapsed_clear["imports_resolved"] != ["audio_terminal_elapsed_clear_5e4894"] or \
            elapsed_clear["imports_added"] != ["audio_lv_object_call_43ded4"]:
        raise RuntimeError("Apollo Main Terminal elapsed-clear binding changed")
    main_obj = file_checked(elapsed_clear["linked_object"], elapsed_clear["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 217 or "audio_terminal_elapsed_clear_5e4894" in actual:
        raise RuntimeError("Apollo Main Terminal elapsed-clear frontier changed")
    set_output_path = G2 / "build/c-firmware/20261016/main-terminal-set-output-5e49b0/receipt.json"
    set_output, set_output_ref = receipt(set_output_path)
    if set_output["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_SET_OUTPUT_C" or \
            set_output["base_sha256"] != main_obj["sha256"] or \
            set_output["unresolved_before"] != 217 or set_output["unresolved_after"] != 222 or \
            set_output["imports_resolved"] != ["audio_terminal_set_output_5e49b0"] or \
            set(set_output["imports_added"]) != {
                "audio_terminal_output_style_20003f80", "audio_terminal_output_payload_20074a94",
                "audio_terminal_output_mode_2007502d", "audio_terminal_output_active_2007502c",
                "audio_terminal_set_label_style_5e482a", "audio_terminal_select_output_mode_5ea2a8"}:
        raise RuntimeError("Apollo Main Terminal set-output binding changed")
    main_obj = file_checked(set_output["linked_object"], set_output["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 222 or "audio_terminal_set_output_5e49b0" in actual:
        raise RuntimeError("Apollo Main Terminal set-output frontier changed")
    output_ram_path = G2 / "build/c-firmware/20261016/main-terminal-output-ram-cells/receipt.json"
    output_ram, output_ram_ref = receipt(output_ram_path)
    if output_ram["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_OUTPUT_RAM_CELLS" or \
            output_ram["base_sha256"] != main_obj["sha256"] or \
            output_ram["unresolved_before"] != 222 or output_ram["unresolved_after"] != 219 or \
            set(output_ram["imports_resolved"]) != {
                "audio_terminal_output_payload_20074a94", "audio_terminal_output_active_2007502c",
                "audio_terminal_output_mode_2007502d"} or output_ram["imports_added"]:
        raise RuntimeError("Apollo Main Terminal output RAM binding changed")
    main_obj = file_checked(output_ram["linked_object"], output_ram["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 219 or any(name in actual for name in output_ram["imports_resolved"]):
        raise RuntimeError("Apollo Main Terminal output RAM frontier changed")
    label_style_path = G2 / "build/c-firmware/20261016/main-terminal-set-label-style-5e482a/receipt.json"
    label_style, label_style_ref = receipt(label_style_path)
    if label_style["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_SET_LABEL_STYLE_C" or \
            label_style["base_sha256"] != main_obj["sha256"] or \
            label_style["unresolved_before"] != 219 or label_style["unresolved_after"] != 222 or \
            label_style["imports_resolved"] != ["audio_terminal_set_label_style_5e482a"] or \
            set(label_style["imports_added"]) != {
                "audio_lv_label_style_call_597ea6", "audio_lv_label_style_call_597f10",
                "audio_lv_label_style_call_597f52", "audio_lv_label_style_call_597ee0"}:
        raise RuntimeError("Apollo Main Terminal label style binding changed")
    main_obj = file_checked(label_style["linked_object"], label_style["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 222 or "audio_terminal_set_label_style_5e482a" in actual:
        raise RuntimeError("Apollo Main Terminal label style frontier changed")
    output_mode_path = G2 / "build/c-firmware/20261016/main-terminal-select-output-mode-5ea2a8/receipt.json"
    output_mode, output_mode_ref = receipt(output_mode_path)
    if output_mode["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_SELECT_OUTPUT_MODE_C" or \
            output_mode["base_sha256"] != main_obj["sha256"] or \
            output_mode["unresolved_before"] != 222 or output_mode["unresolved_after"] != 221 or \
            output_mode["imports_resolved"] != ["audio_terminal_select_output_mode_5ea2a8"] or \
            output_mode["imports_added"] or set(output_mode["additional_providers"]) != {
                "audio_terminal_select_output_mode_core_5ea270", "audio_terminal_output_hash_5ea256"}:
        raise RuntimeError("Apollo Main Terminal output-mode binding changed")
    main_obj = file_checked(output_mode["linked_object"], output_mode["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 221 or "audio_terminal_select_output_mode_5ea2a8" in actual:
        raise RuntimeError("Apollo Main Terminal output-mode frontier changed")
    dismiss_action_path = G2 / "build/c-firmware/20261016/main-terminal-ui-action-dismiss-query-5e68b4/receipt.json"
    dismiss_action, dismiss_action_ref = receipt(dismiss_action_path)
    if dismiss_action["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_ACTION_DISMISS_QUERY_C" or \
            dismiss_action["base_sha256"] != main_obj["sha256"] or \
            dismiss_action["unresolved_before"] != 221 or dismiss_action["unresolved_after"] != 221 or \
            dismiss_action["imports_resolved"] != ["audio_terminal_ui_action_5e68b4"] or \
            dismiss_action["imports_added"] != ["audio_terminal_ui_restore_query_5e6620"]:
        raise RuntimeError("Apollo Main Terminal query-dismiss action binding changed")
    main_obj = file_checked(dismiss_action["linked_object"], dismiss_action["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 221 or "audio_terminal_ui_action_5e68b4" in actual:
        raise RuntimeError("Apollo Main Terminal query-dismiss action frontier changed")
    status_action_path = G2 / "build/c-firmware/20261016/main-terminal-ui-action-status-5e7022/receipt.json"
    status_action, status_action_ref = receipt(status_action_path)
    if status_action["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_ACTION_STATUS_C" or \
            status_action["base_sha256"] != main_obj["sha256"] or \
            status_action["unresolved_before"] != 221 or status_action["unresolved_after"] != 221 or \
            status_action["imports_resolved"] != ["audio_terminal_ui_action_5e7022"] or \
            status_action["imports_added"] != ["audio_terminal_display_status_44ea04"] or \
            set(status_action["additional_providers"]) != {
                "audio_terminal_status_low_5e4f10", "audio_terminal_status_high_5e4f14"}:
        raise RuntimeError("Apollo Main Terminal status action binding changed")
    main_obj = file_checked(status_action["linked_object"], status_action["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 221 or "audio_terminal_ui_action_5e7022" in actual:
        raise RuntimeError("Apollo Main Terminal status action frontier changed")
    reset_pair_path = G2 / "build/c-firmware/20261016/main-terminal-ui-action-reset-pair-5e5290/receipt.json"
    reset_pair, reset_pair_ref = receipt(reset_pair_path)
    if reset_pair["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_ACTION_RESET_PAIR_C" or \
            reset_pair["base_sha256"] != main_obj["sha256"] or \
            reset_pair["unresolved_before"] != 221 or reset_pair["unresolved_after"] != 223 or \
            set(reset_pair["imports_resolved"]) != {
                "audio_terminal_ui_action_5e5290", "audio_terminal_ui_action_5e5386"} or \
            set(reset_pair["imports_added"]) != {
                "audio_terminal_reset_first_5e51ba", "audio_terminal_reset_mode_5eae2c",
                "audio_terminal_reset_display_5e4c84", "audio_terminal_reset_subtree_5ea342"}:
        raise RuntimeError("Apollo Main Terminal reset-pair binding changed")
    main_obj = file_checked(reset_pair["linked_object"], reset_pair["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 223 or any(name in actual for name in reset_pair["imports_resolved"]):
        raise RuntimeError("Apollo Main Terminal reset-pair frontier changed")
    reset_children_path = G2 / "build/c-firmware/20261016/main-terminal-reset-mode-display/receipt.json"
    reset_children, reset_children_ref = receipt(reset_children_path)
    if reset_children["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_RESET_MODE_DISPLAY_C" or \
            reset_children["base_sha256"] != main_obj["sha256"] or \
            reset_children["unresolved_before"] != 223 or reset_children["unresolved_after"] != 222 or \
            set(reset_children["imports_resolved"]) != {
                "audio_terminal_reset_mode_5eae2c", "audio_terminal_reset_display_5e4c84"} or \
            reset_children["imports_added"] != ["audio_terminal_mode_set_5eae1e"]:
        raise RuntimeError("Apollo Main Terminal reset children binding changed")
    main_obj = file_checked(reset_children["linked_object"], reset_children["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 222 or any(name in actual for name in reset_children["imports_resolved"]):
        raise RuntimeError("Apollo Main Terminal reset children frontier changed")
    mode_set_path = G2 / "build/c-firmware/20261016/main-terminal-mode-set-5eae1e/receipt.json"
    mode_set, mode_set_ref = receipt(mode_set_path)
    if mode_set["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_MODE_SET_C" or \
            mode_set["base_sha256"] != main_obj["sha256"] or \
            mode_set["unresolved_before"] != 222 or mode_set["unresolved_after"] != 222 or \
            mode_set["imports_resolved"] != ["audio_terminal_mode_set_5eae1e"] or \
            mode_set["imports_added"] != ["audio_terminal_event_emit_5eadd4"]:
        raise RuntimeError("Apollo Main Terminal mode-set binding changed")
    main_obj = file_checked(mode_set["linked_object"], mode_set["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 222 or "audio_terminal_mode_set_5eae1e" in actual:
        raise RuntimeError("Apollo Main Terminal mode-set frontier changed")
    event_emit_path = G2 / "build/c-firmware/20261016/main-terminal-event-emit-5eadd4/receipt.json"
    event_emit, event_emit_ref = receipt(event_emit_path)
    if event_emit["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_EVENT_EMIT_C" or \
            event_emit["base_sha256"] != main_obj["sha256"] or \
            event_emit["unresolved_before"] != 222 or event_emit["unresolved_after"] != 225 or \
            event_emit["imports_resolved"] != ["audio_terminal_event_emit_5eadd4"] or \
            set(event_emit["imports_added"]) != {
                "audio_terminal_event_type2_5eabde", "audio_terminal_event_type4_5ea9f6",
                "audio_terminal_event_default_5eaad4", "audio_terminal_event_type3_mask_5eaca0"}:
        raise RuntimeError("Apollo Main Terminal event-emitter binding changed")
    main_obj = file_checked(event_emit["linked_object"], event_emit["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 225 or "audio_terminal_event_emit_5eadd4" in actual:
        raise RuntimeError("Apollo Main Terminal event-emitter frontier changed")
    event_type4_path = G2 / "build/c-firmware/20261016/main-terminal-event-type4-5ea9f6/receipt.json"
    event_type4, event_type4_ref = receipt(event_type4_path)
    if event_type4["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_EVENT_TYPE4_C" or \
            event_type4["base_sha256"] != main_obj["sha256"] or \
            event_type4["unresolved_before"] != 225 or event_type4["unresolved_after"] != 226 or \
            event_type4["imports_resolved"] != ["audio_terminal_event_type4_5ea9f6"] or \
            set(event_type4["imports_added"]) != {
                "audio_lv_object_size_call_43f4c0", "audio_terminal_event_reset_list_5ea7dc"}:
        raise RuntimeError("Apollo Main Terminal event type 4 binding changed")
    main_obj = file_checked(event_type4["linked_object"], event_type4["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 226 or "audio_terminal_event_type4_5ea9f6" in actual:
        raise RuntimeError("Apollo Main Terminal event type 4 frontier changed")
    reset_list_path = G2 / "build/c-firmware/20261016/main-terminal-event-reset-list-5ea7dc/receipt.json"
    reset_list, reset_list_ref = receipt(reset_list_path)
    if reset_list["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_EVENT_RESET_LIST_C" or \
            reset_list["base_sha256"] != main_obj["sha256"] or \
            reset_list["unresolved_before"] != 226 or reset_list["unresolved_after"] != 226 or \
            reset_list["imports_resolved"] != ["audio_terminal_event_reset_list_5ea7dc"] or \
            reset_list["imports_added"] != ["audio_lv_object_flag_43ded4"]:
        raise RuntimeError("Apollo Main Terminal event list-reset binding changed")
    main_obj = file_checked(reset_list["linked_object"], reset_list["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 226 or "audio_terminal_event_reset_list_5ea7dc" in actual:
        raise RuntimeError("Apollo Main Terminal event list-reset frontier changed")
    refresh_view_path = G2 / "build/c-firmware/20261016/main-terminal-event-refresh-view-5ea992/oracle-receipt.json"
    refresh_view, refresh_view_ref = receipt(refresh_view_path)
    refresh_source = G2 / "components/audio/uart_thread_source_candidate/terminal_event_refresh_view_5ea992.c"
    if refresh_view["status"] != "PASS_EXPERIMENTAL_TERMINAL_EVENT_REFRESH_VIEW_C_ORACLE" or \
            refresh_view["cases"] != 48 or \
            refresh_view["source_sha256"] != hashlib.sha256(refresh_source.read_bytes()).hexdigest():
        raise RuntimeError("Apollo Main Terminal view-refresh source evidence changed")
    for staged_name, staged_status, staged_cases, staged_source in (
            ("select-input-5eaa54", "PASS_EXPERIMENTAL_TERMINAL_EVENT_SELECT_INPUT_C_ORACLE", 36,
             "terminal_event_select_input_5eaa54.c"),
            ("apply-input-5eaa96", "PASS_EXPERIMENTAL_TERMINAL_EVENT_APPLY_INPUT_C_ORACLE", 36,
             "terminal_event_apply_input_5eaa96.c")):
        staged_path = G2 / f"build/c-firmware/20261016/main-terminal-event-{staged_name}/oracle-receipt.json"
        staged, staged_ref = receipt(staged_path)
        source_path = G2 / "components/audio/uart_thread_source_candidate" / staged_source
        if staged["status"] != staged_status or staged["cases"] != staged_cases or \
                staged["source_sha256"] != hashlib.sha256(source_path.read_bytes()).hexdigest():
            raise RuntimeError(f"Apollo Main Terminal {staged_name} source evidence changed")
        if staged_name.startswith("select"):
            select_input_ref = staged_ref
        else:
            apply_input_ref = staged_ref
    for bound_dir, status, before_count, after_count, resolved, added in (
            ("main-terminal-event-default-5eaad4", "PASS_EXPERIMENTAL_MAIN_TERMINAL_EVENT_DEFAULT_C",
             226, 233, "audio_terminal_event_default_5eaad4",
             {"audio_terminal_event_select_input_5eaa54", "audio_terminal_resource_597324",
              "audio_terminal_item_59737c", "audio_terminal_item_height_5ea67a",
              "audio_terminal_recompute_offsets_5ea6da", "audio_terminal_event_apply_input_5eaa96",
              "audio_terminal_event_refresh_view_5ea992", "audio_terminal_view_position_5ea926"}),
            ("main-terminal-event-select-input-5eaa54", "PASS_EXPERIMENTAL_MAIN_TERMINAL_EVENT_SELECT_INPUT_C",
             233, 232, "audio_terminal_event_select_input_5eaa54", set()),
            ("main-terminal-event-apply-input-5eaa96", "PASS_EXPERIMENTAL_MAIN_TERMINAL_EVENT_APPLY_INPUT_C",
             232, 231, "audio_terminal_event_apply_input_5eaa96", set()),
            ("main-terminal-event-refresh-view-5ea992", "PASS_EXPERIMENTAL_MAIN_TERMINAL_EVENT_REFRESH_VIEW_C",
             231, 230, "audio_terminal_event_refresh_view_5ea992", set())):
        bound_path = G2 / "build/c-firmware/20261016" / bound_dir / "receipt.json"
        bound, bound_ref = receipt(bound_path)
        if bound["status"] != status or bound["base_sha256"] != main_obj["sha256"] or \
                bound["unresolved_before"] != before_count or \
                bound["unresolved_after"] != after_count or \
                bound["imports_resolved"] != [resolved] or \
                set(bound["imports_added"]) != added:
            raise RuntimeError(f"Apollo Main Terminal {bound_dir} binding changed")
        main_obj = file_checked(bound["linked_object"], bound["linked_sha256"])
        actual = undefined(ROOT / main_obj["path"])
        if len(actual) != after_count or resolved in actual:
            raise RuntimeError(f"Apollo Main Terminal {bound_dir} frontier changed")
        if bound_dir.endswith("default-5eaad4"):
            event_default_ref = bound_ref
        elif bound_dir.endswith("select-input-5eaa54"):
            select_input_bound_ref = bound_ref
        elif bound_dir.endswith("apply-input-5eaa96"):
            apply_input_bound_ref = bound_ref
        else:
            refresh_view_bound_ref = bound_ref
    offsets_path = G2 / "build/c-firmware/20261016/main-terminal-recompute-offsets-5ea6da/receipt.json"
    offsets, offsets_ref = receipt(offsets_path)
    if offsets["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_RECOMPUTE_OFFSETS_C" or \
            offsets["base_sha256"] != main_obj["sha256"] or \
            offsets["unresolved_before"] != 230 or offsets["unresolved_after"] != 229 or \
            offsets["imports_resolved"] != ["audio_terminal_recompute_offsets_5ea6da"] or \
            offsets["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal offset-recompute binding changed")
    main_obj = file_checked(offsets["linked_object"], offsets["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 229 or "audio_terminal_recompute_offsets_5ea6da" in actual:
        raise RuntimeError("Apollo Main Terminal offset-recompute frontier changed")
    items_path = G2 / "build/c-firmware/20261016/main-terminal-resource-items-597324/receipt.json"
    items, items_ref = receipt(items_path)
    if items["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_RESOURCE_ITEMS_C" or \
            items["base_sha256"] != main_obj["sha256"] or \
            items["unresolved_before"] != 229 or items["unresolved_after"] != 227 or \
            items["imports_resolved"] != ["audio_terminal_item_59737c", "audio_terminal_resource_597324"] or \
            items["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal resource/item binding changed")
    main_obj = file_checked(items["linked_object"], items["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 227 or any(s in actual for s in items["imports_resolved"]):
        raise RuntimeError("Apollo Main Terminal resource/item frontier changed")
    view_pos_path = G2 / "build/c-firmware/20261016/main-terminal-view-position-5ea926/receipt.json"
    view_pos, view_pos_ref = receipt(view_pos_path)
    if view_pos["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_VIEW_POSITION_C" or \
            view_pos["base_sha256"] != main_obj["sha256"] or \
            view_pos["unresolved_before"] != 227 or view_pos["unresolved_after"] != 228 or \
            view_pos["imports_resolved"] != ["audio_terminal_view_position_5ea926"] or \
            view_pos["imports_added"] != ["audio_terminal_view_index_5ea8ce",
                                          "audio_terminal_view_select_5ea810"]:
        raise RuntimeError("Apollo Main Terminal view-position binding changed")
    main_obj = file_checked(view_pos["linked_object"], view_pos["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 228 or "audio_terminal_view_position_5ea926" in actual:
        raise RuntimeError("Apollo Main Terminal view-position frontier changed")
    view_index_path = G2 / "build/c-firmware/20261016/main-terminal-view-index-5ea8ce/receipt.json"
    view_index, view_index_ref = receipt(view_index_path)
    if view_index["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_VIEW_INDEX_C" or \
            view_index["base_sha256"] != main_obj["sha256"] or \
            view_index["unresolved_before"] != 228 or view_index["unresolved_after"] != 228 or \
            view_index["imports_resolved"] != ["audio_terminal_view_index_5ea8ce"] or \
            view_index["imports_added"] != ["audio_terminal_position_index_5ea868"]:
        raise RuntimeError("Apollo Main Terminal view-index binding changed")
    main_obj = file_checked(view_index["linked_object"], view_index["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 228 or "audio_terminal_view_index_5ea8ce" in actual:
        raise RuntimeError("Apollo Main Terminal view-index frontier changed")
    position_index_path = G2 / "build/c-firmware/20261016/main-terminal-position-index-5ea868/receipt.json"
    position_index, position_index_ref = receipt(position_index_path)
    if position_index["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_POSITION_INDEX_C" or \
            position_index["base_sha256"] != main_obj["sha256"] or \
            position_index["unresolved_before"] != 228 or position_index["unresolved_after"] != 227 or \
            position_index["imports_resolved"] != ["audio_terminal_position_index_5ea868"] or \
            position_index["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal position-index binding changed")
    main_obj = file_checked(position_index["linked_object"], position_index["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 227 or "audio_terminal_position_index_5ea868" in actual:
        raise RuntimeError("Apollo Main Terminal position-index frontier changed")
    view_select_path = G2 / "build/c-firmware/20261016/main-terminal-view-select-5ea810/receipt.json"
    view_select, view_select_ref = receipt(view_select_path)
    if view_select["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_VIEW_SELECT_C" or \
            view_select["base_sha256"] != main_obj["sha256"] or \
            view_select["unresolved_before"] != 227 or view_select["unresolved_after"] != 227 or \
            view_select["imports_resolved"] != ["audio_terminal_view_select_5ea810"] or \
            view_select["imports_added"] != ["audio_terminal_view_row_5ea768"]:
        raise RuntimeError("Apollo Main Terminal view-select binding changed")
    main_obj = file_checked(view_select["linked_object"], view_select["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 227 or "audio_terminal_view_select_5ea810" in actual:
        raise RuntimeError("Apollo Main Terminal view-select frontier changed")
    view_row_path = G2 / "build/c-firmware/20261016/main-terminal-view-row-5ea768/receipt.json"
    view_row, view_row_ref = receipt(view_row_path)
    if view_row["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_VIEW_ROW_C" or \
            view_row["base_sha256"] != main_obj["sha256"] or \
            view_row["unresolved_before"] != 227 or view_row["unresolved_after"] != 229 or \
            view_row["imports_resolved"] != ["audio_terminal_view_row_5ea768"] or \
            view_row["imports_added"] != ["audio_lv_object_clear_flag_43dfa4",
                                       "audio_lv_object_position_43f09a",
                                       "audio_terminal_row_bind_5ea564"]:
        raise RuntimeError("Apollo Main Terminal view-row binding changed")
    main_obj = file_checked(view_row["linked_object"], view_row["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 229 or "audio_terminal_view_row_5ea768" in actual:
        raise RuntimeError("Apollo Main Terminal view-row frontier changed")
    lv_alias_path = G2 / "build/c-firmware/20261016/main-terminal-lv-existing-aliases/receipt.json"
    lv_alias, lv_alias_ref = receipt(lv_alias_path)
    if lv_alias["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_LV_EXISTING_ALIASES_C" or \
            lv_alias["base_sha256"] != main_obj["sha256"] or \
            lv_alias["unresolved_before"] != 229 or lv_alias["unresolved_after"] != 226 or \
            lv_alias["imports_resolved"] != ["audio_lv_object_clear_flag_43dfa4",
                                           "audio_lv_object_flag_43ded4",
                                           "audio_lv_object_position_43f09a"] or \
            lv_alias["imports_added"] != [] or \
            lv_alias["provider_symbols"] != ["audio_uart_page_43ded4",
                                             "audio_uart_page_43dfa4",
                                             "audio_uart_page_43f09a"]:
        raise RuntimeError("Apollo Main Terminal existing LVGL alias binding changed")
    main_obj = file_checked(lv_alias["linked_object"], lv_alias["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 226 or any(s in actual for s in lv_alias["imports_resolved"]):
        raise RuntimeError("Apollo Main Terminal existing LVGL alias frontier changed")
    item_height_path = G2 / "build/c-firmware/20261016/main-terminal-item-height-5ea67a/receipt.json"
    item_height, item_height_ref = receipt(item_height_path)
    if item_height["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_ITEM_HEIGHT_C" or \
            item_height["base_sha256"] != main_obj["sha256"] or \
            item_height["unresolved_before"] != 226 or item_height["unresolved_after"] != 226 or \
            item_height["imports_resolved"] != ["audio_terminal_item_height_5ea67a"] or \
            item_height["imports_added"] != ["audio_terminal_item_spacing_5ea2c2"]:
        raise RuntimeError("Apollo Main Terminal item-height binding changed")
    main_obj = file_checked(item_height["linked_object"], item_height["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 226 or "audio_terminal_item_height_5ea67a" in actual:
        raise RuntimeError("Apollo Main Terminal item-height frontier changed")
    item_spacing_path = G2 / "build/c-firmware/20261016/main-terminal-item-spacing-5ea2c2/receipt.json"
    item_spacing, item_spacing_ref = receipt(item_spacing_path)
    if item_spacing["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_ITEM_SPACING_C" or \
            item_spacing["base_sha256"] != main_obj["sha256"] or \
            item_spacing["unresolved_before"] != 226 or item_spacing["unresolved_after"] != 225 or \
            item_spacing["imports_resolved"] != ["audio_terminal_item_spacing_5ea2c2"] or \
            item_spacing["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal item-spacing binding changed")
    main_obj = file_checked(item_spacing["linked_object"], item_spacing["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 225 or "audio_terminal_item_spacing_5ea2c2" in actual:
        raise RuntimeError("Apollo Main Terminal item-spacing frontier changed")
    row_bind_path = G2 / "build/c-firmware/20261016/main-terminal-row-bind-5ea564/receipt.json"
    row_bind, row_bind_ref = receipt(row_bind_path)
    if row_bind["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_ROW_BIND_C" or \
            row_bind["base_sha256"] != main_obj["sha256"] or \
            row_bind["unresolved_before"] != 225 or row_bind["unresolved_after"] != 243 or \
            row_bind["imports_resolved"] != ["audio_terminal_row_bind_5ea564"] or \
            set(row_bind["imports_added"]) != {
                "audio_lv_child_44dce2", "audio_lv_child_count_44ddea", "audio_lv_color_44104c",
                "audio_lv_delete_44d7b8", "audio_lv_image_create_498668", "audio_lv_image_source_498680",
                "audio_lv_label_create_499416", "audio_lv_label_mode_499678", "audio_lv_label_text_49942e",
                "audio_lv_style_a_44145a", "audio_lv_style_alpha_44142e", "audio_lv_style_color_44140e",
                "audio_lv_style_font_44143e", "audio_lv_style_opa_441488", "audio_lv_style_spacing_44144c",
                "audio_lv_width_43f506", "audio_terminal_image_y_5ea2b0",
                "audio_terminal_row_color_5ea2f2", "audio_terminal_row_image_5ea524"}:
        raise RuntimeError("Apollo Main Terminal row-bind binding changed")
    main_obj = file_checked(row_bind["linked_object"], row_bind["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 243 or "audio_terminal_row_bind_5ea564" in actual:
        raise RuntimeError("Apollo Main Terminal row-bind frontier changed")
    row_alias_path = G2 / "build/c-firmware/20261016/main-terminal-row-existing-aliases/receipt.json"
    row_alias, row_alias_ref = receipt(row_alias_path)
    expected_row_aliases = {
        "audio_lv_child_44dce2", "audio_lv_child_count_44ddea", "audio_lv_color_44104c",
        "audio_lv_delete_44d7b8", "audio_lv_image_create_498668", "audio_lv_image_source_498680",
        "audio_lv_label_create_499416", "audio_lv_label_mode_499678", "audio_lv_label_text_49942e",
        "audio_lv_style_a_44145a", "audio_lv_style_alpha_44142e", "audio_lv_style_color_44140e",
        "audio_lv_style_font_44143e", "audio_lv_style_opa_441488", "audio_lv_style_spacing_44144c",
        "audio_lv_width_43f506"}
    if row_alias["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_ROW_EXISTING_ALIASES_C" or \
            row_alias["base_sha256"] != main_obj["sha256"] or \
            row_alias["unresolved_before"] != 243 or row_alias["unresolved_after"] != 227 or \
            set(row_alias["imports_resolved"]) != expected_row_aliases or \
            row_alias["imports_added"] != [] or \
            set(row_alias["provider_pairs"]) != expected_row_aliases:
        raise RuntimeError("Apollo Main Terminal row existing-alias binding changed")
    main_obj = file_checked(row_alias["linked_object"], row_alias["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 227 or expected_row_aliases.intersection(actual):
        raise RuntimeError("Apollo Main Terminal row existing-alias frontier changed")
    row_children_path = G2 / "build/c-firmware/20261016/main-terminal-row-children-5ea2b0/receipt.json"
    row_children, row_children_ref = receipt(row_children_path)
    if row_children["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_ROW_CHILDREN_C" or \
            row_children["base_sha256"] != main_obj["sha256"] or \
            row_children["unresolved_before"] != 227 or row_children["unresolved_after"] != 225 or \
            row_children["imports_resolved"] != ["audio_terminal_image_y_5ea2b0",
                                                 "audio_terminal_row_color_5ea2f2",
                                                 "audio_terminal_row_image_5ea524"] or \
            row_children["imports_added"] != ["audio_terminal_row_image_hint_5ea4f0"]:
        raise RuntimeError("Apollo Main Terminal row-children binding changed")
    main_obj = file_checked(row_children["linked_object"], row_children["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 225 or any(s in actual for s in row_children["imports_resolved"]):
        raise RuntimeError("Apollo Main Terminal row-children frontier changed")
    row_hint_path = G2 / "build/c-firmware/20261016/main-terminal-row-image-hint-5ea4f0/receipt.json"
    row_hint, row_hint_ref = receipt(row_hint_path)
    if row_hint["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_ROW_IMAGE_HINT_C" or \
            row_hint["base_sha256"] != main_obj["sha256"] or \
            row_hint["unresolved_before"] != 225 or row_hint["unresolved_after"] != 224 or \
            row_hint["imports_resolved"] != ["audio_terminal_row_image_hint_5ea4f0"] or \
            row_hint["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal row-image-hint binding changed")
    main_obj = file_checked(row_hint["linked_object"], row_hint["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 224 or "audio_terminal_row_image_hint_5ea4f0" in actual:
        raise RuntimeError("Apollo Main Terminal row-image-hint frontier changed")
    event_type2_path = G2 / "build/c-firmware/20261016/main-terminal-event-type2-5eabde/receipt.json"
    event_type2, event_type2_ref = receipt(event_type2_path)
    if event_type2["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_EVENT_TYPE2_C" or \
            event_type2["base_sha256"] != main_obj["sha256"] or \
            event_type2["unresolved_before"] != 224 or event_type2["unresolved_after"] != 225 or \
            event_type2["imports_resolved"] != ["audio_terminal_event_type2_5eabde"] or \
            event_type2["imports_added"] != ["audio_terminal_last_record_597350",
                                            "audio_terminal_list_rollover_5eab8e"]:
        raise RuntimeError("Apollo Main Terminal type-two event binding changed")
    main_obj = file_checked(event_type2["linked_object"], event_type2["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 225 or "audio_terminal_event_type2_5eabde" in actual:
        raise RuntimeError("Apollo Main Terminal type-two event frontier changed")
    type2_children_path = G2 / "build/c-firmware/20261016/main-terminal-type2-children/receipt.json"
    type2_children, type2_children_ref = receipt(type2_children_path)
    if type2_children["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_TYPE2_CHILDREN_C" or \
            type2_children["base_sha256"] != main_obj["sha256"] or \
            type2_children["unresolved_before"] != 225 or type2_children["unresolved_after"] != 223 or \
            type2_children["imports_resolved"] != ["audio_terminal_last_record_597350",
                                                   "audio_terminal_list_rollover_5eab8e"] or \
            type2_children["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal type-two children binding changed")
    main_obj = file_checked(type2_children["linked_object"], type2_children["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 223 or any(s in actual for s in type2_children["imports_resolved"]):
        raise RuntimeError("Apollo Main Terminal type-two children frontier changed")
    type3_path = G2 / "build/c-firmware/20261016/main-terminal-event-type3-mask-5eaca0/receipt.json"
    type3, type3_ref = receipt(type3_path)
    if type3["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_EVENT_TYPE3_MASK_C" or \
            type3["base_sha256"] != main_obj["sha256"] or \
            type3["unresolved_before"] != 223 or type3["unresolved_after"] != 222 or \
            type3["imports_resolved"] != ["audio_terminal_event_type3_mask_5eaca0"] or \
            type3["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal type-three event binding changed")
    main_obj = file_checked(type3["linked_object"], type3["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 222 or "audio_terminal_event_type3_mask_5eaca0" in actual:
        raise RuntimeError("Apollo Main Terminal type-three event frontier changed")
    reset_first_path = G2 / "build/c-firmware/20261016/main-terminal-reset-first-5e51ba/receipt.json"
    reset_first, reset_first_ref = receipt(reset_first_path)
    if reset_first["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_RESET_FIRST_C" or \
            reset_first["base_sha256"] != main_obj["sha256"] or \
            reset_first["unresolved_before"] != 222 or reset_first["unresolved_after"] != 224 or \
            reset_first["imports_resolved"] != ["audio_terminal_reset_first_5e51ba"] or \
            reset_first["imports_added"] != ["audio_terminal_reset_ancillary_5e65f8",
                                             "audio_terminal_reset_mode_notice_54f50e",
                                             "audio_terminal_reset_preclear_5e7f26"]:
        raise RuntimeError("Apollo Main Terminal reset prelude binding changed")
    main_obj = file_checked(reset_first["linked_object"], reset_first["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 224 or "audio_terminal_reset_first_5e51ba" in actual:
        raise RuntimeError("Apollo Main Terminal reset prelude frontier changed")
    reset_ancillary_path = G2 / "build/c-firmware/20261016/main-terminal-reset-ancillary-5e65f8/receipt.json"
    reset_ancillary, reset_ancillary_ref = receipt(reset_ancillary_path)
    if reset_ancillary["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_RESET_ANCILLARY_C" or \
            reset_ancillary["base_sha256"] != main_obj["sha256"] or \
            reset_ancillary["unresolved_before"] != 224 or reset_ancillary["unresolved_after"] != 223 or \
            reset_ancillary["imports_resolved"] != ["audio_terminal_reset_ancillary_5e65f8"] or \
            reset_ancillary["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal ancillary reset binding changed")
    main_obj = file_checked(reset_ancillary["linked_object"], reset_ancillary["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 223 or "audio_terminal_reset_ancillary_5e65f8" in actual:
        raise RuntimeError("Apollo Main Terminal ancillary reset frontier changed")
    reset_preclear_path = G2 / "build/c-firmware/20261016/main-terminal-reset-preclear-5e7f26/receipt.json"
    reset_preclear, reset_preclear_ref = receipt(reset_preclear_path)
    if reset_preclear["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_RESET_PRECLEAR_C" or \
            reset_preclear["base_sha256"] != main_obj["sha256"] or \
            reset_preclear["unresolved_before"] != 223 or reset_preclear["unresolved_after"] != 222 or \
            reset_preclear["imports_resolved"] != ["audio_terminal_reset_preclear_5e7f26"] or \
            reset_preclear["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal preclear binding changed")
    main_obj = file_checked(reset_preclear["linked_object"], reset_preclear["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 222 or "audio_terminal_reset_preclear_5e7f26" in actual:
        raise RuntimeError("Apollo Main Terminal preclear frontier changed")
    app_release_path = G2 / "build/c-firmware/20261016/main-even-ai-app-release/receipt.json"
    app_release, app_release_ref = receipt(app_release_path)
    if app_release["status"] != "PASS_EXPERIMENTAL_MAIN_EVEN_AI_APP_RELEASE_C" or \
            app_release["base_sha256"] != main_obj["sha256"] or \
            app_release["unresolved_before"] != 222 or app_release["unresolved_after"] != 221 or \
            app_release["imports_resolved"] != ["audio_terminal_reset_mode_notice_54f50e"] or \
            app_release["imports_added"] != []:
        raise RuntimeError("Apollo Main audio-manager app release binding changed")
    main_obj = file_checked(app_release["linked_object"], app_release["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 221 or "audio_terminal_reset_mode_notice_54f50e" in actual:
        raise RuntimeError("Apollo Main audio-manager app release frontier changed")
    reset_subtree_path = G2 / "build/c-firmware/20261016/main-terminal-reset-subtree-5ea342/receipt.json"
    reset_subtree, reset_subtree_ref = receipt(reset_subtree_path)
    if reset_subtree["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_RESET_SUBTREE_C" or \
            reset_subtree["base_sha256"] != main_obj["sha256"] or \
            reset_subtree["unresolved_before"] != 221 or reset_subtree["unresolved_after"] != 222 or \
            reset_subtree["imports_resolved"] != ["audio_terminal_reset_subtree_5ea342"] or \
            reset_subtree["imports_added"] != ["audio_terminal_initial_image_y_5ea2d4",
                                               "audio_terminal_lv_style_four_5ea224"]:
        raise RuntimeError("Apollo Main Terminal reset subtree binding changed")
    file_checked(reset_subtree["assets"], reset_subtree["assets_sha256"])
    file_checked(reset_subtree["assets_object"], reset_subtree["assets_object_sha256"])
    main_obj = file_checked(reset_subtree["linked_object"], reset_subtree["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 222 or "audio_terminal_reset_subtree_5ea342" in actual:
        raise RuntimeError("Apollo Main Terminal reset subtree frontier changed")
    subtree_children_path = G2 / "build/c-firmware/20261016/main-terminal-reset-subtree-children/receipt.json"
    subtree_children, subtree_children_ref = receipt(subtree_children_path)
    if subtree_children["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_RESET_SUBTREE_CHILDREN_C" or \
            subtree_children["base_sha256"] != main_obj["sha256"] or \
            subtree_children["unresolved_before"] != 222 or subtree_children["unresolved_after"] != 220 or \
            subtree_children["imports_resolved"] != ["audio_terminal_initial_image_y_5ea2d4",
                                                     "audio_terminal_lv_style_four_5ea224"] or \
            subtree_children["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal reset subtree children binding changed")
    main_obj = file_checked(subtree_children["linked_object"], subtree_children["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 220 or any(s in actual for s in subtree_children["imports_resolved"]):
        raise RuntimeError("Apollo Main Terminal reset subtree children frontier changed")
    restore_query_path = G2 / "build/c-firmware/20261016/main-terminal-ui-restore-query-5e6620/receipt.json"
    restore_query, restore_query_ref = receipt(restore_query_path)
    if restore_query["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_RESTORE_QUERY_C" or \
            restore_query["base_sha256"] != main_obj["sha256"] or \
            restore_query["unresolved_before"] != 220 or restore_query["unresolved_after"] != 219 or \
            restore_query["imports_resolved"] != ["audio_terminal_ui_restore_query_5e6620"] or \
            restore_query["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal query restore binding changed")
    main_obj = file_checked(restore_query["linked_object"], restore_query["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 219 or "audio_terminal_ui_restore_query_5e6620" in actual:
        raise RuntimeError("Apollo Main Terminal query restore frontier changed")
    action_57c6_path = G2 / "build/c-firmware/20261016/main-terminal-ui-action-5e57c6/receipt.json"
    action_57c6, action_57c6_ref = receipt(action_57c6_path)
    if action_57c6["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_ACTION_5E57C6_C" or \
            action_57c6["base_sha256"] != main_obj["sha256"] or \
            action_57c6["unresolved_before"] != 219 or action_57c6["unresolved_after"] != 219 or \
            action_57c6["imports_resolved"] != ["audio_terminal_ui_action_5e57c6"] or \
            action_57c6["imports_added"] != ["audio_terminal_image_set_5e47fe"]:
        raise RuntimeError("Apollo Main Terminal return-to-input action binding changed")
    main_obj = file_checked(action_57c6["linked_object"], action_57c6["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 219 or "audio_terminal_ui_action_5e57c6" in actual:
        raise RuntimeError("Apollo Main Terminal return-to-input action frontier changed")
    image_set_path = G2 / "build/c-firmware/20261016/main-terminal-image-set-5e47fe/receipt.json"
    image_set, image_set_ref = receipt(image_set_path)
    if image_set["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_IMAGE_SET_C" or \
            image_set["base_sha256"] != main_obj["sha256"] or \
            image_set["unresolved_before"] != 219 or image_set["unresolved_after"] != 218 or \
            image_set["imports_resolved"] != ["audio_terminal_image_set_5e47fe"] or \
            image_set["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal image-set binding changed")
    main_obj = file_checked(image_set["linked_object"], image_set["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 218 or "audio_terminal_image_set_5e47fe" in actual:
        raise RuntimeError("Apollo Main Terminal image-set frontier changed")
    display_status_path = G2 / "build/c-firmware/20261016/main-terminal-display-status-alias-44ea04/receipt.json"
    display_status, display_status_ref = receipt(display_status_path)
    if display_status["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_DISPLAY_STATUS_ALIAS_C" or \
            display_status["base_sha256"] != main_obj["sha256"] or \
            display_status["unresolved_before"] != 218 or display_status["unresolved_after"] != 217 or \
            display_status["imports_resolved"] != ["audio_terminal_display_status_44ea04"] or \
            display_status["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal display-status alias binding changed")
    main_obj = file_checked(display_status["linked_object"], display_status["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 217 or "audio_terminal_display_status_44ea04" in actual:
        raise RuntimeError("Apollo Main Terminal display-status alias frontier changed")
    disconnect_actions_path = G2 / "build/c-firmware/20261016/main-terminal-ui-disconnect-actions/receipt.json"
    disconnect_actions, disconnect_actions_ref = receipt(disconnect_actions_path)
    if disconnect_actions["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_DISCONNECT_ACTIONS_C" or \
            disconnect_actions["base_sha256"] != main_obj["sha256"] or \
            disconnect_actions["unresolved_before"] != 217 or disconnect_actions["unresolved_after"] != 213 or \
            disconnect_actions["imports_resolved"] != ["audio_terminal_ui_action_5e522e",
                                                       "audio_terminal_ui_action_5e52c2",
                                                       "audio_terminal_ui_action_5e5320",
                                                       "audio_terminal_ui_action_5e53b8"] or \
            disconnect_actions["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal disconnect actions binding changed")
    file_checked(disconnect_actions["assets"], disconnect_actions["assets_sha256"])
    file_checked(disconnect_actions["assets_object"], disconnect_actions["assets_object_sha256"])
    main_obj = file_checked(disconnect_actions["linked_object"], disconnect_actions["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 213 or any(s in actual for s in disconnect_actions["imports_resolved"]):
        raise RuntimeError("Apollo Main Terminal disconnect actions frontier changed")
    action_583c_path = G2 / "build/c-firmware/20261016/main-terminal-ui-action-5e583c/receipt.json"
    action_583c, action_583c_ref = receipt(action_583c_path)
    if action_583c["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_ACTION_5E583C_C" or \
            action_583c["base_sha256"] != main_obj["sha256"] or \
            action_583c["unresolved_before"] != 213 or action_583c["unresolved_after"] != 212 or \
            action_583c["imports_resolved"] != ["audio_terminal_ui_action_5e583c"] or \
            action_583c["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal processing-response action binding changed")
    main_obj = file_checked(action_583c["linked_object"], action_583c["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 212 or "audio_terminal_ui_action_5e583c" in actual:
        raise RuntimeError("Apollo Main Terminal processing-response action frontier changed")
    style_assets_path = G2 / "build/c-firmware/20261016/main-terminal-output-style-assets/receipt.json"
    style_assets, style_assets_ref = receipt(style_assets_path)
    if style_assets["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_OUTPUT_STYLE_ASSETS_C" or \
            style_assets["base_sha256"] != main_obj["sha256"] or \
            style_assets["unresolved_before"] != 212 or style_assets["unresolved_after"] != 211 or \
            style_assets["imports_resolved"] != ["audio_terminal_output_style_20003f80"] or \
            style_assets["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal output style assets binding changed")
    oracle = ROOT / style_assets["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != style_assets["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal output style oracle changed")
    file_checked(style_assets["source"], style_assets["source_sha256"])
    main_obj = file_checked(style_assets["linked_object"], style_assets["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 211 or "audio_terminal_output_style_20003f80" in actual:
        raise RuntimeError("Apollo Main Terminal output style frontier changed")
    action_54a2_path = G2 / "build/c-firmware/20261016/main-terminal-ui-action-5e54a2/receipt.json"
    action_54a2, action_54a2_ref = receipt(action_54a2_path)
    if action_54a2["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_ACTION_5E54A2_C" or \
            action_54a2["base_sha256"] != main_obj["sha256"] or \
            action_54a2["unresolved_before"] != 211 or action_54a2["unresolved_after"] != 210 or \
            action_54a2["imports_resolved"] != ["audio_terminal_ui_action_5e54a2"] or \
            action_54a2["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal event-34 action binding changed")
    oracle = ROOT / action_54a2["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != action_54a2["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal event-34 oracle changed")
    file_checked(action_54a2["source"], action_54a2["source_sha256"])
    main_obj = file_checked(action_54a2["linked_object"], action_54a2["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 210 or "audio_terminal_ui_action_5e54a2" in actual:
        raise RuntimeError("Apollo Main Terminal event-34 frontier changed")
    action_576c_path = G2 / "build/c-firmware/20261016/main-terminal-ui-action-5e576c/receipt.json"
    action_576c, action_576c_ref = receipt(action_576c_path)
    if action_576c["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_ACTION_5E576C_C" or \
            action_576c["base_sha256"] != main_obj["sha256"] or \
            action_576c["unresolved_before"] != 210 or action_576c["unresolved_after"] != 211 or \
            action_576c["imports_resolved"] != ["audio_terminal_ui_action_5e576c"] or \
            action_576c["imports_added"] != ["audio_terminal_display_fallback_5ecafa", "audio_terminal_fsm_prepare_5eae94"]:
        raise RuntimeError("Apollo Main Terminal BLE display-request binding changed")
    oracle = ROOT / action_576c["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != action_576c["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal BLE display-request oracle changed")
    file_checked(action_576c["source"], action_576c["source_sha256"])
    main_obj = file_checked(action_576c["linked_object"], action_576c["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 211 or "audio_terminal_ui_action_5e576c" in actual:
        raise RuntimeError("Apollo Main Terminal BLE display-request frontier changed")
    fallback_adapter_path = G2 / "build/c-firmware/20261016/main-terminal-display-fallback-adapter-5ecafa/receipt.json"
    fallback_adapter, fallback_adapter_ref = receipt(fallback_adapter_path)
    if fallback_adapter["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_DISPLAY_FALLBACK_ADAPTER_C" or \
            fallback_adapter["base_sha256"] != main_obj["sha256"] or \
            fallback_adapter["unresolved_before"] != 211 or fallback_adapter["unresolved_after"] != 210 or \
            fallback_adapter["imports_resolved"] != ["audio_terminal_display_fallback_5ecafa"] or \
            fallback_adapter["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal fallback adapter binding changed")
    file_checked(fallback_adapter["source"], fallback_adapter["source_sha256"])
    file_checked(fallback_adapter["provider"], fallback_adapter["provider_sha256"])
    provider_receipt = ROOT / fallback_adapter["provider_receipt"]
    if hashlib.sha256(provider_receipt.read_bytes()).hexdigest() != fallback_adapter["provider_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal fallback provider evidence changed")
    main_obj = file_checked(fallback_adapter["linked_object"], fallback_adapter["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 210 or "audio_terminal_display_fallback_5ecafa" in actual:
        raise RuntimeError("Apollo Main Terminal fallback adapter frontier changed")
    action_63b4_path = G2 / "build/c-firmware/20261016/main-terminal-ui-action-5e63b4/receipt.json"
    action_63b4, action_63b4_ref = receipt(action_63b4_path)
    if action_63b4["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_ACTION_5E63B4_C" or \
            action_63b4["base_sha256"] != main_obj["sha256"] or \
            action_63b4["unresolved_before"] != 210 or action_63b4["unresolved_after"] != 209 or \
            action_63b4["imports_resolved"] != ["audio_terminal_ui_action_5e63b4"] or \
            action_63b4["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal event-word action binding changed")
    oracle = ROOT / action_63b4["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != action_63b4["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal event-word oracle changed")
    file_checked(action_63b4["source"], action_63b4["source_sha256"])
    main_obj = file_checked(action_63b4["linked_object"], action_63b4["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 209 or "audio_terminal_ui_action_5e63b4" in actual:
        raise RuntimeError("Apollo Main Terminal event-word frontier changed")
    scroll_actions_path = G2 / "build/c-firmware/20261016/main-terminal-ui-scroll-actions-5e6dd0-5e6e30/receipt.json"
    scroll_actions, scroll_actions_ref = receipt(scroll_actions_path)
    if scroll_actions["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_SCROLL_ACTIONS_C" or \
            scroll_actions["base_sha256"] != main_obj["sha256"] or \
            scroll_actions["unresolved_before"] != 209 or scroll_actions["unresolved_after"] != 208 or \
            scroll_actions["imports_resolved"] != ["audio_terminal_ui_action_5e6dd0", "audio_terminal_ui_action_5e6e30"] or \
            scroll_actions["imports_added"] != ["audio_terminal_notify_status_5ec190"]:
        raise RuntimeError("Apollo Main Terminal scroll actions binding changed")
    oracle = ROOT / scroll_actions["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != scroll_actions["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal scroll actions oracle changed")
    file_checked(scroll_actions["source"], scroll_actions["source_sha256"])
    main_obj = file_checked(scroll_actions["linked_object"], scroll_actions["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 208 or any(s in actual for s in scroll_actions["imports_resolved"]):
        raise RuntimeError("Apollo Main Terminal scroll actions frontier changed")
    defer_query_path = G2 / "build/c-firmware/20261016/main-terminal-ui-action-defer-query-5e6d58/receipt.json"
    defer_query, defer_query_ref = receipt(defer_query_path)
    if defer_query["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_ACTION_DEFER_QUERY_C" or \
            defer_query["base_sha256"] != main_obj["sha256"] or \
            defer_query["unresolved_before"] != 208 or defer_query["unresolved_after"] != 207 or \
            defer_query["imports_resolved"] != ["audio_terminal_ui_action_5e6d58"] or \
            defer_query["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal defer-query action binding changed")
    oracle = ROOT / defer_query["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != defer_query["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal defer-query oracle changed")
    file_checked(defer_query["source"], defer_query["source_sha256"])
    main_obj = file_checked(defer_query["linked_object"], defer_query["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 207 or "audio_terminal_ui_action_5e6d58" in actual:
        raise RuntimeError("Apollo Main Terminal defer-query frontier changed")
    notify_status_path = G2 / "build/c-firmware/20261016/main-terminal-notify-status-5ec190/receipt.json"
    notify_status, notify_status_ref = receipt(notify_status_path)
    if notify_status["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_NOTIFY_STATUS_C" or \
            notify_status["base_sha256"] != main_obj["sha256"] or \
            notify_status["unresolved_before"] != 207 or notify_status["unresolved_after"] != 208 or \
            notify_status["imports_resolved"] != ["audio_terminal_notify_status_5ec190"] or \
            notify_status["imports_added"] != ["audio_terminal_status_apply_layout_5ebc9e", "audio_terminal_status_publish_5e5498"]:
        raise RuntimeError("Apollo Main Terminal notify-status binding changed")
    oracle = ROOT / notify_status["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != notify_status["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal notify-status oracle changed")
    file_checked(notify_status["source"], notify_status["source_sha256"])
    main_obj = file_checked(notify_status["linked_object"], notify_status["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 208 or "audio_terminal_notify_status_5ec190" in actual:
        raise RuntimeError("Apollo Main Terminal notify-status frontier changed")
    status_layout_path = G2 / "build/c-firmware/20261016/main-terminal-status-apply-layout-5ebc9e/receipt.json"
    status_layout, status_layout_ref = receipt(status_layout_path)
    if status_layout["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_STATUS_APPLY_LAYOUT_C" or \
            status_layout["base_sha256"] != main_obj["sha256"] or \
            status_layout["unresolved_before"] != 208 or status_layout["unresolved_after"] != 207 or \
            status_layout["imports_resolved"] != ["audio_terminal_status_apply_layout_5ebc9e"] or \
            status_layout["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal status layout binding changed")
    oracle = ROOT / status_layout["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != status_layout["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal status layout oracle changed")
    file_checked(status_layout["source"], status_layout["source_sha256"])
    main_obj = file_checked(status_layout["linked_object"], status_layout["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 207 or "audio_terminal_status_apply_layout_5ebc9e" in actual:
        raise RuntimeError("Apollo Main Terminal status layout frontier changed")
    status_publish_path = G2 / "build/c-firmware/20261016/main-terminal-status-publish-5e5498-5cf134/receipt.json"
    status_publish, status_publish_ref = receipt(status_publish_path)
    if status_publish["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_STATUS_PUBLISH_C" or \
            status_publish["base_sha256"] != main_obj["sha256"] or \
            status_publish["unresolved_before"] != 207 or status_publish["unresolved_after"] != 206 or \
            status_publish["imports_resolved"] != ["audio_terminal_status_publish_5e5498"] or \
            status_publish["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal status publish binding changed")
    oracle = ROOT / status_publish["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != status_publish["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal status publish oracle changed")
    file_checked(status_publish["source"], status_publish["source_sha256"])
    main_obj = file_checked(status_publish["linked_object"], status_publish["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 206 or "audio_terminal_status_publish_5e5498" in actual:
        raise RuntimeError("Apollo Main Terminal status publish frontier changed")
    confirm_scroll_path = G2 / "build/c-firmware/20261016/main-terminal-ui-interrupt-confirm-scroll-5e6cb8/receipt.json"
    confirm_scroll, confirm_scroll_ref = receipt(confirm_scroll_path)
    if confirm_scroll["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_INTERRUPT_CONFIRM_SCROLL_C" or \
            confirm_scroll["base_sha256"] != main_obj["sha256"] or \
            confirm_scroll["unresolved_before"] != 206 or confirm_scroll["unresolved_after"] != 206 or \
            confirm_scroll["imports_resolved"] != ["audio_terminal_ui_action_5e6cb8"] or \
            confirm_scroll["imports_added"] != ["audio_terminal_status_apply_list_5ec3c0"]:
        raise RuntimeError("Apollo Main Terminal interrupt-confirm scroll binding changed")
    oracle = ROOT / confirm_scroll["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != confirm_scroll["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal interrupt-confirm scroll oracle changed")
    file_checked(confirm_scroll["source"], confirm_scroll["source_sha256"])
    main_obj = file_checked(confirm_scroll["linked_object"], confirm_scroll["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 206 or "audio_terminal_ui_action_5e6cb8" in actual:
        raise RuntimeError("Apollo Main Terminal interrupt-confirm scroll frontier changed")
    list_layout_path = G2 / "build/c-firmware/20261016/main-terminal-status-apply-list-5ec3c0/receipt.json"
    list_layout, list_layout_ref = receipt(list_layout_path)
    if list_layout["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_STATUS_APPLY_LIST_C" or \
            list_layout["base_sha256"] != main_obj["sha256"] or \
            list_layout["unresolved_before"] != 206 or list_layout["unresolved_after"] != 205 or \
            list_layout["imports_resolved"] != ["audio_terminal_status_apply_list_5ec3c0"] or \
            list_layout["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal interrupt-confirm list layout binding changed")
    oracle = ROOT / list_layout["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != list_layout["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal interrupt-confirm list layout oracle changed")
    file_checked(list_layout["source"], list_layout["source_sha256"])
    main_obj = file_checked(list_layout["linked_object"], list_layout["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 205 or "audio_terminal_status_apply_list_5ec3c0" in actual:
        raise RuntimeError("Apollo Main Terminal interrupt-confirm list layout frontier changed")
    confirm_show_path = G2 / "build/c-firmware/20261016/main-terminal-ui-action-interrupt-confirm-show-5e6b18/receipt.json"
    confirm_show, confirm_show_ref = receipt(confirm_show_path)
    if confirm_show["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_INTERRUPT_CONFIRM_SHOW_C" or \
            confirm_show["base_sha256"] != main_obj["sha256"] or \
            confirm_show["unresolved_before"] != 205 or confirm_show["unresolved_after"] != 205 or \
            confirm_show["imports_resolved"] != ["audio_terminal_ui_action_5e6b18"] or \
            confirm_show["imports_added"] != ["audio_terminal_interrupt_confirm_prepare_5ec446"]:
        raise RuntimeError("Apollo Main Terminal interrupt-confirm-show binding changed")
    oracle = ROOT / confirm_show["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != confirm_show["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal interrupt-confirm-show oracle changed")
    file_checked(confirm_show["source"], confirm_show["source_sha256"])
    main_obj = file_checked(confirm_show["linked_object"], confirm_show["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 205 or "audio_terminal_ui_action_5e6b18" in actual:
        raise RuntimeError("Apollo Main Terminal interrupt-confirm-show frontier changed")
    confirm_cancel_path = G2 / "build/c-firmware/20261016/main-terminal-ui-action-interrupt-confirm-cancel-5e6ba0/receipt.json"
    confirm_cancel, confirm_cancel_ref = receipt(confirm_cancel_path)
    if confirm_cancel["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_INTERRUPT_CONFIRM_CANCEL_C" or \
            confirm_cancel["base_sha256"] != main_obj["sha256"] or \
            confirm_cancel["unresolved_before"] != 205 or confirm_cancel["unresolved_after"] != 204 or \
            confirm_cancel["imports_resolved"] != ["audio_terminal_ui_action_5e6ba0"] or \
            confirm_cancel["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal interrupt-confirm-cancel binding changed")
    oracle = ROOT / confirm_cancel["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != confirm_cancel["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal interrupt-confirm-cancel oracle changed")
    file_checked(confirm_cancel["source"], confirm_cancel["source_sha256"])
    main_obj = file_checked(confirm_cancel["linked_object"], confirm_cancel["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 204 or "audio_terminal_ui_action_5e6ba0" in actual:
        raise RuntimeError("Apollo Main Terminal interrupt-confirm-cancel frontier changed")
    new_session_path = G2 / "build/c-firmware/20261016/main-terminal-ui-action-new-session-success-5ed870/receipt.json"
    new_session, new_session_ref = receipt(new_session_path)
    if new_session["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_NEW_SESSION_SUCCESS_C" or \
            new_session["base_sha256"] != main_obj["sha256"] or \
            new_session["unresolved_before"] != 204 or new_session["unresolved_after"] != 203 or \
            new_session["imports_resolved"] != ["audio_terminal_ui_action_5ed870"] or \
            new_session["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal new-session success binding changed")
    oracle = ROOT / new_session["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != new_session["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal new-session success oracle changed")
    file_checked(new_session["source"], new_session["source_sha256"])
    main_obj = file_checked(new_session["linked_object"], new_session["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 203 or "audio_terminal_ui_action_5ed870" in actual:
        raise RuntimeError("Apollo Main Terminal new-session success frontier changed")
    query_switch_path = G2 / "build/c-firmware/20261016/main-terminal-ui-action-query-notification-switch-result-5e68dc/receipt.json"
    query_switch, query_switch_ref = receipt(query_switch_path)
    if query_switch["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_NOTIFICATION_SWITCH_RESULT_C" or \
            query_switch["base_sha256"] != main_obj["sha256"] or \
            query_switch["unresolved_before"] != 203 or query_switch["unresolved_after"] != 202 or \
            query_switch["imports_resolved"] != ["audio_terminal_ui_action_5e68dc"] or \
            query_switch["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal query-notification switch-result binding changed")
    oracle = ROOT / query_switch["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != query_switch["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal query-notification switch-result oracle changed")
    file_checked(query_switch["source"], query_switch["source_sha256"])
    main_obj = file_checked(query_switch["linked_object"], query_switch["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 202 or "audio_terminal_ui_action_5e68dc" in actual:
        raise RuntimeError("Apollo Main Terminal query-notification switch-result frontier changed")
    query_scroll_path = G2 / "build/c-firmware/20261016/main-terminal-ui-query-scroll-actions-5e6e88-5e6f60/receipt.json"
    query_scroll, query_scroll_ref = receipt(query_scroll_path)
    if query_scroll["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_SCROLL_ACTIONS_C" or \
            query_scroll["base_sha256"] != main_obj["sha256"] or \
            query_scroll["unresolved_before"] != 202 or query_scroll["unresolved_after"] != 201 or \
            query_scroll["imports_resolved"] != ["audio_terminal_ui_action_5e6e88", "audio_terminal_ui_action_5e6f60"] or \
            query_scroll["imports_added"] != ["audio_terminal_query_layout_5ebb96"]:
        raise RuntimeError("Apollo Main Terminal query-scroll actions binding changed")
    oracle = ROOT / query_scroll["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != query_scroll["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal query-scroll actions oracle changed")
    file_checked(query_scroll["source"], query_scroll["source_sha256"])
    main_obj = file_checked(query_scroll["linked_object"], query_scroll["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 201 or any(s in actual for s in query_scroll["imports_resolved"]):
        raise RuntimeError("Apollo Main Terminal query-scroll actions frontier changed")
    query_layout_path = G2 / "build/c-firmware/20261016/main-terminal-query-layout-5ebb96/receipt.json"
    query_layout, query_layout_ref = receipt(query_layout_path)
    if query_layout["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_LAYOUT_C" or \
            query_layout["base_sha256"] != main_obj["sha256"] or \
            query_layout["unresolved_before"] != 201 or query_layout["unresolved_after"] != 201 or \
            query_layout["imports_resolved"] != ["audio_terminal_query_layout_5ebb96"] or \
            query_layout["imports_added"] != ["audio_terminal_query_items_style_5eb3c6"]:
        raise RuntimeError("Apollo Main Terminal query-layout binding changed")
    oracle = ROOT / query_layout["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != query_layout["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal query-layout oracle changed")
    file_checked(query_layout["source"], query_layout["source_sha256"])
    main_obj = file_checked(query_layout["linked_object"], query_layout["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 201 or "audio_terminal_query_layout_5ebb96" in actual:
        raise RuntimeError("Apollo Main Terminal query-layout frontier changed")
    query_items_path = G2 / "build/c-firmware/20261016/main-terminal-query-items-style-5eb3c6/receipt.json"
    query_items, query_items_ref = receipt(query_items_path)
    if query_items["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_ITEMS_STYLE_C" or \
            query_items["base_sha256"] != main_obj["sha256"] or \
            query_items["unresolved_before"] != 201 or query_items["unresolved_after"] != 201 or \
            query_items["imports_resolved"] != ["audio_terminal_query_items_style_5eb3c6"] or \
            query_items["imports_added"] != ["audio_terminal_query_indicator_5eb322"]:
        raise RuntimeError("Apollo Main Terminal query-items style binding changed")
    oracle = ROOT / query_items["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != query_items["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal query-items style oracle changed")
    file_checked(query_items["source"], query_items["source_sha256"])
    main_obj = file_checked(query_items["linked_object"], query_items["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 201 or "audio_terminal_query_items_style_5eb3c6" in actual:
        raise RuntimeError("Apollo Main Terminal query-items style frontier changed")
    query_indicator_path = G2 / "build/c-firmware/20261016/main-terminal-query-indicator-5eb322/receipt.json"
    query_indicator, query_indicator_ref = receipt(query_indicator_path)
    if query_indicator["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_INDICATOR_C" or \
            query_indicator["base_sha256"] != main_obj["sha256"] or \
            query_indicator["unresolved_before"] != 201 or query_indicator["unresolved_after"] != 200 or \
            query_indicator["imports_resolved"] != ["audio_terminal_query_indicator_5eb322"] or \
            query_indicator["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal query-indicator binding changed")
    oracle = ROOT / query_indicator["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != query_indicator["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal query-indicator oracle changed")
    file_checked(query_indicator["source"], query_indicator["source_sha256"])
    main_obj = file_checked(query_indicator["linked_object"], query_indicator["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 200 or "audio_terminal_query_indicator_5eb322" in actual:
        raise RuntimeError("Apollo Main Terminal query-indicator frontier changed")
    session_scroll_path = G2 / "build/c-firmware/20261016/main-terminal-ui-action-session-list-scroll-5ed492/receipt.json"
    session_scroll, session_scroll_ref = receipt(session_scroll_path)
    if session_scroll["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_SESSION_LIST_SCROLL_C" or \
            session_scroll["base_sha256"] != main_obj["sha256"] or \
            session_scroll["unresolved_before"] != 200 or session_scroll["unresolved_after"] != 200 or \
            session_scroll["imports_resolved"] != ["audio_terminal_ui_action_5ed492"] or \
            session_scroll["imports_added"] != ["audio_terminal_session_select_5ecc1a"]:
        raise RuntimeError("Apollo Main Terminal session-list scroll binding changed")
    oracle = ROOT / session_scroll["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != session_scroll["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal session-list scroll oracle changed")
    file_checked(session_scroll["source"], session_scroll["source_sha256"])
    main_obj = file_checked(session_scroll["linked_object"], session_scroll["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 200 or "audio_terminal_ui_action_5ed492" in actual:
        raise RuntimeError("Apollo Main Terminal session-list scroll frontier changed")
    session_select_path = G2 / "build/c-firmware/20261016/main-terminal-session-select-5ecc1a/receipt.json"
    session_select, session_select_ref = receipt(session_select_path)
    if session_select["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_SESSION_SELECT_C" or \
            session_select["base_sha256"] != main_obj["sha256"] or \
            session_select["unresolved_before"] != 200 or session_select["unresolved_after"] != 202 or \
            session_select["imports_resolved"] != ["audio_terminal_session_select_5ecc1a"] or \
            session_select["imports_added"] != ["audio_terminal_session_animate_5896fc", "audio_terminal_session_apply_5ecb88", "audio_terminal_session_focus_5ecbea"]:
        raise RuntimeError("Apollo Main Terminal session selection binding changed")
    oracle = ROOT / session_select["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != session_select["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal session selection oracle changed")
    file_checked(session_select["source"], session_select["source_sha256"])
    main_obj = file_checked(session_select["linked_object"], session_select["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 202 or "audio_terminal_session_select_5ecc1a" in actual:
        raise RuntimeError("Apollo Main Terminal session selection frontier changed")
    session_focus_path = G2 / "build/c-firmware/20261016/main-terminal-session-focus-5ecbea/receipt.json"
    session_focus, session_focus_ref = receipt(session_focus_path)
    if session_focus["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_SESSION_FOCUS_C" or \
            session_focus["base_sha256"] != main_obj["sha256"] or \
            session_focus["unresolved_before"] != 202 or session_focus["unresolved_after"] != 201 or \
            session_focus["imports_resolved"] != ["audio_terminal_session_focus_5ecbea"] or \
            session_focus["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal session-focus binding changed")
    oracle = ROOT / session_focus["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != session_focus["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal session-focus oracle changed")
    file_checked(session_focus["source"], session_focus["source_sha256"])
    main_obj = file_checked(session_focus["linked_object"], session_focus["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 201 or "audio_terminal_session_focus_5ecbea" in actual:
        raise RuntimeError("Apollo Main Terminal session-focus frontier changed")
    session_apply_path = G2 / "build/c-firmware/20261016/main-terminal-session-apply-5ecb88/receipt.json"
    session_apply, session_apply_ref = receipt(session_apply_path)
    if session_apply["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_SESSION_APPLY_C" or \
            session_apply["base_sha256"] != main_obj["sha256"] or \
            session_apply["unresolved_before"] != 201 or session_apply["unresolved_after"] != 201 or \
            session_apply["imports_resolved"] != ["audio_terminal_session_apply_5ecb88"] or \
            session_apply["imports_added"] != ["audio_terminal_session_row_style_5ecb08"]:
        raise RuntimeError("Apollo Main Terminal session-apply binding changed")
    oracle = ROOT / session_apply["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != session_apply["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal session-apply oracle changed")
    file_checked(session_apply["source"], session_apply["source_sha256"])
    main_obj = file_checked(session_apply["linked_object"], session_apply["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 201 or "audio_terminal_session_apply_5ecb88" in actual:
        raise RuntimeError("Apollo Main Terminal session-apply frontier changed")
    session_row_path = G2 / "build/c-firmware/20261016/main-terminal-session-row-style-5ecb08/receipt.json"
    session_row, session_row_ref = receipt(session_row_path)
    if session_row["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_SESSION_ROW_STYLE_C" or \
            session_row["base_sha256"] != main_obj["sha256"] or \
            session_row["unresolved_before"] != 201 or session_row["unresolved_after"] != 202 or \
            session_row["imports_resolved"] != ["audio_terminal_session_row_style_5ecb08"] or \
            session_row["imports_added"] != ["audio_terminal_session_row_hide_589892", "audio_terminal_session_row_show_5897ee"]:
        raise RuntimeError("Apollo Main Terminal session-row binding changed")
    oracle = ROOT / session_row["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != session_row["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal session-row oracle changed")
    file_checked(session_row["source"], session_row["source_sha256"])
    main_obj = file_checked(session_row["linked_object"], session_row["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 202 or "audio_terminal_session_row_style_5ecb08" in actual:
        raise RuntimeError("Apollo Main Terminal session-row frontier changed")
    anim_add_path = G2 / "build/c-firmware/20261016/main-terminal-list-anim-add-5896fc/receipt.json"
    anim_add, anim_add_ref = receipt(anim_add_path)
    if anim_add["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_LIST_ANIM_ADD_C" or \
            anim_add["base_sha256"] != main_obj["sha256"] or \
            anim_add["unresolved_before"] != 202 or anim_add["unresolved_after"] != 202 or \
            anim_add["imports_resolved"] != ["audio_terminal_session_animate_5896fc"] or \
            anim_add["imports_added"] != ["audio_terminal_list_anim_process_58956e"]:
        raise RuntimeError("Apollo Main Terminal list-animation add binding changed")
    oracle = ROOT / anim_add["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != anim_add["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal list-animation add oracle changed")
    file_checked(anim_add["source"], anim_add["source_sha256"])
    main_obj = file_checked(anim_add["linked_object"], anim_add["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 202 or "audio_terminal_session_animate_5896fc" in actual:
        raise RuntimeError("Apollo Main Terminal list-animation add frontier changed")
    anim_process_path = G2 / "build/c-firmware/20261016/main-terminal-list-anim-process-58956e/receipt.json"
    anim_process, anim_process_ref = receipt(anim_process_path)
    if anim_process["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_LIST_ANIM_PROCESS_C" or \
            anim_process["base_sha256"] != main_obj["sha256"] or \
            anim_process["unresolved_before"] != 202 or anim_process["unresolved_after"] != 204 or \
            anim_process["imports_resolved"] != ["audio_terminal_list_anim_process_58956e"] or \
            anim_process["imports_added"] != ["audio_terminal_list_anim_new_prepare_5894d6", "audio_terminal_list_anim_new_start_58c622", "audio_terminal_list_anim_old_start_58c6c4"]:
        raise RuntimeError("Apollo Main Terminal list-animation process binding changed")
    oracle = ROOT / anim_process["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != anim_process["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal list-animation process oracle changed")
    file_checked(anim_process["source"], anim_process["source_sha256"])
    main_obj = file_checked(anim_process["linked_object"], anim_process["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 204 or "audio_terminal_list_anim_process_58956e" in actual:
        raise RuntimeError("Apollo Main Terminal list-animation process frontier changed")
    anim_prepare_path = G2 / "build/c-firmware/20261016/main-terminal-list-anim-new-prepare-5894d6/receipt.json"
    anim_prepare, anim_prepare_ref = receipt(anim_prepare_path)
    if anim_prepare["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_LIST_ANIM_NEW_PREPARE_C" or \
            anim_prepare["base_sha256"] != main_obj["sha256"] or \
            anim_prepare["unresolved_before"] != 204 or anim_prepare["unresolved_after"] != 203 or \
            anim_prepare["imports_resolved"] != ["audio_terminal_list_anim_new_prepare_5894d6"] or \
            anim_prepare["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal list-animation new-prepare binding changed")
    oracle = ROOT / anim_prepare["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != anim_prepare["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal list-animation new-prepare oracle changed")
    file_checked(anim_prepare["source"], anim_prepare["source_sha256"])
    main_obj = file_checked(anim_prepare["linked_object"], anim_prepare["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 203 or "audio_terminal_list_anim_new_prepare_5894d6" in actual:
        raise RuntimeError("Apollo Main Terminal list-animation new-prepare frontier changed")
    anim_fade_path = G2 / "build/c-firmware/20261016/main-terminal-list-anim-fade-start-58c622/receipt.json"
    anim_fade, anim_fade_ref = receipt(anim_fade_path)
    if anim_fade["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_LIST_ANIM_FADE_START_C" or \
            anim_fade["base_sha256"] != main_obj["sha256"] or \
            anim_fade["unresolved_before"] != 203 or anim_fade["unresolved_after"] != 203 or \
            anim_fade["imports_resolved"] != ["audio_terminal_list_anim_new_start_58c622", "audio_terminal_list_anim_old_start_58c6c4"] or \
            anim_fade["imports_added"] != ["audio_terminal_button_fade_callback_58c230", "audio_uart_lv_anim_path_450688"]:
        raise RuntimeError("Apollo Main Terminal list-animation fade-start binding changed")
    oracle = ROOT / anim_fade["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != anim_fade["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal list-animation fade-start oracle changed")
    file_checked(anim_fade["source"], anim_fade["source_sha256"])
    main_obj = file_checked(anim_fade["linked_object"], anim_fade["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 203 or any(name in actual for name in anim_fade["imports_resolved"]):
        raise RuntimeError("Apollo Main Terminal list-animation fade-start frontier changed")
    anim_path_path = G2 / "build/c-firmware/20261016/main-terminal-list-anim-path-450688/receipt.json"
    anim_path, anim_path_ref = receipt(anim_path_path)
    if anim_path["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_LIST_ANIM_PATH_C" or \
            anim_path["base_sha256"] != main_obj["sha256"] or \
            anim_path["unresolved_before"] != 203 or anim_path["unresolved_after"] != 202 or \
            anim_path["imports_resolved"] != ["audio_uart_lv_anim_path_450688"] or \
            anim_path["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal list-animation path binding changed")
    oracle = ROOT / anim_path["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != anim_path["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal list-animation path oracle changed")
    file_checked(anim_path["source"], anim_path["source_sha256"])
    main_obj = file_checked(anim_path["linked_object"], anim_path["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 202 or "audio_uart_lv_anim_path_450688" in actual:
        raise RuntimeError("Apollo Main Terminal list-animation path frontier changed")
    row_visibility_path = G2 / "build/c-firmware/20261016/main-terminal-session-row-visibility-5897ee/receipt.json"
    row_visibility, row_visibility_ref = receipt(row_visibility_path)
    if row_visibility["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_SESSION_ROW_VISIBILITY_C" or \
            row_visibility["base_sha256"] != main_obj["sha256"] or \
            row_visibility["unresolved_before"] != 202 or row_visibility["unresolved_after"] != 201 or \
            row_visibility["imports_resolved"] != ["audio_terminal_session_row_hide_589892", "audio_terminal_session_row_show_5897ee"] or \
            row_visibility["imports_added"] != ["audio_uart_image_class_756108"]:
        raise RuntimeError("Apollo Main Terminal session-row visibility binding changed")
    for path, digest in zip(row_visibility["oracle_receipts"], row_visibility["oracle_receipt_sha256"]):
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != digest:
            raise RuntimeError("Apollo Main Terminal session-row visibility oracle changed")
    for source, digest in zip(row_visibility["sources"], row_visibility["source_sha256"]):
        file_checked(source, digest)
    main_obj = file_checked(row_visibility["linked_object"], row_visibility["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 201 or any(name in actual for name in row_visibility["imports_resolved"]):
        raise RuntimeError("Apollo Main Terminal session-row visibility frontier changed")
    image_class_path = G2 / "build/c-firmware/20261016/main-lv-image-class-756108/receipt.json"
    image_class, image_class_ref = receipt(image_class_path)
    if image_class["status"] != "PASS_EXPERIMENTAL_MAIN_LV_IMAGE_CLASS_C" or \
            image_class["base_sha256"] != main_obj["sha256"] or \
            image_class["unresolved_before"] != 201 or image_class["unresolved_after"] != 203 or \
            image_class["imports_resolved"] != ["audio_uart_image_class_756108"] or \
            image_class["imports_added"] != ["audio_uart_lv_image_ctor_498bd0", "audio_uart_lv_image_dtor_498c6c", "audio_uart_lv_image_event_498c9c"]:
        raise RuntimeError("Apollo Main LVGL image class binding changed")
    oracle = ROOT / image_class["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != image_class["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main LVGL image class oracle changed")
    file_checked(image_class["source"], image_class["source_sha256"])
    main_obj = file_checked(image_class["linked_object"], image_class["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 203 or "audio_uart_image_class_756108" in actual:
        raise RuntimeError("Apollo Main LVGL image class frontier changed")
    image_lifecycle_path = G2 / "build/c-firmware/20261016/main-lv-image-lifecycle-498bd0/receipt.json"
    image_lifecycle, image_lifecycle_ref = receipt(image_lifecycle_path)
    if image_lifecycle["status"] != "PASS_EXPERIMENTAL_MAIN_LV_IMAGE_LIFECYCLE_C" or \
            image_lifecycle["base_sha256"] != main_obj["sha256"] or \
            image_lifecycle["unresolved_before"] != 203 or image_lifecycle["unresolved_after"] != 201 or \
            image_lifecycle["imports_resolved"] != ["audio_uart_lv_image_ctor_498bd0", "audio_uart_lv_image_dtor_498c6c"] or \
            image_lifecycle["imports_added"] != []:
        raise RuntimeError("Apollo Main LVGL image lifecycle binding changed")
    oracle = ROOT / image_lifecycle["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != image_lifecycle["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main LVGL image lifecycle oracle changed")
    file_checked(image_lifecycle["source"], image_lifecycle["source_sha256"])
    main_obj = file_checked(image_lifecycle["linked_object"], image_lifecycle["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 201 or any(name in actual for name in image_lifecycle["imports_resolved"]):
        raise RuntimeError("Apollo Main LVGL image lifecycle frontier changed")
    button_fade_path = G2 / "build/c-firmware/20261016/main-terminal-button-fade-callback-58c138/receipt.json"
    button_fade, button_fade_ref = receipt(button_fade_path)
    if button_fade["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_BUTTON_FADE_CALLBACK_C" or \
            button_fade["base_sha256"] != main_obj["sha256"] or \
            button_fade["unresolved_before"] != 201 or button_fade["unresolved_after"] != 200 or \
            button_fade["imports_resolved"] != ["audio_terminal_button_fade_callback_58c230"] or \
            button_fade["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal button fade callback binding changed")
    oracle = ROOT / button_fade["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != button_fade["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal button fade callback oracle changed")
    file_checked(button_fade["source"], button_fade["source_sha256"])
    main_obj = file_checked(button_fade["linked_object"], button_fade["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 200 or "audio_terminal_button_fade_callback_58c230" in actual:
        raise RuntimeError("Apollo Main Terminal button fade callback frontier changed")
    image_event_path = G2 / "build/c-firmware/20261016/main-lv-image-event-498c9c/receipt.json"
    image_event, image_event_ref = receipt(image_event_path)
    if image_event["status"] != "PASS_EXPERIMENTAL_MAIN_LV_IMAGE_EVENT_C" or \
            image_event["base_sha256"] != main_obj["sha256"] or \
            image_event["unresolved_before"] != 200 or image_event["unresolved_after"] != 201 or \
            image_event["imports_resolved"] != ["audio_uart_lv_image_event_498c9c"] or \
            image_event["imports_added"] != ["audio_uart_lv_get_click_area_4408b0", "audio_uart_lv_image_draw_498ec0"]:
        raise RuntimeError("Apollo Main LVGL image event binding changed")
    oracle = ROOT / image_event["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != image_event["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main LVGL image event oracle changed")
    file_checked(image_event["source"], image_event["source_sha256"])
    main_obj = file_checked(image_event["linked_object"], image_event["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 201 or "audio_uart_lv_image_event_498c9c" in actual:
        raise RuntimeError("Apollo Main LVGL image event frontier changed")
    click_area_path = G2 / "build/c-firmware/20261016/main-lv-click-area-4408b0/receipt.json"
    click_area, click_area_ref = receipt(click_area_path)
    if click_area["status"] != "PASS_EXPERIMENTAL_MAIN_LV_CLICK_AREA_C" or \
            click_area["base_sha256"] != main_obj["sha256"] or \
            click_area["unresolved_before"] != 201 or click_area["unresolved_after"] != 200 or \
            click_area["imports_resolved"] != ["audio_uart_lv_get_click_area_4408b0"] or \
            click_area["imports_added"] != []:
        raise RuntimeError("Apollo Main LVGL click area binding changed")
    oracle = ROOT / click_area["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != click_area["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main LVGL click area oracle changed")
    file_checked(click_area["source"], click_area["source_sha256"])
    main_obj = file_checked(click_area["linked_object"], click_area["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 200 or "audio_uart_lv_get_click_area_4408b0" in actual:
        raise RuntimeError("Apollo Main LVGL click area frontier changed")
    image_draw_path = G2 / "build/c-firmware/20261016/main-lv-image-draw-498ec0/receipt.json"
    image_draw, image_draw_ref = receipt(image_draw_path)
    if image_draw["status"] != "PASS_EXPERIMENTAL_MAIN_LV_IMAGE_DRAW_C" or \
            image_draw["base_sha256"] != main_obj["sha256"] or \
            image_draw["unresolved_before"] != 200 or image_draw["unresolved_after"] != 203 or \
            image_draw["imports_resolved"] != ["audio_uart_lv_image_draw_498ec0"] or \
            image_draw["imports_added"] != ["audio_uart_lv_draw_image_488a38", "audio_uart_lv_image_style_opa_498634", "audio_uart_lv_image_style_radius_49865e", "audio_uart_lv_obj_init_draw_image_452a34"]:
        raise RuntimeError("Apollo Main LVGL image draw binding changed")
    oracle = ROOT / image_draw["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != image_draw["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main LVGL image draw oracle changed")
    file_checked(image_draw["source"], image_draw["source_sha256"])
    main_obj = file_checked(image_draw["linked_object"], image_draw["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 203 or "audio_uart_lv_image_draw_498ec0" in actual:
        raise RuntimeError("Apollo Main LVGL image draw frontier changed")
    image_style_path = G2 / "build/c-firmware/20261016/main-lv-image-style-accessors-498634/receipt.json"
    image_style, image_style_ref = receipt(image_style_path)
    if image_style["status"] != "PASS_EXPERIMENTAL_MAIN_LV_IMAGE_STYLE_ACCESSORS_C" or \
            image_style["base_sha256"] != main_obj["sha256"] or \
            image_style["unresolved_before"] != 203 or image_style["unresolved_after"] != 201 or \
            image_style["imports_resolved"] != ["audio_uart_lv_image_style_opa_498634", "audio_uart_lv_image_style_radius_49865e"] or \
            image_style["imports_added"] != []:
        raise RuntimeError("Apollo Main LVGL image style accessors binding changed")
    oracle = ROOT / image_style["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != image_style["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main LVGL image style accessors oracle changed")
    file_checked(image_style["source"], image_style["source_sha256"])
    main_obj = file_checked(image_style["linked_object"], image_style["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 201 or any(name in actual for name in image_style["imports_resolved"]):
        raise RuntimeError("Apollo Main LVGL image style accessors frontier changed")
    image_dsc_path = G2 / "build/c-firmware/20261016/main-lv-image-dsc-init-452a34/receipt.json"
    image_dsc, image_dsc_ref = receipt(image_dsc_path)
    if image_dsc["status"] != "PASS_EXPERIMENTAL_MAIN_LV_IMAGE_DSC_INIT_C" or \
            image_dsc["base_sha256"] != main_obj["sha256"] or \
            image_dsc["unresolved_before"] != 201 or image_dsc["unresolved_after"] != 204 or \
            image_dsc["imports_resolved"] != ["audio_uart_lv_obj_init_draw_image_452a34"] or \
            image_dsc["imports_added"] != ["audio_uart_lv_style_image_blend_45260a", "audio_uart_lv_style_image_opa_4524a4", "audio_uart_lv_style_image_recolor_4524b0", "audio_uart_lv_style_image_recolor_opa_4524d0"]:
        raise RuntimeError("Apollo Main LVGL image descriptor initializer binding changed")
    oracle = ROOT / image_dsc["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != image_dsc["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main LVGL image descriptor initializer oracle changed")
    file_checked(image_dsc["source"], image_dsc["source_sha256"])
    main_obj = file_checked(image_dsc["linked_object"], image_dsc["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 204 or any(name in actual for name in image_dsc["imports_resolved"]):
        raise RuntimeError("Apollo Main LVGL image descriptor initializer frontier changed")
    image_fields_path = G2 / "build/c-firmware/20261016/main-lv-image-style-fields-4524a4/receipt.json"
    image_fields, image_fields_ref = receipt(image_fields_path)
    if image_fields["status"] != "PASS_EXPERIMENTAL_MAIN_LV_IMAGE_STYLE_FIELDS_C" or \
            image_fields["base_sha256"] != main_obj["sha256"] or \
            image_fields["unresolved_before"] != 204 or image_fields["unresolved_after"] != 200 or \
            image_fields["imports_resolved"] != ["audio_uart_lv_style_image_blend_45260a", "audio_uart_lv_style_image_opa_4524a4", "audio_uart_lv_style_image_recolor_4524b0", "audio_uart_lv_style_image_recolor_opa_4524d0"] or \
            image_fields["imports_added"] != []:
        raise RuntimeError("Apollo Main LVGL image style fields binding changed")
    oracle = ROOT / image_fields["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != image_fields["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main LVGL image style fields oracle changed")
    file_checked(image_fields["source"], image_fields["source_sha256"])
    main_obj = file_checked(image_fields["linked_object"], image_fields["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 200 or any(name in actual for name in image_fields["imports_resolved"]):
        raise RuntimeError("Apollo Main LVGL image style fields frontier changed")
    draw_scheduler_path = G2 / "build/c-firmware/20261016/main-lv-draw-image-488a38/receipt.json"
    draw_scheduler, draw_scheduler_ref = receipt(draw_scheduler_path)
    if draw_scheduler["status"] != "PASS_EXPERIMENTAL_MAIN_LV_DRAW_IMAGE_C" or \
            draw_scheduler["base_sha256"] != main_obj["sha256"] or \
            draw_scheduler["unresolved_before"] != 200 or draw_scheduler["unresolved_after"] != 199 or \
            draw_scheduler["imports_resolved"] != ["audio_uart_lv_draw_image_488a38"] or \
            draw_scheduler["imports_added"] != []:
        raise RuntimeError("Apollo Main LVGL draw-image scheduler binding changed")
    oracle = ROOT / draw_scheduler["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != draw_scheduler["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main LVGL draw-image scheduler oracle changed")
    file_checked(draw_scheduler["source"], draw_scheduler["source_sha256"])
    main_obj = file_checked(draw_scheduler["linked_object"], draw_scheduler["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 199 or any(name in actual for name in draw_scheduler["imports_resolved"]):
        raise RuntimeError("Apollo Main LVGL draw-image scheduler frontier changed")
    label_alias_path = G2 / "build/c-firmware/20261016/main-terminal-label-text-alias-49942e/receipt.json"
    label_alias, label_alias_ref = receipt(label_alias_path)
    if label_alias["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_LABEL_TEXT_ALIAS_C" or \
            label_alias["base_sha256"] != main_obj["sha256"] or \
            label_alias["unresolved_before"] != 199 or label_alias["unresolved_after"] != 198 or \
            label_alias["imports_resolved"] != ["audio_lv_anim_start_49942e"] or \
            label_alias["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal label-text alias binding changed")
    oracle = ROOT / label_alias["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != label_alias["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal label-text alias oracle changed")
    file_checked(label_alias["source"], label_alias["source_sha256"])
    main_obj = file_checked(label_alias["linked_object"], label_alias["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 198 or any(name in actual for name in label_alias["imports_resolved"]):
        raise RuntimeError("Apollo Main Terminal label-text alias frontier changed")
    label_fmt_path = G2 / "build/c-firmware/20261016/main-terminal-label-text-fmt-49954c/receipt.json"
    label_fmt, label_fmt_ref = receipt(label_fmt_path)
    if label_fmt["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_LABEL_TEXT_FMT_C" or \
            label_fmt["base_sha256"] != main_obj["sha256"] or \
            label_fmt["unresolved_before"] != 198 or label_fmt["unresolved_after"] != 198 or \
            label_fmt["imports_resolved"] != ["audio_lv_label_set_text_fmt_49954c"] or \
            label_fmt["imports_added"] != ["audio_uart_lv_label_vprintf_489ad2"]:
        raise RuntimeError("Apollo Main Terminal formatted label binding changed")
    oracle = ROOT / label_fmt["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != label_fmt["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal formatted label oracle changed")
    file_checked(label_fmt["source"], label_fmt["source_sha256"])
    main_obj = file_checked(label_fmt["linked_object"], label_fmt["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 198 or any(name in actual for name in label_fmt["imports_resolved"]):
        raise RuntimeError("Apollo Main Terminal formatted label frontier changed")
    label_vprintf_path = G2 / "build/c-firmware/20261016/main-lv-label-vprintf-489ad2/receipt.json"
    label_vprintf, label_vprintf_ref = receipt(label_vprintf_path)
    if label_vprintf["status"] != "PASS_EXPERIMENTAL_MAIN_LV_LABEL_VPRINTF_C" or \
            label_vprintf["base_sha256"] != main_obj["sha256"] or \
            label_vprintf["unresolved_before"] != 198 or label_vprintf["unresolved_after"] != 197 or \
            label_vprintf["imports_resolved"] != ["audio_uart_lv_label_vprintf_489ad2"] or \
            label_vprintf["imports_added"] != []:
        raise RuntimeError("Apollo Main LVGL formatted text allocator binding changed")
    oracle = ROOT / label_vprintf["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != label_vprintf["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main LVGL formatted text allocator oracle changed")
    file_checked(label_vprintf["source"], label_vprintf["source_sha256"])
    main_obj = file_checked(label_vprintf["linked_object"], label_vprintf["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 197 or any(name in actual for name in label_vprintf["imports_resolved"]):
        raise RuntimeError("Apollo Main LVGL formatted text allocator frontier changed")
    label_fatal_path = G2 / "build/c-firmware/20261016/main-label-fatal-paths/oracle-receipt.json"
    label_fatal, label_fatal_ref = receipt(label_fatal_path)
    if label_fatal["status"] != "PASS_EXPERIMENTAL_MAIN_LABEL_FATAL_PATHS_ORACLE" or \
            label_fatal["cases"] != 5 or \
            [item["path"] for item in label_fatal["sources"]] != [label_fmt["source"], label_vprintf["source"]]:
        raise RuntimeError("Apollo Main label fatal-path oracle changed")
    for item in label_fatal["sources"]:
        file_checked(item["path"], item["sha256"])
    clear_flag_alias_path = G2 / "build/c-firmware/20261016/main-terminal-clear-flag-alias-43dfa4/receipt.json"
    clear_flag_alias, clear_flag_alias_ref = receipt(clear_flag_alias_path)
    if clear_flag_alias["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_CLEAR_FLAG_ALIAS_C" or \
            clear_flag_alias["base_sha256"] != main_obj["sha256"] or \
            clear_flag_alias["unresolved_before"] != 197 or clear_flag_alias["unresolved_after"] != 196 or \
            clear_flag_alias["imports_resolved"] != ["audio_lv_obj_invalidate_43dfa4"] or \
            clear_flag_alias["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal clear-flag alias binding changed")
    oracle = ROOT / clear_flag_alias["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != clear_flag_alias["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal clear-flag alias oracle changed")
    file_checked(clear_flag_alias["source"], clear_flag_alias["source_sha256"])
    main_obj = file_checked(clear_flag_alias["linked_object"], clear_flag_alias["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 196 or any(name in actual for name in clear_flag_alias["imports_resolved"]):
        raise RuntimeError("Apollo Main Terminal clear-flag alias frontier changed")
    object_alias_path = G2 / "build/c-firmware/20261016/main-terminal-object-abi-aliases/receipt.json"
    object_alias, object_alias_ref = receipt(object_alias_path)
    if object_alias["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_OBJECT_ABI_ALIASES_C" or \
            object_alias["base_sha256"] != main_obj["sha256"] or \
            object_alias["unresolved_before"] != 196 or object_alias["unresolved_after"] != 191 or \
            object_alias["imports_resolved"] != ["audio_lv_object_call_43ded4", "audio_lv_object_call_441488", "audio_lv_object_call_450500", "audio_lv_object_release_44d7b8", "audio_lv_object_size_call_43f4c0"] or \
            object_alias["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal object ABI aliases binding changed")
    oracle = ROOT / object_alias["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != object_alias["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal object ABI aliases oracle changed")
    file_checked(object_alias["source"], object_alias["source_sha256"])
    main_obj = file_checked(object_alias["linked_object"], object_alias["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 191 or any(name in actual for name in object_alias["imports_resolved"]):
        raise RuntimeError("Apollo Main Terminal object ABI aliases frontier changed")
    animimage_path = G2 / "build/c-firmware/20261016/main-lv-animimage-597ea6/receipt.json"
    animimage, animimage_ref = receipt(animimage_path)
    if animimage["status"] != "PASS_EXPERIMENTAL_MAIN_LV_ANIMIMAGE_C" or \
            animimage["base_sha256"] != main_obj["sha256"] or \
            animimage["unresolved_before"] != 191 or animimage["unresolved_after"] != 187 or \
            animimage["imports_resolved"] != ["audio_lv_label_style_call_597ea6", "audio_lv_label_style_call_597ee0", "audio_lv_label_style_call_597f10", "audio_lv_label_style_call_597f52"] or \
            animimage["imports_added"] != []:
        raise RuntimeError("Apollo Main LVGL animimage binding changed")
    oracle = ROOT / animimage["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != animimage["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main LVGL animimage oracle changed")
    file_checked(animimage["source"], animimage["source_sha256"])
    main_obj = file_checked(animimage["linked_object"], animimage["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 187 or any(name in actual for name in animimage["imports_resolved"]):
        raise RuntimeError("Apollo Main LVGL animimage frontier changed")
    query_show_path = G2 / "build/c-firmware/20261016/main-terminal-query-notification-show-5e6548/receipt.json"
    query_show, query_show_ref = receipt(query_show_path)
    if query_show["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_NOTIFICATION_SHOW_C" or \
            query_show["base_sha256"] != main_obj["sha256"] or \
            query_show["unresolved_before"] != 187 or query_show["unresolved_after"] != 188 or \
            query_show["imports_resolved"] != ["audio_terminal_ui_action_5e6548"] or \
            query_show["imports_added"] != ["audio_terminal_counter_b_get_5973dc", "audio_terminal_query_visibility_5ec82a"]:
        raise RuntimeError("Apollo Main Terminal query-notification-show binding changed")
    oracle = ROOT / query_show["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != query_show["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal query-notification-show oracle changed")
    file_checked(query_show["source"], query_show["source_sha256"])
    main_obj = file_checked(query_show["linked_object"], query_show["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 188 or any(name in actual for name in query_show["imports_resolved"]):
        raise RuntimeError("Apollo Main Terminal query-notification-show frontier changed")
    counter_alias_path = G2 / "build/c-firmware/20261016/main-terminal-counter-b-alias-5973dc/receipt.json"
    counter_alias, counter_alias_ref = receipt(counter_alias_path)
    if counter_alias["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_COUNTER_B_ALIAS_C" or \
            counter_alias["base_sha256"] != main_obj["sha256"] or \
            counter_alias["unresolved_before"] != 188 or counter_alias["unresolved_after"] != 187 or \
            counter_alias["imports_resolved"] != ["audio_terminal_counter_b_get_5973dc"] or \
            counter_alias["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal counter-B alias binding changed")
    oracle = ROOT / counter_alias["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != counter_alias["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal counter-B alias oracle changed")
    file_checked(counter_alias["source"], counter_alias["source_sha256"])
    main_obj = file_checked(counter_alias["linked_object"], counter_alias["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 187 or any(name in actual for name in counter_alias["imports_resolved"]):
        raise RuntimeError("Apollo Main Terminal counter-B alias frontier changed")
    query_name_path = G2 / "build/c-firmware/20261016/main-terminal-query-session-name-5ec7f0/receipt.json"
    query_name, query_name_ref = receipt(query_name_path)
    if query_name["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_SESSION_NAME_C" or \
            query_name["base_sha256"] != main_obj["sha256"] or \
            query_name["unresolved_before"] != 187 or query_name["unresolved_after"] != 187 or \
            query_name["imports_resolved"] != [] or query_name["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal query session-name binding changed")
    oracle = ROOT / query_name["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != query_name["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal query session-name oracle changed")
    file_checked(query_name["source"], query_name["source_sha256"])
    main_obj = file_checked(query_name["linked_object"], query_name["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 187 or "audio_terminal_query_visibility_5ec82a" not in actual:
        raise RuntimeError("Apollo Main Terminal query session-name frontier changed")
    query_visibility_path = G2 / "build/c-firmware/20261016/main-terminal-query-visibility-5ec82a/receipt.json"
    query_visibility, query_visibility_ref = receipt(query_visibility_path)
    if query_visibility["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_VISIBILITY_C" or \
            query_visibility["base_sha256"] != main_obj["sha256"] or \
            query_visibility["unresolved_before"] != 187 or query_visibility["unresolved_after"] != 189 or \
            query_visibility["imports_resolved"] != ["audio_terminal_query_visibility_5ec82a"] or \
            query_visibility["imports_added"] != ["audio_terminal_query_root_5e4f54", "audio_uart_page_441180", "audio_uart_page_44119c"] or \
            not query_visibility["image_exact_bytes"]:
        raise RuntimeError("Apollo Main Terminal query visibility binding changed")
    oracle = ROOT / query_visibility["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != query_visibility["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal query visibility oracle changed")
    file_checked(query_visibility["source"], query_visibility["source_sha256"])
    file_checked(query_visibility["image_source"], query_visibility["image_source_sha256"])
    file_checked(query_visibility["image_object"], query_visibility["image_object_sha256"])
    main_obj = file_checked(query_visibility["linked_object"], query_visibility["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 189 or any(name in actual for name in query_visibility["imports_resolved"]):
        raise RuntimeError("Apollo Main Terminal query visibility frontier changed")
    query_style_path = G2 / "build/c-firmware/20261016/main-terminal-query-style-setters/receipt.json"
    query_style, query_style_ref = receipt(query_style_path)
    if query_style["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_STYLE_SETTERS_C" or \
            query_style["base_sha256"] != main_obj["sha256"] or \
            query_style["unresolved_before"] != 189 or query_style["unresolved_after"] != 187 or \
            query_style["imports_resolved"] != ["audio_uart_page_441180", "audio_uart_page_44119c"] or \
            query_style["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal query style binding changed")
    oracle = ROOT / query_style["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != query_style["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal query style oracle changed")
    file_checked(query_style["source"], query_style["source_sha256"])
    main_obj = file_checked(query_style["linked_object"], query_style["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 187 or any(name in actual for name in query_style["imports_resolved"]):
        raise RuntimeError("Apollo Main Terminal query style frontier changed")
    query_root_path = G2 / "build/c-firmware/20261016/main-terminal-query-root-5e4f54/receipt.json"
    query_root, query_root_ref = receipt(query_root_path)
    if query_root["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_QUERY_ROOT_C" or \
            query_root["base_sha256"] != main_obj["sha256"] or \
            query_root["unresolved_before"] != 187 or query_root["unresolved_after"] != 186 or \
            query_root["imports_resolved"] != ["audio_terminal_query_root_5e4f54"] or \
            query_root["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal query root binding changed")
    oracle = ROOT / query_root["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != query_root["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal query root oracle changed")
    file_checked(query_root["source"], query_root["source_sha256"])
    main_obj = file_checked(query_root["linked_object"], query_root["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 186 or any(name in actual for name in query_root["imports_resolved"]):
        raise RuntimeError("Apollo Main Terminal query root frontier changed")
    voice_start_path = G2 / "build/c-firmware/20261016/main-terminal-ui-action-voice-start-5e58ba/receipt.json"
    voice_start, voice_start_ref = receipt(voice_start_path)
    if voice_start["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_VOICE_START_C" or \
            voice_start["base_sha256"] != main_obj["sha256"] or \
            voice_start["unresolved_before"] != 186 or voice_start["unresolved_after"] != 186 or \
            voice_start["imports_resolved"] != ["audio_terminal_ui_action_5e58ba"] or \
            voice_start["imports_added"] != ["audio_terminal_ui_voice_prepare_5ebd0e"] or \
            not voice_start["image_exact_bytes"]:
        raise RuntimeError("Apollo Main Terminal voice-start binding changed")
    for key in ("oracle_receipt", "timer_oracle_receipt"):
        oracle = ROOT / voice_start[key]
        if hashlib.sha256(oracle.read_bytes()).hexdigest() != voice_start[key + "_sha256"]:
            raise RuntimeError("Apollo Main Terminal voice-start oracle changed")
    for key in ("source", "timer_source", "image_source", "action_object", "timer_object", "image_object"):
        file_checked(voice_start[key], voice_start[key + "_sha256"])
    main_obj = file_checked(voice_start["linked_object"], voice_start["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 186 or any(name in actual for name in voice_start["imports_resolved"]):
        raise RuntimeError("Apollo Main Terminal voice-start frontier changed")
    voice_prepare_path = G2 / "build/c-firmware/20261016/main-terminal-ui-voice-prepare-5ebd0e/receipt.json"
    voice_prepare, voice_prepare_ref = receipt(voice_prepare_path)
    if voice_prepare["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_VOICE_PREPARE_C" or \
            voice_prepare["base_sha256"] != main_obj["sha256"] or \
            voice_prepare["unresolved_before"] != 186 or voice_prepare["unresolved_after"] != 187 or \
            voice_prepare["imports_resolved"] != ["audio_terminal_ui_voice_prepare_5ebd0e"] or \
            voice_prepare["imports_added"] != ["audio_terminal_voice_anim_create_597e90", "audio_terminal_voice_style_200014e8"]:
        raise RuntimeError("Apollo Main Terminal voice-prepare binding changed")
    for key in ("oracle_receipt", "wrapper_oracle_receipt"):
        oracle = ROOT / voice_prepare[key]
        if hashlib.sha256(oracle.read_bytes()).hexdigest() != voice_prepare[key + "_sha256"]:
            raise RuntimeError("Apollo Main Terminal voice-prepare oracle changed")
    for key in ("source", "wrapper_source", "object", "wrapper_object"):
        file_checked(voice_prepare[key], voice_prepare[key + "_sha256"])
    main_obj = file_checked(voice_prepare["linked_object"], voice_prepare["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 187 or any(name in actual for name in voice_prepare["imports_resolved"]):
        raise RuntimeError("Apollo Main Terminal voice-prepare frontier changed")
    voice_factory_path = G2 / "build/c-firmware/20261016/main-terminal-voice-anim-factory-597e90/receipt.json"
    voice_factory, voice_factory_ref = receipt(voice_factory_path)
    if voice_factory["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_VOICE_ANIM_FACTORY_C" or \
            voice_factory["base_sha256"] != main_obj["sha256"] or \
            voice_factory["unresolved_before"] != 187 or voice_factory["unresolved_after"] != 187 or \
            voice_factory["imports_resolved"] != ["audio_terminal_voice_anim_create_597e90"] or \
            voice_factory["imports_added"] != ["audio_terminal_voice_anim_ctor_597fae"]:
        raise RuntimeError("Apollo Main Terminal voice animation factory binding changed")
    oracle = ROOT / voice_factory["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != voice_factory["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal voice animation factory oracle changed")
    file_checked(voice_factory["source"], voice_factory["source_sha256"])
    main_obj = file_checked(voice_factory["linked_object"], voice_factory["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 187 or any(name in actual for name in voice_factory["imports_resolved"]):
        raise RuntimeError("Apollo Main Terminal voice animation factory frontier changed")
    voice_anim_path = G2 / "build/c-firmware/20261016/main-terminal-voice-anim-children/receipt.json"
    voice_anim, voice_anim_ref = receipt(voice_anim_path)
    if voice_anim["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_VOICE_ANIM_CHILDREN_C" or \
            voice_anim["base_sha256"] != main_obj["sha256"] or \
            voice_anim["unresolved_before"] != 187 or voice_anim["unresolved_after"] != 186 or \
            voice_anim["imports_resolved"] != ["audio_terminal_voice_anim_ctor_597fae"] or \
            voice_anim["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal voice animation children binding changed")
    for key in ("constructor_oracle_receipt", "callback_oracle_receipt"):
        oracle = ROOT / voice_anim[key]
        if hashlib.sha256(oracle.read_bytes()).hexdigest() != voice_anim[key + "_sha256"]:
            raise RuntimeError("Apollo Main Terminal voice animation child oracle changed")
    for key in ("constructor_source", "callback_source", "constructor_object", "callback_object"):
        file_checked(voice_anim[key], voice_anim[key + "_sha256"])
    main_obj = file_checked(voice_anim["linked_object"], voice_anim["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 186 or any(name in actual for name in voice_anim["imports_resolved"]):
        raise RuntimeError("Apollo Main Terminal voice animation children frontier changed")
    voice_frames_path = G2 / "build/c-firmware/20261016/main-terminal-voice-frames-200014e8/receipt.json"
    voice_frames, voice_frames_ref = receipt(voice_frames_path)
    if voice_frames["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_VOICE_FRAMES_C" or \
            voice_frames["base_sha256"] != main_obj["sha256"] or \
            voice_frames["unresolved_before"] != 186 or voice_frames["unresolved_after"] != 185 or \
            voice_frames["imports_resolved"] != ["audio_terminal_voice_style_200014e8"] or \
            voice_frames["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal voice frame binding changed")
    oracle = ROOT / voice_frames["oracle_receipt"]
    if hashlib.sha256(oracle.read_bytes()).hexdigest() != voice_frames["oracle_receipt_sha256"]:
        raise RuntimeError("Apollo Main Terminal voice frame oracle changed")
    for key in ("source", "linker", "object"):
        file_checked(voice_frames[key], voice_frames[key + "_sha256"])
    main_obj = file_checked(voice_frames["linked_object"], voice_frames["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 185 or any(name in actual for name in voice_frames["imports_resolved"]):
        raise RuntimeError("Apollo Main Terminal voice frame frontier changed")
    voice_stop_path = G2 / "build/c-firmware/20261016/main-terminal-ui-action-voice-stop-5e598a/receipt.json"
    voice_stop, voice_stop_ref = receipt(voice_stop_path)
    if voice_stop["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_VOICE_STOP_C" or \
            voice_stop["base_sha256"] != main_obj["sha256"] or \
            voice_stop["unresolved_before"] != 185 or voice_stop["unresolved_after"] != 184 or \
            voice_stop["imports_resolved"] != ["audio_terminal_ui_action_5e598a"] or \
            voice_stop["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal voice-stop binding changed")
    for source, digest in zip(voice_stop["sources"], voice_stop["source_sha256"]):
        file_checked(source, digest)
    for oracle_path, digest in zip(voice_stop["oracle_receipts"], voice_stop["oracle_receipt_sha256"]):
        file_checked(oracle_path, digest)
    main_obj = file_checked(voice_stop["linked_object"], voice_stop["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 184 or "audio_terminal_ui_action_5e598a" in actual:
        raise RuntimeError("Apollo Main Terminal voice-stop frontier changed")
    asr_final_path = G2 / "build/c-firmware/20261016/main-terminal-ui-action-asr-final-5e5aae/receipt.json"
    asr_final, asr_final_ref = receipt(asr_final_path)
    if asr_final["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_ASR_FINAL_C" or \
            asr_final["base_sha256"] != main_obj["sha256"] or \
            asr_final["unresolved_before"] != 184 or asr_final["unresolved_after"] != 184 or \
            asr_final["imports_resolved"] != ["audio_terminal_ui_action_5e5aae"] or \
            asr_final["imports_added"] != ["audio_terminal_ui_result_area_prepare_5ebff8"]:
        raise RuntimeError("Apollo Main Terminal ASR-final binding changed")
    for source, digest in zip(asr_final["sources"], asr_final["source_sha256"]):
        file_checked(source, digest)
    for oracle_path, digest in zip(asr_final["oracle_receipts"], asr_final["oracle_receipt_sha256"]):
        file_checked(oracle_path, digest)
    main_obj = file_checked(asr_final["linked_object"], asr_final["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 184 or "audio_terminal_ui_action_5e5aae" in actual or \
            "audio_terminal_ui_result_area_prepare_5ebff8" not in actual:
        raise RuntimeError("Apollo Main Terminal ASR-final frontier changed")
    result_area_path = G2 / "build/c-firmware/20261016/main-terminal-result-area-5ebff8/receipt.json"
    result_area, result_area_ref = receipt(result_area_path)
    if result_area["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_RESULT_AREA_C" or \
            result_area["base_sha256"] != main_obj["sha256"] or \
            result_area["unresolved_before"] != 184 or result_area["unresolved_after"] != 183 or \
            result_area["imports_resolved"] != ["audio_terminal_ui_result_area_prepare_5ebff8"] or \
            result_area["imports_added"] != [] or not result_area["icon_exact_bytes"]:
        raise RuntimeError("Apollo Main Terminal result-area binding changed")
    for key in ("source", "icon_source", "source_object", "icon_object"):
        file_checked(result_area[key], result_area[key + "_sha256"])
    file_checked(result_area["oracle_receipt"], result_area["oracle_receipt_sha256"])
    main_obj = file_checked(result_area["linked_object"], result_area["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 183 or "audio_terminal_ui_result_area_prepare_5ebff8" in actual:
        raise RuntimeError("Apollo Main Terminal result-area frontier changed")
    input_confirm_path = G2 / "build/c-firmware/20261016/main-terminal-ui-action-input-confirm-5e5bc6/receipt.json"
    input_confirm, input_confirm_ref = receipt(input_confirm_path)
    if input_confirm["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_INPUT_CONFIRM_C" or \
            input_confirm["base_sha256"] != main_obj["sha256"] or \
            input_confirm["unresolved_before"] != 183 or input_confirm["unresolved_after"] != 182 or \
            input_confirm["imports_resolved"] != ["audio_terminal_ui_action_5e5bc6"] or \
            input_confirm["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal input-confirm binding changed")
    for source, digest in zip(input_confirm["sources"], input_confirm["source_sha256"]):
        file_checked(source, digest)
    for oracle_path, digest in zip(input_confirm["oracle_receipts"], input_confirm["oracle_receipt_sha256"]):
        file_checked(oracle_path, digest)
    main_obj = file_checked(input_confirm["linked_object"], input_confirm["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 182 or "audio_terminal_ui_action_5e5bc6" in actual:
        raise RuntimeError("Apollo Main Terminal input-confirm frontier changed")
    input_cancel_path = G2 / "build/c-firmware/20261016/main-terminal-ui-action-input-cancel-5e5cb0/receipt.json"
    input_cancel, input_cancel_ref = receipt(input_cancel_path)
    if input_cancel["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_INPUT_CANCEL_C" or \
            input_cancel["base_sha256"] != main_obj["sha256"] or \
            input_cancel["unresolved_before"] != 182 or input_cancel["unresolved_after"] != 181 or \
            input_cancel["imports_resolved"] != ["audio_terminal_ui_action_5e5cb0"] or \
            input_cancel["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal input-cancel binding changed")
    file_checked(input_cancel["source"], input_cancel["source_sha256"])
    file_checked(input_cancel["oracle_receipt"], input_cancel["oracle_receipt_sha256"])
    file_checked(input_cancel["object"], input_cancel["object_sha256"])
    main_obj = file_checked(input_cancel["linked_object"], input_cancel["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 181 or "audio_terminal_ui_action_5e5cb0" in actual:
        raise RuntimeError("Apollo Main Terminal input-cancel frontier changed")
    asr_fail_path = G2 / "build/c-firmware/20261016/main-terminal-ui-action-asr-fail-5e5de0/receipt.json"
    asr_fail, asr_fail_ref = receipt(asr_fail_path)
    if asr_fail["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_ASR_FAIL_C" or \
            asr_fail["base_sha256"] != main_obj["sha256"] or \
            asr_fail["unresolved_before"] != 181 or asr_fail["unresolved_after"] != 180 or \
            asr_fail["imports_resolved"] != ["audio_terminal_ui_action_5e5de0"] or \
            asr_fail["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal ASR-fail binding changed")
    file_checked(asr_fail["source"], asr_fail["source_sha256"])
    file_checked(asr_fail["oracle_receipt"], asr_fail["oracle_receipt_sha256"])
    file_checked(asr_fail["object"], asr_fail["object_sha256"])
    main_obj = file_checked(asr_fail["linked_object"], asr_fail["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 180 or "audio_terminal_ui_action_5e5de0" in actual:
        raise RuntimeError("Apollo Main Terminal ASR-fail frontier changed")
    agent_reset_path = G2 / "build/c-firmware/20261016/main-terminal-ui-action-agent-reset-5e5ed4/receipt.json"
    agent_reset, agent_reset_ref = receipt(agent_reset_path)
    if agent_reset["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_AGENT_RESET_C" or \
            agent_reset["base_sha256"] != main_obj["sha256"] or \
            agent_reset["unresolved_before"] != 180 or agent_reset["unresolved_after"] != 179 or \
            agent_reset["imports_resolved"] != ["audio_terminal_ui_action_5e5ed4"] or \
            agent_reset["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal agent-reset binding changed")
    file_checked(agent_reset["source"], agent_reset["source_sha256"])
    file_checked(agent_reset["oracle_receipt"], agent_reset["oracle_receipt_sha256"])
    file_checked(agent_reset["object"], agent_reset["object_sha256"])
    main_obj = file_checked(agent_reset["linked_object"], agent_reset["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 179 or "audio_terminal_ui_action_5e5ed4" in actual:
        raise RuntimeError("Apollo Main Terminal agent-reset frontier changed")
    agent_interrupt_path = G2 / "build/c-firmware/20261016/main-terminal-ui-action-agent-interrupt-5e7068/receipt.json"
    agent_interrupt, agent_interrupt_ref = receipt(agent_interrupt_path)
    if agent_interrupt["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_AGENT_INTERRUPT_C" or \
            agent_interrupt["base_sha256"] != main_obj["sha256"] or \
            agent_interrupt["unresolved_before"] != 179 or agent_interrupt["unresolved_after"] != 178 or \
            agent_interrupt["imports_resolved"] != ["audio_terminal_ui_action_5e7068"] or \
            agent_interrupt["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal agent-interrupt binding changed")
    for source, digest in zip(agent_interrupt["sources"], agent_interrupt["source_sha256"]):
        file_checked(source, digest)
    for oracle_path, digest in zip(agent_interrupt["oracle_receipts"], agent_interrupt["oracle_receipt_sha256"]):
        file_checked(oracle_path, digest)
    main_obj = file_checked(agent_interrupt["linked_object"], agent_interrupt["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 178 or "audio_terminal_ui_action_5e7068" in actual:
        raise RuntimeError("Apollo Main Terminal agent-interrupt frontier changed")
    session_status_path = G2 / "build/c-firmware/20261016/main-terminal-ui-action-session-status-5e6018/receipt.json"
    session_status, session_status_ref = receipt(session_status_path)
    if session_status["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_SESSION_STATUS_C" or \
            session_status["base_sha256"] != main_obj["sha256"] or \
            session_status["unresolved_before"] != 178 or session_status["unresolved_after"] != 177 or \
            session_status["imports_resolved"] != ["audio_terminal_ui_action_5e6018"] or \
            session_status["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal session-status binding changed")
    file_checked(session_status["source"], session_status["source_sha256"])
    file_checked(session_status["oracle_receipt"], session_status["oracle_receipt_sha256"])
    file_checked(session_status["object"], session_status["object_sha256"])
    main_obj = file_checked(session_status["linked_object"], session_status["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 177 or "audio_terminal_ui_action_5e6018" in actual:
        raise RuntimeError("Apollo Main Terminal session-status frontier changed")
    agent_done_path = G2 / "build/c-firmware/20261016/main-terminal-ui-action-agent-done-5e6268/receipt.json"
    agent_done, agent_done_ref = receipt(agent_done_path)
    if agent_done["status"] != "PASS_EXPERIMENTAL_MAIN_TERMINAL_AGENT_DONE_C" or \
            agent_done["base_sha256"] != main_obj["sha256"] or \
            agent_done["unresolved_before"] != 177 or agent_done["unresolved_after"] != 176 or \
            agent_done["imports_resolved"] != ["audio_terminal_ui_action_5e6268"] or \
            agent_done["imports_added"] != []:
        raise RuntimeError("Apollo Main Terminal agent-done binding changed")
    file_checked(agent_done["source"], agent_done["source_sha256"])
    file_checked(agent_done["oracle_receipt"], agent_done["oracle_receipt_sha256"])
    file_checked(agent_done["object"], agent_done["object_sha256"])
    main_obj = file_checked(agent_done["linked_object"], agent_done["linked_sha256"])
    actual = undefined(ROOT / main_obj["path"])
    if len(actual) != 176 or "audio_terminal_ui_action_5e6268" in actual:
        raise RuntimeError("Apollo Main Terminal agent-done frontier changed")
    images["apollo_main"] = {
        "receipt": main_ref, "candidate": main_obj,
        "prior_dm_registry_extent_gate": registry_ref,
        "dm_registry_storage": storage_ref,
        "dm_connection_pair_storage": pair_ref,
        "dm_stack_interface": stack_ref,
        "dm_dispatch_scan_stop": scan_ref,
        "dm_dispatch_scan_stop_wrapper": wrapper_ref,
        "dm_stack_msg_handler": msg_ref,
        "dm_dispatch_4d2544": forward_ref,
        "dm_stack_reset_536918": reset_ref,
        "dm_stack_hci_handler_53694c": hci_ref,
        "dm_stack_hci_scan_complete_5368b6": complete_ref,
        "dm_dispatch_scan_start_536820": scan_start_ref,
        "dm_sec_hci_handler_4d2364": sec_ref,
        "dm_sec_lesc_neg_ltk": lesc_ref,
        "hci_ltk_reply_52b2ce": ltk_ref,
        "smp_encrypt_ind_537be6": encrypt_ref,
        "smp_get_stk_537c4c": stk_ref,
        "dm_sec_interface_78a898": sec_interface_ref,
        "dm_phy_interface_78a85c": phy_interface_ref,
        "dm_lesc_interface_78a8a4": lesc_interface_ref,
        "dm_priv_aes_interface_78a874": priv_aes_interface_ref,
        "mapped_mram_records_7ff000": mram_ref,
        "dm_priv_interface_78a868": priv_interface_ref,
        "hci_addr_resolution_enable_52b7f6": addr_enable_ref,
        "hci_privacy_commands_52b744": hci_priv_ref,
        "dm_dev_priv_forward_4b2ea6": dev_priv_ref,
        "dm_adv_reset_4ba45c": adv_reset_ref,
        "dm_adv_msg_4ba6ac": adv_msg_ref,
        "hci_adv_commands_52b3b0": hci_adv_ref,
        "dm_adv_config_lower_4b9a80": adv_config_ref,
        "dm_adv_control_extent_34": adv_extent_ref,
        "dm_adv_hci_4ba4b0": adv_hci_ref,
        "dm_adv_gen_conn_4b310a": adv_gen_ref,
        "dm_dev_pass_hci_conn_4d29c2": dev_conn_ref,
        "mapped_bootloader_flag_7fe000": flag_ref,
        "als_sync_registry_4ae73c": als_ref,
        "display_manager_state_table_776a3c": display_table_ref,
        "tracepoint_registry_5eeec4": tracepoint_ref,
        "tracepoint_ble_data_5ee8bc": trace_ble_ref,
        "tracepoint_decode_ram_2037b9c0": trace_ram_ref,
        "tracepoint_delete_all_5ee7b4": delete_all_ref,
        "tracepoint_reply_ram_2037bbc8": reply_ram_ref,
        "tracepoint_reply_routing_5ee134": reply_route_ref,
        "tracepoint_send_reply_5edfd8_5ee066": send_reply_ref,
        "tracepoint_encoder_5eded0": encoder_ref,
        "tracepoint_pb_descriptor_77cd84": trace_desc_ref,
        "tracepoint_delete_file_5ee488": trace_delete_ref,
        "tracepoint_path_resolver_5eddf6": trace_resolve_ref,
        "tracepoint_sequence_parser_5edaf0": trace_parse_ref,
        "tracepoint_filename_validator_5ede30": trace_validate_ref,
        "tracepoint_path_formatter_5edba2": trace_format_ref,
        "tracepoint_active_file_47e06a": trace_active_ref,
        "tracepoint_unlink_facade_47498c": trace_unlink_ref,
        "file_errno_location_439cc4": file_errno_ref,
        "file_lfs_remove_wrapper_4cfa76": lfs_remove_ref,
        "file_lfs_remove_core_4ce4dc": lfs_remove_core_ref,
        "file_lfs_dir_drop_4cc5a2": lfs_dir_drop_ref,
        "tracepoint_sorted_file_inventory_5edbb0": trace_inventory_ref,
        "tracepoint_request_file_name_5ee1f8": request_ref,
        "tracepoint_scan_files_5edc5a": scan_ref,
        "tracepoint_file_size_5edb68": file_size_ref,
        "tracepoint_prepare_pull_48ec9e": prepare_ref,
        "tracepoint_reset_pull_478110": reset_ref,
        "tracepoint_dir_facade_474b02": dir_facade_ref,
        "tracepoint_pull_initialize_47e1ec": pull_init_ref,
        "tracepoint_pull_ready_48eb90": pull_ready_ref,
        "tracepoint_pull_complete_47e220": pull_complete_ref,
        "tracepoint_pull_write_batch_47e178": pull_write_ref,
        "tracepoint_reopen_pending_file_47e144": reopen_ref,
        "tracepoint_format_pull_path_47de0a": pull_path_format_ref,
        "tracepoint_open_new_file_47e0c8": open_new_ref,
        "tracepoint_tpf1_header_48ed00": header_ref,
        "tracepoint_version_47dd08": version_ref,
        "tracepoint_trim_old_files_47e090": trim_ref,
        "tracepoint_list_files_47deb4": listing_ref,
        "tracepoint_parse_file_entry_47de18": entry_parser_ref,
        "tracepoint_write_state_47df28": state_write_ref,
        "tracepoint_pull_backend_init_47dfec": backend_init_ref,
        "tracepoint_file_size_47de7a": pull_size_ref,
        "tracepoint_read_state_47df8a": state_read_ref,
        "tracepoint_storage_mkdir_474a76": mkdir_ref,
        "file_lfs_mkdir_4cfc5c": lfs_mkdir_ref,
        "tracepoint_file_open_474550": file_open_ref,
        "tracepoint_file_sync_474910": file_sync_ref,
        "file_lfs_sync_4cfb08": lfs_sync_ref,
        "tracepoint_file_write_474682": file_write_ref,
        "file_lfs_mkdir_core_4cd3aa": mkdir_core_ref,
        "tracepoint_delete_all_files_5ee650": delete_all_files_ref,
        "setting_common_data_4668ae": setting_common_ref,
        "setting_data_recv_466976": setting_recv_ref,
        "setting_response_49b900": setting_response_ref,
        "setting_response_encode_49b3d4": setting_encoder_ref,
        "setting_local_response_49ba58": setting_local_ref,
        "setting_local_response_encode_49b7c4": setting_local_encoder_ref,
        "setting_parse_49b1f8": setting_parse_ref,
        "setting_dispatch_466abc": setting_dispatch_ref,
        "setting_type5_467134": setting_type5_ref,
        "wear_detect_enable_49eb1e": wear_enable_ref,
        "wear_detect_status_49ebb6": wear_status_ref,
        "onboarding_start_46805a": onboarding_start_ref,
        "wear_child_502bf0": wear_wrapper_ref,
        "wear_child_51308a": wear_request_ref,
        "settings_input_check_46b0ec": settings_input_ref,
        "setting_type6_46713e": setting_type6_ref,
        "setting_type8_4671a2": setting_type8_ref,
        "setting_type9_467206": setting_type9_ref,
        "setting_display_start_466890": setting_display_start_ref,
        "dashboard_auto_close_reset_49c0dc": dashboard_reset_ref,
        "setting_coordinates_466e1c_466ea2": setting_coordinates_ref,
        "setting_type12_467c34": setting_type12_ref,
        "gesture_apptype_46658e": gesture_apptype_ref,
        "setting_type10_467308": setting_type10_ref,
        "setting_brightness_refresh_46c18c": brightness_refresh_ref,
        "setting_manual_brightness_46c1c8": manual_brightness_ref,
        "als_manual_brightness_4ae81c": als_manual_ref,
        "als_manual_recalculate_4adcd8": als_recalculate_ref,
        "als_manual_target_4ade36": als_target_ref,
        "als_curve_first_percent_4ad9e2": als_curve_ref,
        "als_manual_target_scale_4addb6": als_target_scale_ref,
        "setting_type1_brightness_466bec": setting_type1_ref,
        "setting_type4_head_up_466f28": setting_type4_ref,
        "setting_head_up_configure_46c524": head_up_config_ref,
        "hub_parameter_config_4a6e3c": hub_parameter_ref,
        "hub_semantic_motion_period_4a4ec0": hub_period_ref,
        "hub_imu_accel_config_4a52a2": hub_imu_ref,
        "hub_semantic_motion_threshold_4a4e8c": hub_threshold_ref,
        "display_deinit_force_47432c": deinit_ref,
        "display_init_force_474100": init_ref,
        "onboarding_wear_notify_47e320": wear_notify_ref,
        "onboarding_event_encode_4a8368": event_encode_ref,
        "silent_mode_set_from_app_46921c": silent_app_ref,
        "sync_send_to_both_ext_464f76": send_both_ref,
        "setting_dominant_hand_467540": dominant_ref,
        "ring_address_is_unset_4a26e8": ring_unset_ref,
        "ring_connect_policy_on_hand_49f15a": ring_policy_ref,
        "ring_policy_get_state_49f05c": ring_get_ref,
        "ble_master_set_target_hand_4a2068": master_target_ref,
        "ble_master_hand_changed_4a2948": hand_changed_ref,
        "ble_peer_ring_status_47d8f0": peer_ring_ref,
        "ble_master_reset_scene_pending_4a2658": scene_pending_ref,
        "ble_master_begin_failure_notify_4a1546": begin_notify_ref,
        "ring_policy_cancel_connect_timeout_49f5f8": cancel_timeout_ref,
        "ring_policy_schedule_timeouts_49f4a8_49f552": schedule_timeouts_ref,
        "system_close_common_data_469d48": system_close_ref,
        "system_close_active_app_get_443504": active_app_ref,
        "production_test_screen_event_5cf7f2": production_ref,
        "lv_color_make_441068": color_ref,
        "gray_screen_event_5cf67e": gray_ref,
        "test_screen_registry_context_min": test_context_ref,
        "distortion_screen_event_5cf330": distortion_ref,
        "distortion_style_wrappers": distortion_style_ref,
        "distortion_screen_closure": distortion_closure_ref,
        "legal_regulatory_event_5bf7b8": legal_ref,
        "legal_fade_in_58c238": legal_fade_ref,
        "legal_fade_helpers": legal_helpers_ref,
        "legal_regulatory_chain": legal_chain_ref,
        "legal_page_helpers": legal_page_helpers_ref,
        "legal_assets": legal_assets_ref,
        "legal_assets_bound": legal_assets_bound_ref,
        "legal_page_builder_5bf332": legal_builder_ref,
        "legal_page_builder_bound": legal_builder_bound_ref,
        "align_to_43f6d6": align_oracle_ref,
        "align_to_bound": align_bound_ref,
        "even_ai_common_data_4e2976": even_ai_oracle_ref,
        "even_ai_common_data_bound": even_ai_bound_ref,
        "even_ai_prepare_4e1f7c": even_ai_prepare_oracle_ref,
        "even_ai_prepare_bound": even_ai_prepare_bound_ref,
        "os_mutex_new_44971c": mutex_oracle_ref,
        "os_mutex_new_bound": mutex_bound_ref,
        "os_mutex_alloc_wrappers_4416d6": alloc_wrappers_oracle_ref,
        "os_mutex_alloc_wrappers_bound": alloc_wrappers_bound_ref,
        "os_mutex_register_4416b8": mutex_register_oracle_ref,
        "os_mutex_register_bound": mutex_register_bound_ref,
        "os_irq_context_44900e": irq_oracle_ref,
        "os_irq_context_bound": irq_bound_ref,
        "os_scheduler_state_4558a4": scheduler_oracle_ref,
        "os_scheduler_state_bound": scheduler_bound_ref,
        "os_interrupt_mask_5fa0a4": mask_oracle_ref,
        "os_interrupt_mask_bound": mask_bound_ref,
        "os_queue_create_cores_4415ca": queue_cores_oracle_ref,
        "os_queue_create_cores_bound": queue_cores_bound_ref,
        "os_queue_initialize_441696": queue_init_oracle_ref,
        "os_queue_initialize_bound": queue_init_bound_ref,
        "os_queue_reset_441516": queue_reset_oracle_ref,
        "os_queue_reset_bound": queue_reset_bound_ref,
        "os_list_initialize_45607c": list_init_oracle_ref,
        "os_list_initialize_bound": list_init_bound_ref,
        "even_ai_frame_chain_bound": even_ai_chain_ref,
        "even_ai_ram_state_bound": even_ai_ram_ref,
        "os_scheduler_state_ram_bound": scheduler_ram_ref,
        "dashboard_layout_current_ram_bound": dashboard_ram_ref,
        "efs_transfer_state_ram_bound": efs_ram_ref,
        "ble_flash_staging_ram_bound": flash_staging_ref,
        "battery_callback_manager_ram_bound": battery_manager_ref,
        "ble_flash_callbacks_ram_bound": ble_callbacks_ref,
        "tpl_response_buffer_ram_bound": tpl_buffer_ref,
        "tpl_timeout_ids_ram_bound": tpl_timeout_ref,
        "tpl_service_row0_ram_bound": tpl_row_ref,
        "even_ai_local_decode_bound": local_decode_ref,
        "even_ai_notify_encoders_bound": notify_ref,
        "even_ai_ready_ram_bound": ready_ram_ref,
        "even_ai_ready_simple_candidate_oracle": ready_simple_ref,
        "even_ai_ready_bound": ready_bound_ref,
        "even_ai_ready_accessors_bound": accessors_ref,
        "even_ai_common_timer_start_bound": timer_ref,
        "even_ai_common_timer_stop_bound": timer_stop_ref,
        "even_ai_init_text_stream_bound": text_init_ref,
        "text_stream_create_bound": text_create_ref,
        "text_stream_buffer_create_bound": text_buffer_ref,
        "file_heap_realloc_bound": heap_realloc_ref,
        "file_heap_ram_cells_bound": heap_ram_ref,
        "file_tlsf_pool_init_bound": pool_init_ref,
        "file_tlsf_backing_ram_bound": backing_ref,
        "file_redirect_init_bound": redirect_ref,
        "even_ai_stop_streaming_bound": stream_stop_ref,
        "text_stream_stop_pause_bound": stop_pause_ref,
        "text_stream_copy_bytes_bound": text_copy_ref,
        "text_stream_set_text_bound": set_text_ref,
        "text_stream_decision_helpers_bound": decision_ref,
        "text_stream_restart_bound": restart_ref,
        "text_stream_dispatch_bound": dispatch_ref,
        "text_stream_begin_bound": begin_ref,
        "text_stream_finish_bound": finish_ref,
        "text_stream_schedule_bound": schedule_ref,
        "text_stream_tick_bound": tick_ref,
        "even_ai_app_acquire_bound": app_acquire_ref,
        "audio_app_setup_children_bound": app_setup_ref,
        "audio_app_control_and_open_bound": app_control_ref,
        "audio_app_hardware_core_bound": hardware_core_ref,
        "audio_app_hardware_indices_bound": hardware_indices_ref,
        "even_ai_sync_remote_bound": sync_remote_ref,
        "even_ai_ancc_display_clear_bound": ancc_display_ref,
        "even_ai_ancc_display_send_bound": ancc_send_ref,
        "even_ai_ancc_state_sync_bound": ancc_state_ref,
        "even_ai_display_ctrl_bound": display_ctrl_ref,
        "message_notify_common_bound": message_notify_ref,
        "message_notify_frame_bound": message_frame_ref,
        "message_notify_whitelist_check_bound": whitelist_check_ref,
        "message_notify_whitelist_ctrl_bound": whitelist_ctrl_ref,
        "message_notify_ctrl_bound": notify_ctrl_ref,
        "message_notify_tx_common_bound": notify_tx_common_ref,
        "message_notify_tx_ctrl_bound": notify_tx_ctrl_ref,
        "message_notify_tx_whitelist_ctrl_bound": notify_tx_whitelist_ref,
        "message_notify_tx_whitelist_check_bound": notify_tx_check_ref,
        "tracepoint_ready_word_extent_bound": ready_word_ref,
        "tracepoint_slave_file_list_bound": slave_file_list_ref,
        "fault_lookup_overrun_bound": fault_lookup_ref,
        "terminal_event_names_ram_bound": terminal_names_ref,
        "terminal_ui_event_bound": terminal_ui_ref,
        "terminal_ui_exit_sync_bound": terminal_exit_ref,
        "terminal_ui_stop_bound": terminal_stop_ref,
        "terminal_ui_stop_result_cleanup_bound": terminal_stop_e_ref,
        "terminal_ui_stop_timer_cleanup_bound": terminal_stop_a_ref,
        "terminal_ui_object_valid_bound": object_valid_ref,
        "terminal_ui_object_descendant_bound": descendant_ref,
        "terminal_list_anim_stop_bound": list_anim_ref,
        "terminal_ui_stop_timer_bound": timer_ref,
        "terminal_ui_stop_services_bcd_bound": services_bcd_ref,
        "terminal_display_state_notify_bound": display_notify_ref,
        "terminal_ui_start_bound": terminal_start_ref,
        "terminal_list_anim_init_bound": list_anim_init_ref,
        "terminal_ui_theme_bound": theme_ref,
        "terminal_ui_tick_bound": terminal_tick_ref,
        "terminal_ui_fsm_bound": terminal_fsm_ref,
        "terminal_ui_fsm_names_bound": fsm_names_ref,
        "terminal_ui_asr_actions_bound": asr_actions_ref,
        "terminal_ui_notification_restore_bound": notification_restore_ref,
        "terminal_ui_notification_exit_actions_bound": exit_actions_ref,
        "terminal_ui_payload_actions_bound": payload_actions_ref,
        "terminal_elapsed_text_bound": elapsed_text_ref,
        "terminal_control_flags_bound": control_flags_ref,
        "terminal_output_start_bound": output_start_ref,
        "terminal_processing_hide_bound": processing_hide_ref,
        "terminal_processing_prepare_bound": processing_prepare_ref,
        "terminal_elapsed_refresh_bound": elapsed_refresh_ref,
        "terminal_elapsed_clear_bound": elapsed_clear_ref,
        "terminal_set_output_bound": set_output_ref,
        "terminal_output_ram_bound": output_ram_ref,
        "terminal_label_style_bound": label_style_ref,
        "terminal_output_mode_bound": output_mode_ref,
        "terminal_query_dismiss_action_bound": dismiss_action_ref,
        "terminal_status_action_bound": status_action_ref,
        "terminal_reset_pair_actions_bound": reset_pair_ref,
        "terminal_reset_mode_display_bound": reset_children_ref,
        "terminal_mode_set_bound": mode_set_ref,
        "terminal_event_emit_bound": event_emit_ref,
        "terminal_event_type4_bound": event_type4_ref,
        "terminal_event_reset_list_bound": reset_list_ref,
        "terminal_event_refresh_view_staged": refresh_view_ref,
        "terminal_event_select_input_staged": select_input_ref,
        "terminal_event_apply_input_staged": apply_input_ref,
        "terminal_event_default_bound": event_default_ref,
        "terminal_event_select_input_bound": select_input_bound_ref,
        "terminal_event_apply_input_bound": apply_input_bound_ref,
        "terminal_event_refresh_view_bound": refresh_view_bound_ref,
        "terminal_recompute_offsets_bound": offsets_ref,
        "terminal_resource_items_bound": items_ref,
        "terminal_view_position_bound": view_pos_ref,
        "terminal_view_index_bound": view_index_ref,
        "terminal_position_index_bound": position_index_ref,
        "terminal_view_select_bound": view_select_ref,
        "terminal_view_row_bound": view_row_ref,
        "terminal_lv_existing_aliases_bound": lv_alias_ref,
        "terminal_item_height_bound": item_height_ref,
        "terminal_item_spacing_bound": item_spacing_ref,
        "terminal_row_bind_bound": row_bind_ref,
        "terminal_row_existing_aliases_bound": row_alias_ref,
        "terminal_row_children_bound": row_children_ref,
        "terminal_row_image_hint_bound": row_hint_ref,
        "terminal_event_type2_bound": event_type2_ref,
        "terminal_type2_children_bound": type2_children_ref,
        "terminal_event_type3_bound": type3_ref,
        "terminal_reset_first_bound": reset_first_ref,
        "terminal_reset_ancillary_bound": reset_ancillary_ref,
        "terminal_reset_preclear_bound": reset_preclear_ref,
        "even_ai_app_release_bound": app_release_ref,
        "terminal_reset_subtree_bound": reset_subtree_ref,
        "terminal_reset_subtree_children_bound": subtree_children_ref,
        "terminal_ui_restore_query_bound": restore_query_ref,
        "terminal_ui_action_5e57c6_bound": action_57c6_ref,
        "terminal_image_set_bound": image_set_ref,
        "terminal_display_status_alias_bound": display_status_ref,
        "terminal_ui_disconnect_actions_bound": disconnect_actions_ref,
        "terminal_ui_action_5e583c_bound": action_583c_ref,
        "terminal_output_style_assets_bound": style_assets_ref,
        "terminal_ui_action_5e54a2_bound": action_54a2_ref,
        "terminal_ui_action_5e576c_bound": action_576c_ref,
        "terminal_display_fallback_adapter_bound": fallback_adapter_ref,
        "terminal_ui_action_5e63b4_bound": action_63b4_ref,
        "terminal_ui_scroll_actions_bound": scroll_actions_ref,
        "terminal_ui_action_defer_query_bound": defer_query_ref,
        "terminal_notify_status_bound": notify_status_ref,
        "terminal_status_layout_bound": status_layout_ref,
        "terminal_status_publish_bound": status_publish_ref,
        "terminal_interrupt_confirm_scroll_bound": confirm_scroll_ref,
        "terminal_status_list_layout_bound": list_layout_ref,
        "terminal_interrupt_confirm_show_bound": confirm_show_ref,
        "terminal_interrupt_confirm_cancel_bound": confirm_cancel_ref,
        "terminal_new_session_success_bound": new_session_ref,
        "terminal_query_notification_switch_result_bound": query_switch_ref,
        "terminal_query_scroll_actions_bound": query_scroll_ref,
        "terminal_query_layout_bound": query_layout_ref,
        "terminal_query_items_style_bound": query_items_ref,
        "terminal_query_indicator_bound": query_indicator_ref,
        "terminal_session_list_scroll_bound": session_scroll_ref,
        "terminal_session_select_bound": session_select_ref,
        "terminal_session_focus_bound": session_focus_ref,
        "terminal_session_apply_bound": session_apply_ref,
        "terminal_session_row_style_bound": session_row_ref,
        "terminal_list_anim_add_bound": anim_add_ref,
        "terminal_list_anim_process_bound": anim_process_ref,
        "terminal_list_anim_new_prepare_bound": anim_prepare_ref,
        "terminal_list_anim_fade_start_bound": anim_fade_ref,
        "terminal_list_anim_path_bound": anim_path_ref,
        "terminal_session_row_visibility_bound": row_visibility_ref,
        "lv_image_class_bound": image_class_ref,
        "lv_image_lifecycle_bound": image_lifecycle_ref,
        "terminal_button_fade_callback_bound": button_fade_ref,
        "lv_image_event_bound": image_event_ref,
        "lv_click_area_bound": click_area_ref,
        "lv_image_draw_bound": image_draw_ref,
        "lv_image_style_accessors_bound": image_style_ref,
        "lv_image_dsc_init_bound": image_dsc_ref,
        "lv_image_style_fields_bound": image_fields_ref,
        "lv_draw_image_scheduler_bound": draw_scheduler_ref,
        "terminal_label_text_alias_bound": label_alias_ref,
        "terminal_label_text_fmt_bound": label_fmt_ref,
        "lv_label_vprintf_bound": label_vprintf_ref,
        "label_fatal_paths_oracle": label_fatal_ref,
        "terminal_clear_flag_alias_bound": clear_flag_alias_ref,
        "terminal_object_abi_aliases_bound": object_alias_ref,
        "lv_animimage_bound": animimage_ref,
        "terminal_query_notification_show_bound": query_show_ref,
        "terminal_counter_b_alias_bound": counter_alias_ref,
        "terminal_query_session_name_bound": query_name_ref,
        "terminal_query_visibility_bound": query_visibility_ref,
        "terminal_query_style_setters_bound": query_style_ref,
        "terminal_query_root_bound": query_root_ref,
        "terminal_voice_start_bound": voice_start_ref,
        "terminal_voice_prepare_bound": voice_prepare_ref,
        "terminal_voice_anim_factory_bound": voice_factory_ref,
        "terminal_voice_anim_children_bound": voice_anim_ref,
        "terminal_voice_frames_bound": voice_frames_ref,
        "terminal_voice_stop_bound": voice_stop_ref,
        "terminal_asr_final_bound": asr_final_ref,
        "terminal_result_area_bound": result_area_ref,
        "terminal_input_confirm_bound": input_confirm_ref,
        "terminal_input_cancel_bound": input_cancel_ref,
        "terminal_asr_fail_bound": asr_fail_ref,
        "terminal_agent_reset_bound": agent_reset_ref,
        "terminal_agent_interrupt_bound": agent_interrupt_ref,
        "terminal_session_status_bound": session_status_ref,
        "terminal_agent_done_bound": agent_done_ref,
        "settings_last_message_ram_extent": {"current_source_receipt": ram_ref, "selected_object_bytes": selected_ram_bytes, "required_minimum_bytes": 104, "integrated": selected_ram_bytes == 104},
        "unresolved_count": len(actual), "unresolved_symbols": actual,
        "source_complete": False, "full_payload_linked": False,
        "remaining_gate": ["176 current imports; agent-done FSM action is C-bound after 75 controlled stock comparisons. Session-status FSM action is C-bound after 1920 controlled stock comparisons. Agent-interrupt FSM action and its one-byte packet encoder are C-bound after 25 and 15 controlled stock comparisons. Agent-reset FSM action is C-bound after 75 controlled stock comparisons. ASR-failure FSM action is C-bound after 75 controlled stock comparisons. Input-cancel FSM action is C-bound after 150 controlled stock comparisons. Input-confirm FSM action and its two TD children are C-bound after 25, 216 and 60 controlled stock comparisons. Terminal result-area constructor 0x5ebff8 is C-bound after 48 controlled cases, with exact source-owned 16x16 icon bytes. Terminal voice-stop action and processing-label helper are C-bound after 100 and four controlled stock comparisons. ASR-final action and timeout-stop helper are C-bound after 150 and 15 controlled comparisons; Terminal query session-name lookup, visibility constructor, two LVGL style wrappers and root constructor are C-bound after 120, 32, 48 and 30 controlled cases, with exact source-owned icon bytes. Terminal voice-start action and timeout child are C-bound after 25 and 24 controlled cases with exact source-owned voice icon. Voice-prepare constructor, five style wrappers, animimage class/factory, constructor and frame callback are C-bound after 16, 80, 3, 12 and 36 controlled cases. The stock scatter-executed 19-frame voice style table at RAM 0x200014e8 and its exact 4864 pixel bytes are C-owned with a bounded placement fragment; complete main scatter/linker integration remains open. LVGL effects and final object graph remain open. Terminal UI callback, exit-sync, teardown, result-area cleanup and timer/object cleanup are C-bound after 224, 16, 9, 12 and 27 controlled stock comparisons. LVGL object membership 0x43e2ea and recursive descendant 0x43ee54 are C-bound after 144 and 60 controlled cases. List animation deinit 0x5896b4 is C-bound after four controlled cases with its 0xd0-byte state at observed RAM 0x20070ea8. Terminal timer clear 0x5e7ec4 is C-bound after four controlled cases with its 0x18-byte state at observed RAM 0x20073c38. Terminal UI start 0x5e716c, its list animation initializer 0x58966c and theme wrapper 0x5e47cc are C-bound after 9, 4 and 4 controlled cases. Terminal tick 0x5e8008 and its deadline, voice-input and elapsed-record children are C-bound after 96, 252, 24 and 160 controlled cases. Terminal status FSM 0x5e7b74 and its exact 4160-byte dispatch table at 0x650430 are C-bound after 775 controlled cases. This exposes 50 distinct action callback targets, of which ten actions are now C-bound: two ASR actions after 54 controlled cases, two exit actions after 108 controlled cases, two payload actions after 48 controlled cases query-dismiss action after 160 controlled cases status action with its two payload helpers after 72 controlled cases and two reset actions after 32 controlled cases, with notification-restore, LVGL scroll and fade-out children C-bound after 24, 18 and 300 controlled cases; the two FSM name lookups are C-bound after 2048 controlled cases with source-owned RAM pointer slots at 0x20003ea4 and 0x20003edc, while the other 21 callback bodies and name RAM initialization remain open. Reset mode 0x5eae2c and display 0x5e4c84 are C-bound after 31 controlled cases; mode-set wrapper 0x5eae1e and event emitter 0x5eadd4 are C-bound after 25 and 144 controlled cases. Event type 4 child 0x5ea9f6 and its list-reset child 0x5ea7dc are C-bound after 12 and 48 controlled cases. Default event child 0x5eaad4 and its input selector, input application and view refresh children are C-bound after 96, 36, 36 and 48 controlled cases; its offset recomputation child is C-bound after 128 controlled cases; resource pointer and ring item lookup are C-bound after 120 controlled cases using the existing Terminal-data RAM owner; view-position child 0x5ea926, view-index child 0x5ea8ce and position-index search 0x5ea868 are C-bound after 144, 84 and 330 controlled cases; view-select child 0x5ea810 and row-update child 0x5ea768 are C-bound after 240 and 320 controlled cases; row LVGL flag, clear-flag and position calls reuse existing C-bound providers through three ABI adapters; item-height child 0x5ea67a is C-bound after 96 controlled cases using the existing 0x200746dc font-pointer cell; spacing child 0x5ea2c2 and row text/image binding 0x5ea564 are C-bound after 8 and 128 controlled cases; sixteen of the nineteen row-binding child imports reuse existing C-bound stock-address providers through ABI adapters; Terminal image-y 0x5ea2b0, row-color 0x5ea2f2 and row-image 0x5ea524 children are C-bound after 600 controlled cases; image-hint 0x5ea4f0 is C-bound after 216 controlled cases; event type-two 0x5eabde and its last-record 0x597350 and rollover 0x5eab8e children are C-bound after 288 and 48 controlled cases; type-three indexed event 0x5eaca0 is C-bound after 2048 controlled cases; reset prelude 0x5e51ba, ancillary reset 0x5e65f8 and voice-timeout preclear 0x5e7f26 are C-bound after 156, 32 and 96 controlled cases, with audio-manager app release 0x54f50e C-bound after 560 controlled cases; reset subtree 0x5ea342 and its style/image-Y children are C-bound after 48 and 23 controlled cases, with both stock image descriptors, 1341 image bytes and the 68-byte welcome text source-owned; query restore 0x5e6620, its return-to-input action 0x5e57c6 and image-set child 0x5e47fe are C-bound after 320, 96 and 12 controlled cases; display-status 0x44ea04 reuses the existing C-bound scroll-to-Y provider after a fresh 80-case stock oracle; four Terminal disconnect FSM actions 0x5e522e, 0x5e52c2, 0x5e5320 and 0x5e53b8 are C-bound after 512 stock comparisons with their 256-byte icon and texts source-owned; processing-response action 0x5e583c and event-34 routing action 0x5e54a2 are C-bound after 96 and 336 stock comparisons; BLE display-request action 0x5e576c is C-bound after 336 comparisons while its prepare child remains open and fallback reuses the C-bound current-session index; packed event-word action 0x5e63b4 is C-bound after 48 stock comparisons; paired scroll/status actions 0x5e6dd0 and 0x5e6e30 are C-bound after 320 stock comparisons, with notification parent 0x5ec190 C-bound after 120 stock comparisons and its layout child 0x5ebc9e and overlay-focus publication 0x5e5498/0x5cf134 C-bound after 480 comparisons each; interrupt-confirm scroll 0x5e6cb8 and its toggle child 0x5ec73c are C-bound after 1920 cases, with the list-style and indicator-layout child 0x5ec3c0/0x5ec34e C-bound after 1536 cases; interrupt-confirm-show action 0x5e6b18 is C-bound after 192 cases while its UI constructor 0x5ec446 remains open; interrupt-confirm-cancel action 0x5e6ba0 is C-bound after 192 cases with its cleanup child already source-owned; new-session success action 0x5ed870 is C-bound after 192 cases through its existing event, reset, cleanup and input-return providers; query-notification switch-result action 0x5e68dc is C-bound after 384 cases through its existing restore-query provider; paired query-scroll actions 0x5e6e88/0x5e6f60 are C-bound after 960 cases, with their query-layout child 0x5ebb96 C-bound after 64 cases; item-style child 0x5eb3c6 and its count provider 0x5eb30c are C-bound after 444 cases, with indicator child 0x5eb322 and font offset 0x5eb2ee C-bound after 487 cases; session-list scroll action 0x5ed492 is C-bound after 384 cases and its selection, count, validity and object-lookup subtree 0x5ecc1a/0x5eca48/0x5eca64/0x5ecb52 after 626 cases; session focus 0x5ecbea, ListFocus wrapper 0x5e5490 and protobuf encoder 0x5cf0ba are C-bound after 360 cases, direct-apply 0x5ecb88 after 192 cases and row-style 0x5ecb08 after 42 cases; list-animation elapsed 0x5893f0, timeout poll 0x5893fe and queue add 0x5896fc are C-bound after 304 cases; queue processor 0x58956e and completion callback 0x58949e are C-bound after 312 controlled cases; new-object preparation 0x5894d6 is C-bound after 384 controlled cases; old/new button fade start children 0x58c6c4/0x58c622 are C-bound after 600 controlled cases; their Bezier path 0x450688 is C-bound after 15 controlled cases; row show/hide walkers 0x5897ee/0x589892 and LVGL class ancestry 0x43e2d4 are C-bound after 140 and 30 controlled cases; image class record 0x756108 is source-owned with exact fixed words and five relocations; image constructor/destroyer 0x498bd0/0x498c6c are C-bound after 84 cases; button fade callback 0x58c230 and recursive body 0x58c138 are C-bound after 168 cases; image event 0x498c9c and click-area 0x4408b0 are C-bound after 432 and 36 stock comparisons; image draw 0x498ec0 is C-bound after 220 stock comparisons; image opacity/radius accessors 0x498634/0x49865e are C-bound after 90 cases; descriptor initializer 0x452a34 is C-bound after 216 stock comparisons; its four exposed style getters are C-bound after 180 stock comparisons; draw scheduler 0x488a38 is C-bound after 168 controlled stock comparisons; it reuses five existing C lower providers; allocation-failure trap, real decoder/renderer effects and final placement remain open; decoder-info helper 0x488f6a and source-type/zero children were already C-bound in the prior image-header chain; Terminal label-text alias for 0x49942e is C-bound after 48 forwarding cases using the existing stock-compared label provider; formatted label 0x49954c is C-bound after 36 variadic stock comparisons and exposes lower formatter 0x489ad2 while real formatter effects remain open; null fatal branches are independently stock-compared in the five-case label fatal-path oracle; lower two-pass formatted text allocator 0x489ad2 is C-bound after 60 stock comparisons through the existing C-owned vsnprintf provider, with allocation-failure trap stock-compared by the five-case label fatal-path oracle and real formatter effects remaining open; Terminal clear-flag alias for stock 0x43dfa4 is C-bound after 48 forwarding cases using the existing C provider; five more Terminal LVGL object ABI aliases are C-bound after 135 forwarding cases through existing stock-address providers; four LVGL animimage setters/start 0x597ea6/0x597ee0/0x597f10/0x597f52 are C-bound after 68 controlled stock cases including null-object assertions, with animation lower effects and final placement open; query-notification-show FSM action 0x5e6548 is C-bound after 200 stock comparisons including enabled logging, exposing counter getter 0x5973dc and query visibility 0x5ec82a; counter getter 0x5973dc is C-bound after 7 direct stock comparisons through the existing source-owned TD-state provider, while query visibility remains open; 0x20000032 is the confirmed encoded 50 percent image pivot; interrupt-confirm defer-query action 0x5e6d58 is C-bound after 192 stock comparisons including enabled logging, with its output-style 24-byte startup pointer table and six image descriptors/1536 pixel bytes now C-owned; final source-resource linker relocation remains open; row resource placement and lower effects remain open; selector and refresh reuse existing C-bound LVGL object-y and object-height providers. Payload control-flags child 0x5e4a6e is C-bound after 240 controlled cases, and elapsed-text child 0x5e48b8 is C-bound after 36 cases; output-start child 0x5e4920 is C-bound after 25 controlled cases; processing-object child 0x5e4878 and processing-state clear child 0x5ea30c are C-bound after 5 and 12 controlled cases; elapsed-refresh child 0x5e4902 and its fallback clear 0x5e4894 are C-bound after 48 and 4 controlled cases; the elapsed counter uses an existing C-owned provider. Set-output child 0x5e49b0 is C-bound after 100 controlled cases; three of its four exposed RAM cells are source-owned at 0x20074a94 and 0x2007502c-0x2007502d; label-style child 0x5e482a is C-bound after 16 controlled cases; output-mode selector/hash and exact ten-phrase table are C-bound after 240 controlled cases; style runtime writes, animation and LVGL lower-call effects remain. The three exposed teardown service children are C-bound after 24 controlled cases; the event call 0x5e5484 and its display-state protobuf encoder are C-bound after 48 controlled cases, while a 0x2a0-byte state-base import remains; exact RAM ownership, lower effects and final placement are open. Cyclic or malformed LVGL trees and concurrent mutation remain open. Enabled callback logging remains open. The thirteen terminal event-name pointer slots are C-owned at the observed RAM address, but runtime initialization and strings remain open. The fault lookup provider covers all 195 matchable stock codes, but 152 overrun matches use absolute stock pointer values whose relocation and validity as strings remain open. The tracepoint slave file-list handler is C-bound after 6480 logging-disabled stock comparisons. Its nanopb, copy and send lower-call effects and enabled logging remain open. Tracepoint file-list-ready has the stock four-byte section extent in the relocatable chain, while its original one-byte provider declaration still needs a from-stage rebuild. The exposed MessageNotify callback, startup state writer, frame decoder, three validators and four encoders are C-bound, with no audio_message_notify_* imports remaining. Frame enabled logging, real nanopb/BLE child effects, CRC cache initialization and source-owned packet/state final RAM placement remain open. The exposed EvenAI display-control, ANCC clear/sync, callback-list display and state packet branches are C-bound. The app-acquire path through state, count, setup, queue facade, hardware descriptor and index helpers is C-bound. The bounded app, first-hardware, audio-thread and ANCC contexts still need final RAM placement, and lower-call side effects plus callback-list concurrency remain open. The text-stream dispatch, begin, finish, schedule and timer callback have C-bound decisions, while lower-call side effects and concurrency remain open. The dominant-hand subtree has C-bound handlers and descendants, need source ownership or attributed external contracts; advertising logging branches and final RAM placement remain outside their bounded oracles. Onboarding event packet, state and sequence RAM and silent-mode showing-UI RAM need final placement. HUB threshold double arithmetic remains controlled in the bounded oracle because Unicorn M-class rejects it.",
                           "All eight DM dispatch entries and the exposed security children now have C bodies; whole-image source and placement remain open.",
                           "DM storage is a 196-byte bounded C-owned block with a registry alias; full allocation extent and final RAM placement remain open.",
                           "Gray and production-test UI registry contexts each have only an observed eight-byte C reservation; full allocation extent, initialization and final RAM placement remain open.",
                           "Distortion-screen 0x5cf330 and six style wrappers are C-bound with 28 callback and 48 wrapper stock comparisons. The 24x24 pixel resource and two text strings match stock bytes; final RAM and image placement remain open.",
                           "Legal-regulatory UI callback 0x5bf7b8, fade action 0x58c238 and two fade helpers are C-bound with 140, 300 and 64 controlled native comparisons; seven page-helper/style entries have 112 direct cases. All 38 legal text/image resource rows are source-owned with 48 pointer relocations. The page builder 0x5bf332 passes a 333-lower-call stock comparison. Its 0x43f6d6 alignment child is C-bound after 230 controlled stock comparisons, with all eleven lower calls resolving to previously bound C; root-cell allocation extent and final RAM placement remain open.",
                           "EvenAI common-data handler 0x4e2976 and its lazy prepare/OS descendants are C-bound. The frame, ten receive handlers, ten transmit handlers, shared service, common response encoder, state mutex wrappers, heartbeat timer, descriptor, and pinned nanopb are bound in an experimental relocatable chain. Seven EvenAI and two scheduler RAM cells have bounded source-owned NOLOAD placement checks. Logging branch oracles cover the frame's extended and compressed formats and first value; handler logging, startup, final global RAM collision, and whole-image placement remain open. CMSIS/FreeRTOS decisions match the pinned CMSIS-FreeRTOS submodule source.",
                           "Dashboard layout current RAM at 0x200e7934 has a bounded 128-byte source-owned NOLOAD reservation from the stock pointer and C copy extent; full allocation/startup and final image placement remain open.",
                           "EFS transfer RAM at 0x20071cc8 has a bounded 0x76-byte source-owned NOLOAD reservation through the observed active flag at offset 0x75; the complete allocation extent, startup, and final image placement remain open.",
                           "BLE bond erase staging RAM at 0x200636a0 has a source-owned 0x0a00-byte NOLOAD reservation matching the initialized live byte-count cell and stock pointer. Runtime size mutations, complete allocation extent, and final startup/layout remain open.",
                           "Charge and ring-battery callback-manager RAM pointers now have source-owned 12-byte NOLOAD spans at 0x20073f78 and 0x20073f90. The manager source accesses only the first 12 bytes; full allocation extents and final startup/layout remain open.",
                           "BLE flash callbacks RAM at 0x20073270 has a source-owned 0x3c-byte NOLOAD reservation matching the stock initializer clear extent. The current C caller accesses the first two words; final startup/layout and hardware behavior remain open.",
                           "TPL response buffer RAM at 0x20004204 has a source-owned eight-byte NOLOAD reservation matching the current C caller's bounded access and transmit length. Stock initialization, complete allocation extent, final layout, and hardware behavior remain open.",
                           "TPL delayed callback argument RAM at 0x20074b04 has a source-owned three-byte NOLOAD reservation matching the stock three-byte writer. Producer history, complete allocation extent, final layout, and hardware behavior remain open.",
                           "TPL service table row zero at 0x20071414 has a source-owned 20-byte NOLOAD reservation matching the authenticated service-zero registration caller and response callback access. Dynamic service indices, full table extent, final layout, and hardware behavior remain open.",
                           "EvenAI local decoder 0x498092 is C-bound after 32 native comparisons of returns, state, config, notification arguments, and enabled log metadata and first values. Its two notification encoder bodies are also C-bound after 136 controlled stock comparisons including enabled logger metadata and first formatted values, with a source-owned one-byte sequence cell at 0x20074ff9. Logger side effects and later variadic values, final layout/startup, and hardware execution remain open.",
                           "EvenAI ready 0x4e20f2 is C-bound after 84 controlled native comparisons across startup alternatives, text carryover, reply, skill, 0/1/0x1ff/0x200 text lengths, and enabled log metadata and first values. Its RAM includes provisional state at 0x2006f138 (0x218 bytes), text-stream handle 0x20074c04, and two 0x400-byte text buffers. Twelve descendant providers became explicit imports. Known service-dispatch ingress caps text at 0x200; indirect or unseen writers, malformed inputs, logger side effects, later variadic values, final layout/startup, and hardware execution remain open.",
                           "EvenAI ready interval and pending-text accessors are C-bound after seven stock comparisons, including the null-handle empty string at 0x552cf4. The final text-stream object lifetime and whole-image placement remain open.",
                           "EvenAI common timer and start-all paths match stock in 36 controlled role/duration/tick cases, including callback order, RAM writes, and ABI returns. Common timer stop also matches stock in 16 RAM/logging cases. Logger side effects, final RAM placement, and whole-image integration remain open.",
                           "EvenAI text-stream initializer 0x4e551e matches stock in 32 existing/new/failed allocation and logger-mode cases. It is C-bound; allocator 0x552b30 is now an explicit unresolved import. Logger side effects and text-stream object lifetime remain open.",
                           "Text-stream allocator 0x552b30 matches stock in five allocation/mutex/first-buffer/second-buffer/success cases, including 0x30-byte object bytes and cleanup call order. Its buffer constructor 0x553338 is now an explicit unresolved import; full lifecycle remains open.",
                           "Text-stream buffer capacity provider 0x553338 matches stock in 100 owner/capacity/growth/reallocation/log cases. It is C-bound; heap reallocator 0x474d54 is now an explicit unresolved import. Heap and logger effects remain open.",
                           "File-heap realloc wrapper 0x474d54 matches stock in 16 mutex/TLSF/return/error-call cases and is C-bound against existing mutex and TLSF providers. Its two heap RAM cells and final placement remain open.",
                           "File-heap mutex and pool pointer cells are C-owned as four-byte NOLOAD storage at stock addresses 0x200748f8 and 0x20074abc, with standalone placement verified. Startup values, final global layout, and hardware remain open.",
                           "TLSF pool initializer 0x5eda64 is C-linked after 16 stock comparisons of the 0x70800-byte zeroing call, TLSF call, pool-handle write and log metadata. Its backing range 0x20208e70..0x20279670 is source-owned NOLOAD storage with standalone placement verified. Independent writers, global collision, and boot ordering remain open.",
                           "Redirect initializer 0x474d9c is C-linked after 32 stock comparisons of both mutex cells, return, and log branches. Its companion mutex cell at 0x200748f4 is source-owned NOLOAD storage; boot wiring and final global placement remain open.",
                           "EvenAI stop-current-streaming 0x4e557c is C-bound after 40 stock comparisons of handle/mode, stop/pause calls, bounded 0x20-byte display-state clear and logging. Its two text-stream descendants are explicit imports; complete display-state allocation and child side effects remain open.",
                           "Text-stream stop 0x552d10 and pause 0x552d40 match stock in 64 controlled object/mutex/timer/buffer cases and are C-bound against existing mutex and timer-stop providers. Complete object lifetime and hardware behavior remain open.",
                           "Text-stream copy-bytes 0x553274 matches stock in 96 controlled 16-bit clamp, mutex, capacity, copy, callback and object-byte cases and is C-bound. Callback effects, malformed objects, and full lifetime remain open.",
                           "EvenAI ready set-text calls now declare and pass the stock fifth stack argument zero, observed at 0x4e24cc and 0x4e269c. The 84-case ready oracle records that argument at intercepted set-text calls; downstream Apollo bindings were rebuilt.",
                           "Text-stream set-text 0x552c20 matches stock in 288 controlled five-argument validation, append/replace, capacity, dispatch and return cases. It is C-bound; four helper routines are now explicit imports. Helper effects and malformed inputs remain open.",
                           "Text-stream validation 0x5533cc and next-interval 0x5532f8 match stock in 120 controlled mode/string and signed-arithmetic cases. They are C-bound; restart and dispatch remain unresolved.",
                           "Text-stream restart 0x552db2 matches stock in 64 signed-length, mutex, timer and state-byte cases and is C-bound. Dispatch remains unresolved; timer and mutex effects remain external.",
                           "Complete data/startup/layout and physical execution remain unproved."],
    }
    if set(images) != {"codec", "ble_em9305", "touch", "case", "apollo_bootloader", "apollo_main"}:
        raise RuntimeError("six-image set changed")
    record = {
        "status": "PASS_EXPERIMENTAL_SIX_CURRENT_C_EVIDENCE_AUDIT",
        "target_id": "official-s200-v2.2.6.10", "target_sha256": TARGET_SHA,
        "images": images, "complete_source_payloads": 0,
        "limits": ["Each row is a separately qualified candidate or experimental object, not one unified final build.",
                   "Zero imports or an experimental ELF does not prove source coverage, stock layout, or hardware operation."],
    }
    OUT.write_text(json.dumps(record, indent=2) + "\n")
    print(record["status"], len(images), record["complete_source_payloads"], sha(OUT))


if __name__ == "__main__":
    main()
