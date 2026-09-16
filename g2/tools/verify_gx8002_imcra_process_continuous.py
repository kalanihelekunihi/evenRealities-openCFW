# SPDX-License-Identifier: MIT
"""Continuous processing development check with explicit zero-FFT helper model."""
import json,subprocess,math,random
from build_gx8002_imcra_process import build,ROOT
from verify_gx8002_memcpy_source import decode
from execute_gx8002_imcra_state import execute as initialize
from execute_gx8002_imcra_process import execute

def verify(concrete_fft=False,signal="impulse",lto=False,stock_fft=False,placed=False,startup=False):
    assert sum(bool(v) for v in (placed,lto,startup))<=1
    assert not stock_fft or concrete_fft
    assert signal in ("impulse","tone","noise","extrema")
    assert concrete_fft or signal=="impulse"
    evidence=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    fixture=decode((ROOT/'build/gx8002-backup-imcra-state/state.disassembly.txt').read_text())
    memory=initialize(fixture,0x1000e384)['memory']
    for address in range(0x20010000,0x20010000+43008):memory.setdefault(address,0)
    for address in range(0x21000000,0x21001000):memory[address]=0
    if concrete_fft:
        from build_transparent_image import Elf32
        from verify_gx8002_source_rfft_cluster import execute as fft_execute
        fft_path=ROOT/'build/gx8002-backup-startup-cluster/cluster.elf'
        fft_elf=Elf32(fft_path.read_bytes(),'fft')
        fft_code=decode((fft_path.parent/'cluster.disassembly.txt').read_text())
        fft_memory={section['address']+i:v for section in fft_elf.sections if section['flags']&2 and not section['flags']&4 for i,v in enumerate(fft_elf.contents(section))}
    if stock_fft:
        from gx8002_imcra_stock_fft import make_fft
        stock_transform=make_fft()
    def helper(name,source):
        def run(r,f,mem,trace,read,write):
            a,b,c=r['r0'],r['r1'],r['r2'];result=0
            trace.append((name,a,b) if name=='peak' else (name,a,b,c))
            if name in ('copy','move'):
                data=[read(b+i,1) for i in range(c)]
                for i,v in enumerate(data):mem[a+i]=v
                result=a
            elif name=='clear':
                for i in range(c):mem[a+i]=b&255
                result=a
            elif name=='peak':
                values=[read(a+i*2,2) for i in range(max(1,b))]
                peak=max(abs(v-65536 if v&32768 else v) for v in values)
                result=peak.bit_length()-15 if peak else -15
            elif name=='shift':
                amount=c if c<0x80000000 else c-0x100000000;assert abs(amount)<=31
                for i in range(b):
                    v=read(a+i*2,2);v=v-65536 if v&32768 else v
                    v=(v>>amount if amount>0 else v<<-amount)&65535
                    mem[a+i*2]=v&255;mem[a+i*2+1]=v>>8
            elif name=='fft':
                if concrete_fft:
                    inverse=a==0x2001700c;assert inverse or a==0x20017020
                    values=[read(b+i*2,2) for i in range(514 if inverse else 512)]
                    values=[v-65536 if v&32768 else v for v in values]
                    if stock_fft and not source:updated,output=stock_transform(values,inverse)
                    else:updated,output=fft_execute(fft_code,0x1000ef64,values,fft_memory,a,512 if inverse else 514)
                    for base,data in ((b,updated),(c,output)):
                        for i,v in enumerate(data):mem[base+i*2]=v&255;mem[base+i*2+1]=(v>>8)&255
                else:
                    for i in range(1028 if a==0x20017020 else 1024):mem[c+i]=0
            for i in (0,1,2,3,12,13,*range(18,32)):r[f'r{i}']=0xdead0000+i
            for i in range(8):f[f'fr{i}']=0xdead1000+i
            r['r0']=result&0xffffffff
        return run
    targets={0x422a8:'move',0x49c84:'copy',0x49d04:'clear',0x46c04:'peak',0x46bcc:'shift',0x478a4:'fft'}
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x4e674','--stop-address=0x4f10e',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new=decode((ROOT/'build/gx8002-imcra-process/prepare.disassembly.txt').read_text())
    candidate_entry=0x10015d34
    if lto:
        from probe_gx8002_imcra_process_lto import probe
        from build_transparent_image import Elf32
        evidence['lto']=probe()
        variant='lto' if lto is True else lto
        assert variant in ('lto','lto-no-loop','lto-register-barriers','lto-register-barriers-shared-min')
        candidate=ROOT/f'build/gx8002-imcra-process-{variant}/process.elf'
        candidate_elf=Elf32(candidate.read_bytes(),'lto')
        candidate_entry=next(s['value'] for s in candidate_elf.symbols() if s['name']=='open_cfw_gx8002_imcra_process')
        new=decode((candidate.parent/'process.disassembly.txt').read_text())

    if placed:
        from build_gx8002_imcra_process_placed import build as build_placed
        evidence['placed']=build_placed()
        new=decode((ROOT/'build/gx8002-imcra-process-placed/process.disassembly.txt').read_text())

    if startup:
        import hashlib
        from build_transparent_image import Elf32
        candidate=ROOT/'build/gx8002-backup-startup-cluster/cluster.elf'
        candidate_elf=Elf32(candidate.read_bytes(),'startup')
        symbols={s['name']:s for s in candidate_elf.symbols()}
        for name in ('open_cfw_gx8002_imcra_process','open_cfw_imcra_min_scan',*evidence['helper_bindings']):
            assert symbols[name]['section'] not in (0,0xfff1)
        candidate_entry=symbols['open_cfw_gx8002_imcra_process']['value']
        assert candidate_entry==0x10015d34
        evidence['startup_elf_sha256']=hashlib.sha256(candidate.read_bytes()).hexdigest()
        new=decode((candidate.parent/'cluster.disassembly.txt').read_text())

    cases=0;sequences=[];nonzero_output_frames=0
    rng=random.Random(0x4e674)
    for mode in (0,2):
        for fused in (False,True):
            memories=[dict(memory),dict(memory)]
            for mem in memories:
                for i in range(4):mem[0x200100bc+i]=(mode>>(8*i))&255
            for frame in range(4 if concrete_fft else 12):
                if concrete_fft:
                    samples=[]
                    for i in range(256):
                        n=frame*256+i
                        sample=(12000 if i==frame*13 else 0) if signal=='impulse' else int(16000*math.sin(2*math.pi*997*n/16000)) if signal=='tone' else rng.randrange(-16000,16001) if signal=='noise' else (-32768 if n%2 else 32767)
                        samples.append(sample&65535)
                    for mem in memories:
                        for i,sample in enumerate(samples):
                            mem[0x21000000+i*2]=sample&255;mem[0x21000001+i*2]=sample>>8
                results=[]
                for index,(source,code,entry) in enumerate(((False,old,0x4e674),(True,new,candidate_entry))):
                    helpers={(k-0x38940+0x10000000 if source else k):helper(v,source) for k,v in targets.items()}
                    results.append(execute(code,entry,memories[index],[0x20010000,0x21000000,0x21000800],helpers,fused=fused))
                assert results[0]['memory']==results[1]['memory'],(mode,fused,frame)
                memories=[result['memory'] for result in results]
                counter=sum(memories[1][0x20010020+i]<<(8*i) for i in range(4))
                assert counter==frame+1
                if not concrete_fft:assert all(memories[1][0x21000800+i]==0 for i in range(512))
                if any(memories[1][0x21000800+i] for i in range(512)):nonzero_output_frames+=1
                cases+=1
            sequences.append({'mode':mode,'fused':fused,'frames':4 if concrete_fft else 12})
    report={'build':evidence,'cases':cases,'sequences':sequences,'source_admitted':False,'limits':['Continuous zero-input sequences with FFT output forced zero by model.', 'Other helpers modeled; actual internal candidate stages execute with shared registers/stack/memory and saved ABI checks.', 'Final memory compared after every frame, not ordered reads or complete trace; no real FFT, general signal, hardware or placement qualification.']}
    report['nonzero_output_frames']=nonzero_output_frames
    if concrete_fft:assert nonzero_output_frames>0
    report['stock_fft']=stock_fft
    report['lto']=lto
    report['placed']=placed
    report['startup']=startup
    report['signal']=signal
    report['concrete_fft']=concrete_fft
    if concrete_fft:report['limits']=[f'Continuous {signal} sequences; actual source FFT executes at a helper boundary for BOTH stock and source callers.', 'FFT stock equivalence relies on separate decoded FFT tests; this does not execute stock FFT here. Separate FFT register/stack model.', 'Other helpers remain models. Final memory and saved processing ABI compared; no ordered-read or hardware qualification.']
    if stock_fft:report['limits']=['Continuous processing with decoded stock radix/split arithmetic and compiled source FFT at separate helper boundaries.', 'Stock FFT wrapper/reversal composition is modeled; kernel instructions execute. Source FFT internal calls execute. Tables generated from reconstructed coefficients.', 'Other helpers modeled, final memory and processing ABI compared. No shared FFT stack, hardware or placement qualification.']
    (ROOT/(f'docs/research/gx8002-imcra-process-source-fft-{signal}{"-stock-fft" if stock_fft else ""}{("-"+variant) if lto else ""}{"-placed" if placed else ""}{"-startup" if startup else ""}.json' if concrete_fft else 'docs/research/gx8002-imcra-process-continuous.json')).write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
