from __future__ import annotations

import ctypes
import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_fifo_adapters_423350.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_hw_fifo_adapters_host.c"

class Instance(ctypes.Structure): _fields_ = [("bytes", ctypes.c_uint8 * 0x11C)]

class BootloaderHardwareFifoAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory(); output = Path(cls.tmp.name) / ("hw-fa.dylib" if sys.platform == "darwin" else "hw-fa.so")
        subprocess.run([os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE), *( ["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"] ), "-o", str(output)], check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(output)); cls.snapshot = cls.lib.open_cfw_bootloader_hw_fifo_snapshot_423350; cls.snapshot.argtypes=[ctypes.POINTER(Instance)]; cls.snapshot.restype=ctypes.c_uint32
        cls.pump = cls.lib.open_cfw_bootloader_hw_fifo_pump_423390; cls.pump.argtypes=[ctypes.POINTER(Instance)]; cls.pump.restype=ctypes.c_uint32
        for n in ("token","enter_count","restore_count","restored_token","fifo_read_status","fifo_read_count","consume_result","consume_count","consume_length","status_position","descriptor_position","fifo_write_status","fifo_write_count"): setattr(cls,n,ctypes.c_uint32.in_dll(cls.lib,"open_cfw_hwfa_host_"+n))
        cls.read_bytes=(ctypes.c_uint8*32).in_dll(cls.lib,"open_cfw_hwfa_host_fifo_read_bytes"); cls.status_values=(ctypes.c_uint32*32).in_dll(cls.lib,"open_cfw_hwfa_host_status_values"); cls.descriptor_results=(ctypes.c_uint32*32).in_dll(cls.lib,"open_cfw_hwfa_host_descriptor_results"); cls.descriptor_bytes=(ctypes.c_uint8*32).in_dll(cls.lib,"open_cfw_hwfa_host_descriptor_bytes"); cls.write_bytes=(ctypes.c_uint8*32).in_dll(cls.lib,"open_cfw_hwfa_host_fifo_write_bytes")
    @classmethod
    def tearDownClass(cls)->None: cls.tmp.cleanup()
    def setUp(self)->None:
        for n in ("enter_count","restore_count","restored_token","fifo_read_status","fifo_read_count","consume_result","consume_count","consume_length","status_position","descriptor_position","fifo_write_status","fifo_write_count"): getattr(self,n).value=0
        self.token.value=0xA5A55A5A
        for a in (self.read_bytes,self.status_values,self.descriptor_results,self.descriptor_bytes,self.write_bytes):
            for i in range(32): a[i]=0
    @staticmethod
    def instance(index=0):
        v=Instance()
        for s in range(4): v.bytes[0x28+s]=(index>>(8*s))&255
        return v
    def test_authenticated_bodies_providers_pool_and_boundaries(self):
        b=OFFICIAL.read_bytes(); self.assertEqual(hashlib.sha256(b[0x13350:0x13390]).hexdigest(),"c50cb54905aafef204f60cc0a71919f9701853167579f85c789ee7729b8e9892"); self.assertEqual(hashlib.sha256(b[0x13390:0x133E0]).hexdigest(),"a51ed43345c464477c7c15d21737e0eb5ec937c962de4369b7da174c5a1088d7"); self.assertEqual(int.from_bytes(b[0x1385C:0x13860],"little"),0x08000001); self.assertEqual(b[0x133E0:0x133E8].hex(),"069eea0100440220")
    def test_snapshot_maps_empty_consume_and_preserves_other_statuses(self):
        v=self.instance(); self.read_bytes[:3]=(1,2,3); self.fifo_read_count.value=3
        self.assertEqual(self.snapshot(ctypes.byref(v)),0x08000001); self.assertEqual((self.consume_count.value,self.consume_length.value),(1,3))
        self.consume_result.value=1; self.assertEqual(self.snapshot(ctypes.byref(v)),0)
        self.fifo_read_status.value=0x08000002; self.assertEqual(self.snapshot(ctypes.byref(v)),0x08000002)
    def test_pump_moves_descriptor_bytes_until_full_or_empty(self):
        v=self.instance(2); self.status_values[:4]=(0,0,0,1<<5); self.descriptor_results[:3]=(1,1,1); self.descriptor_bytes[:3]=(9,8,7)
        self.assertEqual(self.pump(ctypes.byref(v)),0); self.assertEqual((list(self.write_bytes[:3]),self.fifo_write_count.value),([9,8,7],3))
        self.setUp(); self.status_values[0]=0; self.descriptor_results[0]=0; self.assertEqual(self.pump(ctypes.byref(v)),0); self.assertEqual(self.fifo_write_count.value,0)
    def test_critical_token_restored_on_all_paths(self):
        for function in (self.snapshot,self.pump):
            self.enter_count.value=self.restore_count.value=0; function(ctypes.byref(self.instance())); self.assertEqual((self.enter_count.value,self.restore_count.value,self.restored_token.value),(1,1,self.token.value))
    def test_source_cross_compiles(self):
        for c in ("/usr/bin/clang","/opt/homebrew/opt/llvm@22/bin/clang"):
            if Path(c).exists(): subprocess.run([c,"-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-c",str(SOURCE),"-o",str(Path(self.tmp.name)/(Path(c).parent.name+"-hwfa.o"))],check=True,capture_output=True)

if __name__=="__main__": unittest.main()
