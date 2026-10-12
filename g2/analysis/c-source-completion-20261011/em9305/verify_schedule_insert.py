from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();s=s[s.index('/* Native schedule313220'):s.index('/* Native duration332be4')]
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned guards,transitions;
static uint32_t opencfw_em9305_pal_current_time(void){return 100;}
static uint32_t opencfw_em9305_auxiliary_guard_interval(void){guards++;return 1;}
static uint32_t opencfw_em9305_auxiliary_transition_333a60(void){transitions++;return 17;}
'''+s+r'''
static void put(uintptr_t p,unsigned off,uint32_t v){*(uint32_t *)(p+off)=v;}
static uint32_t get(uintptr_t p,unsigned off){return *(uint32_t *)(p+off);}
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);uintptr_t root=0x805f04,head=0x820000,next=0x830000,object=0x840000;unsigned cases=0;
for(unsigned mode=0;mode<2;mode++)for(unsigned special=0;special<2;special++)for(unsigned gap=0;gap<2;gap++){memset((void *)root,0,32);memset((void *)head,0,32);memset((void *)next,0,32);memset((void *)object,0xa5,32);*(uint8_t *)root=mode?2:1;put(root,16,head);put(root,20,next);put(head,0,0);put(head,4,next);put(head,8,0);put(head,12,10);put(head,16,special?4:0);put(next,0,head);put(next,4,0);put(next,8,gap?100:15);put(next,12,10);put(object,12,5);guards=transitions=0;assert(opencfw_em9305_auxiliary_insert_313220(object)==head&&!transitions);unsigned between=gap||(special&&!gap);if(between){assert(get(head,4)==object&&get(object,0)==head&&get(object,4)==next&&get(next,0)==object&&get(root,20)==next&&get(object,8)==(special?5:11)&&guards==4);}else{assert(get(head,4)==next&&get(next,4)==object&&get(object,0)==next&&get(object,4)==0&&get(root,20)==object&&get(object,8)==26&&guards==5);}cases++;}
for(unsigned mode=0;mode<2;mode++){memset((void *)root,0,32);memset((void *)head,0,32);memset((void *)object,0xa5,32);*(uint8_t *)root=mode?2:1;put(root,16,head);put(root,20,head);put(head,8,100);put(head,12,10);put(object,12,5);guards=transitions=0;unsigned result=opencfw_em9305_auxiliary_insert_313220(object);if(!mode){assert(result==17&&transitions==1&&guards==2&&get(root,16)==object&&get(root,20)==head&&get(object,0)==0&&get(object,4)==head&&get(head,0)==object&&get(object,8)==101);}else{assert(result==head&&!transitions&&guards==3&&get(root,16)==head&&get(root,20)==object&&get(object,0)==head&&get(object,4)==0&&get(object,8)==111);}cases++;}
memset((void *)root,0,32);memset((void *)object,0xa5,32);guards=transitions=0;assert(opencfw_em9305_auxiliary_insert_313220(object)==17&&transitions==1&&guards==1&&get(root,16)==object&&get(root,20)==object&&get(object,0)==0&&get(object,4)==0&&get(object,8)==101);cases++;
printf("PASS %u\n",cases);}
''';p=Path(__file__).with_name('schedule-insert-host.c');p.write_text(h);a=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/i && /tmp/i'],text=True);print(a.strip());p.with_name('schedule-insert-host-receipt.json').write_text(json.dumps({'result':a.strip(),'scope':'Actual scheduler with controlled time/guard/transition. Empty/prepend/current-object append, gap/tail insertion, special head timing, link reciprocity, guard counts. No target runtime proof.'},indent=2)+'\n')
