# SPDX-License-Identifier: MIT
import hashlib,json,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
COMPONENT=ROOT/'components/foundation/ambiq_gpio_config'
class GpioConfigTests(unittest.TestCase):
 def test_pinned_function_and_type_text(self):
  source=(COMPONENT/'ambiq_gpio_config.c').read_text();header=(COMPONENT/'gpio_config.h').read_text();prov=json.loads((COMPONENT/'SOURCE_PROVENANCE.json').read_text())
  for name,digest in prov['unchanged_function_text_sha256'].items():
   a=source.index('uint32_t\n'+name+'(');b=source.index('\n}',a)+2
   self.assertEqual(hashlib.sha256(source[a:b].encode()).hexdigest(),digest)
  a=header.index('typedef struct\n{\n    union');b=header.index('} am_hal_gpio_pincfg_t;',a)+len('} am_hal_gpio_pincfg_t;')
  self.assertEqual(hashlib.sha256(header[a:b].encode()).hexdigest(),prov['type_text_sha256'])
  for text in [source,header]:self.assertIn('Copyright (c) 2025, Ambiq Micro, Inc.',text)
 def test_source_module_builds_with_real_mask_provider(self):
  if not all(shutil.which(t) for t in ['clang','arm-none-eabi-ld','arm-none-eabi-nm']):self.skipTest('ARM build tools missing')
  with tempfile.TemporaryDirectory() as folder:
   subprocess.run(['make','ambiq-gpio-config-simulator','GPIO_CONFIG_SIM_DIR='+folder],cwd=ROOT,check=True,capture_output=True)
   result=subprocess.run(['arm-none-eabi-nm',folder+'/gpio_config.elf'],check=True,capture_output=True,text=True).stdout
   for name in ['am_hal_gpio_pinconfig','am_hal_gpio_pinconfig_get','am_hal_interrupt_master_disable','am_hal_gpio_state_write','opencfw_gpio_state_write_raw','opencfw_radio_gpio_idle_pins','am_hal_gpio_interrupt_control','opencfw_gpio_interrupt_control_raw','opencfw_radio_gpio_shutdown_phase']:self.assertRegex(result,r'\bT '+name+r'\n')
 def test_packed_word_bitfields(self):
  if not shutil.which('clang'):self.skipTest('clang missing')
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder)/'bits.c';p.write_text('#include "gpio_config.h"\nint main(void){am_hal_gpio_pincfg_t c={0};if(sizeof(c)!=4)return 1;c.GP.cfg_b.eDriveStrength=7;c.GP.cfg_b.ePullup=6;if(c.GP.cfg!=0xdc00)return 2;c.GP.cfg=0xffffffff;if(c.GP.cfg_b.eDriveStrength!=7||c.GP.cfg_b.ePullup!=7)return 3;return 0;}\n')
   subprocess.run(['clang','-std=c11','-Wall','-Wextra','-Werror','-I',str(COMPONENT),str(p),'-o',folder+'/bits'],check=True,capture_output=True)
   subprocess.run([folder+'/bits'],check=True,capture_output=True)
 def test_optimized_python_rejected(self):
  p=subprocess.run(['python3','-O',str(COMPONENT/'simulator/verify.py')],capture_output=True,text=True)
  self.assertNotEqual(p.returncode,0);self.assertIn('optimized Python rejected',p.stderr)

 def test_pinned_state_body_and_macros(self):
  source=(COMPONENT/'gpio_state.c').read_text();compat=(COMPONENT/'gpio_config_compat.h').read_text();prov=json.loads((COMPONENT/'STATE_PROVENANCE.json').read_text())
  a=source.index('uint32_t\n'+'am_hal_gpio_state_write(');b=source.index('\n}',a)+2
  self.assertEqual(hashlib.sha256(source[a:b].encode()).hexdigest(),prov['unchanged_state_function_text_sha256'])
  for start,end,key in [('#define AM_HAL_MASK32','#define am_hal_gpio_output_clear','unchanged_index_macros_sha256'),('#define am_hal_gpio_output_clear','_Static_assert(offsetof(opencfw_gpio_config_registers_t,RD0)','unchanged_output_macros_sha256')]:
   part=compat[compat.index(start):compat.index(end)].rstrip()
   self.assertEqual(hashlib.sha256(part.encode()).hexdigest(),prov[key])
  self.assertIn('Copyright (c) 2025, Ambiq Micro, Inc.',source)
 def test_operation_abi_converts_raw_values(self):
  if not shutil.which('clang'):self.skipTest('clang missing')
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder)/'abi.c';p.write_text('#include "gpio_config.h"\n_Static_assert(sizeof(am_hal_gpio_write_type_e)==1,"stock byte operation");\nint main(void){am_hal_gpio_write_type_e op=(am_hal_gpio_write_type_e)0x105u;return op!=5;}\n')
   subprocess.run(['clang','-std=c11','-Wall','-Wextra','-Werror','-I',str(COMPONENT),str(p),'-o',folder+'/abi'],check=True,capture_output=True)
   subprocess.run([folder+'/abi'],check=True,capture_output=True)

 def test_pinned_interrupt_control_and_helper(self):
  source=(COMPONENT/'gpio_interrupt_control.c').read_text();prov=json.loads((COMPONENT/'CONTROL_PROVENANCE.json').read_text())
  for name,digest in prov['unchanged_function_text_sha256'].items():
   start=('static ' if name=='gpionum_intreg_index_get' else '')+'uint32_t\n'+name+'('
   a=source.index(start);end='} // '+name+'()';b=source.index(end,a)+len(end)
   self.assertEqual(hashlib.sha256(source[a:b].encode()).hexdigest(),digest)
  self.assertIn('Copyright (c) 2025, Ambiq Micro, Inc.',source)
