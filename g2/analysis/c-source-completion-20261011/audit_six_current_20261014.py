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
        "INFO dispatcher 0x4213e6 passes 7200 direct cases visiting 350/354 stock bytes; the four unvisited bytes are two fallback branches after the invalid-space gate. A 1420-case composed replay reaches 224/354 dispatcher and 788/810 root bytes with resident ROM read controlled. Production M55 and whole-image behavior remain open.")
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
        "settings_last_message_ram_extent": {"current_source_receipt": ram_ref, "selected_object_bytes": selected_ram_bytes, "required_minimum_bytes": 104, "integrated": selected_ram_bytes == 104},
        "unresolved_count": len(actual), "unresolved_symbols": actual,
        "source_complete": False, "full_payload_linked": False,
        "remaining_gate": ["175 current imports; the dominant-hand subtree has C-bound handlers and descendants, need source ownership or attributed external contracts; advertising logging branches and final RAM placement remain outside their bounded oracles. Onboarding event packet, state and sequence RAM and silent-mode showing-UI RAM need final placement. HUB threshold double arithmetic remains controlled in the bounded oracle because Unicorn M-class rejects it.",
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
