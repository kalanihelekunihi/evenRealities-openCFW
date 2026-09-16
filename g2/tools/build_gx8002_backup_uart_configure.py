# SPDX-License-Identifier: MIT
"""Build shared UART configuration C at its backup entry without code cutting."""
import json,subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32,FLAGS


def build():
    out=ROOT/'build/gx8002-backup-uart-configure';out.mkdir(exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_uart_configure.c'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');obj=out/'configure.o'
    command=[pre+'gcc',*FLAGS,'-Os','-ffp-contract=off','-c',str(source),'-o',str(obj)]
    subprocess.run(command,check=True)
    bindings={'open_cfw_gx8002_uart_fifo_depth':0x3cc7c,'open_cfw_gx8002_uart_interrupt':0x3cb90,'open_cfw_gx8002_request_irq':0x3d184,'__floatunsidf':0x4ad0c,'__divdf3':0x4a990,'__muldf3':0x4a790,'__adddf3':0x4a724,'__fixunsdfsi':0x49da4}
    delta=0x10003000-0x3b940
    e=Elf32(obj.read_bytes(),'configure object');undefined={s['name'] for s in e.symbols() if s['name'] and s['section']==0};assert undefined<=set(bindings)
    ld=out/'configure.ld';ld.write_text('SECTIONS { .configure 0x100043a4 : { *(.text*) } }\n'+''.join(f'{name} = {offset+delta:#x};\n' for name,offset in bindings.items()))
    path=out/'configure.elf';subprocess.run([pre+'ld','-T',str(ld),str(obj),'-o',str(path)],check=True)
    elf=Elf32(path.read_bytes(),'configure');allocated=[s for s in elf.sections if s['flags']&2 and s['size']];assert len(allocated)==1
    sec=allocated[0];body=elf.contents(sec);assert len(body)<=376
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    report_path=ROOT/'build/gx8002-fft-q15-uart-cluster-integration-experiment/build-report.json';prior=json.loads(report_path.read_text())
    composed=report_path.parent/'firmware_codec.unadmitted.bin'
    assert sha(composed.read_bytes())==prior['firmware_sha256']
    inventory=[]
    for name in sorted(undefined):
        address=bindings[name];row=next(r for r in prior['ownership'] if r['offset']<=address<r['offset']+r['size'])
        inventory.append({'symbol':name,'offset':address,'current_kind':row['kind'],'current_symbol':row.get('symbol')})
    (out/'configure.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(path)],text=True))
    result={'source_sha256':sha(source.read_bytes()),'command':command,'elf_sha256':sha(path.read_bytes()),'code_bytes':len(body),'stock_envelope_bytes':376,'stock_identical':body==stock[0x3cce4:0x3cce4+len(body)],'dependencies':inventory,'ownership_report_sha256':sha(report_path.read_bytes()),'source_admitted':False,'limits':['Complete recovered shared C fits backup envelope. Absolute bindings do not constitute authenticated/executed dependency closure.','Ordered MMIO traces, FIFO/IRQ behavior, exceptional baud inputs and integration pending.']}
    (ROOT/'docs/research/gx8002-backup-uart-configure.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    r=build();print(r['code_bytes'],r['dependencies'])
