from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4]
p=root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c'
s=p.read_text();a=s.index('/* Native30b7ec..');body=s[a:s.index('/* Native30e4dc..',a)]
body=body.replace('uintptr_t state=0x805a70u;','uintptr_t state=(uintptr_t)ram;')
body=body.replace('(uintptr_t)0x805a99u','(uintptr_t)(ram+41)')
body=body.replace('(uintptr_t)0x805b18u','(uintptr_t)&test_handler')
body=body.replace('__asm__ volatile("mpyuw %0,%1,12":"=r"(offset):"r"(packed));','offset=packed*12u; /* bounded named ISA child normalized for host */')
h=r'''
#include <stdint.h>
#include <assert.h>
#include <string.h>
static _Alignas(4) uint8_t ram[48],hdr[12],msg[24],ctrl[36];
static uint16_t pairs[6];static uint8_t test_handler=0x39;
static unsigned gate,valid,badcontrol,busy,fail,allocs,sends,checks,configs,ens,dis;
static uintptr_t cps[3],pps[3];
uint32_t opencfw_em9305_ll_stream_gate_30e510(void){return gate;}
uint32_t opencfw_em9305_ll_stream_header_valid_332f04(uintptr_t h){assert(h==(uintptr_t)hdr);return valid;}
uint32_t opencfw_em9305_ll_stream_control_valid_332f00(uintptr_t c){assert(c==(uintptr_t)(ctrl+checks*12));checks++;return badcontrol;}
uint32_t opencfw_em9305_ll_stream_enable_307a48(uint32_t i){ens|=1u<<i;return 0;}
uint32_t opencfw_em9305_ll_stream_disable_307970(uint32_t i){dis|=1u<<i;return 0;}
uint32_t opencfw_em9305_ll_stream_configure_307a28(uint32_t i,uintptr_t p,uintptr_t c){assert(i==configs);pps[i]=p;cps[i]=c;configs++;return 0;}
uint64_t opencfw_em9305_controller_pack_address(uintptr_t a){assert(a==0x12345678);return UINT64_C(0x0000abcd76543210);}
uint32_t opencfw_em9305_ll_stream_address_busy_318200(uint32_t k,uint32_t l,uint32_t h){assert(k==2&&l==0x76543210&&h==0xabcd);return busy;}
uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){assert(n==20);allocs++;return fail?0:(uintptr_t)msg;}
uint32_t opencfw_em9305_wsf_task_message_send(uint32_t t,uintptr_t m){assert(t==test_handler&&m==(uintptr_t)msg);sends++;return 7;}
'''+body+r'''
static void reset(unsigned mask){memset(ram,0,sizeof ram);memset(hdr,0,sizeof hdr);memset(msg,0xaa,sizeof msg);*(uint32_t*)(ram+36)=(1u<<8)|(1u<<11);ram[41]=4;hdr[2]=2;hdr[8]=mask;*(uint32_t*)(hdr+4)=0x12345678;for(unsigned i=0;i<3;i++){pairs[2*i]=8;pairs[2*i+1]=4;}gate=valid=1;badcontrol=busy=fail=allocs=sends=checks=configs=ens=dis=0;}
static uint32_t run(void){return opencfw_em9305_ll_stream_command_30b7ec((uintptr_t)hdr,(uintptr_t)pairs,(uintptr_t)ctrl);}
int main(void){unsigned cases=0;
for(unsigned m=1;m<8;m++)for(unsigned k=0;k<5;k++)for(unsigned f=0;f<2;f++){reset(m);hdr[0]=k;fail=f;assert(run()==0&&configs==3&&allocs==1&&sends==!f);unsigned packed=0;for(unsigned bit=0;bit<3;bit++){assert(cps[bit]==(uintptr_t)(ctrl+((m&(1u<<bit))?packed*12:0)));assert(pps[bit]==((bit!=1&&(m&(1u<<bit)))?(uintptr_t)(pairs+packed*2):0));packed+=(m>>bit)&1;}assert(checks==packed&&ens==(m&5)&&dis==((~m)&5));assert(ram[12]==((m&1)!=0)+((m&4)!=0));if(!f){assert(*(uint16_t*)(msg+2)==265&&*(uint16_t*)(msg+4)==k&&msg[6]==2&&msg[16]==m);assert(*(uint32_t*)(msg+8)==0x76543210&&*(uint32_t*)(msg+12)==0xabcd);assert(msg[0]==0xaa&&msg[7]==0xaa);}cases++;}
reset(0);assert(run()==18&&checks==0);cases++;reset(8);assert(run()==17);cases++;
reset(7);gate=0;assert(run()==12);cases++;reset(7);ram[4]=1;assert(run()==12);cases++;
reset(7);valid=0;assert(run()==18);cases++;reset(7);badcontrol=1;assert(run()==18&&configs==0);cases++;
reset(7);pairs[0]=3;assert(run()==18);cases++;reset(7);pairs[1]=3;assert(run()==18);cases++;
reset(2);pairs[0]=0;pairs[1]=0;assert(run()==0);cases++;
reset(7);ram[41]=0;hdr[0]=2;assert(run()==17);cases++;reset(7);hdr[0]=5;assert(run()==18);cases++;
reset(7);busy=1;assert(run()==11&&configs==3&&allocs==0);cases++;
assert(cases==82);return 0;}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],check=True);subprocess.run([str(d/'test')],check=True)
r={'cases_passed':82,'native_range':'30b7ec..30b974','scope':'Actual selected C command with controlled children, fixed RAM normalized and bounded MPYUW normalized; native-reading contract tests, not native runtime equality','body_sha256':hashlib.sha256(body.encode()).hexdigest()}
Path(__file__).with_name('stream-command-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS82 controlled stream command cases')
