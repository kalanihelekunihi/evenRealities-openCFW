from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native30e38c..'):s.index('/* Native307044..')]
body=body.replace('uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;','uintptr_t config=(uintptr_t)configuration;').replace('*(volatile uint16_t *)(uintptr_t)0x805ab8u','stored_timing').replace('*(volatile uint16_t *)(uintptr_t)0x805ab6u','stored_size')
h=r"""
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
static _Alignas(2) uint8_t configuration[40];static uint16_t stored_timing,stored_size;
"""+body+r"""
int main(void){unsigned cases=0;unsigned times[]={0,327,328,2120,2121,17040,17041,65535};unsigned versions[]={0,8,9,255};unsigned limits[]={0,26,27,100,251,252,65535};
for(unsigned size=0;size<65536;size++){for(unsigned t=0;t<8;t++){for(unsigned v=0;v<4;v++){for(unsigned m=0;m<7;m++){
 unsigned timing=times[t],version=versions[v],max=limits[m];configuration[4]=version;*(uint16_t *)(configuration+38)=max;stored_timing=0x5aa5;stored_size=0xa55a;
 unsigned want=size<27||size>251||timing<328||(timing>=2121&&version<9)||(timing>=17041&&version>=9)?48:size>(max<251?max:251)?17:0;
 assert(opencfw_em9305_ll_connection_value_30e38c(size,timing)==want);assert(stored_size==(want?0xa55a:size)&&stored_timing==(want?0x5aa5:timing));cases++;
}}}}printf("%u\n",cases);return 0;}
"""
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],check=True);cases=int(subprocess.check_output([str(d/'test')],text=True))
r={'cases_passed':cases,'native_range':'30e38c..30e3e8','scope':'Actual selected C with normalized configuration/live output RAM; exhaustive16-bit size and timing/version/maximum boundary inputs; status and failure output preservation; native-reading contracts, not native runtime equality','body_sha256':hashlib.sha256(body.encode()).hexdigest()};Path(__file__).with_name('connection-value-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(f'PASS{cases} controlled connection value cases')
