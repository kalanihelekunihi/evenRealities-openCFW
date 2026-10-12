from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text()
def body(signature):
 a=s.index(signature);b=s.index('{',a);depth=1;c=b+1
 while depth:
  depth+=(s[c]=='{')-(s[c]=='}');c+=1
 return s[a:c]
h=r"""#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned allocations,sends,fail,allocated_type,allocated_size;
static uint8_t output[40];
static uintptr_t opencfw_em9305_ll_event_allocate(uint32_t t,uint32_t n){allocations++;allocated_type=t;allocated_size=n;return fail?0:(uintptr_t)(output+2);}
static uint32_t opencfw_em9305_ll_event_send(uintptr_t p){assert(p==(uintptr_t)output);sends++;return 91;}
"""+body('void *opencfw_em9305_memcpy(void *destination')+'\n'+body('uintptr_t opencfw_em9305_radio_address_copy_304604(uintptr_t output')+'\n'+s[s.index('/* Native event32f0a0'):s.index('/* Native330664..330848')]+r"""
struct row{unsigned type,off,mask,event,size,sub,le;};
static const struct row rows[]={{5,16,1,62,19,1,1},{6,0,16,5,4,0,0},{7,16,4,62,10,3,1},{9,1,8,12,8,0,0},{10,16,8,62,12,4,1},{16,16,32,62,11,6,1},{18,16,64,62,11,7,0},{46,19,64,62,5,31,1},{47,20,1,62,9,33,1},{48,19,128,62,5,32,1}};
static void expected(uint8_t *e,const uint8_t *p,unsigned t){
 switch(t){
 case 5:e[1]=p[4];memcpy(e+2,p+6,3);e[5]=(p[9]==2||p[9]==3)?1:p[9];memcpy(e+6,p+((p[9]==2||p[9]==3)?29:10),6);memcpy(e+12,p+16,7);break;
 case 6:e[0]=p[4];memcpy(e+1,p+6,3);break;
 case 7:e[1]=p[4];memcpy(e+2,p+6,8);break;
 case 9:e[0]=p[4];memcpy(e+1,p+6,3);memcpy(e+4,p+10,4);break;
 case 10:e[1]=p[4];memcpy(e+2,p+6,2);memcpy(e+4,p+8,8);break;
 case 16:case 18:memcpy(e+1,p+4,10);break;
 case 46:e[1]=p[4];memcpy(e+2,p+6,3);break;
 case 47:e[1]=p[4];memcpy(e+2,p+6,7);break;
 case 48:memcpy(e+1,p+4,4);break;
 }
}
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;
for(unsigned t=0;t<256;t++)for(unsigned gates=0;gates<4;gates++)for(fail=0;fail<2;fail++)for(unsigned kind=0;kind<256;kind++){
 uint8_t p[40],e[40];for(unsigned j=0;j<40;j++)p[j]=(uint8_t)(j*37+kind*11+t);p[2]=t;p[9]=kind;memset(output,0xa5,40);memset(e,0xa5,40);memset((void *)0x8056e8,0,24);allocations=sends=0;const struct row *r=0;for(unsigned j=0;j<10;j++)if(rows[j].type==t)r=rows+j;
 if(r){*(uint8_t *)(uintptr_t)(0x8056e8+r->off)=(gates&1)?r->mask:0;*(uint8_t *)0x8056ef=(gates&2)?32:0;}
 unsigned admitted=r&&(gates&1)&&(!r->le||(gates&2));unsigned ok=admitted&&!fail;uint32_t v=opencfw_em9305_dispatch_32f0a0((uintptr_t)p);assert(v==ok&&allocations==admitted&&sends==ok);
 if(admitted)assert(allocated_type==r->event&&allocated_size==r->size);
 if(ok){if(r->sub)e[2]=r->sub;expected(e+2,p,t);}assert(!memcmp(output,e,40));cases++;
}
printf("PASS %u\n",cases);}
"""
p=Path(__file__).with_name('event32f0a0-host.c');p.write_text(h)
a=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/e && /tmp/e'],text=True);print(a.strip());p.with_name('event32f0a0-host-receipt.json').write_text(json.dumps({'result':a.strip(),'scope':'Actual generic dispatcher and actual selected memcpy/address-copy with controlled allocation/send. All packet types, feature gates, failures, address-kind bytes; native projection matrix and untouched buffer bytes checked. No native runtime/hardware claim.'},indent=2)+'\n')
