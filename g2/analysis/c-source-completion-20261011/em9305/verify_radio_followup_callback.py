from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Authenticated radio follow-up callback333268'):s.index('/* Authenticated radio status callback333480')]
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static char trace[32];static unsigned n,expected,mutate,request;
static void mark(char c){trace[n++]=c;}
static uint32_t cb(uint32_t status){assert(status==expected);mark('B');return 123;}
static uint32_t cb2(uint32_t status){assert(status==expected);mark('C');return 456;}
uint32_t opencfw_em9305_radio_window_resume_310430(uint32_t a,uint32_t b){assert(a==147&&b==16&&*(uint32_t *)0x805d18==650);mark('W');return 0;}
uint32_t opencfw_em9305_radio_finish_310454(uint32_t a){assert(a==3);mark('F');*(uint32_t *)0x805d18=900;*(uint32_t *)0x805d0c=0x833000;return 0;}
uint32_t opencfw_em9305_radio_configure_3104d8(uint32_t a,uint32_t b){assert(a==4&&b==9);mark('Q');if(mutate)*(uint32_t *)0x805d18=777;return 0;}
uint32_t opencfw_em9305_radio_window_base_310654(uint32_t a){assert(a==150);mark('V');return 0;}
uint32_t opencfw_em9305_radio_setup_310450(uint32_t a){assert(a==44);mark('S');*(uint32_t *)0x805d0c=0x831000;return 0;}
uint32_t opencfw_em9305_radio_timestamp_310474(uint32_t a){assert(a==55);mark('T');*(uint32_t *)0x805d0c=0x832000;return 0;}
uint32_t opencfw_em9305_radio_transform_33322c(uintptr_t a){assert(a==0x833014);mark('X');*(uint16_t *)0x805d24=1;return 0;}
uint32_t opencfw_em9305_radio_request_state_310600(uint32_t a){request=a;mark('R');return 0;}
uint32_t opencfw_em9305_common_activate_310580(uint32_t a){assert(a==0);mark('A');return 0;}
void *opencfw_em9305_memcpy(void *d,const void *s,uint32_t l){assert(d==(void *)0x840000&&s==(void *)0x805d28&&l==4);mark('M');memcpy(d,s,l);*(uint32_t *)0x805cf4=(uint32_t)(uintptr_t)cb2;return d;}
'''+b+r'''
static void reset(unsigned status,unsigned mode,unsigned count,unsigned copy){memset((void *)0x800000,0,0x100000);memset(trace,0,sizeof(trace));n=mutate=request=0;expected=status!=0;*(uint32_t *)0x805cf4=(uint32_t)(uintptr_t)cb;*(uint32_t *)0x805d18=500;*(uint16_t *)0x805d1c=10;*(uint16_t *)0x805d24=count;*(uint8_t *)0x805d04=mode;*(uint8_t *)0x805d26=4;*(uint8_t *)0x805d27=5;*(uint8_t *)0x805d31=9;*(uint32_t *)0x805cfc=100;*(uint32_t *)0x805d08=2000;if(copy){*(uint32_t *)0x805d2c=0x840000;*(uint8_t *)0x805d30=4;*(uint32_t *)0x805d28=0x12345678;}}
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;unsigned counts[]={0,1,65535};for(unsigned status=0;status<4;status++)for(unsigned mode=0;mode<4;mode++)for(unsigned ci=0;ci<3;ci++)for(unsigned copy=0;copy<2;copy++){unsigned count=counts[ci];reset(status,mode,count,copy);assert(opencfw_em9305_radio_callback_333268(status)==(copy?456:123));assert(*(uint16_t *)0x805d24==(uint16_t)(count+1));char want[32]="";if(status==0){if(mode==0)strcat(want,"A");if(mode==1)strcat(want,"W");if(mode==2){strcat(want,count==0?"QR":"R");assert(request==1900);}if(mode==3)strcat(want,"QV");}strcat(want,copy?"MC":"B");assert(strcmp(trace,want)==0);if(copy){assert(*(uint32_t *)0x805d2c==0&&*(uint32_t *)0x840000==0x12345678);}cases++;}
reset(0,2,55,0);mutate=1;*(uint32_t *)0x805d0c=0x830000;*(uint32_t *)(0x830000+4)=44;*(uint32_t *)(0x831000+8)=55;*(uint8_t *)(0x832000+1)=3;assert(opencfw_em9305_radio_callback_333268(0)==123&&strcmp(trace,"STFXQRB")==0&&request==777);cases++;
reset(0,3,0,0);*(uint32_t *)0x805d0c=0x830000;*(uint8_t *)(0x830000+1)=3;assert(opencfw_em9305_radio_callback_333268(0)==123&&strcmp(trace,"FQVB")==0&&*(uint32_t *)0x805d18==1050);cases++;printf("PASS %u\n",cases);}
'''
p=Path(__file__).with_name('radio-followup-callback-host.c');p.write_text(h)
out=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/test && /tmp/test'],text=True)
print(out.strip());p.with_name('radio-followup-callback-host-receipt.json').write_text(json.dumps({'result':out.strip(),'scope':'Selected full callback with controlled child calls; fixed RAM, counter wrap, owner pointer refresh, transform counter mutation, configure time mutation, copy ordering and mandatory callback refresh. No native ARC execution or hardware proof.'},indent=2)+'\n')
