# SPDX-License-Identifier: MIT
import hashlib,json,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class GpioTests(unittest.TestCase):
 def test_pinned_unchanged_function_excerpts(self):
  component=ROOT/'components/foundation/ambiq_gpio';source=(component/'ambiq_gpio_irq.c').read_text();provenance=json.loads((component/'SOURCE_PROVENANCE.json').read_text())
  for name,digest in provenance['unchanged_function_text_sha256'].items():
   i=source.index('uint32_t\n'+name+'(');j=source.index('\n}',i)+2
   self.assertEqual(hashlib.sha256(source[i:j].encode()).hexdigest(),digest)
  self.assertIn('Copyright (c) 2025, Ambiq Micro, Inc.',source)
 def test_source_module_links_with_actual_mask_provider(self):
  if not shutil.which('clang') or not shutil.which('arm-none-eabi-ld') or not shutil.which('arm-none-eabi-nm'):self.skipTest('ARM compile/link tools missing')
  with tempfile.TemporaryDirectory() as folder:
   subprocess.run(['make','ambiq-gpio-simulator','GPIO_SIM_DIR='+folder],cwd=ROOT,check=True,capture_output=True)
   symbols=subprocess.run(['arm-none-eabi-nm',folder+'/ambiq_gpio.elf'],check=True,capture_output=True,text=True).stdout
   for name in ['am_hal_gpio_interrupt_irq_status_get','am_hal_gpio_interrupt_irq_clear','am_hal_gpio_interrupt_register','am_hal_gpio_interrupt_service','am_hal_interrupt_master_disable']:
    self.assertRegex(symbols,r'\bT '+name+r'\n')
 def test_arm32_callback_table_and_sparse_register_abi(self):
  if not shutil.which('clang'):self.skipTest('clang missing')
  with tempfile.TemporaryDirectory() as folder:
   src=Path(folder)/'abi.c';src.write_text('#include "ambiq_gpio_compat.h"\n_Static_assert(sizeof(am_hal_gpio_handler_t)==4,"callback word");\n_Static_assert(sizeof(am_hal_gpio_handler_t[32])==0x80,"bank stride");\n_Static_assert(sizeof(am_hal_gpio_int_channel_e)==4,"channel ABI");\n_Static_assert(offsetof(opencfw_gpio_registers_t,MCUN0INT0CLR)==0x538,"clear offset");\n')
   subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-ffreestanding','-std=c11','-Wall','-Wextra','-Werror','-I',str(ROOT/'components/foundation/ambiq_gpio'),'-c',str(src),'-o',folder+'/abi.o'],check=True,capture_output=True)
 def test_optimized_verifier_rejected(self):
  p=subprocess.run(['python3','-O',str(ROOT/'components/foundation/ambiq_gpio/simulator/verify.py')],capture_output=True,text=True)
  self.assertNotEqual(p.returncode,0);self.assertIn('optimized Python rejected',p.stderr)
