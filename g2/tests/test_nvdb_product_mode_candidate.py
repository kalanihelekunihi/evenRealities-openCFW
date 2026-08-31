import ctypes,hashlib,platform,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'components/apollo_main/core_overlay/nvdb_product_mode.c';FIX=ROOT/'tests/fixtures'
SYMS={f'open_cfw_nvdb_product_mode_{x}' for x in ('default_crc_initialize','load_and_migrate','set','get','update','read')}
class NvdbProductModeCandidateTests(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.t=tempfile.TemporaryDirectory();c.lib=Path(c.t.name)/('p.dylib' if platform.system()=='Darwin' else 'p.so')
  subprocess.run(['clang','-std=c11','-shared','-fPIC','-O1','-include',str(FIX/'nvdb_product_mode_host.h'),str(SRC),str(FIX/'nvdb_product_mode_host.c'),'-o',str(c.lib)],check=True,cwd=ROOT);c.x=ctypes.CDLL(str(c.lib));c.x.open_cfw_nvdb_product_mode_get.restype=ctypes.c_ubyte;c.x.open_cfw_nvdb_product_mode_read.restype=ctypes.c_ubyte;c.x.open_cfw_test_nvdb_product_mode_set_stored.argtypes=[ctypes.POINTER(ctypes.c_ubyte),ctypes.c_int]
 @classmethod
 def tearDownClass(c):c.t.cleanup()
 def setUp(s):s.x.open_cfw_test_nvdb_product_mode_reset()
 def arr(s,n):return (ctypes.c_ubyte*4).in_dll(s.x,n)
 def word(s,n):return ctypes.c_uint.in_dll(s.x,n).value
 def stored(s,b,r=1):a=(ctypes.c_ubyte*4).from_buffer_copy(b);s.x.open_cfw_test_nvdb_product_mode_set_stored(a,r)
 def test_crc_set_update_and_read(s):
  s.assertEqual(s.x.open_cfw_nvdb_product_mode_default_crc_initialize(),0);s.assertEqual(bytes(s.arr('open_cfw_test_nvdb_product_mode_record')),bytes.fromhex('01003e2e'))
  s.x.open_cfw_nvdb_product_mode_set(3);s.assertEqual(s.x.open_cfw_nvdb_product_mode_get(),3)
  s.x.open_cfw_nvdb_product_mode_update(5);s.assertEqual(s.word('open_cfw_test_nvdb_product_mode_writes'),1);s.assertEqual(bytes(s.arr('open_cfw_test_nvdb_product_mode_written')),bytes.fromhex('01059b7e'))
  s.stored(bytes.fromhex('01073e2e'));s.assertEqual(s.x.open_cfw_nvdb_product_mode_read(),7);s.assertEqual(s.x.open_cfw_nvdb_product_mode_get(),7)
 def test_migration_policy(s):
  s.x.open_cfw_nvdb_product_mode_default_crc_initialize();s.stored(bytes(4),0);s.x.open_cfw_nvdb_product_mode_load_and_migrate();s.assertEqual(s.word('open_cfw_test_nvdb_product_mode_writes'),1)
  s.x.open_cfw_test_nvdb_product_mode_reset();s.x.open_cfw_nvdb_product_mode_default_crc_initialize();s.stored(bytes.fromhex('00000000'));s.x.open_cfw_nvdb_product_mode_load_and_migrate();s.assertEqual(s.word('open_cfw_test_nvdb_product_mode_writes'),1)
  s.x.open_cfw_test_nvdb_product_mode_reset();s.x.open_cfw_nvdb_product_mode_default_crc_initialize();s.stored(bytes.fromhex('01020000'));s.x.open_cfw_nvdb_product_mode_load_and_migrate();s.assertEqual(s.word('open_cfw_test_nvdb_product_mode_writes'),0)
 def test_thumb_and_hash(s):
  with tempfile.TemporaryDirectory() as d:
   o=Path(d)/'p.o';subprocess.run(['clang','-target','thumbv7em-none-eabi','-mthumb','-O2','-ffreestanding','-fno-builtin','-fropi','-Wall','-Wextra','-Werror','-c',str(SRC),'-o',str(o)],check=True,cwd=ROOT)
   out=subprocess.run(['nm',str(o)],check=True,capture_output=True,text=True).stdout;got={p[2] for l in out.splitlines() if len(p:=l.split())==3 and p[1]=='T'};s.assertEqual(got,SYMS)
  s.assertEqual(hashlib.sha256(SRC.read_bytes()).hexdigest(),'f02df8296dce95390a54141341cc546668361f3b8acc28b28746976952ecf05e')
if __name__=='__main__':unittest.main()
