# SPDX-License-Identifier: MIT
import subprocess,tempfile,unittest,shutil,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class CmdqBuild(unittest.TestCase):
 def test_real_provider_link(self):
  with tempfile.TemporaryDirectory() as folder:
   subprocess.run(['make','ambiq-cmdq-simulator','AMBIQ_CQ_DIR='+folder],cwd=ROOT,check=True,capture_output=True)
   nm=shutil.which('arm-none-eabi-nm')
   if not nm:self.skipTest('arm-none-eabi-nm missing')
   symbols=subprocess.run([nm,folder+'/ambiq_mspi.elf'],check=True,capture_output=True,text=True).stdout
   for name in ['am_hal_cmdq_disable','am_hal_cmdq_term','mspi_cq_disable','mspi_cq_term','opencfw_cmdq_critical_enter']:
    self.assertRegex(symbols,r'\bT '+name+r'\n')
 def test_optimized_verifier_rejected(self):
  p=subprocess.run(['python3','-O',str(ROOT/'components/foundation/ambiq_mspi/simulator/verify_cmdq.py')],capture_output=True,text=True)
  self.assertNotEqual(p.returncode,0);self.assertIn('optimized Python rejected',p.stderr)

 def test_pinned_cmdq_excerpts(self):
  component=ROOT/'components/foundation/ambiq_mspi'
  provenance=json.loads((component/'CMDQ_PROVENANCE.json').read_text())
  source=(component/'ambiq_cmdq.c').read_text()
  for name,digest in provenance['unchanged_function_text_sha256'].items():
   i=source.index('uint32_t\n'+name+'(');j=source.index('\n}',i)+2
   self.assertEqual(hashlib.sha256(source[i:j].encode()).hexdigest(),digest)
  self.assertIn('Copyright (c) 2025, Ambiq Micro, Inc.',source)

 def test_architectural_profile_and_interrupt_excerpt(self):
  with tempfile.TemporaryDirectory() as folder:
   subprocess.run(['make','ambiq-critical-simulator','AMBIQ_CRITICAL_DIR='+folder],cwd=ROOT,check=True,capture_output=True)
   nm=shutil.which('arm-none-eabi-nm')
   if not nm:self.skipTest('arm-none-eabi-nm missing')
   symbols=subprocess.run([nm,folder+'/ambiq_mspi.elf'],check=True,capture_output=True,text=True).stdout
   self.assertRegex(symbols,r'\bT am_hal_interrupt_master_disable\n')
  component=ROOT/'components/foundation/ambiq_mspi'
  source=(component/'ambiq_interrupt_mask.c').read_text()
  provenance=json.loads((component/'INTERRUPT_MASK_PROVENANCE.json').read_text())
  i=source.index('uint32_t __attribute__((naked))\nam_hal_interrupt_master_disable(void)');j=source.index('\n}',i)+2
  self.assertEqual(hashlib.sha256(source[i:j].encode()).hexdigest(),provenance['unchanged_gcc_function_text_sha256'])

 def test_profile_switch_rebuilds_same_directory(self):
  nm=shutil.which('arm-none-eabi-nm')
  if not nm:self.skipTest('arm-none-eabi-nm missing')
  with tempfile.TemporaryDirectory() as folder:
   for flags,real in [('-DOPENCFW_REAL_CRITICAL',True),('',False),('-DOPENCFW_REAL_CRITICAL',True)]:
    subprocess.run(['make','ambiq-cmdq-simulator','AMBIQ_CQ_DIR='+folder,'AMBIQ_CQ_CRITICAL_FLAGS='+flags],cwd=ROOT,check=True,capture_output=True)
    symbols=subprocess.run([nm,folder+'/ambiq_mspi.elf'],check=True,capture_output=True,text=True).stdout
    self.assertEqual(' T am_hal_interrupt_master_disable\n' in symbols,real)
