import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/ota_service.c"
HOST = ROOT / "tests/fixtures/ota_service_host.c"
SELECTORS = {
    "SELECT": "OtaSelectFlashOps", "FILE_SIZE": "OtaFileSize",
    "ERASE": "OtaEraseRange", "SET_ADDR": "_evenOtaSetFwAddr",
    "VERIFY": "_verifyFlashContent", "BUFFERED_WRITE": "OtaBufferedFlashWrite",
    "COMMIT": "OtaCommitDescriptor", "REPLY": "_evenOtaReplyToAPP",
    "RPC_STATUS": "_RPC_SystemOtaStatusSync", "PARSE_HEX": "OtaParseHexAddress",
    "BOOT_MRAM": "_evenOtaBootloaderWriteFile2MRAM", "FS_PROBE": "_otaFsHealthProbe",
    "FS_HEAL": "_otaFsHealthCheckAndHeal", "COMMAND": "_fileCmdParse",
    "RAW": "_fileRawDataParse", "CRC": "OTA_FileCaculateCRC",
    "EXPORT": "_exportFileParse", "DISPATCH": "OTA_FrameDispatch",
    "RESET_EXPORT": "OTA_ResetExportState", "STATUS4": "OTA_NotifyStatus4",
    "STATUS3": "OTA_NotifyStatus3", "STATUS5": "OTA_NotifyStatus5",
    "CANCEL": "OTA_CancelExport", "ACTIVE": "OTA_TransferActive",
    "INTERFACE": "OTA_SetInterface", "FLASH_ERASE_ADAPTER": "open_cfw_ota_flash_erase",
    "FLASH_READ_ADAPTER": "open_cfw_ota_flash_read",
    "FLASH_WRITE_ADAPTER": "open_cfw_ota_flash_write",
    "STATUS_ADAPTER": "open_cfw_ota_status_sync",
}


class OtaServiceCandidateTests(unittest.TestCase):
    def test_host_behavior(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            binary = Path(td) / "ota-service-host"
            subprocess.run(
                ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", str(HOST), "-o", str(binary)],
                cwd=ROOT,
                check=True,
            )
            result = subprocess.run([str(binary)], text=True, capture_output=True, check=True)
            self.assertIn("ota service host: PASS", result.stdout)

    def test_recovered_surface_is_present(self) -> None:
        text = SOURCE.read_text()
        for name in (
            "OtaSelectFlashOps", "OtaFileSize", "OtaEraseRange", "_evenOtaSetFwAddr",
            "_verifyFlashContent", "OtaBufferedFlashWrite", "OtaCommitDescriptor",
            "_evenOtaReplyToAPP", "_RPC_SystemOtaStatusSync", "OtaParseHexAddress",
            "_evenOtaBootloaderWriteFile2MRAM", "_otaFsHealthProbe",
            "_otaFsHealthCheckAndHeal", "_fileCmdParse", "_fileRawDataParse",
            "_fileCaculateCRC", "_exportFileParse", "OTA_FrameDispatch",
            "OTA_ResetExportState", "OTA_NotifyStatus4", "OTA_NotifyStatus3",
            "OTA_NotifyStatus5", "OTA_CancelExport", "OTA_TransferActive", "OTA_SetInterface",
        ):
            self.assertIn(name, text)

    def test_complete_surface_compiles_for_cortex_m55(self) -> None:
        expected = {
            "OtaSelectFlashOps", "OtaFileSize", "OtaEraseRange", "_evenOtaSetFwAddr",
            "_verifyFlashContent", "OtaBufferedFlashWrite", "OtaCommitDescriptor",
            "_evenOtaReplyToAPP", "_RPC_SystemOtaStatusSync", "OtaParseHexAddress",
            "_evenOtaBootloaderWriteFile2MRAM", "_otaFsHealthProbe",
            "_otaFsHealthCheckAndHeal", "_fileCmdParse", "_fileRawDataParse",
            "_fileCaculateCRC", "_exportFileParse", "OTA_FrameDispatch",
            "OTA_ResetExportState", "OTA_NotifyStatus4", "OTA_NotifyStatus3",
            "OTA_NotifyStatus5", "OTA_CancelExport", "OTA_TransferActive", "OTA_SetInterface",
            "open_cfw_ota_flash_erase", "open_cfw_ota_flash_read",
            "open_cfw_ota_flash_write", "open_cfw_ota_status_sync",
        }
        with tempfile.TemporaryDirectory() as td:
            obj = Path(td) / "ota-service.o"
            subprocess.run([
                "/usr/bin/clang", "-target", "thumbv7em-none-eabi", "-mthumb",
                "-mcpu=cortex-m55", "-O2", "-ffreestanding", "-fno-jump-tables",
                "-fomit-frame-pointer", "-fno-builtin", "-mno-unaligned-access",
                "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-fropi",
                "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror",
                "-mllvm", "-enable-machine-outliner=never", "-c", str(SOURCE), "-o", str(obj),
            ], cwd=ROOT, check=True)
            symbols = subprocess.run(
                ["nm", str(obj)], check=True, capture_output=True, text=True
            ).stdout
            exported = {parts[2] for line in symbols.splitlines()
                        if len(parts := line.split()) == 3 and parts[1] == "T"}
            self.assertEqual(exported, expected)

    def test_selector_builds_expose_one_entry_each(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            for selector, expected in SELECTORS.items():
                obj = Path(td) / f"{selector}.o"
                subprocess.run([
                    "/usr/bin/clang", "-target", "thumbv7em-none-eabi", "-mthumb",
                    "-mcpu=cortex-m55", "-O2", "-ffreestanding", "-fno-jump-tables",
                    "-fomit-frame-pointer", "-fno-builtin", "-mno-unaligned-access",
                    "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-fropi",
                    "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror",
                    "-mllvm", "-enable-machine-outliner=never",
                    "-DOPEN_CFW_OTA_SERVICE_SELECTOR_BUILD=1",
                    f"-DOPEN_CFW_OTA_SERVICE_{selector}_ONLY=1",
                    "-c", str(SOURCE), "-o", str(obj),
                ], cwd=ROOT, check=True)
                symbols = subprocess.run(
                    ["nm", str(obj)], check=True, capture_output=True, text=True
                ).stdout
                exported = {parts[2] for line in symbols.splitlines()
                            if len(parts := line.split()) == 3 and parts[1] == "T"}
                self.assertEqual(exported, {expected}, selector)


if __name__ == "__main__":
    unittest.main()
