#!/usr/bin/env python3
"""Behavior, hardening, and target-compile tests for the Cordio HCI transport."""

from __future__ import annotations

import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/shared/cordio/runtime_cordio_hci_tr.c"
INCLUDE = ROOT / "components/shared/cordio"

HARNESS = r"""
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

static uint8_t tx_type;
static uint16_t tx_length;
static uint16_t tx_result;
static unsigned tx_calls;
static uint16_t max_acl = 1024;
static int fail_alloc;
static unsigned data_allocs;
static unsigned msg_allocs;
static unsigned deliveries;
static uint8_t delivered_type;
static uint16_t delivered_length;
static uint8_t delivered[1024];

uint16_t HciDrvWrite(uint8_t type, uint16_t length, const uint8_t *data) {
    (void)data; tx_type = type; tx_length = length; ++tx_calls; return tx_result;
}
uint16_t HciGetMaxRxAclLen(void) { return max_acl; }
void *WsfMsgDataAlloc(uint16_t length, uint8_t tailroom) {
    (void)tailroom; ++data_allocs; return fail_alloc ? 0 : malloc(length ? length : 1);
}
void *WsfMsgAlloc(uint16_t length) {
    ++msg_allocs; return fail_alloc ? 0 : malloc(length ? length : 1);
}
void hciCoreRecv(uint8_t type, uint8_t *data) {
    uint16_t payload = type == 2 ? (uint16_t)(data[2] | ((uint16_t)data[3] << 8)) : data[1];
    delivered_length = (uint16_t)(payload + (type == 2 ? 4 : 2));
    memcpy(delivered, data, delivered_length);
    delivered_type = type; ++deliveries; free(data);
}
void test_reset(void) {
    extern void open_cfw_hci_tr_reset_for_test(void);
    open_cfw_hci_tr_reset_for_test();
    tx_type = 0; tx_length = tx_result = 0; tx_calls = 0;
    max_acl = 1024; fail_alloc = 0; data_allocs = msg_allocs = 0;
    deliveries = 0; delivered_type = 0; delivered_length = 0;
    memset(delivered, 0, sizeof(delivered));
}
void test_tx_result(uint16_t value) { tx_result = value; }
void test_max_acl(uint16_t value) { max_acl = value; }
void test_fail_alloc(int value) { fail_alloc = value; }
uint8_t test_tx_type(void) { return tx_type; }
uint16_t test_tx_length(void) { return tx_length; }
unsigned test_tx_calls(void) { return tx_calls; }
unsigned test_data_allocs(void) { return data_allocs; }
unsigned test_msg_allocs(void) { return msg_allocs; }
unsigned test_deliveries(void) { return deliveries; }
uint8_t test_delivered_type(void) { return delivered_type; }
uint16_t test_delivered_length(void) { return delivered_length; }
uint8_t test_delivered_byte(unsigned i) { return i < sizeof(delivered) ? delivered[i] : 0; }
"""


class CordioHciTransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        directory = Path(cls.tmp.name)
        harness = directory / "harness.c"
        harness.write_text(HARNESS)
        library = directory / "libhci_tr.so"
        subprocess.run(
            [
                "clang", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                "-DOPEN_CFW_HCI_TR_TEST=1", "-I", str(INCLUDE), str(SOURCE),
                str(harness), "-o", str(library),
            ],
            check=True,
        )
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.hciTrSendAclData.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_uint8)]
        cls.lib.hciTrSendAclData.restype = ctypes.c_uint16
        cls.lib.hciTrSendCmd.argtypes = [ctypes.POINTER(ctypes.c_uint8)]
        cls.lib.hciTrSendCmd.restype = ctypes.c_bool
        cls.lib.hciTrSerialRxIncoming.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint16]
        cls.lib.hciTrSerialRxIncoming.restype = ctypes.c_uint16
        cls.lib.hciTrReceivingPacket.restype = ctypes.c_bool
        cls.lib.test_delivered_byte.argtypes = [ctypes.c_uint]
        cls.lib.test_delivered_byte.restype = ctypes.c_uint8

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def setUp(self) -> None:
        self.lib.test_reset()

    @staticmethod
    def buffer(values: list[int]):
        return (ctypes.c_uint8 * len(values))(*values)

    def receive(self, values: list[int]) -> int:
        data = self.buffer(values)
        return self.lib.hciTrSerialRxIncoming(data, len(values))

    def delivered(self) -> list[int]:
        return [self.lib.test_delivered_byte(i) for i in range(self.lib.test_delivered_length())]

    def test_send_ownership_and_exact_write_contract(self) -> None:
        acl = self.buffer([0x01, 0x20, 0x03, 0x00, 7, 8, 9])
        self.lib.test_tx_result(7)
        self.assertEqual(self.lib.hciTrSendAclData(None, acl), 7)
        self.assertEqual((self.lib.test_tx_type(), self.lib.test_tx_length()), (2, 7))
        self.lib.test_tx_result(6)
        self.assertEqual(self.lib.hciTrSendAclData(None, acl), 0)

        command = self.buffer([0x03, 0x0c, 2, 1, 2])
        self.lib.test_tx_result(5)
        self.assertTrue(self.lib.hciTrSendCmd(command))
        self.assertEqual((self.lib.test_tx_type(), self.lib.test_tx_length()), (1, 5))
        self.lib.test_tx_result(4)
        self.assertFalse(self.lib.hciTrSendCmd(command))
        self.assertEqual(self.lib.test_tx_calls(), 4)

        self.assertEqual(self.lib.hciTrSendAclData(None, None), 0)
        self.assertFalse(self.lib.hciTrSendCmd(None))
        self.assertEqual(self.lib.test_tx_calls(), 4)

    def test_event_and_acl_packets_deliver_exact_bytes(self) -> None:
        event = [4, 0x0e, 3, 0xaa, 0xbb, 0xcc]
        self.assertEqual(self.receive(event), len(event))
        self.assertEqual(self.lib.test_msg_allocs(), 1)
        self.assertEqual(self.lib.test_deliveries(), 1)
        self.assertEqual(self.lib.test_delivered_type(), 4)
        self.assertEqual(self.delivered(), event[1:])
        self.assertFalse(self.lib.hciTrReceivingPacket())

        acl = [2, 0x01, 0x20, 3, 0, 9, 8, 7]
        self.assertEqual(self.receive(acl), len(acl))
        self.assertEqual(self.lib.test_data_allocs(), 1)
        self.assertEqual(self.lib.test_deliveries(), 2)
        self.assertEqual(self.lib.test_delivered_type(), 2)
        self.assertEqual(self.delivered(), acl[1:])

    def test_arbitrary_chunking_preserves_persistent_state(self) -> None:
        packet = [2, 0x02, 0x20, 5, 0, 10, 11, 12, 13, 14]
        for byte in packet[:-1]:
            self.assertEqual(self.receive([byte]), 1)
            self.assertTrue(self.lib.hciTrReceivingPacket())
            self.assertEqual(self.lib.test_deliveries(), 0)
        self.assertEqual(self.receive(packet[-1:]), 1)
        self.assertEqual(self.lib.test_deliveries(), 1)
        self.assertEqual(self.delivered(), packet[1:])
        self.assertFalse(self.lib.hciTrReceivingPacket())

        two = [4, 1, 0, 4, 2, 1, 0x55]
        self.assertEqual(self.receive(two), len(two))
        self.assertEqual(self.lib.test_deliveries(), 3)
        self.assertEqual(self.delivered(), [2, 1, 0x55])

    def test_rejections_discard_chunk_and_reset_atomically(self) -> None:
        self.assertEqual(self.receive([0xff, 1, 2, 3]), 4)
        self.assertFalse(self.lib.hciTrReceivingPacket())
        self.assertEqual(self.lib.test_deliveries(), 0)

        self.lib.test_max_acl(2)
        too_long = [2, 1, 0x20, 3, 0, 9, 9]
        self.assertEqual(self.receive(too_long), len(too_long))
        self.assertEqual(self.lib.test_data_allocs(), 0)
        self.assertFalse(self.lib.hciTrReceivingPacket())

        self.lib.test_max_acl(1024)
        self.lib.test_fail_alloc(1)
        self.assertEqual(self.receive([4, 1, 1, 0xaa]), 4)
        self.assertEqual(self.lib.test_msg_allocs(), 1)
        self.assertFalse(self.lib.hciTrReceivingPacket())

        self.lib.test_fail_alloc(0)
        valid = [4, 2, 1, 0x77]
        self.assertEqual(self.receive(valid), len(valid))
        self.assertEqual(self.lib.test_deliveries(), 1)
        self.assertEqual(self.delivered(), valid[1:])

    def test_null_nonempty_input_fails_closed(self) -> None:
        self.assertEqual(self.lib.hciTrSerialRxIncoming(None, 5), 5)
        self.assertFalse(self.lib.hciTrReceivingPacket())

    def test_cortex_m55_translation_unit_and_all_entries_compile(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "hci_tr.o"
            subprocess.run(
                [
                    "clang", "--target=thumbv7em-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-O2", "-ffreestanding", "-fno-builtin", "-ffunction-sections",
                    "-fdata-sections", "-Wall", "-Wextra", "-Werror",
                    "-DOPEN_CFW_HCI_TR_PRODUCTION=1", "-I", str(INCLUDE), "-c",
                    str(SOURCE), "-o", str(output),
                ],
                check=True,
            )
            symbols = subprocess.run(
                ["nm", "-g", str(output)], check=True, capture_output=True, text=True
            ).stdout
            for function in (
                "hciTrSendAclData", "hciTrSendCmd", "hciTrSerialRxIncoming",
                "hciTrReceivingPacket",
            ):
                self.assertIn(function, symbols)


if __name__ == "__main__":
    unittest.main()
