# SPDX-License-Identifier: MIT
import hashlib,json,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
COMPONENT=ROOT/'components/foundation/wsf_timer'
class TimerStopTests(unittest.TestCase):
 def test_pinned_bodies_and_unchanged_port(self):
  source=(COMPONENT/'wsf_timer_stop.c').read_text();prov=json.loads((COMPONENT/'SOURCE_PROVENANCE.json').read_text())
  for name,digest in prov['unchanged_function_text_sha256'].items():
   start=('static void ' if name=='wsfTimerRemove' else 'void ')+name+'('
   a=source.index(start);b=source.index('\n}',a)+2
   self.assertEqual(hashlib.sha256(source[a:b].encode()).hexdigest(),digest)
  self.assertIn('Copyright (c) 2009-2019 Arm Ltd.',source)
  self.assertEqual(hashlib.sha256((ROOT.parent/prov['port_source']).read_bytes()).hexdigest(),prov['port_sha256'])
 def test_real_port_link_has_no_scheduler_providers(self):
  if not all(shutil.which(t) for t in ['clang','arm-none-eabi-ld','arm-none-eabi-nm']):self.skipTest('ARM tools missing')
  with tempfile.TemporaryDirectory() as folder:
   subprocess.run(['make','ambiq-gpio-config-simulator','GPIO_CONFIG_SIM_DIR='+folder],cwd=ROOT,check=True,capture_output=True)
   symbols=subprocess.check_output(['arm-none-eabi-nm',folder+'/gpio_config.elf'],text=True)
   for name in ['WsfTimerStop','WsfQueueRemove','opencfw_wsf_cs_enter','opencfw_wsf_cs_exit','opencfw_radio_timer_gpio_shutdown_phase']:self.assertRegex(symbols,r'\bT '+name+r'\n')
   self.assertEqual(subprocess.check_output(['arm-none-eabi-nm','-u',folder+'/gpio_config.elf'],text=True),'')
   for name in ['opencfw_wsf_wait','opencfw_wsf_timer_update','opencfw_wsf_notify_task','opencfw_wsf_dispatch']:self.assertNotIn(name,symbols)
