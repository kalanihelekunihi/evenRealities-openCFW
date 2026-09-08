# SPDX-License-Identifier: MIT
import ctypes
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verify_gx8002_model_interface import ROOT,SOURCE


class Task(ctypes.Structure):
    _fields_=[('module_id',ctypes.c_int)]+[(name,ctypes.c_void_p) for name in ('ops','data','input','output','cmd','tmp_mem','weight')]


class ModelInterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sdk=ROOT/'build/upstream-nationalchip-lvp-kws'
        if not (sdk/'include/driver/gx_snpu.h').exists():raise unittest.SkipTest('optional upstream SDK absent')
        cls.temporary=tempfile.TemporaryDirectory();cls.addClassCleanup(cls.temporary.cleanup)
        root=Path(cls.temporary.name)
        (root/'autoconf.h').write_text('#define CONFIG_ARCH_GRUS 1\n')
        fixture=root/'fixture.c';fixture.write_text('#include <driver/gx_snpu.h>\nGX_SNPU_TASK open_cfw_gx8002_saved_task;\n')
        library=root/'model.so'
        subprocess.run(['/usr/bin/clang','-O2','-shared','-fPIC','-std=c11','-Wall','-Wextra','-Werror',
                        '-DOPEN_CFW_GX8002_MODEL_HOST_TEST','-I',str(root),'-I',str(sdk/'include'),
                        str(SOURCE),str(SOURCE.with_name('runtime_gx8002_model_set_task.c')),
                        str(SOURCE.with_name('runtime_gx8002_memcpy.c')),str(fixture),'-o',str(library)],check=True,capture_output=True)
        cls.lib=ctypes.CDLL(str(library));cls.saved=Task.in_dll(cls.lib,'open_cfw_gx8002_saved_task')
        cls.lib.LvpCTCModelInitSnpuTask.argtypes=[ctypes.POINTER(Task)]
        cls.lib.LvpCTCModelInitSnpuTask.restype=ctypes.c_int

    def test_saved_task_copy_then_translation(self):
        self.lib.LvpSetSnpuTask.argtypes = [ctypes.POINTER(Task)]
        self.lib.LvpSetSnpuTask.restype = None
        rng = random.Random(0x121a0)
        for _ in range(1024):
            original = Task()
            for field, _ in Task._fields_:
                setattr(original, field, rng.getrandbits(32))
            before = bytes(original)
            self.lib.LvpSetSnpuTask(ctypes.byref(original))
            self.assertEqual(bytes(self.saved), before)
            self.assertEqual(bytes(original), before)
            translated = Task()
            self.assertEqual(self.lib.LvpCTCModelInitSnpuTask(ctypes.byref(translated)), 0)
            for field in ('ops', 'data', 'cmd', 'tmp_mem', 'weight'):
                self.assertEqual(getattr(translated, field) or 0,
                                 (getattr(original, field) or 0) & 0xfffffff)

    def test_sizes_and_buffer_offsets(self):
        for suffix,value in [('Cmd',9164),('Weight',120800),('Ops',0),('Data',13056),('Tmp',4)]:
            fn=getattr(self.lib,'LvpModelGet'+suffix+'Size');fn.restype=ctypes.c_int
            self.assertEqual(fn(),value)
        self.assertEqual(self.lib.LvpCTCModelGetSnpuFeatsDim(),520)
        for name,offset in [('Out',8464),('Feats',0),('State',1040)]:
            fn=getattr(self.lib,'LvpCTCModelGetSnpu'+name+'Buffer')
            fn.argtypes=[ctypes.c_void_p];fn.restype=ctypes.c_void_p
            for base in (0,0x10003000,0x20000000,0x20020000):
                self.assertEqual(fn(base) or 0,base+offset)

    def test_task_translation_preserves_input_output_and_aliasing(self):
        rng=random.Random(0x2002e85c)
        for alias in (False,True):
            for _ in range(1024):
                for field,_ in Task._fields_:
                    setattr(self.saved,field,rng.getrandbits(32))
                task=self.saved if alias else Task()
                if not alias:
                    for field,_ in Task._fields_:setattr(task,field,rng.getrandbits(32))
                preserved={field:getattr(task,field) for field in ('input','output')}
                translated={field:(getattr(self.saved,field) or 0)&0xfffffff
                            for field in ('ops','data','cmd','tmp_mem','weight')}
                self.assertEqual(self.lib.LvpCTCModelInitSnpuTask(ctypes.byref(task)),0)
                self.assertEqual(task.module_id,256)
                for field,value in preserved.items():self.assertEqual(getattr(task,field),value)
                for field,value in translated.items():self.assertEqual(getattr(task,field) or 0,value)


if __name__=='__main__':unittest.main()
