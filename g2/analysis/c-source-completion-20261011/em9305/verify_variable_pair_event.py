from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Native331f5c..332036'):s.index('/* Native3327f4..3328c6')].replace('*(volatile uint8_t *)(uintptr_t)0x8056fbu','mask').replace('*(volatile uint8_t *)(uintptr_t)0x8056efu','enabled')
h=r'''#include <stdint.h>
#include <assert.h>
#include <string.h>
#include <stdio.h>
static _Alignas(8) uint8_t packet[600],output[600],mask,enabled;static unsigned type,count,ok,allocs,sends;
uintptr_t opencfw_em9305_ll_event_allocate(uint32_t code,uint32_t length){assert(code==62&&length==(type==41?(uint8_t)(19+2*count):3));allocs++;packet[4]=91;return ok?(uintptr_t)(output+8):0;}
uint32_t opencfw_em9305_ll_event_send(uintptr_t e){assert(e==(uintptr_t)(output+6));uint8_t *o=output+8;assert(o[0]==(type==41?27:28)&&o[1]==91&&o[2]==packet[5]);if(type==41){for(unsigned i=0;i<2;i++){assert(o[3+3*i]==packet[8+4*i]&&o[4+3*i]==packet[9+4*i]&&o[5+3*i]==packet[10+4*i]);}assert(!memcmp(o+9,packet+16,5)&&!memcmp(o+14,packet+22,5)&&!memcmp(o+19,packet+28,2*count));assert(o[19+2*count]==0xa5);}else assert(o[3]==0xa5);sends++;return 99;}
'''+b+r'''
int main(void){unsigned n=0;for(type=0;type<256;type++)for(unsigned m=0;m<16;m++)for(unsigned en=0;en<2;en++)for(ok=0;ok<2;ok++)for(unsigned c=0;c<4;c++){
 count=c==3?255:c;mask=m;enabled=en?32:0;allocs=sends=0;for(unsigned j=0;j<sizeof packet;j++)packet[j]=(uint8_t)(j*17);packet[2]=type;packet[26]=count;memset(output,0xa5,sizeof output);unsigned valid=(type==41||type==42)&&(mask&(type==41?4:8))&&en;assert(opencfw_em9305_dispatch_331f5c((uintptr_t)packet)==(valid&&ok));assert(allocs==valid&&sends==(valid&&ok));n++;}
printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('variable-pair-event-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C all type bytes, relevant mask combinations, enable/allocator outcomes, pair counts0/1/2/255 including byte length wrap and fresh fields after allocator. Host oversized fixture preserves native writes despite wrapped allocation length; no hardware or ISA execution.'},indent=2)+'\n');print('PASS',n)
