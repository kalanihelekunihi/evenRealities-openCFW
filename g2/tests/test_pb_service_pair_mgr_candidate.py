#!/usr/bin/env python3
import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/pb_service_pair_mgr.c"
FIXTURE = ROOT / "tests/fixtures/pb_service_pair_mgr_host.c"
SOURCE_SIZE = 27574
SOURCE_SHA256 = "917a17e5c161a4a55a46fe4bb14a5b9a7b613b5db8e31dd4ee18f8ba4e53b0fe"
SELECTORS = {
    "BUFFER_WRITE": "open_cfw_pb_service_pair_mgr_buffer_write",
    "RX_SEC_AUTH": "PB_RxSecAuth",
    "TX_SEC_AUTH": "PB_TxEncodeSecAuth",
    "NOTIFY_SEC_AUTH": "PB_TxEncodeNotifySecAuthImpl",
    "FLAG_SET": "pairMgrSecAuthFlagSet",
    "FLAG_GET": "pairMgrSecAuthFlagGet",
    "RX_PIPE_ROLE": "PB_RxPipeRoleChange",
    "TX_PIPE_ROLE": "PB_TxEncodePipeRoleChange",
    "RING_OWNER": "_PB_RxRingConnectInfoOwnerExecute",
    "RING_COMMON": "_PB_RxRingConnectInfoCommon",
    "RX_RING": "PB_RxRingConnectInfo",
    "RING_TIME": "PB_LastTxEncodeRingConnectInfoTimeSet",
    "TX_RING": "PB_TxEncodeRingConnectInfo",
    "NOTIFY_RING_IMPL": "PB_TxEncodeNotifyRingConnectInfoImpl",
    "NOTIFY_RING": "PB_TxEncodeNotifyRingConnectInfo",
    "RX_BLE_PARAMS": "PB_RxBleConnectParams",
    "TX_BLE_PARAMS": "PB_TxEncodeBleConnectParams",
    "RX_DISCONNECT": "PB_RxDisconnectInfo",
    "TX_DISCONNECT": "PB_TxEncodeDisconnectInfo",
    "RX_UNPAIR": "PB_RxUnpairInfo",
    "TX_UNPAIR": "PB_TxEncodeUnpairInfo",
}


class PbServicePairMgrCandidateTests(unittest.TestCase):
    def test_host_behavior(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory) / "pb-service-pair-mgr"
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
                    "/usr/bin/clang", "-target", "thumbv7em-none-eabi", "-mthumb",
                    "-mcpu=cortex-m55", "-O2", "-ffreestanding",
                    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
                    "-mno-unaligned-access", "-fno-unwind-tables",
                    "-fno-asynchronous-unwind-tables", "-fropi",
                    "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
                    "-Werror", "-mllvm", "-enable-machine-outliner=never",
                    "-DOPEN_CFW_PB_PAIR_MGR_" + selector + "_ONLY=1",
                    "-c", str(SOURCE), "-o", str(obj),
                ], cwd=ROOT, check=True)
                symbols = subprocess.run(
                    ["nm", str(obj)], check=True, capture_output=True, text=True
                ).stdout
                entries = {parts[2] for line in symbols.splitlines()
                           if len(parts := line.split()) == 3 and parts[1] == "T"}
                self.assertEqual(entries, {expected})

    def test_source_is_pinned(self) -> None:
        data = SOURCE.read_bytes()
        self.assertEqual(len(data), SOURCE_SIZE)
        self.assertEqual(hashlib.sha256(data).hexdigest(), SOURCE_SHA256)


if __name__ == "__main__":
    unittest.main()
