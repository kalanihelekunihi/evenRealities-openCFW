from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Authenticated command apply307d0c'):s.index('/* Authenticated command association apply307fcc')]
for unit in [784,912]:b=b.replace('__asm__ volatile("mpyuw %0,%1,'+str(unit)+'":"=r"(offset):"r"(id));','offset=host_mpy(id,'+str(unit)+'u);')
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static uint32_t host_mpy(uint32_t id,uint32_t unit){assert(id<8&&(unit==784||unit==912));return id*unit;}
'''+b+r'''
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;for(unsigned id=0;id<8;id++)for(unsigned mode=0;mode<256;mode++){uintptr_t row=0x803d7eu + id*784;*(uint8_t *)row=99;*(uint8_t *)(row+1)=88;assert(opencfw_em9305_command_apply_307d0c(id,mode)==row&&*(uint8_t *)row==((mode&1)?0:1)&&*(uint8_t *)(row+1)==((mode&1)?((mode>>1)&1):88));cases++;}
for(unsigned id=0;id<8;id++)for(unsigned active=0;active<256;active++){uintptr_t row=0x803d78+id*784;*(uint8_t *)row=active;assert(opencfw_em9305_command_ready_3213d0(id)==(id<=5&&active!=0));cases++;}
for(unsigned count=0;count<10;count++)for(unsigned id=0;id<8;id++)for(unsigned active=0;active<2;active++){memset((void *)0x800000,0,0x100000);*(uint32_t *)0x805cac=0x810000;*(uint8_t *)0x810022=count;*(uint32_t *)0x805c70=0x820000;uintptr_t row=0x820000+id*912;*(uint8_t *)row=active;*(uint16_t *)(row+618)=88;*(uint16_t *)(row+616)=77;*(uint8_t *)(row+614)=66;unsigned expected=id<count&&active;assert(opencfw_em9305_command_apply_309874(id,0x12345,0x23456,0x34567,0xffffffff)==(expected?0:2));assert(*(uint16_t *)(row+618)==(expected?0x4567:88)&&*(uint16_t *)(row+616)==(expected?0x3456:77)&&*(uint8_t *)(row+614)==(expected?0x45:66));cases++;}
printf("PASS %u\n",cases);}
'''
p=Path(__file__).with_name('command-2059-apply-host.c');p.write_text(h)
out=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/test && /tmp/test'],text=True)
print(out.strip());p.with_name('command-2059-apply-host-receipt.json').write_text(json.dumps({'result':out.strip(),'scope':'Selected three bodies; MPYUW normalized only for bounded ids0..7. All mode/readiness bytes, id guard, row activity and low-width fields. No native DSP execution/layout/hardware proof.'},indent=2)+'\n')
