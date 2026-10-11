from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];p=root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c'
s=p.read_text();a=s.index('/* Native30b480..');body=s[a:s.index('/* Native3087a0..',a)]
for old,new in [('(uintptr_t)0x805a94u','(uintptr_t)&test_flags'),('(uintptr_t)0x805b18u','(uintptr_t)&test_handler'),('(uintptr_t)0x805a9fu','(uintptr_t)&test_pending')]:body=body.replace(old,new)
h=r'''
#include <stdint.h>
#include <assert.h>
#include <string.h>
static uint32_t test_flags;static uint8_t test_handler=0x39,test_pending;
static _Alignas(4) uint8_t hdr[12],ctrl[12],msg[40];
static unsigned gate,bad,valid,busy,fail,allocs,sends,expected_size;
uint64_t opencfw_em9305_controller_pack_address(uintptr_t p){assert(p==0x12345678);return UINT64_C(0xabcd76543210);}
uint32_t opencfw_em9305_ll_connection_gate_30e524(void){return gate;}
uint32_t opencfw_em9305_ll_stream_control_valid_332f00(uintptr_t p){assert(p==(uintptr_t)ctrl);return bad;}
uint32_t opencfw_em9305_ll_stream_kind_valid_30e4dc(uint32_t k){assert(k==hdr[5]);return valid;}
uint32_t opencfw_em9305_ll_stream_address_busy_318200(uint32_t k,uint32_t l,uint32_t h){assert(k==hdr[6]&&l==0x76543210&&h==0xabcd);return busy;}
uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){assert(n==expected_size);allocs++;return fail?0:(uintptr_t)msg;}
void *opencfw_em9305_memcpy(void *d,const void *s,uint32_t n){assert(d==msg+4&&s==ctrl&&n==12);return memcpy(d,s,n);}
uint32_t opencfw_em9305_wsf_task_message_send(uint32_t t,uintptr_t m){assert(t==test_handler&&m==(uintptr_t)msg);sends++;return 0;}
'''+body+r'''
static void reset(void){memset(hdr,0,sizeof hdr);memset(msg,0xa5,sizeof msg);for(unsigned i=0;i<12;i++)ctrl[i]=7*i;*(uint16_t*)hdr=8;*(uint16_t*)(hdr+2)=4;hdr[5]=hdr[6]=1;*(uint32_t*)(hdr+8)=0x12345678;test_flags=test_pending=bad=busy=fail=allocs=sends=0;gate=valid=1;expected_size=36;}
static uint32_t run(void){return opencfw_em9305_ll_connection_begin_30b480((uintptr_t)hdr,(uintptr_t)ctrl);}
int main(void){unsigned cases=0;
for(unsigned f=0;f<2;f++)for(unsigned mode=0;mode<3;mode++){reset();fail=f;hdr[4]=mode;assert(run()==0&&allocs==1&&sends==!f);if(!f){assert(*(uint16_t*)(msg+2)==259&&memcmp(msg+4,ctrl,12)==0&&*(uint32_t*)(msg+16)==*(uint32_t*)hdr);assert(*(uint32_t*)(msg+24)==0x76543210&&*(uint32_t*)(msg+28)==0xabcd);assert(msg[21]==1&&msg[22]==mode&&msg[32]==1);assert(msg[0]==0xa5&&msg[1]==0xa5&&msg[20]==0xa5&&msg[23]==0xa5&&msg[33]==0xa5);}cases++;}
reset();gate=0;assert(run()==12&&allocs==0);cases++;reset();*(uint16_t*)hdr=0x4001;assert(run()==18);cases++;reset();*(uint16_t*)hdr=3;assert(run()==18);cases++;reset();*(uint16_t*)(hdr+2)=3;assert(run()==18);cases++;reset();hdr[4]=3;assert(run()==18);cases++;reset();hdr[6]=2;assert(run()==18);cases++;reset();hdr[5]=2;assert(run()==18);cases++;reset();bad=18;assert(run()==18);cases++;reset();valid=0;assert(run()==18);cases++;reset();busy=1;assert(run()==11&&allocs==0);cases++;
reset();test_flags=64;hdr[5]=hdr[6]=3;assert(run()==0);cases++;
for(unsigned f=0;f<2;f++)for(unsigned p=0;p<2;p++){reset();expected_size=4;test_pending=p;fail=f;opencfw_em9305_ll_connection_cancel_30b53c(0x12345678);assert(allocs==1&&sends==!f);if(!f)assert(msg[2]==(p?9:3)&&msg[3]==2&&msg[0]==0xa5&&msg[1]==0xa5);cases++;}
assert(cases==21);return 0;}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],check=True);subprocess.run([str(d/'test')],check=True)
r={'cases_passed':21,'native_ranges':['30b480..30b53c','30b53c..30b570'],'scope':'Actual selected C bodies with controlled children and normalized fixed RAM; bounded native-reading contract tests, not native runtime equality','body_sha256':hashlib.sha256(body.encode()).hexdigest()}
Path(__file__).with_name('connection-begin-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS21 controlled connection begin/cancel cases')
