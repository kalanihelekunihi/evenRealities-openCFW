# SPDX-License-Identifier: MIT
import importlib.util,shutil,subprocess,tempfile,unittest,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
VERIFY=ROOT/'components/foundation/touch_scb/simulator/verify.py'
spec=importlib.util.spec_from_file_location('touch_scb_simulator',VERIFY)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class SimulatorBuildTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('clang') and shutil.which('arm-none-eabi-ld'),'ARM clang/linker unavailable')
    def test_links_source_defined_arm_module(self):
        with tempfile.TemporaryDirectory(prefix='touch-scb-link-') as directory:
            result=subprocess.run(['make','-C',str(ROOT),'touch-scb-simulator','SCB_SIM_DIR='+directory],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            data,segments,symbols=module.elf_info(Path(directory)/'touch_scb.elf')
            self.assertTrue(segments)
            for name in ['touch_scb_sim_read','touch_scb_sim_checked','touch_scb_mmio_read_array','touch_scb_sim_write','touch_scb_sim_write_checked','touch_scb_mmio_write_array','touch_scb_sim_set_rx_level','touch_scb_fifo_set_rx_level']:
                self.assertIn(name,symbols)
                self.assertTrue(any(s['flags']&1 and s['address']<=symbols[name]&~1<s['address']+len(s['data']) for s in segments))
            self.assertTrue((Path(directory)/'touch_scb.map').is_file())

    def test_invalid_elf_rejected(self):
        with tempfile.TemporaryDirectory(prefix='touch-scb-invalid-') as directory:
            path=Path(directory)/'invalid';path.write_bytes(b'not an ELF')
            with self.assertRaises(ValueError):module.elf_info(path)

    def test_optimized_python_rejects_verification(self):
        result=subprocess.run([sys.executable,'-O',str(VERIFY),'--help'],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('optimized Python is rejected',result.stderr)

if __name__=='__main__':unittest.main()
