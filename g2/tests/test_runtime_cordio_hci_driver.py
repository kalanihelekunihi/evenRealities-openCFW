#!/usr/bin/env python3
"""Host behavior and Cortex-M55 compile tests for the clean-room HCI driver."""
from __future__ import annotations

import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "components/shared/cordio/runtime_cordio_hci_driver.c"
INC = ROOT / "components/shared/cordio"
HARNESS = r"""
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include "runtime_cordio_hci_driver.h"
typedef struct { volatile uint32_t w,r,n,cap,item; uint8_t *data; } queue_t;
static unsigned events, starts, stops, resets, reads, writes, boots, shutdowns;
static unsigned constants, carriers, sleeps, errors; static uint8_t last_handler,last_event;
static uint16_t last_opcode; static uint8_t last_len,last_payload[16];
static bool irq; static uint32_t read_status,write_status; static uint8_t inbound[256]; static uint32_t inbound_len;
void open_cfw_hci_driver_queue_init(queue_t*q,void*d,uint32_t item,uint32_t total){q->w=q->r=q->n=0;q->cap=total;q->item=item;q->data=d;}
void open_cfw_hci_driver_queue_add(queue_t*q,uint32_t unused,uint32_t count){(void)unused;q->w=(q->w+q->item*count)%q->cap;q->n+=q->item*count;}
void open_cfw_hci_driver_queue_remove(queue_t*q,uint32_t unused,uint32_t count){(void)unused;q->r=(q->r+q->item*count)%q->cap;q->n-=q->item*count;}
void WsfSetEvent(uint8_t h,uint8_t e){++events;last_handler=h;last_event=e;}void WsfTimerStartMs(void*t,uint32_t ms){(void)t;if(ms==10000)++starts;}void WsfTimerStop(void*t){(void)t;++stops;}
void HciReadBufSizeCmd(void){last_opcode=0x1005;}void DmDevReset(void){++resets;}
void HciVendorSpecificCmd(uint16_t op,uint8_t len,const uint8_t*p){unsigned i;last_opcode=op;last_len=len;for(i=0;i<len&&i<16;++i)last_payload[i]=p[i];}
uint16_t hciTrSerialRxIncoming(const uint8_t*d,uint16_t n){(void)d;return n;}
uint32_t open_cfw_hci_driver_hal_boot(bool cold,uint8_t*a){++boots;if(cold){unsigned i;for(i=0;i<6;++i)a[i]=(uint8_t)(i+1);}return 0;}
void open_cfw_hci_driver_hal_shutdown(void){++shutdowns;}bool open_cfw_hci_driver_hal_irq_pending(void){return irq;}
uint32_t open_cfw_hci_driver_hal_read(uint8_t*d,uint32_t cap,uint32_t*n){++reads;if(inbound_len>cap){*n=inbound_len;return read_status;}memcpy(d,inbound,inbound_len);*n=inbound_len;irq=false;return read_status;}
uint32_t open_cfw_hci_driver_hal_write(const uint8_t*d,uint32_t n){++writes;last_len=(uint8_t)n;memcpy(last_payload,d,n<16?n:16);return write_status;}
void open_cfw_hci_driver_hal_constant_transmission(uint8_t c){constants=c+1;}void open_cfw_hci_driver_hal_carrier_wave(uint8_t c){carriers=c+1;}void open_cfw_hci_driver_hal_sleep(bool e){sleeps=e?2:1;}
static void err(uint32_t status){errors=status;}
void test_reset(void){open_cfw_hci_driver_reset_for_test();events=starts=stops=resets=reads=writes=boots=shutdowns=constants=carriers=sleeps=errors=0;last_handler=last_event=last_len=0;last_opcode=0;irq=false;read_status=write_status=inbound_len=0;memset(last_payload,0,sizeof(last_payload));HciDrvErrorHandlerSet(err);}
unsigned test_count(unsigned i){unsigned v[]={events,starts,stops,resets,reads,writes,boots,shutdowns,constants,carriers,sleeps,errors};return i<12?v[i]:0;}uint8_t test_byte(unsigned i){return i<16?last_payload[i]:0;}uint16_t test_opcode(void){return last_opcode;}uint8_t test_len(void){return last_len;}uint8_t test_handler(void){return last_handler;}uint8_t test_event(void){return last_event;}
void test_inbound(uint32_t n,uint32_t status){unsigned i;inbound_len=n;read_status=status;irq=true;for(i=0;i<n&&i<256;++i)inbound[i]=(uint8_t)i;}void test_write_status(uint32_t s){write_status=s;}
"""


class CordioHciDriverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        directory = Path(cls.tmp.name)
        harness = directory / "harness.c"
        harness.write_text(HARNESS)
        library = directory / "driver.so"
        subprocess.run(
            ["clang", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
             "-DOPEN_CFW_HCI_DRIVER_TEST=1", "-I", str(INC), str(SRC), str(harness),
             "-o", str(library)], check=True
        )
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.hciDrvWrite.argtypes = [ctypes.c_uint8, ctypes.c_uint16,
                                        ctypes.POINTER(ctypes.c_uint8)]
        cls.lib.hciDrvWrite.restype = ctypes.c_uint16
        cls.lib.HciVscSetRfPowerLevelEx.argtypes = [ctypes.c_int8]
        cls.lib.HciVscSetRfPowerLevelEx.restype = ctypes.c_bool
        cls.lib.HciVscSetCustom_BDAddr.argtypes = [ctypes.POINTER(ctypes.c_uint8)]
        cls.lib.HciVscSetCustom_BDAddr.restype = ctypes.c_bool
        cls.lib.open_cfw_hci_driver_mac_for_test.restype = ctypes.POINTER(ctypes.c_uint8)
        cls.lib.open_cfw_hci_driver_nvds_for_test.restype = ctypes.POINTER(ctypes.c_uint8)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def setUp(self) -> None:
        self.lib.test_reset()
        self.lib.HciDrvHandlerInit(7)

    def test_queue_payload_schedule_and_bounds(self) -> None:
        payload = (ctypes.c_uint8 * 3)(0xAA, 0xBB, 0xCC)
        self.assertEqual(self.lib.hciDrvWrite(1, 3, payload), 3)
        self.assertEqual((self.lib.test_count(0), self.lib.test_handler(), self.lib.test_event()),
                         (1, 7, 1))
        self.lib.HciDrvHandler(1, None)
        self.assertEqual(self.lib.test_count(5), 1)
        self.assertEqual(bytes(self.lib.test_byte(i) for i in range(4)), b"\x01\xaa\xbb\xcc")
        self.assertEqual(self.lib.hciDrvWrite(1, 259, payload), 259)
        self.assertEqual(self.lib.open_cfw_hci_driver_error_for_test(), 0x09000001)

    def test_vendor_commands_and_address_validation(self) -> None:
        self.lib.HciVscUpdateNvdsParam()
        self.assertEqual((self.lib.test_opcode(), self.lib.test_len()), (0xFFF2, 8))
        self.assertEqual(bytes(self.lib.test_byte(i) for i in range(8)),
                         bytes([0xFF, 0x7C, 1, 0x0F, 0xB8, 0x19, 0, 0]))
        self.assertFalse(self.lib.HciVscSetRfPowerLevelEx(-28))
        self.assertTrue(self.lib.HciVscSetRfPowerLevelEx(-27))
        self.assertTrue(self.lib.HciVscSetRfPowerLevelEx(6))
        self.assertFalse(self.lib.HciVscSetRfPowerLevelEx(7))
        address = (ctypes.c_uint8 * 6)(1, 2, 3, 4, 5, 6)
        zeros = (ctypes.c_uint8 * 6)()
        self.assertFalse(self.lib.HciVscSetCustom_BDAddr(None))
        self.assertFalse(self.lib.HciVscSetCustom_BDAddr(zeros))
        self.assertTrue(self.lib.HciVscSetCustom_BDAddr(address))
        self.lib.HciVscUpdateBDAddress()
        self.assertEqual((self.lib.test_opcode(), self.lib.test_len()), (0xFC43, 6))
        self.assertEqual(bytes(self.lib.test_byte(i) for i in range(6)), bytes(address))

    def test_interrupt_heartbeat_and_hardware_adapter_paths(self) -> None:
        self.lib.HciDrvIntService()
        self.assertEqual((self.lib.open_cfw_hci_driver_interrupts_for_test(),
                          self.lib.test_count(0)), (1, 1))
        message = (ctypes.c_uint8 * 4)(0, 0, 2, 0)
        self.lib.HciDrvHandler(0, message)
        self.assertEqual((self.lib.test_opcode(), self.lib.test_count(1)), (0x1005, 1))
        self.lib.test_inbound(4, 0)
        self.lib.HciDrvHandler(1, None)
        self.assertEqual(self.lib.test_count(4), 1)
        self.assertEqual(self.lib.HciDrvRadioBoot(True), 0)
        self.assertEqual(bytes(self.lib.open_cfw_hci_driver_mac_for_test()[i] for i in range(6)),
                         bytes([1, 2, 3, 4, 5, 6]))
        self.lib.HciDrvRadioShutdown()
        self.assertEqual((self.lib.test_count(6), self.lib.test_count(7)), (1, 1))
        self.lib.HciVscConstantTransmission(4)
        self.lib.HciVscCarrierWaveMode(5)
        self.lib.HciDrvBleSleepSet(True)
        self.assertEqual([self.lib.test_count(i) for i in (8, 9, 10)], [5, 6, 2])

    def test_target_compile_exports_full_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            obj = Path(directory) / "driver.o"
            subprocess.run(
                ["clang", "--target=thumbv7em-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                 "-O2", "-ffreestanding", "-fno-builtin", "-ffunction-sections",
                 "-fdata-sections", "-Wall", "-Wextra", "-Werror",
                 "-DOPEN_CFW_HCI_DRIVER_PRODUCTION=1", "-I", str(INC), "-c", str(SRC),
                 "-o", str(obj)], check=True
            )
            symbols = subprocess.run(["nm", "-g", str(obj)], capture_output=True,
                                     text=True, check=True).stdout
            for name in (
                "error_check", "HciDrvRadioBoot", "HciDrvRadioShutdown", "hciDrvWrite",
                "HciDrvHandlerInit", "HciDrvIntService", "HciDrvHandler",
                "HciDrvErrorHandlerSet", "HciVscUpdateNvdsParam",
                "HciVscSetRfPowerLevelEx", "HciVscConstantTransmission",
                "HciVscSetCustom_BDAddr", "HciVscUpdateBDAddress",
                "HciVscCarrierWaveMode", "HciDrvBleSleepSet", "HciDrvEmptyWriteQueue",
            ):
                self.assertIn(f" T {name}\n", symbols)


if __name__ == "__main__":
    unittest.main()
