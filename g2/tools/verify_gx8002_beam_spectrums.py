# SPDX-License-Identifier: MIT
"""Decoded beam core comparison; DSP and FFT calls explicitly modeled."""
import json,random,subprocess
from build_gx8002_beam_spectrums import build,ROOT
from verify_gx8002_memcpy_source import decode
from execute_gx8002_imcra_process import execute

def verify(startup=False,concrete_fft=False,entry_wrapper=False):
    assert not entry_wrapper or startup
    assert not concrete_fft or startup
    evidence=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x45be4','--stop-address=0x45dac',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new=decode((ROOT/'build/gx8002-beam-spectrums/spectrums.disassembly.txt').read_text())
    if startup:
        from build_transparent_image import Elf32
        from analyze_gx8002_upstream_objects import sha
        target=ROOT/'build/gx8002-backup-startup-cluster/cluster.elf'
        elf=Elf32(target.read_bytes(),'startup')
        symbols={s['name']:s for s in elf.symbols()}
        for name in ('open_cfw_gx8002_beam_spectrums',*evidence['helper_bindings']):
            assert symbols[name]['section'] not in (0,0xfff1)
        if entry_wrapper:
            wrapper=symbols['beamforming_triMic_spectrums']
            assert wrapper['section'] not in (0,0xfff1) and wrapper['value']==0x1000de94
        evidence['startup_elf_sha256']=sha(target.read_bytes())
        new=decode((target.parent/'cluster.disassembly.txt').read_text())
    if concrete_fft:
        from gx8002_imcra_stock_fft import make_fft
        from verify_gx8002_source_rfft_cluster import execute as fft_execute
        stock_fft=make_fft()
        fft_memory={section['address']+i:v for section in elf.sections if section['flags']&2 and not section['flags']&4 for i,v in enumerate(elf.contents(section))}
    rng=random.Random(0x45be4);cases=0;nonzero_fft_cases=0
    def signed(v):return v-65536 if v&32768 else v
    for channels in ((1,2,3) if concrete_fft else (0,1,2,3)):
      for samples in ((256,512) if concrete_fft else (1,7,32)):
       for frame in ((0,5) if concrete_fft else (0,1,5)):
        for amplitude in ((0,128,32768) if concrete_fft else (0,1,128,32767,32768)):
         mem={a:0 for a in range(0x21000000,0x2100c000 if concrete_fft else 0x21006000)}
         def put(a,v,n=4):
            for i in range(n):mem[a+i]=(v>>(8*i))&255
         state=0x21000000;inputs=0x21001000;work=0x21002000;window=0x21003000
         for index,value in {1:channels,2:4,3:samples,5:512 if concrete_fft else 64,6:257 if concrete_fft else 65,28:window,30:0x21006000 if concrete_fft else 0x21004000,31:0x21009000 if concrete_fft else 0x21005000,33:work,37:state+256}.items():put(state+index*4,value)
         for i in range(samples*channels):put(inputs+2*i,rng.choice((-amplitude,amplitude)),2)
         for i in range(samples):put(window+4*i,rng.choice((0,16384,32767,65535,0xffffffff)))
         def helper(name):
          def run(r,f,m,trace,read,write):
            a,b,c,d=(r[f'r{i}'] for i in range(4))
            if name=='peak':
             trace.append((name,a,c))
             v=max((min(32767,abs(signed(read(a+2*i,2)))) for i in range(c)),default=0)
             write(b,v,2)
            elif name=='shift':
             trace.append((name,a,b,c,d))
             for i in range(d):write(c+2*i,max(-32768,min(32767,signed(read(a+2*i,2))*(1<<b))),2)
            elif name=='fill':
             trace.append((name,a,b,c))
             for i in range(c):write(b+2*i,a,2)
            else:
             trace.append((name,a,b,c))
             if concrete_fft:
                assert a==0x20017020
                values=[signed(read(b+2*i,2)) for i in range(512)]
                updated,output=fft_execute(new,0x1000ef64,values,fft_memory,a,514) if source else stock_fft(values,False)
                for address,data in ((b,updated),(c,output)):
                    for i,v in enumerate(data):write(address+2*i,v,2)
             else:
                for i in range(64):write(c+2*i,read(b+2*i,2)^0x1234,2)
            for i in (0,1,2,3,12,13,*range(18,32)):r[f'r{i}']=0xdead0000+i
            for i in range(8):f[f'fr{i}']=0xdead1000+i
          return run
         targets={0x47a74:'peak',0x47a00:'shift',0x47aec:'fill',0x478a4:'fft'}
         results=[]
         for source,code,entry in ((False,old,0x45be4),(True,new,0x1000de94 if entry_wrapper else 0x1000d2a4)):
          helpers={(a-0x38940+0x10000000 if source else a):helper(n) for a,n in targets.items() if not (startup and source and n!='fft')}
          results.append(execute(code,entry,mem,[state,inputs,frame],helpers))
         if startup:
            assert results[0]['memory']==results[1]['memory'] and results[0]['result']==results[1]['result'],(channels,samples,frame,amplitude)
         else:assert results[0]==results[1],(channels,samples,frame,amplitude)
         if concrete_fft:
            nonzero=any(v for a,v in results[1]['memory'].items() if 0x21006000<=a<0x2100c000)
            if amplitude==0:assert not nonzero
            else:assert nonzero
            nonzero_fft_cases+=int(nonzero)
         cases+=1
    report={'entry_wrapper':entry_wrapper,'nonzero_fft_cases':nonzero_fft_cases,'concrete_fft':concrete_fft,'startup':startup,'build':evidence,'cases':cases,'source_admitted':False,'limits':['Decoded stock/core C comparison with modeled DSP/FFT helpers and caller clobbers.','Final memory, ordered nonstack writes/helper calls and saved ABI compared for bounded valid states.','FFT is an input-sensitive stand-in; DSP saturation model and physical instructions need independent verification. No hardware/source closure claim.']}
    if startup:report['limits']=['Integrated source core/peak/shift/fill execute with shared registers and stack; stock DSP helpers modeled as in standalone checks.', 'Final memory/result and saved ABI compared; helper call traces differ. FFT remains an input-sensitive stand-in. No hardware qualification.']
    if concrete_fft:report['limits']=['Integrated source DSP helpers execute on the core stack; source FFT and decoded stock FFT execute at separate helper boundaries.', 'Stock DSP helpers and stock FFT wrapper/reversal composition remain modeled. Final memory/result and saved core ABI compared.', 'No complete beam output/initializer, continuous-stream, physical FPU or hardware qualification.']
    (ROOT/('docs/research/gx8002-beam-spectrums-verification'+('-startup' if startup else '')+('-fft' if concrete_fft else '')+('-entry' if entry_wrapper else '')+'.json')).write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
