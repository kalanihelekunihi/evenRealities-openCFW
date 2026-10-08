#!/usr/bin/env python3
"""Run clockmux against mapped source children and bounded hardware services."""
from pathlib import Path
import hashlib, importlib.util, json, struct, sys
from unicorn import (Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS,
                     UC_HOOK_CODE, UC_HOOK_MEM_WRITE, UC_HOOK_MEM_INVALID)
from unicorn import arm_const as a

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
IMAGE=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
ELF=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/tmp/clockmux-chain/clockmux-native-chain.elf')
OUT=Path(sys.argv[2]) if len(sys.argv)>2 else HERE/'native-chain-cache-expanded.json'
blob=IMAGE.read_bytes();digest=hashlib.sha256(blob).hexdigest()
assert digest=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
spec=importlib.util.spec_from_file_location('elf_reader',ROOT/'g2/components/bootloader/update_core/elf_reader.py')
reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
_,segments,symbols=reader.elf_info(ELF)
SOURCE_NATIVE={
 'opencfw_bl_delay_us':'delay','opencfw_hal_status_poll':'poll',
 'opencfw_bl_radio_mode_apply':'gpio','opencfw_bl_power_register_read':'power_read',
 'opencfw_bl_power_register_update':'power_update',
 'opencfw_low_power_prepare':'prepare','opencfw_low_power_finish':'finish',
 'opencfw_bl_mspi_mode_enter':'mode_enter','opencfw_bl_mspi_mode_leave':'mode_leave',
 'opencfw_cache_invalidate':'cache'}
UNREACHED_SERVICES={
 'opencfw_boot_control_delay_status_change':'unreached_test_service_delay_status',
 'opencfw_boot_power_special_mode':'unreached_test_service_special_mode',
 'opencfw_bl_clock_release_all':'unreached_test_service_clock_release_all'}
SOURCE_CUTS={}
native={symbols[n]&~1:k for n,k in SOURCE_NATIVE.items()}
unreached_service_addrs={symbols[n]&~1:k for n,k in UNREACHED_SERVICES.items()}
source_cuts={symbols[n]&~1:k for n,k in SOURCE_CUTS.items()}
MMIO=[0x40008858,0x4000885c,0x400200c0,0x4002000c,0x400201b0,
      0x400204d8,0x400204e8,0x40004044,0x40004030,0x4001003c,
      0x40010400,0x40020120,0x40020128,0x4002012c,0x40201000,
      0x40208100,0x40209100,0x400b2000,0x40210000,
      0xe000ed14,0xe000ed80,0xe000ed84,0xe000ef74]

