from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Authenticated fragmented-report helpers'):s.index('/* Authenticated dispatch3316e0')]
b=b.replace('__asm__ volatile("divu %0,%1,247":"=r"(quotient):"r"(remaining));','quotient=remaining/247u;').replace('__asm__ volatile("mpyw %0,%1,-247":"=r"(negative_product):"r"(quotient));','negative_product=0u-quotient*247u;')
a=b.index('   register uint32_t nr0');z=b.index('   needed=nr1;',a)+len('   needed=nr1;');b=b[:a]+'   needed=(remaining>243u)+((uint8_t)(remaining+(remaining>=244u?12u:0u))!=0u);'+b[z:]
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned allocations,sends,fail_at;static uintptr_t packets[300];static uint32_t lengths[300];
static uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){assert(n==246);unsigned i=allocations++;lengths[i]=n;if(i==fail_at)return 0;return 0x830000+i*512;}
static uintptr_t opencfw_em9305_ll_event_allocate(uint32_t code,uint32_t n){assert(code==62);unsigned i=allocations++;lengths[i]=n;if(i==fail_at)return 0;return 0x830002+i*512;}
static uint32_t opencfw_em9305_ll_event_send(uintptr_t p){packets[sends++]=p+2;return 99;}
static void *opencfw_em9305_memcpy(void *d,const void *s,uint32_t n){return memcpy(d,s,n);}
static uintptr_t opencfw_em9305_radio_address_copy_304604(uintptr_t d,uintptr_t s){memcpy((void *)d,(void *)s,6);return d;}
'''+b+r'''
static void setup(unsigned type,unsigned limit){memset((void *)0x800000,0,0x100000);for(unsigned n=0;n<40;n++)*(uint8_t *)(uintptr_t)(0x810000+n)=n;*(uint8_t *)0x810002=type;*(uint8_t *)0x8056fc=255;*(uint8_t *)0x8056fd=1;*(uint8_t *)0x8056ef=32;*(uint32_t *)0x805cac=0x820000;*(uint8_t *)0x82000e=limit;*(uint8_t *)0x820004=13;allocations=sends=0;fail_at=999;}
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;
for(unsigned type=0;type<256;type++){if(type==5||type==30||type==32||type==38||type==52||type==53)continue;setup(type,10);assert(opencfw_em9305_dispatch_331334(0x810000)==0&&allocations==0);cases++;}
unsigned types[]={5,30,38,53},lens[]={34,20,24,4},ops[]={41,36,38,39};for(unsigned t=0;t<4;t++)for(unsigned alloc=0;alloc<2;alloc++){setup(types[t],10);if(!alloc)fail_at=0;assert(opencfw_em9305_dispatch_331334(0x810000)==alloc&&allocations==1&&sends==alloc&&lengths[0]==lens[t]);if(alloc){uint8_t *e=(uint8_t *)packets[0];assert(e[0]==ops[t]&&e[1]==4);if(types[t]==53)assert(e[2]==5&&e[3]==6);else assert(e[2]==6&&e[3]==7&&e[4]==8&&e[5]==9);if(types[t]==5)assert(!memcmp(e+6,(void *)0x81000a,6)&&!memcmp(e+12,(void *)0x810017,6)&&!memcmp(e+18,(void *)0x81001d,6)&&e[33]==37);if(types[t]==30)assert(!memcmp(e+6,(void *)0x81000a,6)&&e[12]==16&&e[13]==18&&e[19]==24);if(types[t]==38)assert(e[9]==13&&!memcmp(e+10,(void *)0x81000e,6)&&e[16]==20&&e[17]==22&&e[23]==28);}cases++;}
for(unsigned variant=0;variant<2;variant++)for(unsigned length=0;length<(variant?256:1000);length++)for(unsigned limit=0;limit<7;limit++)for(unsigned fail=0;fail<3;fail++){setup(variant?52:32,limit);if(variant){*(uint8_t *)0x81000d=length;*(uint32_t *)0x810010=0x850000;}else{*(uint16_t *)0x81000a=length;*(uint32_t *)0x81000c=0x850000;}for(unsigned n=0;n<1000;n++)*(uint8_t *)(uintptr_t)(0x850000+n)=n;fail_at=fail==2?999:fail;unsigned needed=variant?(unsigned)((length>243)+((uint8_t)(length+(length>=244?12:0))!=0)):(length+246)/247;unsigned actual=(length+243)/244;if(actual==0)actual=1;unsigned possible=needed<=limit;unsigned n=possible?(actual<limit?actual:limit):0;unsigned expected=possible&&actual<=limit&&fail_at>=actual;assert(opencfw_em9305_dispatch_331334(0x810000)==expected);unsigned sent=fail_at<n?fail_at:n;assert(sends==sent&&*(uint8_t *)0x805718==sent);unsigned offset=0;for(unsigned i=0;i<sends;i++){uint8_t *e=(uint8_t *)packets[i];unsigned chunk=length-offset<244?length-offset:244;assert(e[0]==(variant?40:37)&&e[10]==chunk&&!memcmp(e+11,(void *)(uintptr_t)(0x850000+offset),chunk));offset+=chunk;}cases++;}
printf("PASS %u\n",cases);}
'''
p=Path(__file__).with_name('dispatch-331334-host.c');p.write_text(h)
out=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/test && /tmp/test'],text=True);print(out.strip());p.with_name('dispatch-331334-host-receipt.json').write_text(json.dumps({'result':out.strip(),'scope':'Full six-path selected dispatch and three real helpers with controlled allocation/copy/send. Native DSP normalized: bounded16-bit DIVU/MPYW and explicit carry-conditioned byte preflight. Basic packing, unsupported types, zero/244/247 boundaries, capacity/counter/allocation/payload. Not native DSP execution or hardware proof.'},indent=2)+'\n')
