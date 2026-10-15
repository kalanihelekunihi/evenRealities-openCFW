#!/usr/bin/env python3
"""Compare compiled R1 configuration callbacks with authenticated stock Thumb."""
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, __version__ as unicorn_version
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC

ROOT=Path(__file__).resolve().parents[2]


def main():
    application=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin'
    image=application.read_bytes()
    assert hashlib.sha256(image).hexdigest()=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    report=json.loads((ROOT/'r1/research/source-build/rtos/report.json').read_text())
    unit=report['units'][-1]
    source=ROOT/unit['source']
    assert hashlib.sha256(source.read_bytes()).hexdigest()==unit['source_sha256']
    obj=ROOT/'r1/research/source-build/rtos/11_static_task_memory.o'
    assert unit['compiled'] and hashlib.sha256(obj.read_bytes()).hexdigest()==unit['object_sha256']
    pairs=[('vApplicationGetIdleTaskMemory',0x95bb8,0x95bcc,0x2002b4d0),
           ('vApplicationGetTimerTaskMemory',0x95bd0,0x95be4,0x2002b940)]
    bodies=[]
    for name,entry,literal,control in pairs:
        assert struct.unpack_from('<I',image,literal-0x27000)[0]==control
        body=image[entry-0x27000:entry-0x27000+18]
        assert hashlib.sha256(body).hexdigest()=='2493b37197606152e480a50e74a2c99cfbfc851026f1545cb4ee3001568d1123'
        bodies.append(dict(name=name,entry=hex(entry),body_sha256=hashlib.sha256(body).hexdigest(),control=hex(control),stack=hex(control+112),words=256))
    bindir=Path(shutil.which('arm-none-eabi-ld')).parent
    with tempfile.TemporaryDirectory(prefix='r1-task-layout-') as temporary:
        temp=Path(temporary); script=temp/'layout.ld';elf=temp/'callbacks.elf';binary=temp/'callbacks.bin'
        script.write_text('''SECTIONS {
 .text 0x01000000 : { *(.text*) }
 .ARM.exidx : { *(.ARM.exidx*) }
 .r1.idle_task_memory 0x2002b4d0 (NOLOAD) : { *(.r1.idle_task_memory) }
 .r1.timer_task_memory 0x2002b940 (NOLOAD) : { *(.r1.timer_task_memory) }
 /DISCARD/ : { *(.comment) *(.note*) }
}''')
        subprocess.run([str(bindir/'arm-none-eabi-ld'),'-T',str(script),str(obj),'-o',str(elf)],check=True)
        subprocess.run([str(bindir/'arm-none-eabi-objcopy'),'-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
        symbols=subprocess.check_output([str(bindir/'arm-none-eabi-nm'),str(elf)],text=True)
        addresses={line.split()[-1]:int(line.split()[0],16) for line in symbols.splitlines() if len(line.split())==3}
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB);uc.mem_map(0x20000,0xc0000);uc.mem_write(0x27000,image)
        uc.mem_map(0x1000000,0x1000);uc.mem_write(0x1000000,binary.read_bytes());uc.mem_map(0x20000000,0x40000)
        stop=0x20000100
        uc.mem_write(stop,b'\x00\xbe')
        def execute(entry,args):
            uc.mem_write(0x20001000,bytes([0xa5])*64)
            for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),args):uc.reg_write(reg,value)
            uc.reg_write(UC_ARM_REG_SP,0x20010000);uc.reg_write(UC_ARM_REG_LR,stop|1)
            uc.emu_start(entry|1,stop,count=1000);assert uc.reg_read(UC_ARM_REG_PC)==stop
            return bytes(uc.mem_read(0x20001000,64))
        comparisons=0
        for name,entry,_,_ in pairs:
            for offset in range(0,40,4):
                args=[0x20001000+offset+x for x in (0,4,8)]
                assert execute(entry,args)==execute(addresses[name],args)
                comparisons+=1
    output=dict(application_sha256=hashlib.sha256(image).hexdigest(),source_sha256=unit['source_sha256'],
                object_sha256=unit['object_sha256'],unicorn_version=unicorn_version,callbacks=bodies,
                comparisons=comparisons,scope='stock Thumb versus linked ARM C callbacks; matching pointer outputs and untouched guard bytes',
                stock_tcb_type_proven=False,candidate_tcb_bytes=report['candidate_tcb_bytes'],stock_control_reservation_bytes=112,
                full_image_link=False,instruction_identity=False)
    (ROOT/'r1/research/source-build/rtos/static-memory-verification.json').write_text(json.dumps(output,indent=2)+'\n')
    print(f'{comparisons} callback comparisons passed with stock RAM pointer layout')


if __name__=='__main__':main()
