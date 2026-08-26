#!/usr/bin/env python3
"""Behavior, bounds, and target-compile tests for the HCI platform shim."""

from __future__ import annotations

import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/shared/cordio/runtime_cordio_hci_core_ps.c"
INCLUDE = ROOT / "components/shared/cordio"

HARNESS = r"""
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include "runtime_cordio_hci_core_ps.h"

static uint8_t connection[28];
static uint16_t connection_handle;
static unsigned cmd_init_calls, tx_ready_calls, timeout_calls, evt_calls, reset_calls;
static unsigned enq_calls, deq_index, free_calls, acl_calls, iso_calls, flow_calls;
static uint8_t tx_ready_value, enq_type, set_handler, set_event;
static uint8_t *enq_message;
static uint8_t *deq_messages[8];
static uint8_t deq_types[8];
static uint8_t *reassembly_result;
static uint16_t flow_handle;

void hciCmdInit(void) { ++cmd_init_calls; }
void *hciCoreConnByHandle(uint16_t handle) { return handle == connection_handle ? connection : 0; }
void hciCoreTxReady(uint8_t value) { ++tx_ready_calls; tx_ready_value = value; }
void hciCmdTimeout(void *message) { (void)message; ++timeout_calls; }
void hciEvtProcessMsg(uint8_t *message) { (void)message; ++evt_calls; }
void hciCoreResetSequence(uint8_t *message) { (void)message; ++reset_calls; }
uint8_t *hciCoreAclReassembly(uint8_t *message) { (void)message; return reassembly_result; }
void WsfMsgEnq(void *queue, uint8_t type, void *message) {
    (void)queue; ++enq_calls; enq_type = type; enq_message = message;
}
void *WsfMsgDeq(void *queue, uint8_t *type) {
    (void)queue; if (!deq_messages[deq_index]) return 0;
    *type = deq_types[deq_index]; return deq_messages[deq_index++];
}
void WsfMsgFree(void *message) { (void)message; ++free_calls; }
void WsfSetEvent(uint8_t handler, uint8_t event) { set_handler = handler; set_event = event; }
static void acl_callback(uint8_t *data) { (void)data; ++acl_calls; }
static void iso_callback(uint8_t *data) { (void)data; ++iso_calls; }
static void flow_callback(uint16_t handle, bool disabled) {
    if (!disabled) { ++flow_calls; flow_handle = handle; }
}
void test_reset(void) {
    open_cfw_hci_core_ps_reset_for_test(); memset(connection, 0, sizeof(connection));
    connection_handle = 0xffff; cmd_init_calls = tx_ready_calls = timeout_calls = 0;
    evt_calls = reset_calls = enq_calls = deq_index = free_calls = 0;
    acl_calls = iso_calls = flow_calls = 0; tx_ready_value = enq_type = 0;
    set_handler = set_event = 0; enq_message = 0; reassembly_result = 0;
    memset(deq_messages, 0, sizeof(deq_messages)); memset(deq_types, 0, sizeof(deq_types));
    open_cfw_hci_core_ps_set_callbacks_for_test(acl_callback, flow_callback, iso_callback);
}
void test_connection(uint16_t handle, uint8_t flow, uint8_t queued, uint8_t out) {
    connection_handle = handle; connection[0x17] = flow; connection[0x18] = queued; connection[0x19] = out;
}
uint8_t test_connection_byte(unsigned i) { return i < sizeof(connection) ? connection[i] : 0; }
void test_queue(unsigned i, uint8_t type, uint8_t *message) {
    if (i < 8) { deq_types[i] = type; deq_messages[i] = message; }
}
void test_reassembly(uint8_t *message) { reassembly_result = message; }
unsigned test_counter(unsigned i) {
    unsigned v[] = {cmd_init_calls,tx_ready_calls,timeout_calls,evt_calls,reset_calls,enq_calls,
                    free_calls,acl_calls,iso_calls,flow_calls};
    return i < sizeof(v)/sizeof(v[0]) ? v[i] : 0;
}
uint8_t test_tx_ready(void) { return tx_ready_value; }
uint8_t test_enq_type(void) { return enq_type; }
uint8_t test_set_handler(void) { return set_handler; }
uint8_t test_set_event(void) { return set_event; }
uint16_t test_flow_handle(void) { return flow_handle; }
"""


class CordioHciCorePsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        directory = Path(cls.tmp.name)
        harness = directory / "harness.c"
        harness.write_text(HARNESS)
        library = directory / "libhci_core_ps.so"
        subprocess.run([
            "clang", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
            "-DOPEN_CFW_HCI_CORE_PS_TEST=1", "-I", str(INCLUDE), str(SOURCE),
            str(harness), "-o", str(library),
        ], check=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.hciCoreNumCmplPkts.argtypes = [ctypes.POINTER(ctypes.c_uint8)]
        cls.lib.hciCoreRecv.argtypes = [ctypes.c_uint8, ctypes.POINTER(ctypes.c_uint8)]
        cls.lib.HciCoreHandler.argtypes = [ctypes.c_uint8, ctypes.c_void_p]
        cls.lib.HciGetLeSupFeat.restype = ctypes.c_uint64
        cls.lib.HciGetLeSupFeat32.restype = ctypes.c_uint32
        cls.lib.HciGetBdAddr.restype = ctypes.POINTER(ctypes.c_uint8)
        cls.lib.HciGetSupStates.restype = ctypes.POINTER(ctypes.c_uint8)
        cls.lib.open_cfw_hci_core_ps_set_core_u64_for_test.argtypes = [ctypes.c_uint16, ctypes.c_uint64]
        cls.lib.test_queue.argtypes = [ctypes.c_uint, ctypes.c_uint8, ctypes.POINTER(ctypes.c_uint8)]
        cls.lib.test_reassembly.argtypes = [ctypes.POINTER(ctypes.c_uint8)]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def setUp(self) -> None:
        self.lib.test_reset()

    @staticmethod
    def buffer(values: list[int]):
        return (ctypes.c_uint8 * len(values))(*values)

    def test_init_and_completed_packet_accounting_saturate(self) -> None:
        self.lib.hciCoreInit()
        self.assertEqual(self.lib.test_counter(0), 1)
        self.lib.open_cfw_hci_core_ps_set_core_u8_for_test(0x81, 2)
        self.lib.test_connection(0x1234, 1, 3, 2)
        message = self.buffer([1, 0x34, 0x12, 5, 0])
        self.lib.hciCoreNumCmplPkts(message)
        self.assertEqual((self.lib.test_connection_byte(0x18), self.lib.test_connection_byte(0x19)), (1, 0))
        self.assertEqual((self.lib.test_counter(1), self.lib.test_tx_ready()), (1, 2))
        self.assertEqual((self.lib.test_counter(9), self.lib.test_flow_handle()), (1, 0x1234))

    def test_receive_queue_and_unknown_type_fail_closed(self) -> None:
        self.lib.open_cfw_hci_core_ps_set_handler_for_test(7, False)
        message = self.buffer([1, 2, 3, 4])
        self.lib.hciCoreRecv(4, message)
        self.assertEqual((self.lib.test_counter(5), self.lib.test_enq_type()), (1, 4))
        self.assertEqual((self.lib.test_set_handler(), self.lib.test_set_event()), (7, 1))
        self.lib.hciCoreRecv(0xff, message)
        self.assertEqual(self.lib.test_counter(6), 1)
        self.lib.hciCoreRecv(4, None)
        self.assertEqual(self.lib.test_counter(5), 1)

    def test_handler_timeout_event_acl_iso_and_unknown(self) -> None:
        timeout = self.buffer([0, 0, 1, 0])
        self.lib.HciCoreHandler(0, timeout)
        self.assertEqual(self.lib.test_counter(2), 1)

        event, acl, iso, unknown = [self.buffer([i, 0, 0, 0]) for i in range(4)]
        self.lib.test_queue(0, 4, event)
        self.lib.test_queue(1, 2, acl)
        self.lib.test_queue(2, 5, iso)
        self.lib.test_queue(3, 9, unknown)
        self.lib.test_reassembly(acl)
        self.lib.open_cfw_hci_core_ps_set_handler_for_test(1, True)
        self.lib.HciCoreHandler(1, None)
        self.assertEqual((self.lib.test_counter(3), self.lib.test_counter(4)), (1, 1))
        self.assertEqual((self.lib.test_counter(7), self.lib.test_counter(8)), (1, 1))
        self.assertEqual(self.lib.test_counter(6), 2)

    def test_all_getters_use_authenticated_offsets(self) -> None:
        for offset, value in ((0x84, 6), (0x90, 0xfe), (0x83, 9), (0x91, 3),
                              (0x94, 2), (0x95, 4), (0x60, 0xaa), (0x68, 0xbb)):
            self.lib.open_cfw_hci_core_ps_set_core_u8_for_test(offset, value)
        self.lib.open_cfw_hci_core_ps_set_core_u16_for_test(0x7c, 0x1234)
        self.lib.open_cfw_hci_core_ps_set_core_u16_for_test(0x7e, 0x5678)
        self.lib.open_cfw_hci_core_ps_set_core_u16_for_test(0x92, 0x9abc)
        self.lib.open_cfw_hci_core_ps_set_core_u64_for_test(0x88, 0x112233445566778b)
        self.assertEqual(self.lib.HciGetWhiteListSize(), 6)
        self.assertEqual(ctypes.c_int8(self.lib.HciGetAdvTxPwr()).value, -2)
        self.assertEqual((self.lib.HciGetBufSize(), self.lib.HciGetMaxRxAclLen()), (0x5678, 0x1234))
        self.assertEqual((self.lib.HciGetNumBufs(), self.lib.HciGetResolvingListSize()), (9, 3))
        self.assertTrue(self.lib.HciLlPrivacySupported())
        self.assertEqual((self.lib.HciGetMaxAdvDataLen(), self.lib.HciGetNumSupAdvSets()), (0x9abc, 2))
        self.assertTrue(self.lib.HciLeAdvExtSupported())
        self.assertEqual(self.lib.HciGetPerAdvListSize(), 4)
        self.assertEqual(self.lib.HciGetLeSupFeat(), 0x1122334455667789)
        self.assertEqual(self.lib.HciGetLeSupFeat32(), 0x55667789)
        self.assertEqual(self.lib.HciGetSupStates()[0], 0xaa)
        self.assertEqual(self.lib.HciGetBdAddr()[0], 0xbb)

    def test_cortex_m55_translation_unit_and_all_apis_compile(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "hci_core_ps.o"
            subprocess.run([
                "clang", "--target=thumbv7em-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                "-O2", "-ffreestanding", "-fno-builtin", "-ffunction-sections",
                "-fdata-sections", "-Wall", "-Wextra", "-Werror",
                "-DOPEN_CFW_HCI_CORE_PS_PRODUCTION=1", "-I", str(INCLUDE), "-c",
                str(SOURCE), "-o", str(output),
            ], check=True)
            symbols = subprocess.run(["nm", "-g", str(output)], check=True,
                                     capture_output=True, text=True).stdout
            for function in ("hciCoreInit", "hciCoreNumCmplPkts", "hciCoreRecv",
                             "HciCoreHandler", "HciGetBdAddr", "HciGetWhiteListSize",
                             "HciGetAdvTxPwr", "HciGetBufSize", "HciGetNumBufs",
                             "HciGetSupStates", "HciGetLeSupFeat", "HciGetLeSupFeat32",
                             "HciGetMaxRxAclLen", "HciGetResolvingListSize",
                             "HciLlPrivacySupported", "HciGetMaxAdvDataLen",
                             "HciGetNumSupAdvSets", "HciLeAdvExtSupported",
                             "HciGetPerAdvListSize", "HciGetLocalVerInfo"):
                self.assertIn(function, symbols)


if __name__ == "__main__":
    unittest.main()
