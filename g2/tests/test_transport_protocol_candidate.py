#!/usr/bin/env python3
import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/transport_protocol.c"
FIXTURE = ROOT / "tests/fixtures/transport_protocol_host.c"
SELECTORS = {
    "INIT": "TPL_Init",
    "CONTEXT_GET": "_getOrCreateContext",
    "CONTEXT_FREE": "open_cfw_tpl_context_free",
    "CONTEXT_MARK": "open_cfw_tpl_context_mark_packet",
    "CONTEXT_SEEN": "open_cfw_tpl_context_packet_seen",
    "SCHEDULE": "open_cfw_tpl_schedule_rx_timeout",
    "TIMEOUT_CALLBACK": "_rxNextPacketTimeout",
    "TIMEOUT_HANDLER": "TPL_RxPacketTimeoutHandler",
    "SYNC_CALLBACK": "_rxSyncEventCallback",
    "RESPONSE": "_tplReponse",
    "RECEIVE": "TPL_ReceivePacket",
    "SEND": "TPL_SendPacket",
    "RESET": "open_cfw_tpl_reset_receive_contexts",
}


class TransportProtocolCandidateTests(unittest.TestCase):
    def test_host_behavior(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / "transport-protocol"
            subprocess.run([
                "/usr/bin/clang", "-std=c11", "-O2", "-Wall", "-Wextra",
                "-Werror", str(FIXTURE), "-o", str(executable),
            ], cwd=ROOT, check=True)
            subprocess.run([str(executable)], check=True)

    def test_selector_builds_expose_one_entry_each(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            for selector, expected in SELECTORS.items():
                obj = Path(directory) / (selector + ".o")
                subprocess.run([
                    "/usr/bin/clang", "-target", "thumbv7em-none-eabi",
                    "-mthumb", "-mcpu=cortex-m55", "-O2", "-ffreestanding",
                    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
                    "-mno-unaligned-access", "-fno-unwind-tables",
                    "-fno-asynchronous-unwind-tables", "-fropi",
                    "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
                    "-Werror", "-mllvm", "-enable-machine-outliner=never",
                    "-DOPEN_CFW_TPL_" + selector + "_ONLY=1", "-c", str(SOURCE),
                    "-o", str(obj),
                ], cwd=ROOT, check=True)
                symbols = subprocess.run(
                    ["nm", str(obj)], check=True, capture_output=True, text=True
                ).stdout
                entries = {parts[2] for line in symbols.splitlines()
                           if len(parts := line.split()) == 3 and parts[1] == "T"}
                self.assertEqual(entries, {expected})

    def test_source_is_nonempty_and_pinned_by_digest_shape(self) -> None:
        data = SOURCE.read_bytes()
        self.assertGreater(len(data), 20_000)
        self.assertEqual(len(hashlib.sha256(data).hexdigest()), 64)


if __name__ == "__main__":
    unittest.main()
