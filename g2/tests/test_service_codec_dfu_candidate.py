import ctypes
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"components/apollo_main/core_overlay/service_codec_dfu.c"
FIXTURE=ROOT/"tests/fixtures/service_codec_dfu_host.c"
HEADER=ROOT/"tests/fixtures/service_codec_dfu_host.h"
NAMES=("open_cfw_dfu_load_package","open_cfw_dfu_release_package","open_cfw_dfu_format_version","open_cfw_dfu_parse_version_bytes","open_cfw_dfu_get_package_version","open_cfw_dfu_validate_firmware_header","open_cfw_dfu_host_is_little_endian","open_cfw_dfu_bswap32","open_cfw_dfu_host_to_be32","open_cfw_dfu_wait_token","open_cfw_dfu_read_boot_header","open_cfw_dfu_download_boot_stage1","open_cfw_dfu_download_boot_stage2","open_cfw_dfu_flash_image","open_cfw_svc_codec_dfu","open_cfw_svc_codec_check_and_upgrade")

class CodecDfuCandidateTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();lib=Path(cls.tmp.name)/("dfu.dylib" if os.uname().sysname=="Darwin" else "dfu.so")
  cmd=[os.environ.get("OPENCFW_CLANG","/usr/bin/clang"),"-O2","-Wall","-Wextra","-Werror","-include",str(HEADER),str(SOURCE),str(FIXTURE),"-I",str(HEADER.parent)]
  cmd += (["-dynamiclib","-o",str(lib)] if os.uname().sysname=="Darwin" else ["-shared","-fPIC","-o",str(lib)])
  subprocess.run(cmd,check=True,capture_output=True);cls.lib=ctypes.CDLL(str(lib));cls.lib.host_dfu_set_rx.argtypes=[ctypes.c_void_p,ctypes.c_uint32]
  cls.lib.host_dfu_copy_tx.argtypes=[ctypes.c_void_p,ctypes.c_uint32];cls.lib.host_dfu_copy_tx.restype=ctypes.c_uint32
  cls.lib.open_cfw_dfu_crc32.argtypes=[ctypes.c_void_p,ctypes.c_uint32];cls.lib.open_cfw_dfu_crc32.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def setUp(self):self.lib.host_dfu_reset()
 def test_all_target_selectors_compile_strictly(self):
  flags=["--target=thumbv7em-none-eabi","-mthumb","-mcpu=cortex-m55","-O2","-ffreestanding","-fno-jump-tables","-fomit-frame-pointer","-fno-builtin","-mno-unaligned-access","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-fropi","-ffunction-sections","-fdata-sections","-Wall","-Wextra","-Werror","-mllvm","-enable-machine-outliner=never"]
  for i,name in enumerate(NAMES,1):
   obj=Path(self.tmp.name)/f"{i}.o";subprocess.run([os.environ.get("OPENCFW_CLANG","/usr/bin/clang"),*flags,f"-DOPEN_CFW_SELECTOR={i}","-c",str(SOURCE),"-o",str(obj)],check=True,capture_output=True);self.assertGreater(obj.stat().st_size,0,name)
 def test_package_load_crc_and_release(self):
  self.lib.host_dfu_make_package(0,0);self.assertEqual(self.lib.open_cfw_dfu_load_package(),0)
  self.assertEqual(ctypes.c_uint32.in_dll(self.lib,"codec_dfu_boot_size").value,96);self.assertEqual(ctypes.c_uint32.in_dll(self.lib,"codec_dfu_firmware_size").value,96)
  self.lib.open_cfw_dfu_release_package();self.assertEqual(ctypes.c_uint32.in_dll(self.lib,"codec_dfu_boot_size").value,0)
  self.lib.host_dfu_make_package(1,0);self.assertEqual(self.lib.open_cfw_dfu_load_package(),-1)
  self.lib.host_dfu_make_package(0,1);self.assertEqual(self.lib.open_cfw_dfu_load_package(),-1)
 def test_version_helpers(self):
  out=ctypes.create_string_buffer(32);self.assertGreater(self.lib.open_cfw_dfu_format_version(0x01020304,out,32),0);self.assertEqual(out.value,b"1.2.3.4")
  raw=(ctypes.c_ubyte*4)(1,2,3,4);value=ctypes.c_uint32();self.assertEqual(self.lib.open_cfw_dfu_parse_version_bytes(raw,ctypes.byref(value)),0);self.assertEqual(value.value,0x01020304)
  self.assertEqual(self.lib.open_cfw_dfu_bswap32(0x11223344),0x44332211)
 def test_token_match_and_timeout(self):
  data=ctypes.create_string_buffer(b"noise~sta~");self.lib.host_dfu_set_rx(data,len(data.raw)-1);token=ctypes.create_string_buffer(b"~sta~")
  self.assertEqual(self.lib.open_cfw_dfu_wait_token(token,5,100),0);self.assertEqual(self.lib.open_cfw_dfu_wait_token(token,5,3),-1)
 def test_check_upgrade_skip_and_cache(self):
  self.lib.host_dfu_make_package(0,0);self.lib.host_dfu_set_codec_version(0x01020304);self.assertEqual(self.lib.open_cfw_svc_codec_check_and_upgrade(False),1)
 def tx(self):
  result=(ctypes.c_ubyte*32768)();size=self.lib.host_dfu_copy_tx(result,len(result));return bytes(result[:size])
 def rx(self,data):
  buffer=ctypes.create_string_buffer(data);self.lib.host_dfu_set_rx(buffer,len(data))
 def test_boot_stages_match_recovered_wire_contract(self):
  self.lib.host_dfu_make_package(0,0);self.assertEqual(self.lib.open_cfw_dfu_load_package(),0);self.assertEqual(self.lib.open_cfw_dfu_read_boot_header(),0)
  boot_pointer=ctypes.c_void_p.in_dll(self.lib,"codec_dfu_boot_buffer").value;boot=ctypes.string_at(boot_pointer,96)
  self.rx(b"wfbOKGETGET");self.assertEqual(self.lib.open_cfw_dfu_download_boot_stage1(),0)
  self.assertEqual(self.tx(),b"\x59\x08\x00\x00\x00"+boot[32:64]+b"GET\x40\x42\x0f\x00OK")
  self.lib.host_dfu_clear_tx();self.rx(b"readyOboot>");self.assertEqual(self.lib.open_cfw_dfu_download_boot_stage2(),0)
  self.assertEqual(self.tx(),b"\x53\x44\x33\x22\x11\x20\x00\x00\x00"+boot[64:96])
 def test_flash_matches_recovered_command_and_ack_contract(self):
  self.lib.host_dfu_make_package(0,0);self.assertEqual(self.lib.open_cfw_dfu_load_package(),0);self.rx(b"~sta~~fin~[Result]:SUCC")
  firmware_pointer=ctypes.c_void_p.in_dll(self.lib,"codec_dfu_firmware_buffer").value;firmware=ctypes.string_at(firmware_pointer,96)
  self.assertEqual(self.lib.open_cfw_dfu_flash_image(),0);crc=self.lib.open_cfw_dfu_crc32(firmware_pointer,96)&0xffffffff
  self.assertEqual(self.tx(),b"serialdown 0 96 8192"+crc.to_bytes(4,"little")+firmware)
 def test_end_to_end_dfu_success_and_cleanup(self):
  self.lib.host_dfu_make_package(0,0);self.rx(b"MwfbOKGETGETreadyOboot>~sta~~fin~[Result]:SUCC")
  self.assertEqual(self.lib.open_cfw_svc_codec_dfu(),0);self.assertEqual(ctypes.c_uint32.in_dll(self.lib,"codec_dfu_boot_size").value,0)
  self.assertEqual(self.lib.host_dfu_reboot_true_count(),1);self.assertEqual(self.lib.host_dfu_reboot_false_count(),1)

if __name__=="__main__":unittest.main()