def run(source,f):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
    for lo,sz in [(0,0x1000),(0x08000000,0x1000),(0x410000,0x25000),
                  (0x10000,0x10000),(0x30000,0x10000),(0x20000000,0x40000),
                  (0x40000000,0x300000),(0xe000e000,0x10000),
                  (0x47ff0000,0x10000)]:u.mem_map(lo,sz)
    if source:
        for seg in segments:u.mem_write(seg['address'],seg['data'])
    else:u.mem_write(0x410000,blob)
    def w(p,x):u.mem_write(p,struct.pack('<I',x&0xffffffff))
    state=(0x5af0<<16)|f['flags'];w(0x40008858,state)
    w(0x4000885c,2 if f.get('guard_busy') else 0)
    for p in MMIO[2:]:w(p,0x13579bdf)
    w(0x4002000c,f.get('revision',0x22))
    w(0x4001003c,f['pin_read'])
    w(0x40004030,0x01000000)
    w(0xe000ed14,0x10000 if f.get('cache_enabled',True) else 0)
    w(0xe000ed80,(f.get('cache_sets',1)<<13)|(f.get('cache_ways',1)<<3))
    w(0xe000ed84,0)
    sp=0x2003f000;entry=0x20001000
    u.mem_write(sp-0x100,b'\xa5'*0x100)
    u.mem_write(entry,struct.pack('<III',f['r1'],f['r2'],f['r5']))
    u.reg_write(a.UC_ARM_REG_SP,sp);u.reg_write(a.UC_ARM_REG_LR,0x08000001)
    u.reg_write(a.UC_ARM_REG_PRIMASK,f['primask'])
    u.reg_write(a.UC_ARM_REG_R0,0x76543210);u.reg_write(a.UC_ARM_REG_R1,f['r1'])
    u.reg_write(a.UC_ARM_REG_R2,f['r2']);u.reg_write(a.UC_ARM_REG_R3,0x89abcdef)
    u.reg_write(a.UC_ARM_REG_R5,f['r5'])
    for n in [4,6,7,8,9,10,11]:u.reg_write(getattr(a,f'UC_ARM_REG_R{n}'),0xa0000000+n)
    pc=(symbols['opencfw_boot_clockmux_entry']&~1) if source else 0x41acb2
    cuts=source_cuts if source else {}
    calls=[];rom_waits=[];writes=[];syswrites=[];pcs=[];mode_sizes={};done=False
    def event(k,regs,spv):
        if k=='delay': item=[k,regs[0]]
        elif k=='poll':item=[k,*regs,spv]
        elif k=='gpio':
            ptr=regs[1];item=[k,regs[0],u.mem_read(ptr,1)[0] if ptr else None]
        elif k=='power_read':item=[k,regs[0]]
        elif k=='power_update':item=[k,regs[0],regs[1]]
        elif k=='cache':item=[k,regs[0],regs[1]]
        elif k in ('mode_enter','mode_leave'):item=[k,regs[0]]
        else:item=[k]
        calls.append(item)
    def hook(cpu,p,size,_):
        nonlocal done
        pcs.append(p)
        if not source and 0x41d3e4<=p<0x41d676:mode_sizes[p]=size
        if p==0x08000000:done=True;cpu.emu_stop();return
        if p==0x40:
            rom_waits.append(cpu.reg_read(a.UC_ARM_REG_R0))
            cpu.reg_write(a.UC_ARM_REG_PC,cpu.reg_read(a.UC_ARM_REG_LR));return
        if source and p in unreached_service_addrs:
            event(unreached_service_addrs[p],[cpu.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4)],
                  struct.unpack('<I',cpu.mem_read(cpu.reg_read(a.UC_ARM_REG_SP),4))[0])
        if source and p in native:
            regs=[cpu.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4)]
            event(native[p],regs,struct.unpack('<I',cpu.mem_read(cpu.reg_read(a.UC_ARM_REG_SP),4))[0])
        elif not source and p in [0x41d1c0,0x41d246,0x41d3e4,0x41d90e,
                                   0x41d92c,0x41ca5c,0x41caa2,0x41e348,
                                   0x41bf84,0x41c17a]:
            k={0x41d1c0:'delay',0x41d246:'poll',0x41d3e4:'gpio',
               0x41d90e:'power_read',0x41d92c:'power_update',
               0x41ca5c:'prepare',0x41caa2:'finish',0x41e348:'cache',
               0x41bf84:'mode_enter',0x41c17a:'mode_leave'}[p]
            regs=[cpu.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4)]
            event(k,regs,struct.unpack('<I',cpu.mem_read(cpu.reg_read(a.UC_ARM_REG_SP),4))[0])
        if p in cuts:
            k=cuts[p];regs=[cpu.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4)]
            event(k,regs,struct.unpack('<I',cpu.mem_read(cpu.reg_read(a.UC_ARM_REG_SP),4))[0])
            cpu.reg_write(a.UC_ARM_REG_R0,0)
            cpu.reg_write(a.UC_ARM_REG_PC,cpu.reg_read(a.UC_ARM_REG_LR))
    def write(cpu,access,p,size,value,_):
        row=[p,size,value&((1<<(size*8))-1)]
        if 0x40000000<=p<0x40300000:writes.append(row)
        elif 0xe000e000<=p<=0xe000efff:syswrites.append(row)
        control_to_status={
          0x40021004:(0x40021008,[(0x01000000,0x01000000),(0x02000000,0x02000000)]),
          0x4002100c:(0x40021010,[(0x4,0x4),(0x40,0xc0),(0x80,0xc0),(0x400,0x400)])}
        if p in control_to_status:
            status_address,mapping=control_to_status[p]
            masks=0
            acknowledged=0
            for command_bit,status_mask in mapping:
                masks |= status_mask
                if value & command_bit: acknowledged |= status_mask
            prior=struct.unpack('<I',cpu.mem_read(status_address,4))[0]
            cpu.mem_write(status_address,struct.pack('<I',(prior&~masks)|acknowledged))
    def invalid(cpu,access,p,size,value,_):
        raise RuntimeError(f'unmapped {access=} {p:#x} at {cpu.reg_read(a.UC_ARM_REG_PC):#x}, source={source}, flags={f["flags"]:#x}')
    u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0x40000000,end=0x402fffff)
    u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0xe000e000,end=0xe000efff);u.hook_add(UC_HOOK_MEM_INVALID,invalid)
    try:u.emu_start(pc|1,0,count=300000)
    except Exception as e:raise RuntimeError(f'emu failed source={source} fixture={f}, tail={[hex(x) for x in pcs[-12:]], calls[-6:]}') from e
    assert done,(source,hex(pc),f)
    return {'return_regs':[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in [0,1,2]],
      'callee_saved':[u.reg_read(getattr(a,f'UC_ARM_REG_R{i}')) for i in range(4,12)],
      'sp':u.reg_read(a.UC_ARM_REG_SP),'primask':u.reg_read(a.UC_ARM_REG_PRIMASK),
      'calls':calls,'rom_wait_cycles':rom_waits,'mmio_writes':writes,
      'system_writes':syswrites,'mmio_final':{hex(p):struct.unpack('<I',u.mem_read(p,4))[0] for p in MMIO},
      '_stock_mode_sizes':mode_sizes}

