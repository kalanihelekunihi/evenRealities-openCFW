from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text()
body=s[s.index('/* Native32385c..'):s.index('/* Native30853c..')]
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint8_t packet[16],record[400];static unsigned queued,removes,handler,kind,count;
uintptr_t opencfw_em9305_wsf_event_remove(uintptr_t queue,uintptr_t out){assert(queue==(uintptr_t)(record+368));removes++;*(uint8_t*)out=handler;return queued?(uintptr_t)packet:0;}
'''+body+r'''
int main(void){unsigned cases=0;
for(unsigned offset=0;offset<12;offset++)for(unsigned pattern=0;pattern<256;pattern++)for(unsigned tag=0;tag<16;tag++){
 _Alignas(2) uint8_t actual[32],expected[32];for(unsigned i=0;i<32;i++)actual[i]=(uint8_t)(pattern+tag*i);memcpy(expected,actual,32);
 unsigned m=12;uint32_t k=expected[m+2],h=expected[m]|((uint32_t)expected[m+1]<<8);uint32_t upper=((k<<12)|h)>>8;
 expected[offset]=h;expected[offset+1]=upper;expected[offset+2]=expected[m+4];expected[offset+3]=expected[m+5];
 assert(opencfw_em9305_ll_packet_header_32385c((uintptr_t)(actual+offset),(uintptr_t)(actual+m))==4);assert(memcmp(actual,expected,32)==0);cases++;
}
for(queued=0;queued<2;queued++)for(handler=0;handler<256;handler++)for(kind=0;kind<256;kind++)for(count=0;count<256;count++){
 memset(packet,0xa5,16);packet[2]=kind;packet[3]=count;removes=0;
 assert(opencfw_em9305_ll_primary_take_3252dc((uintptr_t)record)==(queued?(uintptr_t)packet:0)&&removes==1);
 if(queued){unsigned k=kind&3;assert(packet[0]==handler&&packet[1]==((k==1?1:k==2?2:3)<<4)&&packet[2]==count&&packet[3]==0);}else assert(packet[0]==0xa5&&packet[1]==0xa5&&packet[2]==kind&&packet[3]==count);
 for(unsigned i=4;i<16;i++)assert(packet[i]==0xa5);cases++;
}
printf("%u\n",cases);}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'t.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'t.c'),'-o',str(d/'t')],check=True);n=int(subprocess.check_output([str(d/'t')],text=True))
Path(__file__).with_name('pending-header-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual header and primary take C bodies. Exhaustive packet kind/count/handler bytes, empty queue, shifted overlapping destination/metadata. Controlled WSF child; not native runtime equality.','body_sha256':hashlib.sha256(body.encode()).hexdigest()},indent=2)+'\n');print('PASS',n)
