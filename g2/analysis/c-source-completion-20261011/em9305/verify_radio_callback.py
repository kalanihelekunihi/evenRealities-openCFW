from pathlib import Path
import subprocess,re,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Authenticated stock334474'):]
b=re.sub(r'__asm__ volatile\("mpyuw %0,%1,%2".*?;', 'offset=id*912u;',b)
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned calls,mutate;
void *opencfw_em9305_memcpy(void *d,const void *s,uint32_t n){return memcpy(d,s,n);}
uint32_t opencfw_em9305_radio_encode_3239d4(uintptr_t p,uintptr_t q){assert(p==0x880000+1077&&memcmp((void *)q,"\5\0\0\0\42",5)==0);assert(*(uint16_t *)(0x850000+76)==15);calls++;if(mutate)*(uint32_t *)(0x880000+2812)=0x851000;return 17;}
uint32_t opencfw_em9305_radio_encode_323c94(uintptr_t p,uintptr_t q){assert(p==0x880000+1079&&q==(mutate?0x851000:0x850000)+100);calls++;return 19;}
uint32_t opencfw_em9305_radio_transfer_31dd88(uintptr_t p,uintptr_t q,uintptr_t r){assert(p==0x840000+912*3&&q==(mutate?0x851000:0x850000)+100&&r==0x880000);assert(*(uint16_t *)(r+528)==36&&*(uint8_t *)(r+688)==1);calls++;return 77;}
uint32_t opencfw_em9305_radio_encode_324594(uintptr_t p,uintptr_t q,uintptr_t r,uint32_t n){assert(p==0x880000&&q==p+1077&&r==p+1144&&n==1);calls++;return 0x12345;}
'''+b+r'''
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;for(unsigned scenario=0;scenario<7;scenario++){memset((void *)0x800000,0,0x100000);uintptr_t r=0x880000,control=0x850000,buffer=0x860000;calls=0;mutate=scenario==6;
*(uint32_t *)(r+2812)=control;*(uint32_t *)(r+1160)=buffer;*(uint32_t *)(r+1148)=0x830000;*(uint32_t *)0x805c70=0x840000;*(uint16_t *)(control+94)=3;*(uint16_t *)(0x851000+94)=3;*(uint8_t *)(r+799)=130;
*(uint8_t *)(control+77)=scenario==0||scenario==6;unsigned index=scenario==4?33:scenario==5?65:1;*(uint8_t *)(buffer+3854)=scenario==1?255:index;uintptr_t entry=buffer+index*256;*(uint8_t *)entry=scenario==2?0:1;*(uint8_t *)(entry+1)=8;*(uint16_t *)(entry+2)=0x3210;for(unsigned i=0;i<8;i++)*(uint8_t *)(entry+4+i)=i+1;
*(uint32_t *)(buffer+3844)=4;*(uint32_t *)(buffer+3848)=8;
unsigned expected=scenario==0||scenario==6?77:0x12345;assert(opencfw_em9305_radio_callback_32d7f4(r)==expected);assert(calls==(scenario==0||scenario==6?3:1));
if(scenario!=0&&scenario!=6){assert(*(uint16_t *)(r+528)==0x2345);if(scenario==1||scenario==2){assert(*(uint8_t *)(r+689)==3);assert(*(uint32_t *)(buffer+3844)==4&&*(uint32_t *)(buffer+3848)==8);}else{assert(*(uint8_t *)(r+689)==1&&*(uint16_t *)(r+1144)==8&&*(uint16_t *)(r+706)==0x3210);assert(*(uint8_t *)entry==0&&*(uint8_t *)(buffer+3854)==255);for(unsigned i=0;i<8;i++)assert(*(uint8_t *)(uintptr_t)(0x830000+i)==i+1);uint64_t mask=(8ULL<<32)|4ULL;mask|=1ULL<<(index&63);assert(*(uint32_t *)(buffer+3844)==(uint32_t)mask&&*(uint32_t *)(buffer+3848)==(uint32_t)(mask>>32));}}
cases++;}printf("PASS %u\n",cases);}
'''
p=Path(__file__).with_name('radio-callback-host.c');p.write_text(h)
output=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror /work/'+str(p.relative_to(root))+' -o /tmp/test && /tmp/test'],text=True);assert output.strip()=='PASS 7';print(output.strip())
raw=(root/'g2/build/c-firmware/20261011/em-activation-round/em-inspection.bin').read_bytes();assert raw[0x334474-0x302400:0x334479-0x302400]==bytes([5,0,0,0,34])
p.with_name('radio-callback-host-receipt.json').write_text(json.dumps({'cases_passed':7,'template_bytes_verified':5,'scope':'Host fixed-RAM effects, controlled true children, MPYUW normalized: control and fresh-control pointers, absent/empty/payload masks incl 33/65. No native ISA/runtime/hardware qualification.'},indent=2)+'\n')