fixtures=[
 {'flags':0x10,'r1':0x11223344,'r2':0x76543210,'r5':0xa5b6c7d8,'pin_read':0xdeadbeef,'primask':1},
 {'flags':0x7f,'r1':0,'r2':0,'r5':0x20027064,'pin_read':0x12345678,'primask':0},
 {'flags':0x7f,'r1':0x11223344,'r2':0x76543210,'r5':0xa5b6c7d8,'pin_read':0xdeadbeef,'primask':1},
 {'flags':0x3c,'r1':0,'r2':0xabcdef01,'r5':0x20027064,'pin_read':0x0badf00d,'primask':1},
 {'flags':0x64,'r1':0x01020304,'r2':0x10203040,'r5':0x20027064,'pin_read':0x31415926,'primask':0},
 {'flags':0x0c,'r1':0xffffffff,'r2':0x55555555,'r5':0xaaaaaaaa,'pin_read':0x87654321,'primask':1},
 {'flags':0x01,'r1':0,'r2':0,'r5':0xa5b6c7d8,'pin_read':0,'primask':0},
 {'flags':0,'r1':0x11223344,'r2':0x76543210,'r5':0x20027064,'pin_read':0xffffffff,'primask':1},
 {'flags':0x7f,'r1':0x11223344,'r2':0x76543210,'r5':0x20027064,'pin_read':0x13579bdf,'primask':1,'guard_busy':True},
 {'flags':0x7f,'r1':0,'r2':0,'r5':0xa5b6c7d8,'pin_read':0,'primask':0,'revision':0x21},
 {'flags':0x7f,'r1':0,'r2':0,'r5':0x20027064,'pin_read':0x12345678,'primask':0,
  'cache_enabled':True,'cache_sets':0,'cache_ways':0,'cache_case':'enabled_1x1'},
 {'flags':0x7f,'r1':0x11223344,'r2':0x76543210,'r5':0xa5b6c7d8,'pin_read':0xdeadbeef,'primask':1,
  'cache_enabled':True,'cache_sets':2,'cache_ways':1,'cache_case':'enabled_3x2'},
 {'flags':0x7f,'r1':0x01020304,'r2':0x10203040,'r5':0x20027064,'pin_read':0x31415926,'primask':0,
  'cache_enabled':True,'cache_sets':1,'cache_ways':2,'cache_case':'enabled_2x3'},
 {'flags':0x7f,'r1':0xffffffff,'r2':0x55555555,'r5':0xaaaaaaaa,'pin_read':0x87654321,'primask':1,
  'cache_enabled':False,'cache_sets':3,'cache_ways':3,'cache_case':'disabled_4x4'},
]
def address_ranges(widths):
    rows=[]
    for pc,size in sorted(widths.items()):
        if rows and rows[-1][1] == pc:
            rows[-1][1] += size
        else:
            rows.append([pc,pc+size])
    return [[hex(start),hex(end)] for start,end in rows]
rows=[];mode_widths={}
for f in fixtures:
 stock=run(False,f);source=run(True,f)
 stock_sizes=stock.pop('_stock_mode_sizes');source.pop('_stock_mode_sizes')
 if any(row[0].startswith('unreached_test_service_') for row in source['calls']):
  raise AssertionError(('unexpected test service use',f,source['calls']))
 if f.get('cache_case'):
  cache_calls=[x for x in stock['calls'] if x[0]=='cache']
  assert cache_calls==[['cache',0,1]],(f,cache_calls)
  maintenance=[x for x in stock['system_writes'] if x[0]==0xe000ef74]
  expected=0 if not f['cache_enabled'] else (f['cache_sets']+1)*(f['cache_ways']+1)
  assert len(maintenance)==expected,(f,maintenance,expected)
  expected_values=[] if not f['cache_enabled'] else [
                   ((_set<<5)&0x3fe0)|(way<<30)
                   for _set in range(f['cache_sets'],-1,-1)
                   for way in range(f['cache_ways'],-1,-1)]
  assert [row[2] for row in maintenance]==expected_values,(f,maintenance,expected_values)
 if stock!=source:
  OUT.with_suffix('.failure.json').write_text(json.dumps({'fixture':f,'stock':stock,'source':source},indent=2)+'\n')
  raise AssertionError((f,stock,source))
 mode_widths.update(stock_sizes)
 rows.append({'fixture':f,'result':stock})
