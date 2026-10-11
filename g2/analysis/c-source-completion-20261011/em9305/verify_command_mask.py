from pathlib import Path
import subprocess,tempfile,re,json
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text()
b=s[s.index('/* Native3098ac'):s.index('extern uint32_t opencfw_em9305_radio_record_ready_31ac08')]
b=re.sub(r'__asm__ volatile\("mpyuw %0,%1,%2".*?;', 'offset=(id&65535u)*784u;(void)offset;',b)
b=b.replace("*(volatile uint32_t *)(uintptr_t)(0x804084u+offset)","fixture_record").replace("(uintptr_t)(0x803f78u+offset)","(uintptr_t)&fixture_capacity")
h=r"""#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <sys/mman.h>
static uintptr_t fixture_record;
static uint8_t fixture_capacity;
"""+b+r"""
int main(void){_Alignas(4) uint8_t storage[400];uintptr_t rec=(uintptr_t)storage;fixture_record=rec;uint8_t list[16];unsigned cases=0;
for(unsigned count=0;count<=16;count++)for(unsigned capacity=0;capacity<=255;capacity++)for(unsigned seed=0;seed<=255;seed++){
fixture_capacity=capacity;*(uint32_t *)(rec+8)=0xdeadbeef;*(uint32_t *)(rec+12)=0xa55aa55a;for(unsigned i=0;i<16;i++)list[i]=(uint8_t)(seed+i*17);
unsigned expected=18;uint64_t mask=0xa55aa55adeadbeefULL;if(count>=1&&count<=15&&capacity>=count){mask=0;expected=0;for(unsigned i=0;i<count;i++){if(list[i]>=capacity){expected=18;break;}mask|=1ULL<<(list[i]&63);}}
assert(opencfw_em9305_command_apply_3098ac(0,0x12340040,count,(uintptr_t)list)==expected);assert(*(uint16_t *)(rec+366)==64);assert(*(uint32_t *)(rec+8)==(uint32_t)mask);assert(*(uint32_t *)(rec+12)==(uint32_t)(mask>>32));cases++;}
printf("%u\n",cases);}
"""
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('command-mask-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Host actual C count/capacity/list masks, flags and retained partial writes. MPYUW and fixed-address RAM mapped to host fixtures; no native ISA/runtime/hardware proof.'},indent=2)+'\n')
print('PASS',n)
