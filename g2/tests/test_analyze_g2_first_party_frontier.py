import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).resolve().parents[1] / "tools/analyze_g2_first_party_frontier.py"
SPEC = importlib.util.spec_from_file_location("analyze_g2_first_party_frontier", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AnalyzeG2FirstPartyFrontierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        corpus = MODULE.DEFAULT_CORPUS
        if not (corpus / "SHA256SUMS").is_file():
            raise unittest.SkipTest("authenticated Apollo corpus unavailable")
        cls.report = MODULE.analyze()

    def test_exhaustive_path_partition(self) -> None:
        surface = self.report["surface"]
        self.assertEqual(surface["retained_first_party_paths"], 234)
        self.assertEqual(surface["closed_paths"], 234)
        self.assertEqual(surface["open_paths"], 0)
        self.assertEqual(len(self.report["inventory"]), 234)
        self.assertEqual(
            {item["status"] for item in self.report["inventory"]}, {"closed"}
        )

    def test_function_and_byte_partition(self) -> None:
        surface = self.report["surface"]
        self.assertEqual(surface["cross_status_anchored_functions"], 0)
        self.assertEqual(surface["closed_anchored_functions"], 1230)
        self.assertEqual(surface["open_anchored_functions"], 0)
        self.assertEqual(surface["anchored_functions"], 1230)
        self.assertEqual(surface["closed_anchored_body_bytes"], 485274)
        self.assertEqual(surface["open_anchored_body_bytes"], 0)
        self.assertEqual(surface["anchored_body_bytes"], 485274)

    def test_complete_object_totals_and_protocol_status(self) -> None:
        surface = self.report["surface"]
        self.assertEqual(surface["closed_manifest_body_bytes"], 814846)
        self.assertEqual(surface["closed_manifest_physical_bytes_known"], 885418)
        self.assertEqual(surface["closed_manifests_with_physical_bytes"], 232)
        self.assertEqual(surface["closed_manifests_without_physical_bytes"], 2)
        onboarding = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"app\gui\onboarding\onboarding_data_manager.c"
        )
        self.assertEqual(onboarding["status"], "closed")
        self.assertEqual((onboarding["anchored_functions"], onboarding["anchored_body_bytes"]), (5, 692))
        controller = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"app\gui\onboarding\onboarding.c"
        )
        self.assertEqual(controller["status"], "closed")
        self.assertEqual((controller["anchored_functions"], controller["anchored_body_bytes"]), (4, 2518))
        main_page = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"app\gui\onboarding\ui_onboarding_main_page.c"
        )
        self.assertEqual(main_page["status"], "closed")
        self.assertEqual((main_page["anchored_functions"], main_page["anchored_body_bytes"]), (7, 3648))
        stock_page = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"app\gui\onboarding\ui_onboarding_stock_page.c"
        )
        self.assertEqual(stock_page["status"], "closed")
        self.assertEqual((stock_page["anchored_functions"], stock_page["anchored_body_bytes"]), (10, 6624))
        news_page = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"app\gui\onboarding\ui_onboarding_news_page.c"
        )
        self.assertEqual(news_page["status"], "closed")
        self.assertEqual((news_page["anchored_functions"], news_page["anchored_body_bytes"]), (19, 7006))
        font_manager = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"app\gui\common\lvgl_font_manager.c"
        )
        self.assertEqual(font_manager["status"], "closed")
        self.assertEqual((font_manager["anchored_functions"], font_manager["anchored_body_bytes"]), (7, 2586))
        common_list = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"app\gui\EvenHub\common_list_container.c"
        )
        self.assertEqual(common_list["status"], "closed")
        self.assertEqual((common_list["anchored_functions"], common_list["anchored_body_bytes"]), (6, 6746))
        common_text = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"app\gui\EvenHub\common_text_container.c"
        )
        self.assertEqual(common_text["status"], "closed")
        self.assertEqual((common_text["anchored_functions"], common_text["anchored_body_bytes"]), (9, 4648))
        evenhub_ui = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"app\gui\EvenHub\evenhub_ui.c"
        )
        self.assertEqual(evenhub_ui["status"], "closed")
        self.assertEqual((evenhub_ui["anchored_functions"], evenhub_ui["anchored_body_bytes"]), (9, 3682))
        parser = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"app\gui\EvenHub\evenhub_data_parser.c"
        )
        self.assertEqual(parser["status"], "closed")
        self.assertEqual((parser["anchored_functions"], parser["anchored_body_bytes"]), (12, 8136))
        sync_framework = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"framework\sync\sync_framework.c"
        )
        self.assertEqual(sync_framework["status"], "closed")
        self.assertEqual((sync_framework["anchored_functions"], sync_framework["anchored_body_bytes"]), (23, 10954))
        sync_interface = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"framework\sync\sync_interface_api.c"
        )
        self.assertEqual(sync_interface["status"], "closed")
        self.assertEqual((sync_interface["anchored_functions"], sync_interface["anchored_body_bytes"]), (13, 6136))
        display_thread = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"framework\sync\display_thread.c"
        )
        self.assertEqual(display_thread["status"], "closed")
        self.assertEqual((display_thread["anchored_functions"], display_thread["anchored_body_bytes"]), (14, 8442))
        drv_mx25 = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"driver\flash\drv_mx25u25643g.c"
        )
        self.assertEqual(drv_mx25["status"], "closed")
        self.assertEqual((drv_mx25["anchored_functions"], drv_mx25["anchored_body_bytes"]), (21, 5420))
        notif_list = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"app\gui\MessageNotify\ui_msg_notif_list.c"
        )
        self.assertEqual(notif_list["status"], "closed")
        self.assertEqual((notif_list["anchored_functions"], notif_list["anchored_body_bytes"]), (18, 5392))
        dashboard_main = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"app\gui\dashboard\screens\ui_DashBaord_Main_Screen.c"
        )
        self.assertEqual(dashboard_main["status"], "closed")
        self.assertEqual((dashboard_main["anchored_functions"], dashboard_main["anchored_body_bytes"]), (8, 3458))
        teleprompt = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"app\gui\teleprompt\teleprompt_ui.c"
        )
        self.assertEqual(teleprompt["status"], "closed")
        self.assertEqual((teleprompt["anchored_functions"], teleprompt["anchored_body_bytes"]), (8, 3034))
        em9305_dfu = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"platform\service\DFU\service_em9305_dfu.c"
        )
        self.assertEqual(em9305_dfu["status"], "closed")
        self.assertEqual((em9305_dfu["anchored_functions"], em9305_dfu["anchored_body_bytes"]), (6, 2784))
        tag_data = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"app\gui\conversate\conversate_tag_data.c"
        )
        self.assertEqual(tag_data["status"], "closed")
        self.assertEqual((tag_data["anchored_functions"], tag_data["anchored_body_bytes"]), (9, 2562))
        layout4 = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"app\gui\dashboard\dashboard_watchface_layout4.c"
        )
        self.assertEqual(layout4["status"], "closed")
        self.assertEqual((layout4["anchored_functions"], layout4["anchored_body_bytes"]), (3, 2524))
        dashboard_ext = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"app\gui\dashboard\dashboard_ext.c"
        )
        self.assertEqual(dashboard_ext["status"], "closed")
        self.assertEqual((dashboard_ext["anchored_functions"], dashboard_ext["anchored_body_bytes"]), (6, 2498))
        dashboard_data = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"platform\protocols\dashboard_service\dashboard_data_process.c"
        )
        self.assertEqual(dashboard_data["status"], "closed")
        self.assertEqual((dashboard_data["anchored_functions"], dashboard_data["anchored_body_bytes"]), (7, 2492))
        display_manager = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"platform\display_mgr\displaydrv_manager.c"
        )
        self.assertEqual(display_manager["status"], "closed")
        self.assertEqual((display_manager["anchored_functions"], display_manager["anchored_body_bytes"]), (12, 2438))
        npmx = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"driver\npmx_driver_transplant\src\npmx_main_driver.c"
        )
        self.assertEqual(npmx["status"], "closed")
        self.assertEqual((npmx["anchored_functions"], npmx["anchored_body_bytes"]), (11, 2290))
        navigation_data = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"app\gui\navigation\navigation_data_handler.c"
        )
        self.assertEqual(navigation_data["status"], "closed")
        self.assertEqual((navigation_data["anchored_functions"], navigation_data["anchored_body_bytes"]), (7, 2290))
        service_audio = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"platform\audio\service_audio.c"
        )
        self.assertEqual(service_audio["status"], "closed")
        self.assertEqual((service_audio["anchored_functions"], service_audio["anchored_body_bytes"]), (7, 2256))
        pdm_production = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"driver\pdm\drv_pdm_production.c"
        )
        self.assertEqual(pdm_production["status"], "closed")
        self.assertEqual((pdm_production["anchored_functions"], pdm_production["anchored_body_bytes"]), (0, 0))
        cb_ring = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"platform\service\callback_mgr\cb_ring_battery.c"
        )
        self.assertEqual(cb_ring["status"], "closed")
        self.assertEqual(cb_ring["anchored_functions"], 0)
        self.assertEqual(cb_ring["anchored_body_bytes"], 0)
        for retained in (
            r"platform\service\callback_mgr\cb_charge.c",
            r"platform\service\callback_mgr\cb_msg_notif.c",
        ):
            facade = next(item for item in self.report["inventory"] if item["retained_path"] == retained)
            self.assertEqual(facade["status"], "closed")
            self.assertEqual(facade["anchored_functions"], 0)
        manager = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"platform\service\callback_mgr\callback_manager.c"
        )
        self.assertEqual(manager["status"], "closed")
        self.assertEqual((manager["anchored_functions"], manager["anchored_body_bytes"]), (4, 1032))
        central = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"platform\ble\app_ble_central.c"
        )
        self.assertEqual(central["status"], "closed")
        self.assertEqual(central["anchored_functions"], 24)
        self.assertEqual(central["anchored_body_bytes"], 11484)
        connect_params = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"platform\ble\app_connect_params.c"
        )
        self.assertEqual(connect_params["status"], "closed")
        self.assertEqual(connect_params["anchored_functions"], 10)
        self.assertEqual(connect_params["anchored_body_bytes"], 6202)
        peripheral = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"platform\ble\app_ble_peripheral.c"
        )
        self.assertEqual(peripheral["status"], "closed")
        self.assertEqual(peripheral["anchored_functions"], 12)
        self.assertEqual(peripheral["anchored_body_bytes"], 4816)
        transport = next(
            item for item in self.report["inventory"]
            if item["retained_path"] ==
            r"platform\protocols\transport_protocol\transport_protocol.c"
        )
        self.assertEqual(transport["status"], "closed")
        self.assertEqual(transport["anchored_functions"], 7)
        self.assertEqual(transport["anchored_body_bytes"], 3572)
        settings = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"platform\service\settings\service_settings.c"
        )
        self.assertEqual(settings["status"], "closed")
        self.assertEqual(settings["anchored_functions"], 13)
        self.assertEqual(settings["anchored_body_bytes"], 3626)
        tracepoint = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"app\gui\tracepoint\tracepoint_setting.c"
        )
        self.assertEqual(tracepoint["status"], "closed")
        self.assertEqual(tracepoint["anchored_functions"], 9)
        self.assertEqual(tracepoint["anchored_body_bytes"], 3194)
        product_rtos = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"product\s200\app\config\rtos.c"
        )
        self.assertEqual(product_rtos["status"], "closed")
        self.assertEqual(product_rtos["anchored_functions"], 1)
        self.assertEqual(product_rtos["anchored_body_bytes"], 88)
        util_error = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"utils\assert\util_error_check.c"
        )
        self.assertEqual(util_error["status"], "closed")
        self.assertEqual(util_error["anchored_functions"], 1)
        self.assertEqual(util_error["anchored_body_bytes"], 178)
        logger_setting = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"app\gui\logger\logger_setting.c"
        )
        self.assertEqual(logger_setting["status"], "closed")
        self.assertEqual(logger_setting["anchored_functions"], 1)
        self.assertEqual(logger_setting["anchored_body_bytes"], 84)
        ux_system = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"app\ux\ux_system\ux_system.c"
        )
        self.assertEqual(ux_system["status"], "closed")
        self.assertEqual(ux_system["anchored_functions"], 1)
        self.assertEqual(ux_system["anchored_body_bytes"], 88)
        health = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"app\gui\health\health.c"
        )
        self.assertEqual(health["status"], "closed")
        self.assertEqual(health["anchored_functions"], 1)
        self.assertEqual(health["anchored_body_bytes"], 94)
        quicklist = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"app\gui\quicklist\quicklist.c"
        )
        self.assertEqual(quicklist["status"], "closed")
        self.assertEqual(quicklist["anchored_functions"], 1)
        self.assertEqual(quicklist["anchored_body_bytes"], 94)
        watchface_manager = next(
            item for item in self.report["inventory"]
            if item["retained_path"] ==
            r"app\gui\dashboard\dashboard_watchface_manager.c"
        )
        self.assertEqual(watchface_manager["status"], "closed")
        self.assertEqual(watchface_manager["anchored_functions"], 1)
        self.assertEqual(watchface_manager["anchored_body_bytes"], 98)
        text_stream = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"app\gui\EvenAI\text_stream_service.c"
        )
        self.assertEqual(text_stream["status"], "closed")
        self.assertEqual(text_stream["anchored_functions"], 1)
        self.assertEqual(text_stream["anchored_body_bytes"], 116)
        terminal_core = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"app\gui\terminal\terminal.c"
        )
        self.assertEqual(terminal_core["status"], "closed")
        self.assertEqual(terminal_core["anchored_functions"], 1)
        self.assertEqual(terminal_core["anchored_body_bytes"], 122)
        drv_rtc = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"driver\rtc\drv_rtc.c"
        )
        self.assertEqual(drv_rtc["status"], "closed")
        self.assertEqual(drv_rtc["anchored_functions"], 1)
        self.assertEqual(drv_rtc["anchored_body_bytes"], 130)
        teleprompt_file_list = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"app\gui\teleprompt\teleprompt_file_list.c"
        )
        self.assertEqual(teleprompt_file_list["status"], "closed")
        self.assertEqual(teleprompt_file_list["anchored_functions"], 1)
        self.assertEqual(teleprompt_file_list["anchored_body_bytes"], 144)
        even_ai_timer = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"app\gui\EvenAI\even_ai_timer.c"
        )
        self.assertEqual(even_ai_timer["status"], "closed")
        self.assertEqual(even_ai_timer["anchored_functions"], 2)
        self.assertEqual(even_ai_timer["anchored_body_bytes"], 152)
        cb_ble_status = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"platform\service\callback_mgr\cb_ble_status.c"
        )
        self.assertEqual(cb_ble_status["status"], "closed")
        self.assertEqual(cb_ble_status["anchored_functions"], 2)
        self.assertEqual(cb_ble_status["anchored_body_bytes"], 154)
        conversate_menu = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"app\gui\conversate\conversate_ui_menu_page.c"
        )
        self.assertEqual(conversate_menu["status"], "closed")
        self.assertEqual(conversate_menu["anchored_functions"], 1)
        self.assertEqual(conversate_menu["anchored_body_bytes"], 218)
        conversate_tag = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"app\gui\conversate\conversate_ui_tag_page.c"
        )
        self.assertEqual(conversate_tag["status"], "closed")
        self.assertEqual(conversate_tag["anchored_functions"], 1)
        self.assertEqual(conversate_tag["anchored_body_bytes"], 238)
        exit_prompt = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"app\gui\anim\exit_prompt.c"
        )
        self.assertEqual(exit_prompt["status"], "closed")
        self.assertEqual(exit_prompt["anchored_functions"], 2)
        self.assertEqual(exit_prompt["anchored_body_bytes"], 276)
        at_core = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"platform\service\eAT\core\at_core.c"
        )
        self.assertEqual(at_core["status"], "closed")
        self.assertEqual(at_core["anchored_functions"], 2)
        self.assertEqual(at_core["anchored_body_bytes"], 302)
        hal_i2c = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"driver\hal\src\hal_i2c.c"
        )
        self.assertEqual(hal_i2c["status"], "closed")
        self.assertEqual(hal_i2c["anchored_functions"], 1)
        self.assertEqual(hal_i2c["anchored_body_bytes"], 308)
        ring_battery = next(
            item for item in self.report["inventory"]
            if item["retained_path"] ==
            r"platform\service\ring_battery\service_ring_battery.c"
        )
        self.assertEqual(ring_battery["status"], "closed")
        self.assertEqual(ring_battery["anchored_functions"], 2)
        self.assertEqual(ring_battery["anchored_body_bytes"], 306)
        opt3007_registers = next(
            item for item in self.report["inventory"]
            if item["retained_path"] ==
            r"driver\sensor\als\opt3007\opt3007_registers.c"
        )
        self.assertEqual(opt3007_registers["status"], "closed")
        self.assertEqual(opt3007_registers["anchored_functions"], 1)
        self.assertEqual(opt3007_registers["anchored_body_bytes"], 340)
        codec_porting = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"platform\audio\service_codec_porting.c"
        )
        self.assertEqual(codec_porting["status"], "closed")
        self.assertEqual(codec_porting["anchored_functions"], 2)
        self.assertEqual(codec_porting["anchored_body_bytes"], 342)
        thread_notification = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"platform\threads\thread_notification.c"
        )
        self.assertEqual(thread_notification["status"], "closed")
        self.assertEqual(thread_notification["anchored_functions"], 3)
        self.assertEqual(thread_notification["anchored_body_bytes"], 374)
        gx8002b = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"driver\codec\drv_gx8002b.c"
        )
        self.assertEqual(gx8002b["status"], "closed")
        self.assertEqual(gx8002b["anchored_functions"], 3)
        self.assertEqual(gx8002b["anchored_body_bytes"], 424)
        service_db_api = next(
            item for item in self.report["inventory"]
            if item["retained_path"] ==
            r"platform\service\flashDB\db_api\service_db_api.c"
        )
        self.assertEqual(service_db_api["status"], "closed")
        self.assertEqual(service_db_api["anchored_functions"], 5)
        self.assertEqual(service_db_api["anchored_body_bytes"], 462)
        ui_even_ai = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"app\gui\EvenAI\ui_even_ai.c"
        )
        self.assertEqual(ui_even_ai["status"], "closed")
        self.assertEqual(ui_even_ai["anchored_functions"], 2)
        self.assertEqual(ui_even_ai["anchored_body_bytes"], 346)
        service_time = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"platform\service\time\service_time.c"
        )
        self.assertEqual(service_time["status"], "closed")
        self.assertEqual(service_time["anchored_functions"], 2)
        self.assertEqual(service_time["anchored_body_bytes"], 438)
        thread_audio = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"platform\threads\thread_audio.c"
        )
        self.assertEqual(thread_audio["status"], "closed")
        self.assertEqual(thread_audio["anchored_functions"], 3)
        self.assertEqual(thread_audio["anchored_body_bytes"], 394)
        compress_log_core = next(
            item for item in self.report["inventory"]
            if item["retained_path"] ==
            r"platform\service\compress_log\core\compress_log.c"
        )
        self.assertEqual(compress_log_core["status"], "closed")
        self.assertEqual(compress_log_core["anchored_functions"], 2)
        self.assertEqual(compress_log_core["anchored_body_bytes"], 520)
        compress_log_port = next(
            item for item in self.report["inventory"]
            if item["retained_path"] ==
            r"platform\service\compress_log\port\compress_log_port.c"
        )
        self.assertEqual(compress_log_port["status"], "closed")
        self.assertEqual(compress_log_port["anchored_functions"], 3)
        self.assertEqual(compress_log_port["anchored_body_bytes"], 680)
        file_runtime = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"product\s200\app\config\redirect.c"
        )
        self.assertEqual(file_runtime["status"], "closed")
        self.assertEqual(file_runtime["anchored_functions"], 5)
        self.assertEqual(file_runtime["anchored_body_bytes"], 746)
        service_algo = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"platform\audio\service_algo.c"
        )
        self.assertEqual(service_algo["status"], "closed")
        self.assertEqual(service_algo["anchored_functions"], 2)
        self.assertEqual(service_algo["anchored_body_bytes"], 656)
        uart_sync = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"framework\sync\uart_sync.c"
        )
        self.assertEqual(uart_sync["status"], "closed")
        self.assertEqual(uart_sync["anchored_functions"], 2)
        self.assertEqual(uart_sync["anchored_body_bytes"], 688)
        service_nvdb = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"platform\service\flashDB\NV\service_nvdb.c"
        )
        self.assertEqual(service_nvdb["status"], "closed")
        self.assertEqual(service_nvdb["anchored_functions"], 2)
        self.assertEqual(service_nvdb["anchored_body_bytes"], 882)
        production_mic = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"platform\product_test\production_mic_func.c"
        )
        self.assertEqual(production_mic["status"], "closed")
        self.assertEqual(production_mic["anchored_functions"], 5)
        self.assertEqual(production_mic["anchored_body_bytes"], 646)
        ancc = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"platform\ble\profiles\ancc\profile_ancc.c"
        )
        self.assertEqual(ancc["status"], "closed")
        self.assertEqual(ancc["anchored_functions"], 10)
        self.assertEqual(ancc["anchored_body_bytes"], 2824)
        expected_profiles = {
            r"platform\ble\profiles\eus\profile_eus.c": (4, 684),
            r"platform\ble\profiles\ess\profile_ess.c": (1, 142),
            r"platform\ble\profiles\efs\profile_efs.c": (3, 480),
            r"platform\ble\profiles\nus\profile_nus.c": (3, 548),
        }
        for retained_path, expected in expected_profiles.items():
            profile = next(
                item for item in self.report["inventory"]
                if item["retained_path"] == retained_path
            )
            self.assertEqual(profile["status"], "closed")
            self.assertEqual(
                (profile["anchored_functions"], profile["anchored_body_bytes"]),
                expected,
            )
        for retained_path, expected in {
            r"platform\ble\profiles\ota\profile_ota.c": (1, 124),
            r"platform\ble\profiles\ring\profile_ring.c": (5, 1382),
        }.items():
            profile = next(
                item for item in self.report["inventory"]
                if item["retained_path"] == retained_path
            )
            self.assertEqual(profile["status"], "closed")
            self.assertEqual(
                (profile["anchored_functions"], profile["anchored_body_bytes"]),
                expected,
            )
        efs = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"platform\protocols\efs_service\efs_service.c"
        )
        self.assertEqual(efs["status"], "closed")
        self.assertEqual(efs["anchored_functions"], 6)
        self.assertEqual(efs["anchored_body_bytes"], 9046)
        ota = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"platform\protocols\ota_service\ota_service.c"
        )
        self.assertEqual(ota["status"], "closed")
        self.assertEqual(ota["anchored_functions"], 12)
        self.assertEqual(ota["anchored_body_bytes"], 14482)
        codec = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"platform\audio\service_codec_host.c"
        )
        self.assertEqual(codec["status"], "closed")
        self.assertEqual(codec["anchored_functions"], 13)
        self.assertEqual(codec["anchored_body_bytes"], 5208)
        codec_dfu = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"platform\audio\service_codec_dfu.c"
        )
        self.assertEqual(codec_dfu["status"], "closed")
        self.assertEqual(codec_dfu["anchored_functions"], 9)
        self.assertEqual(codec_dfu["anchored_body_bytes"], 8676)
        touch_dfu = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"platform\input\touchDFU\service_touch_dfu.c"
        )
        self.assertEqual(touch_dfu["status"], "closed")
        self.assertEqual(touch_dfu["anchored_functions"], 12)
        self.assertEqual(touch_dfu["anchored_body_bytes"], 5774)
        terminal = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"app\gui\terminal\terminal_pb_msg_handler.c"
        )
        self.assertEqual(terminal["status"], "closed")
        self.assertEqual(terminal["anchored_functions"], 10)
        self.assertEqual(terminal["anchored_body_bytes"], 4906)
        whitelist = next(
            item for item in self.report["inventory"]
            if item["retained_path"] ==
            r"platform\service\message_notify\service_whitelist.c"
        )
        self.assertEqual(whitelist["status"], "closed")
        self.assertEqual(whitelist["anchored_functions"], 5)
        self.assertEqual(whitelist["anchored_body_bytes"], 4206)
        teleprompt = next(
            item for item in self.report["inventory"]
            if item["retained_path"] ==
            r"app\gui\teleprompt\teleprompt_page_data.c"
        )
        self.assertEqual(teleprompt["status"], "closed")
        self.assertEqual(teleprompt["anchored_functions"], 9)
        self.assertEqual(teleprompt["anchored_body_bytes"], 3790)
        imu = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"driver\sensor\imu\imu_icm45608.c"
        )
        self.assertEqual(imu["status"], "closed")
        self.assertEqual(imu["anchored_functions"], 11)
        self.assertEqual(imu["anchored_body_bytes"], 3762)
        production_thread = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"platform\threads\thread_ble_production.c"
        )
        self.assertEqual(production_thread["status"], "closed")
        self.assertEqual(production_thread["anchored_functions"], 6)
        self.assertEqual(production_thread["anchored_body_bytes"], 1854)
        pt_protocol = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"platform\product_test\pt_protocol_procsr.c"
        )
        self.assertEqual(pt_protocol["status"], "closed")
        self.assertEqual(pt_protocol["anchored_functions"], 69)
        self.assertEqual(pt_protocol["anchored_body_bytes"], 31984)
        quicklist_page = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"app\gui\quicklist\ui_quicklist_page.c"
        )
        self.assertEqual(quicklist_page["status"], "closed")
        self.assertEqual((quicklist_page["anchored_functions"], quicklist_page["anchored_body_bytes"]), (43, 16478))
        news_page = next(item for item in self.report["inventory"] if item["retained_path"] == r"app\gui\dashboard\screens\ui_widget_news_page.c")
        self.assertEqual(news_page["status"], "closed")
        self.assertEqual((news_page["anchored_functions"], news_page["anchored_body_bytes"]), (22, 15450))
        dashboard_stock_page = next(item for item in self.report["inventory"] if item["retained_path"] == r"app\gui\dashboard\screens\ui_stock_page.c")
        self.assertEqual(dashboard_stock_page["status"], "closed")
        self.assertEqual((dashboard_stock_page["anchored_functions"], dashboard_stock_page["anchored_body_bytes"]), (19, 13180))
        navigation_ui = next(item for item in self.report["inventory"] if item["retained_path"] == r"app\gui\navigation\navigation_ui.c")
        self.assertEqual(navigation_ui["status"], "closed")
        self.assertEqual((navigation_ui["anchored_functions"], navigation_ui["anchored_body_bytes"]), (16, 11044))
        menu_page = next(item for item in self.report["inventory"] if item["retained_path"] == r"app\gui\menu\menu_page.c")
        self.assertEqual(menu_page["status"], "closed")
        self.assertEqual((menu_page["anchored_functions"], menu_page["anchored_body_bytes"]), (14, 9614))
        health_page = next(item for item in self.report["inventory"] if item["retained_path"] == r"app\gui\health\ui_health_page.c")
        self.assertEqual(health_page["status"], "closed")
        self.assertEqual((health_page["anchored_functions"], health_page["anchored_body_bytes"]), (7, 2160))
        ring_service = next(item for item in self.report["inventory"] if item["retained_path"] == r"platform\protocols\ring_service\ring_service.c")
        self.assertEqual(ring_service["status"], "closed")
        self.assertEqual((ring_service["anchored_functions"], ring_service["anchored_body_bytes"]), (9, 2074))
        input_manager = next(item for item in self.report["inventory"] if item["retained_path"] == r"platform\input\service_input_manager.c")
        self.assertEqual(input_manager["status"], "closed")
        self.assertEqual((input_manager["anchored_functions"], input_manager["anchored_body_bytes"]), (5, 2036))
        calendar_page = next(item for item in self.report["inventory"] if item["retained_path"] == r"app\gui\dashboard\screens\ui_calendar_page.c")
        self.assertEqual(calendar_page["status"], "closed")
        self.assertEqual((calendar_page["anchored_functions"], calendar_page["anchored_body_bytes"]), (5, 2028))
        ota_transport = next(item for item in self.report["inventory"] if item["retained_path"] == r"platform\protocols\ota_service\ota_transport.c")
        self.assertEqual(ota_transport["status"], "closed")
        self.assertEqual((ota_transport["anchored_functions"], ota_transport["anchored_body_bytes"]), (2, 2000))
        efs_transport = next(item for item in self.report["inventory"] if item["retained_path"] == r"platform\protocols\efs_service\efs_transport.c")
        self.assertEqual(efs_transport["status"], "closed")
        self.assertEqual((efs_transport["anchored_functions"], efs_transport["anchored_body_bytes"]), (2, 1990))
        loading_page = next(item for item in self.report["inventory"] if item["retained_path"] == r"app\gui\EvenHub\evenhub_loading_Page.c")
        self.assertEqual(loading_page["status"], "closed")
        self.assertEqual((loading_page["anchored_functions"], loading_page["anchored_body_bytes"]), (2, 1984))
        layout1 = next(item for item in self.report["inventory"] if item["retained_path"] == r"app\gui\dashboard\dashboard_watchface_layout1.c")
        self.assertEqual(layout1["status"], "closed")
        self.assertEqual((layout1["anchored_functions"], layout1["anchored_body_bytes"]), (2, 1928))
        teleprompt_fsm = next(item for item in self.report["inventory"] if item["retained_path"] == r"app\gui\teleprompt\teleprompt_fsm.c")
        self.assertEqual(teleprompt_fsm["status"], "closed")
        self.assertEqual((teleprompt_fsm["anchored_functions"], teleprompt_fsm["anchored_body_bytes"]), (3, 1902))
        health_data_manager = next(item for item in self.report["inventory"] if item["retained_path"] == r"app\gui\health\health_data_manager.c")
        self.assertEqual(health_data_manager["status"], "closed")
        self.assertEqual((health_data_manager["anchored_functions"], health_data_manager["anchored_body_bytes"]), (5, 1848))
        evenhub_main = next(item for item in self.report["inventory"] if item["retained_path"] == r"app\gui\EvenHub\evenhub_main.c")
        self.assertEqual(evenhub_main["status"], "closed")
        self.assertEqual((evenhub_main["anchored_functions"], evenhub_main["anchored_body_bytes"]), (3, 1848))
        translate = next(item for item in self.report["inventory"] if item["retained_path"] == r"app\gui\translate\translate.c")
        self.assertEqual(translate["status"], "closed")
        self.assertEqual((translate["anchored_functions"], translate["anchored_body_bytes"]), (7, 1838))
        translate_ui = next(item for item in self.report["inventory"] if item["retained_path"] == r"app\gui\translate\translate_ui.c")
        self.assertEqual(translate_ui["status"], "closed")
        self.assertEqual((translate_ui["anchored_functions"], translate_ui["anchored_body_bytes"]), (7, 1568))
        teleprompt = next(item for item in self.report["inventory"] if item["retained_path"] == r"app\gui\teleprompt\teleprompt.c")
        self.assertEqual(teleprompt["status"], "closed")
        self.assertEqual((teleprompt["anchored_functions"], teleprompt["anchored_body_bytes"]), (7, 1752))
        comm_data = next(item for item in self.report["inventory"] if item["retained_path"] == r"app\gui\conversate\conversate_comm_data.c")
        self.assertEqual(comm_data["status"], "closed")
        self.assertEqual((comm_data["anchored_functions"], comm_data["anchored_body_bytes"]), (6, 1718))
        conversate = next(item for item in self.report["inventory"] if item["retained_path"] == r"app\gui\conversate\conversate.c")
        self.assertEqual(conversate["status"], "closed")
        self.assertEqual((conversate["anchored_functions"], conversate["anchored_body_bytes"]), (9, 1506))
        image_container = next(item for item in self.report["inventory"] if item["retained_path"] == r"app\gui\EvenHub\common_image_container.c")
        self.assertEqual(image_container["status"], "closed")
        self.assertEqual((image_container["anchored_functions"], image_container["anchored_body_bytes"]), (2, 1492))
        layout2 = next(item for item in self.report["inventory"] if item["retained_path"] == r"app\gui\dashboard\dashboard_watchface_layout2.c")
        self.assertEqual(layout2["status"], "closed")
        self.assertEqual((layout2["anchored_functions"], layout2["anchored_body_bytes"]), (1, 1484))
        layout3 = next(item for item in self.report["inventory"] if item["retained_path"] == r"app\gui\dashboard\dashboard_watchface_layout3.c")
        self.assertEqual(layout3["status"], "closed")
        self.assertEqual((layout3["anchored_functions"], layout3["anchored_body_bytes"]), (1, 1708))
        thread_ring = next(item for item in self.report["inventory"] if item["retained_path"] == r"platform\threads\thread_ring.c")
        self.assertEqual(thread_ring["status"], "closed")
        self.assertEqual((thread_ring["anchored_functions"], thread_ring["anchored_body_bytes"]), (5, 1696))
        event_loop = next(item for item in self.report["inventory"] if item["retained_path"] == r"framework\fw_event_loop\fw_event_loop.c")
        self.assertEqual(event_loop["status"], "closed")
        self.assertEqual((event_loop["anchored_functions"], event_loop["anchored_body_bytes"]), (5, 1698))
        ring_policy = next(item for item in self.report["inventory"] if item["retained_path"] == r"platform\protocols\ring_service\ring_connect_policy.c")
        self.assertEqual(ring_policy["status"], "closed")
        self.assertEqual((ring_policy["anchored_functions"], ring_policy["anchored_body_bytes"]), (11, 1686))
        system_close = next(item for item in self.report["inventory"] if item["retained_path"] == r"app\gui\SystemClose\systemClose.c")
        self.assertEqual(system_close["status"], "closed")
        self.assertEqual((system_close["anchored_functions"], system_close["anchored_body_bytes"]), (5, 1632))

    def test_open_frontier_order(self) -> None:
        self.assertEqual(self.report["top_open_frontier"], [])
        main_page = next(item for item in self.report["inventory"] if item["retained_path"] == r"app\gui\conversate\conversate_ui_main_page.c")
        self.assertEqual(main_page["status"], "closed")
        universal = next(item for item in self.report["inventory"] if item["retained_path"] == r"platform\service\service_universal_setting\service_universal_setting.c")
        self.assertEqual(universal["status"], "closed")

    def test_audio_manager_is_closed(self) -> None:
        item = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"platform\audio\service_audio_manager.c"
        )
        self.assertEqual(item["status"], "closed")
        self.assertEqual(item["anchored_functions"], 4)
        self.assertEqual(item["anchored_body_bytes"], 984)

    def test_system_kvdb_is_closed(self) -> None:
        item = next(
            item for item in self.report["inventory"]
            if item["retained_path"] == r"platform\service\flashDB\kv\service_kvdb.c"
        )
        self.assertEqual(item["status"], "closed")
        self.assertEqual(item["anchored_functions"], 2)
        self.assertEqual(item["anchored_body_bytes"], 1256)


if __name__ == "__main__":
    unittest.main()
