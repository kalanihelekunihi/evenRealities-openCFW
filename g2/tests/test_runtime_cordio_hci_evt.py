#!/usr/bin/env python3
"""Host behavior and Cortex-M55 inventory tests for the clean-room HCI event port."""
from __future__ import annotations

import ctypes
import csv
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "components/shared/cordio/runtime_cordio_hci_evt.c"
INC = ROOT / "components/shared/cordio"
INCLUDES = [
    INC,
    ROOT / "third_party/cordio/wsf/include",
    ROOT / "third_party/cordio/ble-host/include",
    ROOT / "third_party/cordio/ble-host/sources/stack/cfg",
]
MAP = ROOT / "tools/manifests/ambiq-cordio-hci-evt-function-map.tsv"
HARNESS = r"""
#include <stdint.h>
#include "runtime_cordio_hci_evt.h"
static unsigned callbacks,cmd_completions,num_packets,conn_opens,conn_closes,cis_opens,cis_closes;
static uint8_t last_event,last_status,last_u8;static uint16_t last_handle;static uint8_t cis_present;
static void callback(hciEvt_t*m){++callbacks;last_event=m->hdr.event;last_status=m->hdr.status;
 switch(m->hdr.event){case HCI_LE_CONN_CMPL_CBACK_EVT:case HCI_LE_ENHANCED_CONN_CMPL_CBACK_EVT:last_handle=m->leConnCmpl.handle;last_u8=m->leConnCmpl.role;break;
 case HCI_DISCONNECT_CMPL_CBACK_EVT:case HCI_CIS_DISCONNECT_CMPL_CBACK_EVT:last_handle=m->disconnectCmpl.handle;last_u8=m->disconnectCmpl.reason;break;
 case HCI_READ_RSSI_CMD_CMPL_CBACK_EVT:last_handle=m->readRssiCmdCmpl.handle;last_u8=(uint8_t)m->readRssiCmdCmpl.rssi;break;
 case HCI_LE_ADV_REPORT_CBACK_EVT:last_u8=m->leAdvReport.len;last_handle=m->leAdvReport.pData?m->leAdvReport.pData[0]:0;break;default:break;}}
void hciCmdRecvCmpl(uint8_t n){cmd_completions+=n;}void hciCoreNumCmplPkts(uint8_t*p){num_packets+=p[0];}
void hciCoreConnOpen(uint16_t h){++conn_opens;last_handle=h;}void hciCoreConnClose(uint16_t h){++conn_closes;last_handle=h;}
void*hciCoreCisByHandle(uint16_t h){(void)h;return cis_present?(void*)1:0;}void hciCoreCisOpen(uint16_t h){++cis_opens;last_handle=h;}void hciCoreCisClose(uint16_t h){++cis_closes;last_handle=h;}
uint8_t hciCoreVsCmdCmplRcvd(uint16_t o,uint8_t*p,uint8_t n){(void)o;(void)p;(void)n;return 0;}uint8_t hciCoreVsEvtRcvd(uint8_t*p,uint8_t n){(void)p;(void)n;return 0;}uint8_t hciCoreHwErrorRcvd(uint8_t*p){(void)p;return 0;}
void test_reset(void){open_cfw_hci_evt_reset_for_test();open_cfw_hci_evt_set_callback_for_test(callback);callbacks=cmd_completions=num_packets=conn_opens=conn_closes=cis_opens=cis_closes=0;last_event=last_status=last_u8=0;last_handle=0;cis_present=0;}
void test_process(uint8_t*p){hciEvtProcessMsg(p);}void test_cis(uint8_t v){cis_present=v;}unsigned test_count(unsigned i){unsigned v[]={callbacks,cmd_completions,num_packets,conn_opens,conn_closes,cis_opens,cis_closes};return i<7?v[i]:0;}
uint8_t test_event(void){return last_event;}uint8_t test_status(void){return last_status;}uint8_t test_u8(void){return last_u8;}uint16_t test_handle(void){return last_handle;}uint32_t test_stat(unsigned i){open_cfw_hci_evt_stats_t*s=hciEvtGetStats();uint32_t*v=(uint32_t*)s;return i<4?v[i]:0;}
"""


class CordioHciEventTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        directory = Path(cls.tmp.name)
        harness = directory / "harness.c"
        harness.write_text(HARNESS)
        library = directory / "event.so"
        command = ["clang", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                   "-DOPEN_CFW_HCI_EVT_TEST=1"]
        for include in INCLUDES:
            command += ["-I", str(include)]
        command += [str(SRC), str(harness), "-o", str(library)]
        subprocess.run(command, check=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.test_process.argtypes = [ctypes.POINTER(ctypes.c_uint8)]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def setUp(self) -> None:
        self.lib.test_reset()

    def process(self, values: list[int]) -> None:
        packet = (ctypes.c_uint8 * len(values))(*values)
        self.lib.test_process(packet)

    def test_le_connection_and_disconnect_lifecycle(self) -> None:
        payload = [0, 0x34, 0x12, 1, 0, 1, 2, 3, 4, 5, 6, 0x18, 0, 0, 0,
                   0x48, 0, 5]
        self.process([0x3E, len(payload) + 1, 0x01, *payload])
        self.assertEqual((self.lib.test_event(), self.lib.test_handle(), self.lib.test_u8()),
                         (1, 0x1234, 1))
        self.assertEqual(self.lib.test_count(3), 1)
        self.process([0x05, 4, 0, 0x34, 0x12, 0x13])
        self.assertEqual((self.lib.test_event(), self.lib.test_count(4)), (3, 1))
        self.lib.test_cis(1)
        self.process([0x05, 4, 0, 0x78, 0x56, 0x16])
        self.assertEqual((self.lib.test_event(), self.lib.test_count(6)), (70, 1))

    def test_command_complete_and_advertising_report(self) -> None:
        self.process([0x0E, 7, 1, 0x05, 0x14, 0, 0x22, 0x11, 0xD8])
        self.assertEqual((self.lib.test_count(1), self.lib.test_event(),
                          self.lib.test_handle(), self.lib.test_u8()),
                         (1, 7, 0x1122, 0xD8))
        report = [1, 0, 1, 1, 2, 3, 4, 5, 6, 3, 0xAA, 0xBB, 0xCC, 0xC0]
        self.process([0x3E, len(report) + 1, 0x02, *report])
        self.assertEqual((self.lib.test_event(), self.lib.test_u8(), self.lib.test_handle()),
                         (6, 3, 0xAA))

    def test_malformed_unknown_and_completed_packets_fail_closed(self) -> None:
        self.process([0x3E, 0])
        self.process([0x7D, 0])
        self.process([0x13, 5, 1, 1, 0, 2, 0])
        self.assertEqual(self.lib.test_count(2), 1)
        self.assertEqual((self.lib.test_stat(0), self.lib.test_stat(2), self.lib.test_stat(3)),
                         (3, 1, 1))

    def test_target_compile_exports_exact_80_api_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            obj = Path(directory) / "event.o"
            command = ["clang", "--target=thumbv7em-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                       "-O2", "-ffreestanding", "-fno-builtin", "-ffunction-sections",
                       "-fdata-sections", "-Wall", "-Wextra", "-Werror",
                       "-DOPEN_CFW_HCI_EVT_PRODUCTION=1"]
            for include in INCLUDES:
                command += ["-I", str(include)]
            command += ["-c", str(SRC), "-o", str(obj)]
            subprocess.run(command, check=True)
            symbols = subprocess.run(["nm", "-g", str(obj)], capture_output=True,
                                     text=True, check=True).stdout
            actual = {line.split()[-1] for line in symbols.splitlines()
                      if len(line.split()) == 3 and line.split()[1] == "T"}
            with MAP.open(newline="") as handle:
                expected = {row["function"] for row in csv.DictReader(handle, delimiter="\t")}
            self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
