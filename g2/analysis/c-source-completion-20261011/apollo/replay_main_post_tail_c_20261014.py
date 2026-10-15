#!/usr/bin/env python3
"""Rebuild source-backed Apollo Main stages after archive-tail replay."""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BUILD = G2 / "build/c-firmware/20261014"
HERE = Path(__file__).resolve().parent
OUT = BUILD / "main-post-tail-c-replay"
TAIL = BUILD / "main-corrected-archive-tail-replay/receipt.json"
STAGES = (
    ("bind_main_lvgl_runtime_state_20261014.py", "main-lvgl-runtime-state", 367, 363),
    ("bind_main_sync_receive_strings_20261014.py", "main-sync-receive-strings", 363, 358),
    ("bind_main_sync_runtime_cells_20261014.py", "main-sync-runtime-cells", 358, 349),
    ("bind_main_thread_log_strings_20261014.py", "main-thread-log-strings", 349, 336),
    ("bind_main_thread_runtime_cells_20261014.py", "main-thread-runtime-cells", 336, 330),
    ("bind_main_page_font_style_44143e_20261014.py", "main-page-font-style", 330, 329),
    ("bind_main_page_locale_lookup_20261014.py", "main-page-locale-lookup", 329, 328),
    ("bind_main_display_context_runtime_20261014.py", "main-display-context-runtime", 328, 325),
    ("bind_main_timeout_runtime_20261014.py", "main-timeout-runtime", 325, 313),
    ("bind_main_sync_module_aliases_20261014.py", "main-sync-module-aliases", 313, 305),
    ("bind_main_sync_timer_runtime_20261014.py", "main-sync-timer-runtime", 305, 302),
    ("bind_main_role_display_runtime_20261014.py", "main-role-display-runtime", 302, 298),
    ("bind_main_font_gpio_runtime_20261014.py", "main-font-gpio-runtime", 298, 293),
    ("bind_main_uart_session_runtime_20261014.py", "main-uart-session-runtime", 293, 287),
    ("bind_main_uart_queue_runtime_20261014.py", "main-uart-queue-runtime", 287, 282),
    ("bind_main_ring_task_display_path_20261014.py", "main-ring-task-display-path", 282, 279),
    ("bind_main_display_thread_runtime_20261014.py", "main-display-thread-runtime", 279, 275),
    ("bind_main_display_startup_runtime_20261014.py", "main-display-startup-runtime", 275, 268),
    ("bind_main_display_control_lock_data_20261014.py", "main-display-control-lock-data", 268, 266),
    ("bind_main_display_ring_templates_20261014.py", "main-display-ring-templates", 266, 263),
    ("bind_main_ring_list_runtime_20261014.py", "main-ring-list-runtime", 263, 259),
    ("bind_main_audio_clock_pin_config_20261014.py", "main-audio-clock-pin-config", 259, 258),
    ("bind_main_dashboard_file_runtime_20261014.py", "main-dashboard-file-runtime", 258, 254),
    ("bind_main_hub_send_queue_20261014.py", "main-hub-send-queue", 254, 253),
    ("bind_main_case_status_20261014.py", "main-case-status", 253, 252),
    ("bind_main_onboarding_imu_cells_20261014.py", "main-onboarding-imu-cells", 252, 250),
    ("bind_main_ring_status_pointer_20261014.py", "main-ring-status-pointer", 250, 249),
    ("bind_main_radio_gpio_callback_20261014.py", "main-radio-gpio-callback", 249, 248),
    ("bind_main_uart_product_mode_state_20261014.py", "main-uart-product-mode-state", 248, 247),
    ("bind_main_charger_state_minimum_20261014.py", "main-charger-state-minimum", 247, 246),
    ("bind_main_flashdb_kv_delete_20261014.py", "main-flashdb-kv-delete", 246, 245),
    ("bind_main_flashdb_gc_move_20261014.py", "main-flashdb-gc-move", 245, 244),
    ("bind_main_flashdb_store_value_20261014.py", "main-flashdb-store-value", 244, 243),
    ("bind_main_quicklist_decode_20261015.py", "main-quicklist-decode", 243, 244),
    ("bind_main_quicklist_store_one_20261015.py", "main-quicklist-store-one", 244, 244),
    ("bind_main_quicklist_store_many_20261015.py", "main-quicklist-store-many", 244, 243),
    ("bind_main_quicklist_tick_alias_20261015.py", "main-quicklist-tick-alias", 243, 242),
    ("bind_main_quicklist_frame_process_20261015.py", "main-quicklist-frame-process", 242, 248),
    ("bind_main_quicklist_rx_validators_20261015.py", "main-quicklist-rx-validators", 248, 245),
    ("bind_main_quicklist_pb_descriptor_20261015.py", "main-quicklist-pb-descriptor", 245, 244),
    ("bind_main_quicklist_tx_encoders_20261015.py", "main-quicklist-tx-encoders", 244, 241),
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def file_from_receipt(row, path_key, hash_key):
    path = ROOT / row[path_key]
    if sha(path) != row[hash_key]:
        raise RuntimeError(f"stale receipt input/output: {path}")
    return path


def imports(path):
    output = subprocess.check_output(["arm-none-eabi-nm", "-u", str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.strip()}


def main():
    tail = json.loads(TAIL.read_text())
    previous = file_from_receipt(tail, "linked_object", "linked_object_sha256")
    if tail["unresolved_after"] != 367 or len(imports(previous)) != 367:
        raise RuntimeError("corrected archive-tail baseline changed")
    records = []
    for script_name, directory, expected_before, expected_after in STAGES:
        script = HERE / script_name
        if not script.is_file():
            raise RuntimeError(f"missing C binder: {script}")
        result = subprocess.run([sys.executable, str(script)], check=True,
                                capture_output=True, text=True)
        receipt_path = BUILD / directory / "receipt.json"
        row = json.loads(receipt_path.read_text())
        base = file_from_receipt(row, "base_object", "base_sha256")
        linked = file_from_receipt(row, "linked_object", "linked_object_sha256")
        source = file_from_receipt(row, "source", "source_sha256")
        if base != previous:
            raise RuntimeError(f"noncontiguous Main C handoff: {directory}")
        before, after = imports(base), imports(linked)
        if (len(before), len(after)) != (expected_before, expected_after):
            raise RuntimeError(f"Main C import count changed: {directory}")
        if before - after != set(row["imports_resolved"]) or after - before != set(row["imports_added"]):
            raise RuntimeError(f"Main C import receipt delta changed: {directory}")
        records.append({
            "stage": directory,
            "binder": str(script.relative_to(ROOT)), "binder_sha256": sha(script),
            "status": row["status"], "binder_output": result.stdout.strip(),
            "receipt": str(receipt_path.relative_to(ROOT)), "receipt_sha256": sha(receipt_path),
            "source": str(source.relative_to(ROOT)), "source_sha256": sha(source),
            "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
            "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
            "unresolved_before": len(before), "unresolved_after": len(after),
            "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
        })
        previous = linked
    refresh_script = HERE / "bind_main_quicklist_refresh_20261015.py"
    refresh_result = subprocess.run([sys.executable, str(refresh_script)], check=True,
                                    capture_output=True, text=True)
    refresh_path = G2 / "build/c-firmware/20261015/main-quicklist-refresh/integrated-receipt.json"
    refresh = json.loads(refresh_path.read_text())
    if refresh["status"] != "PASS_EXPERIMENTAL_MAIN_QUICKLIST_REFRESH_CHAIN_C":
        raise RuntimeError("QuickList refresh stage status changed")
    base = file_from_receipt(refresh, "base_object", "base_sha256")
    linked = file_from_receipt(refresh, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 241 or len(imports(linked)) != 244:
        raise RuntimeError("QuickList refresh stage handoff changed")
    for item in refresh["sources"]:
        if sha(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError("stale QuickList refresh source")
    if imports(base)-imports(linked) != set(refresh["imports_resolved"]) or \
            imports(linked)-imports(base) != set(refresh["imports_added"]):
        raise RuntimeError("QuickList refresh import delta changed")
    records.append({
        "stage": "main-quicklist-refresh", "binder": str(refresh_script.relative_to(ROOT)),
        "binder_sha256": sha(refresh_script), "status": refresh["status"],
        "binder_output": refresh_result.stdout.strip(),
        "receipt": str(refresh_path.relative_to(ROOT)), "receipt_sha256": sha(refresh_path),
        "sources": refresh["sources"], "base_object": str(base.relative_to(ROOT)),
        "base_sha256": sha(base), "linked_object": str(linked.relative_to(ROOT)),
        "linked_sha256": sha(linked), "unresolved_before": 241, "unresolved_after": 244,
        "imports_resolved": sorted(imports(base)-imports(linked)),
        "imports_added": sorted(imports(linked)-imports(base)),
    })
    previous = linked
    mode_script = HERE / "bind_main_quicklist_mode_one_20261015.py"
    mode_result = subprocess.run([sys.executable, str(mode_script)], check=True,
                                 capture_output=True, text=True)
    mode_path = G2 / "build/c-firmware/20261015/main-quicklist-mode-one/receipt.json"
    mode = json.loads(mode_path.read_text())
    if mode["status"] != "PASS_EXPERIMENTAL_MAIN_QUICKLIST_MODE_ONE_C":
        raise RuntimeError("QuickList mode-one stage status changed")
    base = file_from_receipt(mode, "base_object", "base_sha256")
    linked = file_from_receipt(mode, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 244 or len(imports(linked)) != 244:
        raise RuntimeError("QuickList mode-one stage handoff changed")
    for item in mode["sources"]:
        if sha(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError("stale QuickList mode-one source")
    if imports(base)-imports(linked) != set(mode["imports_resolved"]) or \
            imports(linked)-imports(base) != set(mode["imports_added"]):
        raise RuntimeError("QuickList mode-one import delta changed")
    records.append({
        "stage": "main-quicklist-mode-one", "binder": str(mode_script.relative_to(ROOT)),
        "binder_sha256": sha(mode_script), "status": mode["status"],
        "binder_output": mode_result.stdout.strip(),
        "receipt": str(mode_path.relative_to(ROOT)), "receipt_sha256": sha(mode_path),
        "sources": mode["sources"], "base_object": str(base.relative_to(ROOT)),
        "base_sha256": sha(base), "linked_object": str(linked.relative_to(ROOT)),
        "linked_sha256": sha(linked), "unresolved_before": 244, "unresolved_after": 244,
        "imports_resolved": sorted(imports(base)-imports(linked)),
        "imports_added": sorted(imports(linked)-imports(base)),
    })
    previous = linked
    selector_script = HERE / "bind_main_quicklist_select_records_20261015.py"
    selector_result = subprocess.run([sys.executable, str(selector_script)], check=True,
                                     capture_output=True, text=True)
    selector_path = G2 / "build/c-firmware/20261015/main-quicklist-select-records/receipt.json"
    selector = json.loads(selector_path.read_text())
    if selector["status"] != "PASS_EXPERIMENTAL_MAIN_QUICKLIST_SELECT_RECORDS_C":
        raise RuntimeError("QuickList selector stage status changed")
    base = file_from_receipt(selector, "base_object", "base_sha256")
    linked = file_from_receipt(selector, "linked_object", "linked_sha256")
    source = file_from_receipt(selector, "source", "source_sha256")
    if base != previous or len(imports(base)) != 244 or len(imports(linked)) != 244 or \
            imports(base) != imports(linked):
        raise RuntimeError("QuickList selector stage handoff changed")
    records.append({
        "stage": "main-quicklist-select-records", "binder": str(selector_script.relative_to(ROOT)),
        "binder_sha256": sha(selector_script), "status": selector["status"],
        "binder_output": selector_result.stdout.strip(),
        "receipt": str(selector_path.relative_to(ROOT)), "receipt_sha256": sha(selector_path),
        "source": str(source.relative_to(ROOT)), "source_sha256": sha(source),
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 244, "unresolved_after": 244,
        "imports_resolved": [], "imports_added": [],
    })
    previous = linked
    mode_two_script = HERE / "bind_main_quicklist_mode_two_20261015.py"
    mode_two_result = subprocess.run([sys.executable, str(mode_two_script)], check=True,
                                     capture_output=True, text=True)
    mode_two_path = G2 / "build/c-firmware/20261015/main-quicklist-mode-two/receipt.json"
    mode_two = json.loads(mode_two_path.read_text())
    if mode_two["status"] != "PASS_EXPERIMENTAL_MAIN_QUICKLIST_MODE_TWO_C":
        raise RuntimeError("QuickList mode-two stage status changed")
    base = file_from_receipt(mode_two, "base_object", "base_sha256")
    linked = file_from_receipt(mode_two, "linked_object", "linked_sha256")
    source = file_from_receipt(mode_two, "source", "source_sha256")
    if base != previous or len(imports(base)) != 244 or len(imports(linked)) != 243 or \
            imports(base)-imports(linked) != {"audio_quicklist_mode_two_4f5a1c"} or \
            imports(linked)-imports(base):
        raise RuntimeError("QuickList mode-two stage handoff changed")
    records.append({
        "stage": "main-quicklist-mode-two", "binder": str(mode_two_script.relative_to(ROOT)),
        "binder_sha256": sha(mode_two_script), "status": mode_two["status"],
        "binder_output": mode_two_result.stdout.strip(),
        "receipt": str(mode_two_path.relative_to(ROOT)), "receipt_sha256": sha(mode_two_path),
        "source": str(source.relative_to(ROOT)), "source_sha256": sha(source),
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 244, "unresolved_after": 243,
        "imports_resolved": ["audio_quicklist_mode_two_4f5a1c"], "imports_added": [],
    })
    previous = linked
    mode_detail_script = HERE / "bind_main_quicklist_mode_two_detail_20261015.py"
    mode_detail_result = subprocess.run([sys.executable, str(mode_detail_script)], check=True,
                                        capture_output=True, text=True)
    mode_detail_path = G2 / "build/c-firmware/20261015/main-quicklist-mode-two-detail/receipt.json"
    mode_detail = json.loads(mode_detail_path.read_text())
    if mode_detail["status"] != "PASS_EXPERIMENTAL_MAIN_QUICKLIST_MODE_TWO_DETAIL_C":
        raise RuntimeError("QuickList mode-two-detail stage status changed")
    base = file_from_receipt(mode_detail, "base_object", "base_sha256")
    linked = file_from_receipt(mode_detail, "linked_object", "linked_sha256")
    source = file_from_receipt(mode_detail, "source", "source_sha256")
    if base != previous or len(imports(base)) != 243 or len(imports(linked)) != 242 or \
            imports(base)-imports(linked) != {"audio_quicklist_mode_two_detail_4f5838"} or \
            imports(linked)-imports(base):
        raise RuntimeError("QuickList mode-two-detail stage handoff changed")
    records.append({
        "stage": "main-quicklist-mode-two-detail", "binder": str(mode_detail_script.relative_to(ROOT)),
        "binder_sha256": sha(mode_detail_script), "status": mode_detail["status"],
        "binder_output": mode_detail_result.stdout.strip(),
        "receipt": str(mode_detail_path.relative_to(ROOT)), "receipt_sha256": sha(mode_detail_path),
        "source": str(source.relative_to(ROOT)), "source_sha256": sha(source),
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 243, "unresolved_after": 242,
        "imports_resolved": ["audio_quicklist_mode_two_detail_4f5838"], "imports_added": [],
    })
    previous = linked
    mode_three_script = HERE / "bind_main_quicklist_mode_three_20261015.py"
    mode_three_result = subprocess.run([sys.executable, str(mode_three_script)], check=True,
                                       capture_output=True, text=True)
    mode_three_path = G2 / "build/c-firmware/20261015/main-quicklist-mode-three/receipt.json"
    mode_three = json.loads(mode_three_path.read_text())
    if mode_three["status"] != "PASS_EXPERIMENTAL_MAIN_QUICKLIST_MODE_THREE_C":
        raise RuntimeError("QuickList mode-three stage status changed")
    base = file_from_receipt(mode_three, "base_object", "base_sha256")
    linked = file_from_receipt(mode_three, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 242 or len(imports(linked)) != 241 or \
            imports(base)-imports(linked) != {"audio_quicklist_mode_three_4f5c4c"} or \
            imports(linked)-imports(base):
        raise RuntimeError("QuickList mode-three stage handoff changed")
    for item in mode_three["sources"]:
        if sha(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError("stale QuickList mode-three source")
    records.append({
        "stage": "main-quicklist-mode-three", "binder": str(mode_three_script.relative_to(ROOT)),
        "binder_sha256": sha(mode_three_script), "status": mode_three["status"],
        "binder_output": mode_three_result.stdout.strip(),
        "receipt": str(mode_three_path.relative_to(ROOT)), "receipt_sha256": sha(mode_three_path),
        "sources": mode_three["sources"], "base_object": str(base.relative_to(ROOT)),
        "base_sha256": sha(base), "linked_object": str(linked.relative_to(ROOT)),
        "linked_sha256": sha(linked), "unresolved_before": 242, "unresolved_after": 241,
        "imports_resolved": ["audio_quicklist_mode_three_4f5c4c"], "imports_added": [],
    })
    previous = linked
    aux_script = HERE / "bind_main_quicklist_aux_update_20261015.py"
    aux_result = subprocess.run([sys.executable, str(aux_script)], check=True,
                                capture_output=True, text=True)
    aux_path = G2 / "build/c-firmware/20261015/main-quicklist-aux-update/receipt.json"
    aux = json.loads(aux_path.read_text())
    if aux["status"] != "PASS_EXPERIMENTAL_MAIN_QUICKLIST_AUX_UPDATE_C":
        raise RuntimeError("QuickList auxiliary stage status changed")
    base = file_from_receipt(aux, "base_object", "base_sha256")
    linked = file_from_receipt(aux, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 241 or len(imports(linked)) != 241 or \
            imports(base)-imports(linked) != {"audio_quicklist_aux_update_4f6328"} or \
            imports(linked)-imports(base) != {"audio_quicklist_send_completed_5591b0"}:
        raise RuntimeError("QuickList auxiliary stage handoff changed")
    source = ROOT / aux["source"]
    if sha(source) != aux["source_sha256"]:
        raise RuntimeError("stale QuickList auxiliary source")
    records.append({
        "stage": "main-quicklist-aux-update", "binder": str(aux_script.relative_to(ROOT)),
        "binder_sha256": sha(aux_script), "status": aux["status"],
        "binder_output": aux_result.stdout.strip(),
        "receipt": str(aux_path.relative_to(ROOT)), "receipt_sha256": sha(aux_path),
        "source": aux["source"], "source_sha256": aux["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 241, "unresolved_after": 241,
        "imports_resolved": ["audio_quicklist_aux_update_4f6328"],
        "imports_added": ["audio_quicklist_send_completed_5591b0"],
    })
    previous = linked
    send_script = HERE / "bind_main_quicklist_send_completed_20261015.py"
    send_result = subprocess.run([sys.executable, str(send_script)], check=True,
                                 capture_output=True, text=True)
    send_path = G2 / "build/c-firmware/20261015/main-quicklist-send-completed/receipt.json"
    send = json.loads(send_path.read_text())
    if send["status"] != "PASS_EXPERIMENTAL_MAIN_QUICKLIST_SEND_COMPLETED_C":
        raise RuntimeError("QuickList completed sender stage status changed")
    base = file_from_receipt(send, "base_object", "base_sha256")
    linked = file_from_receipt(send, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 241 or len(imports(linked)) != 241 or \
            imports(base)-imports(linked) != {"audio_quicklist_send_completed_5591b0"} or \
            imports(linked)-imports(base) != {"audio_ring_pb_tx_ble_475c1a"}:
        raise RuntimeError("QuickList completed sender stage handoff changed")
    source = ROOT / send["source"]
    if sha(source) != send["source_sha256"]:
        raise RuntimeError("stale QuickList completed sender source")
    records.append({
        "stage": "main-quicklist-send-completed", "binder": str(send_script.relative_to(ROOT)),
        "binder_sha256": sha(send_script), "status": send["status"],
        "binder_output": send_result.stdout.strip(),
        "receipt": str(send_path.relative_to(ROOT)), "receipt_sha256": sha(send_path),
        "source": send["source"], "source_sha256": send["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 241, "unresolved_after": 241,
        "imports_resolved": ["audio_quicklist_send_completed_5591b0"],
        "imports_added": ["audio_ring_pb_tx_ble_475c1a"],
    })
    previous = linked
    notify_script = HERE / "bind_main_quicklist_notify_alias_20261015.py"
    notify_result = subprocess.run([sys.executable, str(notify_script)], check=True,
                                   capture_output=True, text=True)
    notify_path = G2 / "build/c-firmware/20261015/main-quicklist-notify-alias/receipt.json"
    notify = json.loads(notify_path.read_text())
    if notify["status"] != "PASS_EXPERIMENTAL_MAIN_QUICKLIST_NOTIFY_ALIAS_C":
        raise RuntimeError("QuickList notify transport stage status changed")
    base = file_from_receipt(notify, "base_object", "base_sha256")
    linked = file_from_receipt(notify, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 241 or len(imports(linked)) != 240 or \
            imports(base)-imports(linked) != {"audio_ring_pb_tx_ble_475c1a"} or \
            imports(linked)-imports(base):
        raise RuntimeError("QuickList notify transport stage handoff changed")
    for key, digest in (("source", "source_sha256"), ("alias", "alias_sha256")):
        if sha(ROOT / notify[key]) != notify[digest]:
            raise RuntimeError("stale QuickList notify transport source")
    records.append({
        "stage": "main-quicklist-notify-alias", "binder": str(notify_script.relative_to(ROOT)),
        "binder_sha256": sha(notify_script), "status": notify["status"],
        "binder_output": notify_result.stdout.strip(),
        "receipt": str(notify_path.relative_to(ROOT)), "receipt_sha256": sha(notify_path),
        "source": notify["source"], "source_sha256": notify["source_sha256"],
        "alias": notify["alias"], "alias_sha256": notify["alias_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 241, "unresolved_after": 240,
        "imports_resolved": ["audio_ring_pb_tx_ble_475c1a"], "imports_added": [],
    })
    previous = linked
    factory_script = HERE / "bind_main_page_factory_498668_20261015.py"
    factory_result = subprocess.run([sys.executable, str(factory_script)], check=True,
                                    capture_output=True, text=True)
    factory_path = G2 / "build/c-firmware/20261015/main-page-factory-498668/receipt.json"
    factory = json.loads(factory_path.read_text())
    if factory["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_FACTORY_498668_C":
        raise RuntimeError("page factory stage status changed")
    base = file_from_receipt(factory, "base_object", "base_sha256")
    linked = file_from_receipt(factory, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 240 or len(imports(linked)) != 241 or \
            imports(base)-imports(linked) != {"audio_uart_page_498668"} or \
            imports(linked)-imports(base) != {"audio_uart_page_create_44cf98",
                                            "audio_uart_page_initialize_44d0f0"}:
        raise RuntimeError("page factory stage handoff changed")
    if sha(ROOT / factory["source"]) != factory["source_sha256"]:
        raise RuntimeError("stale page factory source")
    records.append({
        "stage": "main-page-factory-498668", "binder": str(factory_script.relative_to(ROOT)),
        "binder_sha256": sha(factory_script), "status": factory["status"],
        "binder_output": factory_result.stdout.strip(),
        "receipt": str(factory_path.relative_to(ROOT)), "receipt_sha256": sha(factory_path),
        "source": factory["source"], "source_sha256": factory["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 240, "unresolved_after": 241,
        "imports_resolved": ["audio_uart_page_498668"],
        "imports_added": ["audio_uart_page_create_44cf98",
                          "audio_uart_page_initialize_44d0f0"],
    })
    previous = linked
    init_script = HERE / "bind_main_page_initialize_44d0f0_20261015.py"
    init_result = subprocess.run([sys.executable, str(init_script)], check=True,
                                 capture_output=True, text=True)
    init_path = G2 / "build/c-firmware/20261015/main-page-initialize-44d0f0/receipt.json"
    init = json.loads(init_path.read_text())
    if init["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_INITIALIZE_44D0F0_C":
        raise RuntimeError("page initializer stage status changed")
    base = file_from_receipt(init, "base_object", "base_sha256")
    linked = file_from_receipt(init, "linked_object", "linked_sha256")
    init_children = {"audio_uart_page_lock_44bde0", "audio_uart_page_descriptor_init_44d1fc",
                     "audio_uart_page_relayout_43ffa0", "audio_uart_page_context_44d33a",
                     "audio_uart_page_needs_context_44d1cc", "audio_uart_page_attach_context_44d342",
                     "audio_uart_page_overlay_44dca2"}
    if base != previous or len(imports(base)) != 241 or len(imports(linked)) != 247 or \
            imports(base)-imports(linked) != {"audio_uart_page_initialize_44d0f0"} or \
            imports(linked)-imports(base) != init_children:
        raise RuntimeError("page initializer stage handoff changed")
    if sha(ROOT / init["source"]) != init["source_sha256"]:
        raise RuntimeError("stale page initializer source")
    records.append({
        "stage": "main-page-initialize-44d0f0", "binder": str(init_script.relative_to(ROOT)),
        "binder_sha256": sha(init_script), "status": init["status"],
        "binder_output": init_result.stdout.strip(),
        "receipt": str(init_path.relative_to(ROOT)), "receipt_sha256": sha(init_path),
        "source": init["source"], "source_sha256": init["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 241, "unresolved_after": 247,
        "imports_resolved": ["audio_uart_page_initialize_44d0f0"],
        "imports_added": sorted(init_children),
    })
    previous = linked
    lock_script = HERE / "bind_main_page_lock_44bde0_20261015.py"
    lock_result = subprocess.run([sys.executable, str(lock_script)], check=True,
                                 capture_output=True, text=True)
    lock_path = G2 / "build/c-firmware/20261015/main-page-lock-44bde0/receipt.json"
    lock = json.loads(lock_path.read_text())
    if lock["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_LOCK_44BDE0_C":
        raise RuntimeError("page lock stage status changed")
    base = file_from_receipt(lock, "base_object", "base_sha256")
    linked = file_from_receipt(lock, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 247 or len(imports(linked)) != 246 or \
            imports(base)-imports(linked) != {"audio_uart_page_lock_44bde0"} or \
            imports(linked)-imports(base):
        raise RuntimeError("page lock stage handoff changed")
    if sha(ROOT / lock["source"]) != lock["source_sha256"]:
        raise RuntimeError("stale page lock source")
    records.append({
        "stage": "main-page-lock-44bde0", "binder": str(lock_script.relative_to(ROOT)),
        "binder_sha256": sha(lock_script), "status": lock["status"],
        "binder_output": lock_result.stdout.strip(),
        "receipt": str(lock_path.relative_to(ROOT)), "receipt_sha256": sha(lock_path),
        "source": lock["source"], "source_sha256": lock["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 247, "unresolved_after": 246,
        "imports_resolved": ["audio_uart_page_lock_44bde0"], "imports_added": [],
    })
    previous = linked
    needs_script = HERE / "bind_main_page_needs_context_44d1cc_20261015.py"
    needs_result = subprocess.run([sys.executable, str(needs_script)], check=True,
                                  capture_output=True, text=True)
    needs_path = G2 / "build/c-firmware/20261015/main-page-needs-context-44d1cc/receipt.json"
    needs = json.loads(needs_path.read_text())
    if needs["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_NEEDS_CONTEXT_44D1CC_C":
        raise RuntimeError("page context stage status changed")
    base = file_from_receipt(needs, "base_object", "base_sha256")
    linked = file_from_receipt(needs, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 246 or len(imports(linked)) != 245 or \
            imports(base)-imports(linked) != {"audio_uart_page_needs_context_44d1cc"} or \
            imports(linked)-imports(base):
        raise RuntimeError("page context stage handoff changed")
    if sha(ROOT / needs["source"]) != needs["source_sha256"]:
        raise RuntimeError("stale page context source")
    records.append({
        "stage": "main-page-needs-context-44d1cc", "binder": str(needs_script.relative_to(ROOT)),
        "binder_sha256": sha(needs_script), "status": needs["status"],
        "binder_output": needs_result.stdout.strip(),
        "receipt": str(needs_path.relative_to(ROOT)), "receipt_sha256": sha(needs_path),
        "source": needs["source"], "source_sha256": needs["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 246, "unresolved_after": 245,
        "imports_resolved": ["audio_uart_page_needs_context_44d1cc"], "imports_added": [],
    })
    previous = linked
    descriptor_script = HERE / "bind_main_page_descriptor_init_44d1fc_20261015.py"
    descriptor_result = subprocess.run([sys.executable, str(descriptor_script)], check=True,
                                       capture_output=True, text=True)
    descriptor_path = G2 / "build/c-firmware/20261015/main-page-descriptor-init-44d1fc/receipt.json"
    descriptor = json.loads(descriptor_path.read_text())
    if descriptor["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_DESCRIPTOR_INIT_44D1FC_C":
        raise RuntimeError("page descriptor stage status changed")
    base = file_from_receipt(descriptor, "base_object", "base_sha256")
    linked = file_from_receipt(descriptor, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 245 or len(imports(linked)) != 244 or \
            imports(base)-imports(linked) != {"audio_uart_page_descriptor_init_44d1fc"} or \
            imports(linked)-imports(base):
        raise RuntimeError("page descriptor stage handoff changed")
    if sha(ROOT / descriptor["source"]) != descriptor["source_sha256"]:
        raise RuntimeError("stale page descriptor source")
    records.append({
        "stage": "main-page-descriptor-init-44d1fc",
        "binder": str(descriptor_script.relative_to(ROOT)),
        "binder_sha256": sha(descriptor_script), "status": descriptor["status"],
        "binder_output": descriptor_result.stdout.strip(),
        "receipt": str(descriptor_path.relative_to(ROOT)), "receipt_sha256": sha(descriptor_path),
        "source": descriptor["source"], "source_sha256": descriptor["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 245, "unresolved_after": 244,
        "imports_resolved": ["audio_uart_page_descriptor_init_44d1fc"], "imports_added": [],
    })
    previous = linked
    context_script = HERE / "bind_main_page_context_44d33a_20261015.py"
    context_result = subprocess.run([sys.executable, str(context_script)], check=True,
                                    capture_output=True, text=True)
    context_path = G2 / "build/c-firmware/20261015/main-page-context-44d33a/receipt.json"
    context = json.loads(context_path.read_text())
    if context["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_CONTEXT_44D33A_C":
        raise RuntimeError("page context pointer stage status changed")
    base = file_from_receipt(context, "base_object", "base_sha256")
    linked = file_from_receipt(context, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 244 or len(imports(linked)) != 243 or \
            imports(base)-imports(linked) != {"audio_uart_page_context_44d33a"} or \
            imports(linked)-imports(base):
        raise RuntimeError("page context pointer stage handoff changed")
    if sha(ROOT / context["source"]) != context["source_sha256"]:
        raise RuntimeError("stale page context pointer source")
    records.append({
        "stage": "main-page-context-44d33a", "binder": str(context_script.relative_to(ROOT)),
        "binder_sha256": sha(context_script), "status": context["status"],
        "binder_output": context_result.stdout.strip(),
        "receipt": str(context_path.relative_to(ROOT)), "receipt_sha256": sha(context_path),
        "source": context["source"], "source_sha256": context["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 244, "unresolved_after": 243,
        "imports_resolved": ["audio_uart_page_context_44d33a"], "imports_added": [],
    })
    previous = linked
    relayout_script = HERE / "bind_main_page_relayout_43ffa0_20261015.py"
    relayout_result = subprocess.run([sys.executable, str(relayout_script)], check=True,
                                     capture_output=True, text=True)
    relayout_path = G2 / "build/c-firmware/20261015/main-page-relayout-43ffa0/receipt.json"
    relayout = json.loads(relayout_path.read_text())
    if relayout["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_RELAYOUT_43FFA0_C":
        raise RuntimeError("page relayout stage status changed")
    base = file_from_receipt(relayout, "base_object", "base_sha256")
    linked = file_from_receipt(relayout, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 243 or len(imports(linked)) != 242 or \
            imports(base)-imports(linked) != {"audio_uart_page_relayout_43ffa0"} or \
            imports(linked)-imports(base):
        raise RuntimeError("page relayout stage handoff changed")
    if sha(ROOT / relayout["source"]) != relayout["source_sha256"]:
        raise RuntimeError("stale page relayout source")
    records.append({
        "stage": "main-page-relayout-43ffa0", "binder": str(relayout_script.relative_to(ROOT)),
        "binder_sha256": sha(relayout_script), "status": relayout["status"],
        "binder_output": relayout_result.stdout.strip(),
        "receipt": str(relayout_path.relative_to(ROOT)), "receipt_sha256": sha(relayout_path),
        "source": relayout["source"], "source_sha256": relayout["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 243, "unresolved_after": 242,
        "imports_resolved": ["audio_uart_page_relayout_43ffa0"], "imports_added": [],
    })
    previous = linked
    overlay_script = HERE / "bind_main_page_overlay_44dca2_20261015.py"
    overlay_result = subprocess.run([sys.executable, str(overlay_script)], check=True,
                                    capture_output=True, text=True)
    overlay_path = G2 / "build/c-firmware/20261015/main-page-overlay-44dca2/receipt.json"
    overlay = json.loads(overlay_path.read_text())
    if overlay["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_OVERLAY_44DCA2_C":
        raise RuntimeError("page overlay stage status changed")
    base = file_from_receipt(overlay, "base_object", "base_sha256")
    linked = file_from_receipt(overlay, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 242 or len(imports(linked)) != 241 or \
            imports(base)-imports(linked) != {"audio_uart_page_overlay_44dca2"} or \
            imports(linked)-imports(base):
        raise RuntimeError("page overlay stage handoff changed")
    if sha(ROOT / overlay["source"]) != overlay["source_sha256"]:
        raise RuntimeError("stale page overlay source")
    records.append({
        "stage": "main-page-overlay-44dca2", "binder": str(overlay_script.relative_to(ROOT)),
        "binder_sha256": sha(overlay_script), "status": overlay["status"],
        "binder_output": overlay_result.stdout.strip(),
        "receipt": str(overlay_path.relative_to(ROOT)), "receipt_sha256": sha(overlay_path),
        "source": overlay["source"], "source_sha256": overlay["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 242, "unresolved_after": 241,
        "imports_resolved": ["audio_uart_page_overlay_44dca2"], "imports_added": [],
    })
    previous = linked
    attach_script = HERE / "bind_main_page_attach_context_44d342_20261015.py"
    attach_result = subprocess.run([sys.executable, str(attach_script)], check=True,
                                   capture_output=True, text=True)
    attach_path = G2 / "build/c-firmware/20261015/main-page-attach-context-44d342/receipt.json"
    attach = json.loads(attach_path.read_text())
    if attach["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_ATTACH_CONTEXT_NORMAL_C":
        raise RuntimeError("page attachment stage status changed")
    base = file_from_receipt(attach, "base_object", "base_sha256")
    linked = file_from_receipt(attach, "linked_object", "linked_sha256")
    attach_lower = {"audio_uart_page_unlink_44d3b2", "audio_uart_page_notify_44d5f8"}
    if base != previous or len(imports(base)) != 241 or len(imports(linked)) != 242 or \
            imports(base)-imports(linked) != {"audio_uart_page_attach_context_44d342"} or \
            imports(linked)-imports(base) != attach_lower:
        raise RuntimeError("page attachment stage handoff changed")
    if sha(ROOT / attach["source"]) != attach["source_sha256"]:
        raise RuntimeError("stale page attachment source")
    records.append({
        "stage": "main-page-attach-context-44d342", "binder": str(attach_script.relative_to(ROOT)),
        "binder_sha256": sha(attach_script), "status": attach["status"],
        "binder_output": attach_result.stdout.strip(),
        "receipt": str(attach_path.relative_to(ROOT)), "receipt_sha256": sha(attach_path),
        "source": attach["source"], "source_sha256": attach["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 241, "unresolved_after": 242,
        "imports_resolved": ["audio_uart_page_attach_context_44d342"],
        "imports_added": sorted(attach_lower),
    })
    previous = linked
    notify_script = HERE / "bind_main_page_notify_44d5f8_20261015.py"
    notify_result = subprocess.run([sys.executable, str(notify_script)], check=True,
                                   capture_output=True, text=True)
    notify_path = G2 / "build/c-firmware/20261015/main-page-notify-44d5f8/receipt.json"
    notify = json.loads(notify_path.read_text())
    if notify["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_NOTIFY_C":
        raise RuntimeError("page notification stage status changed")
    base = file_from_receipt(notify, "base_object", "base_sha256")
    linked = file_from_receipt(notify, "linked_object", "linked_sha256")
    notify_lower = {"audio_uart_page_update_unbound_44d45c",
                    "audio_uart_page_update_bound_44d4b6"}
    if base != previous or len(imports(base)) != 242 or len(imports(linked)) != 243 or \
            imports(base)-imports(linked) != {"audio_uart_page_notify_44d5f8"} or \
            imports(linked)-imports(base) != notify_lower:
        raise RuntimeError("page notification stage handoff changed")
    if sha(ROOT / notify["source"]) != notify["source_sha256"]:
        raise RuntimeError("stale page notification source")
    records.append({
        "stage": "main-page-notify-44d5f8", "binder": str(notify_script.relative_to(ROOT)),
        "binder_sha256": sha(notify_script), "status": notify["status"],
        "binder_output": notify_result.stdout.strip(),
        "receipt": str(notify_path.relative_to(ROOT)), "receipt_sha256": sha(notify_path),
        "source": notify["source"], "source_sha256": notify["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 242, "unresolved_after": 243,
        "imports_resolved": ["audio_uart_page_notify_44d5f8"],
        "imports_added": sorted(notify_lower),
    })
    previous = linked
    update_script = HERE / "bind_main_page_update_wrappers_44d45c_20261015.py"
    update_result = subprocess.run([sys.executable, str(update_script)], check=True,
                                   capture_output=True, text=True)
    update_path = G2 / "build/c-firmware/20261015/main-page-update-wrappers-44d45c/receipt.json"
    update = json.loads(update_path.read_text())
    if update["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_UPDATE_WRAPPERS_NORMAL_C":
        raise RuntimeError("page update wrapper stage status changed")
    base = file_from_receipt(update, "base_object", "base_sha256")
    linked = file_from_receipt(update, "linked_object", "linked_sha256")
    update_removed = {"audio_uart_page_update_unbound_44d45c",
                      "audio_uart_page_update_bound_44d4b6"}
    update_lower = {"audio_uart_page_update_core_44d63a"}
    if base != previous or len(imports(base)) != 243 or len(imports(linked)) != 242 or \
            imports(base)-imports(linked) != update_removed or \
            imports(linked)-imports(base) != update_lower:
        raise RuntimeError("page update wrapper stage handoff changed")
    if sha(ROOT / update["source"]) != update["source_sha256"]:
        raise RuntimeError("stale page update wrapper source")
    records.append({
        "stage": "main-page-update-wrappers-44d45c", "binder": str(update_script.relative_to(ROOT)),
        "binder_sha256": sha(update_script), "status": update["status"],
        "binder_output": update_result.stdout.strip(),
        "receipt": str(update_path.relative_to(ROOT)), "receipt_sha256": sha(update_path),
        "source": update["source"], "source_sha256": update["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 243, "unresolved_after": 242,
        "imports_resolved": sorted(update_removed), "imports_added": sorted(update_lower),
    })
    previous = linked
    core_script = HERE / "bind_main_page_update_core_44d63a_20261015.py"
    core_result = subprocess.run([sys.executable, str(core_script)], check=True,
                                 capture_output=True, text=True)
    core_path = G2 / "build/c-firmware/20261015/main-page-update-core-44d63a/receipt.json"
    core = json.loads(core_path.read_text())
    if core["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_UPDATE_CORE_C":
        raise RuntimeError("page update core stage status changed")
    base = file_from_receipt(core, "base_object", "base_sha256")
    linked = file_from_receipt(core, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 242 or len(imports(linked)) != 242 or \
            imports(base)-imports(linked) != {"audio_uart_page_update_core_44d63a"} or \
            imports(linked)-imports(base) != {"audio_uart_page_context_find_44d77a"}:
        raise RuntimeError("page update core stage handoff changed")
    if sha(ROOT / core["source"]) != core["source_sha256"]:
        raise RuntimeError("stale page update core source")
    records.append({
        "stage": "main-page-update-core-44d63a", "binder": str(core_script.relative_to(ROOT)),
        "binder_sha256": sha(core_script), "status": core["status"],
        "binder_output": core_result.stdout.strip(),
        "receipt": str(core_path.relative_to(ROOT)), "receipt_sha256": sha(core_path),
        "source": core["source"], "source_sha256": core["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 242, "unresolved_after": 242,
        "imports_resolved": ["audio_uart_page_update_core_44d63a"],
        "imports_added": ["audio_uart_page_context_find_44d77a"],
    })
    previous = linked
    context_script = HERE / "bind_main_page_context_find_44d77a_20261015.py"
    context_result = subprocess.run([sys.executable, str(context_script)], check=True,
                                    capture_output=True, text=True)
    context_path = G2 / "build/c-firmware/20261015/main-page-context-find-44d77a/receipt.json"
    context = json.loads(context_path.read_text())
    if context["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_CONTEXT_FIND_C":
        raise RuntimeError("page context lookup stage status changed")
    base = file_from_receipt(context, "base_object", "base_sha256")
    linked = file_from_receipt(context, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 242 or len(imports(linked)) != 241 or \
            imports(base)-imports(linked) != {"audio_uart_page_context_find_44d77a"} or \
            imports(linked)-imports(base):
        raise RuntimeError("page context lookup stage handoff changed")
    if sha(ROOT / context["source"]) != context["source_sha256"]:
        raise RuntimeError("stale page context lookup source")
    records.append({
        "stage": "main-page-context-find-44d77a", "binder": str(context_script.relative_to(ROOT)),
        "binder_sha256": sha(context_script), "status": context["status"],
        "binder_output": context_result.stdout.strip(),
        "receipt": str(context_path.relative_to(ROOT)), "receipt_sha256": sha(context_path),
        "source": context["source"], "source_sha256": context["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 242, "unresolved_after": 241,
        "imports_resolved": ["audio_uart_page_context_find_44d77a"],
        "imports_added": [],
    })
    previous = linked
    unlink_script = HERE / "bind_main_page_unlink_44d3b2_20261015.py"
    unlink_result = subprocess.run([sys.executable, str(unlink_script)], check=True,
                                   capture_output=True, text=True)
    unlink_path = G2 / "build/c-firmware/20261015/main-page-unlink-44d3b2/receipt.json"
    unlink = json.loads(unlink_path.read_text())
    if unlink["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_UNLINK_NORMAL_C":
        raise RuntimeError("page unlink stage status changed")
    base = file_from_receipt(unlink, "base_object", "base_sha256")
    linked = file_from_receipt(unlink, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 241 or len(imports(linked)) != 240 or \
            imports(base)-imports(linked) != {"audio_uart_page_unlink_44d3b2"} or \
            imports(linked)-imports(base):
        raise RuntimeError("page unlink stage handoff changed")
    if sha(ROOT / unlink["source"]) != unlink["source_sha256"]:
        raise RuntimeError("stale page unlink source")
    records.append({
        "stage": "main-page-unlink-44d3b2", "binder": str(unlink_script.relative_to(ROOT)),
        "binder_sha256": sha(unlink_script), "status": unlink["status"],
        "binder_output": unlink_result.stdout.strip(),
        "receipt": str(unlink_path.relative_to(ROOT)), "receipt_sha256": sha(unlink_path),
        "source": unlink["source"], "source_sha256": unlink["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 241, "unresolved_after": 240,
        "imports_resolved": ["audio_uart_page_unlink_44d3b2"], "imports_added": [],
    })
    previous = linked
    editing_script = HERE / "bind_main_page_editing_44d510_20261015.py"
    editing_result = subprocess.run([sys.executable, str(editing_script)], check=True,
                                    capture_output=True, text=True)
    editing_path = G2 / "build/c-firmware/20261015/main-page-editing-44d510/receipt.json"
    editing = json.loads(editing_path.read_text())
    if editing["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_EDITING_C":
        raise RuntimeError("page editing stage status changed")
    base = file_from_receipt(editing, "base_object", "base_sha256")
    linked = file_from_receipt(editing, "linked_object", "linked_sha256")
    editing_defs = {"audio_uart_page_set_editing_44d510",
                    "audio_uart_page_active_object_44d58c",
                    "audio_uart_page_get_editing_44d5a4"}
    if base != previous or len(imports(base)) != 240 or len(imports(linked)) != 240 or \
            imports(base) != imports(linked) or \
            not editing_defs <= {line.split()[-1] for line in subprocess.check_output(
                ["arm-none-eabi-nm", "--defined-only", str(linked)], text=True).splitlines()}:
        raise RuntimeError("page editing stage handoff changed")
    if sha(ROOT / editing["source"]) != editing["source_sha256"]:
        raise RuntimeError("stale page editing source")
    records.append({
        "stage": "main-page-editing-44d510", "binder": str(editing_script.relative_to(ROOT)),
        "binder_sha256": sha(editing_script), "status": editing["status"],
        "binder_output": editing_result.stdout.strip(),
        "receipt": str(editing_path.relative_to(ROOT)), "receipt_sha256": sha(editing_path),
        "source": editing["source"], "source_sha256": editing["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 240, "unresolved_after": 240,
        "definitions": sorted(editing_defs), "imports_resolved": [], "imports_added": [],
    })
    previous = linked
    scrollbar_script = HERE / "bind_main_page_scrollbar_mode_44e368_20261015.py"
    scrollbar_result = subprocess.run([sys.executable, str(scrollbar_script)], check=True,
                                      capture_output=True, text=True)
    scrollbar_path = G2 / "build/c-firmware/20261015/main-page-scrollbar-mode-44e368/receipt.json"
    scrollbar = json.loads(scrollbar_path.read_text())
    if scrollbar["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_SCROLLBAR_MODE_C":
        raise RuntimeError("page scrollbar mode stage status changed")
    base = file_from_receipt(scrollbar, "base_object", "base_sha256")
    linked = file_from_receipt(scrollbar, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 240 or len(imports(linked)) != 239 or \
            imports(base)-imports(linked) != {"audio_uart_page_44e368"} or \
            imports(linked)-imports(base):
        raise RuntimeError("page scrollbar mode stage handoff changed")
    if sha(ROOT / scrollbar["source"]) != scrollbar["source_sha256"]:
        raise RuntimeError("stale page scrollbar mode source")
    records.append({
        "stage": "main-page-scrollbar-mode-44e368", "binder": str(scrollbar_script.relative_to(ROOT)),
        "binder_sha256": sha(scrollbar_script), "status": scrollbar["status"],
        "binder_output": scrollbar_result.stdout.strip(),
        "receipt": str(scrollbar_path.relative_to(ROOT)), "receipt_sha256": sha(scrollbar_path),
        "source": scrollbar["source"], "source_sha256": scrollbar["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 240, "unresolved_after": 239,
        "imports_resolved": ["audio_uart_page_44e368"], "imports_added": [],
    })
    previous = linked
    create_script = HERE / "bind_main_page_create_44cf98_20261015.py"
    create_result = subprocess.run([sys.executable, str(create_script)], check=True,
                                   capture_output=True, text=True)
    create_path = G2 / "build/c-firmware/20261015/main-page-create-44cf98/receipt.json"
    create = json.loads(create_path.read_text())
    if create["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_CREATE_C":
        raise RuntimeError("page constructor stage status changed")
    base = file_from_receipt(create, "base_object", "base_sha256")
    linked = file_from_receipt(create, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 239 or len(imports(linked)) != 238 or \
            imports(base)-imports(linked) != {"audio_uart_page_create_44cf98"} or \
            imports(linked)-imports(base):
        raise RuntimeError("page constructor stage handoff changed")
    if sha(ROOT / create["source"]) != create["source_sha256"]:
        raise RuntimeError("stale page constructor source")
    records.append({
        "stage": "main-page-create-44cf98", "binder": str(create_script.relative_to(ROOT)),
        "binder_sha256": sha(create_script), "status": create["status"],
        "binder_output": create_result.stdout.strip(),
        "receipt": str(create_path.relative_to(ROOT)), "receipt_sha256": sha(create_path),
        "source": create["source"], "source_sha256": create["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 239, "unresolved_after": 238,
        "imports_resolved": ["audio_uart_page_create_44cf98"], "imports_added": [],
    })
    previous = linked
    child_script = HERE / "bind_main_lv_first_live_child_44e164_20261015.py"
    child_result = subprocess.run([sys.executable, str(child_script)], check=True,
                                  capture_output=True, text=True)
    child_path = G2 / "build/c-firmware/20261015/main-lv-first-live-child-44e164/receipt.json"
    child = json.loads(child_path.read_text())
    if child["status"] != "PASS_EXPERIMENTAL_MAIN_LV_FIRST_LIVE_CHILD_C":
        raise RuntimeError("LVGL first live child stage status changed")
    base = file_from_receipt(child, "base_object", "base_sha256")
    linked = file_from_receipt(child, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 238 or len(imports(linked)) != 238 or \
            imports(base) != imports(linked) or \
            "audio_uart_lv_first_live_child_44e164" not in {line.split()[-1] for line in
                subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(linked)],
                                        text=True).splitlines()}:
        raise RuntimeError("LVGL first live child stage handoff changed")
    if sha(ROOT / child["source"]) != child["source_sha256"]:
        raise RuntimeError("stale LVGL first live child source")
    records.append({
        "stage": "main-lv-first-live-child-44e164", "binder": str(child_script.relative_to(ROOT)),
        "binder_sha256": sha(child_script), "status": child["status"],
        "binder_output": child_result.stdout.strip(),
        "receipt": str(child_path.relative_to(ROOT)), "receipt_sha256": sha(child_path),
        "source": child["source"], "source_sha256": child["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 238, "unresolved_after": 238,
        "definitions": ["audio_uart_lv_first_live_child_44e164"],
        "imports_resolved": [], "imports_added": [],
    })
    previous = linked
    clean_script = HERE / "bind_main_page_clean_44d878_20261015.py"
    clean_result = subprocess.run([sys.executable, str(clean_script)], check=True,
                                   capture_output=True, text=True)
    clean_path = G2 / "build/c-firmware/20261015/main-page-clean-44d878/receipt.json"
    clean = json.loads(clean_path.read_text())
    if clean["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_CLEAN_C":
        raise RuntimeError("page clean stage status changed")
    base = file_from_receipt(clean, "base_object", "base_sha256")
    linked = file_from_receipt(clean, "linked_object", "linked_sha256")
    clean_lower = {"audio_uart_lv_child_delete_44df80", "audio_uart_lv_position_reset_44e9ba"}
    if base != previous or len(imports(base)) != 238 or len(imports(linked)) != 239 or \
            imports(base)-imports(linked) != {"audio_uart_page_44d878"} or \
            imports(linked)-imports(base) != clean_lower:
        raise RuntimeError("page clean stage handoff changed")
    if sha(ROOT / clean["source"]) != clean["source_sha256"]:
        raise RuntimeError("stale page clean source")
    records.append({
        "stage": "main-page-clean-44d878", "binder": str(clean_script.relative_to(ROOT)),
        "binder_sha256": sha(clean_script), "status": clean["status"],
        "binder_output": clean_result.stdout.strip(),
        "receipt": str(clean_path.relative_to(ROOT)), "receipt_sha256": sha(clean_path),
        "source": clean["source"], "source_sha256": clean["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 238, "unresolved_after": 239,
        "imports_resolved": ["audio_uart_page_44d878"], "imports_added": sorted(clean_lower),
    })
    previous = linked
    position_script = HERE / "bind_main_lv_position_reset_44e9ba_20261015.py"
    position_result = subprocess.run([sys.executable, str(position_script)], check=True,
                                      capture_output=True, text=True)
    position_path = G2 / "build/c-firmware/20261015/main-lv-position-reset-44e9ba/receipt.json"
    position = json.loads(position_path.read_text())
    if position["status"] != "PASS_EXPERIMENTAL_MAIN_LV_POSITION_RESET_C":
        raise RuntimeError("position reset stage status changed")
    base = file_from_receipt(position, "base_object", "base_sha256")
    linked = file_from_receipt(position, "linked_object", "linked_sha256")
    position_lower = {"audio_uart_lv_scroll_to_x_44e9da", "audio_uart_lv_scroll_to_y_44ea04"}
    if base != previous or len(imports(base)) != 239 or len(imports(linked)) != 240 or \
            imports(base)-imports(linked) != {"audio_uart_lv_position_reset_44e9ba"} or \
            imports(linked)-imports(base) != position_lower:
        raise RuntimeError("position reset stage handoff changed")
    if sha(ROOT / position["source"]) != position["source_sha256"]:
        raise RuntimeError("stale position reset source")
    records.append({
        "stage": "main-lv-position-reset-44e9ba", "binder": str(position_script.relative_to(ROOT)),
        "binder_sha256": sha(position_script), "status": position["status"],
        "binder_output": position_result.stdout.strip(),
        "receipt": str(position_path.relative_to(ROOT)), "receipt_sha256": sha(position_path),
        "source": position["source"], "source_sha256": position["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 239, "unresolved_after": 240,
        "imports_resolved": ["audio_uart_lv_position_reset_44e9ba"],
        "imports_added": sorted(position_lower),
    })
    previous = linked
    axes_script = HERE / "bind_main_lv_scroll_axes_44e9da_20261015.py"
    axes_result = subprocess.run([sys.executable, str(axes_script)], check=True,
                                  capture_output=True, text=True)
    axes_path = G2 / "build/c-firmware/20261015/main-lv-scroll-axes-44e9da/receipt.json"
    axes = json.loads(axes_path.read_text())
    if axes["status"] != "PASS_EXPERIMENTAL_MAIN_LV_SCROLL_AXES_C":
        raise RuntimeError("scroll axes stage status changed")
    base = file_from_receipt(axes, "base_object", "base_sha256")
    linked = file_from_receipt(axes, "linked_object", "linked_sha256")
    axes_resolved = {"audio_uart_lv_scroll_to_x_44e9da", "audio_uart_lv_scroll_to_y_44ea04"}
    axes_lower = {"audio_uart_lv_scroll_move_44e79e", "audio_uart_lv_scroll_by_44ea98"}
    if base != previous or len(imports(base)) != 240 or len(imports(linked)) != 240 or \
            imports(base)-imports(linked) != axes_resolved or \
            imports(linked)-imports(base) != axes_lower:
        raise RuntimeError("scroll axes stage handoff changed")
    if sha(ROOT / axes["source"]) != axes["source_sha256"]:
        raise RuntimeError("stale scroll axes source")
    records.append({
        "stage": "main-lv-scroll-axes-44e9da", "binder": str(axes_script.relative_to(ROOT)),
        "binder_sha256": sha(axes_script), "status": axes["status"],
        "binder_output": axes_result.stdout.strip(),
        "receipt": str(axes_path.relative_to(ROOT)), "receipt_sha256": sha(axes_path),
        "source": axes["source"], "source_sha256": axes["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 240, "unresolved_after": 240,
        "imports_resolved": sorted(axes_resolved), "imports_added": sorted(axes_lower),
    })
    previous = linked
    by_script = HERE / "bind_main_lv_scroll_by_44ea98_20261015.py"
    by_result = subprocess.run([sys.executable, str(by_script)], check=True,
                                capture_output=True, text=True)
    by_path = G2 / "build/c-firmware/20261015/main-lv-scroll-by-44ea98/receipt.json"
    by = json.loads(by_path.read_text())
    if by["status"] != "PASS_EXPERIMENTAL_MAIN_LV_SCROLL_BY_C":
        raise RuntimeError("scroll-by stage status changed")
    base = file_from_receipt(by, "base_object", "base_sha256")
    linked = file_from_receipt(by, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 240 or len(imports(linked)) != 239 or \
            imports(base)-imports(linked) != {"audio_uart_lv_scroll_by_44ea98"} or \
            imports(linked)-imports(base):
        raise RuntimeError("scroll-by stage handoff changed")
    if sha(ROOT / by["source"]) != by["source_sha256"]:
        raise RuntimeError("stale scroll-by source")
    records.append({
        "stage": "main-lv-scroll-by-44ea98", "binder": str(by_script.relative_to(ROOT)),
        "binder_sha256": sha(by_script), "status": by["status"],
        "binder_output": by_result.stdout.strip(),
        "receipt": str(by_path.relative_to(ROOT)), "receipt_sha256": sha(by_path),
        "source": by["source"], "source_sha256": by["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 240, "unresolved_after": 239,
        "imports_resolved": ["audio_uart_lv_scroll_by_44ea98"], "imports_added": [],
    })
    previous = linked
    move_script = HERE / "bind_main_lv_scroll_move_44e79e_20261015.py"
    move_result = subprocess.run([sys.executable, str(move_script)], check=True,
                                  capture_output=True, text=True)
    move_path = G2 / "build/c-firmware/20261015/main-lv-scroll-move-44e79e/receipt.json"
    move = json.loads(move_path.read_text())
    if move["status"] != "PASS_EXPERIMENTAL_MAIN_LV_SCROLL_MOVE_C":
        raise RuntimeError("scroll movement stage status changed")
    base = file_from_receipt(move, "base_object", "base_sha256")
    linked = file_from_receipt(move, "linked_object", "linked_sha256")
    move_lower = {"audio_uart_lv_scroll_mode_44e2a4", "audio_uart_lv_scroll_top_44e4aa",
                  "audio_uart_lv_scroll_dispatch_44e884"}
    if base != previous or len(imports(base)) != 239 or len(imports(linked)) != 241 or \
            imports(base)-imports(linked) != {"audio_uart_lv_scroll_move_44e79e"} or \
            imports(linked)-imports(base) != move_lower:
        raise RuntimeError("scroll movement stage handoff changed")
    if sha(ROOT / move["source"]) != move["source_sha256"]:
        raise RuntimeError("stale scroll movement source")
    records.append({
        "stage": "main-lv-scroll-move-44e79e", "binder": str(move_script.relative_to(ROOT)),
        "binder_sha256": sha(move_script), "status": move["status"],
        "binder_output": move_result.stdout.strip(),
        "receipt": str(move_path.relative_to(ROOT)), "receipt_sha256": sha(move_path),
        "source": move["source"], "source_sha256": move["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 239, "unresolved_after": 241,
        "imports_resolved": ["audio_uart_lv_scroll_move_44e79e"],
        "imports_added": sorted(move_lower),
    })
    previous = linked
    getters_script = HERE / "bind_main_lv_scroll_mode_top_44e2a4_20261015.py"
    getters_result = subprocess.run([sys.executable, str(getters_script)], check=True,
                                     capture_output=True, text=True)
    getters_path = G2 / "build/c-firmware/20261015/main-lv-scroll-mode-top-44e2a4/receipt.json"
    getters = json.loads(getters_path.read_text())
    if getters["status"] != "PASS_EXPERIMENTAL_MAIN_LV_SCROLL_MODE_TOP_C":
        raise RuntimeError("scroll getter stage status changed")
    base = file_from_receipt(getters, "base_object", "base_sha256")
    linked = file_from_receipt(getters, "linked_object", "linked_sha256")
    getters_resolved = {"audio_uart_lv_scroll_mode_44e2a4", "audio_uart_lv_scroll_top_44e4aa"}
    if base != previous or len(imports(base)) != 241 or len(imports(linked)) != 239 or \
            imports(base)-imports(linked) != getters_resolved or \
            imports(linked)-imports(base):
        raise RuntimeError("scroll getter stage handoff changed")
    if sha(ROOT / getters["source"]) != getters["source_sha256"]:
        raise RuntimeError("stale scroll getter source")
    records.append({
        "stage": "main-lv-scroll-mode-top-44e2a4", "binder": str(getters_script.relative_to(ROOT)),
        "binder_sha256": sha(getters_script), "status": getters["status"],
        "binder_output": getters_result.stdout.strip(),
        "receipt": str(getters_path.relative_to(ROOT)), "receipt_sha256": sha(getters_path),
        "source": getters["source"], "source_sha256": getters["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 241, "unresolved_after": 239,
        "imports_resolved": sorted(getters_resolved), "imports_added": [],
    })
    previous = linked
    dispatch_script = HERE / "bind_main_lv_scroll_dispatch_44e884_20261015.py"
    dispatch_result = subprocess.run([sys.executable, str(dispatch_script)], check=True,
                                      capture_output=True, text=True)
    dispatch_path = G2 / "build/c-firmware/20261015/main-lv-scroll-dispatch-44e884/receipt.json"
    dispatch = json.loads(dispatch_path.read_text())
    if dispatch["status"] != "PASS_EXPERIMENTAL_MAIN_LV_SCROLL_DISPATCH_C":
        raise RuntimeError("scroll dispatch stage status changed")
    base = file_from_receipt(dispatch, "base_object", "base_sha256")
    linked = file_from_receipt(dispatch, "linked_object", "linked_sha256")
    dispatch_lower = {"audio_uart_lv_anim_values_4506ce", "audio_uart_lv_anim_duration_clamp_4505a2",
                      "audio_uart_lv_anim_start_450408", "audio_uart_lv_anim_path_450672",
                      "audio_uart_lv_anim_init_4503d6"}
    if base != previous or len(imports(base)) != 239 or len(imports(linked)) != 243 or \
            imports(base)-imports(linked) != {"audio_uart_lv_scroll_dispatch_44e884"} or \
            imports(linked)-imports(base) != dispatch_lower:
        raise RuntimeError("scroll dispatch stage handoff changed")
    if sha(ROOT / dispatch["source"]) != dispatch["source_sha256"]:
        raise RuntimeError("stale scroll dispatch source")
    records.append({
        "stage": "main-lv-scroll-dispatch-44e884", "binder": str(dispatch_script.relative_to(ROOT)),
        "binder_sha256": sha(dispatch_script), "status": dispatch["status"],
        "binder_output": dispatch_result.stdout.strip(),
        "receipt": str(dispatch_path.relative_to(ROOT)), "receipt_sha256": sha(dispatch_path),
        "source": dispatch["source"], "source_sha256": dispatch["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 239, "unresolved_after": 243,
        "imports_resolved": ["audio_uart_lv_scroll_dispatch_44e884"],
        "imports_added": sorted(dispatch_lower),
    })
    previous = linked
    values_script = HERE / "bind_main_lv_anim_values_4506ce_20261015.py"
    values_result = subprocess.run([sys.executable, str(values_script)], check=True,
                                    capture_output=True, text=True)
    values_path = G2 / "build/c-firmware/20261015/main-lv-anim-values-4506ce/receipt.json"
    values = json.loads(values_path.read_text())
    if values["status"] != "PASS_EXPERIMENTAL_MAIN_LV_ANIM_VALUES_C":
        raise RuntimeError("animation values stage status changed")
    base = file_from_receipt(values, "base_object", "base_sha256")
    linked = file_from_receipt(values, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 243 or len(imports(linked)) != 242 or \
            imports(base)-imports(linked) != {"audio_uart_lv_anim_values_4506ce"} or \
            imports(linked)-imports(base):
        raise RuntimeError("animation values stage handoff changed")
    if sha(ROOT / values["source"]) != values["source_sha256"]:
        raise RuntimeError("stale animation values source")
    records.append({
        "stage": "main-lv-anim-values-4506ce", "binder": str(values_script.relative_to(ROOT)),
        "binder_sha256": sha(values_script), "status": values["status"],
        "binder_output": values_result.stdout.strip(),
        "receipt": str(values_path.relative_to(ROOT)), "receipt_sha256": sha(values_path),
        "source": values["source"], "source_sha256": values["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 243, "unresolved_after": 242,
        "imports_resolved": ["audio_uart_lv_anim_values_4506ce"], "imports_added": [],
    })
    previous = linked
    init_script = HERE / "bind_main_lv_anim_init_4503d6_20261015.py"
    init_result = subprocess.run([sys.executable, str(init_script)], check=True,
                                  capture_output=True, text=True)
    init_path = G2 / "build/c-firmware/20261015/main-lv-anim-init-4503d6/receipt.json"
    init = json.loads(init_path.read_text())
    if init["status"] != "PASS_EXPERIMENTAL_MAIN_LV_ANIM_INIT_C":
        raise RuntimeError("animation init stage status changed")
    base = file_from_receipt(init, "base_object", "base_sha256")
    linked = file_from_receipt(init, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 242 or len(imports(linked)) != 242 or \
            imports(base)-imports(linked) != {"audio_uart_lv_anim_init_4503d6"} or \
            imports(linked)-imports(base) != {"audio_uart_lv_anim_default_path_450634"}:
        raise RuntimeError("animation init stage handoff changed")
    if sha(ROOT / init["source"]) != init["source_sha256"]:
        raise RuntimeError("stale animation init source")
    records.append({
        "stage": "main-lv-anim-init-4503d6", "binder": str(init_script.relative_to(ROOT)),
        "binder_sha256": sha(init_script), "status": init["status"],
        "binder_output": init_result.stdout.strip(),
        "receipt": str(init_path.relative_to(ROOT)), "receipt_sha256": sha(init_path),
        "source": init["source"], "source_sha256": init["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 242, "unresolved_after": 242,
        "imports_resolved": ["audio_uart_lv_anim_init_4503d6"],
        "imports_added": ["audio_uart_lv_anim_default_path_450634"],
    })
    previous = linked
    paths_script = HERE / "bind_main_lv_anim_paths_450634_20261015.py"
    paths_result = subprocess.run([sys.executable, str(paths_script)], check=True,
                                   capture_output=True, text=True)
    paths_path = G2 / "build/c-firmware/20261015/main-lv-anim-paths-450634/receipt.json"
    paths = json.loads(paths_path.read_text())
    if paths["status"] != "PASS_EXPERIMENTAL_MAIN_LV_ANIM_PATHS_C":
        raise RuntimeError("animation paths stage status changed")
    base = file_from_receipt(paths, "base_object", "base_sha256")
    linked = file_from_receipt(paths, "linked_object", "linked_sha256")
    paths_resolved = {"audio_uart_lv_anim_path_450672", "audio_uart_lv_anim_default_path_450634"}
    paths_lower = {"audio_uart_lv_anim_interpolate_4888b4", "audio_uart_lv_anim_bezier_450a04"}
    if base != previous or len(imports(base)) != 242 or len(imports(linked)) != 242 or \
            imports(base)-imports(linked) != paths_resolved or \
            imports(linked)-imports(base) != paths_lower:
        raise RuntimeError("animation paths stage handoff changed")
    if sha(ROOT / paths["source"]) != paths["source_sha256"]:
        raise RuntimeError("stale animation paths source")
    records.append({
        "stage": "main-lv-anim-paths-450634", "binder": str(paths_script.relative_to(ROOT)),
        "binder_sha256": sha(paths_script), "status": paths["status"],
        "binder_output": paths_result.stdout.strip(),
        "receipt": str(paths_path.relative_to(ROOT)), "receipt_sha256": sha(paths_path),
        "source": paths["source"], "source_sha256": paths["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 242, "unresolved_after": 242,
        "imports_resolved": sorted(paths_resolved), "imports_added": sorted(paths_lower),
    })
    previous = linked
    interpolation_script = HERE / "bind_main_lv_anim_interpolation_4888b4_20261015.py"
    interpolation_result = subprocess.run([sys.executable, str(interpolation_script)], check=True,
                                          capture_output=True, text=True)
    interpolation_path = G2 / "build/c-firmware/20261015/main-lv-anim-interpolation-4888b4/receipt.json"
    interpolation = json.loads(interpolation_path.read_text())
    if interpolation["status"] != "PASS_EXPERIMENTAL_MAIN_LV_ANIM_INTERPOLATION_C":
        raise RuntimeError("animation interpolation stage status changed")
    base = file_from_receipt(interpolation, "base_object", "base_sha256")
    linked = file_from_receipt(interpolation, "linked_object", "linked_sha256")
    interpolation_resolved = {"audio_uart_lv_anim_interpolate_4888b4",
                              "audio_uart_lv_anim_bezier_450a04"}
    if base != previous or len(imports(base)) != 242 or len(imports(linked)) != 241 or \
            imports(base)-imports(linked) != interpolation_resolved or \
            imports(linked)-imports(base) != {"audio_uart_lv_anim_bezier_curve_48869a"}:
        raise RuntimeError("animation interpolation stage handoff changed")
    if sha(ROOT / interpolation["source"]) != interpolation["source_sha256"]:
        raise RuntimeError("stale animation interpolation source")
    records.append({
        "stage": "main-lv-anim-interpolation-4888b4",
        "binder": str(interpolation_script.relative_to(ROOT)),
        "binder_sha256": sha(interpolation_script), "status": interpolation["status"],
        "binder_output": interpolation_result.stdout.strip(),
        "receipt": str(interpolation_path.relative_to(ROOT)),
        "receipt_sha256": sha(interpolation_path),
        "source": interpolation["source"], "source_sha256": interpolation["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 242, "unresolved_after": 241,
        "imports_resolved": sorted(interpolation_resolved),
        "imports_added": ["audio_uart_lv_anim_bezier_curve_48869a"],
    })
    previous = linked
    speed_script = HERE / "bind_main_lv_anim_speed_4505a2_20261015.py"
    speed_result = subprocess.run([sys.executable, str(speed_script)], check=True,
                                    capture_output=True, text=True)
    speed_path = G2 / "build/c-firmware/20261015/main-lv-anim-speed-4505a2/receipt.json"
    speed = json.loads(speed_path.read_text())
    if speed["status"] != "PASS_EXPERIMENTAL_MAIN_LV_ANIM_SPEED_C":
        raise RuntimeError("animation speed stage status changed")
    base = file_from_receipt(speed, "base_object", "base_sha256")
    linked = file_from_receipt(speed, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 241 or len(imports(linked)) != 240 or \
            imports(base)-imports(linked) != {"audio_uart_lv_anim_duration_clamp_4505a2"} or \
            imports(linked)-imports(base):
        raise RuntimeError("animation speed stage handoff changed")
    if sha(ROOT / speed["source"]) != speed["source_sha256"]:
        raise RuntimeError("stale animation speed source")
    records.append({
        "stage": "main-lv-anim-speed-4505a2", "binder": str(speed_script.relative_to(ROOT)),
        "binder_sha256": sha(speed_script), "status": speed["status"],
        "binder_output": speed_result.stdout.strip(),
        "receipt": str(speed_path.relative_to(ROOT)), "receipt_sha256": sha(speed_path),
        "source": speed["source"], "source_sha256": speed["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 241, "unresolved_after": 240,
        "imports_resolved": ["audio_uart_lv_anim_duration_clamp_4505a2"],
        "imports_added": [],
    })
    previous = linked
    bezier_script = HERE / "bind_main_lv_anim_bezier_curve_48869a_20261015.py"
    bezier_result = subprocess.run([sys.executable, str(bezier_script)], check=True,
                                     capture_output=True, text=True)
    bezier_path = G2 / "build/c-firmware/20261015/main-lv-anim-bezier-curve-48869a/receipt.json"
    bezier = json.loads(bezier_path.read_text())
    if bezier["status"] != "PASS_EXPERIMENTAL_MAIN_LV_ANIM_BEZIER_CURVE_C":
        raise RuntimeError("Bezier solver stage status changed")
    base = file_from_receipt(bezier, "base_object", "base_sha256")
    linked = file_from_receipt(bezier, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 240 or len(imports(linked)) != 240 or \
            imports(base)-imports(linked) != {"audio_uart_lv_anim_bezier_curve_48869a"} or \
            imports(linked)-imports(base) != {"audio_uart_lv_div64_47cc1c"}:
        raise RuntimeError("Bezier solver stage handoff changed")
    if sha(ROOT / bezier["source"]) != bezier["source_sha256"]:
        raise RuntimeError("stale Bezier solver source")
    records.append({
        "stage": "main-lv-anim-bezier-curve-48869a", "binder": str(bezier_script.relative_to(ROOT)),
        "binder_sha256": sha(bezier_script), "status": bezier["status"],
        "binder_output": bezier_result.stdout.strip(),
        "receipt": str(bezier_path.relative_to(ROOT)), "receipt_sha256": sha(bezier_path),
        "source": bezier["source"], "source_sha256": bezier["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 240, "unresolved_after": 240,
        "imports_resolved": ["audio_uart_lv_anim_bezier_curve_48869a"],
        "imports_added": ["audio_uart_lv_div64_47cc1c"],
    })
    previous = linked
    div_script = HERE / "bind_main_lv_div64_47cc1c_20261015.py"
    div_result = subprocess.run([sys.executable, str(div_script)], check=True,
                                  capture_output=True, text=True)
    div_path = G2 / "build/c-firmware/20261015/main-lv-div64-47cc1c/receipt.json"
    div = json.loads(div_path.read_text())
    if div["status"] != "PASS_EXPERIMENTAL_MAIN_LV_DIV64_QUOTIENT_C":
        raise RuntimeError("signed quotient stage status changed")
    base = file_from_receipt(div, "base_object", "base_sha256")
    linked = file_from_receipt(div, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 240 or len(imports(linked)) != 239 or \
            imports(base)-imports(linked) != {"audio_uart_lv_div64_47cc1c"} or \
            imports(linked)-imports(base):
        raise RuntimeError("signed quotient stage handoff changed")
    if sha(ROOT / div["source"]) != div["source_sha256"]:
        raise RuntimeError("stale signed quotient source")
    records.append({
        "stage": "main-lv-div64-47cc1c", "binder": str(div_script.relative_to(ROOT)),
        "binder_sha256": sha(div_script), "status": div["status"],
        "binder_output": div_result.stdout.strip(),
        "receipt": str(div_path.relative_to(ROOT)), "receipt_sha256": sha(div_path),
        "source": div["source"], "source_sha256": div["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 240, "unresolved_after": 239,
        "imports_resolved": ["audio_uart_lv_div64_47cc1c"], "imports_added": [],
    })
    previous = linked
    start_script = HERE / "bind_main_lv_anim_start_450408_20261015.py"
    start_result = subprocess.run([sys.executable, str(start_script)], check=True,
                                    capture_output=True, text=True)
    start_path = G2 / "build/c-firmware/20261015/main-lv-anim-start-450408/receipt.json"
    start = json.loads(start_path.read_text())
    if start["status"] != "PASS_EXPERIMENTAL_MAIN_LV_ANIM_START_C":
        raise RuntimeError("animation start stage status changed")
    base = file_from_receipt(start, "base_object", "base_sha256")
    linked = file_from_receipt(start, "linked_object", "linked_sha256")
    start_lower = {"audio_uart_lv_anim_normalize_450a3e",
                   "audio_uart_lv_anim_cancel_matching_450a74"}
    if base != previous or len(imports(base)) != 239 or len(imports(linked)) != 240 or \
            imports(base)-imports(linked) != {"audio_uart_lv_anim_start_450408"} or \
            imports(linked)-imports(base) != start_lower:
        raise RuntimeError("animation start stage handoff changed")
    if sha(ROOT / start["source"]) != start["source_sha256"]:
        raise RuntimeError("stale animation start source")
    records.append({
        "stage": "main-lv-anim-start-450408", "binder": str(start_script.relative_to(ROOT)),
        "binder_sha256": sha(start_script), "status": start["status"],
        "binder_output": start_result.stdout.strip(),
        "receipt": str(start_path.relative_to(ROOT)), "receipt_sha256": sha(start_path),
        "source": start["source"], "source_sha256": start["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 239, "unresolved_after": 240,
        "imports_resolved": ["audio_uart_lv_anim_start_450408"],
        "imports_added": sorted(start_lower),
    })
    previous = linked
    normalize_script = HERE / "bind_main_lv_anim_normalize_4506fc_20261015.py"
    normalize_result = subprocess.run([sys.executable, str(normalize_script)], check=True,
                                        capture_output=True, text=True)
    normalize_path = G2 / "build/c-firmware/20261015/main-lv-anim-normalize-4506fc/receipt.json"
    normalize = json.loads(normalize_path.read_text())
    if normalize["status"] != "PASS_EXPERIMENTAL_MAIN_LV_ANIM_NORMALIZE_C":
        raise RuntimeError("animation normalize stage status changed")
    base = file_from_receipt(normalize, "base_object", "base_sha256")
    linked = file_from_receipt(normalize, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 240 or len(imports(linked)) != 239 or \
            imports(base)-imports(linked) != {"audio_uart_lv_anim_normalize_450a3e"} or \
            imports(linked)-imports(base):
        raise RuntimeError("animation normalize stage handoff changed")
    if sha(ROOT / normalize["source"]) != normalize["source_sha256"]:
        raise RuntimeError("stale animation normalize source")
    records.append({
        "stage": "main-lv-anim-normalize-4506fc",
        "binder": str(normalize_script.relative_to(ROOT)),
        "binder_sha256": sha(normalize_script), "status": normalize["status"],
        "binder_output": normalize_result.stdout.strip(),
        "receipt": str(normalize_path.relative_to(ROOT)),
        "receipt_sha256": sha(normalize_path),
        "source": normalize["source"], "source_sha256": normalize["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 240, "unresolved_after": 239,
        "imports_resolved": ["audio_uart_lv_anim_normalize_450a3e"],
        "imports_added": [],
    })
    previous = linked
    cancel_script = HERE / "bind_main_lv_anim_cancel_450a74_20261015.py"
    cancel_result = subprocess.run([sys.executable, str(cancel_script)], check=True,
                                     capture_output=True, text=True)
    cancel_path = G2 / "build/c-firmware/20261015/main-lv-anim-cancel-450a74/receipt.json"
    cancel = json.loads(cancel_path.read_text())
    if cancel["status"] != "PASS_EXPERIMENTAL_MAIN_LV_ANIM_CANCEL_C":
        raise RuntimeError("animation cancel stage status changed")
    base = file_from_receipt(cancel, "base_object", "base_sha256")
    linked = file_from_receipt(cancel, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 239 or len(imports(linked)) != 238 or \
            imports(base)-imports(linked) != {"audio_uart_lv_anim_cancel_matching_450a74"} or \
            imports(linked)-imports(base):
        raise RuntimeError("animation cancel stage handoff changed")
    if sha(ROOT / cancel["source"]) != cancel["source_sha256"]:
        raise RuntimeError("stale animation cancel source")
    records.append({
        "stage": "main-lv-anim-cancel-450a74", "binder": str(cancel_script.relative_to(ROOT)),
        "binder_sha256": sha(cancel_script), "status": cancel["status"],
        "binder_output": cancel_result.stdout.strip(),
        "receipt": str(cancel_path.relative_to(ROOT)), "receipt_sha256": sha(cancel_path),
        "source": cancel["source"], "source_sha256": cancel["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 239, "unresolved_after": 238,
        "imports_resolved": ["audio_uart_lv_anim_cancel_matching_450a74"],
        "imports_added": [],
    })
    previous = linked
    delete_script = HERE / "bind_main_lv_child_delete_44df80_20261015.py"
    delete_result = subprocess.run([sys.executable, str(delete_script)], check=True,
                                    capture_output=True, text=True)
    delete_path = G2 / "build/c-firmware/20261015/main-lv-child-delete-44df80/receipt.json"
    delete = json.loads(delete_path.read_text())
    if delete["status"] != "PASS_EXPERIMENTAL_MAIN_LV_CHILD_DELETE_C":
        raise RuntimeError("child deletion stage status changed")
    base = file_from_receipt(delete, "base_object", "base_sha256")
    linked = file_from_receipt(delete, "linked_object", "linked_sha256")
    resolved = {"audio_uart_lv_child_delete_44df80"}
    added = {"audio_uart_lv_child_index_44de92", "audio_uart_lv_cleanup_matching_484052",
             "audio_uart_lv_input_active_452ffa", "audio_uart_lv_input_unlink_44df60",
             "audio_uart_lv_obj_delete_cleanup_44d16e", "audio_uart_lv_obj_group_43e1be",
             "audio_uart_lv_style_destroy_450228", "audio_uart_page_delete_event_filter_44d7b8"}
    if base != previous or len(imports(base)) != 238 or len(imports(linked)) != 245 or \
            imports(base)-imports(linked) != resolved or \
            imports(linked)-imports(base) != added:
        raise RuntimeError("child deletion stage handoff changed")
    if sha(ROOT / delete["source"]) != delete["source_sha256"]:
        raise RuntimeError("stale child deletion source")
    records.append({
        "stage": "main-lv-child-delete-44df80", "binder": str(delete_script.relative_to(ROOT)),
        "binder_sha256": sha(delete_script), "status": delete["status"],
        "binder_output": delete_result.stdout.strip(),
        "receipt": str(delete_path.relative_to(ROOT)), "receipt_sha256": sha(delete_path),
        "source": delete["source"], "source_sha256": delete["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 238, "unresolved_after": 245,
        "imports_resolved": sorted(resolved), "imports_added": sorted(added),
    })
    previous = linked
    index_script = HERE / "bind_main_lv_child_index_44de92_20261015.py"
    index_result = subprocess.run([sys.executable, str(index_script)], check=True,
                                   capture_output=True, text=True)
    index_path = G2 / "build/c-firmware/20261015/main-lv-child-index-44de92/receipt.json"
    index_receipt = json.loads(index_path.read_text())
    if index_receipt["status"] != "PASS_EXPERIMENTAL_MAIN_LV_CHILD_INDEX_C":
        raise RuntimeError("child index stage status changed")
    base = file_from_receipt(index_receipt, "base_object", "base_sha256")
    linked = file_from_receipt(index_receipt, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 245 or len(imports(linked)) != 244 or \
            imports(base)-imports(linked) != {"audio_uart_lv_child_index_44de92"} or \
            imports(linked)-imports(base):
        raise RuntimeError("child index stage handoff changed")
    if sha(ROOT / index_receipt["source"]) != index_receipt["source_sha256"]:
        raise RuntimeError("stale child index source")
    records.append({
        "stage": "main-lv-child-index-44de92", "binder": str(index_script.relative_to(ROOT)),
        "binder_sha256": sha(index_script), "status": index_receipt["status"],
        "binder_output": index_result.stdout.strip(),
        "receipt": str(index_path.relative_to(ROOT)), "receipt_sha256": sha(index_path),
        "source": index_receipt["source"], "source_sha256": index_receipt["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 245, "unresolved_after": 244,
        "imports_resolved": ["audio_uart_lv_child_index_44de92"], "imports_added": [],
    })
    previous = linked
    group_script = HERE / "bind_main_lv_obj_group_43e1be_20261015.py"
    group_result = subprocess.run([sys.executable, str(group_script)], check=True,
                                   capture_output=True, text=True)
    group_path = G2 / "build/c-firmware/20261015/main-lv-obj-group-43e1be/receipt.json"
    group = json.loads(group_path.read_text())
    if group["status"] != "PASS_EXPERIMENTAL_MAIN_LV_OBJ_GROUP_C":
        raise RuntimeError("object group stage status changed")
    base = file_from_receipt(group, "base_object", "base_sha256")
    linked = file_from_receipt(group, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 244 or len(imports(linked)) != 243 or \
            imports(base)-imports(linked) != {"audio_uart_lv_obj_group_43e1be"} or \
            imports(linked)-imports(base):
        raise RuntimeError("object group stage handoff changed")
    if sha(ROOT / group["source"]) != group["source_sha256"]:
        raise RuntimeError("stale object group source")
    records.append({
        "stage": "main-lv-obj-group-43e1be", "binder": str(group_script.relative_to(ROOT)),
        "binder_sha256": sha(group_script), "status": group["status"],
        "binder_output": group_result.stdout.strip(),
        "receipt": str(group_path.relative_to(ROOT)), "receipt_sha256": sha(group_path),
        "source": group["source"], "source_sha256": group["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 244, "unresolved_after": 243,
        "imports_resolved": ["audio_uart_lv_obj_group_43e1be"], "imports_added": [],
    })
    previous = linked
    active_script = HERE / "bind_main_lv_input_active_452ffa_20261015.py"
    active_result = subprocess.run([sys.executable, str(active_script)], check=True,
                                    capture_output=True, text=True)
    active_path = G2 / "build/c-firmware/20261015/main-lv-input-active-452ffa/receipt.json"
    active = json.loads(active_path.read_text())
    if active["status"] != "PASS_EXPERIMENTAL_MAIN_LV_INPUT_ACTIVE_C":
        raise RuntimeError("input active stage status changed")
    base = file_from_receipt(active, "base_object", "base_sha256")
    linked = file_from_receipt(active, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 243 or len(imports(linked)) != 242 or \
            imports(base)-imports(linked) != {"audio_uart_lv_input_active_452ffa"} or \
            imports(linked)-imports(base):
        raise RuntimeError("input active stage handoff changed")
    if sha(ROOT / active["source"]) != active["source_sha256"]:
        raise RuntimeError("stale input active source")
    records.append({
        "stage": "main-lv-input-active-452ffa", "binder": str(active_script.relative_to(ROOT)),
        "binder_sha256": sha(active_script), "status": active["status"],
        "binder_output": active_result.stdout.strip(),
        "receipt": str(active_path.relative_to(ROOT)), "receipt_sha256": sha(active_path),
        "source": active["source"], "source_sha256": active["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 243, "unresolved_after": 242,
        "imports_resolved": ["audio_uart_lv_input_active_452ffa"], "imports_added": [],
    })
    previous = linked
    destroy_script = HERE / "bind_main_lv_style_destroy_450228_20261015.py"
    destroy_result = subprocess.run([sys.executable, str(destroy_script)], check=True,
                                     capture_output=True, text=True)
    destroy_path = G2 / "build/c-firmware/20261015/main-lv-style-destroy-450228/receipt.json"
    destroy = json.loads(destroy_path.read_text())
    if destroy["status"] != "PASS_EXPERIMENTAL_MAIN_LV_STYLE_DESTROY_C":
        raise RuntimeError("style destroy stage status changed")
    base = file_from_receipt(destroy, "base_object", "base_sha256")
    linked = file_from_receipt(destroy, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 242 or len(imports(linked)) != 241 or \
            imports(base)-imports(linked) != {"audio_uart_lv_style_destroy_450228"} or \
            imports(linked)-imports(base):
        raise RuntimeError("style destroy stage handoff changed")
    if sha(ROOT / destroy["source"]) != destroy["source_sha256"]:
        raise RuntimeError("stale style destroy source")
    records.append({
        "stage": "main-lv-style-destroy-450228", "binder": str(destroy_script.relative_to(ROOT)),
        "binder_sha256": sha(destroy_script), "status": destroy["status"],
        "binder_output": destroy_result.stdout.strip(),
        "receipt": str(destroy_path.relative_to(ROOT)), "receipt_sha256": sha(destroy_path),
        "source": destroy["source"], "source_sha256": destroy["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 242, "unresolved_after": 241,
        "imports_resolved": ["audio_uart_lv_style_destroy_450228"], "imports_added": [],
    })
    previous = linked
    cleanup_script = HERE / "bind_main_lv_obj_delete_cleanup_44d16e_20261015.py"
    cleanup_result = subprocess.run([sys.executable, str(cleanup_script)], check=True,
                                     capture_output=True, text=True)
    cleanup_path = G2 / "build/c-firmware/20261015/main-lv-obj-delete-cleanup-44d16e/receipt.json"
    cleanup = json.loads(cleanup_path.read_text())
    if cleanup["status"] != "PASS_EXPERIMENTAL_MAIN_LV_OBJ_DELETE_CLEANUP_C":
        raise RuntimeError("object cleanup stage status changed")
    base = file_from_receipt(cleanup, "base_object", "base_sha256")
    linked = file_from_receipt(cleanup, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 241 or len(imports(linked)) != 240 or \
            imports(base)-imports(linked) != {"audio_uart_lv_obj_delete_cleanup_44d16e"} or \
            imports(linked)-imports(base):
        raise RuntimeError("object cleanup stage handoff changed")
    if sha(ROOT / cleanup["source"]) != cleanup["source_sha256"]:
        raise RuntimeError("stale object cleanup source")
    records.append({
        "stage": "main-lv-obj-delete-cleanup-44d16e",
        "binder": str(cleanup_script.relative_to(ROOT)),
        "binder_sha256": sha(cleanup_script), "status": cleanup["status"],
        "binder_output": cleanup_result.stdout.strip(),
        "receipt": str(cleanup_path.relative_to(ROOT)), "receipt_sha256": sha(cleanup_path),
        "source": cleanup["source"], "source_sha256": cleanup["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 241, "unresolved_after": 240,
        "imports_resolved": ["audio_uart_lv_obj_delete_cleanup_44d16e"], "imports_added": [],
    })
    previous = linked
    unlink_script = HERE / "bind_main_lv_input_unlink_44df60_20261015.py"
    unlink_result = subprocess.run([sys.executable, str(unlink_script)], check=True,
                                    capture_output=True, text=True)
    unlink_path = G2 / "build/c-firmware/20261015/main-lv-input-unlink-44df60/receipt.json"
    unlink = json.loads(unlink_path.read_text())
    if unlink["status"] != "PASS_EXPERIMENTAL_MAIN_LV_INPUT_UNLINK_C":
        raise RuntimeError("input unlink stage status changed")
    base = file_from_receipt(unlink, "base_object", "base_sha256")
    linked = file_from_receipt(unlink, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 240 or len(imports(linked)) != 240 or \
            imports(base)-imports(linked) != {"audio_uart_lv_input_unlink_44df60"} or \
            imports(linked)-imports(base) != {"audio_uart_lv_input_clear_452f26"}:
        raise RuntimeError("input unlink stage handoff changed")
    if sha(ROOT / unlink["source"]) != unlink["source_sha256"]:
        raise RuntimeError("stale input unlink source")
    records.append({
        "stage": "main-lv-input-unlink-44df60", "binder": str(unlink_script.relative_to(ROOT)),
        "binder_sha256": sha(unlink_script), "status": unlink["status"],
        "binder_output": unlink_result.stdout.strip(),
        "receipt": str(unlink_path.relative_to(ROOT)), "receipt_sha256": sha(unlink_path),
        "source": unlink["source"], "source_sha256": unlink["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 240, "unresolved_after": 240,
        "imports_resolved": ["audio_uart_lv_input_unlink_44df60"],
        "imports_added": ["audio_uart_lv_input_clear_452f26"],
    })
    previous = linked
    clear_script = HERE / "bind_main_lv_input_clear_452f26_20261015.py"
    clear_result = subprocess.run([sys.executable, str(clear_script)], check=True,
                                   capture_output=True, text=True)
    clear_path = G2 / "build/c-firmware/20261015/main-lv-input-clear-452f26/receipt.json"
    clear = json.loads(clear_path.read_text())
    if clear["status"] != "PASS_EXPERIMENTAL_MAIN_LV_INPUT_CLEAR_C":
        raise RuntimeError("input clear stage status changed")
    base = file_from_receipt(clear, "base_object", "base_sha256")
    linked = file_from_receipt(clear, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 240 or len(imports(linked)) != 240 or \
            imports(base)-imports(linked) != {"audio_uart_lv_input_clear_452f26"} or \
            imports(linked)-imports(base) != {"audio_uart_lv_input_event_453002"}:
        raise RuntimeError("input clear stage handoff changed")
    if sha(ROOT / clear["source"]) != clear["source_sha256"]:
        raise RuntimeError("stale input clear source")
    records.append({
        "stage": "main-lv-input-clear-452f26", "binder": str(clear_script.relative_to(ROOT)),
        "binder_sha256": sha(clear_script), "status": clear["status"],
        "binder_output": clear_result.stdout.strip(),
        "receipt": str(clear_path.relative_to(ROOT)), "receipt_sha256": sha(clear_path),
        "source": clear["source"], "source_sha256": clear["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 240, "unresolved_after": 240,
        "imports_resolved": ["audio_uart_lv_input_clear_452f26"],
        "imports_added": ["audio_uart_lv_input_event_453002"],
    })
    previous = linked
    input_event_script = HERE / "bind_main_lv_input_event_453002_20261015.py"
    input_event_result = subprocess.run([sys.executable, str(input_event_script)], check=True,
                                        capture_output=True, text=True)
    input_event_path = G2 / "build/c-firmware/20261015/main-lv-input-event-453002/receipt.json"
    input_event = json.loads(input_event_path.read_text())
    if input_event["status"] != "PASS_EXPERIMENTAL_MAIN_LV_INPUT_EVENT_C":
        raise RuntimeError("input event stage status changed")
    base = file_from_receipt(input_event, "base_object", "base_sha256")
    linked = file_from_receipt(input_event, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 240 or len(imports(linked)) != 239 or \
            imports(base)-imports(linked) != {"audio_uart_lv_input_event_453002"} or \
            imports(linked)-imports(base):
        raise RuntimeError("input event stage handoff changed")
    if sha(ROOT / input_event["source"]) != input_event["source_sha256"]:
        raise RuntimeError("stale input event source")
    records.append({
        "stage": "main-lv-input-event-453002",
        "binder": str(input_event_script.relative_to(ROOT)),
        "binder_sha256": sha(input_event_script), "status": input_event["status"],
        "binder_output": input_event_result.stdout.strip(),
        "receipt": str(input_event_path.relative_to(ROOT)),
        "receipt_sha256": sha(input_event_path),
        "source": input_event["source"], "source_sha256": input_event["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 240, "unresolved_after": 239,
        "imports_resolved": ["audio_uart_lv_input_event_453002"], "imports_added": [],
    })
    previous = linked
    matching_script = HERE / "bind_main_lv_cleanup_matching_484052_20261015.py"
    matching_result = subprocess.run([sys.executable, str(matching_script)], check=True,
                                      capture_output=True, text=True)
    matching_path = G2 / "build/c-firmware/20261015/main-lv-cleanup-matching-484052/receipt.json"
    matching = json.loads(matching_path.read_text())
    if matching["status"] != "PASS_EXPERIMENTAL_MAIN_LV_CLEANUP_MATCHING_C":
        raise RuntimeError("cleanup matching stage status changed")
    base = file_from_receipt(matching, "base_object", "base_sha256")
    linked = file_from_receipt(matching, "linked_object", "linked_sha256")
    timer_added = {"audio_uart_lv_timer_iter_4645ec", "audio_uart_lv_timer_remove_4644ee"}
    if base != previous or len(imports(base)) != 239 or len(imports(linked)) != 240 or \
            imports(base)-imports(linked) != {"audio_uart_lv_cleanup_matching_484052"} or \
            imports(linked)-imports(base) != timer_added:
        raise RuntimeError("cleanup matching stage handoff changed")
    if sha(ROOT / matching["source"]) != matching["source_sha256"]:
        raise RuntimeError("stale cleanup matching source")
    records.append({
        "stage": "main-lv-cleanup-matching-484052",
        "binder": str(matching_script.relative_to(ROOT)),
        "binder_sha256": sha(matching_script), "status": matching["status"],
        "binder_output": matching_result.stdout.strip(),
        "receipt": str(matching_path.relative_to(ROOT)),
        "receipt_sha256": sha(matching_path),
        "source": matching["source"], "source_sha256": matching["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 239, "unresolved_after": 240,
        "imports_resolved": ["audio_uart_lv_cleanup_matching_484052"],
        "imports_added": sorted(timer_added),
    })
    previous = linked
    timer_script = HERE / "bind_main_lv_timer_helpers_4645ec_20261015.py"
    timer_result = subprocess.run([sys.executable, str(timer_script)], check=True,
                                   capture_output=True, text=True)
    timer_path = G2 / "build/c-firmware/20261015/main-lv-timer-helpers-4645ec/receipt.json"
    timer = json.loads(timer_path.read_text())
    if timer["status"] != "PASS_EXPERIMENTAL_MAIN_LV_TIMER_HELPERS_C":
        raise RuntimeError("timer helpers stage status changed")
    base = file_from_receipt(timer, "base_object", "base_sha256")
    linked = file_from_receipt(timer, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 240 or len(imports(linked)) != 238 or \
            imports(base)-imports(linked) != timer_added or \
            imports(linked)-imports(base):
        raise RuntimeError("timer helpers stage handoff changed")
    if sha(ROOT / timer["source"]) != timer["source_sha256"]:
        raise RuntimeError("stale timer helpers source")
    records.append({
        "stage": "main-lv-timer-helpers-4645ec", "binder": str(timer_script.relative_to(ROOT)),
        "binder_sha256": sha(timer_script), "status": timer["status"],
        "binder_output": timer_result.stdout.strip(),
        "receipt": str(timer_path.relative_to(ROOT)), "receipt_sha256": sha(timer_path),
        "source": timer["source"], "source_sha256": timer["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 240, "unresolved_after": 238,
        "imports_resolved": sorted(timer_added), "imports_added": [],
    })
    previous = linked
    delete_filter_script = HERE / "bind_main_lv_delete_filter_44d7b8_20261015.py"
    delete_filter_result = subprocess.run([sys.executable, str(delete_filter_script)], check=True,
                                          capture_output=True, text=True)
    delete_filter_path = G2 / "build/c-firmware/20261015/main-lv-delete-filter-44d7b8/receipt.json"
    delete_filter = json.loads(delete_filter_path.read_text())
    if delete_filter["status"] != "PASS_EXPERIMENTAL_MAIN_LV_DELETE_FILTER_C":
        raise RuntimeError("delete filter stage status changed")
    base = file_from_receipt(delete_filter, "base_object", "base_sha256")
    linked = file_from_receipt(delete_filter, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 238 or len(imports(linked)) != 236 or \
            imports(base)-imports(linked) != {"audio_uart_page_delete_event_filter_44d7b8",
                                              "audio_uart_display_object_delete"} or \
            imports(linked)-imports(base):
        raise RuntimeError("delete filter stage handoff changed")
    if sha(ROOT / delete_filter["source"]) != delete_filter["source_sha256"]:
        raise RuntimeError("stale delete filter source")
    records.append({
        "stage": "main-lv-delete-filter-44d7b8",
        "binder": str(delete_filter_script.relative_to(ROOT)),
        "binder_sha256": sha(delete_filter_script), "status": delete_filter["status"],
        "binder_output": delete_filter_result.stdout.strip(),
        "receipt": str(delete_filter_path.relative_to(ROOT)),
        "receipt_sha256": sha(delete_filter_path),
        "source": delete_filter["source"], "source_sha256": delete_filter["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 238, "unresolved_after": 236,
        "imports_resolved": ["audio_uart_display_object_delete",
                             "audio_uart_page_delete_event_filter_44d7b8"],
        "imports_added": [],
    })
    previous = linked
    flush_script = HERE / "bind_main_display_flush_4736f4_20261015.py"
    flush_result = subprocess.run([sys.executable, str(flush_script)], check=True,
                                  capture_output=True, text=True)
    flush_path = G2 / "build/c-firmware/20261015/main-display-flush-4736f4/receipt.json"
    flush = json.loads(flush_path.read_text())
    if flush["status"] != "PASS_EXPERIMENTAL_MAIN_DISPLAY_FLUSH_C":
        raise RuntimeError("display flush stage status changed")
    base = file_from_receipt(flush, "base_object", "base_sha256")
    linked = file_from_receipt(flush, "linked_object", "linked_sha256")
    flush_added = {"audio_uart_display_area_copy_439c04", "audio_uart_display_area_x_44fb4e",
                   "audio_uart_display_area_y_44fb9a", "audio_uart_display_flush_begin_47381e",
                   "audio_uart_display_flush_end_47386a", "audio_uart_display_flush_ready_44fc42",
                   "audio_uart_display_flush_transfer_47366c",
                   "audio_uart_display_flush_view_474066"}
    if base != previous or len(imports(base)) != 236 or len(imports(linked)) != 243 or \
            imports(base)-imports(linked) != {"audio_uart_display_flush_callback"} or \
            imports(linked)-imports(base) != flush_added:
        raise RuntimeError("display flush stage handoff changed")
    if sha(ROOT / flush["source"]) != flush["source_sha256"]:
        raise RuntimeError("stale display flush source")
    records.append({
        "stage": "main-display-flush-4736f4", "binder": str(flush_script.relative_to(ROOT)),
        "binder_sha256": sha(flush_script), "status": flush["status"],
        "binder_output": flush_result.stdout.strip(),
        "receipt": str(flush_path.relative_to(ROOT)), "receipt_sha256": sha(flush_path),
        "source": flush["source"], "source_sha256": flush["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 236, "unresolved_after": 243,
        "imports_resolved": ["audio_uart_display_flush_callback"],
        "imports_added": sorted(flush_added),
    })
    previous = linked
    geometry_script = HERE / "bind_main_display_flush_geometry_44fb4e_20261015.py"
    geometry_result = subprocess.run([sys.executable, str(geometry_script)], check=True,
                                     capture_output=True, text=True)
    geometry_path = G2 / "build/c-firmware/20261015/main-display-flush-geometry-44fb4e/receipt.json"
    geometry = json.loads(geometry_path.read_text())
    if geometry["status"] != "PASS_EXPERIMENTAL_MAIN_DISPLAY_FLUSH_GEOMETRY_C":
        raise RuntimeError("display flush geometry stage status changed")
    base = file_from_receipt(geometry, "base_object", "base_sha256")
    linked = file_from_receipt(geometry, "linked_object", "linked_sha256")
    geometry_resolved = {"audio_uart_display_area_copy_439c04",
                         "audio_uart_display_area_x_44fb4e",
                         "audio_uart_display_area_y_44fb9a",
                         "audio_uart_display_flush_ready_44fc42"}
    if base != previous or len(imports(base)) != 243 or len(imports(linked)) != 239 or \
            imports(base)-imports(linked) != geometry_resolved or \
            imports(linked)-imports(base):
        raise RuntimeError("display flush geometry stage handoff changed")
    if sha(ROOT / geometry["source"]) != geometry["source_sha256"]:
        raise RuntimeError("stale display flush geometry source")
    records.append({
        "stage": "main-display-flush-geometry-44fb4e",
        "binder": str(geometry_script.relative_to(ROOT)),
        "binder_sha256": sha(geometry_script), "status": geometry["status"],
        "binder_output": geometry_result.stdout.strip(),
        "receipt": str(geometry_path.relative_to(ROOT)),
        "receipt_sha256": sha(geometry_path),
        "source": geometry["source"], "source_sha256": geometry["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 243, "unresolved_after": 239,
        "imports_resolved": sorted(geometry_resolved), "imports_added": [],
    })
    previous = linked
    lock_script = HERE / "bind_main_display_flush_lock_47381e_20261015.py"
    lock_result = subprocess.run([sys.executable, str(lock_script)], check=True,
                                 capture_output=True, text=True)
    lock_path = G2 / "build/c-firmware/20261015/main-display-flush-lock-47381e/receipt.json"
    lock = json.loads(lock_path.read_text())
    if lock["status"] != "PASS_EXPERIMENTAL_MAIN_DISPLAY_FLUSH_LOCK_C":
        raise RuntimeError("display flush lock stage status changed")
    base = file_from_receipt(lock, "base_object", "base_sha256")
    linked = file_from_receipt(lock, "linked_object", "linked_sha256")
    lock_resolved = {"audio_uart_display_flush_begin_47381e",
                     "audio_uart_display_flush_end_47386a"}
    if base != previous or len(imports(base)) != 239 or len(imports(linked)) != 238 or \
            imports(base)-imports(linked) != lock_resolved or \
            imports(linked)-imports(base) != {"audio_uart_display_in_isr_442228"}:
        raise RuntimeError("display flush lock stage handoff changed")
    if sha(ROOT / lock["source"]) != lock["source_sha256"]:
        raise RuntimeError("stale display flush lock source")
    records.append({
        "stage": "main-display-flush-lock-47381e",
        "binder": str(lock_script.relative_to(ROOT)),
        "binder_sha256": sha(lock_script), "status": lock["status"],
        "binder_output": lock_result.stdout.strip(),
        "receipt": str(lock_path.relative_to(ROOT)), "receipt_sha256": sha(lock_path),
        "source": lock["source"], "source_sha256": lock["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 239, "unresolved_after": 238,
        "imports_resolved": sorted(lock_resolved),
        "imports_added": ["audio_uart_display_in_isr_442228"],
    })
    previous = linked
    isr_script = HERE / "bind_main_display_in_isr_442228_20261015.py"
    isr_result = subprocess.run([sys.executable, str(isr_script)], check=True,
                                capture_output=True, text=True)
    isr_path = G2 / "build/c-firmware/20261015/main-display-in-isr-442228/receipt.json"
    isr = json.loads(isr_path.read_text())
    if isr["status"] != "PASS_EXPERIMENTAL_MAIN_DISPLAY_IN_ISR_C":
        raise RuntimeError("display ISR stage status changed")
    base = file_from_receipt(isr, "base_object", "base_sha256")
    linked = file_from_receipt(isr, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 238 or len(imports(linked)) != 237 or \
            imports(base)-imports(linked) != {"audio_uart_display_in_isr_442228"} or \
            imports(linked)-imports(base):
        raise RuntimeError("display ISR stage handoff changed")
    if sha(ROOT / isr["source"]) != isr["source_sha256"]:
        raise RuntimeError("stale display ISR source")
    records.append({
        "stage": "main-display-in-isr-442228", "binder": str(isr_script.relative_to(ROOT)),
        "binder_sha256": sha(isr_script), "status": isr["status"],
        "binder_output": isr_result.stdout.strip(),
        "receipt": str(isr_path.relative_to(ROOT)), "receipt_sha256": sha(isr_path),
        "source": isr["source"], "source_sha256": isr["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 238, "unresolved_after": 237,
        "imports_resolved": ["audio_uart_display_in_isr_442228"], "imports_added": [],
    })
    previous = linked
    transfer_script = HERE / "bind_main_display_flush_transfer_47366c_20261015.py"
    transfer_result = subprocess.run([sys.executable, str(transfer_script)], check=True,
                                     capture_output=True, text=True)
    transfer_path = G2 / "build/c-firmware/20261015/main-display-flush-transfer-47366c/receipt.json"
    transfer = json.loads(transfer_path.read_text())
    if transfer["status"] != "PASS_EXPERIMENTAL_MAIN_DISPLAY_FLUSH_TRANSFER_C":
        raise RuntimeError("display transfer stage status changed")
    base = file_from_receipt(transfer, "base_object", "base_sha256")
    linked = file_from_receipt(transfer, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 237 or len(imports(linked)) != 237 or \
            imports(base)-imports(linked) != {"audio_uart_display_flush_transfer_47366c"} or \
            imports(linked)-imports(base) != {"audio_uart_display_frame_transfer_5fa13c"}:
        raise RuntimeError("display transfer stage handoff changed")
    if sha(ROOT / transfer["source"]) != transfer["source_sha256"]:
        raise RuntimeError("stale display transfer source")
    records.append({
        "stage": "main-display-flush-transfer-47366c",
        "binder": str(transfer_script.relative_to(ROOT)),
        "binder_sha256": sha(transfer_script), "status": transfer["status"],
        "binder_output": transfer_result.stdout.strip(),
        "receipt": str(transfer_path.relative_to(ROOT)), "receipt_sha256": sha(transfer_path),
        "source": transfer["source"], "source_sha256": transfer["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 237, "unresolved_after": 237,
        "imports_resolved": ["audio_uart_display_flush_transfer_47366c"],
        "imports_added": ["audio_uart_display_frame_transfer_5fa13c"],
    })
    previous = linked
    frame_script = HERE / "bind_main_display_frame_transfer_5fa13c_20261015.py"
    frame_result = subprocess.run([sys.executable, str(frame_script)], check=True,
                                  capture_output=True, text=True)
    frame_path = G2 / "build/c-firmware/20261015/main-display-frame-transfer-5fa13c/receipt.json"
    frame = json.loads(frame_path.read_text())
    if frame["status"] != "PASS_EXPERIMENTAL_MAIN_DISPLAY_FRAME_TRANSFER_C":
        raise RuntimeError("display frame transfer stage status changed")
    base = file_from_receipt(frame, "base_object", "base_sha256")
    linked = file_from_receipt(frame, "linked_object", "linked_sha256")
    frame_added = {"audio_uart_display_graphics_blend_513924",
                   "audio_uart_display_graphics_finish_4b1548",
                   "audio_uart_display_graphics_target_4b1516"}
    if base != previous or len(imports(base)) != 237 or len(imports(linked)) != 239 or \
            imports(base)-imports(linked) != {"audio_uart_display_frame_transfer_5fa13c"} or \
            imports(linked)-imports(base) != frame_added:
        raise RuntimeError("display frame transfer stage handoff changed")
    if sha(ROOT / frame["source"]) != frame["source_sha256"]:
        raise RuntimeError("stale display frame transfer source")
    records.append({
        "stage": "main-display-frame-transfer-5fa13c",
        "binder": str(frame_script.relative_to(ROOT)),
        "binder_sha256": sha(frame_script), "status": frame["status"],
        "binder_output": frame_result.stdout.strip(),
        "receipt": str(frame_path.relative_to(ROOT)), "receipt_sha256": sha(frame_path),
        "source": frame["source"], "source_sha256": frame["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 237, "unresolved_after": 239,
        "imports_resolved": ["audio_uart_display_frame_transfer_5fa13c"],
        "imports_added": sorted(frame_added),
    })
    previous = linked
    target_script = HERE / "bind_main_display_graphics_target_4b1516_20261015.py"
    target_result = subprocess.run([sys.executable, str(target_script)], check=True,
                                   capture_output=True, text=True)
    target_path = G2 / "build/c-firmware/20261015/main-display-graphics-target-4b1516/receipt.json"
    target = json.loads(target_path.read_text())
    if target["status"] != "PASS_EXPERIMENTAL_MAIN_DISPLAY_GRAPHICS_TARGET_C":
        raise RuntimeError("graphics target stage status changed")
    base = file_from_receipt(target, "base_object", "base_sha256")
    linked = file_from_receipt(target, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 239 or len(imports(linked)) != 238 or \
            imports(base)-imports(linked) != {"audio_uart_display_graphics_target_4b1516"} or \
            imports(linked)-imports(base):
        raise RuntimeError("graphics target stage handoff changed")
    if sha(ROOT / target["source"]) != target["source_sha256"]:
        raise RuntimeError("stale graphics target source")
    records.append({
        "stage": "main-display-graphics-target-4b1516",
        "binder": str(target_script.relative_to(ROOT)),
        "binder_sha256": sha(target_script), "status": target["status"],
        "binder_output": target_result.stdout.strip(),
        "receipt": str(target_path.relative_to(ROOT)), "receipt_sha256": sha(target_path),
        "source": target["source"], "source_sha256": target["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 239, "unresolved_after": 238,
        "imports_resolved": ["audio_uart_display_graphics_target_4b1516"],
        "imports_added": [],
    })
    previous = linked
    finish_script = HERE / "bind_main_display_graphics_finish_4b1548_20261015.py"
    finish_result = subprocess.run([sys.executable, str(finish_script)], check=True,
                                   capture_output=True, text=True)
    finish_path = G2 / "build/c-firmware/20261015/main-display-graphics-finish-4b1548/receipt.json"
    finish = json.loads(finish_path.read_text())
    if finish["status"] != "PASS_EXPERIMENTAL_MAIN_DISPLAY_GRAPHICS_FINISH_C":
        raise RuntimeError("graphics finish stage status changed")
    base = file_from_receipt(finish, "base_object", "base_sha256")
    linked = file_from_receipt(finish, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 238 or len(imports(linked)) != 237 or \
            imports(base)-imports(linked) != {"audio_uart_display_graphics_finish_4b1548"} or \
            imports(linked)-imports(base):
        raise RuntimeError("graphics finish stage handoff changed")
    if sha(ROOT / finish["source"]) != finish["source_sha256"]:
        raise RuntimeError("stale graphics finish source")
    records.append({
        "stage": "main-display-graphics-finish-4b1548",
        "binder": str(finish_script.relative_to(ROOT)),
        "binder_sha256": sha(finish_script), "status": finish["status"],
        "binder_output": finish_result.stdout.strip(),
        "receipt": str(finish_path.relative_to(ROOT)), "receipt_sha256": sha(finish_path),
        "source": finish["source"], "source_sha256": finish["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 238, "unresolved_after": 237,
        "imports_resolved": ["audio_uart_display_graphics_finish_4b1548"],
        "imports_added": [],
    })
    previous = linked
    view_script = HERE / "bind_main_display_flush_view_474066_20261015.py"
    view_result = subprocess.run([sys.executable, str(view_script)], check=True,
                                 capture_output=True, text=True)
    view_path = G2 / "build/c-firmware/20261015/main-display-flush-view-474066/receipt.json"
    view = json.loads(view_path.read_text())
    if view["status"] != "PASS_EXPERIMENTAL_MAIN_DISPLAY_FLUSH_VIEW_C":
        raise RuntimeError("display view stage status changed")
    base = file_from_receipt(view, "base_object", "base_sha256")
    linked = file_from_receipt(view, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 237 or len(imports(linked)) != 237 or \
            imports(base)-imports(linked) != {"audio_uart_display_flush_view_474066"} or \
            imports(linked)-imports(base) != {"audio_uart_display_manager_queue_cell"}:
        raise RuntimeError("display view stage handoff changed")
    if sha(ROOT / view["source"]) != view["source_sha256"]:
        raise RuntimeError("stale display view source")
    records.append({
        "stage": "main-display-flush-view-474066",
        "binder": str(view_script.relative_to(ROOT)),
        "binder_sha256": sha(view_script), "status": view["status"],
        "binder_output": view_result.stdout.strip(),
        "receipt": str(view_path.relative_to(ROOT)), "receipt_sha256": sha(view_path),
        "source": view["source"], "source_sha256": view["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 237, "unresolved_after": 237,
        "imports_resolved": ["audio_uart_display_flush_view_474066"],
        "imports_added": ["audio_uart_display_manager_queue_cell"],
    })
    previous = linked
    queue_script = HERE / "bind_main_display_manager_queue_cell_20000664_20261015.py"
    queue_result = subprocess.run([sys.executable, str(queue_script)], check=True,
                                  capture_output=True, text=True)
    queue_path = G2 / "build/c-firmware/20261015/main-display-manager-queue-cell-20000664/receipt.json"
    queue = json.loads(queue_path.read_text())
    if queue["status"] != "PASS_EXPERIMENTAL_MAIN_DISPLAY_MANAGER_QUEUE_CELL_C":
        raise RuntimeError("display queue cell stage status changed")
    base = file_from_receipt(queue, "base_object", "base_sha256")
    linked = file_from_receipt(queue, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 237 or len(imports(linked)) != 236 or \
            imports(base)-imports(linked) != {"audio_uart_display_manager_queue_cell"} or \
            imports(linked)-imports(base):
        raise RuntimeError("display queue cell stage handoff changed")
    if sha(ROOT / queue["source"]) != queue["source_sha256"]:
        raise RuntimeError("stale display queue cell source")
    records.append({
        "stage": "main-display-manager-queue-cell-20000664",
        "binder": str(queue_script.relative_to(ROOT)),
        "binder_sha256": sha(queue_script), "status": queue["status"],
        "binder_output": queue_result.stdout.strip(),
        "receipt": str(queue_path.relative_to(ROOT)), "receipt_sha256": sha(queue_path),
        "source": queue["source"], "source_sha256": queue["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 237, "unresolved_after": 236,
        "imports_resolved": ["audio_uart_display_manager_queue_cell"],
        "imports_added": [],
    })
    previous = linked
    board_script = HERE / "bind_main_display_board_callback_444684_20261015.py"
    board_result = subprocess.run([sys.executable, str(board_script)], check=True,
                                  capture_output=True, text=True)
    board_path = G2 / "build/c-firmware/20261015/main-display-board-callback-444684/receipt.json"
    board = json.loads(board_path.read_text())
    if board["status"] != "PASS_EXPERIMENTAL_MAIN_DISPLAY_BOARD_CALLBACK_C":
        raise RuntimeError("display board callback stage status changed")
    base = file_from_receipt(board, "base_object", "base_sha256")
    linked = file_from_receipt(board, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 236 or len(imports(linked)) != 235 or \
            imports(base)-imports(linked) != {"audio_uart_display_board_data"} or \
            imports(linked)-imports(base):
        raise RuntimeError("display board callback stage handoff changed")
    if sha(ROOT / board["source"]) != board["source_sha256"]:
        raise RuntimeError("stale display board callback source")
    records.append({
        "stage": "main-display-board-callback-444684",
        "binder": str(board_script.relative_to(ROOT)),
        "binder_sha256": sha(board_script), "status": board["status"],
        "binder_output": board_result.stdout.strip(),
        "receipt": str(board_path.relative_to(ROOT)), "receipt_sha256": sha(board_path),
        "source": board["source"], "source_sha256": board["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 236, "unresolved_after": 235,
        "imports_resolved": ["audio_uart_display_board_data"], "imports_added": [],
    })
    previous = linked
    style_script = HERE / "bind_main_display_page_style_755610_20261015.py"
    style_result = subprocess.run([sys.executable, str(style_script)], check=True,
                                  capture_output=True, text=True)
    style_path = G2 / "build/c-firmware/20261015/main-display-page-style-755610/receipt.json"
    style = json.loads(style_path.read_text())
    if style["status"] != "PASS_EXPERIMENTAL_MAIN_DISPLAY_PAGE_STYLE_C":
        raise RuntimeError("display page style stage status changed")
    base = file_from_receipt(style, "base_object", "base_sha256")
    linked = file_from_receipt(style, "linked_object", "linked_sha256")
    style_added = {"audio_uart_lv_font_glyph_bitmap_4b239c",
                   "audio_uart_lv_font_glyph_dsc_4b26a4"}
    if base != previous or len(imports(base)) != 235 or len(imports(linked)) != 236 or \
            imports(base)-imports(linked) != {"audio_uart_display_page_style"} or \
            imports(linked)-imports(base) != style_added:
        raise RuntimeError("display page style stage handoff changed")
    if sha(ROOT / style["source"]) != style["source_sha256"]:
        raise RuntimeError("stale display page style source")
    records.append({
        "stage": "main-display-page-style-755610",
        "binder": str(style_script.relative_to(ROOT)),
        "binder_sha256": sha(style_script), "status": style["status"],
        "binder_output": style_result.stdout.strip(),
        "receipt": str(style_path.relative_to(ROOT)), "receipt_sha256": sha(style_path),
        "source": style["source"], "source_sha256": style["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 235, "unresolved_after": 236,
        "imports_resolved": ["audio_uart_display_page_style"],
        "imports_added": sorted(style_added),
    })
    previous = linked
    glyph_script = HERE / "bind_main_lv_font_glyph_dsc_4b26a4_20261015.py"
    glyph_result = subprocess.run([sys.executable, str(glyph_script)], check=True,
                                  capture_output=True, text=True)
    glyph_path = G2 / "build/c-firmware/20261015/main-lv-font-glyph-dsc-4b26a4/receipt.json"
    glyph = json.loads(glyph_path.read_text())
    if glyph["status"] != "PASS_EXPERIMENTAL_MAIN_LV_FONT_GLYPH_DSC_C":
        raise RuntimeError("LV glyph descriptor stage status changed")
    base = file_from_receipt(glyph, "base_object", "base_sha256")
    linked = file_from_receipt(glyph, "linked_object", "linked_sha256")
    glyph_added = {"audio_uart_lv_font_kerning_4b28ee",
                   "audio_uart_lv_font_lookup_4b2774"}
    if base != previous or len(imports(base)) != 236 or len(imports(linked)) != 237 or \
            imports(base)-imports(linked) != {"audio_uart_lv_font_glyph_dsc_4b26a4"} or \
            imports(linked)-imports(base) != glyph_added:
        raise RuntimeError("LV glyph descriptor stage handoff changed")
    if sha(ROOT / glyph["source"]) != glyph["source_sha256"]:
        raise RuntimeError("stale LV glyph descriptor source")
    records.append({
        "stage": "main-lv-font-glyph-dsc-4b26a4",
        "binder": str(glyph_script.relative_to(ROOT)),
        "binder_sha256": sha(glyph_script), "status": glyph["status"],
        "binder_output": glyph_result.stdout.strip(),
        "receipt": str(glyph_path.relative_to(ROOT)), "receipt_sha256": sha(glyph_path),
        "source": glyph["source"], "source_sha256": glyph["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 236, "unresolved_after": 237,
        "imports_resolved": ["audio_uart_lv_font_glyph_dsc_4b26a4"],
        "imports_added": sorted(glyph_added),
    })
    previous = linked
    kerning_script = HERE / "bind_main_lv_font_kerning_4b28ee_20261015.py"
    kerning_result = subprocess.run([sys.executable, str(kerning_script)], check=True,
                                    capture_output=True, text=True)
    kerning_path = G2 / "build/c-firmware/20261015/main-lv-font-kerning-4b28ee/receipt.json"
    kerning = json.loads(kerning_path.read_text())
    if kerning["status"] != "PASS_EXPERIMENTAL_MAIN_LV_FONT_KERNING_C":
        raise RuntimeError("LV font kerning stage status changed")
    base = file_from_receipt(kerning, "base_object", "base_sha256")
    linked = file_from_receipt(kerning, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 237 or len(imports(linked)) != 237 or \
            imports(base)-imports(linked) != {"audio_uart_lv_font_kerning_4b28ee"} or \
            imports(linked)-imports(base) != {"audio_uart_lv_font_pair_search_52a284"}:
        raise RuntimeError("LV font kerning stage handoff changed")
    if sha(ROOT / kerning["source"]) != kerning["source_sha256"]:
        raise RuntimeError("stale LV font kerning source")
    records.append({
        "stage": "main-lv-font-kerning-4b28ee",
        "binder": str(kerning_script.relative_to(ROOT)),
        "binder_sha256": sha(kerning_script), "status": kerning["status"],
        "binder_output": kerning_result.stdout.strip(),
        "receipt": str(kerning_path.relative_to(ROOT)), "receipt_sha256": sha(kerning_path),
        "source": kerning["source"], "source_sha256": kerning["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 237, "unresolved_after": 237,
        "imports_resolved": ["audio_uart_lv_font_kerning_4b28ee"],
        "imports_added": ["audio_uart_lv_font_pair_search_52a284"],
    })
    previous = linked
    search_script = HERE / "bind_main_lv_font_pair_search_52a284_20261015.py"
    search_result = subprocess.run([sys.executable, str(search_script)], check=True,
                                   capture_output=True, text=True)
    search_path = G2 / "build/c-firmware/20261015/main-lv-font-pair-search-52a284/receipt.json"
    search = json.loads(search_path.read_text())
    if search["status"] != "PASS_EXPERIMENTAL_MAIN_LV_FONT_PAIR_SEARCH_C":
        raise RuntimeError("LV font pair search stage status changed")
    base = file_from_receipt(search, "base_object", "base_sha256")
    linked = file_from_receipt(search, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 237 or len(imports(linked)) != 236 or \
            imports(base)-imports(linked) != {"audio_uart_lv_font_pair_search_52a284"} or \
            imports(linked)-imports(base):
        raise RuntimeError("LV font pair search stage handoff changed")
    if sha(ROOT / search["source"]) != search["source_sha256"]:
        raise RuntimeError("stale LV font pair search source")
    records.append({
        "stage": "main-lv-font-pair-search-52a284",
        "binder": str(search_script.relative_to(ROOT)),
        "binder_sha256": sha(search_script), "status": search["status"],
        "binder_output": search_result.stdout.strip(),
        "receipt": str(search_path.relative_to(ROOT)), "receipt_sha256": sha(search_path),
        "source": search["source"], "source_sha256": search["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 237, "unresolved_after": 236,
        "imports_resolved": ["audio_uart_lv_font_pair_search_52a284"],
        "imports_added": [],
    })
    previous = linked
    lookup_script = HERE / "bind_main_lv_font_lookup_4b2774_20261015.py"
    lookup_result = subprocess.run([sys.executable, str(lookup_script)], check=True,
                                   capture_output=True, text=True)
    lookup_path = G2 / "build/c-firmware/20261015/main-lv-font-lookup-4b2774/receipt.json"
    lookup = json.loads(lookup_path.read_text())
    if lookup["status"] != "PASS_EXPERIMENTAL_MAIN_LV_FONT_LOOKUP_C":
        raise RuntimeError("LV font lookup stage status changed")
    base = file_from_receipt(lookup, "base_object", "base_sha256")
    linked = file_from_receipt(lookup, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 236 or len(imports(linked)) != 235 or \
            imports(base)-imports(linked) != {"audio_uart_lv_font_lookup_4b2774"} or \
            imports(linked)-imports(base):
        raise RuntimeError("LV font lookup stage handoff changed")
    if sha(ROOT / lookup["source"]) != lookup["source_sha256"]:
        raise RuntimeError("stale LV font lookup source")
    records.append({
        "stage": "main-lv-font-lookup-4b2774",
        "binder": str(lookup_script.relative_to(ROOT)),
        "binder_sha256": sha(lookup_script), "status": lookup["status"],
        "binder_output": lookup_result.stdout.strip(),
        "receipt": str(lookup_path.relative_to(ROOT)), "receipt_sha256": sha(lookup_path),
        "source": lookup["source"], "source_sha256": lookup["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 236, "unresolved_after": 235,
        "imports_resolved": ["audio_uart_lv_font_lookup_4b2774"],
        "imports_added": [],
    })
    previous = linked
    bitmap_script = HERE / "bind_main_lv_font_bitmap_4b239c_20261015.py"
    bitmap_result = subprocess.run([sys.executable, str(bitmap_script)], check=True,
                                   capture_output=True, text=True)
    bitmap_path = G2 / "build/c-firmware/20261015/main-lv-font-bitmap-4b239c/receipt.json"
    bitmap = json.loads(bitmap_path.read_text())
    if bitmap["status"] != "PASS_EXPERIMENTAL_MAIN_LV_FONT_BITMAP_C":
        raise RuntimeError("LV font bitmap stage status changed")
    base = file_from_receipt(bitmap, "base_object", "base_sha256")
    linked = file_from_receipt(bitmap, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 235 or len(imports(linked)) != 234 or \
            imports(base)-imports(linked) != {"audio_uart_lv_font_glyph_bitmap_4b239c"} or \
            imports(linked)-imports(base):
        raise RuntimeError("LV font bitmap stage handoff changed")
    if sha(ROOT / bitmap["source"]) != bitmap["source_sha256"]:
        raise RuntimeError("stale LV font bitmap source")
    records.append({
        "stage": "main-lv-font-bitmap-4b239c",
        "binder": str(bitmap_script.relative_to(ROOT)),
        "binder_sha256": sha(bitmap_script), "status": bitmap["status"],
        "binder_output": bitmap_result.stdout.strip(),
        "receipt": str(bitmap_path.relative_to(ROOT)), "receipt_sha256": sha(bitmap_path),
        "source": bitmap["source"], "source_sha256": bitmap["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 235, "unresolved_after": 234,
        "imports_resolved": ["audio_uart_lv_font_glyph_bitmap_4b239c"],
        "imports_added": [],
    })
    previous = linked
    factory499416_script = HERE / "bind_main_page_factory_499416_20261015.py"
    factory499416_result = subprocess.run([sys.executable, str(factory499416_script)], check=True,
                                         capture_output=True, text=True)
    factory499416_path = G2 / "build/c-firmware/20261015/main-page-factory-499416/receipt.json"
    factory499416 = json.loads(factory499416_path.read_text())
    if factory499416["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_FACTORY_499416_C":
        raise RuntimeError("page factory 499416 stage status changed")
    base = file_from_receipt(factory499416, "base_object", "base_sha256")
    linked = file_from_receipt(factory499416, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 234 or len(imports(linked)) != 236 or \
            imports(base)-imports(linked) != {"audio_uart_page_499416"} or \
            imports(linked)-imports(base) != {"audio_uart_page_class_ctor_49a0c0",
                                             "audio_uart_page_class_dtor_49a150",
                                             "audio_uart_page_class_event_49a16e"}:
        raise RuntimeError("page factory 499416 stage handoff changed")
    if sha(ROOT / factory499416["source"]) != factory499416["source_sha256"]:
        raise RuntimeError("stale page factory 499416 source")
    if sha(ROOT / factory499416["class_source"]) != factory499416["class_source_sha256"]:
        raise RuntimeError("stale page class 7561bc source")
    records.append({
        "stage": "main-page-factory-499416",
        "binder": str(factory499416_script.relative_to(ROOT)),
        "binder_sha256": sha(factory499416_script), "status": factory499416["status"],
        "binder_output": factory499416_result.stdout.strip(),
        "receipt": str(factory499416_path.relative_to(ROOT)),
        "receipt_sha256": sha(factory499416_path),
        "source": factory499416["source"], "source_sha256": factory499416["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 234, "unresolved_after": 236,
        "imports_resolved": ["audio_uart_page_499416"],
        "imports_added": ["audio_uart_page_class_ctor_49a0c0",
                          "audio_uart_page_class_dtor_49a150",
                          "audio_uart_page_class_event_49a16e"],
    })
    previous = linked
    class_lifecycle_script = HERE / "bind_main_page_class_lifecycle_49a0c0_20261015.py"
    class_lifecycle_result = subprocess.run([sys.executable, str(class_lifecycle_script)],
                                            check=True, capture_output=True, text=True)
    class_lifecycle_path = G2 / "build/c-firmware/20261015/main-page-class-lifecycle-49a0c0/receipt.json"
    class_lifecycle = json.loads(class_lifecycle_path.read_text())
    if class_lifecycle["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_CLASS_LIFECYCLE_C":
        raise RuntimeError("page class lifecycle stage status changed")
    base = file_from_receipt(class_lifecycle, "base_object", "base_sha256")
    linked = file_from_receipt(class_lifecycle, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 236 or len(imports(linked)) != 235 or \
            imports(base)-imports(linked) != {"audio_uart_page_class_ctor_49a0c0",
                                               "audio_uart_page_class_dtor_49a150"} or \
            imports(linked)-imports(base) != {"audio_uart_page_layout_499678"}:
        raise RuntimeError("page class lifecycle stage handoff changed")
    if sha(ROOT / class_lifecycle["source"]) != class_lifecycle["source_sha256"]:
        raise RuntimeError("stale page class lifecycle source")
    records.append({
        "stage": "main-page-class-lifecycle-49a0c0",
        "binder": str(class_lifecycle_script.relative_to(ROOT)),
        "binder_sha256": sha(class_lifecycle_script), "status": class_lifecycle["status"],
        "binder_output": class_lifecycle_result.stdout.strip(),
        "receipt": str(class_lifecycle_path.relative_to(ROOT)),
        "receipt_sha256": sha(class_lifecycle_path),
        "source": class_lifecycle["source"],
        "source_sha256": class_lifecycle["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 236, "unresolved_after": 235,
        "imports_resolved": ["audio_uart_page_class_ctor_49a0c0",
                             "audio_uart_page_class_dtor_49a150"],
        "imports_added": ["audio_uart_page_layout_499678"],
    })
    previous = linked
    page_layout_script = HERE / "bind_main_page_layout_499678_20261015.py"
    page_layout_result = subprocess.run([sys.executable, str(page_layout_script)],
                                        check=True, capture_output=True, text=True)
    page_layout_path = G2 / "build/c-firmware/20261015/main-page-layout-499678/receipt.json"
    page_layout = json.loads(page_layout_path.read_text())
    if page_layout["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_LAYOUT_C":
        raise RuntimeError("page layout stage status changed")
    base = file_from_receipt(page_layout, "base_object", "base_sha256")
    linked = file_from_receipt(page_layout, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 235 or len(imports(linked)) != 235 or \
            imports(base)-imports(linked) != {"audio_uart_page_layout_499678"} or \
            imports(linked)-imports(base) != {"audio_uart_page_layout_update_49a602"}:
        raise RuntimeError("page layout stage handoff changed")
    if sha(ROOT / page_layout["source"]) != page_layout["source_sha256"]:
        raise RuntimeError("stale page layout source")
    records.append({
        "stage": "main-page-layout-499678",
        "binder": str(page_layout_script.relative_to(ROOT)),
        "binder_sha256": sha(page_layout_script), "status": page_layout["status"],
        "binder_output": page_layout_result.stdout.strip(),
        "receipt": str(page_layout_path.relative_to(ROOT)),
        "receipt_sha256": sha(page_layout_path),
        "source": page_layout["source"], "source_sha256": page_layout["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 235, "unresolved_after": 235,
        "imports_resolved": ["audio_uart_page_layout_499678"],
        "imports_added": ["audio_uart_page_layout_update_49a602"],
    })
    previous = linked
    event_script = HERE / "bind_main_page_class_event_49a16e_20261015.py"
    event_result = subprocess.run([sys.executable, str(event_script)], check=True,
                                  capture_output=True, text=True)
    event_path = G2 / "build/c-firmware/20261015/main-page-class-event-49a16e/receipt.json"
    event = json.loads(event_path.read_text())
    if event["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_CLASS_EVENT_C":
        raise RuntimeError("page class event stage status changed")
    base = file_from_receipt(event, "base_object", "base_sha256")
    linked = file_from_receipt(event, "linked_object", "linked_sha256")
    event_added = {"audio_uart_page_event_calculate_489546",
                   "audio_uart_page_event_code_450286",
                   "audio_uart_page_event_dispatch_49a31c",
                   "audio_uart_page_event_extent_4519fa",
                   "audio_uart_page_event_finish_49ab06",
                   "audio_uart_page_event_prepare_49aacc",
                   "audio_uart_page_metric_499360", "audio_uart_page_metric_49936a",
                   "audio_uart_page_metric_499374", "audio_uart_page_metric_4993c0",
                   "audio_uart_page_metric_4993ca", "audio_uart_page_metric_4993d4"}
    if base != previous or len(imports(base)) != 235 or len(imports(linked)) != 246 or \
            imports(base)-imports(linked) != {"audio_uart_page_class_event_49a16e"} or \
            imports(linked)-imports(base) != event_added:
        raise RuntimeError("page class event stage handoff changed")
    if sha(ROOT / event["source"]) != event["source_sha256"]:
        raise RuntimeError("stale page class event source")
    records.append({
        "stage": "main-page-class-event-49a16e",
        "binder": str(event_script.relative_to(ROOT)), "binder_sha256": sha(event_script),
        "status": event["status"], "binder_output": event_result.stdout.strip(),
        "receipt": str(event_path.relative_to(ROOT)), "receipt_sha256": sha(event_path),
        "source": event["source"], "source_sha256": event["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 235, "unresolved_after": 246,
        "imports_resolved": ["audio_uart_page_class_event_49a16e"],
        "imports_added": sorted(event_added),
    })
    previous = linked
    getters_script = HERE / "bind_main_page_metric_getters_499360_20261015.py"
    getters_result = subprocess.run([sys.executable, str(getters_script)], check=True,
                                    capture_output=True, text=True)
    getters_path = G2 / "build/c-firmware/20261015/main-page-metric-getters-499360/receipt.json"
    getters = json.loads(getters_path.read_text())
    if getters["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_METRIC_GETTERS_C":
        raise RuntimeError("page metric getters stage status changed")
    base = file_from_receipt(getters, "base_object", "base_sha256")
    linked = file_from_receipt(getters, "linked_object", "linked_sha256")
    getter_set = {"audio_uart_page_metric_499360", "audio_uart_page_metric_49936a",
                  "audio_uart_page_metric_499374", "audio_uart_page_metric_4993c0",
                  "audio_uart_page_metric_4993ca", "audio_uart_page_metric_4993d4"}
    if base != previous or len(imports(base)) != 246 or len(imports(linked)) != 240 or \
            imports(base)-imports(linked) != getter_set or imports(linked)-imports(base):
        raise RuntimeError("page metric getters stage handoff changed")
    if sha(ROOT / getters["source"]) != getters["source_sha256"]:
        raise RuntimeError("stale page metric getters source")
    records.append({
        "stage": "main-page-metric-getters-499360",
        "binder": str(getters_script.relative_to(ROOT)), "binder_sha256": sha(getters_script),
        "status": getters["status"], "binder_output": getters_result.stdout.strip(),
        "receipt": str(getters_path.relative_to(ROOT)), "receipt_sha256": sha(getters_path),
        "source": getters["source"], "source_sha256": getters["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 246, "unresolved_after": 240,
        "imports_resolved": sorted(getter_set), "imports_added": [],
    })
    previous = linked
    event_helpers_script = HERE / "bind_main_page_event_helpers_450286_20261015.py"
    event_helpers_result = subprocess.run([sys.executable, str(event_helpers_script)],
                                          check=True, capture_output=True, text=True)
    event_helpers_path = G2 / "build/c-firmware/20261015/main-page-event-helpers-450286/receipt.json"
    event_helpers = json.loads(event_helpers_path.read_text())
    if event_helpers["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_EVENT_HELPERS_C":
        raise RuntimeError("page event helpers stage status changed")
    base = file_from_receipt(event_helpers, "base_object", "base_sha256")
    linked = file_from_receipt(event_helpers, "linked_object", "linked_sha256")
    helper_set = {"audio_uart_page_event_code_450286",
                  "audio_uart_page_event_extent_4519fa",
                  "audio_uart_page_event_prepare_49aacc"}
    if base != previous or len(imports(base)) != 240 or len(imports(linked)) != 237 or \
            imports(base)-imports(linked) != helper_set or imports(linked)-imports(base):
        raise RuntimeError("page event helpers stage handoff changed")
    if sha(ROOT / event_helpers["source"]) != event_helpers["source_sha256"]:
        raise RuntimeError("stale page event helpers source")
    records.append({
        "stage": "main-page-event-helpers-450286",
        "binder": str(event_helpers_script.relative_to(ROOT)),
        "binder_sha256": sha(event_helpers_script), "status": event_helpers["status"],
        "binder_output": event_helpers_result.stdout.strip(),
        "receipt": str(event_helpers_path.relative_to(ROOT)),
        "receipt_sha256": sha(event_helpers_path),
        "source": event_helpers["source"],
        "source_sha256": event_helpers["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 240, "unresolved_after": 237,
        "imports_resolved": sorted(helper_set), "imports_added": [],
    })
    previous = linked
    finish_script = HERE / "bind_main_page_event_finish_49ab06_20261015.py"
    finish_result = subprocess.run([sys.executable, str(finish_script)], check=True,
                                   capture_output=True, text=True)
    finish_path = G2 / "build/c-firmware/20261015/main-page-event-finish-49ab06/receipt.json"
    finish = json.loads(finish_path.read_text())
    if finish["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_EVENT_FINISH_C":
        raise RuntimeError("page event finish stage status changed")
    base = file_from_receipt(finish, "base_object", "base_sha256")
    linked = file_from_receipt(finish, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 237 or len(imports(linked)) != 236 or \
            imports(base)-imports(linked) != {"audio_uart_page_event_finish_49ab06"} or \
            imports(linked)-imports(base):
        raise RuntimeError("page event finish stage handoff changed")
    if sha(ROOT / finish["source"]) != finish["source_sha256"]:
        raise RuntimeError("stale page event finish source")
    records.append({
        "stage": "main-page-event-finish-49ab06",
        "binder": str(finish_script.relative_to(ROOT)),
        "binder_sha256": sha(finish_script), "status": finish["status"],
        "binder_output": finish_result.stdout.strip(),
        "receipt": str(finish_path.relative_to(ROOT)),
        "receipt_sha256": sha(finish_path),
        "source": finish["source"], "source_sha256": finish["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 237, "unresolved_after": 236,
        "imports_resolved": ["audio_uart_page_event_finish_49ab06"], "imports_added": [],
    })
    previous = linked
    text_size_script = HERE / "bind_main_page_text_size_489546_20261015.py"
    text_size_result = subprocess.run([sys.executable, str(text_size_script)], check=True,
                                      capture_output=True, text=True)
    text_size_path = G2 / "build/c-firmware/20261015/main-page-text-size-489546/receipt.json"
    text_size = json.loads(text_size_path.read_text())
    if text_size["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_SIZE_C":
        raise RuntimeError("page text size stage status changed")
    base = file_from_receipt(text_size, "base_object", "base_sha256")
    linked = file_from_receipt(text_size, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 236 or len(imports(linked)) != 237 or \
            imports(base)-imports(linked) != {"audio_uart_page_event_calculate_489546"} or \
            imports(linked)-imports(base) != {"audio_uart_text_line_length_4897fc",
                                             "audio_uart_text_line_width_489934"}:
        raise RuntimeError("page text size stage handoff changed")
    if sha(ROOT / text_size["source"]) != text_size["source_sha256"]:
        raise RuntimeError("stale page text size source")
    records.append({
        "stage": "main-page-text-size-489546",
        "binder": str(text_size_script.relative_to(ROOT)),
        "binder_sha256": sha(text_size_script), "status": text_size["status"],
        "binder_output": text_size_result.stdout.strip(),
        "receipt": str(text_size_path.relative_to(ROOT)),
        "receipt_sha256": sha(text_size_path),
        "source": text_size["source"], "source_sha256": text_size["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 236, "unresolved_after": 237,
        "imports_resolved": ["audio_uart_page_event_calculate_489546"],
        "imports_added": ["audio_uart_text_line_length_4897fc",
                          "audio_uart_text_line_width_489934"],
    })
    previous = linked
    line_width_script = HERE / "bind_main_page_text_line_width_489934_20261015.py"
    line_width_result = subprocess.run([sys.executable, str(line_width_script)], check=True,
                                       capture_output=True, text=True)
    line_width_path = G2 / "build/c-firmware/20261015/main-page-text-line-width-489934/receipt.json"
    line_width = json.loads(line_width_path.read_text())
    if line_width["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_LINE_WIDTH_C":
        raise RuntimeError("page text line width stage status changed")
    base = file_from_receipt(line_width, "base_object", "base_sha256")
    linked = file_from_receipt(line_width, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 237 or len(imports(linked)) != 238 or \
            imports(base)-imports(linked) != {"audio_uart_text_line_width_489934"} or \
            imports(linked)-imports(base) != {"audio_uart_text_next_glyph_489b3c",
                                             "audio_uart_font_glyph_advance_4d57f4"}:
        raise RuntimeError("page text line width stage handoff changed")
    if sha(ROOT / line_width["source"]) != line_width["source_sha256"]:
        raise RuntimeError("stale page text line width source")
    records.append({
        "stage": "main-page-text-line-width-489934",
        "binder": str(line_width_script.relative_to(ROOT)),
        "binder_sha256": sha(line_width_script), "status": line_width["status"],
        "binder_output": line_width_result.stdout.strip(),
        "receipt": str(line_width_path.relative_to(ROOT)),
        "receipt_sha256": sha(line_width_path),
        "source": line_width["source"], "source_sha256": line_width["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 237, "unresolved_after": 238,
        "imports_resolved": ["audio_uart_text_line_width_489934"],
        "imports_added": ["audio_uart_text_next_glyph_489b3c",
                          "audio_uart_font_glyph_advance_4d57f4"],
    })
    previous = linked
    line_length_script = HERE / "bind_main_page_text_line_length_4897fc_20261015.py"
    line_length_result = subprocess.run([sys.executable, str(line_length_script)], check=True,
                                        capture_output=True, text=True)
    line_length_path = G2 / "build/c-firmware/20261015/main-page-text-line-length-4897fc/receipt.json"
    line_length = json.loads(line_length_path.read_text())
    if line_length["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_LINE_LENGTH_C":
        raise RuntimeError("page text line length stage status changed")
    base = file_from_receipt(line_length, "base_object", "base_sha256")
    linked = file_from_receipt(line_length, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 238 or len(imports(linked)) != 239 or \
            imports(base)-imports(linked) != {"audio_uart_text_line_length_4897fc"} or \
            imports(linked)-imports(base) != {"audio_uart_text_line_segment_489698",
                                             "audio_uart_text_decode_489c5e"}:
        raise RuntimeError("page text line length stage handoff changed")
    if sha(ROOT / line_length["source"]) != line_length["source_sha256"]:
        raise RuntimeError("stale page text line length source")
    records.append({
        "stage": "main-page-text-line-length-4897fc",
        "binder": str(line_length_script.relative_to(ROOT)),
        "binder_sha256": sha(line_length_script), "status": line_length["status"],
        "binder_output": line_length_result.stdout.strip(),
        "receipt": str(line_length_path.relative_to(ROOT)),
        "receipt_sha256": sha(line_length_path),
        "source": line_length["source"], "source_sha256": line_length["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 238, "unresolved_after": 239,
        "imports_resolved": ["audio_uart_text_line_length_4897fc"],
        "imports_added": ["audio_uart_text_line_segment_489698",
                          "audio_uart_text_decode_489c5e"],
    })
    previous = linked
    decode_script = HERE / "bind_main_page_text_decode_489c5e_20261015.py"
    decode_result = subprocess.run([sys.executable, str(decode_script)], check=True,
                                   capture_output=True, text=True)
    decode_path = G2 / "build/c-firmware/20261015/main-page-text-decode-489c5e/receipt.json"
    decode = json.loads(decode_path.read_text())
    if decode["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_DECODE_C":
        raise RuntimeError("page text decoder stage status changed")
    base = file_from_receipt(decode, "base_object", "base_sha256")
    linked = file_from_receipt(decode, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 239 or len(imports(linked)) != 238 or \
            imports(base)-imports(linked) != {"audio_uart_text_decode_489c5e"} or \
            imports(linked)-imports(base):
        raise RuntimeError("page text decoder stage handoff changed")
    if sha(ROOT / decode["source"]) != decode["source_sha256"]:
        raise RuntimeError("stale page text decoder source")
    records.append({
        "stage": "main-page-text-decode-489c5e",
        "binder": str(decode_script.relative_to(ROOT)),
        "binder_sha256": sha(decode_script), "status": decode["status"],
        "binder_output": decode_result.stdout.strip(),
        "receipt": str(decode_path.relative_to(ROOT)),
        "receipt_sha256": sha(decode_path),
        "source": decode["source"], "source_sha256": decode["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 239, "unresolved_after": 238,
        "imports_resolved": ["audio_uart_text_decode_489c5e"],
        "imports_added": [],
    })
    previous = linked
    next_glyph_script = HERE / "bind_main_page_text_next_glyph_489b3c_20261015.py"
    next_glyph_result = subprocess.run([sys.executable, str(next_glyph_script)], check=True,
                                       capture_output=True, text=True)
    next_glyph_path = G2 / "build/c-firmware/20261015/main-page-text-next-glyph-489b3c/receipt.json"
    next_glyph = json.loads(next_glyph_path.read_text())
    if next_glyph["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_NEXT_GLYPH_C":
        raise RuntimeError("page text next glyph stage status changed")
    base = file_from_receipt(next_glyph, "base_object", "base_sha256")
    linked = file_from_receipt(next_glyph, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 238 or len(imports(linked)) != 237 or \
            imports(base)-imports(linked) != {"audio_uart_text_next_glyph_489b3c"} or \
            imports(linked)-imports(base):
        raise RuntimeError("page text next glyph stage handoff changed")
    if sha(ROOT / next_glyph["source"]) != next_glyph["source_sha256"]:
        raise RuntimeError("stale page text next glyph source")
    records.append({
        "stage": "main-page-text-next-glyph-489b3c",
        "binder": str(next_glyph_script.relative_to(ROOT)),
        "binder_sha256": sha(next_glyph_script), "status": next_glyph["status"],
        "binder_output": next_glyph_result.stdout.strip(),
        "receipt": str(next_glyph_path.relative_to(ROOT)),
        "receipt_sha256": sha(next_glyph_path),
        "source": next_glyph["source"], "source_sha256": next_glyph["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 238, "unresolved_after": 237,
        "imports_resolved": ["audio_uart_text_next_glyph_489b3c"],
        "imports_added": [],
    })
    previous = linked
    glyph_advance_script = HERE / "bind_main_page_font_glyph_advance_4d57f4_20261015.py"
    glyph_advance_result = subprocess.run([sys.executable, str(glyph_advance_script)], check=True,
                                          capture_output=True, text=True)
    glyph_advance_path = G2 / "build/c-firmware/20261015/main-page-font-glyph-advance-4d57f4/receipt.json"
    glyph_advance = json.loads(glyph_advance_path.read_text())
    if glyph_advance["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_FONT_GLYPH_ADVANCE_C":
        raise RuntimeError("page font glyph advance stage status changed")
    base = file_from_receipt(glyph_advance, "base_object", "base_sha256")
    linked = file_from_receipt(glyph_advance, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 237 or len(imports(linked)) != 238 or \
            imports(base)-imports(linked) != {"audio_uart_font_glyph_advance_4d57f4"} or \
            imports(linked)-imports(base) != {"audio_uart_font_glyph_is_missing_4d559c",
                                             "audio_uart_font_glyph_describe_4d56c0"}:
        raise RuntimeError("page font glyph advance stage handoff changed")
    if sha(ROOT / glyph_advance["source"]) != glyph_advance["source_sha256"]:
        raise RuntimeError("stale page font glyph advance source")
    records.append({
        "stage": "main-page-font-glyph-advance-4d57f4",
        "binder": str(glyph_advance_script.relative_to(ROOT)),
        "binder_sha256": sha(glyph_advance_script), "status": glyph_advance["status"],
        "binder_output": glyph_advance_result.stdout.strip(),
        "receipt": str(glyph_advance_path.relative_to(ROOT)),
        "receipt_sha256": sha(glyph_advance_path),
        "source": glyph_advance["source"], "source_sha256": glyph_advance["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 237, "unresolved_after": 238,
        "imports_resolved": ["audio_uart_font_glyph_advance_4d57f4"],
        "imports_added": ["audio_uart_font_glyph_is_missing_4d559c",
                          "audio_uart_font_glyph_describe_4d56c0"],
    })
    previous = linked
    glyph_missing_script = HERE / "bind_main_page_font_glyph_missing_4d559c_20261015.py"
    glyph_missing_result = subprocess.run([sys.executable, str(glyph_missing_script)], check=True,
                                          capture_output=True, text=True)
    glyph_missing_path = G2 / "build/c-firmware/20261015/main-page-font-glyph-missing-4d559c/receipt.json"
    glyph_missing = json.loads(glyph_missing_path.read_text())
    if glyph_missing["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_FONT_GLYPH_MISSING_C":
        raise RuntimeError("page font glyph missing stage status changed")
    base = file_from_receipt(glyph_missing, "base_object", "base_sha256")
    linked = file_from_receipt(glyph_missing, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 238 or len(imports(linked)) != 237 or \
            imports(base)-imports(linked) != {"audio_uart_font_glyph_is_missing_4d559c"} or \
            imports(linked)-imports(base):
        raise RuntimeError("page font glyph missing stage handoff changed")
    if sha(ROOT / glyph_missing["source"]) != glyph_missing["source_sha256"]:
        raise RuntimeError("stale page font glyph missing source")
    records.append({
        "stage": "main-page-font-glyph-missing-4d559c",
        "binder": str(glyph_missing_script.relative_to(ROOT)),
        "binder_sha256": sha(glyph_missing_script), "status": glyph_missing["status"],
        "binder_output": glyph_missing_result.stdout.strip(),
        "receipt": str(glyph_missing_path.relative_to(ROOT)),
        "receipt_sha256": sha(glyph_missing_path),
        "source": glyph_missing["source"], "source_sha256": glyph_missing["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 238, "unresolved_after": 237,
        "imports_resolved": ["audio_uart_font_glyph_is_missing_4d559c"],
        "imports_added": [],
    })
    previous = linked
    glyph_describe_script = HERE / "bind_main_page_font_glyph_describe_4d56c0_20261015.py"
    glyph_describe_result = subprocess.run([sys.executable, str(glyph_describe_script)], check=True,
                                           capture_output=True, text=True)
    glyph_describe_path = G2 / "build/c-firmware/20261015/main-page-font-glyph-describe-4d56c0/receipt.json"
    glyph_describe = json.loads(glyph_describe_path.read_text())
    if glyph_describe["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_FONT_GLYPH_DESCRIBE_C":
        raise RuntimeError("page font glyph describe stage status changed")
    base = file_from_receipt(glyph_describe, "base_object", "base_sha256")
    linked = file_from_receipt(glyph_describe, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 237 or len(imports(linked)) != 238 or \
            imports(base)-imports(linked) != {"audio_uart_font_glyph_describe_4d56c0"} or \
            imports(linked)-imports(base) != {"audio_uart_font_resource_enter_46f65e",
                                             "audio_uart_font_resource_leave_46f674"}:
        raise RuntimeError("page font glyph describe stage handoff changed")
    if sha(ROOT / glyph_describe["source"]) != glyph_describe["source_sha256"]:
        raise RuntimeError("stale page font glyph describe source")
    records.append({
        "stage": "main-page-font-glyph-describe-4d56c0",
        "binder": str(glyph_describe_script.relative_to(ROOT)),
        "binder_sha256": sha(glyph_describe_script), "status": glyph_describe["status"],
        "binder_output": glyph_describe_result.stdout.strip(),
        "receipt": str(glyph_describe_path.relative_to(ROOT)),
        "receipt_sha256": sha(glyph_describe_path),
        "source": glyph_describe["source"], "source_sha256": glyph_describe["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 237, "unresolved_after": 238,
        "imports_resolved": ["audio_uart_font_glyph_describe_4d56c0"],
        "imports_added": ["audio_uart_font_resource_enter_46f65e",
                          "audio_uart_font_resource_leave_46f674"],
    })
    previous = linked
    resource_alias_script = HERE / "bind_main_page_font_resource_aliases_20261015.py"
    resource_alias_result = subprocess.run([sys.executable, str(resource_alias_script)], check=True,
                                           capture_output=True, text=True)
    resource_alias_path = G2 / "build/c-firmware/20261015/main-page-font-resource-aliases/receipt.json"
    resource_alias = json.loads(resource_alias_path.read_text())
    if resource_alias["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_FONT_RESOURCE_ALIASES_C":
        raise RuntimeError("page font resource alias stage status changed")
    base = file_from_receipt(resource_alias, "base_object", "base_sha256")
    linked = file_from_receipt(resource_alias, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 238 or len(imports(linked)) != 236 or \
            imports(base)-imports(linked) != {"audio_uart_font_resource_enter_46f65e",
                                             "audio_uart_font_resource_leave_46f674"} or \
            imports(linked)-imports(base):
        raise RuntimeError("page font resource alias stage handoff changed")
    if sha(ROOT / resource_alias["source"]) != resource_alias["source_sha256"]:
        raise RuntimeError("stale page font resource alias source")
    records.append({
        "stage": "main-page-font-resource-aliases",
        "binder": str(resource_alias_script.relative_to(ROOT)),
        "binder_sha256": sha(resource_alias_script), "status": resource_alias["status"],
        "binder_output": resource_alias_result.stdout.strip(),
        "receipt": str(resource_alias_path.relative_to(ROOT)),
        "receipt_sha256": sha(resource_alias_path),
        "source": resource_alias["source"], "source_sha256": resource_alias["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 238, "unresolved_after": 236,
        "imports_resolved": ["audio_uart_font_resource_enter_46f65e",
                             "audio_uart_font_resource_leave_46f674"],
        "imports_added": [],
    })
    previous = linked
    segment_script = HERE / "bind_main_page_text_line_segment_489698_20261015.py"
    segment_result = subprocess.run([sys.executable, str(segment_script)], check=True,
                                    capture_output=True, text=True)
    segment_path = G2 / "build/c-firmware/20261015/main-page-text-line-segment-489698/receipt.json"
    segment = json.loads(segment_path.read_text())
    if segment["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_LINE_SEGMENT_C":
        raise RuntimeError("page text line segment stage status changed")
    base = file_from_receipt(segment, "base_object", "base_sha256")
    linked = file_from_receipt(segment, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 236 or len(imports(linked)) != 235 or \
            imports(base)-imports(linked) != {"audio_uart_text_line_segment_489698"} or \
            imports(linked)-imports(base):
        raise RuntimeError("page text line segment stage handoff changed")
    if len(segment["sources"]) != 4 or len(segment["oracle_receipts"]) != 4:
        raise RuntimeError("page text line segment source count changed")
    for item in segment["sources"]:
        if sha(ROOT / item["path"]) != item["sha256"] or \
                sha(ROOT / item["object"]) != item["object_sha256"]:
            raise RuntimeError("stale page text segment source or object")
    for item in segment["oracle_receipts"]:
        if sha(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError("stale page text segment oracle")
    records.append({
        "stage": "main-page-text-line-segment-489698",
        "binder": str(segment_script.relative_to(ROOT)),
        "binder_sha256": sha(segment_script), "status": segment["status"],
        "binder_output": segment_result.stdout.strip(),
        "receipt": str(segment_path.relative_to(ROOT)),
        "receipt_sha256": sha(segment_path),
        "sources": segment["sources"], "oracle_receipts": segment["oracle_receipts"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 236, "unresolved_after": 235,
        "imports_resolved": ["audio_uart_text_line_segment_489698"],
        "imports_added": [],
    })
    previous = linked
    decoder_cell_script = HERE / "bind_main_page_text_decode_cell_78f2a4_20261015.py"
    decoder_cell_result = subprocess.run([sys.executable, str(decoder_cell_script)], check=True,
                                         capture_output=True, text=True)
    decoder_cell_path = G2 / "build/c-firmware/20261015/main-page-text-decode-cell-78f2a4/receipt.json"
    decoder_cell = json.loads(decoder_cell_path.read_text())
    if decoder_cell["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_DECODE_CELL_C":
        raise RuntimeError("page decoder cell stage status changed")
    base = file_from_receipt(decoder_cell, "base_object", "base_sha256")
    linked = file_from_receipt(decoder_cell, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 235 or len(imports(linked)) != 235 or \
            imports(base) != imports(linked) or \
            decoder_cell["native_word"] != "0x489c5f":
        raise RuntimeError("page decoder cell stage handoff changed")
    if sha(ROOT / decoder_cell["source"]) != decoder_cell["source_sha256"]:
        raise RuntimeError("stale page decoder cell source")
    records.append({
        "stage": "main-page-text-decode-cell-78f2a4",
        "binder": str(decoder_cell_script.relative_to(ROOT)),
        "binder_sha256": sha(decoder_cell_script), "status": decoder_cell["status"],
        "binder_output": decoder_cell_result.stdout.strip(),
        "receipt": str(decoder_cell_path.relative_to(ROOT)),
        "receipt_sha256": sha(decoder_cell_path),
        "source": decoder_cell["source"], "source_sha256": decoder_cell["source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 235, "unresolved_after": 235,
        "imports_resolved": [], "imports_added": [],
    })
    previous = linked
    utf8_callbacks_script = HERE / "bind_main_page_text_utf8_callbacks_20261015.py"
    utf8_callbacks_result = subprocess.run([sys.executable, str(utf8_callbacks_script)], check=True,
                                          capture_output=True, text=True)
    utf8_callbacks_path = G2 / "build/c-firmware/20261015/main-page-text-utf8-callbacks/receipt.json"
    utf8_callbacks = json.loads(utf8_callbacks_path.read_text())
    if utf8_callbacks["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_UTF8_CALLBACKS_C":
        raise RuntimeError("page UTF-8 callbacks stage status changed")
    base = file_from_receipt(utf8_callbacks, "base_object", "base_sha256")
    linked = file_from_receipt(utf8_callbacks, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 235 or len(imports(linked)) != 235 or \
            imports(base) != imports(linked) or \
            len(utf8_callbacks["native_thumb_words"]) != 7:
        raise RuntimeError("page UTF-8 callbacks stage handoff changed")
    if len(utf8_callbacks["sources"]) != 3 or len(utf8_callbacks["oracle_receipts"]) != 3 or \
            sha(ROOT / utf8_callbacks["table_source"]) != utf8_callbacks["table_source_sha256"]:
        raise RuntimeError("page UTF-8 callback source set changed")
    for item in utf8_callbacks["sources"]:
        if sha(ROOT / item["path"]) != item["sha256"] or \
                sha(ROOT / item["object"]) != item["object_sha256"]:
            raise RuntimeError("stale page UTF-8 callback source or object")
    for item in utf8_callbacks["oracle_receipts"]:
        if sha(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError("stale page UTF-8 callback oracle")
    records.append({
        "stage": "main-page-text-utf8-callbacks",
        "binder": str(utf8_callbacks_script.relative_to(ROOT)),
        "binder_sha256": sha(utf8_callbacks_script), "status": utf8_callbacks["status"],
        "binder_output": utf8_callbacks_result.stdout.strip(),
        "receipt": str(utf8_callbacks_path.relative_to(ROOT)),
        "receipt_sha256": sha(utf8_callbacks_path),
        "sources": utf8_callbacks["sources"],
        "oracle_receipts": utf8_callbacks["oracle_receipts"],
        "table_source": utf8_callbacks["table_source"],
        "table_source_sha256": utf8_callbacks["table_source_sha256"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 235, "unresolved_after": 235,
        "imports_resolved": [], "imports_added": [],
    })
    previous = linked
    layout_helpers_script = HERE / "bind_main_page_layout_helpers_49a5c0_20261015.py"
    layout_helpers_result = subprocess.run([sys.executable, str(layout_helpers_script)], check=True,
                                           capture_output=True, text=True)
    layout_helpers_path = G2 / "build/c-firmware/20261015/main-page-layout-helpers-49a5c0/receipt.json"
    layout_helpers = json.loads(layout_helpers_path.read_text())
    if layout_helpers["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_LAYOUT_HELPERS_C":
        raise RuntimeError("page layout helpers stage status changed")
    base = file_from_receipt(layout_helpers, "base_object", "base_sha256")
    linked = file_from_receipt(layout_helpers, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 235 or len(imports(linked)) != 235 or \
            imports(base) != imports(linked) or \
            set(layout_helpers["source_owned_symbols"]) != {
                "audio_uart_page_layout_copy_anim_49a5c0",
                "audio_uart_page_layout_flags_49abea"}:
        raise RuntimeError("page layout helpers stage handoff changed")
    if sha(ROOT / layout_helpers["source"]) != layout_helpers["source_sha256"]:
        raise RuntimeError("stale page layout helpers source")
    records.append({
        "stage": "main-page-layout-helpers-49a5c0",
        "binder": str(layout_helpers_script.relative_to(ROOT)),
        "binder_sha256": sha(layout_helpers_script), "status": layout_helpers["status"],
        "binder_output": layout_helpers_result.stdout.strip(),
        "receipt": str(layout_helpers_path.relative_to(ROOT)),
        "receipt_sha256": sha(layout_helpers_path),
        "source": layout_helpers["source"], "source_sha256": layout_helpers["source_sha256"],
        "source_owned_symbols": layout_helpers["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 235, "unresolved_after": 235,
        "imports_resolved": [], "imports_added": [],
    })
    previous = linked
    layout_metric_script = HERE / "bind_main_page_layout_metric_getters_499402_20261015.py"
    layout_metric_result = subprocess.run([sys.executable, str(layout_metric_script)], check=True,
                                          capture_output=True, text=True)
    layout_metric_path = G2 / "build/c-firmware/20261015/main-page-layout-metric-getters-499402/receipt.json"
    layout_metric = json.loads(layout_metric_path.read_text())
    if layout_metric["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_LAYOUT_METRIC_GETTERS_C":
        raise RuntimeError("page layout metric stage status changed")
    base = file_from_receipt(layout_metric, "base_object", "base_sha256")
    linked = file_from_receipt(layout_metric, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 235 or len(imports(linked)) != 235 or \
            imports(base) != imports(linked) or \
            set(layout_metric["source_owned_symbols"]) != {
                "audio_uart_page_metric_499402", "audio_uart_page_metric_49940c"}:
        raise RuntimeError("page layout metric stage handoff changed")
    if sha(ROOT / layout_metric["source"]) != layout_metric["source_sha256"]:
        raise RuntimeError("stale page layout metric source")
    records.append({
        "stage": "main-page-layout-metric-getters-499402",
        "binder": str(layout_metric_script.relative_to(ROOT)),
        "binder_sha256": sha(layout_metric_script), "status": layout_metric["status"],
        "binder_output": layout_metric_result.stdout.strip(),
        "receipt": str(layout_metric_path.relative_to(ROOT)),
        "receipt_sha256": sha(layout_metric_path),
        "source": layout_metric["source"], "source_sha256": layout_metric["source_sha256"],
        "source_owned_symbols": layout_metric["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 235, "unresolved_after": 235,
        "imports_resolved": [], "imports_added": [],
    })
    previous = linked
    anim_lookup_script = HERE / "bind_main_page_lv_anim_lookup_450566_20261015.py"
    anim_lookup_result = subprocess.run([sys.executable, str(anim_lookup_script)], check=True,
                                       capture_output=True, text=True)
    anim_lookup_path = G2 / "build/c-firmware/20261015/main-page-lv-anim-lookup-450566/receipt.json"
    anim_lookup = json.loads(anim_lookup_path.read_text())
    if anim_lookup["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_LV_ANIM_LOOKUP_C":
        raise RuntimeError("page animation lookup stage status changed")
    base = file_from_receipt(anim_lookup, "base_object", "base_sha256")
    linked = file_from_receipt(anim_lookup, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 235 or len(imports(linked)) != 235 or \
            imports(base) != imports(linked) or \
            anim_lookup["source_owned_symbols"] != ["audio_uart_page_lv_anim_lookup_450566"]:
        raise RuntimeError("page animation lookup stage handoff changed")
    if sha(ROOT / anim_lookup["source"]) != anim_lookup["source_sha256"]:
        raise RuntimeError("stale page animation lookup source")
    records.append({
        "stage": "main-page-lv-anim-lookup-450566",
        "binder": str(anim_lookup_script.relative_to(ROOT)),
        "binder_sha256": sha(anim_lookup_script), "status": anim_lookup["status"],
        "binder_output": anim_lookup_result.stdout.strip(),
        "receipt": str(anim_lookup_path.relative_to(ROOT)),
        "receipt_sha256": sha(anim_lookup_path),
        "source": anim_lookup["source"], "source_sha256": anim_lookup["source_sha256"],
        "source_owned_symbols": anim_lookup["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 235, "unresolved_after": 235,
        "imports_resolved": [], "imports_added": [],
    })
    previous = linked
    invalidate_script = HERE / "bind_main_page_invalidate_440656_20261015.py"
    invalidate_result = subprocess.run([sys.executable, str(invalidate_script)], check=True,
                                    capture_output=True, text=True)
    invalidate_path = G2 / "build/c-firmware/20261015/main-page-invalidate-440656/receipt.json"
    invalidate = json.loads(invalidate_path.read_text())
    if invalidate["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_INVALIDATE_C":
        raise RuntimeError("page invalidate stage status changed")
    base = file_from_receipt(invalidate, "base_object", "base_sha256")
    linked = file_from_receipt(invalidate, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 235 or len(imports(linked)) != 235 or \
            imports(base) != imports(linked) or \
            invalidate["source_owned_symbols"] != ["audio_uart_page_invalidate_440656"]:
        raise RuntimeError("page invalidate stage handoff changed")
    if sha(ROOT / invalidate["source"]) != invalidate["source_sha256"]:
        raise RuntimeError("stale page invalidate source")
    records.append({
        "stage": "main-page-invalidate-440656",
        "binder": str(invalidate_script.relative_to(ROOT)),
        "binder_sha256": sha(invalidate_script), "status": invalidate["status"],
        "binder_output": invalidate_result.stdout.strip(),
        "receipt": str(invalidate_path.relative_to(ROOT)),
        "receipt_sha256": sha(invalidate_path),
        "source": invalidate["source"], "source_sha256": invalidate["source_sha256"],
        "source_owned_symbols": invalidate["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 235, "unresolved_after": 235,
        "imports_resolved": [], "imports_added": [],
    })
    previous = linked
    text_pointer_script = HERE / "bind_main_page_text_pointer_4997f8_20261015.py"
    text_pointer_result = subprocess.run([sys.executable, str(text_pointer_script)], check=True,
                                         capture_output=True, text=True)
    text_pointer_path = G2 / "build/c-firmware/20261015/main-page-text-pointer-4997f8/receipt.json"
    text_pointer = json.loads(text_pointer_path.read_text())
    if text_pointer["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_POINTER_C":
        raise RuntimeError("page text pointer stage status changed")
    base = file_from_receipt(text_pointer, "base_object", "base_sha256")
    linked = file_from_receipt(text_pointer, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 235 or len(imports(linked)) != 235 or \
            imports(base) != imports(linked) or \
            text_pointer["source_owned_symbols"] != ["audio_uart_page_text_pointer_4997f8"]:
        raise RuntimeError("page text pointer stage handoff changed")
    if sha(ROOT / text_pointer["source"]) != text_pointer["source_sha256"]:
        raise RuntimeError("stale page text pointer source")
    records.append({
        "stage": "main-page-text-pointer-4997f8",
        "binder": str(text_pointer_script.relative_to(ROOT)),
        "binder_sha256": sha(text_pointer_script), "status": text_pointer["status"],
        "binder_output": text_pointer_result.stdout.strip(),
        "receipt": str(text_pointer_path.relative_to(ROOT)),
        "receipt_sha256": sha(text_pointer_path),
        "source": text_pointer["source"], "source_sha256": text_pointer["source_sha256"],
        "source_owned_symbols": text_pointer["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 235, "unresolved_after": 235,
        "imports_resolved": [], "imports_added": [],
    })
    previous = linked
    text_width_script = HERE / "bind_main_page_text_width_4899a4_20261015.py"
    text_width_result = subprocess.run([sys.executable, str(text_width_script)], check=True,
                                       capture_output=True, text=True)
    text_width_path = G2 / "build/c-firmware/20261015/main-page-text-width-4899a4/receipt.json"
    text_width = json.loads(text_width_path.read_text())
    if text_width["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_WIDTH_C":
        raise RuntimeError("page text width stage status changed")
    base = file_from_receipt(text_width, "base_object", "base_sha256")
    linked = file_from_receipt(text_width, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 235 or len(imports(linked)) != 235 or \
            imports(base) != imports(linked) or \
            text_width["source_owned_symbols"] != ["audio_uart_text_width_4899a4"]:
        raise RuntimeError("page text width stage handoff changed")
    if sha(ROOT / text_width["source"]) != text_width["source_sha256"]:
        raise RuntimeError("stale page text width source")
    records.append({
        "stage": "main-page-text-width-4899a4",
        "binder": str(text_width_script.relative_to(ROOT)),
        "binder_sha256": sha(text_width_script), "status": text_width["status"],
        "binder_output": text_width_result.stdout.strip(),
        "receipt": str(text_width_path.relative_to(ROOT)),
        "receipt_sha256": sha(text_width_path),
        "source": text_width["source"], "source_sha256": text_width["source_sha256"],
        "source_owned_symbols": text_width["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 235, "unresolved_after": 235,
        "imports_resolved": [], "imports_added": [],
    })
    previous = linked
    text_align_script = HERE / "bind_main_page_text_align_49ac4a_20261015.py"
    text_align_result = subprocess.run([sys.executable, str(text_align_script)], check=True,
                                       capture_output=True, text=True)
    text_align_path = G2 / "build/c-firmware/20261015/main-page-text-align-49ac4a/receipt.json"
    text_align = json.loads(text_align_path.read_text())
    if text_align["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_TEXT_ALIGN_C":
        raise RuntimeError("page text alignment stage status changed")
    base = file_from_receipt(text_align, "base_object", "base_sha256")
    linked = file_from_receipt(text_align, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 235 or len(imports(linked)) != 235 or \
            imports(base) != imports(linked) or \
            text_align["source_owned_symbols"] != ["audio_uart_page_text_align_49ac4a"]:
        raise RuntimeError("page text alignment stage handoff changed")
    if sha(ROOT / text_align["source"]) != text_align["source_sha256"]:
        raise RuntimeError("stale page text alignment source")
    records.append({
        "stage": "main-page-text-align-49ac4a",
        "binder": str(text_align_script.relative_to(ROOT)),
        "binder_sha256": sha(text_align_script), "status": text_align["status"],
        "binder_output": text_align_result.stdout.strip(),
        "receipt": str(text_align_path.relative_to(ROOT)),
        "receipt_sha256": sha(text_align_path),
        "source": text_align["source"], "source_sha256": text_align["source_sha256"],
        "source_owned_symbols": text_align["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 235, "unresolved_after": 235,
        "imports_resolved": [], "imports_added": [],
    })
    previous = linked
    page_factory_script = HERE / "bind_main_page_factory_43de82_20261015.py"
    page_factory_result = subprocess.run([sys.executable, str(page_factory_script)], check=True,
                                         capture_output=True, text=True)
    page_factory_path = G2 / "build/c-firmware/20261015/main-page-factory-43de82/receipt.json"
    page_factory = json.loads(page_factory_path.read_text())
    if page_factory["status"] != "PASS_EXPERIMENTAL_MAIN_PAGE_FACTORY_43DE82_C":
        raise RuntimeError("generic page factory stage status changed")
    base = file_from_receipt(page_factory, "base_object", "base_sha256")
    linked = file_from_receipt(page_factory, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 235 or len(imports(linked)) != 235 or \
            imports(base) - imports(linked) != {"audio_uart_page_43de82"} or \
            imports(linked) - imports(base) != {"audio_uart_lv_base_class_7564f8"} or \
            page_factory["source_owned_symbols"] != ["audio_uart_page_43de82"]:
        raise RuntimeError("generic page factory stage handoff changed")
    if sha(ROOT / page_factory["source"]) != page_factory["source_sha256"]:
        raise RuntimeError("stale generic page factory source")
    records.append({
        "stage": "main-page-factory-43de82",
        "binder": str(page_factory_script.relative_to(ROOT)),
        "binder_sha256": sha(page_factory_script), "status": page_factory["status"],
        "binder_output": page_factory_result.stdout.strip(),
        "receipt": str(page_factory_path.relative_to(ROOT)),
        "receipt_sha256": sha(page_factory_path),
        "source": page_factory["source"], "source_sha256": page_factory["source_sha256"],
        "source_owned_symbols": page_factory["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 235, "unresolved_after": 235,
        "imports_resolved": ["audio_uart_page_43de82"], "imports_added": ["audio_uart_lv_base_class_7564f8"],
    })
    previous = linked
    registry_script = HERE / "bind_main_registry_lookup_45fffe_20261015.py"
    registry_result = subprocess.run([sys.executable, str(registry_script)], check=True,
                                     capture_output=True, text=True)
    registry_path = G2 / "build/c-firmware/20261015/main-registry-lookup-45fffe/receipt.json"
    registry = json.loads(registry_path.read_text())
    if registry["status"] != "PASS_EXPERIMENTAL_MAIN_REGISTRY_LOOKUP_C":
        raise RuntimeError("registry lookup stage status changed")
    base = file_from_receipt(registry, "base_object", "base_sha256")
    linked = file_from_receipt(registry, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 235 or len(imports(linked)) != 234 or \
            imports(base) - imports(linked) != {"audio_uart_page_45fffe"} or \
            imports(linked) - imports(base) or \
            registry["source_owned_symbols"] != ["audio_uart_page_45fffe"]:
        raise RuntimeError("registry lookup stage handoff changed")
    if sha(ROOT / registry["source"]) != registry["source_sha256"]:
        raise RuntimeError("stale registry lookup source")
    records.append({
        "stage": "main-registry-lookup-45fffe",
        "binder": str(registry_script.relative_to(ROOT)),
        "binder_sha256": sha(registry_script), "status": registry["status"],
        "binder_output": registry_result.stdout.strip(),
        "receipt": str(registry_path.relative_to(ROOT)),
        "receipt_sha256": sha(registry_path),
        "source": registry["source"], "source_sha256": registry["source_sha256"],
        "source_owned_symbols": registry["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 235, "unresolved_after": 234,
        "imports_resolved": ["audio_uart_page_45fffe"], "imports_added": [],
    })
    previous = linked
    base_ctor_script = HERE / "bind_main_lv_base_ctor_43e33e_20261015.py"
    base_ctor_result = subprocess.run([sys.executable, str(base_ctor_script)], check=True,
                                      capture_output=True, text=True)
    base_ctor_path = G2 / "build/c-firmware/20261015/main-lv-base-ctor-43e33e/receipt.json"
    base_ctor = json.loads(base_ctor_path.read_text())
    if base_ctor["status"] != "PASS_EXPERIMENTAL_MAIN_LV_BASE_CTOR_C":
        raise RuntimeError("base constructor stage status changed")
    base = file_from_receipt(base_ctor, "base_object", "base_sha256")
    linked = file_from_receipt(base_ctor, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 234 or len(imports(linked)) != 234 or \
            imports(base) != imports(linked) or \
            set(base_ctor["source_owned_symbols"]) != {
                "audio_uart_lv_metric_43dd86", "audio_uart_lv_metric_43dd90",
                "audio_uart_lv_base_ctor_43e33e"}:
        raise RuntimeError("base constructor stage handoff changed")
    if sha(ROOT / base_ctor["source"]) != base_ctor["source_sha256"]:
        raise RuntimeError("stale base constructor source")
    records.append({
        "stage": "main-lv-base-ctor-43e33e",
        "binder": str(base_ctor_script.relative_to(ROOT)),
        "binder_sha256": sha(base_ctor_script), "status": base_ctor["status"],
        "binder_output": base_ctor_result.stdout.strip(),
        "receipt": str(base_ctor_path.relative_to(ROOT)),
        "receipt_sha256": sha(base_ctor_path),
        "source": base_ctor["source"], "source_sha256": base_ctor["source_sha256"],
        "source_owned_symbols": base_ctor["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 234, "unresolved_after": 234,
        "imports_resolved": [], "imports_added": [],
    })
    previous = linked
    style_mark_script = HERE / "bind_main_lv_style_mark_45028e_20261015.py"
    style_mark_result = subprocess.run([sys.executable, str(style_mark_script)], check=True,
                                       capture_output=True, text=True)
    style_mark_path = G2 / "build/c-firmware/20261015/main-lv-style-mark-45028e/receipt.json"
    style_mark = json.loads(style_mark_path.read_text())
    if style_mark["status"] != "PASS_EXPERIMENTAL_MAIN_LV_STYLE_MARK_C":
        raise RuntimeError("LV style marker stage status changed")
    base = file_from_receipt(style_mark, "base_object", "base_sha256")
    linked = file_from_receipt(style_mark, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 234 or len(imports(linked)) != 234 or \
            imports(base) != imports(linked) or \
            style_mark["source_owned_symbols"] != ["audio_uart_lv_style_mark_45028e"]:
        raise RuntimeError("LV style marker stage handoff changed")
    if sha(ROOT / style_mark["source"]) != style_mark["source_sha256"]:
        raise RuntimeError("stale LV style marker source")
    records.append({
        "stage": "main-lv-style-mark-45028e",
        "binder": str(style_mark_script.relative_to(ROOT)),
        "binder_sha256": sha(style_mark_script), "status": style_mark["status"],
        "binder_output": style_mark_result.stdout.strip(),
        "receipt": str(style_mark_path.relative_to(ROOT)),
        "receipt_sha256": sha(style_mark_path),
        "source": style_mark["source"], "source_sha256": style_mark["source_sha256"],
        "source_owned_symbols": style_mark["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 234, "unresolved_after": 234,
        "imports_resolved": [], "imports_added": [],
    })
    previous = linked
    base_dtor_script = HERE / "bind_main_lv_base_dtor_43e3de_20261015.py"
    base_dtor_result = subprocess.run([sys.executable, str(base_dtor_script)], check=True,
                                      capture_output=True, text=True)
    base_dtor_path = G2 / "build/c-firmware/20261015/main-lv-base-dtor-43e3de/receipt.json"
    base_dtor = json.loads(base_dtor_path.read_text())
    if base_dtor["status"] != "PASS_EXPERIMENTAL_MAIN_LV_BASE_DTOR_C":
        raise RuntimeError("base destructor stage status changed")
    base = file_from_receipt(base_dtor, "base_object", "base_sha256")
    linked = file_from_receipt(base_dtor, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 234 or len(imports(linked)) != 234 or \
            imports(base) != imports(linked) or \
            base_dtor["source_owned_symbols"] != ["audio_uart_lv_base_dtor_43e3de"]:
        raise RuntimeError("base destructor stage handoff changed")
    if sha(ROOT / base_dtor["source"]) != base_dtor["source_sha256"]:
        raise RuntimeError("stale base destructor source")
    records.append({
        "stage": "main-lv-base-dtor-43e3de",
        "binder": str(base_dtor_script.relative_to(ROOT)),
        "binder_sha256": sha(base_dtor_script), "status": base_dtor["status"],
        "binder_output": base_dtor_result.stdout.strip(),
        "receipt": str(base_dtor_path.relative_to(ROOT)),
        "receipt_sha256": sha(base_dtor_path),
        "source": base_dtor["source"], "source_sha256": base_dtor["source_sha256"],
        "source_owned_symbols": base_dtor["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 234, "unresolved_after": 234,
        "imports_resolved": [], "imports_added": [],
    })
    previous = linked
    base_metrics_script = HERE / "bind_main_lv_base_metrics_43dd52_20261015.py"
    base_metrics_result = subprocess.run([sys.executable, str(base_metrics_script)], check=True,
                                         capture_output=True, text=True)
    base_metrics_path = G2 / "build/c-firmware/20261015/main-lv-base-metrics-43dd52/receipt.json"
    base_metrics = json.loads(base_metrics_path.read_text())
    if base_metrics["status"] != "PASS_EXPERIMENTAL_MAIN_LV_BASE_METRICS_C":
        raise RuntimeError("base metrics stage status changed")
    base = file_from_receipt(base_metrics, "base_object", "base_sha256")
    linked = file_from_receipt(base_metrics, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 234 or len(imports(linked)) != 234 or \
            imports(base) != imports(linked) or \
            set(base_metrics["source_owned_symbols"]) != {
                "audio_uart_lv_metric_43dd52", "audio_uart_lv_metric_43dd5c",
                "audio_uart_lv_metric_43dd66", "audio_uart_lv_metric_43de76"}:
        raise RuntimeError("base metrics stage handoff changed")
    if sha(ROOT / base_metrics["source"]) != base_metrics["source_sha256"]:
        raise RuntimeError("stale base metrics source")
    records.append({
        "stage": "main-lv-base-metrics-43dd52",
        "binder": str(base_metrics_script.relative_to(ROOT)),
        "binder_sha256": sha(base_metrics_script), "status": base_metrics["status"],
        "binder_output": base_metrics_result.stdout.strip(),
        "receipt": str(base_metrics_path.relative_to(ROOT)),
        "receipt_sha256": sha(base_metrics_path),
        "source": base_metrics["source"], "source_sha256": base_metrics["source_sha256"],
        "source_owned_symbols": base_metrics["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 234, "unresolved_after": 234,
        "imports_resolved": [], "imports_added": [],
    })
    previous = linked
    base_event_script = HERE / "bind_main_lv_base_event_43e7d2_20261015.py"
    base_event_result = subprocess.run([sys.executable, str(base_event_script)], check=True,
                                       capture_output=True, text=True)
    base_event_path = G2 / "build/c-firmware/20261015/main-lv-base-event-43e7d2/receipt.json"
    base_event = json.loads(base_event_path.read_text())
    if base_event["status"] != "PASS_EXPERIMENTAL_MAIN_LV_BASE_EVENT_C":
        raise RuntimeError("base event stage status changed")
    base = file_from_receipt(base_event, "base_object", "base_sha256")
    linked = file_from_receipt(base_event, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 234 or len(imports(linked)) != 244 or \
            imports(base) - imports(linked) or \
            imports(linked) - imports(base) != set(base_event["imports_added"]) or \
            base_event["source_owned_symbols"] != ["audio_uart_lv_base_event_43e7d2"]:
        raise RuntimeError("base event stage handoff changed")
    if sha(ROOT / base_event["source"]) != base_event["source_sha256"]:
        raise RuntimeError("stale base event source")
    records.append({
        "stage": "main-lv-base-event-43e7d2", "binder": str(base_event_script.relative_to(ROOT)),
        "binder_sha256": sha(base_event_script), "status": base_event["status"],
        "binder_output": base_event_result.stdout.strip(),
        "receipt": str(base_event_path.relative_to(ROOT)), "receipt_sha256": sha(base_event_path),
        "source": base_event["source"], "source_sha256": base_event["source_sha256"],
        "source_owned_symbols": base_event["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 234, "unresolved_after": 244,
        "imports_resolved": [], "imports_added": base_event["imports_added"],
    })
    previous = linked
    state_script = HERE / "bind_main_lv_base_state_helpers_20261015.py"
    state_result = subprocess.run([sys.executable, str(state_script)], check=True,
                                  capture_output=True, text=True)
    state_path = G2 / "build/c-firmware/20261015/main-lv-base-state-helpers/receipt.json"
    state = json.loads(state_path.read_text())
    if state["status"] != "PASS_EXPERIMENTAL_MAIN_LV_BASE_STATE_HELPERS_C":
        raise RuntimeError("base state helper stage status changed")
    base = file_from_receipt(state, "base_object", "base_sha256")
    linked = file_from_receipt(state, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 244 or len(imports(linked)) != 242 or \
            imports(base) - imports(linked) != set(state["imports_resolved"]) or \
            imports(linked) - imports(base) or \
            set(state["source_owned_symbols"]) != {
                "audio_uart_lv_obj_state_43e156", "audio_uart_lv_obj_is_scrolling_44d19a"}:
        raise RuntimeError("base state helper stage handoff changed")
    if sha(ROOT / state["source"]) != state["source_sha256"]:
        raise RuntimeError("stale base state helper source")
    records.append({
        "stage": "main-lv-base-state-helpers", "binder": str(state_script.relative_to(ROOT)),
        "binder_sha256": sha(state_script), "status": state["status"],
        "binder_output": state_result.stdout.strip(),
        "receipt": str(state_path.relative_to(ROOT)), "receipt_sha256": sha(state_path),
        "source": state["source"], "source_sha256": state["source_sha256"],
        "source_owned_symbols": state["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 244, "unresolved_after": 242,
        "imports_resolved": state["imports_resolved"], "imports_added": [],
    })
    previous = linked
    base_class_script = HERE / "bind_main_lv_base_class_7564f8_20261015.py"
    base_class_result = subprocess.run([sys.executable, str(base_class_script)], check=True,
                                       capture_output=True, text=True)
    base_class_path = G2 / "build/c-firmware/20261015/main-lv-base-class-7564f8/receipt.json"
    base_class = json.loads(base_class_path.read_text())
    if base_class["status"] != "PASS_EXPERIMENTAL_MAIN_LV_BASE_CLASS_C":
        raise RuntimeError("base class stage status changed")
    base = file_from_receipt(base_class, "base_object", "base_sha256")
    linked = file_from_receipt(base_class, "linked_object", "linked_sha256")
    if base != previous or len(imports(base)) != 242 or len(imports(linked)) != 241 or \
            imports(base) - imports(linked) != {"audio_uart_lv_base_class_7564f8"} or \
            imports(linked) - imports(base) or \
            set(base_class["source_owned_symbols"]) != {
                "audio_uart_lv_base_class_7564f8", "audio_uart_lv_base_class_name_78dc64"}:
        raise RuntimeError("base class stage handoff changed")
    if sha(ROOT / base_class["source"]) != base_class["source_sha256"]:
        raise RuntimeError("stale base class source")
    records.append({
        "stage": "main-lv-base-class-7564f8", "binder": str(base_class_script.relative_to(ROOT)),
        "binder_sha256": sha(base_class_script), "status": base_class["status"],
        "binder_output": base_class_result.stdout.strip(),
        "receipt": str(base_class_path.relative_to(ROOT)), "receipt_sha256": sha(base_class_path),
        "source": base_class["source"], "source_sha256": base_class["source_sha256"],
        "source_owned_symbols": base_class["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 242, "unresolved_after": 241,
        "imports_resolved": ["audio_uart_lv_base_class_7564f8"], "imports_added": [],
    })
    previous = linked
    accessors_script = HERE / "bind_main_lv_event_accessors_4518d8_20261015.py"
    accessors_result = subprocess.run([sys.executable, str(accessors_script)], check=True,
                                      capture_output=True, text=True)
    accessors_path = G2 / "build/c-firmware/20261015/main-lv-event-accessors-4518d8/receipt.json"
    accessors = json.loads(accessors_path.read_text())
    if accessors["status"] != "PASS_EXPERIMENTAL_MAIN_LV_EVENT_ACCESSORS_C":
        raise RuntimeError("LV event accessor stage status changed")
    base = file_from_receipt(accessors, "base_object", "base_sha256")
    linked = file_from_receipt(accessors, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_input_reset_4518d8", "audio_uart_lv_event_param_4519a0"}
    if base != previous or len(imports(base)) != 241 or len(imports(linked)) != 239 or \
            imports(base) - imports(linked) != owned or imports(linked) - imports(base) or \
            set(accessors["source_owned_symbols"]) != owned:
        raise RuntimeError("LV event accessor stage handoff changed")
    if sha(ROOT / accessors["source"]) != accessors["source_sha256"]:
        raise RuntimeError("stale LV event accessor source")
    records.append({
        "stage": "main-lv-event-accessors-4518d8", "binder": str(accessors_script.relative_to(ROOT)),
        "binder_sha256": sha(accessors_script), "status": accessors["status"],
        "binder_output": accessors_result.stdout.strip(),
        "receipt": str(accessors_path.relative_to(ROOT)), "receipt_sha256": sha(accessors_path),
        "source": accessors["source"], "source_sha256": accessors["source_sha256"],
        "source_owned_symbols": accessors["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 241, "unresolved_after": 239,
        "imports_resolved": accessors["imports_resolved"], "imports_added": [],
    })
    previous = linked
    flags_script = HERE / "bind_main_lv_obj_flags_43e046_20261015.py"
    flags_result = subprocess.run([sys.executable, str(flags_script)], check=True,
                                  capture_output=True, text=True)
    flags_path = G2 / "build/c-firmware/20261015/main-lv-obj-flags-43e046/receipt.json"
    flags = json.loads(flags_path.read_text())
    if flags["status"] != "PASS_EXPERIMENTAL_MAIN_LV_OBJ_FLAGS_C":
        raise RuntimeError("LV object flags stage status changed")
    base = file_from_receipt(flags, "base_object", "base_sha256")
    linked = file_from_receipt(flags, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_obj_flag_set_43e046", "audio_uart_lv_obj_flag_clear_43e086"}
    lower = {"audio_uart_lv_obj_state_apply_43ebec"}
    if base != previous or len(imports(base)) != 239 or len(imports(linked)) != 238 or \
            imports(base) - imports(linked) != owned or imports(linked) - imports(base) != lower or \
            set(flags["source_owned_symbols"]) != owned:
        raise RuntimeError("LV object flags stage handoff changed")
    if sha(ROOT / flags["source"]) != flags["source_sha256"]:
        raise RuntimeError("stale LV object flags source")
    records.append({
        "stage": "main-lv-obj-flags-43e046", "binder": str(flags_script.relative_to(ROOT)),
        "binder_sha256": sha(flags_script), "status": flags["status"],
        "binder_output": flags_result.stdout.strip(),
        "receipt": str(flags_path.relative_to(ROOT)), "receipt_sha256": sha(flags_path),
        "source": flags["source"], "source_sha256": flags["source_sha256"],
        "source_owned_symbols": flags["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 239, "unresolved_after": 238,
        "imports_resolved": flags["imports_resolved"], "imports_added": flags["imports_added"],
    })
    previous = linked
    view_script = HERE / "bind_main_lv_scroll_to_view_44ea56_20261015.py"
    view_result = subprocess.run([sys.executable, str(view_script)], check=True,
                                 capture_output=True, text=True)
    view_path = G2 / "build/c-firmware/20261015/main-lv-scroll-to-view-44ea56/receipt.json"
    view = json.loads(view_path.read_text())
    if view["status"] != "PASS_EXPERIMENTAL_MAIN_LV_SCROLL_TO_VIEW_C":
        raise RuntimeError("LV scroll-to-view stage status changed")
    base = file_from_receipt(view, "base_object", "base_sha256")
    linked = file_from_receipt(view, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_scroll_to_view_44ea56"}
    lower = {"audio_uart_lv_scroll_view_step_44f40c"}
    if base != previous or len(imports(base)) != 238 or len(imports(linked)) != 238 or \
            imports(base) - imports(linked) != owned or imports(linked) - imports(base) != lower or \
            set(view["source_owned_symbols"]) != owned:
        raise RuntimeError("LV scroll-to-view stage handoff changed")
    if sha(ROOT / view["source"]) != view["source_sha256"]:
        raise RuntimeError("stale LV scroll-to-view source")
    records.append({
        "stage": "main-lv-scroll-to-view-44ea56", "binder": str(view_script.relative_to(ROOT)),
        "binder_sha256": sha(view_script), "status": view["status"],
        "binder_output": view_result.stdout.strip(),
        "receipt": str(view_path.relative_to(ROOT)), "receipt_sha256": sha(view_path),
        "source": view["source"], "source_sha256": view["source_sha256"],
        "source_owned_symbols": view["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 238, "unresolved_after": 238,
        "imports_resolved": view["imports_resolved"], "imports_added": view["imports_added"],
    })
    previous = linked
    invalidate_script = HERE / "bind_main_lv_invalidate_alias_4405d4_20261015.py"
    invalidate_result = subprocess.run([sys.executable, str(invalidate_script)], check=True,
                                       capture_output=True, text=True)
    invalidate_path = G2 / "build/c-firmware/20261015/main-lv-invalidate-alias-4405d4/receipt.json"
    invalidate = json.loads(invalidate_path.read_text())
    if invalidate["status"] != "PASS_EXPERIMENTAL_MAIN_LV_INVALIDATE_ALIAS_C":
        raise RuntimeError("LV invalidate alias stage status changed")
    base = file_from_receipt(invalidate, "base_object", "base_sha256")
    linked = file_from_receipt(invalidate, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_invalidate_area_4405d4"}
    if base != previous or len(imports(base)) != 238 or len(imports(linked)) != 237 or \
            imports(base) - imports(linked) != owned or imports(linked) - imports(base) or \
            set(invalidate["source_owned_symbols"]) != owned:
        raise RuntimeError("LV invalidate alias stage handoff changed")
    if sha(ROOT / invalidate["source"]) != invalidate["source_sha256"] or \
            sha(ROOT / invalidate["existing_source"]) != invalidate["existing_source_sha256"]:
        raise RuntimeError("stale LV invalidate alias or existing source")
    records.append({
        "stage": "main-lv-invalidate-alias-4405d4",
        "binder": str(invalidate_script.relative_to(ROOT)),
        "binder_sha256": sha(invalidate_script), "status": invalidate["status"],
        "binder_output": invalidate_result.stdout.strip(),
        "receipt": str(invalidate_path.relative_to(ROOT)), "receipt_sha256": sha(invalidate_path),
        "source": invalidate["source"], "source_sha256": invalidate["source_sha256"],
        "existing_source": invalidate["existing_source"],
        "existing_source_sha256": invalidate["existing_source_sha256"],
        "source_owned_symbols": invalidate["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 238, "unresolved_after": 237,
        "imports_resolved": invalidate["imports_resolved"], "imports_added": [],
    })
    previous = linked
    compass_script = HERE / "bind_main_lv_compass_452c66_20261015.py"
    compass_result = subprocess.run([sys.executable, str(compass_script)], check=True,
                                    capture_output=True, text=True)
    compass_path = G2 / "build/c-firmware/20261015/main-lv-compass-452c66/receipt.json"
    compass = json.loads(compass_path.read_text())
    if compass["status"] != "PASS_EXPERIMENTAL_MAIN_LV_COMPASS_C":
        raise RuntimeError("LV extent stage status changed")
    base = file_from_receipt(compass, "base_object", "base_sha256")
    linked = file_from_receipt(compass, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_compass_452c66"}
    lower = {f"audio_uart_lv_compass_part_{address:x}" for address in
             (0x452450, 0x452498, 0x45246e, 0x45245a, 0x452464,
              0x452410, 0x45243a, 0x452446, 0x4522d4, 0x4522de)}
    if base != previous or len(imports(base)) != 237 or len(imports(linked)) != 246 or \
            imports(base) - imports(linked) != owned or imports(linked) - imports(base) != lower or \
            set(compass["source_owned_symbols"]) != owned:
        raise RuntimeError("LV extent stage handoff changed")
    if sha(ROOT / compass["source"]) != compass["source_sha256"]:
        raise RuntimeError("stale LV extent source")
    records.append({
        "stage": "main-lv-compass-452c66", "binder": str(compass_script.relative_to(ROOT)),
        "binder_sha256": sha(compass_script), "status": compass["status"],
        "binder_output": compass_result.stdout.strip(),
        "receipt": str(compass_path.relative_to(ROOT)), "receipt_sha256": sha(compass_path),
        "source": compass["source"], "source_sha256": compass["source_sha256"],
        "source_owned_symbols": compass["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 237, "unresolved_after": 246,
        "imports_resolved": compass["imports_resolved"],
        "imports_added": compass["imports_added"],
    })
    previous = linked
    metrics_script = HERE / "bind_main_lv_compass_metrics_20261015.py"
    metrics_result = subprocess.run([sys.executable, str(metrics_script)], check=True,
                                    capture_output=True, text=True)
    metrics_path = G2 / "build/c-firmware/20261015/main-lv-compass-metrics/receipt.json"
    metrics = json.loads(metrics_path.read_text())
    if metrics["status"] != "PASS_EXPERIMENTAL_MAIN_LV_COMPASS_METRICS_C":
        raise RuntimeError("LV extent metric stage status changed")
    base = file_from_receipt(metrics, "base_object", "base_sha256")
    linked = file_from_receipt(metrics, "linked_object", "linked_sha256")
    owned = {f"audio_uart_lv_compass_part_{address:x}" for address in
             (0x452450, 0x452498, 0x45246e, 0x45245a, 0x452464,
              0x452410, 0x45243a, 0x452446, 0x4522d4, 0x4522de)}
    if base != previous or len(imports(base)) != 246 or len(imports(linked)) != 236 or \
            imports(base) - imports(linked) != owned or imports(linked) - imports(base) or \
            set(metrics["source_owned_symbols"]) != owned:
        raise RuntimeError("LV extent metric stage handoff changed")
    if sha(ROOT / metrics["source"]) != metrics["source_sha256"] or \
            sha(ROOT / metrics["existing_style_source"]) != metrics["existing_style_source_sha256"]:
        raise RuntimeError("stale LV extent metric or style source")
    records.append({
        "stage": "main-lv-compass-metrics", "binder": str(metrics_script.relative_to(ROOT)),
        "binder_sha256": sha(metrics_script), "status": metrics["status"],
        "binder_output": metrics_result.stdout.strip(),
        "receipt": str(metrics_path.relative_to(ROOT)), "receipt_sha256": sha(metrics_path),
        "source": metrics["source"], "source_sha256": metrics["source_sha256"],
        "existing_style_source": metrics["existing_style_source"],
        "existing_style_source_sha256": metrics["existing_style_source_sha256"],
        "source_owned_symbols": metrics["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 246, "unresolved_after": 236,
        "imports_resolved": metrics["imports_resolved"], "imports_added": [],
    })
    previous = linked
    layer_script = HERE / "bind_main_lv_event_layer_451960_20261015.py"
    layer_result = subprocess.run([sys.executable, str(layer_script)], check=True,
                                  capture_output=True, text=True)
    layer_path = G2 / "build/c-firmware/20261015/main-lv-event-layer-451960/receipt.json"
    layer = json.loads(layer_path.read_text())
    if layer["status"] != "PASS_EXPERIMENTAL_MAIN_LV_EVENT_LAYER_C":
        raise RuntimeError("LV event layer stage status changed")
    base = file_from_receipt(layer, "base_object", "base_sha256")
    linked = file_from_receipt(layer, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_event_layer_451960"}
    if base != previous or len(imports(base)) != 236 or len(imports(linked)) != 236 or \
            imports(base) != imports(linked) or set(layer["source_owned_symbols"]) != owned:
        raise RuntimeError("LV event layer stage handoff changed")
    if sha(ROOT / layer["source"]) != layer["source_sha256"]:
        raise RuntimeError("stale LV event layer source")
    records.append({
        "stage": "main-lv-event-layer-451960", "binder": str(layer_script.relative_to(ROOT)),
        "binder_sha256": sha(layer_script), "status": layer["status"],
        "binder_output": layer_result.stdout.strip(),
        "receipt": str(layer_path.relative_to(ROOT)), "receipt_sha256": sha(layer_path),
        "source": layer["source"], "source_sha256": layer["source_sha256"],
        "source_owned_symbols": layer["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 236, "unresolved_after": 236,
        "imports_resolved": [], "imports_added": [],
    })
    previous = linked
    event_metrics_script = HERE / "bind_main_lv_event_state_metrics_20261015.py"
    event_metrics_result = subprocess.run([sys.executable, str(event_metrics_script)], check=True,
                                          capture_output=True, text=True)
    event_metrics_path = G2 / "build/c-firmware/20261015/main-lv-event-state-metrics/receipt.json"
    event_metrics = json.loads(event_metrics_path.read_text())
    if event_metrics["status"] != "PASS_EXPERIMENTAL_MAIN_LV_EVENT_STATE_METRICS_C":
        raise RuntimeError("LV event-state metric stage status changed")
    base = file_from_receipt(event_metrics, "base_object", "base_sha256")
    linked = file_from_receipt(event_metrics, "linked_object", "linked_sha256")
    owned = {f"audio_uart_lv_event_state_metric_{address:x}" for address in
             (0x43de4a, 0x43dd72, 0x43dd7c, 0x43ddd8, 0x43dda8,
              0x43de6a, 0x43ddb4, 0x43ddcc, 0x43ddc0, 0x43de54)}
    if base != previous or len(imports(base)) != 236 or len(imports(linked)) != 236 or \
            imports(base) != imports(linked) or \
            set(event_metrics["source_owned_symbols"]) != owned:
        raise RuntimeError("LV event-state metric stage handoff changed")
    if sha(ROOT / event_metrics["source"]) != event_metrics["source_sha256"] or \
            sha(ROOT / event_metrics["existing_style_source"]) != event_metrics["existing_style_source_sha256"]:
        raise RuntimeError("stale LV event-state metric or style source")
    records.append({
        "stage": "main-lv-event-state-metrics", "binder": str(event_metrics_script.relative_to(ROOT)),
        "binder_sha256": sha(event_metrics_script), "status": event_metrics["status"],
        "binder_output": event_metrics_result.stdout.strip(),
        "receipt": str(event_metrics_path.relative_to(ROOT)),
        "receipt_sha256": sha(event_metrics_path),
        "source": event_metrics["source"], "source_sha256": event_metrics["source_sha256"],
        "existing_style_source": event_metrics["existing_style_source"],
        "existing_style_source_sha256": event_metrics["existing_style_source_sha256"],
        "source_owned_symbols": event_metrics["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 236, "unresolved_after": 236,
        "imports_resolved": [], "imports_added": [],
    })
    previous = linked
    small_script = HERE / "bind_main_lv_event_state_small_helpers_20261015.py"
    small_result = subprocess.run([sys.executable, str(small_script)], check=True,
                                  capture_output=True, text=True)
    small_path = G2 / "build/c-firmware/20261015/main-lv-event-state-small-helpers/receipt.json"
    small = json.loads(small_path.read_text())
    if small["status"] != "PASS_EXPERIMENTAL_MAIN_LV_EVENT_STATE_SMALL_HELPERS_C":
        raise RuntimeError("LV event-state small helper stage status changed")
    base = file_from_receipt(small, "base_object", "base_sha256")
    linked = file_from_receipt(small, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_event_area_copy_43dcc0",
             "audio_uart_lv_event_state_metric_43de06",
             "audio_uart_lv_event_state_metric_43ddfc"}
    if base != previous or len(imports(base)) != 236 or len(imports(linked)) != 236 or \
            imports(base) != imports(linked) or set(small["source_owned_symbols"]) != owned:
        raise RuntimeError("LV event-state small helper stage handoff changed")
    if sha(ROOT / small["source"]) != small["source_sha256"]:
        raise RuntimeError("stale LV event-state small helper source")
    records.append({
        "stage": "main-lv-event-state-small-helpers", "binder": str(small_script.relative_to(ROOT)),
        "binder_sha256": sha(small_script), "status": small["status"],
        "binder_output": small_result.stdout.strip(),
        "receipt": str(small_path.relative_to(ROOT)), "receipt_sha256": sha(small_path),
        "source": small["source"], "source_sha256": small["source_sha256"],
        "source_owned_symbols": small["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 236, "unresolved_after": 236,
        "imports_resolved": [], "imports_added": [],
    })
    previous = linked
    event_state_script = HERE / "bind_main_lv_obj_event_state_43e442_20261015.py"
    event_state_result = subprocess.run([sys.executable, str(event_state_script)], check=True,
                                        capture_output=True, text=True)
    event_state_path = G2 / "build/c-firmware/20261015/main-lv-obj-event-state-43e442/receipt.json"
    event_state = json.loads(event_state_path.read_text())
    if event_state["status"] != "PASS_EXPERIMENTAL_MAIN_LV_OBJ_EVENT_STATE_C":
        raise RuntimeError("LV event-state stage status changed")
    base = file_from_receipt(event_state, "base_object", "base_sha256")
    linked = file_from_receipt(event_state, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_obj_event_state_43e442"}
    lower = {"audio_uart_lv_draw_scrollbars_43e63e",
             "audio_uart_lv_draw_task_build_452616",
             "audio_uart_lv_draw_task_init_451b9c",
             "audio_uart_lv_draw_task_render_451c6e"}
    if base != previous or len(imports(base)) != 236 or len(imports(linked)) != 239 or \
            imports(base) - imports(linked) != owned or \
            imports(linked) - imports(base) != lower or \
            set(event_state["source_owned_symbols"]) != owned:
        raise RuntimeError("LV event-state stage handoff changed")
    if sha(ROOT / event_state["source"]) != event_state["source_sha256"]:
        raise RuntimeError("stale LV event-state source")
    records.append({
        "stage": "main-lv-obj-event-state-43e442",
        "binder": str(event_state_script.relative_to(ROOT)),
        "binder_sha256": sha(event_state_script), "status": event_state["status"],
        "binder_output": event_state_result.stdout.strip(),
        "receipt": str(event_state_path.relative_to(ROOT)),
        "receipt_sha256": sha(event_state_path),
        "source": event_state["source"], "source_sha256": event_state["source_sha256"],
        "source_owned_symbols": event_state["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 236, "unresolved_after": 239,
        "imports_resolved": event_state["imports_resolved"],
        "imports_added": event_state["imports_added"],
    })
    previous = linked
    scrollbars_script = HERE / "bind_main_lv_draw_scrollbars_43e63e_20261015.py"
    scrollbars_result = subprocess.run([sys.executable, str(scrollbars_script)], check=True,
                                       capture_output=True, text=True)
    scrollbars_path = G2 / "build/c-firmware/20261015/main-lv-draw-scrollbars-43e63e/receipt.json"
    scrollbars = json.loads(scrollbars_path.read_text())
    if scrollbars["status"] != "PASS_EXPERIMENTAL_MAIN_LV_DRAW_SCROLLBARS_C":
        raise RuntimeError("LV draw scrollbar stage status changed")
    base = file_from_receipt(scrollbars, "base_object", "base_sha256")
    linked = file_from_receipt(scrollbars, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_draw_scrollbars_43e63e"}
    lower = {"audio_uart_lv_scrollbar_draw_descriptor_43e6a6"}
    if base != previous or len(imports(base)) != 239 or len(imports(linked)) != 239 or \
            imports(base) - imports(linked) != owned or \
            imports(linked) - imports(base) != lower or \
            set(scrollbars["source_owned_symbols"]) != owned:
        raise RuntimeError("LV draw scrollbar stage handoff changed")
    if sha(ROOT / scrollbars["source"]) != scrollbars["source_sha256"]:
        raise RuntimeError("stale LV draw scrollbar source")
    records.append({
        "stage": "main-lv-draw-scrollbars-43e63e",
        "binder": str(scrollbars_script.relative_to(ROOT)),
        "binder_sha256": sha(scrollbars_script), "status": scrollbars["status"],
        "binder_output": scrollbars_result.stdout.strip(),
        "receipt": str(scrollbars_path.relative_to(ROOT)),
        "receipt_sha256": sha(scrollbars_path),
        "source": scrollbars["source"], "source_sha256": scrollbars["source_sha256"],
        "source_owned_symbols": scrollbars["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 239, "unresolved_after": 239,
        "imports_resolved": scrollbars["imports_resolved"],
        "imports_added": scrollbars["imports_added"],
    })
    previous = linked
    descriptor_script = HERE / "bind_main_lv_scrollbar_descriptor_43e6a6_20261015.py"
    descriptor_result = subprocess.run([sys.executable, str(descriptor_script)], check=True,
                                       capture_output=True, text=True)
    descriptor_path = G2 / "build/c-firmware/20261015/main-lv-scrollbar-descriptor-43e6a6/receipt.json"
    descriptor = json.loads(descriptor_path.read_text())
    if descriptor["status"] != "PASS_EXPERIMENTAL_MAIN_LV_SCROLLBAR_DESCRIPTOR_C":
        raise RuntimeError("LV scrollbar descriptor stage status changed")
    base = file_from_receipt(descriptor, "base_object", "base_sha256")
    linked = file_from_receipt(descriptor, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_scrollbar_draw_descriptor_43e6a6"}
    lower = {"audio_uart_lv_effective_opacity_44c47a"} | {
        f"audio_uart_lv_scrollbar_metric_{address:x}" for address in
        (0x43dd9a, 0x43ddf0, 0x43dde2, 0x43de3e, 0x43de1c, 0x43de26, 0x43de30)}
    if base != previous or len(imports(base)) != 239 or len(imports(linked)) != 246 or \
            imports(base) - imports(linked) != owned or \
            imports(linked) - imports(base) != lower or \
            set(descriptor["source_owned_symbols"]) != owned:
        raise RuntimeError("LV scrollbar descriptor stage handoff changed")
    if sha(ROOT / descriptor["source"]) != descriptor["source_sha256"]:
        raise RuntimeError("stale LV scrollbar descriptor source")
    records.append({
        "stage": "main-lv-scrollbar-descriptor-43e6a6",
        "binder": str(descriptor_script.relative_to(ROOT)),
        "binder_sha256": sha(descriptor_script), "status": descriptor["status"],
        "binder_output": descriptor_result.stdout.strip(),
        "receipt": str(descriptor_path.relative_to(ROOT)),
        "receipt_sha256": sha(descriptor_path),
        "source": descriptor["source"], "source_sha256": descriptor["source_sha256"],
        "source_owned_symbols": descriptor["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 239, "unresolved_after": 246,
        "imports_resolved": descriptor["imports_resolved"],
        "imports_added": descriptor["imports_added"],
    })
    previous = linked
    scrollbar_metrics_script = HERE / "bind_main_lv_scrollbar_metrics_20261015.py"
    scrollbar_metrics_result = subprocess.run([sys.executable, str(scrollbar_metrics_script)],
                                              check=True, capture_output=True, text=True)
    scrollbar_metrics_path = G2 / "build/c-firmware/20261015/main-lv-scrollbar-metrics/receipt.json"
    scrollbar_metrics = json.loads(scrollbar_metrics_path.read_text())
    if scrollbar_metrics["status"] != "PASS_EXPERIMENTAL_MAIN_LV_SCROLLBAR_METRICS_C":
        raise RuntimeError("LV scrollbar metric stage status changed")
    base = file_from_receipt(scrollbar_metrics, "base_object", "base_sha256")
    linked = file_from_receipt(scrollbar_metrics, "linked_object", "linked_sha256")
    owned = {f"audio_uart_lv_scrollbar_metric_{address:x}" for address in
             (0x43dd9a, 0x43ddf0, 0x43dde2, 0x43de3e, 0x43de1c, 0x43de26, 0x43de30)}
    if base != previous or len(imports(base)) != 246 or len(imports(linked)) != 239 or \
            imports(base) - imports(linked) != owned or \
            imports(linked) - imports(base) or \
            set(scrollbar_metrics["source_owned_symbols"]) != owned:
        raise RuntimeError("LV scrollbar metric stage handoff changed")
    if sha(ROOT / scrollbar_metrics["source"]) != scrollbar_metrics["source_sha256"] or \
            sha(ROOT / scrollbar_metrics["existing_style_source"]) != scrollbar_metrics["existing_style_source_sha256"]:
        raise RuntimeError("stale LV scrollbar metric or style source")
    records.append({
        "stage": "main-lv-scrollbar-metrics",
        "binder": str(scrollbar_metrics_script.relative_to(ROOT)),
        "binder_sha256": sha(scrollbar_metrics_script), "status": scrollbar_metrics["status"],
        "binder_output": scrollbar_metrics_result.stdout.strip(),
        "receipt": str(scrollbar_metrics_path.relative_to(ROOT)),
        "receipt_sha256": sha(scrollbar_metrics_path),
        "source": scrollbar_metrics["source"],
        "source_sha256": scrollbar_metrics["source_sha256"],
        "existing_style_source": scrollbar_metrics["existing_style_source"],
        "existing_style_source_sha256": scrollbar_metrics["existing_style_source_sha256"],
        "source_owned_symbols": scrollbar_metrics["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 246, "unresolved_after": 239,
        "imports_resolved": scrollbar_metrics["imports_resolved"], "imports_added": [],
    })
    previous = linked
    opacity_script = HERE / "bind_main_lv_effective_opacity_44c47a_20261015.py"
    opacity_result = subprocess.run([sys.executable, str(opacity_script)], check=True,
                                    capture_output=True, text=True)
    opacity_path = G2 / "build/c-firmware/20261015/main-lv-effective-opacity-44c47a/receipt.json"
    opacity = json.loads(opacity_path.read_text())
    if opacity["status"] != "PASS_EXPERIMENTAL_MAIN_LV_EFFECTIVE_OPACITY_C":
        raise RuntimeError("LV effective opacity stage status changed")
    base = file_from_receipt(opacity, "base_object", "base_sha256")
    linked = file_from_receipt(opacity, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_style_opacity_44b8b8",
             "audio_uart_lv_effective_opacity_44c47a"}
    if base != previous or len(imports(base)) != 239 or len(imports(linked)) != 238 or \
            imports(base) - imports(linked) != {"audio_uart_lv_effective_opacity_44c47a"} or \
            imports(linked) - imports(base) or \
            set(opacity["source_owned_symbols"]) != owned:
        raise RuntimeError("LV effective opacity stage handoff changed")
    if sha(ROOT / opacity["source"]) != opacity["source_sha256"]:
        raise RuntimeError("stale LV effective opacity source")
    records.append({
        "stage": "main-lv-effective-opacity-44c47a",
        "binder": str(opacity_script.relative_to(ROOT)),
        "binder_sha256": sha(opacity_script), "status": opacity["status"],
        "binder_output": opacity_result.stdout.strip(),
        "receipt": str(opacity_path.relative_to(ROOT)),
        "receipt_sha256": sha(opacity_path),
        "source": opacity["source"], "source_sha256": opacity["source_sha256"],
        "source_owned_symbols": opacity["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 239, "unresolved_after": 238,
        "imports_resolved": opacity["imports_resolved"], "imports_added": [],
    })
    previous = linked
    draw_init_script = HERE / "bind_main_lv_draw_task_init_451b9c_20261015.py"
    draw_init_result = subprocess.run([sys.executable, str(draw_init_script)], check=True,
                                      capture_output=True, text=True)
    draw_init_path = G2 / "build/c-firmware/20261015/main-lv-draw-task-init-451b9c/receipt.json"
    draw_init = json.loads(draw_init_path.read_text())
    if draw_init["status"] != "PASS_EXPERIMENTAL_MAIN_LV_DRAW_TASK_INIT_C":
        raise RuntimeError("LV draw task init stage status changed")
    base = file_from_receipt(draw_init, "base_object", "base_sha256")
    linked = file_from_receipt(draw_init, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_draw_task_init_451b9c"}
    if base != previous or len(imports(base)) != 238 or len(imports(linked)) != 237 or \
            imports(base) - imports(linked) != owned or imports(linked) - imports(base) or \
            set(draw_init["source_owned_symbols"]) != owned:
        raise RuntimeError("LV draw task init stage handoff changed")
    if sha(ROOT / draw_init["source"]) != draw_init["source_sha256"]:
        raise RuntimeError("stale LV draw task init source")
    records.append({
        "stage": "main-lv-draw-task-init-451b9c",
        "binder": str(draw_init_script.relative_to(ROOT)),
        "binder_sha256": sha(draw_init_script), "status": draw_init["status"],
        "binder_output": draw_init_result.stdout.strip(),
        "receipt": str(draw_init_path.relative_to(ROOT)),
        "receipt_sha256": sha(draw_init_path),
        "source": draw_init["source"], "source_sha256": draw_init["source_sha256"],
        "source_owned_symbols": draw_init["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 238, "unresolved_after": 237,
        "imports_resolved": draw_init["imports_resolved"], "imports_added": [],
    })
    previous = linked
    draw_opacity_script = HERE / "bind_main_lv_draw_task_opacity_452df0_20261015.py"
    draw_opacity_result = subprocess.run([sys.executable, str(draw_opacity_script)], check=True,
                                         capture_output=True, text=True)
    draw_opacity_path = G2 / "build/c-firmware/20261015/main-lv-draw-task-opacity-452df0/receipt.json"
    draw_opacity = json.loads(draw_opacity_path.read_text())
    if draw_opacity["status"] != "PASS_EXPERIMENTAL_MAIN_LV_DRAW_TASK_OPACITY_C":
        raise RuntimeError("LV draw-task opacity stage status changed")
    base = file_from_receipt(draw_opacity, "base_object", "base_sha256")
    linked = file_from_receipt(draw_opacity, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_draw_task_style_opacity_4525fe",
             "audio_uart_lv_draw_task_opacity_452df0"}
    if base != previous or len(imports(base)) != 237 or len(imports(linked)) != 237 or \
            imports(base) != imports(linked) or \
            set(draw_opacity["source_owned_symbols"]) != owned:
        raise RuntimeError("LV draw-task opacity stage handoff changed")
    if sha(ROOT / draw_opacity["source"]) != draw_opacity["source_sha256"]:
        raise RuntimeError("stale LV draw-task opacity source")
    records.append({
        "stage": "main-lv-draw-task-opacity-452df0",
        "binder": str(draw_opacity_script.relative_to(ROOT)),
        "binder_sha256": sha(draw_opacity_script), "status": draw_opacity["status"],
        "binder_output": draw_opacity_result.stdout.strip(),
        "receipt": str(draw_opacity_path.relative_to(ROOT)),
        "receipt_sha256": sha(draw_opacity_path),
        "source": draw_opacity["source"], "source_sha256": draw_opacity["source_sha256"],
        "source_owned_symbols": draw_opacity["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 237, "unresolved_after": 237,
        "imports_resolved": [], "imports_added": [],
    })
    previous = linked
    draw_metrics_script = HERE / "bind_main_lv_draw_task_metrics_20261015.py"
    draw_metrics_result = subprocess.run([sys.executable, str(draw_metrics_script)], check=True,
                                         capture_output=True, text=True)
    draw_metrics_path = G2 / "build/c-firmware/20261015/main-lv-draw-task-metrics/receipt.json"
    draw_metrics = json.loads(draw_metrics_path.read_text())
    if draw_metrics["status"] != "PASS_EXPERIMENTAL_MAIN_LV_DRAW_TASK_METRICS_C":
        raise RuntimeError("LV draw-task metrics stage status changed")
    base = file_from_receipt(draw_metrics, "base_object", "base_sha256")
    linked = file_from_receipt(draw_metrics, "linked_object", "linked_sha256")
    owned = {f"audio_uart_lv_draw_metric_{address}" for address in
             re.findall(r"^(?:RAW|BYTE|BOOL)\(([0-9a-f]{6}),",
                        (G2 / "components/audio/uart_thread_source_candidate/display_lv_draw_task_metrics.c").read_text(),
                        re.M)}
    if base != previous or len(imports(base)) != 237 or len(imports(linked)) != 237 or \
            imports(base) != imports(linked) or len(owned) != 43 or \
            set(draw_metrics["source_owned_symbols"]) != owned:
        raise RuntimeError("LV draw-task metrics stage handoff changed")
    if sha(ROOT / draw_metrics["source"]) != draw_metrics["source_sha256"]:
        raise RuntimeError("stale LV draw-task metrics source")
    records.append({
        "stage": "main-lv-draw-task-metrics",
        "binder": str(draw_metrics_script.relative_to(ROOT)),
        "binder_sha256": sha(draw_metrics_script), "status": draw_metrics["status"],
        "binder_output": draw_metrics_result.stdout.strip(),
        "receipt": str(draw_metrics_path.relative_to(ROOT)),
        "receipt_sha256": sha(draw_metrics_path),
        "source": draw_metrics["source"], "source_sha256": draw_metrics["source_sha256"],
        "source_owned_symbols": draw_metrics["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 237, "unresolved_after": 237,
        "imports_resolved": [], "imports_added": [],
    })
    previous = linked
    draw_color_script = HERE / "bind_main_lv_draw_color_helpers_20261015.py"
    draw_color_result = subprocess.run([sys.executable, str(draw_color_script)], check=True,
                                       capture_output=True, text=True)
    draw_color_path = G2 / "build/c-firmware/20261015/main-lv-draw-color-helpers/receipt.json"
    draw_color = json.loads(draw_color_path.read_text())
    if draw_color["status"] != "PASS_EXPERIMENTAL_MAIN_LV_DRAW_COLOR_HELPERS_C":
        raise RuntimeError("LV draw color helper stage status changed")
    base = file_from_receipt(draw_color, "base_object", "base_sha256")
    linked = file_from_receipt(draw_color, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_color_with_alpha_440fde",
             "audio_uart_lv_draw_color_style_44b8d0",
             "audio_uart_lv_draw_color_style_44b8de"}
    if base != previous or len(imports(base)) != 237 or len(imports(linked)) != 237 or \
            imports(base) != imports(linked) or \
            set(draw_color["source_owned_symbols"]) != owned:
        raise RuntimeError("LV draw color helper stage handoff changed")
    if sha(ROOT / draw_color["source"]) != draw_color["source_sha256"]:
        raise RuntimeError("stale LV draw color helper source")
    records.append({
        "stage": "main-lv-draw-color-helpers",
        "binder": str(draw_color_script.relative_to(ROOT)),
        "binder_sha256": sha(draw_color_script), "status": draw_color["status"],
        "binder_output": draw_color_result.stdout.strip(),
        "receipt": str(draw_color_path.relative_to(ROOT)),
        "receipt_sha256": sha(draw_color_path),
        "source": draw_color["source"], "source_sha256": draw_color["source_sha256"],
        "source_owned_symbols": draw_color["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 237, "unresolved_after": 237,
        "imports_resolved": [], "imports_added": [],
    })
    previous = linked
    draw_composition_script = HERE / "bind_main_lv_draw_color_composition_44c54a_20261015.py"
    draw_composition_result = subprocess.run([sys.executable, str(draw_composition_script)],
                                             check=True, capture_output=True, text=True)
    draw_composition_path = G2 / "build/c-firmware/20261015/main-lv-draw-color-composition-44c54a/receipt.json"
    draw_composition = json.loads(draw_composition_path.read_text())
    if draw_composition["status"] != "PASS_EXPERIMENTAL_MAIN_LV_DRAW_COLOR_COMPOSITION_C":
        raise RuntimeError("LV draw color composition stage status changed")
    base = file_from_receipt(draw_composition, "base_object", "base_sha256")
    linked = file_from_receipt(draw_composition, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_draw_color_composite_44c54a",
             "audio_uart_lv_draw_color_chain_44c582"}
    lower = {"audio_uart_lv_color_blend_482ef6"}
    if base != previous or len(imports(base)) != 237 or len(imports(linked)) != 238 or \
            imports(base) - imports(linked) or imports(linked) - imports(base) != lower or \
            set(draw_composition["source_owned_symbols"]) != owned:
        raise RuntimeError("LV draw color composition stage handoff changed")
    if sha(ROOT / draw_composition["source"]) != draw_composition["source_sha256"] or \
            sha(ROOT / draw_composition["leaf_source"]) != draw_composition["leaf_source_sha256"]:
        raise RuntimeError("stale LV draw color composition or leaf source")
    records.append({
        "stage": "main-lv-draw-color-composition-44c54a",
        "binder": str(draw_composition_script.relative_to(ROOT)),
        "binder_sha256": sha(draw_composition_script), "status": draw_composition["status"],
        "binder_output": draw_composition_result.stdout.strip(),
        "receipt": str(draw_composition_path.relative_to(ROOT)),
        "receipt_sha256": sha(draw_composition_path),
        "source": draw_composition["source"], "source_sha256": draw_composition["source_sha256"],
        "leaf_source": draw_composition["leaf_source"],
        "leaf_source_sha256": draw_composition["leaf_source_sha256"],
        "source_owned_symbols": draw_composition["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 237, "unresolved_after": 238,
        "imports_resolved": [], "imports_added": draw_composition["imports_added"],
    })
    previous = linked
    color_blend_script = HERE / "bind_main_lv_color_blend_482ef6_20261015.py"
    color_blend_result = subprocess.run([sys.executable, str(color_blend_script)], check=True,
                                        capture_output=True, text=True)
    color_blend_path = G2 / "build/c-firmware/20261015/main-lv-color-blend-482ef6/receipt.json"
    color_blend = json.loads(color_blend_path.read_text())
    if color_blend["status"] != "PASS_EXPERIMENTAL_MAIN_LV_COLOR_BLEND_C":
        raise RuntimeError("LV color blend stage status changed")
    base = file_from_receipt(color_blend, "base_object", "base_sha256")
    linked = file_from_receipt(color_blend, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_color_rgb_blend_482e4c", "audio_uart_lv_color_blend_482ef6"}
    resolved = {"audio_uart_lv_color_blend_482ef6"}
    if base != previous or len(imports(base)) != 238 or len(imports(linked)) != 237 or \
            imports(base) - imports(linked) != resolved or imports(linked) - imports(base) or \
            set(color_blend["source_owned_symbols"]) != owned:
        raise RuntimeError("LV color blend stage handoff changed")
    if sha(ROOT / color_blend["source"]) != color_blend["source_sha256"]:
        raise RuntimeError("stale LV color blend source")
    records.append({
        "stage": "main-lv-color-blend-482ef6",
        "binder": str(color_blend_script.relative_to(ROOT)),
        "binder_sha256": sha(color_blend_script), "status": color_blend["status"],
        "binder_output": color_blend_result.stdout.strip(),
        "receipt": str(color_blend_path.relative_to(ROOT)),
        "receipt_sha256": sha(color_blend_path),
        "source": color_blend["source"], "source_sha256": color_blend["source_sha256"],
        "source_owned_symbols": color_blend["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 238, "unresolved_after": 237,
        "imports_resolved": color_blend["imports_resolved"], "imports_added": [],
    })
    previous = linked
    color_variant_script = HERE / "bind_main_lv_draw_color_variant_452e68_20261015.py"
    color_variant_result = subprocess.run([sys.executable, str(color_variant_script)], check=True,
                                          capture_output=True, text=True)
    color_variant_path = G2 / "build/c-firmware/20261015/main-lv-draw-color-variant-452e68/receipt.json"
    color_variant = json.loads(color_variant_path.read_text())
    if color_variant["status"] != "PASS_EXPERIMENTAL_MAIN_LV_DRAW_COLOR_VARIANT_C":
        raise RuntimeError("LV draw color variant stage status changed")
    base = file_from_receipt(color_variant, "base_object", "base_sha256")
    linked = file_from_receipt(color_variant, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_draw_color_variant_452e68"}
    if base != previous or len(imports(base)) != 237 or len(imports(linked)) != 237 or \
            imports(base) != imports(linked) or \
            set(color_variant["source_owned_symbols"]) != owned:
        raise RuntimeError("LV draw color variant stage handoff changed")
    if sha(ROOT / color_variant["source"]) != color_variant["source_sha256"]:
        raise RuntimeError("stale LV draw color variant source")
    records.append({
        "stage": "main-lv-draw-color-variant-452e68",
        "binder": str(color_variant_script.relative_to(ROOT)),
        "binder_sha256": sha(color_variant_script), "status": color_variant["status"],
        "binder_output": color_variant_result.stdout.strip(),
        "receipt": str(color_variant_path.relative_to(ROOT)),
        "receipt_sha256": sha(color_variant_path),
        "source": color_variant["source"], "source_sha256": color_variant["source_sha256"],
        "source_owned_symbols": color_variant["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 237, "unresolved_after": 237,
        "imports_resolved": [], "imports_added": [],
    })
    previous = linked
    rgb_mix_script = HERE / "bind_main_lv_draw_rgb_mix_452e22_20261015.py"
    rgb_mix_result = subprocess.run([sys.executable, str(rgb_mix_script)], check=True,
                                    capture_output=True, text=True)
    rgb_mix_path = G2 / "build/c-firmware/20261015/main-lv-draw-rgb-mix-452e22/receipt.json"
    rgb_mix = json.loads(rgb_mix_path.read_text())
    if rgb_mix["status"] != "PASS_EXPERIMENTAL_MAIN_LV_DRAW_RGB_MIX_LOW24_C":
        raise RuntimeError("LV draw RGB mix stage status changed")
    base = file_from_receipt(rgb_mix, "base_object", "base_sha256")
    linked = file_from_receipt(rgb_mix, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_color_rgb_mix_482dd8", "audio_uart_lv_draw_rgb_mix_452e22"}
    if base != previous or len(imports(base)) != 237 or len(imports(linked)) != 237 or \
            imports(base) != imports(linked) or set(rgb_mix["source_owned_symbols"]) != owned:
        raise RuntimeError("LV draw RGB mix stage handoff changed")
    if sha(ROOT / rgb_mix["source"]) != rgb_mix["source_sha256"]:
        raise RuntimeError("stale LV draw RGB mix source")
    records.append({
        "stage": "main-lv-draw-rgb-mix-452e22",
        "binder": str(rgb_mix_script.relative_to(ROOT)),
        "binder_sha256": sha(rgb_mix_script), "status": rgb_mix["status"],
        "binder_output": rgb_mix_result.stdout.strip(),
        "receipt": str(rgb_mix_path.relative_to(ROOT)),
        "receipt_sha256": sha(rgb_mix_path),
        "source": rgb_mix["source"], "source_sha256": rgb_mix["source_sha256"],
        "source_owned_symbols": rgb_mix["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 237, "unresolved_after": 237,
        "imports_resolved": [], "imports_added": [],
        "comparison_scope": "low 24 RGB bits; stock top byte unwritten",
    })
    previous = linked
    draw_build_script = HERE / "bind_main_lv_draw_task_build_452616_20261015.py"
    draw_build_result = subprocess.run([sys.executable, str(draw_build_script)], check=True,
                                       capture_output=True, text=True)
    draw_build_path = G2 / "build/c-firmware/20261015/main-lv-draw-task-build-452616/receipt.json"
    draw_build = json.loads(draw_build_path.read_text())
    if draw_build["status"] != "PASS_EXPERIMENTAL_MAIN_LV_DRAW_TASK_BUILD_C":
        raise RuntimeError("LV draw-task builder stage status changed")
    base = file_from_receipt(draw_build, "base_object", "base_sha256")
    linked = file_from_receipt(draw_build, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_draw_task_build_452616"}
    if base != previous or len(imports(base)) != 237 or len(imports(linked)) != 236 or \
            imports(base) - imports(linked) != owned or imports(linked) - imports(base) or \
            set(draw_build["source_owned_symbols"]) != owned:
        raise RuntimeError("LV draw-task builder stage handoff changed")
    if sha(ROOT / draw_build["source"]) != draw_build["source_sha256"]:
        raise RuntimeError("stale LV draw-task builder source")
    records.append({
        "stage": "main-lv-draw-task-build-452616",
        "binder": str(draw_build_script.relative_to(ROOT)),
        "binder_sha256": sha(draw_build_script), "status": draw_build["status"],
        "binder_output": draw_build_result.stdout.strip(),
        "receipt": str(draw_build_path.relative_to(ROOT)),
        "receipt_sha256": sha(draw_build_path),
        "source": draw_build["source"], "source_sha256": draw_build["source_sha256"],
        "source_owned_symbols": draw_build["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 237, "unresolved_after": 236,
        "imports_resolved": draw_build["imports_resolved"], "imports_added": [],
    })
    previous = linked
    descriptor_script = HERE / "bind_main_lv_draw_descriptor_init_451c3a_20261015.py"
    descriptor_result = subprocess.run([sys.executable, str(descriptor_script)], check=True,
                                       capture_output=True, text=True)
    descriptor_path = G2 / "build/c-firmware/20261015/main-lv-draw-descriptor-init-451c3a/receipt.json"
    descriptor = json.loads(descriptor_path.read_text())
    if descriptor["status"] != "PASS_EXPERIMENTAL_MAIN_LV_DRAW_DESCRIPTOR_INIT_C":
        raise RuntimeError("LV draw descriptor initializer status changed")
    base = file_from_receipt(descriptor, "base_object", "base_sha256")
    linked = file_from_receipt(descriptor, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_draw_descriptor_init_451c3a"}
    if base != previous or len(imports(base)) != 236 or imports(base) != imports(linked) or \
            set(descriptor["source_owned_symbols"]) != owned:
        raise RuntimeError("LV draw descriptor initializer handoff changed")
    if sha(ROOT / descriptor["source"]) != descriptor["source_sha256"]:
        raise RuntimeError("stale LV draw descriptor initializer source")
    records.append({
        "stage": "main-lv-draw-descriptor-init-451c3a",
        "binder": str(descriptor_script.relative_to(ROOT)),
        "binder_sha256": sha(descriptor_script), "status": descriptor["status"],
        "binder_output": descriptor_result.stdout.strip(),
        "receipt": str(descriptor_path.relative_to(ROOT)),
        "receipt_sha256": sha(descriptor_path),
        "source": descriptor["source"], "source_sha256": descriptor["source_sha256"],
        "source_owned_symbols": descriptor["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 236, "unresolved_after": 236,
        "imports_resolved": [], "imports_added": [],
    })
    previous = linked
    render_alloc_script = HERE / "bind_main_lv_render_task_alloc_4843ee_20261015.py"
    render_alloc_result = subprocess.run([sys.executable, str(render_alloc_script)], check=True,
                                         capture_output=True, text=True)
    render_alloc_path = G2 / "build/c-firmware/20261015/main-lv-render-task-alloc-4843ee/receipt.json"
    render_alloc = json.loads(render_alloc_path.read_text())
    if render_alloc["status"] != "PASS_EXPERIMENTAL_MAIN_LV_RENDER_TASK_ALLOC_C":
        raise RuntimeError("LV render task allocator status changed")
    base = file_from_receipt(render_alloc, "base_object", "base_sha256")
    linked = file_from_receipt(render_alloc, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_render_task_alloc_4843ee"}
    if base != previous or len(imports(base)) != 236 or imports(base) != imports(linked) or \
            set(render_alloc["source_owned_symbols"]) != owned:
        raise RuntimeError("LV render task allocator handoff changed")
    if sha(ROOT / render_alloc["source"]) != render_alloc["source_sha256"]:
        raise RuntimeError("stale LV render task allocator source")
    records.append({
        "stage": "main-lv-render-task-alloc-4843ee",
        "binder": str(render_alloc_script.relative_to(ROOT)),
        "binder_sha256": sha(render_alloc_script), "status": render_alloc["status"],
        "binder_output": render_alloc_result.stdout.strip(),
        "receipt": str(render_alloc_path.relative_to(ROOT)),
        "receipt_sha256": sha(render_alloc_path),
        "source": render_alloc["source"], "source_sha256": render_alloc["source_sha256"],
        "source_owned_symbols": render_alloc["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 236, "unresolved_after": 236,
        "imports_resolved": [], "imports_added": [],
        "comparison_scope": "successful zeroed allocation and list insertion",
    })
    previous = linked
    render_queue_script = HERE / "bind_main_lv_render_task_queue_484476_20261015.py"
    render_queue_result = subprocess.run([sys.executable, str(render_queue_script)], check=True,
                                         capture_output=True, text=True)
    render_queue_path = G2 / "build/c-firmware/20261015/main-lv-render-task-queue-484476/receipt.json"
    render_queue = json.loads(render_queue_path.read_text())
    if render_queue["status"] != "PASS_EXPERIMENTAL_MAIN_LV_RENDER_TASK_QUEUE_C":
        raise RuntimeError("LV render task queue status changed")
    base = file_from_receipt(render_queue, "base_object", "base_sha256")
    linked = file_from_receipt(render_queue, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_render_task_queue_484476"}
    added = {"audio_uart_lv_refresh_tasks_484548"}
    if base != previous or len(imports(base)) != 236 or len(imports(linked)) != 237 or \
            imports(linked) - imports(base) != added or imports(base) - imports(linked) or \
            set(render_queue["source_owned_symbols"]) != owned:
        raise RuntimeError("LV render task queue handoff changed")
    if sha(ROOT / render_queue["source"]) != render_queue["source_sha256"]:
        raise RuntimeError("stale LV render task queue source")
    records.append({
        "stage": "main-lv-render-task-queue-484476",
        "binder": str(render_queue_script.relative_to(ROOT)),
        "binder_sha256": sha(render_queue_script), "status": render_queue["status"],
        "binder_output": render_queue_result.stdout.strip(),
        "receipt": str(render_queue_path.relative_to(ROOT)),
        "receipt_sha256": sha(render_queue_path),
        "source": render_queue["source"], "source_sha256": render_queue["source_sha256"],
        "source_owned_symbols": render_queue["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 236, "unresolved_after": 237,
        "imports_resolved": [], "imports_added": render_queue["imports_added"],
        "comparison_scope": "controlled object event, callbacks, logger and refresh dispatch",
    })
    previous = linked
    refresh_script = HERE / "bind_main_lv_refresh_tasks_484548_20261015.py"
    refresh_result = subprocess.run([sys.executable, str(refresh_script)], check=True,
                                    capture_output=True, text=True)
    refresh_path = G2 / "build/c-firmware/20261015/main-lv-refresh-tasks-484548/receipt.json"
    refresh = json.loads(refresh_path.read_text())
    if refresh["status"] != "PASS_EXPERIMENTAL_MAIN_LV_REFRESH_TASKS_C":
        raise RuntimeError("LV refresh tasks status changed")
    base = file_from_receipt(refresh, "base_object", "base_sha256")
    linked = file_from_receipt(refresh, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_display_next_44fa22", "audio_uart_lv_render_idle_callbacks_484528",
             "audio_uart_lv_refresh_tasks_484548"}
    resolved = {"audio_uart_lv_refresh_tasks_484548"}
    added = {"audio_uart_lv_render_task_evaluate_48458e"}
    if base != previous or len(imports(base)) != 237 or len(imports(linked)) != 237 or \
            imports(base) - imports(linked) != resolved or imports(linked) - imports(base) != added or \
            set(refresh["source_owned_symbols"]) != owned:
        raise RuntimeError("LV refresh tasks handoff changed")
    if sha(ROOT / refresh["source"]) != refresh["source_sha256"]:
        raise RuntimeError("stale LV refresh tasks source")
    records.append({
        "stage": "main-lv-refresh-tasks-484548",
        "binder": str(refresh_script.relative_to(ROOT)),
        "binder_sha256": sha(refresh_script), "status": refresh["status"],
        "binder_output": refresh_result.stdout.strip(),
        "receipt": str(refresh_path.relative_to(ROOT)),
        "receipt_sha256": sha(refresh_path),
        "source": refresh["source"], "source_sha256": refresh["source_sha256"],
        "source_owned_symbols": refresh["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 237, "unresolved_after": 237,
        "imports_resolved": refresh["imports_resolved"],
        "imports_added": refresh["imports_added"],
        "comparison_scope": "controlled display iteration, task walk and idle callbacks",
    })
    previous = linked
    evaluate_script = HERE / "bind_main_lv_render_task_evaluate_48458e_20261015.py"
    evaluate_result = subprocess.run([sys.executable, str(evaluate_script)], check=True,
                                     capture_output=True, text=True)
    evaluate_path = G2 / "build/c-firmware/20261015/main-lv-render-task-evaluate-48458e/receipt.json"
    evaluate = json.loads(evaluate_path.read_text())
    if evaluate["status"] != "PASS_EXPERIMENTAL_MAIN_LV_RENDER_TASK_EVALUATE_C":
        raise RuntimeError("LV render task evaluator status changed")
    base = file_from_receipt(evaluate, "base_object", "base_sha256")
    linked = file_from_receipt(evaluate, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_render_task_evaluate_48458e"}
    added = {"audio_uart_lv_render_task_free_4848e8"}
    if base != previous or len(imports(base)) != 237 or len(imports(linked)) != 237 or \
            imports(base) - imports(linked) != owned or imports(linked) - imports(base) != added or \
            set(evaluate["source_owned_symbols"]) != owned:
        raise RuntimeError("LV render task evaluator handoff changed")
    if sha(ROOT / evaluate["source"]) != evaluate["source_sha256"]:
        raise RuntimeError("stale LV render task evaluator source")
    records.append({
        "stage": "main-lv-render-task-evaluate-48458e",
        "binder": str(evaluate_script.relative_to(ROOT)),
        "binder_sha256": sha(evaluate_script), "status": evaluate["status"],
        "binder_output": evaluate_result.stdout.strip(),
        "receipt": str(evaluate_path.relative_to(ROOT)),
        "receipt_sha256": sha(evaluate_path),
        "source": evaluate["source"], "source_sha256": evaluate["source_sha256"],
        "source_owned_symbols": evaluate["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 237, "unresolved_after": 237,
        "imports_resolved": evaluate["imports_resolved"],
        "imports_added": evaluate["imports_added"],
        "comparison_scope": "controlled completed-task removal, backend evaluation and parent wakeup",
    })
    previous = linked
    cleanup_script = HERE / "bind_main_lv_render_task_free_4848e8_20261015.py"
    cleanup_result = subprocess.run([sys.executable, str(cleanup_script)], check=True,
                                    capture_output=True, text=True)
    cleanup_path = G2 / "build/c-firmware/20261015/main-lv-render-task-free-4848e8/receipt.json"
    cleanup = json.loads(cleanup_path.read_text())
    if cleanup["status"] != "PASS_EXPERIMENTAL_MAIN_LV_RENDER_TASK_FREE_C":
        raise RuntimeError("LV render task cleanup status changed")
    base = file_from_receipt(cleanup, "base_object", "base_sha256")
    linked = file_from_receipt(cleanup, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_render_task_free_4848e8", "audio_uart_lv_draw_task_image_desc_489fc8"}
    resolved = {"audio_uart_lv_render_task_free_4848e8"}
    if base != previous or len(imports(base)) != 237 or len(imports(linked)) != 236 or \
            imports(base) - imports(linked) != resolved or imports(linked) - imports(base) or \
            set(cleanup["source_owned_symbols"]) != owned:
        raise RuntimeError("LV render task cleanup handoff changed")
    if sha(ROOT / cleanup["source"]) != cleanup["source_sha256"]:
        raise RuntimeError("stale LV render task cleanup source")
    records.append({
        "stage": "main-lv-render-task-free-4848e8",
        "binder": str(cleanup_script.relative_to(ROOT)),
        "binder_sha256": sha(cleanup_script), "status": cleanup["status"],
        "binder_output": cleanup_result.stdout.strip(),
        "receipt": str(cleanup_path.relative_to(ROOT)),
        "receipt_sha256": sha(cleanup_path),
        "source": cleanup["source"], "source_sha256": cleanup["source_sha256"],
        "source_owned_symbols": cleanup["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 237, "unresolved_after": 236,
        "imports_resolved": cleanup["imports_resolved"], "imports_added": [],
        "comparison_scope": "controlled generic, image and draw-buffer task cleanup",
    })
    previous = linked
    image_header_script = HERE / "bind_main_lv_image_header_488f6a_20261015.py"
    image_header_result = subprocess.run([sys.executable, str(image_header_script)], check=True,
                                         capture_output=True, text=True)
    image_header_path = G2 / "build/c-firmware/20261015/main-lv-image-header-488f6a/receipt.json"
    image_header = json.loads(image_header_path.read_text())
    if image_header["status"] != "PASS_EXPERIMENTAL_MAIN_LV_IMAGE_HEADER_C":
        raise RuntimeError("LV image header status changed")
    base = file_from_receipt(image_header, "base_object", "base_sha256")
    linked = file_from_receipt(image_header, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_image_header_488f6a"}
    if base != previous or len(imports(base)) != 236 or imports(base) != imports(linked) or \
            set(image_header["source_owned_symbols"]) != owned:
        raise RuntimeError("LV image header handoff changed")
    if sha(ROOT / image_header["source"]) != image_header["source_sha256"]:
        raise RuntimeError("stale LV image header source")
    records.append({
        "stage": "main-lv-image-header-488f6a",
        "binder": str(image_header_script.relative_to(ROOT)),
        "binder_sha256": sha(image_header_script), "status": image_header["status"],
        "binder_output": image_header_result.stdout.strip(),
        "receipt": str(image_header_path.relative_to(ROOT)),
        "receipt_sha256": sha(image_header_path),
        "source": image_header["source"], "source_sha256": image_header["source_sha256"],
        "source_owned_symbols": image_header["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 236, "unresolved_after": 236,
        "imports_resolved": [], "imports_added": [],
        "comparison_scope": "controlled 0x4c-byte image header request and decoder result",
    })
    previous = linked
    image_desc_script = HERE / "bind_main_lv_image_descriptor_init_489f5e_20261015.py"
    image_desc_result = subprocess.run([sys.executable, str(image_desc_script)], check=True,
                                       capture_output=True, text=True)
    image_desc_path = G2 / "build/c-firmware/20261015/main-lv-image-descriptor-init-489f5e/receipt.json"
    image_desc = json.loads(image_desc_path.read_text())
    if image_desc["status"] != "PASS_EXPERIMENTAL_MAIN_LV_IMAGE_DESCRIPTOR_INIT_C":
        raise RuntimeError("LV image descriptor status changed")
    base = file_from_receipt(image_desc, "base_object", "base_sha256")
    linked = file_from_receipt(image_desc, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_image_descriptor_init_489f5e", "audio_uart_lv_palette_table_716330",
             "audio_uart_page_488290"}
    resolved = {"audio_uart_page_488290"}
    if base != previous or len(imports(base)) != 236 or len(imports(linked)) != 235 or \
            imports(base) - imports(linked) != resolved or imports(linked) - imports(base) or \
            set(image_desc["source_owned_symbols"]) != owned:
        raise RuntimeError("LV image descriptor handoff changed")
    if sha(ROOT / image_desc["source"]) != image_desc["source_sha256"]:
        raise RuntimeError("stale LV image descriptor source")
    records.append({
        "stage": "main-lv-image-descriptor-init-489f5e",
        "binder": str(image_desc_script.relative_to(ROOT)),
        "binder_sha256": sha(image_desc_script), "status": image_desc["status"],
        "binder_output": image_desc_result.stdout.strip(),
        "receipt": str(image_desc_path.relative_to(ROOT)),
        "receipt_sha256": sha(image_desc_path),
        "source": image_desc["source"], "source_sha256": image_desc["source_sha256"],
        "source_owned_symbols": image_desc["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 236, "unresolved_after": 235,
        "imports_resolved": image_desc["imports_resolved"], "imports_added": [],
        "comparison_scope": "100-byte image descriptor and nineteen source-owned palette RGB triples",
    })
    previous = linked
    renderer_script = HERE / "bind_main_lv_draw_task_render_451c6e_20261015.py"
    renderer_result = subprocess.run([sys.executable, str(renderer_script)], check=True,
                                     capture_output=True, text=True)
    renderer_path = G2 / "build/c-firmware/20261015/main-lv-draw-task-render-451c6e/receipt.json"
    renderer = json.loads(renderer_path.read_text())
    if renderer["status"] != "PASS_EXPERIMENTAL_MAIN_LV_DRAW_TASK_RENDER_C":
        raise RuntimeError("LV renderer status changed")
    base = file_from_receipt(renderer, "base_object", "base_sha256")
    linked = file_from_receipt(renderer, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_draw_task_render_451c6e"}
    added = {"audio_uart_lv_area_transform_451082"}
    if base != previous or len(imports(base)) != 235 or len(imports(linked)) != 235 or \
            imports(base) - imports(linked) != owned or imports(linked) - imports(base) != added or \
            set(renderer["source_owned_symbols"]) != owned:
        raise RuntimeError("LV renderer handoff changed")
    if sha(ROOT / renderer["source"]) != renderer["source_sha256"]:
        raise RuntimeError("stale LV renderer source")
    records.append({
        "stage": "main-lv-draw-task-render-451c6e",
        "binder": str(renderer_script.relative_to(ROOT)),
        "binder_sha256": sha(renderer_script), "status": renderer["status"],
        "binder_output": renderer_result.stdout.strip(),
        "receipt": str(renderer_path.relative_to(ROOT)),
        "receipt_sha256": sha(renderer_path),
        "source": renderer["source"], "source_sha256": renderer["source_sha256"],
        "source_owned_symbols": renderer["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 235, "unresolved_after": 235,
        "imports_resolved": renderer["imports_resolved"],
        "imports_added": renderer["imports_added"],
        "comparison_scope": "five task branches, combined draw and allocation-failure logger entry",
    })
    previous = linked
    area_transform_script = HERE / "bind_main_lv_area_transform_451082_20261015.py"
    area_transform_result = subprocess.run([sys.executable, str(area_transform_script)], check=True,
                                           capture_output=True, text=True)
    area_transform_path = G2 / "build/c-firmware/20261015/main-lv-area-transform-451082/receipt.json"
    area_transform = json.loads(area_transform_path.read_text())
    if area_transform["status"] != "PASS_EXPERIMENTAL_MAIN_LV_AREA_TRANSFORM_C":
        raise RuntimeError("LV area transform status changed")
    base = file_from_receipt(area_transform, "base_object", "base_sha256")
    linked = file_from_receipt(area_transform, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_area_transform_451082"}
    if base != previous or len(imports(base)) != 235 or len(imports(linked)) != 234 or \
            imports(base) - imports(linked) != owned or imports(linked) - imports(base) or \
            set(area_transform["source_owned_symbols"]) != owned:
        raise RuntimeError("LV area transform handoff changed")
    if sha(ROOT / area_transform["source"]) != area_transform["source_sha256"]:
        raise RuntimeError("stale LV area transform source")
    records.append({
        "stage": "main-lv-area-transform-451082",
        "binder": str(area_transform_script.relative_to(ROOT)),
        "binder_sha256": sha(area_transform_script), "status": area_transform["status"],
        "binder_output": area_transform_result.stdout.strip(),
        "receipt": str(area_transform_path.relative_to(ROOT)),
        "receipt_sha256": sha(area_transform_path),
        "source": area_transform["source"], "source_sha256": area_transform["source_sha256"],
        "source_owned_symbols": area_transform["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 235, "unresolved_after": 234,
        "imports_resolved": area_transform["imports_resolved"], "imports_added": [],
        "comparison_scope": "all 256 alignment modes across three bounded geometries",
    })
    previous = linked
    state_apply_script = HERE / "bind_main_lv_obj_state_apply_43ebec_20261015.py"
    state_apply_result = subprocess.run([sys.executable, str(state_apply_script)], check=True,
                                        capture_output=True, text=True)
    state_apply_path = G2 / "build/c-firmware/20261015/main-lv-obj-state-apply-43ebec/receipt.json"
    state_apply = json.loads(state_apply_path.read_text())
    if state_apply["status"] != "PASS_EXPERIMENTAL_MAIN_LV_OBJ_STATE_APPLY_C":
        raise RuntimeError("LV state application status changed")
    base = file_from_receipt(state_apply, "base_object", "base_sha256")
    linked = file_from_receipt(state_apply, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_obj_state_apply_43ebec"}
    added = {"audio_uart_lv_state_transition_kind_44c178",
             "audio_uart_lv_style_reference_43dce0",
             "audio_uart_lv_state_property_refresh_44bfae"}
    if base != previous or len(imports(base)) != 234 or len(imports(linked)) != 236 or \
            imports(base) - imports(linked) != owned or imports(linked) - imports(base) != added or \
            set(state_apply["source_owned_symbols"]) != owned:
        raise RuntimeError("LV state application handoff changed")
    if sha(ROOT / state_apply["source"]) != state_apply["source_sha256"]:
        raise RuntimeError("stale LV state application source")
    records.append({
        "stage": "main-lv-obj-state-apply-43ebec",
        "binder": str(state_apply_script.relative_to(ROOT)),
        "binder_sha256": sha(state_apply_script), "status": state_apply["status"],
        "binder_output": state_apply_result.stdout.strip(),
        "receipt": str(state_apply_path.relative_to(ROOT)),
        "receipt_sha256": sha(state_apply_path),
        "source": state_apply["source"], "source_sha256": state_apply["source_sha256"],
        "source_owned_symbols": state_apply["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 234, "unresolved_after": 236,
        "imports_resolved": state_apply["imports_resolved"],
        "imports_added": state_apply["imports_added"],
        "comparison_scope": "controlled state mutation and bounded style records",
    })
    previous = linked
    style_ref_script = HERE / "bind_main_lv_style_reference_43dce0_20261015.py"
    style_ref_result = subprocess.run([sys.executable, str(style_ref_script)], check=True,
                                      capture_output=True, text=True)
    style_ref_path = G2 / "build/c-firmware/20261015/main-lv-style-reference-43dce0/receipt.json"
    style_ref = json.loads(style_ref_path.read_text())
    if style_ref["status"] != "PASS_EXPERIMENTAL_MAIN_LV_STYLE_REFERENCE_C":
        raise RuntimeError("LV style reference status changed")
    base = file_from_receipt(style_ref, "base_object", "base_sha256")
    linked = file_from_receipt(style_ref, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_style_reference_43dce0"}
    if base != previous or len(imports(base)) != 236 or len(imports(linked)) != 235 or \
            imports(base) - imports(linked) != owned or imports(linked) - imports(base) or \
            set(style_ref["source_owned_symbols"]) != owned:
        raise RuntimeError("LV style reference handoff changed")
    if sha(ROOT / style_ref["source"]) != style_ref["source_sha256"]:
        raise RuntimeError("stale LV style reference source")
    records.append({
        "stage": "main-lv-style-reference-43dce0",
        "binder": str(style_ref_script.relative_to(ROOT)),
        "binder_sha256": sha(style_ref_script), "status": style_ref["status"],
        "binder_output": style_ref_result.stdout.strip(),
        "receipt": str(style_ref_path.relative_to(ROOT)),
        "receipt_sha256": sha(style_ref_path),
        "source": style_ref["source"], "source_sha256": style_ref["source_sha256"],
        "source_owned_symbols": style_ref["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 236, "unresolved_after": 235,
        "imports_resolved": style_ref["imports_resolved"], "imports_added": [],
        "comparison_scope": "packed and sparse style property lookup",
    })
    previous = linked
    transition_kind_script = HERE / "bind_main_lv_state_transition_kind_44c178_20261015.py"
    transition_kind_result = subprocess.run([sys.executable, str(transition_kind_script)], check=True,
                                            capture_output=True, text=True)
    transition_kind_path = G2 / "build/c-firmware/20261015/main-lv-state-transition-kind-44c178/receipt.json"
    transition_kind = json.loads(transition_kind_path.read_text())
    if transition_kind["status"] != "PASS_EXPERIMENTAL_MAIN_LV_STATE_TRANSITION_KIND_C":
        raise RuntimeError("LV transition-kind status changed")
    base = file_from_receipt(transition_kind, "base_object", "base_sha256")
    linked = file_from_receipt(transition_kind, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_state_transition_kind_44c178"}
    if base != previous or len(imports(base)) != 235 or len(imports(linked)) != 234 or \
            imports(base) - imports(linked) != owned or imports(linked) - imports(base) or \
            set(transition_kind["source_owned_symbols"]) != owned:
        raise RuntimeError("LV transition-kind handoff changed")
    if sha(ROOT / transition_kind["source"]) != transition_kind["source_sha256"]:
        raise RuntimeError("stale LV transition-kind source")
    records.append({
        "stage": "main-lv-state-transition-kind-44c178",
        "binder": str(transition_kind_script.relative_to(ROOT)),
        "binder_sha256": sha(transition_kind_script), "status": transition_kind["status"],
        "binder_output": transition_kind_result.stdout.strip(),
        "receipt": str(transition_kind_path.relative_to(ROOT)),
        "receipt_sha256": sha(transition_kind_path),
        "source": transition_kind["source"], "source_sha256": transition_kind["source_sha256"],
        "source_owned_symbols": transition_kind["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 235, "unresolved_after": 234,
        "imports_resolved": transition_kind["imports_resolved"], "imports_added": [],
        "comparison_scope": "geometry/layout priority scan with controlled style lookup",
    })
    previous = linked
    transition_style_script = HERE / "bind_main_lv_transition_style_44c72c_20261015.py"
    transition_style_result = subprocess.run([sys.executable, str(transition_style_script)], check=True,
                                         capture_output=True, text=True)
    transition_style_path = G2 / "build/c-firmware/20261015/main-lv-transition-style-44c72c/receipt.json"
    transition_style = json.loads(transition_style_path.read_text())
    if transition_style["status"] != "PASS_EXPERIMENTAL_MAIN_LV_TRANSITION_STYLE_C":
        raise RuntimeError("LV transition style status changed")
    base = file_from_receipt(transition_style, "base_object", "base_sha256")
    linked = file_from_receipt(transition_style, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_transition_style_44c72c"}
    if base != previous or len(imports(base)) != 234 or len(imports(linked)) != 234 or \
            imports(base) != imports(linked) or set(transition_style["source_owned_symbols"]) != owned:
        raise RuntimeError("LV transition style handoff changed")
    if sha(ROOT / transition_style["source"]) != transition_style["source_sha256"]:
        raise RuntimeError("stale LV transition style source")
    records.append({
        "stage": "main-lv-transition-style-44c72c",
        "binder": str(transition_style_script.relative_to(ROOT)),
        "binder_sha256": sha(transition_style_script), "status": transition_style["status"],
        "binder_output": transition_style_result.stdout.strip(),
        "receipt": str(transition_style_path.relative_to(ROOT)),
        "receipt_sha256": sha(transition_style_path),
        "source": transition_style["source"], "source_sha256": transition_style["source_sha256"],
        "source_owned_symbols": transition_style["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 234, "unresolved_after": 234,
        "imports_resolved": [], "imports_added": [],
        "comparison_scope": "five existing transition-style lookups and three controlled insertions",
    })
    previous = linked
    state_property_script = HERE / "bind_main_lv_state_property_refresh_44bfae_20261015.py"
    state_property_result = subprocess.run([sys.executable, str(state_property_script)], check=True,
                                           capture_output=True, text=True)
    state_property_path = G2 / "build/c-firmware/20261015/main-lv-state-property-refresh-44bfae/receipt.json"
    state_property = json.loads(state_property_path.read_text())
    if state_property["status"] != "PASS_EXPERIMENTAL_MAIN_LV_STATE_PROPERTY_REFRESH_C":
        raise RuntimeError("LV state-property refresh status changed")
    base = file_from_receipt(state_property, "base_object", "base_sha256")
    linked = file_from_receipt(state_property, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_state_property_refresh_44bfae"}
    callbacks = {"audio_uart_lv_transition_exec_44cae0",
                 "audio_uart_lv_transition_ready_44cc8c",
                 "audio_uart_lv_transition_delete_44ccd8"}
    if base != previous or len(imports(base)) != 234 or len(imports(linked)) != 236 or \
            imports(base) - imports(linked) != owned or \
            imports(linked) - imports(base) != callbacks or \
            set(state_property["source_owned_symbols"]) != owned:
        raise RuntimeError("LV state-property refresh handoff changed")
    if sha(ROOT / state_property["source"]) != state_property["source_sha256"]:
        raise RuntimeError("stale LV state-property refresh source")
    records.append({
        "stage": "main-lv-state-property-refresh-44bfae",
        "binder": str(state_property_script.relative_to(ROOT)),
        "binder_sha256": sha(state_property_script), "status": state_property["status"],
        "binder_output": state_property_result.stdout.strip(),
        "receipt": str(state_property_path.relative_to(ROOT)),
        "receipt_sha256": sha(state_property_path),
        "source": state_property["source"], "source_sha256": state_property["source_sha256"],
        "source_owned_symbols": state_property["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 234, "unresolved_after": 236,
        "imports_resolved": state_property["imports_resolved"],
        "imports_added": state_property["imports_added"],
        "comparison_scope": "six controlled style-refresh and animation-descriptor cases",
    })
    previous = linked
    transition_ready_script = HERE / "bind_main_lv_transition_ready_44cc8c_20261015.py"
    transition_ready_result = subprocess.run([sys.executable, str(transition_ready_script)], check=True,
                                            capture_output=True, text=True)
    transition_ready_path = G2 / "build/c-firmware/20261015/main-lv-transition-ready-44cc8c/receipt.json"
    transition_ready = json.loads(transition_ready_path.read_text())
    if transition_ready["status"] != "PASS_EXPERIMENTAL_MAIN_LV_TRANSITION_READY_C":
        raise RuntimeError("LV transition-ready status changed")
    base = file_from_receipt(transition_ready, "base_object", "base_sha256")
    linked = file_from_receipt(transition_ready, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_transition_ready_44cc8c"}
    if base != previous or len(imports(base)) != 236 or len(imports(linked)) != 235 or \
            imports(base) - imports(linked) != owned or imports(linked) - imports(base) or \
            set(transition_ready["source_owned_symbols"]) != owned:
        raise RuntimeError("LV transition-ready handoff changed")
    if sha(ROOT / transition_ready["source"]) != transition_ready["source_sha256"]:
        raise RuntimeError("stale LV transition-ready source")
    records.append({
        "stage": "main-lv-transition-ready-44cc8c",
        "binder": str(transition_ready_script.relative_to(ROOT)),
        "binder_sha256": sha(transition_ready_script), "status": transition_ready["status"],
        "binder_output": transition_ready_result.stdout.strip(),
        "receipt": str(transition_ready_path.relative_to(ROOT)),
        "receipt_sha256": sha(transition_ready_path),
        "source": transition_ready["source"], "source_sha256": transition_ready["source_sha256"],
        "source_owned_symbols": transition_ready["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 236, "unresolved_after": 235,
        "imports_resolved": transition_ready["imports_resolved"], "imports_added": [],
        "comparison_scope": "four controlled callback sequences",
    })
    previous = linked
    transition_delete_script = HERE / "bind_main_lv_transition_delete_44ccd8_20261015.py"
    transition_delete_result = subprocess.run([sys.executable, str(transition_delete_script)], check=True,
                                             capture_output=True, text=True)
    transition_delete_path = G2 / "build/c-firmware/20261015/main-lv-transition-delete-44ccd8/receipt.json"
    transition_delete = json.loads(transition_delete_path.read_text())
    if transition_delete["status"] != "PASS_EXPERIMENTAL_MAIN_LV_TRANSITION_DELETE_C":
        raise RuntimeError("LV transition-delete status changed")
    base = file_from_receipt(transition_delete, "base_object", "base_sha256")
    linked = file_from_receipt(transition_delete, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_transition_delete_44ccd8"}
    if base != previous or len(imports(base)) != 235 or len(imports(linked)) != 234 or \
            imports(base) - imports(linked) != owned or imports(linked) - imports(base) or \
            set(transition_delete["source_owned_symbols"]) != owned:
        raise RuntimeError("LV transition-delete handoff changed")
    if sha(ROOT / transition_delete["source"]) != transition_delete["source_sha256"]:
        raise RuntimeError("stale LV transition-delete source")
    records.append({
        "stage": "main-lv-transition-delete-44ccd8",
        "binder": str(transition_delete_script.relative_to(ROOT)),
        "binder_sha256": sha(transition_delete_script), "status": transition_delete["status"],
        "binder_output": transition_delete_result.stdout.strip(),
        "receipt": str(transition_delete_path.relative_to(ROOT)),
        "receipt_sha256": sha(transition_delete_path),
        "source": transition_delete["source"], "source_sha256": transition_delete["source_sha256"],
        "source_owned_symbols": transition_delete["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 235, "unresolved_after": 234,
        "imports_resolved": transition_delete["imports_resolved"], "imports_added": [],
        "comparison_scope": "four controlled duplicate/overlay/deallocation branches",
    })
    previous = linked
    transition_exec_script = HERE / "bind_main_lv_transition_exec_44cae0_20261015.py"
    transition_exec_result = subprocess.run([sys.executable, str(transition_exec_script)], check=True,
                                           capture_output=True, text=True)
    transition_exec_path = G2 / "build/c-firmware/20261015/main-lv-transition-exec-44cae0/receipt.json"
    transition_exec = json.loads(transition_exec_path.read_text())
    if transition_exec["status"] != "PASS_EXPERIMENTAL_MAIN_LV_TRANSITION_EXEC_C":
        raise RuntimeError("LV transition-exec status changed")
    base = file_from_receipt(transition_exec, "base_object", "base_sha256")
    linked = file_from_receipt(transition_exec, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_transition_exec_44cae0"}
    if base != previous or len(imports(base)) != 234 or len(imports(linked)) != 233 or \
            imports(base) - imports(linked) != owned or imports(linked) - imports(base) or \
            set(transition_exec["source_owned_symbols"]) != owned:
        raise RuntimeError("LV transition-exec handoff changed")
    if sha(ROOT / transition_exec["source"]) != transition_exec["source_sha256"]:
        raise RuntimeError("stale LV transition-exec source")
    records.append({
        "stage": "main-lv-transition-exec-44cae0",
        "binder": str(transition_exec_script.relative_to(ROOT)),
        "binder_sha256": sha(transition_exec_script), "status": transition_exec["status"],
        "binder_output": transition_exec_result.stdout.strip(),
        "receipt": str(transition_exec_path.relative_to(ROOT)),
        "receipt_sha256": sha(transition_exec_path),
        "source": transition_exec["source"], "source_sha256": transition_exec["source_sha256"],
        "source_owned_symbols": transition_exec["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 234, "unresolved_after": 233,
        "imports_resolved": transition_exec["imports_resolved"], "imports_added": [],
        "comparison_scope": "twenty-four controlled color, threshold, and numeric interpolation cases",
    })
    previous = linked
    scroll_view_script = HERE / "bind_main_lv_scroll_view_step_44f40c_20261015.py"
    scroll_view_result = subprocess.run([sys.executable, str(scroll_view_script)], check=True,
                                        capture_output=True, text=True)
    scroll_view_path = G2 / "build/c-firmware/20261015/main-lv-scroll-view-step-44f40c/receipt.json"
    scroll_view = json.loads(scroll_view_path.read_text())
    if scroll_view["status"] != "PASS_EXPERIMENTAL_MAIN_LV_SCROLL_VIEW_STEP_C":
        raise RuntimeError("LV scroll-view step status changed")
    base = file_from_receipt(scroll_view, "base_object", "base_sha256")
    linked = file_from_receipt(scroll_view, "linked_object", "linked_sha256")
    owned = {"audio_uart_lv_scroll_view_step_44f40c"}
    if base != previous or len(imports(base)) != 233 or len(imports(linked)) != 232 or \
            imports(base) - imports(linked) != owned or imports(linked) - imports(base) or \
            set(scroll_view["source_owned_symbols"]) != owned:
        raise RuntimeError("LV scroll-view step handoff changed")
    if sha(ROOT / scroll_view["source"]) != scroll_view["source_sha256"]:
        raise RuntimeError("stale LV scroll-view step source")
    records.append({
        "stage": "main-lv-scroll-view-step-44f40c",
        "binder": str(scroll_view_script.relative_to(ROOT)),
        "binder_sha256": sha(scroll_view_script), "status": scroll_view["status"],
        "binder_output": scroll_view_result.stdout.strip(),
        "receipt": str(scroll_view_path.relative_to(ROOT)),
        "receipt_sha256": sha(scroll_view_path),
        "source": scroll_view["source"], "source_sha256": scroll_view["source_sha256"],
        "source_owned_symbols": scroll_view["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 233, "unresolved_after": 232,
        "imports_resolved": scroll_view["imports_resolved"], "imports_added": [],
        "comparison_scope": "twenty-three controlled scroll alignment and direction cases",
    })
    previous = linked
    nema_alias_script = HERE / "bind_main_graphics_nema_alias_513924_20261015.py"
    nema_alias_result = subprocess.run([sys.executable, str(nema_alias_script)], check=True,
                                       capture_output=True, text=True)
    nema_alias_path = G2 / "build/c-firmware/20261015/main-graphics-nema-alias-513924/receipt.json"
    nema_alias = json.loads(nema_alias_path.read_text())
    if nema_alias["status"] != "PASS_EXPERIMENTAL_MAIN_GRAPHICS_NEMA_ALIAS_C":
        raise RuntimeError("Main Nema call-name status changed")
    base = file_from_receipt(nema_alias, "base_object", "base_sha256")
    linked = file_from_receipt(nema_alias, "linked_object", "linked_sha256")
    owned = {"audio_uart_display_graphics_blend_513924"}
    if base != previous or len(imports(base)) != 232 or len(imports(linked)) != 231 or \
            imports(base) - imports(linked) != owned or imports(linked) - imports(base) or \
            set(nema_alias["source_owned_symbols"]) != owned:
        raise RuntimeError("Main Nema call-name handoff changed")
    if sha(ROOT / nema_alias["source"]) != nema_alias["source_sha256"]:
        raise RuntimeError("stale Main Nema call-name source")
    records.append({
        "stage": "main-graphics-nema-alias-513924",
        "binder": str(nema_alias_script.relative_to(ROOT)),
        "binder_sha256": sha(nema_alias_script), "status": nema_alias["status"],
        "binder_output": nema_alias_result.stdout.strip(),
        "receipt": str(nema_alias_path.relative_to(ROOT)),
        "receipt_sha256": sha(nema_alias_path),
        "source": nema_alias["source"], "source_sha256": nema_alias["source_sha256"],
        "source_owned_symbols": nema_alias["source_owned_symbols"],
        "base_object": str(base.relative_to(ROOT)), "base_sha256": sha(base),
        "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
        "unresolved_before": 232, "unresolved_after": 231,
        "imports_resolved": nema_alias["imports_resolved"], "imports_added": [],
        "comparison_scope": "call-name forwarding to Nema encoder with 2420 native cases",
    })
    previous = linked
    OUT.mkdir(parents=True, exist_ok=True)
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_POST_TAIL_C_REPLAY",
        "tail_receipt": str(TAIL.relative_to(ROOT)), "tail_receipt_sha256": sha(TAIL),
        "stages": records,
        "linked_object": str(previous.relative_to(ROOT)), "linked_object_sha256": sha(previous),
        "unresolved_before": 367, "unresolved_after": len(imports(previous)),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["This replays one hundred ninety-two bounded C source/data stages after the corrected Main archive; 231 imports remain. The LV renderer, all-mode area alignment, bounded object state application, packed/sparse style lookup, transition-kind priority scan, transition-style lookup and controlled insertion, per-property state refresh, all three transition callbacks, scroll-to-view step, and Nema graphics-mode call name are C-bound; the Nema encoder has 2420 native comparisons. Transition-style allocation failure remains open; live image decoder, display dispatch, allocation fatal loop, full page layout, final stock placement and hardware behavior remain open.",
                   "Native RAM initializers, full-image layout and hardware behavior remain open."],
    }
    if receipt["unresolved_after"] != 231:
        raise RuntimeError("Main post-tail C replay count changed")
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(records), 367, receipt["unresolved_after"], sha(path))


if __name__ == "__main__":
    main()
