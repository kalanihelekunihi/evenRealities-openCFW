"""Build a current Cortex-M0 test ELF for all CASE legacy opcode branches."""
from pathlib import Path
import subprocess
R=Path(__file__).resolve().parents[3]
S=R/'components/case/legacy_default_candidate_20261010'
O=Path(__file__).with_name('case-legacy256-build');O.mkdir(exist_ok=True)
names='status_a3 word_a4 dogfeed_df toggle_dd default set_sn_a5 control_b0 control_aa_ab reset_toggle_ae charging_status_d3 watchdog_d0 gpio_a1 log_toggle_af version_a0 pmic_d4 simulate_d1 charging_d2 known_dispatch scan_a2 shipmode_ee_prefix reset_ff_prefix'.split()
objects=[]
for name in names:
 src=S/(name+'.c');obj=O/(name+'.o')
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m0','-mthumb','-Os','-ffreestanding','-fno-builtin','-c',str(src),'-o',str(obj)],check=True)
 objects.append(obj)
link=(R/'analysis/case-legacy-default-candidate-20261010/linked254.ld').read_text()
extra='''
case_legacy_ee_first = 0x0010ff01;
case_legacy_ee_power_stop = 0x0010ff11;
case_legacy_ee_wake_prepare = 0x0010ff21;
case_legacy_ee_wake_enable = 0x0010ff31;
case_legacy_ee_enter_standby = 0x0010ff41;
case_legacy_reset_first = 0x0010ff51;
'''
ld=O/'linked256.ld';ld.write_text(link.replace('SECTIONS {',extra+'SECTIONS {'))
out=O/'linked256.elf'
subprocess.run(['arm-none-eabi-ld','-T',str(ld),*map(str,objects),'-o',str(out)],check=True)
print(out)
