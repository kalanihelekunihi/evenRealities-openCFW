from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native32f70c..'):s.index('/* Native32f770..')]
body=body.replace('*(volatile uint8_t *)(uintptr_t)0x8056fcu','first_flags').replace('*(volatile uint8_t *)(uintptr_t)0x8056efu','second_flags')
h=r"""
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint8_t input[16],output[16],expected[16],first_flags,second_flags;static unsigned allocation_ok,alias,allocations,sends;static uint8_t *destination;
uintptr_t opencfw_em9305_ll_event_allocate(uint32_t type,uint32_t n){assert(type==0x3e&&n==12);allocations++;if(!allocation_ok)return 0;destination[0]=type;destination[1]=n;return (uintptr_t)(destination+2);}
uint32_t opencfw_em9305_ll_event_send(uintptr_t p){assert(p==(uintptr_t)destination&&memcmp(destination,expected,16)==0);sends++;return 0xdeadbeef;}
"""+body+r"""
int main(void){unsigned cases=0;unsigned fs[]={0,4,255,251},ss[]={0,32,255,223};
for(unsigned command=0;command<256;command++){for(unsigned f=0;f<4;f++){for(unsigned g=0;g<4;g++){for(allocation_ok=0;allocation_ok<2;allocation_ok++){for(alias=0;alias<2;alias++){for(unsigned b=0;b<16;b++){
 for(unsigned i=0;i<16;i++)input[i]=(uint8_t)(17*b+i*13);input[2]=command;memset(output,0xa5,16);destination=alias?input:output;memcpy(expected,destination,16);first_flags=fs[f];second_flags=ss[g];allocations=sends=0;
 unsigned eligible=command==0x33&&(first_flags&4)&&(second_flags&32),ok=eligible&&allocation_ok;
 if(ok){expected[0]=0x23;expected[1]=12;expected[3]=input[4];for(unsigned i=0;i<10;i++)expected[4+i]=input[6+i];}
 assert(opencfw_em9305_dispatch_32f70c((uintptr_t)input)==ok&&allocations==eligible&&sends==ok&&memcmp(destination,expected,16)==0);cases++;
}}}}}}printf("%u\n",cases);return 0;}
"""
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],check=True);cases=int(subprocess.check_output([str(d/'test')],text=True))
r={'cases_passed':cases,'native_range':'32f70c..32f76e','scope':'Actual selected C with normalized live mask bytes and controlled allocation/send; all event selector bytes, gate bit boundaries, allocation failure, source/destination alias and complete output including untouched bytes; native-reading contracts, not native runtime equality','body_sha256':hashlib.sha256(body.encode()).hexdigest()};Path(__file__).with_name('event33-relay-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(f'PASS{cases} controlled event33 relay cases')
