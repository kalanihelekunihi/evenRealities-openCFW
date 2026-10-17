#!/usr/bin/env python3
"""Replay the Main chain from the five-callback locale archive."""
import importlib.util
from pathlib import Path

script = Path(__file__).with_name("replay_main_locale_relocatable_current_20261016.py")
spec = importlib.util.spec_from_file_location("locale_replay", script)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.START = module.BUILD / "main-locale-five-archive/receipt.json"
module.OUT = module.BUILD / "main-locale-five-current-replay"
module.EXPECTED_START_STATUS = "PASS_EXPERIMENTAL_MAIN_LOCALE_FIVE_ARCHIVE_C"
module.RESULT_STATUS = "PASS_EXPERIMENTAL_MAIN_LOCALE_FIVE_CURRENT_REPLAY_C"
module.REMOVED = {"audio_uart_ring_locale_dispatch_200044c0"}
module.PROVIDERS = {"audio_uart_ring_locale_dispatch_200044c0",
                    "audio_uart_locale_ascii_space_4d4384",
                    "audio_uart_locale_ascii_lower_4d4398",
                    "audio_uart_locale_ascii_alpha_4d436e",
                    "audio_uart_locale_ascii_lowercase_4d4368",
                    "audio_uart_locale_ascii_uppercase_4d436c"}
module.main()
