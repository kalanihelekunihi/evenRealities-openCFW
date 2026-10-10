import unicorn as u
from unicorn.arm_const import *
print('import',u.__version__,flush=True)
c=u.Uc(u.UC_ARCH_ARM,u.UC_MODE_THUMB|u.UC_MODE_MCLASS);print('create',flush=True)
c.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M33);print('cpu',flush=True)
c.mem_map(0x1000,0x1000);c.mem_write(0x1000,bytes.fromhex('012000ee100ab8ee400a'));print('map',flush=True)
c.reg_write(UC_ARM_REG_FPSCR,0);print('FPSCR',c.reg_read(UC_ARM_REG_FPSCR),flush=True)
# Enable CP10/11 through a real architectural CPACR store, not a CP15 register API.
c.mem_map(0xe000e000,0x1000);c.mem_write(0xe000ed88,(0xf00000).to_bytes(4,'little'));print('CPACR memory seeded',flush=True)
c.emu_start(0x1001,0,count=1);print('integer',c.reg_read(UC_ARM_REG_R0),flush=True)
c.emu_start(0x1003,0,count=1);print('VMOV',flush=True)
c.emu_start(0x1007,0,count=1);print('VCVT',c.reg_read(UC_ARM_REG_FPSCR),flush=True)
