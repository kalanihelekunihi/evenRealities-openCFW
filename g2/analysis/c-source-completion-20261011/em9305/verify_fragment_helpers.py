from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Authenticated fragmented-report helpers'):s.index('/* Authenticated full dispatch331334')]
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned allocation;static unsigned copies;
static uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){assert(n==246);return allocation?0x830000:0;}
static void *opencfw_em9305_memcpy(void *d,const void *s,uint32_t n){copies++;return memcpy(d,s,n);}
'''+b+r'''
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;for(unsigned alloc=0;alloc<2;alloc++)for(unsigned length=0;length<512;length++){allocation=alloc;assert(opencfw_em9305_ll_fragment_allocate_32e48c(0x13e,length)==(alloc?0x830002:0));assert(opencfw_em9305_ll_fragment_allocate_32e4a8(0x23e,length)==(alloc?0x830002:0));if(alloc)assert(*(uint8_t *)0x830000==0x3e&&*(uint8_t *)0x830001==(uint8_t)length);cases++;}
uintptr_t input=0x810000,output=0x820000,data=0x840000;for(unsigned i=0;i<32;i++)*(uint8_t *)(input+i)=i;for(unsigned i=0;i<256;i++)*(uint8_t *)(data+i)=i;
for(unsigned mode=0;mode<256;mode++)for(unsigned bytes=0;bytes<256;bytes++)for(unsigned complete=0;complete<2;complete++){*(uint32_t *)(input+16)=data;*(uint8_t *)(input+13)=complete?bytes:(uint8_t)(bytes+1);*(uint8_t *)(input+12)=mode;copies=0;assert(opencfw_em9305_ll_fragment_format_330f48(output,input,data,bytes)==(bytes?output+11:output));assert(copies==(bytes!=0));uint8_t *out=(uint8_t *)output;assert(out[0]==40&&out[1]==4&&out[2]==5&&out[3]==6&&out[4]==1&&out[5]==8&&out[6]==9&&out[7]==10&&out[8]==11&&out[9]==(complete?(mode==255?255:mode==2?2:0):1)&&out[10]==bytes&&!memcmp(out+11,(void *)data,bytes));cases++;}
printf("PASS %u\n",cases);}
'''
p=Path(__file__).with_name('fragment-helpers-host.c');p.write_text(h)
out=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/test && /tmp/test'],text=True);print(out.strip());p.with_name('fragment-helpers-host-receipt.json').write_text(json.dumps({'result':out.strip(),'scope':'Three actual helper bodies, controlled allocator/memcpy. Allocation cut, low byte length, all mode/length bytes, fragment complete status and exact fields/return. No native target runtime/hardware proof.'},indent=2)+'\n')
