from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Native332038..332192'):s.index('/* Native30e0e4 tail')]
h=r'''#include <stdint.h>
#include <assert.h>
#include <string.h>
#include <stdio.h>
static _Alignas(4) uint8_t input[64];static uint16_t command;static unsigned calls,copies,events,seed;
void *opencfw_em9305_memcpy(void *d,const void *s,unsigned n){assert(n==16&&s==input+(command==0x2068?15:20));copies++;return memcpy(d,s,n);}
static uint32_t inspect(uintptr_t p,unsigned mode){uint8_t *v=(uint8_t *)p;assert(copies==1&&mode==(command==0x2069));assert(!memcmp(v,input,3));assert(*(uint32_t *)(v+4)==((uint32_t)input[3]|((uint32_t)input[4]<<8)|((uint32_t)input[5]<<16)));if(!mode){assert(!memcmp(v+8,input+6,4)&&!memcmp(v+12,input+10,5)&&!memcmp(v+17,input+15,16));}else{assert(!memcmp(v+8,input+20,16)&&!memcmp(v+24,input+6,3)&&!memcmp(v+28,input+9,4)&&!memcmp(v+32,input+13,7));}calls++;return 0x12340000|seed;}
uint32_t opencfw_em9305_command_30b230(uintptr_t p){return inspect(p,0);}
uint32_t opencfw_em9305_command_30b2d8(uintptr_t p){return inspect(p,1);}
uint32_t opencfw_em9305_command_30e0e4(uint32_t a,uint32_t b){assert(a==input[0]&&b==input[1]&&copies==0);calls++;return 0x12340000|seed;}
uint32_t opencfw_em9305_ll_status_event_331bf8(uintptr_t p,uint32_t status){assert(p==(uintptr_t)&command&&calls==1&&status==(0x12340000|seed));events++;return 0;}
'''+b+r'''
int main(void){unsigned n=0;for(unsigned c=0;c<65536;c++)for(seed=0;seed<4;seed++){command=c;for(unsigned i=0;i<64;i++)input[i]=(uint8_t)(i*31+seed*53);calls=copies=events=0;unsigned valid=c>=0x2068&&c<=0x206a;assert(opencfw_em9305_dispatch_332038((uintptr_t)&command,(uintptr_t)input)==valid);assert(calls==valid&&events==valid&&copies==(valid&&c!=0x206a));n++;}
printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('packed-command-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C all16bitcommands/four input patterns, written native struct fields/copies/status forwarding. Does not read uninitialized native padding; real children normalized. ISA/layout/hardware unproved.'},indent=2)+'\n');print('PASS',n)
