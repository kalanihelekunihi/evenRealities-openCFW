from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Native31ac84..31ace0'):s.index('/* Native317320..317334')].replace('*(volatile uint32_t *)(record+56u+i*4u)','host_stream(i)')
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static _Alignas(4) uint8_t record[512],streams[8][8];static unsigned present,mode,actions,releases,steps,queued,mutate;
static uintptr_t host_stream(unsigned i){assert(i<8&&record[0]==0);return (present&(1u<<i))?(uintptr_t)streams[i]:0;}
uint32_t opencfw_em9305_ll_test_30cb24(uint32_t id,uint32_t mask){assert(mode<2&&mask==(mode==0?2:1)&&id<8);actions++;return 99;}
void opencfw_em9305_radio_stream_release_31ace0(uintptr_t p){assert(p>=(uintptr_t)streams&&p<(uintptr_t)(streams+8));releases++;if(mutate)record[52]=0;}
uint32_t opencfw_em9305_wsf_queue_empty(uintptr_t p){assert(p==(uintptr_t)(record+184)&&mode==1);return queued==0;}
void opencfw_em9305_radio_record_queue_step_317320(uintptr_t p){assert(p==(uintptr_t)record&&queued>0);queued--;steps++;}
'''+b+r'''
int main(void){unsigned n=0;for(unsigned count=0;count<8;count++)for(mode=0;mode<3;mode++)for(present=0;present<256;present++)for(unsigned q=0;q<4;q++)for(mutate=0;mutate<2;mutate++){
 memset(record,0,sizeof record);record[0]=1;record[3]=mode;record[52]=count;for(unsigned i=0;i<8;i++)*(uint16_t *)(streams[i]+2)=i;actions=releases=steps=0;queued=q;
 unsigned expected=0;for(unsigned i=0;i<count;i++)if(present&(1u<<i)){expected++;if(mutate)break;}
 opencfw_em9305_radio_record_release_31ac84((uintptr_t)record);assert(record[0]==0&&releases==expected&&actions==(mode<2?expected:0)&&steps==(mode==1?q:0));n++;}
printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('record-cleanup-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C stream/null masks/mode/count/queue cuts and child-mutated fresh count. 32bit stream pointers/children normalized; no native ISA or hardware proof.'},indent=2)+'\n');print('PASS',n)
