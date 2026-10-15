#!/usr/bin/env python3
"""Verify typed native initialization and execute its real provider tables."""
import hashlib,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    receipt=BASE/'adc/verification.json';receipt.unlink(missing_ok=True)
    app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    report=json.loads((BASE/'adc/report.json').read_text());obj=BASE/'adc/stock_named_adc.o';assert sha(obj)==report['units'][0]['object_sha256']
    for path,digest in report['inputs'].items():assert sha(ROOT/path)==digest,path
    integrated=BASE/'i2c5/st25-i2c5-registry.o';integration=json.loads((BASE/'i2c5/report.json').read_text());assert sha(integrated)==integration['relocatable_sha256']
    lib=ROOT/'vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update/arm-none-eabi/lib/thumb/v7e-m+fp/hard/libc.a'
    roots={'r1_named_adc_register_all':0x5493c,'r1_named_adc_open':0x54864,'r1_named_adc_sample':0x548f0,'r1_named_adc_close':0x547f4}
    comparisons=0
    with tempfile.TemporaryDirectory() as directory:
        tmp=Path(directory);ld=tmp/'test.ld';elf=tmp/'test.elf';text=tmp/'text.bin';data=tmp/'records.bin'
        ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .r1.adc.state 0x20006ef4 : { *(.r1.adc.state) } .r1.adc.ops 0x20006f70 : { *(.r1.adc.ops) } .r1.registry.head 0x20007680 (NOLOAD) : { *(.r1.registry.head) } /DISCARD/ : { *(.comment) *(.note*) } }')
        subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--gc-sections','--entry='+next(iter(roots)),*['--undefined='+n for n in roots],*['--defsym='+n+'='+hex(0x100e001+i*16) for i,n in enumerate(('nrfx_saadc_init','nrfx_saadc_channel_init','nrfx_saadc_channel_uninit','nrfx_saadc_sample_convert','nrfx_saadc_uninit','r1_adc_error'))],str(obj),str(integrated),str(lib),'-o',str(elf)],check=True,capture_output=True)
        subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(text)],check=True)
        subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.adc.state='+str(data),str(elf)],check=True)
        syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
        stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB);stock.mem_map(0x20000,0xc0000);stock.mem_write(0x27000,app.read_bytes());events={id(stock):[],id(candidate):[]}
        for uc in (stock,candidate):uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000);uc.mem_map(0x50000000,0x1000)
        stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208
        candidate.mem_write(0x1000000,text.read_bytes());candidate.mem_write(0x20006ef4,data.read_bytes());assert len(data.read_bytes())==124
        ops=tmp/'ops.bin';subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.adc.ops='+str(ops),str(elf)],check=True);candidate.mem_write(0x20006f70,ops.read_bytes())
        def normalize(uc):
            result=bytearray(uc.mem_read(0x20006ef4,124))
            for i in range(3):
                for off in (0,16):result[4+i*40+off:4+i*40+off+4]=bytes(4)
            return bytes(result)
        assert normalize(stock)==normalize(candidate)
        from unicorn import UC_HOOK_CODE
        provider_state=[0,0,0,0]
        names=('init','channel_init','channel_uninit','sample','uninit','error')
        provider_map={address:name for address,name in zip((0x7af7c,0x7aeac,0x7af38,0x7b090,0x7b150,0x4e5bc),names)}
        provider_map.update({0x100e000+i*16:name for i,name in enumerate(names)})
        def providers(uc,address,size,data):
            if address in (0x9a5e0,syms['r1_twi_delay_busy']):
                value=uc.reg_read(UC_ARM_REG_R0)*(64 if uc is candidate else 1);events[id(uc)].append(('settle_cycles',value));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
            if address not in provider_map:return
            name=provider_map[address];a=uc.reg_read(UC_ARM_REG_R0);b=uc.reg_read(UC_ARM_REG_R1);value=0
            if name=='init':events[id(uc)].append((name,bytes(uc.mem_read(a,4)),b));value=provider_state[0]
            elif name=='channel_init':events[id(uc)].append((name,a,bytes(uc.mem_read(b,9))));value=provider_state[1]
            elif name=='sample':events[id(uc)].append((name,a));uc.mem_write(b,struct.pack('<H',provider_state[3]&65535));value=provider_state[2]
            elif name in ('channel_uninit','error'):events[id(uc)].append((name,a))
            else:events[id(uc)].append((name,))
            uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        for uc in (stock,candidate):
            uc.hook_add(UC_HOOK_CODE,providers)
            uc.mem_write(0x20002500,bytes(24));uc.mem_write(0x50000000,bytes(4096))
        def compare(name,args):
            nonlocal comparisons
            results=[]
            for uc,entry in ((stock,roots[name]),(candidate,syms[name])):
                events[id(uc)].clear();uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101)
                for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):uc.reg_write(reg,value)
                uc.emu_start(entry|1,0x20000100,count=2000000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100
                results.append((uc.reg_read(UC_ARM_REG_R0),list(events[id(uc)]),normalize(uc),bytes(uc.mem_read(0x20007680,4)),bytes(uc.mem_read(0x20003000,16)),bytes(uc.mem_read(0x50000000,4096))))
            assert results[0]==results[1],(name,args,results);comparisons+=1
        for _ in range(2):compare('r1_named_adc_register_all',[0,0,0,0])
        for i,name in enumerate(('vbat_adc','vpmic_isns_adc','vnfc_rect_adc','missing')):
            for uc in (stock,candidate):uc.mem_write(0x20002600,name.encode()+b'\0');uc.mem_write(0x20002500,struct.pack('<I',0x20002600))
            for initialized in (0,1,2,255):
                for opened in (0,1,255):
                    for statuses in ((0,0),(7,0),(0,8)):
                        provider_state[:2]=statuses
                        for uc in (stock,candidate):
                            uc.mem_write(0x20006ef4,bytes([initialized]))
                            if i<3:uc.mem_write(0x20006efc+i*40,bytes([opened]))
                        compare('r1_named_adc_open',[0x20002500,0,0,0])
            for opened in (0,1):
                for sample in (0,2048,32767,32768,65535):
                    for status in (0,7):
                        provider_state[2:]=[status,sample]
                        if i<3:
                            for uc in (stock,candidate):uc.mem_write(0x20006efc+i*40,bytes([opened]))
                        compare('r1_named_adc_sample',[0x20002500,0,0x20003000,0])
            for mask in range(8):
                for initialized in (0,1,2,255):
                    for uc in (stock,candidate):
                        uc.mem_write(0x20006ef4,bytes([initialized]))
                        for j in range(3):uc.mem_write(0x20006efc+j*40,bytes([(mask>>j)&1]))
                    compare('r1_named_adc_close',[0x20002500,0,0,0])
    result=dict(application_sha256=sha(app),adc_report_sha256=sha(BASE/'adc/report.json'),integration_report_sha256=sha(BASE/'i2c5/report.json'),object_sha256=sha(obj),comparisons=comparisons,initialized_state_bytes=124,runtime_archive_sha256=sha(lib),scope='Three typed ADC records, registration, open/config/error/settling order, named sampling and all-channel close transitions versus stock',limitations=['Final nrfx ADC and error-handler seams are intercepted; this does not establish physical sampling or fatal-error runtime behavior.','Sample tests write a result even on injected provider failure; untouched/uninitialized result behavior remains unproven.','Settling compares work arguments, not cycles.','Newlib strcmp is a binary test dependency.'],application_linked=False,instruction_identity_proven=False)
    receipt.write_text(json.dumps(result,indent=2)+'\n');print(f'124 ADC initial-state bytes verified; {comparisons} native ADC comparisons passed')
if __name__=='__main__':main()
