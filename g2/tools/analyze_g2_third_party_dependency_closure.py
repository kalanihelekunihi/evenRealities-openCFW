#!/usr/bin/env python3
"""Aggregate the authenticated G2 third-party dependency closure ledger."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tools/manifests/g2-third-party-dependency-closure.json"
EXPECTED_FAMILIES = {
    "FreeRTOS-Kernel", "CMSIS-FreeRTOS", "CMSIS-Core", "AmbiqSuite-Apollo510",
    "AmbiqSuite-ANCC-profile", "AmbiqSuite-AMOTA-profile",
    "NemaGFX-NemaVG-Ambiq-GPU-patch", "FreeType", "littlefs", "TLSF", "LZ4",
    "nanopb", "FlashDB", "EasyLogger", "FreeRTOS-Plus-CLI", "mpaland-printf",
    "TinyFrame", "CmBacktrace", "AndersKaloer-Ring-Buffer", "LVGL",
    "Packetcraft-Cordio", "Goodix-GR551x-app-error", "Nordic-nPMX",
    "Google-liblc3", "IAR-DLIB", "DaveGamble-cJSON",
}
ALLOWED_STATUS = {"closed", "bounded_waiting_external_gate"}


class ClosureError(RuntimeError):
    pass


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ClosureError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def analyze(corpus: Path, plan: Path, component_report: Path) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text())
    rows = manifest["dependencies"]
    families = {row["family"] for row in rows}
    if len(rows) != len(families) or families != EXPECTED_FAMILIES:
        raise ClosureError("dependency-family census changed")
    for row in rows:
        if row["functional_status"] not in ALLOWED_STATUS:
            raise ClosureError(f"open local functional gap recorded for {row['family']}")
        if not row["origin"] or not row["version"]:
            raise ClosureError(f"origin/version missing for {row['family']}")
        if row["functional_status"] == "bounded_waiting_external_gate" and not row["residual_gates"]:
            raise ClosureError(f"external gate missing for {row['family']}")
        for evidence in row["evidence"]:
            path = ROOT / evidence
            if not path.is_file():
                raise ClosureError(f"evidence missing for {row['family']}: {evidence}")

    cordio = _load(ROOT / "tools/analyze_g2_cordio_closure.py", "third_party_cordio_closure").analyze(corpus)
    ancc = _load(ROOT / "tools/analyze_g2_ambiqsuite_ancc_profile.py", "third_party_ambiqsuite_ancc_profile").analyze()
    amota = _load(ROOT / "tools/analyze_g2_ble_ota_ring_profiles.py", "third_party_ambiqsuite_amota_profile").analyze()
    product_rtos = _load(
        ROOT / "tools/analyze_g2_product_rtos.py", "third_party_ambiqsuite_product_rtos"
    ).analyze()
    gx8002b = _load(
        ROOT / "tools/analyze_g2_drv_gx8002b.py", "third_party_ambiqsuite_gx8002b"
    ).analyze()
    pdm_production = _load(
        ROOT / "tools/analyze_g2_drv_pdm_production.py",
        "third_party_ambiqsuite_pdm_production",
    ).analyze()
    pdm = _load(
        ROOT / "tools/analyze_g2_drv_pdm.py", "third_party_ambiqsuite_pdm"
    ).analyze()
    service_ancc = _load(
        ROOT / "tools/analyze_g2_service_ancc.py", "third_party_service_ancc_boundary"
    ).analyze()
    als = _load(ROOT / "tools/analyze_g2_als.py", "third_party_als_boundary").analyze()
    thread_ble_production = _load(
        ROOT / "tools/analyze_g2_thread_ble_production.py",
        "third_party_thread_ble_production_boundary",
    ).analyze()
    pt_protocol = _load(
        ROOT / "tools/analyze_g2_pt_protocol.py",
        "third_party_pt_protocol_boundary",
    ).analyze()
    ui_quicklist_page = _load(
        ROOT / "tools/analyze_g2_ui_quicklist_page.py",
        "third_party_ui_quicklist_page_boundary",
    ).analyze()
    ui_widget_news_page = _load(
        ROOT / "tools/analyze_g2_ui_widget_news_page.py",
        "third_party_ui_widget_news_page_boundary",
    ).analyze()
    ui_stock_page = _load(
        ROOT / "tools/analyze_g2_ui_stock_page.py",
        "third_party_ui_stock_page_boundary",
    ).analyze()
    navigation_ui = _load(
        ROOT / "tools/analyze_g2_navigation_ui.py",
        "third_party_navigation_ui_boundary",
    ).analyze()
    menu_page = _load(
        ROOT / "tools/analyze_g2_menu_page.py",
        "third_party_menu_page_boundary",
    ).analyze()
    ui_health_page = _load(
        ROOT / "tools/analyze_g2_ui_health_page.py",
        "third_party_ui_health_page_boundary",
    ).analyze()
    ring_service = _load(
        ROOT / "tools/analyze_g2_ring_service.py",
        "third_party_ring_service_boundary",
    ).analyze()
    service_input_manager = _load(
        ROOT / "tools/analyze_g2_service_input_manager.py",
        "third_party_service_input_manager_boundary",
    ).analyze()
    ui_calendar_page = _load(
        ROOT / "tools/analyze_g2_ui_calendar_page.py",
        "third_party_ui_calendar_page_boundary",
    ).analyze()
    ota_transport = _load(
        ROOT / "tools/analyze_g2_ota_transport.py",
        "third_party_ota_transport_boundary",
    ).analyze()
    efs_transport = _load(
        ROOT / "tools/analyze_g2_efs_transport.py",
        "third_party_efs_transport_boundary",
    ).analyze()
    evenhub_loading_page = _load(
        ROOT / "tools/analyze_g2_evenhub_loading_page.py",
        "third_party_evenhub_loading_page_boundary",
    ).analyze()
    dashboard_watchface_layout1 = _load(
        ROOT / "tools/analyze_g2_dashboard_watchface_layout1.py",
        "third_party_dashboard_watchface_layout1_boundary",
    ).analyze()
    teleprompt_fsm = _load(
        ROOT / "tools/analyze_g2_teleprompt_fsm.py",
        "third_party_teleprompt_fsm_boundary",
    ).analyze()
    health_data_manager = _load(
        ROOT / "tools/analyze_g2_health_data_manager.py",
        "third_party_health_data_manager_boundary",
    ).analyze()
    evenhub_main = _load(
        ROOT / "tools/analyze_g2_evenhub_main.py",
        "third_party_evenhub_main_boundary",
    ).analyze()
    translate = _load(
        ROOT / "tools/analyze_g2_translate.py",
        "third_party_translate_boundary",
    ).analyze()
    teleprompt_controller = _load(
        ROOT / "tools/analyze_g2_teleprompt_controller.py",
        "third_party_teleprompt_controller_boundary",
    ).analyze()
    conversate_comm_data = _load(
        ROOT / "tools/analyze_g2_conversate_comm_data.py",
        "third_party_conversate_comm_data_boundary",
    ).analyze()
    conversate_controller = _load(
        ROOT / "tools/analyze_g2_conversate_controller.py",
        "third_party_conversate_controller_boundary",
    ).analyze()
    conversate_ui_main_page = _load(
        ROOT / "tools/analyze_g2_conversate_ui_main_page.py",
        "third_party_conversate_ui_main_page_boundary",
    ).analyze()
    service_universal_setting = _load(
        ROOT / "tools/analyze_g2_service_universal_setting.py",
        "third_party_service_universal_setting_boundary",
    ).analyze()
    common_image_container = _load(
        ROOT / "tools/analyze_g2_common_image_container.py",
        "third_party_common_image_container_boundary",
    ).analyze()
    dashboard_watchface_layout2 = _load(
        ROOT / "tools/analyze_g2_dashboard_watchface_layout2.py",
        "third_party_dashboard_watchface_layout2_boundary",
    ).analyze()
    dashboard_watchface_layout3 = _load(
        ROOT / "tools/analyze_g2_dashboard_watchface_layout3.py",
        "third_party_dashboard_watchface_layout3_boundary",
    ).analyze()
    thread_ring = _load(
        ROOT / "tools/analyze_g2_thread_ring.py",
        "third_party_thread_ring_boundary",
    ).analyze()
    sensor_hub = _load(
        ROOT / "tools/analyze_g2_sensor_hub.py",
        "third_party_sensor_hub_boundary",
    ).analyze()
    fw_event_loop = _load(
        ROOT / "tools/analyze_g2_fw_event_loop.py",
        "third_party_fw_event_loop_boundary",
    ).analyze()
    ring_connect_policy = _load(
        ROOT / "tools/analyze_g2_ring_connect_policy.py",
        "third_party_ring_connect_policy_boundary",
    ).analyze()
    system_close = _load(
        ROOT / "tools/analyze_g2_system_close.py",
        "third_party_system_close_boundary",
    ).analyze()
    iar_float_exponent = _load(
        ROOT / "tools/analyze_g2_iar_float_exponent.py",
        "third_party_iar_float_exponent_boundary",
    ).analyze()
    translate_ui = _load(
        ROOT / "tools/analyze_g2_translate_ui.py",
        "third_party_translate_ui_boundary",
    ).analyze()
    service_db_api = _load(
        ROOT / "tools/analyze_g2_service_db_api.py", "third_party_flashdb_service_db_api"
    ).analyze()
    ui_even_ai = _load(
        ROOT / "tools/analyze_g2_ui_even_ai.py", "third_party_lvgl_ui_even_ai"
    ).analyze()
    service_time = _load(
        ROOT / "tools/analyze_g2_service_time.py", "third_party_time_service_boundary"
    ).analyze()
    thread_audio = _load(
        ROOT / "tools/analyze_g2_thread_audio.py", "third_party_audio_thread_boundary"
    ).analyze()
    compress_log_core = _load(
        ROOT / "tools/analyze_g2_compress_log_core.py", "third_party_compress_log_core_boundary"
    ).analyze()
    compress_log_port = _load(
        ROOT / "tools/analyze_g2_compress_log_port.py", "third_party_compress_log_port_boundary"
    ).analyze()
    file_runtime = _load(
        ROOT / "tools/analyze_g2_file_runtime.py", "third_party_file_runtime_boundary"
    ).analyze()
    service_algo = _load(
        ROOT / "tools/analyze_g2_service_algo.py", "third_party_audio_service_algo_boundary"
    ).analyze()
    uart_sync = _load(
        ROOT / "tools/analyze_g2_uart_sync.py", "third_party_uart_sync_boundary"
    ).analyze()
    service_nvdb = _load(
        ROOT / "tools/analyze_g2_service_nvdb.py", "third_party_factory_nvdb_boundary"
    ).analyze()
    production_mic = _load(
        ROOT / "tools/analyze_g2_production_mic.py", "third_party_production_mic_boundary"
    ).analyze()
    service_audio_manager = _load(
        ROOT / "tools/analyze_g2_service_audio_manager.py",
        "third_party_service_audio_manager_boundary",
    ).analyze()
    service_kvdb = _load(
        ROOT / "tools/analyze_g2_service_kvdb.py",
        "third_party_system_kvdb_boundary",
    ).analyze()
    ux_battery_sync = _load(
        ROOT / "tools/analyze_g2_ux_battery_sync.py",
        "third_party_ux_battery_sync_boundary",
    ).analyze()
    cb_ring_battery = _load(
        ROOT / "tools/analyze_g2_cb_ring_battery.py",
        "third_party_cb_ring_battery_boundary",
    ).analyze()
    callback_facades = _load(
        ROOT / "tools/analyze_g2_callback_facades.py",
        "third_party_callback_facade_boundaries",
    ).analyze()
    callback_manager = _load(
        ROOT / "tools/analyze_g2_callback_manager.py",
        "third_party_callback_manager_boundary",
    ).analyze()
    silent_mode = _load(
        ROOT / "tools/analyze_g2_silent_mode.py",
        "third_party_silent_mode_boundary",
    ).analyze()
    onboarding_data_manager = _load(
        ROOT / "tools/analyze_g2_onboarding_data_manager.py",
        "third_party_onboarding_data_manager_boundary",
    ).analyze()
    onboarding_controller = _load(
        ROOT / "tools/analyze_g2_onboarding_controller.py",
        "third_party_onboarding_controller_boundary",
    ).analyze()
    onboarding_main_page = _load(
        ROOT / "tools/analyze_g2_onboarding_main_page.py",
        "third_party_onboarding_main_page_boundary",
    ).analyze()
    onboarding_stock_page = _load(
        ROOT / "tools/analyze_g2_onboarding_stock_page.py",
        "third_party_onboarding_stock_page_boundary",
    ).analyze()
    onboarding_news_page = _load(
        ROOT / "tools/analyze_g2_onboarding_news_page.py",
        "third_party_onboarding_news_page_boundary",
    ).analyze()
    lvgl_font_manager = _load(
        ROOT / "tools/analyze_g2_lvgl_font_manager.py",
        "third_party_lvgl_font_manager_boundary",
    ).analyze()
    common_list_container = _load(
        ROOT / "tools/analyze_g2_common_list_container.py",
        "third_party_common_list_container_boundary",
    ).analyze()
    common_text_container = _load(
        ROOT / "tools/analyze_g2_common_text_container.py",
        "third_party_common_text_container_boundary",
    ).analyze()
    evenhub_ui = _load(
        ROOT / "tools/analyze_g2_evenhub_ui.py",
        "third_party_evenhub_ui_boundary",
    ).analyze()
    evenhub_data_parser = _load(
        ROOT / "tools/analyze_g2_evenhub_data_parser.py",
        "third_party_evenhub_data_parser_boundary",
    ).analyze()
    sync_framework = _load(
        ROOT / "tools/analyze_g2_sync_framework.py",
        "third_party_sync_framework_boundary",
    ).analyze()
    sync_interface_api = _load(
        ROOT / "tools/analyze_g2_sync_interface_api.py",
        "third_party_sync_interface_api_boundary",
    ).analyze()
    display_thread = _load(
        ROOT / "tools/analyze_g2_display_thread.py",
        "third_party_display_thread_boundary",
    ).analyze()
    drv_mx25 = _load(
        ROOT / "tools/analyze_g2_drv_mx25u25643g.py",
        "third_party_drv_mx25_boundary",
    ).analyze()
    ui_msg_notif_list = _load(
        ROOT / "tools/analyze_g2_ui_msg_notif_list.py",
        "third_party_ui_msg_notif_list_boundary",
    ).analyze()
    dashboard_main = _load(
        ROOT / "tools/analyze_g2_dashboard_main_screen.py",
        "third_party_dashboard_main_boundary",
    ).analyze()
    teleprompt_ui = _load(
        ROOT / "tools/analyze_g2_teleprompt_ui.py",
        "third_party_teleprompt_ui_boundary",
    ).analyze()
    service_em9305_dfu = _load(
        ROOT / "tools/analyze_g2_service_em9305_dfu.py",
        "third_party_service_em9305_dfu_boundary",
    ).analyze()
    conversate_tag_data = _load(
        ROOT / "tools/analyze_g2_conversate_tag_data.py",
        "third_party_conversate_tag_data_boundary",
    ).analyze()
    dashboard_layout4 = _load(
        ROOT / "tools/analyze_g2_dashboard_watchface_layout4.py",
        "third_party_dashboard_watchface_layout4_boundary",
    ).analyze()
    dashboard_ext = _load(
        ROOT / "tools/analyze_g2_dashboard_ext.py",
        "third_party_dashboard_ext_boundary",
    ).analyze()
    dashboard_data_process = _load(
        ROOT / "tools/analyze_g2_dashboard_data_process.py",
        "third_party_dashboard_data_process_boundary",
    ).analyze()
    displaydrv_manager = _load(
        ROOT / "tools/analyze_g2_displaydrv_manager.py",
        "third_party_displaydrv_manager_boundary",
    ).analyze()
    npmx_main_driver = _load(
        ROOT / "tools/analyze_g2_npmx_main_driver.py",
        "third_party_npmx_main_driver_boundary",
    ).analyze()
    liblc3 = _load(
        ROOT / "tools/analyze_g2_liblc3.py",
        "third_party_liblc3_boundary",
    ).analyze()
    service_audio = _load(
        ROOT / "tools/analyze_g2_service_audio.py",
        "third_party_liblc3_service_audio_consumer",
    ).analyze()
    util_error = _load(
        ROOT / "tools/analyze_g2_util_error_check.py", "third_party_goodix_util_error"
    ).analyze()
    display = _load(ROOT / "tools/analyze_g2_lvgl_display_port_closure.py", "third_party_lvgl_display_closure").analyze(
        _load(ROOT / "tools/analyze_apollo_embedded_source_paths.py", "third_party_paths_for_image").DEFAULT_IMAGE,
        component_report,
        corpus,
    )
    accounting = _load(ROOT / "tools/analyze_g2_apollo_origin_accounting.py", "third_party_origin_accounting").analyze(
        plan, component_report, corpus
    )
    freetype_module = _load(ROOT / "tools/freetype_g2_config_audit.py", "third_party_freetype_config")
    freetype = freetype_module.authenticate(freetype_module.Image(freetype_module.DEFAULT_IMAGE))

    if cordio["retained_path_census"]["unclassified_reusable_paths"] != 0:
        raise ClosureError("Cordio retained reusable path gap reopened")
    if cordio["copied_profile_source_admission"]["source_owned_functions"] != 6:
        raise ClosureError("Cordio copied GATT-profile source closure changed")
    app_framework = cordio["ambiq_application_framework_source_admission"]
    if not app_framework["source_identification_closed"] or app_framework["retained_paths"] != 9:
        raise ClosureError("AmbiqSuite Cordio application-framework lineage changed")
    if app_framework["anchored_functions"] != 50 or app_framework["anchored_body_bytes"] != 29110:
        raise ClosureError("AmbiqSuite Cordio application-framework stock boundary changed")
    if app_framework["exact_source_text_identity"] or app_framework["historical_g2_generating_commit"] is not None:
        raise ClosureError("AmbiqSuite Cordio application-framework provenance overclaim")
    if ancc["surface"]["source_derived_stock_functions"] != 12:
        raise ClosureError("AmbiqSuite copied ANCC-profile source closure changed")
    if amota["aggregate"]["ambiq_skeleton_derived_stock_functions"] != 4:
        raise ClosureError("AmbiqSuite-derived AMOTA-profile closure changed")
    ambiq_rtos = product_rtos["provider_boundary"]["ambiq_hal"]
    if (
        ambiq_rtos["selected_source_equivalent_version"] != "5.1.0"
        or ambiq_rtos["stock_sleep_wfi_count"] != 2
        or ambiq_rtos["sdk_5_0_sleep_wfi_count"] != 1
        or ambiq_rtos["sdk_5_1_sleep_wfi_count"] != 2
        or not ambiq_rtos["build_predates_public_import"]
        or ambiq_rtos["exact_private_pre_release_commit"] is not None
    ):
        raise ClosureError("Apollo510 HAL 5.1.0-lineage discriminator changed")
    gx_provider = gx8002b["provider_boundary"]
    if (
        gx_provider["cmsis_core_linked_definitions"] != 3
        or gx_provider["ambiqsuite_i2s_calls"] != 13
        or len(gx_provider["ambiqsuite_i2s_apis"]) != 12
        or gx_provider["ambiqsuite_public_commit"] != "5efc0228528a8adce5eae0d226fac85d2551eb3b"
        or gx_provider["private_generating_commit_recoverable"]
        or gx8002b["identity"]["nationalchip_lvp_code_linked"]
    ):
        raise ClosureError("GX8002B AmbiqSuite/CMSIS provider boundary changed")
    pdm_provider = pdm_production["provider_boundary"]
    if (
        pdm_provider["ambiqsuite_pdm_calls"] != 13
        or pdm_provider["ambiqsuite_pdm_apis"] != 12
        or pdm_provider["ambiqsuite_selected_commit"]
        != "5efc0228528a8adce5eae0d226fac85d2551eb3b"
        or pdm_provider["ambiqsuite_source_git_blob"]
        != "23a440bfd6121509b0586f0afe1990fcf59dd8fb"
        or len(pdm_production["identity"]["embedded_third_party_definitions"]) != 3
        or pdm_production["production"]["production_routed"]
    ):
        raise ClosureError("PDM production AmbiqSuite/CMSIS provider boundary changed")
    pdm_provider = pdm["provider_boundary"]
    if (
        pdm_provider["ambiqsuite_pdm_calls"] != 19
        or pdm_provider["ambiqsuite_pdm_apis"] != 14
        or pdm_provider["ambiqsuite_selected_commit"] != "5efc0228528a8adce5eae0d226fac85d2551eb3b"
        or pdm_provider["ambiqsuite_source_git_blob"] != "23a440bfd6121509b0586f0afe1990fcf59dd8fb"
        or len(pdm["identity"]["embedded_third_party_definitions"]) != 3
        or pdm["surface"]["stored_function_entry_pointers"] != 1
        or pdm["production"]["production_routed"]
    ):
        raise ClosureError("generic PDM AmbiqSuite/CMSIS provider boundary changed")
    ancc_service_provider = service_ancc["provider_boundary"]
    if (
        ancc_service_provider["cmsis_freertos_mutex_calls"] != 17
        or ancc_service_provider["cmsis_freertos_commit"] != "d213f261b5be6bb29a7cce8b84071706b72f4d53"
        or ancc_service_provider["direct_ambiqsuite_ancc_calls"] != 0
        or ancc_service_provider["embedded_ambiqsuite_ancc_definitions"] != 0
        or ancc_service_provider["ambiqsuite_ancc_selected_commit"] != "de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f"
        or service_ancc["surface"]["stored_interior_callback_pointers"] != 3
        or service_ancc["production"]["production_routed"]
    ):
        raise ClosureError("service ANCC RTOS/upstream boundary changed")
    als_provider = als["provider_boundary"]
    if (
        als_provider["cmsis_freertos_delay_calls"] != 1
        or als_provider["cmsis_freertos_commit"] != "d213f261b5be6bb29a7cce8b84071706b72f4d53"
        or als_provider["opt3007_adapter_calls"] != 6
        or als_provider["public_opt3007_software_commit"] is not None
        or als["surface"]["bounded_first_party_indirect_calls"] != 1
        or als["identity"]["embedded_third_party_definitions"]
        or not als["production"]["production_routed"]
    ):
        raise ClosureError("ALS RTOS/OPT3007 specification boundary changed")
    production_thread_provider = thread_ble_production["provider_boundary"]
    if (
        production_thread_provider["cmsis_freertos_calls"] != 15
        or production_thread_provider["cmsis_freertos_commit"]
        != "d213f261b5be6bb29a7cce8b84071706b72f4d53"
        or production_thread_provider["freertos_assert_calls"] != 3
        or production_thread_provider["freertos_kernel_commit"]
        != "def7d2df2b0506d3d249334974f51e427c17a41c"
        or production_thread_provider["easylogger_calls"] != 106
        or production_thread_provider["historical_product_thread_commit"] is not None
        or thread_ble_production["surface"]["stored_function_pointers"] != 1
        or thread_ble_production["surface"]["strict_interior_ingress"] != 0
        or thread_ble_production["identity"]["embedded_third_party_definitions"]
        or thread_ble_production["production"]["production_routed"]
    ):
        raise ClosureError("BLE production-thread RTOS/provider boundary changed")
    pt_provider = pt_protocol["provider_boundary"]
    if (
        pt_provider["easylogger_calls"] != 1280
        or pt_provider["cmsis_freertos_calls"] != 7
        or pt_provider["freertos_kernel_calls"] != 1
        or pt_provider["runtime_calls"] != 41
        or pt_provider["mpaland_printf_calls"] != 1
        or pt_provider["historical_product_test_commit"] is not None
        or pt_protocol["surface"]["bounded_internal_dispatches"] != 1
        or pt_protocol["surface"]["stored_function_pointers"] != 66
        or pt_protocol["identity"]["embedded_third_party_definitions"]
        or pt_protocol["production"]["production_routed"]
    ):
        raise ClosureError("product-test protocol reusable/provider boundary changed")
    quicklist_provider = ui_quicklist_page["provider_boundary"]
    if (
        quicklist_provider["lvgl_calls"] != 415
        or quicklist_provider["easylogger_calls"] != 465
        or quicklist_provider["cmsis_freertos_calls"] != 5
        or quicklist_provider["iar_runtime_calls"] != 24
        or quicklist_provider["historical_quicklist_commit"] is not None
        or ui_quicklist_page["surface"]["stored_function_pointers"] != 15
        or ui_quicklist_page["surface"]["strict_interior_ingress"] != 0
        or ui_quicklist_page["identity"]["embedded_third_party_definitions"]
        or ui_quicklist_page["production"]["production_routed"]
    ):
        raise ClosureError("quicklist-page reusable/provider boundary changed")
    news_provider = ui_widget_news_page["provider_boundary"]
    if (
        news_provider["lvgl_calls"] != 508
        or news_provider["easylogger_calls"] != 565
        or news_provider["cmsis_freertos_calls"] != 8
        or news_provider["runtime_calls"] != 36
        or news_provider["historical_news_page_commit"] is not None
        or ui_widget_news_page["surface"]["stored_function_pointers"] != 12
        or ui_widget_news_page["surface"]["indirect_body_calls"] != 0
        or ui_widget_news_page["identity"]["embedded_third_party_definitions"]
        or ui_widget_news_page["production"]["production_routed"]
    ):
        raise ClosureError("dashboard news-page reusable/provider boundary changed")
    stock_provider = ui_stock_page["provider_boundary"]
    if (
        stock_provider["lvgl_calls"] != 454
        or stock_provider["easylogger_calls"] != 355
        or stock_provider["cmsis_freertos_calls"] != 0
        or stock_provider["runtime_calls"] != 10
        or stock_provider["historical_stock_page_commit"] is not None
        or ui_stock_page["surface"]["stored_function_pointers"] != 2
        or ui_stock_page["surface"]["indirect_body_calls"] != 0
        or ui_stock_page["identity"]["embedded_third_party_definitions"]
        or ui_stock_page["production"]["production_routed"]
    ):
        raise ClosureError("dashboard stock-page reusable/provider boundary changed")
    navigation_provider = navigation_ui["provider_boundary"]
    if (
        navigation_provider["lvgl_calls"] != 702
        or navigation_provider["easylogger_calls"] != 1245
        or navigation_provider["cmsis_freertos_calls"] != 20
        or navigation_provider["runtime_calls"] != 67
        or navigation_provider["nanopb_calls"] != 22
        or navigation_provider["mpaland_printf_calls"] != 2
        or navigation_provider["historical_navigation_ui_commit"] is not None
        or navigation_ui["surface"]["stored_function_start_pointers"] != 14
        or navigation_ui["surface"]["stored_interior_entry_pointers"] != 5
        or navigation_ui["surface"]["indirect_body_calls"] != 0
        or navigation_ui["identity"]["embedded_third_party_definitions"]
        or navigation_ui["production"]["production_routed"]
    ):
        raise ClosureError("navigation UI reusable/provider boundary changed")
    menu_provider = menu_page["provider_boundary"]
    if (
        menu_provider["lvgl_calls"] != 124
        or menu_provider["easylogger_calls"] != 445
        or menu_provider["cmsis_freertos_calls"] != 3
        or menu_provider["runtime_calls"] != 24
        or menu_provider["nanopb_calls"] != 15
        or menu_provider["historical_menu_page_commit"] is not None
        or menu_page["surface"]["stored_function_start_pointers"] != 8
        or menu_page["surface"]["stored_interior_entry_pointers"] != 1
        or menu_page["surface"]["indirect_body_calls"] != 0
        or menu_page["identity"]["embedded_third_party_definitions"]
        or menu_page["production"]["production_routed"]
    ):
        raise ClosureError("menu-page reusable/provider boundary changed")
    health_provider = ui_health_page["provider_boundary"]
    if (
        health_provider["lvgl_calls"] != 437
        or health_provider["easylogger_calls"] != 55
        or health_provider["cmsis_freertos_calls"] != 0
        or health_provider["runtime_calls"] != 4
        or health_provider["mpaland_printf_calls"] != 36
        or health_provider["historical_health_page_commit"] is not None
        or ui_health_page["surface"]["stored_function_pointers"] != 2
        or ui_health_page["surface"]["indirect_body_calls"] != 0
        or ui_health_page["identity"]["embedded_third_party_definitions"]
        or not ui_health_page["production"]["production_routed"]
    ):
        raise ClosureError("health-page reusable/provider boundary changed")
    ring_provider = ring_service["provider_boundary"]
    if (
        ring_provider["easylogger_calls"] != 76
        or ring_provider["cmsis_freertos_calls"] != 2
        or ring_provider["runtime_calls"] != 8
        or ring_provider["nanopb_calls"] != 1
        or ring_provider["cordio_calls"] != 0
        or ring_provider["historical_ring_service_commit"] is not None
        or ring_service["surface"]["stored_function_pointers"] != 2
        or ring_service["surface"]["indirect_body_calls"] != 0
        or ring_service["identity"]["embedded_third_party_definitions"]
        or not ring_service["production"]["production_routed"]
    ):
        raise ClosureError("ring-service reusable/provider boundary changed")
    input_provider = service_input_manager["provider_boundary"]
    if (
        input_provider["easylogger_calls"] != 85
        or input_provider["cmsis_freertos_calls"] != 2
        or input_provider["runtime_calls"] != 2
        or input_provider["nanopb_calls"] != 2
        or input_provider["bounded_abs_calls"] != 1
        or input_provider["historical_input_manager_commit"] is not None
        or service_input_manager["surface"]["stored_function_pointers"] != 2
        or service_input_manager["surface"]["indirect_body_calls"] != 0
        or service_input_manager["identity"]["embedded_third_party_definitions"]
        or service_input_manager["production"]["production_routed"]
    ):
        raise ClosureError("input-manager reusable/provider boundary changed")
    calendar_provider = ui_calendar_page["provider_boundary"]
    if (
        calendar_provider["lvgl_calls"] != 533
        or calendar_provider["easylogger_calls"] != 85
        or calendar_provider["cmsis_freertos_calls"] != 34
        or calendar_provider["runtime_calls"] != 12
        or calendar_provider["historical_calendar_page_commit"] is not None
        or ui_calendar_page["surface"]["stored_function_pointers"] != 3
        or ui_calendar_page["surface"]["indirect_body_calls"] != 0
        or ui_calendar_page["identity"]["embedded_third_party_definitions"]
        or ui_calendar_page["production"]["production_routed"]
    ):
        raise ClosureError("calendar-page reusable/provider boundary changed")
    ota_transport_provider = ota_transport["provider_boundary"]
    if (
        ota_transport_provider["easylogger_calls"] != 60
        or ota_transport_provider["runtime_calls"] != 8
        or ota_transport_provider["ota_service_calls"] != 5
        or ota_transport_provider["crc16_calls"] != 4
        or ota_transport_provider["heap_wrapper_calls"] != 6
        or ota_transport_provider["registered_callback_calls"] != 4
        or ota_transport_provider["historical_ota_transport_commit"] is not None
        or ota_transport["surface"]["indirect_body_calls"] != 4
        or ota_transport["identity"]["embedded_third_party_definitions"]
        or not ota_transport["production"]["production_routed"]
    ):
        raise ClosureError("OTA-transport reusable/provider boundary changed")
    efs_transport_provider = efs_transport["provider_boundary"]
    if (
        efs_transport_provider["easylogger_calls"] != 60
        or efs_transport_provider["cmsis_freertos_calls"] != 1
        or efs_transport_provider["runtime_calls"] != 8
        or efs_transport_provider["efs_service_calls"] != 5
        or efs_transport_provider["crc16_calls"] != 4
        or efs_transport_provider["heap_wrapper_calls"] != 6
        or efs_transport_provider["registered_callback_calls"] != 4
        or efs_transport_provider["historical_efs_transport_commit"] is not None
        or efs_transport["surface"]["indirect_body_calls"] != 4
        or efs_transport["identity"]["embedded_third_party_definitions"]
        or not efs_transport["production"]["production_routed"]
    ):
        raise ClosureError("EFS-transport reusable/provider boundary changed")
    loading_provider = evenhub_loading_page["provider_boundary"]
    if (
        loading_provider["lvgl_calls"] != 36
        or loading_provider["easylogger_calls"] != 85
        or loading_provider["runtime_calls"] != 2
        or loading_provider["historical_loading_page_commit"] is not None
        or evenhub_loading_page["surface"]["stored_function_pointers"] != 2
        or evenhub_loading_page["surface"]["indirect_body_calls"] != 0
        or evenhub_loading_page["identity"]["embedded_third_party_definitions"]
        or evenhub_loading_page["production"]["production_routed"]
    ):
        raise ClosureError("EvenHub-loading-page reusable/provider boundary changed")
    layout1_provider = dashboard_watchface_layout1["provider_boundary"]
    if (
        layout1_provider["lvgl_calls"] != 154
        or layout1_provider["easylogger_calls"] != 20
        or layout1_provider["iar_dlib_calls"] != 13
        or layout1_provider["mpaland_printf_calls"] != 10
        or layout1_provider["private_generating_commit_recoverable"]
        or dashboard_watchface_layout1["surface"]["bounded_local_callback_targets"] != 2
        or dashboard_watchface_layout1["identity"]["embedded_third_party_definitions"]
        or dashboard_watchface_layout1["production"]["production_routed"]
    ):
        raise ClosureError("dashboard-layout1 reusable/provider boundary changed")
    fsm_provider = teleprompt_fsm["provider_boundary"]
    if (
        fsm_provider["easylogger_calls"] != 140
        or fsm_provider["iar_runtime_calls"] != 3
        or fsm_provider["lvgl_calls"] != 1
        or fsm_provider["nanopb_calls"] != 2
        or fsm_provider["historical_fsm_commit"] is not None
        or teleprompt_fsm["surface"]["bounded_handler_table_entries"] != 9
        or teleprompt_fsm["identity"]["embedded_third_party_definitions"]
        or teleprompt_fsm["production"]["production_routed"]
    ):
        raise ClosureError("teleprompt-FSM reusable/provider boundary changed")
    health_manager_provider = health_data_manager["provider_boundary"]
    if (
        health_manager_provider["easylogger_calls"] != 120
        or health_manager_provider["iar_runtime_calls"] != 6
        or health_manager_provider["closed_health_lock_calls"] != 10
        or health_manager_provider["direct_cmsis_freertos_calls"] != 0
        or health_manager_provider["historical_health_manager_commit"] is not None
        or health_data_manager["identity"]["embedded_third_party_definitions"]
        or not health_data_manager["production"]["production_routed"]
    ):
        raise ClosureError("health-data-manager reusable/provider boundary changed")
    evenhub_main_provider = evenhub_main["provider_boundary"]
    if (
        evenhub_main_provider["easylogger_calls"] != 120
        or evenhub_main_provider["iar_runtime_calls"] != 6
        or evenhub_main_provider["lvgl_calls"] != 2
        or evenhub_main_provider["cmsis_freertos_calls"] != 2
        or evenhub_main_provider["nanopb_calls"] != 3
        or evenhub_main_provider["heap_wrapper_calls"] != 2
        or evenhub_main_provider["first_party_calls"] != 45
        or evenhub_main_provider["historical_evenhub_main_commit"] is not None
        or evenhub_main["surface"]["raw_noncode_pseudo_bl_sites"] != 1
        or evenhub_main["surface"]["raw_unaligned_interior_word_collisions"] != 1
        or evenhub_main["identity"]["embedded_third_party_definitions"]
        or evenhub_main["production"]["production_routed"]
    ):
        raise ClosureError("EvenHub-main reusable/provider boundary changed")
    translate_provider = translate["provider_boundary"]
    if (
        tuple(translate_provider[x] for x in ("easylogger_calls","iar_runtime_calls","lvgl_calls","cmsis_freertos_calls","nanopb_calls","first_party_calls")) != (105,7,2,7,3,32)
        or translate_provider["historical_translate_commit"] is not None
        or translate["surface"]["indirect_body_calls"] != 0
        or translate["identity"]["embedded_third_party_definitions"]
        or translate["production"]["production_routed"]
    ):
        raise ClosureError("translate reusable/provider boundary changed")
    teleprompt_controller_provider = teleprompt_controller["provider_boundary"]
    if (
        tuple(teleprompt_controller_provider[x] for x in ("easylogger_calls","iar_runtime_calls","lvgl_calls","cmsis_freertos_calls","nanopb_calls","first_party_calls")) != (90,4,2,7,3,43)
        or teleprompt_controller_provider["historical_teleprompt_commit"] is not None
        or teleprompt_controller["surface"]["indirect_body_calls"] != 0
        or teleprompt_controller["identity"]["embedded_third_party_definitions"]
        or teleprompt_controller["production"]["production_routed"]
    ):
        raise ClosureError("teleprompt-controller reusable/provider boundary changed")
    comm_provider = conversate_comm_data["provider_boundary"]
    if (
        tuple(comm_provider[x] for x in ("easylogger_calls","iar_dlib_calls","lvgl_calls")) != (60,11,1)
        or comm_provider["historical_conversate_commit"] is not None
        or conversate_comm_data["surface"]["indirect_body_calls"] != 0
        or conversate_comm_data["identity"]["embedded_third_party_definitions"]
        or conversate_comm_data["production"]["production_routed"]
    ):
        raise ClosureError("Conversate-common-data reusable/provider boundary changed")
    controller_provider = conversate_controller["provider_boundary"]
    if (
        tuple(controller_provider[x] for x in (
            "easylogger_calls", "iar_dlib_calls", "cmsis_freertos_calls",
            "lvgl_calls", "nanopb_calls", "source_owned_eabi_calls",
            "cmbacktrace_calls", "first_party_calls",
        )) != (80, 4, 7, 2, 3, 1, 1, 41)
        or controller_provider["cmbacktrace_selected_compatibility_commit"] != "73714489f9d8af130aacb515586b397b604a5768"
        or controller_provider["cmbacktrace_exact_historical_commit"] is not None
        or conversate_controller["surface"]["indirect_body_calls"] != 0
        or conversate_controller["identity"]["embedded_third_party_definitions"]
        or conversate_controller["production"]["production_routed"]
    ):
        raise ClosureError("Conversate-controller reusable/provider boundary changed")
    main_page_provider = conversate_ui_main_page["provider_boundary"]
    if (
        tuple(main_page_provider[x] for x in (
            "easylogger_calls", "lvgl_calls", "iar_dlib_calls", "first_party_calls",
        )) != (130, 98, 2, 53)
        or main_page_provider["historical_main_page_commit"] is not None
        or conversate_ui_main_page["surface"]["indirect_body_calls"] != 0
        or conversate_ui_main_page["surface"]["stored_strict_interior_entries"] != 1
        or conversate_ui_main_page["identity"]["embedded_third_party_definitions"]
        or conversate_ui_main_page["production"]["production_routed"]
    ):
        raise ClosureError("conversate-main-page reusable/provider boundary changed")
    universal_provider = service_universal_setting["provider_boundary"]
    if (
        tuple(universal_provider[x] for x in (
            "easylogger_calls", "iar_dlib_calls", "source_owned_crc_calls",
            "closed_kv_calls", "first_party_calls",
        )) != (75, 17, 3, 3, 5)
        or universal_provider["historical_universal_setting_commit"] is not None
        or service_universal_setting["surface"]["indirect_body_calls"] != 0
        or service_universal_setting["identity"]["embedded_third_party_definitions"]
        or service_universal_setting["production"]["production_routed"]
    ):
        raise ClosureError("service-universal-setting reusable/provider boundary changed")
    image_provider = common_image_container["provider_boundary"]
    if (
        tuple(image_provider[x] for x in (
            "easylogger_calls", "lvgl_calls", "source_owned_heap_calls",
            "source_owned_cache_calls", "bounded_abs_calls", "first_party_calls",
        )) != (70, 3, 3, 1, 1, 2)
        or image_provider["historical_container_commit"] is not None
        or common_image_container["surface"]["indirect_body_calls"] != 0
        or common_image_container["identity"]["embedded_third_party_definitions"]
        or common_image_container["production"]["production_routed"]
    ):
        raise ClosureError("common-image-container reusable/provider boundary changed")
    layout2_provider = dashboard_watchface_layout2["provider_boundary"]
    if (
        tuple(layout2_provider[x] for x in ("easylogger_calls","lvgl_calls","iar_dlib_calls","mpaland_printf_calls","first_party_calls")) != (20,104,9,5,43)
        or layout2_provider["historical_layout2_commit"] is not None
        or dashboard_watchface_layout2["surface"]["indirect_body_calls"] != 0
        or dashboard_watchface_layout2["identity"]["embedded_third_party_definitions"]
        or dashboard_watchface_layout2["production"]["production_routed"]
    ):
        raise ClosureError("dashboard-layout2 reusable/provider boundary changed")
    layout3_provider = dashboard_watchface_layout3["provider_boundary"]
    if (
        tuple(layout3_provider[x] for x in ("easylogger_calls","lvgl_calls","iar_dlib_calls","mpaland_printf_calls","first_party_calls")) != (20,125,10,2,16)
        or layout3_provider["historical_layout3_commit"] is not None
        or dashboard_watchface_layout3["surface"]["raw_overlapping_pseudo_bl_sites"] != 5
        or dashboard_watchface_layout3["identity"]["embedded_third_party_definitions"]
        or dashboard_watchface_layout3["production"]["production_routed"]
    ):
        raise ClosureError("dashboard-layout3 reusable/provider boundary changed")
    thread_ring_provider = thread_ring["provider_boundary"]
    if (
        tuple(thread_ring_provider[x] for x in ("easylogger_calls","cmsis_freertos_calls","freertos_assert_calls","iar_dlib_calls","source_owned_heap_wrapper_calls","closed_ring_service_calls","event_loop_calls","other_first_party_calls")) != (110,10,2,2,3,13,16,6)
        or thread_ring_provider["historical_thread_ring_commit"] is not None
        or thread_ring["surface"]["restored_functions"] != 12
        or thread_ring["surface"]["stored_entry_pointers"] != 8
        or thread_ring["identity"]["embedded_third_party_definitions"]
        or not thread_ring["production"]["production_routed"]
    ):
        raise ClosureError("Ring-thread reusable/provider boundary changed")
    sensor_hub_provider = sensor_hub["provider_boundary"]
    if (
        tuple(sensor_hub_provider[x] for x in ("easylogger_calls", "admitted_lvgl_calls", "cmsis_freertos_calls", "closed_first_party_calls", "translation_lookup_calls", "nanopb_calls", "bounded_open_first_party_calls")) != (130, 69, 9, 36, 8, 1, 1)
        or sensor_hub_provider["freertos_kernel_direct_calls"] != 0
        or sensor_hub_provider["embedded_sensor_fusion_library"] is not None
        or sensor_hub["surface"]["restored_functions"] != 26
        or sensor_hub["surface"]["stored_function_entry_pointers"] != 3
        or sensor_hub["identity"]["embedded_third_party_definitions"]
        or not sensor_hub["production"]["production_routed"]
        or sensor_hub["production"]["source_functions"] != 31
        or sensor_hub["production"]["hardware_validation"] != "blocked_unavailable_physical_evidence"
    ):
        raise ClosureError("Sensor Hub reusable/provider boundary changed")
    event_loop_provider = fw_event_loop["provider_boundary"]
    if (
        tuple(event_loop_provider[x] for x in ("easylogger_calls","cmsis_freertos_calls","freertos_critical_port_calls","bounded_first_party_indirect_calls")) != (80,20,4,1)
        or event_loop_provider["historical_fw_event_loop_commit"] is not None
        or fw_event_loop["surface"]["restored_functions"] != 1
        or fw_event_loop["identity"]["embedded_third_party_definitions"]
        or not fw_event_loop["production"]["production_routed"]
        or fw_event_loop["production"]["source_routed_functions"] != 6
    ):
        raise ClosureError("firmware-event-loop reusable/provider boundary changed")
    ring_policy_provider = ring_connect_policy["provider_boundary"]
    if (
        tuple(ring_policy_provider[x] for x in ("easylogger_calls","cmsis_freertos_calls","closed_event_loop_calls","closed_nanopb_facade_calls","closed_ble_central_calls")) != (95,1,10,1,1)
        or tuple(ring_policy_provider[x] for x in ("direct_cordio_calls","direct_nanopb_calls")) != (0,0)
        or ring_policy_provider["historical_ring_connect_policy_commit"] is not None
        or ring_connect_policy["surface"]["restored_functions"] != 4
        or ring_connect_policy["surface"]["stored_entry_pointers"] != 1
        or ring_connect_policy["identity"]["embedded_third_party_definitions"]
        or not ring_connect_policy["production"]["production_routed"]
    ):
        raise ClosureError("Ring-connect-policy reusable/provider boundary changed")
    system_close_provider = system_close["provider_boundary"]
    if (
        tuple(system_close_provider[x] for x in ("easylogger_calls","lvgl_calls","iar_dlib_calls","first_party_calls")) != (130,99,5,37)
        or system_close_provider["direct_cmsis_freertos_calls"] != 0
        or system_close_provider["historical_system_close_commit"] is not None
        or system_close["surface"]["restored_functions"] != 15
        or system_close["surface"]["stored_entry_pointers"] != 3
        or system_close["identity"]["embedded_third_party_definitions"]
        or not system_close["production"]["production_routed"]
        or not system_close["production"]["source_admitted"]
        or system_close["production"]["software_functional_gap"]
    ):
        raise ClosureError("SystemClose reusable/provider boundary changed")
    if (
        iar_float_exponent["identity"]["family"] != "IAR-DLIB"
        or iar_float_exponent["surface"]["linked_functions"] != 3
        or iar_float_exponent["surface"]["physical_bytes"] != 268
        or not iar_float_exponent["production"]["production_routed"]
        or iar_float_exponent["production"]["production_profiles"] != ["apple-clang"]
        or iar_float_exponent["production"]["pending_profiles"] != ["linux-clang"]
        or not iar_float_exponent["production"]["exact_stock_reproduction"]
        or iar_float_exponent["production"]["remaining_functional_gap"]
    ):
        raise ClosureError("IAR float-exponent production boundary changed")
    translate_ui_provider = translate_ui["provider_boundary"]
    if (
        tuple(translate_ui_provider[x] for x in ("easylogger_calls","lvgl_calls","iar_dlib_calls","cmsis_freertos_calls","first_party_calls","bounded_first_party_indirect_calls")) != (175,125,10,2,34,1)
        or translate_ui_provider["historical_translate_ui_commit"] is not None
        or translate_ui["surface"]["restored_functions"] != 22
        or translate_ui["surface"]["stored_entry_pointers"] != 13
        or translate_ui["identity"]["embedded_third_party_definitions"]
        or translate_ui["production"]["production_routed"]
    ):
        raise ClosureError("Translate-UI reusable/provider boundary changed")
    db_provider = service_db_api["provider_boundary"]
    if (
        db_provider["flashdb_version"] != "2.1.1"
        or db_provider["flashdb_commit"] != "714d6159e7e6afb267a3953756abca445c350e61"
        or db_provider["flashdb_calls"] != 2
        or db_provider["cmsis_freertos_calls"] != 7
        or not db_provider["unsafe_zero_on_failure_fal_seam"]
        or service_db_api["identity"]["embedded_third_party_definitions"]
    ):
        raise ClosureError("FlashDB service-adapter provider boundary changed")
    even_ai_provider = ui_even_ai["provider_boundary"]
    if (
        even_ai_provider["lvgl_calls"] != 182
        or even_ai_provider["cmsis_freertos_calls"] != 1
        or even_ai_provider["lvgl_commit"] != "344c7c318047b7348e1be8572a9fd4260c251cfa"
        or ui_even_ai["identity"]["embedded_third_party_definitions"]
    ):
        raise ClosureError("EvenAI UI LVGL/CMSIS provider boundary changed")
    time_provider = service_time["provider_boundary"]
    if (
        time_provider["iar_dlib_calls"] != 8
        or time_provider["direct_cmsis_freertos_calls"] != 0
        or service_time["identity"]["embedded_third_party_definitions"]
    ):
        raise ClosureError("time-service CMSIS/IAR ownership boundary changed")
    audio_provider = thread_audio["provider_boundary"]
    if (
        audio_provider["cmsis_freertos_calls"] != 20
        or audio_provider["cmsis_wrapper_count"] != 14
        or audio_provider["iar_dlib_calls"] != 1
        or audio_provider["closed_codec_gx8002b_calls"] != 19
        or audio_provider["nationalchip_lvp_code_linked"]
        or thread_audio["identity"]["embedded_third_party_definitions"]
    ):
        raise ClosureError("audio-thread CMSIS/codec ownership boundary changed")
    compress_provider = compress_log_core["provider_boundary"]
    if (
        compress_provider["iar_dlib_calls"] != 13
        or compress_provider["easylogger_control_output_calls"] != 30
        or compress_provider["freertos_kernel_port_calls"] != 14
        or compress_provider["cmsis_freertos_calls"] != 2
        or compress_provider["private_hook_is_upstream_easylogger"]
        or compress_provider["private_compact_output_entry"] != "0x0043CE9E"
        or compress_provider["upstream_derived_elog_output_entry"] != "0x0043D574"
        or compress_log_core["identity"]["embedded_third_party_definitions"]
    ):
        raise ClosureError("compact-log EasyLogger/RTOS ownership boundary changed")
    compress_port_provider = compress_log_port["provider_boundary"]
    if (
        compress_port_provider["easylogger_control_output_calls"] != 24
        or compress_port_provider["closed_compact_log_core_calls"] != 6
        or compress_port_provider["iar_dlib_calls"] != 2
        or compress_port_provider["source_owned_file_runtime_calls"] != 18
        or compress_port_provider["source_owned_delayed_callback_calls"] != 3
        or compress_port_provider["littlefs_commit"] != "0494ce7169f06a734a7bd7585f49a9fa91fa7318"
        or not compress_port_provider["all_file_runtime_entries_production_source_owned"]
        or not compress_port_provider["all_delayed_callback_entries_production_source_owned"]
        or compress_log_port["identity"]["embedded_third_party_definitions"]
    ):
        raise ClosureError("compact-log port littlefs/file-runtime ownership boundary changed")
    file_provider = file_runtime["provider_boundary"]
    if (
        file_provider["cmsis_freertos_calls"] != 36
        or file_provider["littlefs_backend_adapter_calls"] != 14
        or file_provider["tlsf_calls"] != 3
        or file_provider["iar_dlib_calls"] != 6
        or file_provider["embedded_third_party_definitions"] != 0
        or file_runtime["production"]["source_owned_functions"] != 18
        or not file_runtime["production"]["production_routed"]
    ):
        raise ClosureError("shared file-runtime dependency/production ownership changed")
    algo_provider = service_algo["provider_boundary"]
    if (
        algo_provider["iar_dlib_memory_math_calls"] != 10
        or algo_provider["source_owned_unsigned_64_division_calls"] != 6
        or algo_provider["iar_asin_calls"] != 1
        or algo_provider["iar_signed_64_to_double_calls"] != 4
        or algo_provider["iar_sqrt_calls"] != 2
        or service_algo["identity"]["nationalchip_lvp_code_linked"]
        or service_algo["identity"]["embedded_third_party_definitions"]
        or not service_algo["behavior"]["short_aligned_input_is_accepted_but_read_as_3200_bytes"]
    ):
        raise ClosureError("audio service-algorithm IAR/DSP ownership changed")
    uart_provider = uart_sync["provider_boundary"]
    if (
        uart_provider["easylogger_and_compact_calls"] != 30
        or uart_provider["cmsis_freertos_calls"] != 8
        or uart_provider["iar_dlib_calls"] != 1
        or uart_provider["g2_stream_calls"] != 4
        or uart_provider["g2_uart_adapter_calls"] != 5
        or uart_provider["tinyframe_and_sync_framework_calls"] != 4
        or uart_provider["bounded_indirect_initializer_calls"] != 1
        or uart_provider["tinyframe_selected_commit"]
        != "eb75483e035916ef9f3e9fce0d2ae389cb09785f"
        or uart_provider["ambiqsuite_apollo510_commit"]
        != "5efc0228528a8adce5eae0d226fac85d2551eb3b"
        or uart_sync["identity"]["embedded_third_party_definitions"]
        or uart_sync["behavior"]["dynamic_initializer_pointer_slot"] != "0x20000658"
    ):
        raise ClosureError("UART-sync RTOS/TinyFrame/Ambiq ownership boundary changed")
    nvdb_provider = service_nvdb["provider_boundary"]
    if (
        nvdb_provider["flashdb_version"] != "2.1.1"
        or nvdb_provider["flashdb_commit"]
        != "714d6159e7e6afb267a3953756abca445c350e61"
        or nvdb_provider["flashdb_core_calls"] != 4
        or nvdb_provider["g2_database_adapter_calls"] != 9
        or nvdb_provider["iar_dlib_calls"] != 2
        or service_nvdb["identity"]["embedded_third_party_definitions"]
        or service_nvdb["behavior"]["factory_magic_value"] != 0x55550022
        or service_nvdb["behavior"]["magic_mismatch_policy"]
        != "wholesale fdb_kv_set_default"
        or not service_nvdb["behavior"]["stock_fal_zero_on_driver_failure_hazard"]
    ):
        raise ClosureError("factory NVdb FlashDB ownership/safety boundary changed")
    production_mic_provider = production_mic["provider_boundary"]
    if (
        production_mic_provider["iar_dlib_memory_calls"] != 5
        or production_mic_provider["g2_codec_pdm_pcm_calls"] != 24
        or production_mic_provider["direct_cmsis_freertos_calls"] != 0
        or production_mic["identity"]["nationalchip_lvp_code_linked"]
        or production_mic["identity"]["embedded_third_party_definitions"]
        or production_mic["surface"]["restored_functions"] != 1
        or not production_mic["behavior"]["stereo_extracted_channels_concatenated"]
    ):
        raise ClosureError("production microphone IAR/DSP ownership boundary changed")
    audio_manager_provider = service_audio_manager["provider_boundary"]
    if (
        audio_manager_provider["easylogger_and_compact_calls"] != 80
        or audio_manager_provider["iar_dlib_memset_calls"] != 1
        or audio_manager_provider["g2_product_role_and_system_calls"] != 8
        or audio_manager_provider["g2_audio_hardware_and_power_calls"] != 11
        or audio_manager_provider["g2_common_data_transport_calls"] != 1
        or audio_manager_provider["direct_cmsis_freertos_calls"] != 0
        or service_audio_manager["identity"]["embedded_third_party_definitions"]
        or service_audio_manager["surface"]["restored_functions"] != 2
        or service_audio_manager["behavior"]["common_data_frame_id"] != 0x10C
    ):
        raise ClosureError("audio-manager IAR/RTOS ownership boundary changed")
    kvdb_provider = service_kvdb["provider_boundary"]
    if (
        kvdb_provider["flashdb_version"] != "2.1.1"
        or kvdb_provider["flashdb_commit"]
        != "714d6159e7e6afb267a3953756abca445c350e61"
        or kvdb_provider["flashdb_core_calls"] != 4
        or kvdb_provider["g2_database_adapter_calls"] != 12
        or kvdb_provider["closed_migration_target_entries"] != 11
        or service_kvdb["identity"]["embedded_third_party_definitions"]
        or service_kvdb["behavior"]["boot_count_startup_value"] != 0
        or not service_kvdb["behavior"]["boot_count_read_increment_write"]
        or not service_kvdb["behavior"]["stock_fal_zero_on_driver_failure_hazard"]
    ):
        raise ClosureError("system KVDB FlashDB/default lifecycle changed")
    battery_sync_provider = ux_battery_sync["provider_boundary"]
    if (
        battery_sync_provider["easylogger_calls"] != 45
        or battery_sync_provider["g2_charger_common_calls"] != 4
        or battery_sync_provider["g2_ring_battery_calls"] != 6
        or battery_sync_provider["g2_callback_manager_calls"] != 2
        or battery_sync_provider["direct_cmsis_freertos_calls"] != 0
        or ux_battery_sync["identity"]["embedded_third_party_definitions"]
        or ux_battery_sync["behavior"]["service_record_id"] != 0x105
    ):
        raise ClosureError("UX battery-sync third-party/provider boundary changed")
    cb_ring_provider = cb_ring_battery["provider_boundary"]
    if (
        cb_ring_provider["easylogger_calls"] != 5
        or cb_ring_provider["g2_generic_callback_manager_calls"] != 4
        or cb_ring_provider["direct_cmsis_freertos_calls"] != 0
        or cb_ring_battery["identity"]["embedded_third_party_definitions"]
        or cb_ring_battery["behavior"]["callback_list_address"] != 0x20073F90
        or cb_ring_battery["surface"]["restored_functions"] != 4
    ):
        raise ClosureError("ring-battery callback third-party/provider boundary changed")
    facade_provider = callback_facades["aggregate"]
    if (
        facade_provider["easylogger_calls"] != 20
        or facade_provider["generic_callback_manager_calls"] != 10
        or facade_provider["direct_cmsis_freertos_calls"] != 0
        or callback_facades["identity"]["embedded_third_party_definitions"]
        or facade_provider["restored_functions"] != 6
        or callback_facades["modules"]["charge"]["callback_list_address"] != 0x20073F78
        or callback_facades["modules"]["msg_notif"]["callback_list_address"] != 0x20073F84
    ):
        raise ClosureError("charge/message callback third-party/provider boundary changed")
    callback_manager_provider = callback_manager["provider_boundary"]
    if (
        callback_manager_provider["easylogger_calls"] != 70
        or callback_manager_provider["source_owned_heap_wrapper_calls"] != 2
        or callback_manager_provider["direct_cmsis_freertos_calls"] != 0
        or callback_manager_provider["bounded_registered_callback_sites"] != 1
        or callback_manager["identity"]["embedded_third_party_definitions"]
        or callback_manager["surface"]["restored_functions"] != 1
    ):
        raise ClosureError("generic callback-manager third-party/provider boundary changed")
    silent_provider = silent_mode["provider_boundary"]
    if (
        silent_provider["easylogger_calls"] != 70
        or silent_provider["lvgl_calls"] != 70
        or silent_provider["freertos_vtaskdelay_calls"] != 1
        or silent_provider["iar_memset_calls"] != 1
        or silent_provider["direct_cmsis_freertos_calls"] != 0
        or silent_mode["identity"]["embedded_third_party_definitions"]
        or silent_mode["surface"]["restored_functions"] != 3
    ):
        raise ClosureError("silent-mode third-party/provider boundary changed")
    onboarding_provider = onboarding_data_manager["provider_boundary"]
    if (
        onboarding_provider["easylogger_calls"] != 35
        or onboarding_provider["cmsis_freertos_calls"] != 3
        or onboarding_provider["iar_memset_calls"] != 3
        or onboarding_provider["closed_onboarding_kvdb_calls"] != 4
        or onboarding_provider["closed_onboarding_protobuf_calls"] != 1
        or onboarding_provider["selected_flashdb_commit"]
        != "714d6159e7e6afb267a3953756abca445c350e61"
        or onboarding_provider["selected_nanopb_commit"]
        != "98bf4db69897b53434f3d0ba72e0a3ab1a902824"
        or onboarding_data_manager["identity"]["embedded_third_party_definitions"]
        or onboarding_data_manager["surface"]["strict_interior_code_ingress"] != 0
    ):
        raise ClosureError("onboarding data-manager third-party/provider boundary changed")
    controller_provider = onboarding_controller["provider_boundary"]
    if (
        controller_provider["easylogger_calls"] != 165
        or controller_provider["lvgl_calls"] != 32
        or controller_provider["cmsis_freertos_calls"] != 1
        or controller_provider["iar_memset_calls"] != 2
        or controller_provider["closed_onboarding_data_manager_calls"] != 5
        or controller_provider["closed_onboarding_protobuf_calls"] != 1
        or onboarding_controller["identity"]["embedded_third_party_definitions"]
        or onboarding_controller["surface"]["restored_functions"] != 3
    ):
        raise ClosureError("onboarding controller third-party/provider boundary changed")
    main_page_provider = onboarding_main_page["provider_boundary"]
    if (
        main_page_provider["lvgl_calls"] != 264
        or main_page_provider["easylogger_calls"] != 45
        or main_page_provider["cmsis_freertos_calls"] != 23
        or main_page_provider["iar_dlib_calls"] != 17
        or main_page_provider["mpaland_printf_calls"] != 4
        or main_page_provider["closed_onboarding_protobuf_calls"] != 1
        or onboarding_main_page["identity"]["embedded_third_party_definitions"]
        or onboarding_main_page["surface"]["restored_functions"] != 15
    ):
        raise ClosureError("onboarding main-page third-party/provider boundary changed")
    stock_page_provider = onboarding_stock_page["provider_boundary"]
    if (
        stock_page_provider["lvgl_calls"] != 447
        or stock_page_provider["easylogger_calls"] != 110
        or stock_page_provider["cmsis_freertos_calls"] != 2
        or stock_page_provider["iar_dlib_calls"] != 5
        or stock_page_provider["first_party_calls"] != 33
        or onboarding_stock_page["identity"]["embedded_third_party_definitions"]
        or onboarding_stock_page["surface"]["restored_functions"] != 0
        or onboarding_stock_page["surface"]["strict_interior_ingress"] != 0
    ):
        raise ClosureError("onboarding stock-page third-party/provider boundary changed")
    news_page_provider = onboarding_news_page["provider_boundary"]
    if (
        news_page_provider["lvgl_calls"] != 232
        or news_page_provider["easylogger_calls"] != 160
        or news_page_provider["cmsis_freertos_calls"] != 16
        or news_page_provider["iar_dlib_calls"] != 15
        or news_page_provider["source_owned_aeabi_calls"] != 1
        or news_page_provider["closed_time_service_calls"] != 2
        or news_page_provider["first_party_calls"] != 44
        or onboarding_news_page["identity"]["embedded_third_party_definitions"]
        or onboarding_news_page["surface"]["strict_interior_ingress"] != 0
        or onboarding_news_page["surface"]["raw_overlapping_pseudo_bl_sites"] != 2
    ):
        raise ClosureError("onboarding news-page third-party/provider boundary changed")
    font_provider = lvgl_font_manager["provider_boundary"]
    if (
        font_provider["easylogger_calls"] != 125
        or font_provider["iar_dlib_calls"] != 2
        or font_provider["g2_mspi_lock_calls"] != 2
        or font_provider["source_owned_heap_wrapper_calls"] != 9
        or font_provider["lvgl_freetype_adapter_calls"] != 2
        or font_provider["freetype_version"] != "2.9.1"
        or font_provider["freetype_commit"] != "86bc8a95056c97a810986434a3f268cbe67f2902"
        or lvgl_font_manager["identity"]["embedded_third_party_definitions"]
    ):
        raise ClosureError("LVGL font-manager third-party/provider boundary changed")
    list_provider = common_list_container["provider_boundary"]
    if (
        list_provider["easylogger_calls"] != 310
        or list_provider["lvgl_calls"] != 91
        or list_provider["iar_dlib_calls"] != 3
        or list_provider["source_owned_heap_wrapper_calls"] != 6
        or list_provider["first_party_calls"] != 9
        or list_provider["selection_callback_calls"] != 2
        or list_provider["selection_callback_target"] != "0x004949C0"
        or common_list_container["surface"]["bounded_indirect_targets"] != 1
        or common_list_container["identity"]["embedded_third_party_definitions"]
    ):
        raise ClosureError("common-list-container third-party/provider boundary changed")
    text_provider = common_text_container["provider_boundary"]
    if (
        text_provider["easylogger_calls"] != 325
        or text_provider["lvgl_calls"] != 78
        or text_provider["iar_dlib_calls"] != 5
        or text_provider["source_owned_heap_wrapper_calls"] != 6
        or text_provider["first_party_calls"] != 12
        or text_provider["navigation_callback_calls"] != 4
        or text_provider["navigation_callback_target"] != "0x00494A78"
        or common_text_container["surface"]["bounded_indirect_targets"] != 1
        or common_text_container["surface"]["restored_functions"] != 3
        or common_text_container["identity"]["embedded_third_party_definitions"]
    ):
        raise ClosureError("common-text-container third-party/provider boundary changed")
    evenhub_provider = evenhub_ui["provider_boundary"]
    if (
        evenhub_provider["easylogger_calls"] != 690
        or evenhub_provider["lvgl_calls"] != 37
        or evenhub_provider["nanopb_calls"] != 7
        or evenhub_provider["iar_dlib_calls"] != 22
        or evenhub_provider["source_owned_heap_wrapper_calls"] != 10
        or evenhub_provider["closed_lz4_adapter_calls"] != 2
        or evenhub_provider["first_party_calls"] != 55
        or evenhub_provider["bounded_indirect_targets"] != 3
        or evenhub_ui["surface"]["restored_functions"] != 16
        or evenhub_ui["identity"]["embedded_third_party_definitions"]
    ):
        raise ClosureError("EvenHub UI third-party/provider boundary changed")
    parser_provider = evenhub_data_parser["provider_boundary"]
    if (
        parser_provider["easylogger_calls"] != 385
        or parser_provider["nanopb_calls"] != 25
        or parser_provider["cmsis_freertos_calls"] != 3
        or parser_provider["lvgl_calls"] != 14
        or parser_provider["iar_dlib_calls"] != 54
        or parser_provider["source_owned_heap_wrapper_calls"] != 12
        or parser_provider["first_party_calls"] != 48
        or evenhub_data_parser["surface"]["restored_functions"] != 2
        or evenhub_data_parser["surface"]["indirect_body_calls"] != 0
        or evenhub_data_parser["identity"]["embedded_third_party_definitions"]
    ):
        raise ClosureError("EvenHub data-parser third-party/provider boundary changed")
    sync_provider = sync_framework["provider_boundary"]
    if (
        sync_provider["easylogger_calls"] != 825
        or sync_provider["cmsis_freertos_calls"] != 35
        or sync_provider["freertos_kernel_calls"] != 4
        or sync_provider["tinyframe_calls"] != 26
        or sync_provider["ambiqsuite_calls"] != 2
        or sync_provider["nanopb_calls"] != 1
        or sync_provider["iar_dlib_calls"] != 17
        or sync_provider["source_owned_heap_wrapper_calls"] != 86
        or sync_provider["thread_pool_calls"] != 18
        or sync_provider["delay_wrapper_calls"] != 1
        or sync_provider["first_party_calls"] != 36
        or sync_framework["surface"]["restored_functions"] != 20
        or sync_framework["surface"]["indirect_body_calls"] != 14
        or sync_framework["identity"]["embedded_third_party_definitions"]
    ):
        raise ClosureError("sync-framework third-party/provider boundary changed")
    sync_api_provider = sync_interface_api["provider_boundary"]
    if (
        sync_api_provider["easylogger_calls"] != 255
        or sync_api_provider["cmsis_freertos_calls"] != 17
        or sync_api_provider["freertos_assert_calls"] != 9
        or sync_api_provider["iar_dlib_calls"] != 13
        or sync_api_provider["source_owned_heap_wrapper_calls"] != 33
        or sync_api_provider["first_party_calls"] != 6
        or sync_interface_api["surface"]["restored_functions"] != 0
        or sync_interface_api["surface"]["indirect_body_calls"] != 0
        or sync_interface_api["identity"]["embedded_third_party_definitions"]
    ):
        raise ClosureError("sync-interface API third-party/provider boundary changed")
    display_provider = display_thread["provider_boundary"]
    if (
        display_provider["easylogger_calls"] != 310
        or display_provider["cmsis_freertos_calls"] != 21
        or display_provider["freertos_calls"] != 11
        or display_provider["lvgl_calls"] != 12
        or display_provider["iar_dlib_calls"] != 23
        or display_provider["source_owned_runtime_calls"] != 5
        or display_provider["first_party_calls"] != 140
        or display_thread["surface"]["restored_functions"] != 13
        or display_thread["surface"]["indirect_body_calls"] != 12
        or not display_thread["production"]["production_routed"]
        or display_thread["identity"]["embedded_third_party_definitions"]
    ):
        raise ClosureError("display-thread third-party/provider boundary changed")
    mx25_provider = drv_mx25["provider_boundary"]
    if (
        mx25_provider["easylogger_calls"] != 230
        or mx25_provider["ambiqsuite_calls"] != 31
        or mx25_provider["cmsis_freertos_calls"] != 5
        or mx25_provider["shared_nanopb_initializer_calls"] != 3
        or mx25_provider["iar_dlib_calls"] != 7
        or mx25_provider["source_owned_runtime_calls"] != 16
        or mx25_provider["source_owned_delay_calls"] != 5
        or drv_mx25["surface"]["restored_functions"] != 19
        or drv_mx25["surface"]["indirect_body_calls"] != 0
        or drv_mx25["production"]["production_routed"]
        or drv_mx25["identity"]["embedded_third_party_definitions"]
    ):
        raise ClosureError("MX25U25643G driver third-party/provider boundary changed")
    notif_provider = ui_msg_notif_list["provider_boundary"]
    if (
        notif_provider["easylogger_calls"] != 205
        or notif_provider["lvgl_calls"] != 304
        or notif_provider["cmsis_freertos_calls"] != 6
        or notif_provider["iar_dlib_calls"] != 11
        or notif_provider["source_owned_heap_wrapper_calls"] != 8
        or notif_provider["first_party_calls"] != 65
        or ui_msg_notif_list["surface"]["restored_functions"] != 13
        or ui_msg_notif_list["surface"]["indirect_body_calls"] != 0
        or ui_msg_notif_list["production"]["production_routed"]
        or ui_msg_notif_list["identity"]["embedded_third_party_definitions"]
    ):
        raise ClosureError("notification-list third-party/provider boundary changed")
    dashboard_provider = dashboard_main["provider_boundary"]
    if (
        dashboard_provider["easylogger_calls"] != 255
        or dashboard_provider["lvgl_calls"] != 146
        or dashboard_provider["cmsis_freertos_calls"] != 2
        or dashboard_provider["iar_dlib_calls"] != 7
        or dashboard_provider["first_party_calls"] != 109
        or dashboard_main["surface"]["restored_functions"] != 17
        or dashboard_main["surface"]["stored_interior_callback_pointers"] != 7
        or dashboard_main["surface"]["unaligned_word_pseudo_pointers"] != 6
        or dashboard_main["surface"]["indirect_body_calls"] != 0
        or dashboard_main["identity"]["embedded_third_party_definitions"]
    ):
        raise ClosureError("dashboard main-screen third-party/provider boundary changed")
    teleprompt_provider = teleprompt_ui["provider_boundary"]
    if (
        teleprompt_provider["easylogger_calls"] != 330
        or teleprompt_provider["lvgl_calls"] != 252
        or teleprompt_provider["iar_dlib_calls"] != 10
        or teleprompt_provider["first_party_calls"] != 132
        or teleprompt_ui["surface"]["restored_functions"] != 38
        or teleprompt_ui["surface"]["indirect_body_calls"] != 1
        or teleprompt_ui["surface"]["stored_interior_callback_targets"] != 2
        or teleprompt_ui["identity"]["embedded_third_party_definitions"]
    ):
        raise ClosureError("teleprompt UI third-party/provider boundary changed")
    em9305_dfu_provider = service_em9305_dfu["provider_boundary"]
    if (
        em9305_dfu_provider["easylogger_calls"] != 125
        or em9305_dfu_provider["source_owned_file_heap_calls"] != 18
        or em9305_dfu_provider["iar_dlib_calls"] != 4
        or em9305_dfu_provider["shared_nanopb_initializer_calls"] != 1
        or em9305_dfu_provider["first_party_calls"] != 4
        or em9305_dfu_provider["direct_em9305_packetcraft_calls"] != 0
        or service_em9305_dfu["surface"]["restored_functions"] != 1
        or service_em9305_dfu["identity"]["embedded_third_party_definitions"]
    ):
        raise ClosureError("EM9305 DFU-service third-party/provider boundary changed")
    tag_provider = conversate_tag_data["provider_boundary"]
    if (
        tag_provider["easylogger_calls"] != 140
        or tag_provider["source_owned_heap_wrapper_calls"] != 8
        or tag_provider["iar_dlib_calls"] != 7
        or tag_provider["nanopb_calls"] != 0
        or tag_provider["json_calls"] != 0
        or conversate_tag_data["surface"]["restored_functions"] != 3
        or conversate_tag_data["identity"]["embedded_third_party_definitions"]
    ):
        raise ClosureError("conversate tag-data third-party/provider boundary changed")
    layout4_provider = dashboard_layout4["provider_boundary"]
    if (
        layout4_provider["easylogger_calls"] != 60
        or layout4_provider["lvgl_calls"] != 122
        or layout4_provider["iar_dlib_calls"] != 14
        or layout4_provider["ambiqsuite_calls"] != 3
        or layout4_provider["first_party_calls"] != 31
        or dashboard_layout4["surface"]["restored_functions"] != 20
        or dashboard_layout4["surface"]["indirect_body_calls"] != 0
        or dashboard_layout4["surface"]["stored_function_entry_pointers"] != 11
        or dashboard_layout4["identity"]["embedded_third_party_definitions"]
    ):
        raise ClosureError("dashboard layout-4 third-party/provider boundary changed")
    dashboard_ext_provider = dashboard_ext["provider_boundary"]
    if (
        dashboard_ext_provider["easylogger_calls"] != 220
        or dashboard_ext_provider["iar_dlib_calls"] != 18
        or dashboard_ext_provider["source_owned_file_runtime_calls"] != 16
        or dashboard_ext_provider["nanopb_calls"] != 5
        or dashboard_ext_provider["freertos_calls"] != 3
        or dashboard_ext_provider["first_party_calls"] != 29
        or dashboard_ext["surface"]["restored_functions"] != 10
        or dashboard_ext["surface"]["indirect_body_calls"] != 0
        or dashboard_ext["identity"]["embedded_third_party_definitions"]
    ):
        raise ClosureError("dashboard extension third-party/provider boundary changed")
    dashboard_data_provider = dashboard_data_process["provider_boundary"]
    if (
        dashboard_data_provider["easylogger_calls"] != 170
        or dashboard_data_provider["iar_dlib_calls"] != 32
        or dashboard_data_provider["nanopb_calls"] != 19
        or dashboard_data_provider["cmsis_freertos_calls"] != 4
        or dashboard_data_provider["freertos_calls"] != 1
        or dashboard_data_provider["first_party_calls"] != 29
        or dashboard_data_process["surface"]["restored_functions"] != 4
        or dashboard_data_process["surface"]["indirect_body_calls"] != 0
        or dashboard_data_process["identity"]["embedded_third_party_definitions"]
    ):
        raise ClosureError("dashboard data-process third-party/provider boundary changed")
    display_manager_provider = displaydrv_manager["provider_boundary"]
    if (
        display_manager_provider["easylogger_calls"] != 125
        or display_manager_provider["cmsis_freertos_calls"] != 20
        or display_manager_provider["iar_dlib_calls"] != 11
        or display_manager_provider["first_party_uled_display_calls"] != 22
        or display_manager_provider["direct_lvgl_calls"] != 0
        or display_manager_provider["direct_ambiqsuite_calls"] != 0
        or displaydrv_manager["surface"]["restored_functions"] != 7
        or displaydrv_manager["surface"]["indirect_body_calls"] != 0
        or displaydrv_manager["identity"]["embedded_third_party_definitions"]
    ):
        raise ClosureError("display-driver manager third-party/provider boundary changed")
    npmx_provider = npmx_main_driver["provider_boundary"]
    if (
        npmx_provider["npmx_calls"] != 72
        or npmx_provider["npmx_entry_targets"] != 42
        or npmx_provider["npmx_selected_commit"]
        != "e1aaec53f456887a7d7b80d82f684d1ac3cb08c8"
        or npmx_provider["npmx_adjacent_excluded_commit"]
        != "53de7af4394382e1a21008eaa18ed9e5e1809504"
        or not npmx_provider["exact_public_candidate"]
        or npmx_provider["exact_private_checkout_proven"]
        or npmx_main_driver["production"]["production_routed"]
    ):
        raise ClosureError("Nordic nPMX exact-public-candidate boundary changed")
    if (
        liblc3["selected"]["commit"]
        != "96a3af0beb5487aca3b98a4b992a539a1f6d80d1"
        or liblc3["stock"]["public_entries"] != 4
        or liblc3["stock"]["direct_public_entry_calls"] != 5
        or not liblc3["compatibility"]["sns_flt_max_present"]
        or not liblc3["compatibility"]["pre_ltpf_bypass_layout"]
        or liblc3["snapshot"]["files"] != 38
        or liblc3["selected"]["exact_public_commit_recoverable"]
        or liblc3["production"]["production_routed"]
    ):
        raise ClosureError("Google liblc3 source/version boundary changed")
    service_audio_provider = service_audio["provider_boundary"]
    if (
        service_audio_provider["liblc3_calls"] != 5
        or service_audio_provider["liblc3_commit"]
        != "96a3af0beb5487aca3b98a4b992a539a1f6d80d1"
        or service_audio["surface"]["linked_functions"] != 14
        or service_audio["surface"]["indirect_body_calls"] != 1
        or service_audio["surface"]["resolved_indirect_body_calls"] != 1
        or service_audio["surface"]["registered_external_callback_entries"] != 2
        or service_audio["identity"]["embedded_third_party_definitions"]
    ):
        raise ClosureError("service_audio liblc3 consumer boundary changed")
    goodix = util_error["goodix_source_lineage"]
    if (
        goodix["exact_source_snapshot_version"] != "1.7.0"
        or goodix["stock_table_rows"] != 43
        or goodix["first_located_incompatible_version"] != "2.0.1"
        or not goodix["official_2_0_2_confirms_incompatible_blob"]
        or goodix["exact_generating_commit"] is not None
        or util_error["identity"]["goodix_ble_stack_linkage_proven"]
    ):
        raise ClosureError("Goodix copied app_error source identification changed")
    if display["display_port"]["functional_closure_percent"] != 100:
        raise ClosureError("LVGL display-port functional gap reopened")
    if freetype["allocator"]["lifecycle"]["FT_Done_FreeType"]["stock_entry_recoverable"]:
        raise ClosureError("FreeType destructor topology changed; ledger requires review")
    third_party_bytes = accounting["opaque_origin_lower_bounds"]["third_party_path_anchored"]
    if third_party_bytes != 122_876:
        raise ClosureError("third-party path-anchored byte census changed")

    selected = sum(row["selected_source_commit"] is not None for row in rows)
    exact_historical = sum(row["historical_generating_commit"] is not None for row in rows)
    closed = sum(row["functional_status"] == "closed" for row in rows)
    gated = len(rows) - closed
    return {
        "schema_version": 1,
        "analysis_mode": "read-only; no signing, flashing, erase, or hardware operation",
        "dependency_census": {
            "families": len(rows),
            "selected_source_commit_or_baseline": selected,
            "historical_generating_commit_recoverable": exact_historical,
            "linked_functional_status_closed": closed,
            "bounded_waiting_external_gate": gated,
            "locally_actionable_bounded_functional_gaps": 0,
        },
        "cross_checks": {
            "third_party_path_anchored_opaque_bytes": third_party_bytes,
            "cordio_unclassified_reusable_paths": 0,
            "cordio_copied_gatt_profile_source_owned_functions": 6,
            "ambiqsuite_cordio_application_framework_paths": 9,
            "ambiqsuite_cordio_application_framework_anchored_functions": 50,
            "ambiqsuite_cordio_application_framework_anchored_bytes": 29110,
            "ambiqsuite_copied_ancc_profile_source_derived_functions": 12,
            "ambiqsuite_amota_profile_skeleton_derived_functions": 4,
            "ambiqsuite_apollo510_stock_sleep_wfi_count": 2,
            "ambiqsuite_apollo510_sdk_5_0_sleep_wfi_count": 1,
            "ambiqsuite_apollo510_sdk_5_1_sleep_wfi_count": 2,
            "ambiqsuite_apollo510_private_generating_commit_recoverable": False,
            "gx8002b_cmsis_core_linked_definitions": 3,
            "gx8002b_ambiqsuite_i2s_calls": 13,
            "gx8002b_ambiqsuite_i2s_apis": 12,
            "gx8002b_nationalchip_lvp_code_linked": False,
            "pdm_production_ambiqsuite_calls": 13,
            "pdm_production_ambiqsuite_apis": 12,
            "pdm_production_selected_commit": "5efc0228528a8adce5eae0d226fac85d2551eb3b",
            "pdm_production_source_git_blob": "23a440bfd6121509b0586f0afe1990fcf59dd8fb",
            "pdm_production_cmsis_core_linked_definitions": 3,
            "pdm_production_routed": False,
            "pdm_ambiqsuite_calls": 19,
            "pdm_ambiqsuite_apis": 14,
            "pdm_selected_commit": "5efc0228528a8adce5eae0d226fac85d2551eb3b",
            "pdm_source_git_blob": "23a440bfd6121509b0586f0afe1990fcf59dd8fb",
            "pdm_cmsis_core_linked_definitions": 3,
            "pdm_stored_irq_entry_pointers": 1,
            "pdm_routed": False,
            "service_ancc_cmsis_freertos_mutex_calls": 17,
            "service_ancc_direct_ambiqsuite_ancc_calls": 0,
            "service_ancc_embedded_ambiqsuite_ancc_definitions": 0,
            "service_ancc_stored_interior_callback_pointers": 3,
            "service_ancc_routed": False,
            "als_cmsis_freertos_delay_calls": 1,
            "als_opt3007_adapter_calls": 6,
            "als_public_opt3007_software_commit": None,
            "als_bounded_first_party_indirect_calls": 1,
            "als_embedded_third_party_definitions": 0,
            "als_routed": True,
            "thread_ble_production_cmsis_freertos_calls": 15,
            "thread_ble_production_freertos_assert_calls": 3,
            "thread_ble_production_easylogger_calls": 106,
            "thread_ble_production_stored_function_pointers": 1,
            "thread_ble_production_strict_interior_ingress": 0,
            "thread_ble_production_embedded_third_party_definitions": 0,
            "thread_ble_production_historical_commit": None,
            "thread_ble_production_routed": False,
            "pt_protocol_easylogger_calls": 1280,
            "pt_protocol_cmsis_freertos_calls": 7,
            "pt_protocol_freertos_kernel_calls": 1,
            "pt_protocol_iar_runtime_calls": 41,
            "pt_protocol_mpaland_printf_calls": 1,
            "pt_protocol_bounded_internal_dispatches": 1,
            "pt_protocol_stored_function_pointers": 66,
            "pt_protocol_embedded_third_party_definitions": 0,
            "pt_protocol_historical_commit": None,
            "pt_protocol_routed": False,
            "ui_quicklist_page_lvgl_calls": 415,
            "ui_quicklist_page_easylogger_calls": 465,
            "ui_quicklist_page_cmsis_freertos_calls": 5,
            "ui_quicklist_page_iar_runtime_calls": 24,
            "ui_quicklist_page_stored_function_pointers": 15,
            "ui_quicklist_page_embedded_third_party_definitions": 0,
            "ui_quicklist_page_historical_commit": None,
            "ui_quicklist_page_routed": False,
            "ui_widget_news_page_lvgl_calls": 508,
            "ui_widget_news_page_easylogger_calls": 565,
            "ui_widget_news_page_cmsis_freertos_calls": 8,
            "ui_widget_news_page_runtime_calls": 36,
            "ui_widget_news_page_stored_function_pointers": 12,
            "ui_widget_news_page_embedded_third_party_definitions": 0,
            "ui_widget_news_page_historical_commit": None,
            "ui_widget_news_page_routed": False,
            "ui_stock_page_lvgl_calls": 454,
            "ui_stock_page_easylogger_calls": 355,
            "ui_stock_page_cmsis_freertos_calls": 0,
            "ui_stock_page_runtime_calls": 10,
            "ui_stock_page_stored_function_pointers": 2,
            "ui_stock_page_embedded_third_party_definitions": 0,
            "ui_stock_page_historical_commit": None,
            "ui_stock_page_routed": False,
            "navigation_ui_lvgl_calls": 702,
            "navigation_ui_easylogger_calls": 1245,
            "navigation_ui_cmsis_freertos_calls": 20,
            "navigation_ui_runtime_calls": 67,
            "navigation_ui_nanopb_calls": 22,
            "navigation_ui_mpaland_printf_calls": 2,
            "navigation_ui_stored_function_start_pointers": 14,
            "navigation_ui_stored_interior_entry_pointers": 5,
            "navigation_ui_embedded_third_party_definitions": 0,
            "navigation_ui_historical_commit": None,
            "navigation_ui_routed": False,
            "menu_page_lvgl_calls": 124,
            "menu_page_easylogger_calls": 445,
            "menu_page_cmsis_freertos_calls": 3,
            "menu_page_runtime_calls": 24,
            "menu_page_nanopb_calls": 15,
            "menu_page_stored_function_start_pointers": 8,
            "menu_page_stored_interior_entry_pointers": 1,
            "menu_page_embedded_third_party_definitions": 0,
            "menu_page_historical_commit": None,
            "menu_page_routed": False,
            "ui_health_page_lvgl_calls": 437,
            "ui_health_page_easylogger_calls": 55,
            "ui_health_page_cmsis_freertos_calls": 0,
            "ui_health_page_runtime_calls": 4,
            "ui_health_page_mpaland_printf_calls": 36,
            "ui_health_page_stored_function_pointers": 2,
            "ui_health_page_embedded_third_party_definitions": 0,
            "ui_health_page_historical_commit": None,
            "ui_health_page_routed": True,
            "ring_service_easylogger_calls": 76,
            "ring_service_cmsis_freertos_calls": 2,
            "ring_service_runtime_calls": 8,
            "ring_service_nanopb_calls": 1,
            "ring_service_cordio_calls": 0,
            "ring_service_stored_function_pointers": 2,
            "ring_service_embedded_third_party_definitions": 0,
            "ring_service_historical_commit": None,
            "ring_service_routed": False,
            "service_input_manager_easylogger_calls": 85,
            "service_input_manager_cmsis_freertos_calls": 2,
            "service_input_manager_runtime_calls": 2,
            "service_input_manager_nanopb_calls": 2,
            "service_input_manager_bounded_abs_calls": 1,
            "service_input_manager_stored_function_pointers": 2,
            "service_input_manager_embedded_third_party_definitions": 0,
            "service_input_manager_historical_commit": None,
            "service_input_manager_routed": False,
            "ui_calendar_page_lvgl_calls": 533,
            "ui_calendar_page_easylogger_calls": 85,
            "ui_calendar_page_cmsis_freertos_calls": 34,
            "ui_calendar_page_runtime_calls": 12,
            "ui_calendar_page_stored_function_pointers": 3,
            "ui_calendar_page_embedded_third_party_definitions": 0,
            "ui_calendar_page_historical_commit": None,
            "ui_calendar_page_routed": False,
            "ota_transport_easylogger_calls": 60,
            "ota_transport_runtime_calls": 8,
            "ota_transport_ota_service_calls": 5,
            "ota_transport_crc16_calls": 4,
            "ota_transport_heap_wrapper_calls": 6,
            "ota_transport_registered_callback_calls": 4,
            "ota_transport_indirect_body_calls": 4,
            "ota_transport_embedded_third_party_definitions": 0,
            "ota_transport_historical_commit": None,
            "ota_transport_routed": True,
            "efs_transport_easylogger_calls": 60,
            "efs_transport_cmsis_freertos_calls": 1,
            "efs_transport_runtime_calls": 8,
            "efs_transport_efs_service_calls": 5,
            "efs_transport_crc16_calls": 4,
            "efs_transport_heap_wrapper_calls": 6,
            "efs_transport_registered_callback_calls": 4,
            "efs_transport_indirect_body_calls": 4,
            "efs_transport_embedded_third_party_definitions": 0,
            "efs_transport_historical_commit": None,
            "efs_transport_routed": True,
            "evenhub_loading_page_lvgl_calls": 36,
            "evenhub_loading_page_easylogger_calls": 85,
            "evenhub_loading_page_runtime_calls": 2,
            "evenhub_loading_page_stored_function_pointers": 2,
            "evenhub_loading_page_embedded_third_party_definitions": 0,
            "evenhub_loading_page_historical_commit": None,
            "evenhub_loading_page_routed": False,
            "dashboard_watchface_layout1_lvgl_calls": 154,
            "dashboard_watchface_layout1_easylogger_calls": 20,
            "dashboard_watchface_layout1_iar_dlib_calls": 13,
            "dashboard_watchface_layout1_mpaland_printf_calls": 10,
            "dashboard_watchface_layout1_bounded_local_callback_targets": 2,
            "dashboard_watchface_layout1_embedded_third_party_definitions": 0,
            "dashboard_watchface_layout1_private_commit_recoverable": False,
            "dashboard_watchface_layout1_routed": False,
            "teleprompt_fsm_easylogger_calls": 140,
            "teleprompt_fsm_iar_runtime_calls": 3,
            "teleprompt_fsm_lvgl_calls": 1,
            "teleprompt_fsm_nanopb_calls": 2,
            "teleprompt_fsm_bounded_handler_table_entries": 9,
            "teleprompt_fsm_embedded_third_party_definitions": 0,
            "teleprompt_fsm_historical_commit": None,
            "teleprompt_fsm_routed": False,
            "health_data_manager_easylogger_calls": 120,
            "health_data_manager_iar_runtime_calls": 6,
            "health_data_manager_closed_health_lock_calls": 10,
            "health_data_manager_direct_cmsis_freertos_calls": 0,
            "health_data_manager_embedded_third_party_definitions": 0,
            "health_data_manager_historical_commit": None,
            "health_data_manager_routed": True,
            "evenhub_main_easylogger_calls": 120,
            "evenhub_main_iar_runtime_calls": 6,
            "evenhub_main_lvgl_calls": 2,
            "evenhub_main_cmsis_freertos_calls": 2,
            "evenhub_main_nanopb_calls": 3,
            "evenhub_main_heap_wrapper_calls": 2,
            "evenhub_main_first_party_calls": 45,
            "evenhub_main_raw_noncode_pseudo_bl_sites": 1,
            "evenhub_main_raw_unaligned_interior_word_collisions": 1,
            "evenhub_main_embedded_third_party_definitions": 0,
            "evenhub_main_historical_commit": None,
            "evenhub_main_routed": False,
            "translate_easylogger_calls": 105,
            "translate_iar_runtime_calls": 7,
            "translate_lvgl_calls": 2,
            "translate_cmsis_freertos_calls": 7,
            "translate_nanopb_calls": 3,
            "translate_first_party_calls": 32,
            "translate_embedded_third_party_definitions": 0,
            "translate_historical_commit": None,
            "translate_routed": False,
            "teleprompt_controller_easylogger_calls": 90,
            "teleprompt_controller_iar_runtime_calls": 4,
            "teleprompt_controller_lvgl_calls": 2,
            "teleprompt_controller_cmsis_freertos_calls": 7,
            "teleprompt_controller_nanopb_calls": 3,
            "teleprompt_controller_first_party_calls": 43,
            "teleprompt_controller_embedded_third_party_definitions": 0,
            "teleprompt_controller_historical_commit": None,
            "teleprompt_controller_routed": False,
            "conversate_comm_data_easylogger_calls": 60,
            "conversate_comm_data_iar_dlib_calls": 11,
            "conversate_comm_data_lvgl_calls": 1,
            "conversate_comm_data_embedded_third_party_definitions": 0,
            "conversate_comm_data_historical_commit": None,
            "conversate_comm_data_routed": False,
            "conversate_controller_easylogger_calls": 80,
            "conversate_controller_iar_dlib_calls": 4,
            "conversate_controller_cmsis_freertos_calls": 7,
            "conversate_controller_lvgl_calls": 2,
            "conversate_controller_nanopb_calls": 3,
            "conversate_controller_source_owned_eabi_calls": 1,
            "conversate_controller_cmbacktrace_calls": 1,
            "conversate_controller_first_party_calls": 41,
            "conversate_controller_cmbacktrace_selected_compatibility_commit": "73714489f9d8af130aacb515586b397b604a5768",
            "conversate_controller_cmbacktrace_exact_historical_commit": None,
            "conversate_controller_embedded_third_party_definitions": 0,
            "conversate_controller_routed": False,
            "conversate_ui_main_page_easylogger_calls": 130,
            "conversate_ui_main_page_lvgl_calls": 98,
            "conversate_ui_main_page_iar_dlib_calls": 2,
            "conversate_ui_main_page_first_party_calls": 53,
            "conversate_ui_main_page_stored_strict_interior_entries": 1,
            "conversate_ui_main_page_embedded_third_party_definitions": 0,
            "conversate_ui_main_page_historical_commit": None,
            "conversate_ui_main_page_routed": False,
            "service_universal_setting_easylogger_calls": 75,
            "service_universal_setting_iar_dlib_calls": 17,
            "service_universal_setting_source_owned_crc_calls": 3,
            "service_universal_setting_closed_kv_calls": 3,
            "service_universal_setting_first_party_calls": 5,
            "service_universal_setting_embedded_third_party_definitions": 0,
            "service_universal_setting_historical_commit": None,
            "service_universal_setting_routed": False,
            "common_image_container_easylogger_calls": 70,
            "common_image_container_lvgl_calls": 3,
            "common_image_container_source_owned_heap_calls": 3,
            "common_image_container_source_owned_cache_calls": 1,
            "common_image_container_bounded_abs_calls": 1,
            "common_image_container_first_party_calls": 2,
            "common_image_container_embedded_third_party_definitions": 0,
            "common_image_container_historical_commit": None,
            "common_image_container_routed": False,
            "dashboard_watchface_layout2_easylogger_calls": 20,
            "dashboard_watchface_layout2_lvgl_calls": 104,
            "dashboard_watchface_layout2_iar_dlib_calls": 9,
            "dashboard_watchface_layout2_mpaland_printf_calls": 5,
            "dashboard_watchface_layout2_first_party_calls": 43,
            "dashboard_watchface_layout2_embedded_third_party_definitions": 0,
            "dashboard_watchface_layout2_historical_commit": None,
            "dashboard_watchface_layout2_routed": False,
            "dashboard_watchface_layout3_easylogger_calls": 20,
            "dashboard_watchface_layout3_lvgl_calls": 125,
            "dashboard_watchface_layout3_iar_dlib_calls": 10,
            "dashboard_watchface_layout3_mpaland_printf_calls": 2,
            "dashboard_watchface_layout3_first_party_calls": 16,
            "dashboard_watchface_layout3_raw_overlapping_pseudo_bl_sites": 5,
            "dashboard_watchface_layout3_embedded_third_party_definitions": 0,
            "dashboard_watchface_layout3_historical_commit": None,
            "dashboard_watchface_layout3_routed": False,
            "thread_ring_easylogger_calls": 110,
            "thread_ring_cmsis_freertos_calls": 10,
            "thread_ring_freertos_assert_calls": 2,
            "thread_ring_iar_dlib_calls": 2,
            "thread_ring_source_owned_heap_wrapper_calls": 3,
            "thread_ring_closed_ring_service_calls": 13,
            "thread_ring_event_loop_calls": 16,
            "thread_ring_other_first_party_calls": 6,
            "thread_ring_restored_functions": 12,
            "thread_ring_stored_entry_pointers": 8,
            "thread_ring_embedded_third_party_definitions": 0,
            "thread_ring_historical_commit": None,
            "thread_ring_routed": True,
            "sensor_hub_easylogger_calls": 130,
            "sensor_hub_lvgl_calls": 69,
            "sensor_hub_cmsis_freertos_calls": 9,
            "sensor_hub_closed_first_party_calls": 36,
            "sensor_hub_translation_lookup_calls": 8,
            "sensor_hub_nanopb_calls": 1,
            "sensor_hub_bounded_open_first_party_calls": 1,
            "sensor_hub_direct_freertos_calls": 0,
            "sensor_hub_restored_functions": 26,
            "sensor_hub_stored_entry_pointers": 3,
            "sensor_hub_embedded_third_party_definitions": 0,
            "sensor_hub_embedded_sensor_fusion_library": None,
            "sensor_hub_routed": True,
            "sensor_hub_hardware_validation": "blocked_unavailable_physical_evidence",
            "fw_event_loop_easylogger_calls": 80,
            "fw_event_loop_cmsis_freertos_calls": 20,
            "fw_event_loop_freertos_critical_port_calls": 4,
            "fw_event_loop_bounded_first_party_indirect_calls": 1,
            "fw_event_loop_restored_functions": 1,
            "fw_event_loop_embedded_third_party_definitions": 0,
            "fw_event_loop_historical_commit": None,
            "fw_event_loop_routed": True,
            "fw_event_loop_source_routed_functions": 6,
            "ring_connect_policy_easylogger_calls": 95,
            "ring_connect_policy_cmsis_freertos_calls": 1,
            "ring_connect_policy_closed_event_loop_calls": 10,
            "ring_connect_policy_closed_nanopb_facade_calls": 1,
            "ring_connect_policy_closed_ble_central_calls": 1,
            "ring_connect_policy_direct_cordio_calls": 0,
            "ring_connect_policy_direct_nanopb_calls": 0,
            "ring_connect_policy_restored_functions": 4,
            "ring_connect_policy_stored_entry_pointers": 1,
            "ring_connect_policy_embedded_third_party_definitions": 0,
            "ring_connect_policy_historical_commit": None,
            "ring_connect_policy_routed": True,
            "system_close_easylogger_calls": 130,
            "system_close_lvgl_calls": 99,
            "system_close_iar_dlib_calls": 5,
            "system_close_first_party_calls": 37,
            "system_close_direct_cmsis_freertos_calls": 0,
            "system_close_restored_functions": 15,
            "system_close_stored_entry_pointers": 3,
            "system_close_embedded_third_party_definitions": 0,
            "system_close_historical_commit": None,
            "system_close_routed": True,
            "iar_float_exponent_functions": 3,
            "iar_float_exponent_bytes": 268,
            "iar_float_exponent_exact_stock_reproduction": True,
            "iar_float_exponent_apple_routed": True,
            "iar_float_exponent_linux_pending": True,
            "iar_float_exponent_exact_release": None,
            "translate_ui_easylogger_calls": 175,
            "translate_ui_lvgl_calls": 125,
            "translate_ui_iar_dlib_calls": 10,
            "translate_ui_cmsis_freertos_calls": 2,
            "translate_ui_first_party_calls": 34,
            "translate_ui_bounded_first_party_indirect_calls": 1,
            "translate_ui_restored_functions": 22,
            "translate_ui_stored_entry_pointers": 13,
            "translate_ui_embedded_third_party_definitions": 0,
            "translate_ui_historical_commit": None,
            "translate_ui_routed": False,
            "service_db_api_flashdb_calls": 2,
            "service_db_api_cmsis_freertos_calls": 7,
            "service_db_api_embedded_third_party_definitions": 0,
            "service_db_api_unsafe_zero_on_failure_fal_seam": True,
            "ui_even_ai_lvgl_calls": 182,
            "ui_even_ai_cmsis_freertos_calls": 1,
            "ui_even_ai_embedded_third_party_definitions": 0,
            "service_time_iar_dlib_calls": 8,
            "service_time_direct_cmsis_freertos_calls": 0,
            "service_time_embedded_third_party_definitions": 0,
            "thread_audio_cmsis_freertos_calls": 20,
            "thread_audio_cmsis_wrapper_count": 14,
            "thread_audio_iar_dlib_calls": 1,
            "thread_audio_closed_codec_gx8002b_calls": 19,
            "thread_audio_embedded_third_party_definitions": 0,
            "thread_audio_nationalchip_lvp_code_linked": False,
            "compress_log_core_iar_dlib_calls": 13,
            "compress_log_core_easylogger_control_output_calls": 30,
            "compress_log_core_freertos_kernel_port_calls": 14,
            "compress_log_core_cmsis_freertos_calls": 2,
            "compress_log_core_private_hook_is_upstream_easylogger": False,
            "compress_log_core_embedded_third_party_definitions": 0,
            "compress_log_port_easylogger_control_output_calls": 24,
            "compress_log_port_closed_core_calls": 6,
            "compress_log_port_iar_dlib_calls": 2,
            "compress_log_port_source_owned_file_runtime_calls": 18,
            "compress_log_port_source_owned_delayed_callback_calls": 3,
            "compress_log_port_embedded_third_party_definitions": 0,
            "file_runtime_cmsis_freertos_calls": 36,
            "file_runtime_littlefs_backend_adapter_calls": 14,
            "file_runtime_tlsf_calls": 3,
            "file_runtime_iar_dlib_calls": 6,
            "file_runtime_embedded_third_party_definitions": 0,
            "file_runtime_production_source_owned_functions": 18,
            "service_algo_iar_dlib_memory_math_calls": 10,
            "service_algo_source_owned_unsigned_64_division_calls": 6,
            "service_algo_nationalchip_lvp_code_linked": False,
            "service_algo_embedded_third_party_definitions": 0,
            "service_algo_short_aligned_input_hazard": True,
            "uart_sync_cmsis_freertos_calls": 8,
            "uart_sync_tinyframe_and_sync_framework_calls": 4,
            "uart_sync_g2_uart_adapter_calls": 5,
            "uart_sync_bounded_indirect_initializer_calls": 1,
            "uart_sync_embedded_third_party_definitions": 0,
            "service_nvdb_flashdb_core_calls": 4,
            "service_nvdb_g2_database_adapter_calls": 9,
            "service_nvdb_iar_dlib_calls": 2,
            "service_nvdb_embedded_third_party_definitions": 0,
            "service_nvdb_wholesale_default_reset_on_magic_mismatch": True,
            "service_nvdb_stock_fal_zero_on_failure_hazard": True,
            "production_mic_iar_dlib_memory_calls": 5,
            "production_mic_g2_codec_pdm_pcm_calls": 24,
            "production_mic_direct_cmsis_freertos_calls": 0,
            "production_mic_nationalchip_lvp_code_linked": False,
            "production_mic_embedded_third_party_definitions": 0,
            "production_mic_restored_stereo_callbacks": 1,
            "service_audio_manager_iar_dlib_memset_calls": 1,
            "service_audio_manager_direct_cmsis_freertos_calls": 0,
            "service_audio_manager_g2_audio_hardware_and_power_calls": 11,
            "service_audio_manager_g2_common_data_transport_calls": 1,
            "service_audio_manager_embedded_third_party_definitions": 0,
            "service_audio_manager_restored_functions": 2,
            "service_kvdb_flashdb_core_calls": 4,
            "service_kvdb_g2_database_adapter_calls": 12,
            "service_kvdb_closed_migration_target_entries": 11,
            "service_kvdb_embedded_third_party_definitions": 0,
            "service_kvdb_boot_count_startup_value": 0,
            "service_kvdb_boot_count_lifecycle_resolved": True,
            "ux_battery_sync_easylogger_calls": 45,
            "ux_battery_sync_direct_cmsis_freertos_calls": 0,
            "ux_battery_sync_g2_charger_common_calls": 4,
            "ux_battery_sync_g2_ring_battery_calls": 6,
            "ux_battery_sync_embedded_third_party_definitions": 0,
            "ux_battery_sync_service_record_id": 0x105,
            "cb_ring_battery_easylogger_calls": 5,
            "cb_ring_battery_direct_cmsis_freertos_calls": 0,
            "cb_ring_battery_generic_callback_manager_calls": 4,
            "cb_ring_battery_embedded_third_party_definitions": 0,
            "cb_ring_battery_restored_functions": 4,
            "callback_facades_easylogger_calls": 20,
            "callback_facades_direct_cmsis_freertos_calls": 0,
            "callback_facades_generic_callback_manager_calls": 10,
            "callback_facades_embedded_third_party_definitions": 0,
            "callback_facades_restored_functions": 6,
            "callback_manager_easylogger_calls": 70,
            "callback_manager_source_owned_heap_wrapper_calls": 2,
            "callback_manager_direct_cmsis_freertos_calls": 0,
            "callback_manager_bounded_registered_callback_sites": 1,
            "callback_manager_embedded_third_party_definitions": 0,
            "callback_manager_restored_functions": 1,
            "silent_mode_easylogger_calls": 70,
            "silent_mode_lvgl_calls": 70,
            "silent_mode_freertos_vtaskdelay_calls": 1,
            "silent_mode_iar_memset_calls": 1,
            "silent_mode_embedded_third_party_definitions": 0,
            "silent_mode_restored_functions": 3,
            "onboarding_data_manager_easylogger_calls": 35,
            "onboarding_data_manager_cmsis_freertos_calls": 3,
            "onboarding_data_manager_iar_memset_calls": 3,
            "onboarding_data_manager_closed_kvdb_calls": 4,
            "onboarding_data_manager_closed_protobuf_calls": 1,
            "onboarding_data_manager_embedded_third_party_definitions": 0,
            "onboarding_data_manager_strict_interior_code_ingress": 0,
            "onboarding_controller_easylogger_calls": 165,
            "onboarding_controller_lvgl_calls": 32,
            "onboarding_controller_cmsis_freertos_calls": 1,
            "onboarding_controller_iar_memset_calls": 2,
            "onboarding_controller_closed_data_manager_calls": 5,
            "onboarding_controller_embedded_third_party_definitions": 0,
            "onboarding_controller_restored_functions": 3,
            "onboarding_main_page_lvgl_calls": 264,
            "onboarding_main_page_easylogger_calls": 45,
            "onboarding_main_page_cmsis_freertos_calls": 23,
            "onboarding_main_page_iar_dlib_calls": 17,
            "onboarding_main_page_mpaland_printf_calls": 4,
            "onboarding_main_page_embedded_third_party_definitions": 0,
            "onboarding_main_page_restored_functions": 15,
            "onboarding_stock_page_lvgl_calls": 447,
            "onboarding_stock_page_easylogger_calls": 110,
            "onboarding_stock_page_cmsis_freertos_calls": 2,
            "onboarding_stock_page_iar_dlib_calls": 5,
            "onboarding_stock_page_first_party_calls": 33,
            "onboarding_stock_page_embedded_third_party_definitions": 0,
            "onboarding_stock_page_restored_functions": 0,
            "onboarding_news_page_lvgl_calls": 232,
            "onboarding_news_page_easylogger_calls": 160,
            "onboarding_news_page_cmsis_freertos_calls": 16,
            "onboarding_news_page_iar_dlib_calls": 15,
            "onboarding_news_page_source_owned_aeabi_calls": 1,
            "onboarding_news_page_closed_time_service_calls": 2,
            "onboarding_news_page_first_party_calls": 44,
            "onboarding_news_page_embedded_third_party_definitions": 0,
            "onboarding_news_page_raw_overlapping_pseudo_bl_sites": 2,
            "lvgl_font_manager_easylogger_calls": 125,
            "lvgl_font_manager_iar_dlib_calls": 2,
            "lvgl_font_manager_g2_mspi_lock_calls": 2,
            "lvgl_font_manager_source_owned_heap_wrapper_calls": 9,
            "lvgl_font_manager_lvgl_freetype_adapter_calls": 2,
            "lvgl_font_manager_freetype_version": "2.9.1",
            "lvgl_font_manager_freetype_commit": "86bc8a95056c97a810986434a3f268cbe67f2902",
            "lvgl_font_manager_embedded_third_party_definitions": 0,
            "common_list_container_easylogger_calls": 310,
            "common_list_container_lvgl_calls": 91,
            "common_list_container_iar_dlib_calls": 3,
            "common_list_container_source_owned_heap_wrapper_calls": 6,
            "common_list_container_first_party_calls": 9,
            "common_list_container_selection_callback_calls": 2,
            "common_list_container_bounded_indirect_targets": 1,
            "common_list_container_embedded_third_party_definitions": 0,
            "common_text_container_easylogger_calls": 325,
            "common_text_container_lvgl_calls": 78,
            "common_text_container_iar_dlib_calls": 5,
            "common_text_container_source_owned_heap_wrapper_calls": 6,
            "common_text_container_first_party_calls": 12,
            "common_text_container_navigation_callback_calls": 4,
            "common_text_container_bounded_indirect_targets": 1,
            "common_text_container_restored_functions": 3,
            "common_text_container_embedded_third_party_definitions": 0,
            "evenhub_ui_easylogger_calls": 690,
            "evenhub_ui_lvgl_calls": 37,
            "evenhub_ui_nanopb_calls": 7,
            "evenhub_ui_iar_dlib_calls": 22,
            "evenhub_ui_source_owned_heap_wrapper_calls": 10,
            "evenhub_ui_closed_lz4_adapter_calls": 2,
            "evenhub_ui_first_party_calls": 55,
            "evenhub_ui_bounded_indirect_targets": 3,
            "evenhub_ui_restored_functions": 16,
            "evenhub_ui_embedded_third_party_definitions": 0,
            "evenhub_data_parser_easylogger_calls": 385,
            "evenhub_data_parser_nanopb_calls": 25,
            "evenhub_data_parser_cmsis_freertos_calls": 3,
            "evenhub_data_parser_lvgl_calls": 14,
            "evenhub_data_parser_iar_dlib_calls": 54,
            "evenhub_data_parser_source_owned_heap_wrapper_calls": 12,
            "evenhub_data_parser_first_party_calls": 48,
            "evenhub_data_parser_restored_functions": 2,
            "evenhub_data_parser_indirect_body_calls": 0,
            "evenhub_data_parser_embedded_third_party_definitions": 0,
            "sync_framework_easylogger_calls": 825,
            "sync_framework_cmsis_freertos_calls": 35,
            "sync_framework_freertos_kernel_calls": 4,
            "sync_framework_tinyframe_calls": 26,
            "sync_framework_ambiqsuite_calls": 2,
            "sync_framework_nanopb_calls": 1,
            "sync_framework_iar_dlib_calls": 17,
            "sync_framework_source_owned_heap_wrapper_calls": 86,
            "sync_framework_thread_pool_calls": 18,
            "sync_framework_first_party_calls": 36,
            "sync_framework_restored_functions": 20,
            "sync_framework_indirect_body_calls": 14,
            "sync_framework_embedded_third_party_definitions": 0,
            "sync_interface_api_easylogger_calls": 255,
            "sync_interface_api_cmsis_freertos_calls": 17,
            "sync_interface_api_freertos_assert_calls": 9,
            "sync_interface_api_iar_dlib_calls": 13,
            "sync_interface_api_source_owned_heap_wrapper_calls": 33,
            "sync_interface_api_first_party_calls": 6,
            "sync_interface_api_restored_functions": 0,
            "sync_interface_api_indirect_body_calls": 0,
            "sync_interface_api_embedded_third_party_definitions": 0,
            "display_thread_easylogger_calls": 310,
            "display_thread_cmsis_freertos_calls": 21,
            "display_thread_freertos_calls": 11,
            "display_thread_lvgl_calls": 12,
            "display_thread_iar_dlib_calls": 23,
            "display_thread_source_owned_runtime_calls": 5,
            "display_thread_first_party_calls": 140,
            "display_thread_restored_functions": 13,
            "display_thread_indirect_body_calls": 12,
            "display_thread_production_source_routed_functions": 2,
            "display_thread_embedded_third_party_definitions": 0,
            "drv_mx25_easylogger_calls": 230,
            "drv_mx25_ambiqsuite_calls": 31,
            "drv_mx25_cmsis_freertos_calls": 5,
            "drv_mx25_shared_nanopb_initializer_calls": 3,
            "drv_mx25_iar_dlib_calls": 7,
            "drv_mx25_source_owned_runtime_calls": 16,
            "drv_mx25_source_owned_delay_calls": 5,
            "drv_mx25_restored_functions": 19,
            "drv_mx25_indirect_body_calls": 0,
            "drv_mx25_production_routed": False,
            "drv_mx25_embedded_third_party_definitions": 0,
            "ui_msg_notif_list_easylogger_calls": 205,
            "ui_msg_notif_list_lvgl_calls": 304,
            "ui_msg_notif_list_cmsis_freertos_calls": 6,
            "ui_msg_notif_list_iar_dlib_calls": 11,
            "ui_msg_notif_list_source_owned_heap_wrapper_calls": 8,
            "ui_msg_notif_list_first_party_calls": 65,
            "ui_msg_notif_list_restored_functions": 13,
            "ui_msg_notif_list_indirect_body_calls": 0,
            "ui_msg_notif_list_production_routed": False,
            "ui_msg_notif_list_embedded_third_party_definitions": 0,
            "dashboard_main_easylogger_calls": 255,
            "dashboard_main_lvgl_calls": 146,
            "dashboard_main_cmsis_freertos_calls": 2,
            "dashboard_main_iar_dlib_calls": 7,
            "dashboard_main_first_party_calls": 109,
            "dashboard_main_restored_functions": 17,
            "dashboard_main_stored_interior_callbacks": 7,
            "dashboard_main_unaligned_word_pseudo_pointers": 6,
            "dashboard_main_embedded_third_party_definitions": 0,
            "teleprompt_ui_easylogger_calls": 330,
            "teleprompt_ui_lvgl_calls": 252,
            "teleprompt_ui_iar_dlib_calls": 10,
            "teleprompt_ui_first_party_calls": 132,
            "teleprompt_ui_restored_functions": 38,
            "teleprompt_ui_indirect_body_calls": 1,
            "teleprompt_ui_stored_interior_callback_targets": 2,
            "teleprompt_ui_embedded_third_party_definitions": 0,
            "service_em9305_dfu_easylogger_calls": 125,
            "service_em9305_dfu_source_owned_file_heap_calls": 18,
            "service_em9305_dfu_iar_dlib_calls": 4,
            "service_em9305_dfu_shared_nanopb_initializer_calls": 1,
            "service_em9305_dfu_first_party_calls": 4,
            "service_em9305_dfu_direct_em9305_packetcraft_calls": 0,
            "service_em9305_dfu_restored_functions": 1,
            "service_em9305_dfu_embedded_third_party_definitions": 0,
            "conversate_tag_data_easylogger_calls": 140,
            "conversate_tag_data_source_owned_heap_wrapper_calls": 8,
            "conversate_tag_data_iar_dlib_calls": 7,
            "conversate_tag_data_nanopb_calls": 0,
            "conversate_tag_data_json_calls": 0,
            "conversate_tag_data_restored_functions": 3,
            "conversate_tag_data_embedded_third_party_definitions": 0,
            "dashboard_layout4_easylogger_calls": 60,
            "dashboard_layout4_lvgl_calls": 122,
            "dashboard_layout4_iar_dlib_calls": 14,
            "dashboard_layout4_ambiqsuite_calls": 3,
            "dashboard_layout4_first_party_calls": 31,
            "dashboard_layout4_restored_functions": 20,
            "dashboard_layout4_indirect_body_calls": 0,
            "dashboard_layout4_stored_function_entry_pointers": 11,
            "dashboard_layout4_embedded_third_party_definitions": 0,
            "dashboard_ext_easylogger_calls": 220,
            "dashboard_ext_iar_dlib_calls": 18,
            "dashboard_ext_source_owned_file_runtime_calls": 16,
            "dashboard_ext_nanopb_calls": 5,
            "dashboard_ext_freertos_calls": 3,
            "dashboard_ext_first_party_calls": 29,
            "dashboard_ext_restored_functions": 10,
            "dashboard_ext_indirect_body_calls": 0,
            "dashboard_ext_embedded_third_party_definitions": 0,
            "dashboard_data_process_easylogger_calls": 170,
            "dashboard_data_process_iar_dlib_calls": 32,
            "dashboard_data_process_nanopb_calls": 19,
            "dashboard_data_process_cmsis_freertos_calls": 4,
            "dashboard_data_process_freertos_calls": 1,
            "dashboard_data_process_first_party_calls": 29,
            "dashboard_data_process_restored_functions": 4,
            "dashboard_data_process_indirect_body_calls": 0,
            "dashboard_data_process_embedded_third_party_definitions": 0,
            "displaydrv_manager_easylogger_calls": 125,
            "displaydrv_manager_cmsis_freertos_calls": 20,
            "displaydrv_manager_iar_dlib_calls": 11,
            "displaydrv_manager_first_party_uled_display_calls": 22,
            "displaydrv_manager_direct_lvgl_calls": 0,
            "displaydrv_manager_direct_ambiqsuite_calls": 0,
            "displaydrv_manager_restored_functions": 7,
            "displaydrv_manager_indirect_body_calls": 0,
            "displaydrv_manager_embedded_third_party_definitions": 0,
            "npmx_main_driver_calls": 72,
            "npmx_main_driver_entry_targets": 42,
            "npmx_selected_commit": "e1aaec53f456887a7d7b80d82f684d1ac3cb08c8",
            "npmx_adjacent_excluded_commit": "53de7af4394382e1a21008eaa18ed9e5e1809504",
            "npmx_exact_public_candidate": True,
            "npmx_exact_private_checkout_proven": False,
            "npmx_production_routed": False,
            "liblc3_selected_commit": "96a3af0beb5487aca3b98a4b992a539a1f6d80d1",
            "liblc3_public_entries": 4,
            "liblc3_direct_public_entry_calls": 5,
            "liblc3_sns_flt_max_present": True,
            "liblc3_pre_ltpf_bypass_layout": True,
            "liblc3_snapshot_files": 38,
            "liblc3_exact_public_commit_recoverable": False,
            "liblc3_production_routed": False,
            "service_audio_liblc3_calls": 5,
            "service_audio_linked_functions": 14,
            "service_audio_indirect_body_calls": 1,
            "service_audio_resolved_indirect_body_calls": 1,
            "service_audio_registered_callback_entries": 2,
            "service_audio_embedded_third_party_definitions": 0,
            "goodix_app_error_source_snapshot_version": "1.7.0",
            "goodix_app_error_stock_table_rows": 43,
            "goodix_app_error_first_incompatible_version": "2.0.1",
            "goodix_app_error_generating_commit_recoverable": False,
            "goodix_ble_stack_linkage_proven": False,
            "lvgl_display_port_source_owned_functions": display["display_port"]["source_owned_functions"],
            "lvgl_third_party_input_port_paths": display["input_boundary"]["third_party_ambiq_input_port_paths"],
            "freetype_done_freetype_stock_entry_recoverable": False,
        },
        "dependencies": rows,
        "next_frontier": {
            "third_party": "hardware, unavailable proprietary history/assets, or explicit production-admission decisions only",
            "locally_actionable": "first-party/project ownership recovery and conservative classification of unanchored functions",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ghidra-corpus", type=Path, required=True)
    parser.add_argument("--flash-plan", type=Path, default=ROOT / "build/source/flash-plan.json")
    parser.add_argument("--component-report", type=Path, default=ROOT / "components/apollo_main/core_overlay/build/build-report.json")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = analyze(args.ghidra_corpus, args.flash_plan, args.component_report)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        census = report["dependency_census"]
        print(
            "G2 third-party dependency closure: PASS "
            f"({census['families']} families; "
            f"{census['locally_actionable_bounded_functional_gaps']} local bounded gaps)"
        )
        print(f"selected source commits/baselines: {census['selected_source_commit_or_baseline']}")
        print("exact historical producing commits: 0 (source-identical/private history is unobservable)")
        print("hardware/flash operations: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
