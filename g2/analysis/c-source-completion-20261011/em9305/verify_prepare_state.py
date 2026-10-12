from pathlib import Path
import subprocess,re,json
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text()
b=s[s.index('/* Authenticated preparation state 32d694'):s.index('/* Authenticated packet advance 32d738')]
b=re.sub(r'__asm__ volatile\("mpyuw %0,%1,%2".*?;','product=unit*index;',b)
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <string.h>
#include <stdio.h>
#include <sys/mman.h>
uintptr_t opencfw_em9305_wsf_event_peek(uintptr_t queue,uintptr_t handler){uint32_t node=*(volatile uint32_t *)queue;if(!node)return 0;*(volatile uint8_t *)handler=*(volatile uint8_t *)(uintptr_t)(node+4);return node+8;}
'''+b+r'''
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;uintptr_t p=0x860000,state=0x870000,flag=0x880000,node=0x840000,packet=node+8;uint8_t in[3],out[8];
for(unsigned a=0;a<256;a++)for(unsigned c=0;c<256;c++){in[0]=a;in[1]=77;in[2]=c;memset(out,0xa5,8);unsigned n=opencfw_em9305_short_header_decode_32dedc((uintptr_t)out,(uintptr_t)in);assert(n==((a&32)?3:2));assert(out[0]==(a&3)&&out[1]==((a>>2)&1)&&out[2]==((a>>3)&1)&&out[3]==((a>>4)&1)&&out[4]==((a>>5)&1)&&out[5]==77);assert(out[6]==((a&32)?c>>6:0xa5)&&out[7]==((a&32)?c&31:0xa5));cases++;}
memset((void *)state,0xa5,24);assert(opencfw_em9305_radio_prepare_state_32d694(p,state,flag)==0&&*(uint8_t *)flag==0&&*(uint32_t *)state==0xa5a5a5a5);cases++;
for(unsigned single=0;single<2;single++)for(unsigned header=0;header<2;header++){*(uint32_t *)(p+360)=node;*(uint32_t *)(p+364)=single?node:node+100;*(uint8_t *)(node+4)=255;*(uint8_t *)packet=header?32:0;*(uint8_t *)(packet+1)=255;assert(opencfw_em9305_radio_prepare_state_32d694(p,state,flag)==1);assert(*(uint16_t *)state==255+2+header&&*(uint32_t *)(state+4)==packet&&*(uint8_t *)flag==!single);cases++;}
for(unsigned single=0;single<2;single++)for(unsigned ix=0;ix<8;ix++)for(unsigned unit=0;unit<256;unit++)for(unsigned len=0;len<300;len+=37)for(unsigned extra=0;extra<2;extra++){memset((void *)packet,0,100);memset((void *)state,0xa5,24);*(uint32_t *)(p+360)=node;*(uint32_t *)(p+364)=single?node:node+100;*(uint8_t *)(node+4)=2;*(uint32_t *)packet=0x830000;*(uint16_t *)(packet+4)=len;*(uint8_t *)(packet+6)=unit;*(uint8_t *)(packet+7)=ix;*(uint8_t *)(packet+ix*8+8)=23;*(uint8_t *)(packet+ix*8+9)=extra?17:0;unsigned product=unit*ix,u=len<product+unit?len-product:unit;unsigned kind=opencfw_em9305_radio_prepare_state_32d694(p,state,flag);assert(kind==2+extra);assert(*(uint16_t *)state==23&&*(uint16_t *)(state+8)==(uint16_t)u&&*(uint32_t *)(state+4)==packet+ix*8+10&&*(uint32_t *)(state+12)==0x830000+product);assert(*(uint8_t *)flag==(!single||product+(uint16_t)u<len));if(extra)assert(*(uint16_t *)(state+16)==17&&*(uint32_t *)(state+20)==packet+ix*8+12);else assert(*(uint32_t *)(state+16)==0xa5a5a5a5&&*(uint32_t *)(state+20)==0xa5a5a5a5);cases++;}
printf("PASS %u\n",cases);}
'''
p=Path(__file__).with_name('prepare-state-host.c');p.write_text(h)
out=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/test && /tmp/test'],text=True)
print(out.strip());p.with_name('prepare-state-host-receipt.json').write_text(json.dumps({'result':out.strip(),'scope':'Host fixed RAM queue/header/segmentation cases including unsigned truncation and untouched optional fields. MPYUW normalized to unsigned multiplication. No native ARC runtime, layout or hardware proof.'},indent=2)+'\n')