result={'status':'PASS','cases':len(rows),'stock_sha256':digest,
 'elf_sha256':hashlib.sha256(ELF.read_bytes()).hexdigest(),
 'native_children':['41d1c0 delay source/stock','41d246 poll source/stock','41d3e4 selector2/4 source mode apply','41d90e register read source/stock','41d92c register update source/stock','41ca5c/41caa2 PLL power helpers source/stock','41e348 cache source/stock','41bf84/41c17a MSPI power-domain C source/stock'],
 'cuts':['Power-domain sibling services20/23/29 are not reached in these fixtures; their existing source definitions do not expand this caller-specific proof.','Control-to-status acknowledgement is synthesized identically after writes to 0x40021004/0x4002100c; stock and source status-poll bodies execute against the resulting status registers. ROM cycle-wait at 0x40 is controlled.'],
 'mode_function_extent':['0x41d3e4','0x41d676'],'stock_mode_unique_pcs':len(mode_widths),
 'stock_mode_bytes_reached':sum(mode_widths.values()),
 'stock_mode_reached_ranges':address_ranges(mode_widths),
 'compared_machine_state':['R0/R1/R2','R4-R11 callee-saved','SP','PRIMASK'],
 'cache_coverage':{'caller_arguments':['NULL','1'],'enabled_disabled_variants':True,
                   'ccsidr_sets_ways_variants':True,
                   'whole_invalidate_register':'0xe000ef74',
                   'system_write_capture_range':['0xe000e000','0xe000efff']},
 'cache_cases':[f for f in fixtures if f.get('cache_case')],
 'limits':['Selector2/4 paths are compared from the 658-byte stock entry; the C class-provider source maps the directly relevant 88-byte subrange 0x41d3e4..0x41d43c and is not a complete replacement for other selectors in that 658-byte function.','PLL power methods are exported source accessors in the active clock_class_provider6.c; no stock executable bytes are used source-side.','The power-domain C entries execute without direct child cuts on selector 2/4 clockmux paths; control/status acknowledgement is an offline model, not hardware evidence. ROM timing is controlled. No physical delay, electrical, clock-stability, or hardware behavior is claimed.'],
 'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in [
  'g2/components/bootloader/initializer_callbacks/startup_clockmux.c',
  'g2/components/bootloader/initializer_callbacks/startup_clockmux.h',
  'g2/components/bootloader/initializer_callbacks/startup_clockmux_entry.S',
  'g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize/clockmux_entry.h',
  'g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize/clockmux_entry.S',
  'g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-clockmux/build_native_chain.sh',
  'g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-clockmux/native-chain.ld',
  'g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-clockmux/native_adapters.c',
  'g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-clockmux/native_pll_access.c',
  'g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-clockmux/power_domain_test_services.c',
  'g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-clockmux/verify_native_chain.py',
  'g2/analysis/bootloader-completion-2026-10-06/upstream-worker/ambiqhal-apollo510/ambiqhal/CMSIS/AmbiqMicro/Include/apollo510.h',
  'g2/analysis/bootloader-completion-2026-10-06/upstream-worker/ambiqhal-apollo510/ambiqhal/CMSIS/AmbiqMicro/Include/system_apollo510.h',
  'g2/analysis/bootloader-completion-2026-10-06/upstream-worker/ambiqhal-apollo510/cmsis-5-590/CMSIS/Core/Include/core_cm55.h',
  'g2/components/bootloader/clock_manager/clock_class_provider2.c',
  'g2/components/bootloader/clock_manager/clock_class_provider2.h',
  'g2/components/bootloader/clock_manager/clock_class_provider4.c',
  'g2/components/bootloader/clock_manager/clock_class_provider4.h',
  'g2/components/bootloader/clock_manager/clock_class_provider6.c',
  'g2/components/bootloader/clock_manager/clock_class_provider6.h',
  'g2/components/bootloader/clock_manager/clock_class_providers.c',
  'g2/components/bootloader/clock_manager/clock_class_providers.h',
  'g2/components/bootloader/clock_manager/clock_manager.c',
  'g2/components/bootloader/clock_manager/clock_manager.h',
  'g2/components/bootloader/nor_mspi_init/status_poll.c',
  'g2/components/bootloader/platform_control/power_domains.c',
  'g2/components/bootloader/platform_control/power_domains.h',
  'g2/components/bootloader/platform_control/runtime_query.c',
  'g2/components/bootloader/platform_control/runtime_query.h',
  'g2/components/bootloader/platform_control/critical_save.S',
  'g2/components/foundation/cache_maintenance/cache_maintenance.c',
  'g2/components/foundation/cache_maintenance/cache_maintenance.h',
  'g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-clockmux/power_register_read.c',
  'g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-clockmux/power_domain_test_services.c']},
 'comparisons':rows}
OUT.write_text(json.dumps(result,indent=2)+'\n');print('PASS',len(rows),'native-child clockmux chain cases; selector function',len(mode_widths),'unique PCs /',sum(mode_widths.values()),'bytes reached')
