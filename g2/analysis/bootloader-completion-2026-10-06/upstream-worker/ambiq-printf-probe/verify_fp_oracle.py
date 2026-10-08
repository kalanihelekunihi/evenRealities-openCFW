import ctypes,json,random,hashlib
from pathlib import Path
from unicorn import *
from unicorn import arm_const as a
lib=ctypes.CDLL('/tmp/opencfw-fp-oracle.dylib');lib.convert_bits.argtypes=[ctypes.c_uint64];lib.convert_bits.restype=ctypes.c_uint32
rng=random.Random(41552);bits=[0,1,0x8000000000000000,0x7ff0000000000000,0xfff0000000000000,0x3ff4000000000000,0x3ff0000010000000,0x3ff0000030000000,0x47efffffe0000000,0x47effffff0000000]+[rng.getrandbits(64) for _ in range(2000)];bits=[b for b in bits if not ((b>>52)&0x7ff==0x7ff and b&((1<<52)-1))];results=[]
for model in [a.UC_CPU_ARM_CORTEX_A9,a.UC_CPU_ARM_CORTEX_A15]:
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.ctl_set_cpu_model(model);u.mem_map(0x1000,4096);u.mem_write(0x1000,bytes.fromhex('b7eec00b'));u.reg_write(a.UC_ARM_REG_C1_C0_2,0xf<<20);u.reg_write(a.UC_ARM_REG_FPEXC,0x40000000)
 for b in bits:
  u.reg_write(a.UC_ARM_REG_FPSCR,0);u.reg_write(a.UC_ARM_REG_D0,b);u.emu_start(0x1001,0x1004,count=1);got=u.reg_read(a.UC_ARM_REG_S0);want=lib.convert_bits(b);assert got==want,(model,hex(b),hex(got),hex(want))
 results.append({'model':model,'cases':len(bits),'status':'PASS'})
r={'status':'PASS','models':results,'negative_control_changed_result_rejected':lib.convert_bits(0x3ff4000000000000)!=0,'seed':41552,'native_library_sha256':hashlib.sha256(Path('/tmp/opencfw-fp-oracle.dylib').read_bytes()).hexdigest(),'limits':['Only conversion result bits checked; FPSCR round-nearest, FZ/DN disabled. Exception flags, other rounding modes and target hardware not certified.','NaN payload propagation excluded from exact-bit oracle; formatter NaN behavior compared separately.','A9/A15 share Unicorn implementation; independent comparator is native host C float cast, not a second independent ARM emulator.']};Path(__file__).with_name('fp-oracle.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
