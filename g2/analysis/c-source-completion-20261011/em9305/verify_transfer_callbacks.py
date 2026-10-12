from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Native31df6c'):s.index('extern uint32_t opencfw_em9305_radio_prepare_32780c')]
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned calls;
uint32_t opencfw_em9305_radio_cb_31dfd0(uintptr_t p){assert(p==0x880000&&*(uint8_t *)0x802a38==0&&*(uint8_t *)0x802a34==0);calls++;return 99;}
'''+b+r'''
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);uintptr_t event=0x880000,source=0x860000;*(uint32_t *)(event+36)=source;unsigned cases=0;
for(unsigned a=0;a<256;a++)for(unsigned c=0;c<256;c++){*(uint8_t *)(source+379)=a;*(uint8_t *)(source+380)=c;assert(opencfw_em9305_radio_cb_31df6c(event)==source+379);assert(*(uint8_t *)(source+379)==(a&&c?0:a));cases++;}
for(unsigned mode=0;mode<256;mode++)for(unsigned a=0;a<2;a++)for(unsigned c=0;c<2;c++){*(uint8_t *)(source+379)=a;*(uint8_t *)(source+380)=c;*(uint8_t *)(source+1)=mode;*(uint8_t *)0x802a38=12;*(uint8_t *)0x802a34=13;calls=0;assert(opencfw_em9305_radio_cb_31dc68(event)==(mode?99:event));assert(calls==(mode!=0));assert(*(uint8_t *)(source+379)==(a&&c?0:a));assert(*(uint8_t *)0x802a38==(mode?0:12)&&*(uint8_t *)0x802a34==(mode?0:13));cases++;}
for(unsigned mode=0;mode<2;mode++)for(unsigned count=0;count<=65535;count++){*(uint8_t *)(source+341)=mode;*(uint8_t *)(source+630)=7;*(uint16_t *)(source+904)=count;*(uint16_t *)0x802a40=count;assert(opencfw_em9305_radio_cb_31e7c8(event,0)==(mode?0x802a40:count+1));assert(*(uint8_t *)(source+630)==1&&*(uint16_t *)(source+904)==(uint16_t)(count+1));assert(*(uint16_t *)0x802a40==(mode?(uint16_t)(count+1):count));cases++;}
assert(opencfw_em9305_radio_cb_31e7c8(0,1)==0);assert(opencfw_em9305_radio_cb_31e7c8(123,0xffffffff)==123);cases+=2;printf("PASS %u\n",cases);}
'''
p=Path(__file__).with_name('transfer-callbacks-host.c');p.write_text(h);output=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror /work/'+str(p.relative_to(root))+' -o /tmp/test && /tmp/test'],text=True);assert output.strip()=='PASS 197634';print(output.strip())
p.with_name('transfer-callbacks-host-receipt.json').write_text(json.dumps({'cases_passed':197634,'scope':'Host fixed RAM actual C pending-byte/status/count wrap effects and controlled tail child; status gate tested with invalid/null event addresses. No full child/native runtime/layout/hardware proof.'},indent=2)+'\n')
