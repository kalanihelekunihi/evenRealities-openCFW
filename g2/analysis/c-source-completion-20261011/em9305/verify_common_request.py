from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();s=s[s.index('/* Native request30455c'):s.index('/* Native schedule313220')].replace('__asm__ volatile("mpyuw %0,%1,24":"=r"(offset):"r"(index));','offset=index*24u;')
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <sys/mman.h>
static unsigned calls,mutate;
static uint32_t opencfw_em9305_auxiliary_select_314d94(uint32_t index){calls++;if(mutate)*(uint32_t *)(uintptr_t)(0x801658+index*24)=99;*(uint8_t *)0x8016bd=1;return index;}
'''+s+r'''
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;uint32_t values[]={0,1,0x7fffffff,0xffffffff};for(unsigned index=0;index<8;index++)for(unsigned selected=0;selected<3;selected++)for(unsigned ci=0;ci<4;ci++)for(mutate=0;mutate<2;mutate++){uintptr_t slot=0x801658+24*index;*(uint32_t *)slot=values[ci];*(uint8_t *)0x8016bd=selected;calls=0;uint32_t expected=selected==0&&mutate?100:values[ci]+1;assert(opencfw_em9305_common_request_30455c(index)==slot&&calls==(selected==0)&&*(uint32_t *)slot==expected);assert(opencfw_em9305_pal_request_noop_30fd2c(values[ci])==values[ci]);cases++;}
printf("PASS %u\n",cases);}
''';p=Path(__file__).with_name('common-request-host.c');p.write_text(h);a=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/r && /tmp/r'],text=True);print(a.strip());p.with_name('common-request-host-receipt.json').write_text(json.dumps({'result':a.strip(),'scope':'Actual request/noop C, bounded native MPYUW stride normalized, controlled select child mutating count. Gating, post-child count capture,32-bit wrap/address return. No target runtime proof.'},indent=2)+'\n')
