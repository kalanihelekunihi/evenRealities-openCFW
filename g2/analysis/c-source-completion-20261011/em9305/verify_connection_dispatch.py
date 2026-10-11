from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];p=root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c'
s=p.read_text();a=s.index('/* Native330440..');body=s[a:s.index('/* Native30e524..',a)]
h=r'''
#include <stdint.h>
#include <assert.h>
#include <string.h>
static uint16_t cmd;static uint8_t input[32],packet[8];static unsigned handled,fail,mutate,update,allocs,sends,begins,events,cancels,fallbacks;
uint32_t opencfw_em9305_dispatch_33052c(uintptr_t r,uintptr_t i){assert(r==(uintptr_t)&cmd&&i==(uintptr_t)input);return handled;}
uint32_t opencfw_em9305_ll_stream_control_decode_332a78(uintptr_t o,uintptr_t i){assert(i==(uintptr_t)(input+13));memcpy((void*)o,(void*)i,12);return 12;}
uint32_t opencfw_em9305_ll_connection_begin_30b480(uintptr_t h,uintptr_t c){uint8_t *p=(uint8_t*)h;assert(*(uint16_t*)p==(uint16_t)(input[0]+((unsigned)input[1]<<8)));assert(*(uint16_t*)(p+2)==(uint16_t)(input[2]+((unsigned)input[3]<<8)));assert(p[4]==input[4]&&p[5]==input[12]&&p[6]==input[5]);assert(*(uint32_t*)(p+8)==(uint32_t)(uintptr_t)(input+6));assert(memcmp((void*)c,input+13,12)==0);begins++;return 0x91;}
uint32_t opencfw_em9305_ll_status_event_331bf8(uintptr_t r,uint32_t status){assert(r==(uintptr_t)&cmd&&status==0x91&&begins==1);events++;return 0;}
void opencfw_em9305_ll_connection_cancel_30b53c(uintptr_t i){assert(i==(uintptr_t)input);cancels++;}
uint32_t opencfw_em9305_ll_connection_update_30cf40(uintptr_t i){assert(i==(uintptr_t)input);update++;if(mutate==1)cmd=0x1234;return 0x91;}
uintptr_t opencfw_em9305_ll_response_allocate_32e428(uint32_t n,uint32_t command){assert(n==1&&command==cmd&&update==1);allocs++;if(mutate==2)cmd=0x1234;return fail?0:(uintptr_t)(packet+5);}
uint32_t opencfw_em9305_ll_event_send(uintptr_t p){assert(p==(uintptr_t)packet);assert(packet[5]==(mutate?0xa5:0x91));sends++;return 0;}
uint32_t opencfw_em9305_dispatch_32ef10(uintptr_t r,uintptr_t i){assert(r==(uintptr_t)&cmd&&i==(uintptr_t)input);fallbacks++;return 63;}
'''+body+r'''
static void reset(uint16_t c){cmd=c;handled=fail=mutate=update=allocs=sends=begins=events=cancels=fallbacks=0;for(unsigned i=0;i<32;i++)input[i]=3+7*i;memset(packet,0xa5,sizeof packet);}
static uint32_t run(void){return opencfw_em9305_dispatch_330440((uintptr_t)&cmd,(uintptr_t)input);}
int main(void){reset(0x200d);handled=1;assert(run()==1&&begins==0);reset(0x200d);assert(run()==1&&begins==1&&events==1);reset(0x200e);assert(run()==1&&cancels==1);reset(0x9999);assert(run()==63&&fallbacks==1);for(unsigned f=0;f<2;f++)for(unsigned m=0;m<3;m++){reset(0x2014);fail=f;mutate=m;assert(run()==1&&update==1&&allocs==1&&sends==!f);}return 0;}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],check=True);subprocess.run([str(d/'test')],check=True)
r={'cases_passed':10,'native_range':'330440..3304f0','scope':'Actual selected C dispatcher with controlled children, native-reading field and callback/reload contracts; not native runtime equality','body_sha256':hashlib.sha256(body.encode()).hexdigest()}
Path(__file__).with_name('connection-dispatch-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS10 controlled connection dispatcher cases')
