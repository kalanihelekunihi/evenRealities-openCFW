#!/usr/bin/env python3
"""Compare compiled board scalars with stock scatter initialization."""
import hashlib,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
from inspect_stock_twi_initialization import main as inspect_stock
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    inspect_stock();stock=json.loads((BASE/'software-twi/stock-initialization.json').read_text())
    report=json.loads((BASE/'report.json').read_text());row=next(x for x in report['units'] if x['source'].endswith('software_twi.c'));obj=Path(row['command'][-1]);assert sha(obj)==row['object_sha256'] and sha(ROOT/row['source'])==row['source_sha256']
    with tempfile.TemporaryDirectory() as directory:
        tmp=Path(directory);elf=tmp/'test.elf';binary=tmp/'test.bin'
        subprocess.run(['arm-none-eabi-ld','-Ttext=0x1000000','--gc-sections','--entry=software_twi_initialize','--undefined=software_twi_bus_record',str(obj),'-o',str(elf)],check=True,capture_output=True)
        subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(elf),str(binary)],check=True)
        syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB);uc.mem_map(0x1000000,0x20000);uc.mem_write(0x1000000,binary.read_bytes());uc.mem_map(0x20000000,0x40000)
        # Explicit test provider references; no GPIO is invoked by initialization.
        providers=[0x100e001+i*16 for i in range(7)];uc.mem_write(0x20002000,struct.pack('<7I',*providers)+bytes([3,0,0,0]))
        def call(name,arg):
            uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101);uc.reg_write(UC_ARM_REG_R0,arg);uc.emu_start(syms[name]|1,0x20000100,count=100000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100;return uc.reg_read(UC_ARM_REG_R0)
        call('software_twi_initialize',0x20002000);records=[]
        for i,expected in enumerate(stock['records']):
            data=bytes(uc.mem_read(call('software_twi_bus_record',i),112));words=struct.unpack('<28I',data)
            observed=dict(name=bytes(uc.mem_read(words[0],16)).split(b'\0')[0].decode(),opened=data[4],delay_context=words[2],scl_pin=words[3],sda_pin=words[4],input_pull=data[36])
            assert observed=={k:expected[k] for k in observed},(i,observed,expected)
            assert [words[x] for x in (5,6,7,8,10,11)]==providers[:6]
            records.append(observed)
    result=dict(application_sha256=stock['application_sha256'],stock_initialization_sha256=sha(BASE/'software-twi/stock-initialization.json'),source_report_sha256=sha(BASE/'report.json'),source_sha256=row['source_sha256'],object_sha256=sha(obj),records=records,scalar_checks=24,provider_binding_checks=24,limitations=['Contextual initializer is not a native stock entry.','Callback references are injected test providers; actual provider bodies and native scatter relocation remain open.','Pull=3 is supplied explicitly by the caller and matches the stock seed.'])
    (BASE/'software-twi/board-configuration-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('24 board scalar checks and 24 provider binding checks passed')
if __name__=='__main__':main()
