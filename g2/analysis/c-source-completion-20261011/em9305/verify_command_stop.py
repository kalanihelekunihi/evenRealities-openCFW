from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();s=s[s.index('/* Native stop30b654'):s.index('/* Native common release304588')]
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned release,aux,mutate;
static uint32_t opencfw_em9305_common_release_304588(uint32_t n){assert(n==3);release++;return 99;}
static uint32_t opencfw_em9305_auxiliary_release_303ecc(void){assert(*(uint8_t *)0x8058dc==3);aux++;if(mutate){*(uint8_t *)0x8058e0=77;*(uint8_t *)0x8058dc=4;}return 98;}
static uint32_t opencfw_em9305_command_count_down_30e48c(void){*(uint8_t *)0x805a79-=1;return 0x805a79;}
static void *opencfw_em9305_memcpy(void *o,const void *i,uint32_t n){assert(n==20);return memcpy(o,i,n);}
static void *opencfw_em9305_memset(void *o,uint32_t v,uint32_t n){assert(v==0&&n==20);return memset(o,v,n);}
'''+s+r'''
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;unsigned counts[]={0,1,255};
for(unsigned state=0;state<6;state++)for(unsigned kind=0;kind<5;kind++)for(unsigned output=0;output<2;output++)for(unsigned ci=0;ci<3;ci++)for(mutate=0;mutate<2;mutate++){*(uint8_t *)0x8058dc=state;*(uint8_t *)0x805995=kind;*(uint8_t *)0x805a78=1;*(uint8_t *)0x805a79=counts[ci];for(unsigned j=0;j<20;j++)*(uint8_t *)(uintptr_t)(0x8058e0+j)=j+1;memset((void *)0x840000,0xa5,24);aux=release=0;unsigned quick=state==1&&kind==3;unsigned valid=state==1||state==2;assert(opencfw_em9305_command_stop_30b654(output?0x840000:0)==(valid?0:12)&&release==quick&&aux==(state==2));assert(*(uint8_t *)0x8058dc==(quick?0:state==2&&mutate?4:valid?3:state));assert(*(uint8_t *)0x805a79==(quick?(uint8_t)(counts[ci]-1):counts[ci])&&*(uint8_t *)0x805a78==(quick?0:1));for(unsigned j=0;j<20;j++){assert(*(uint8_t *)(uintptr_t)(0x8058e0+j)==(valid&&!quick?0:j+1));unsigned expected=output&&valid&&!quick?(state==2&&mutate&&j==0?77:j+1):0xa5;assert(*(uint8_t *)(uintptr_t)(0x840000+j)==expected);}assert(*(uint8_t *)0x840014==0xa5);cases++;}
printf("PASS %u\n",cases);}
''';p=Path(__file__).with_name('command-stop-host.c');p.write_text(h);a=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/s && /tmp/s'],text=True);print(a.strip());p.with_name('command-stop-host-receipt.json').write_text(json.dumps({'result':a.strip(),'scope':'Actual stop C with controlled copy/clear/release children, optional report output, quick-release/counter underflow, unsupported state and child-driven state/report changes. No hardware/runtime proof.'},indent=2)+'\n')
