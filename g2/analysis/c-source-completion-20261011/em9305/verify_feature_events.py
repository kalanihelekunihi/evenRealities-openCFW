from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path('/Users/kalani/Repo/evenRealities-openCFW')
p=root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c'
s=p.read_text();start=s.index('/* Native332394..33248e:');body=s[start:s.index('/* Native30c2e0..30c33a:',start)]
# Bind only the native fixed feature-mask address to host storage.
bound=body.replace('(uintptr_t)0x8056e8u','(uintptr_t)features')
h=r'''
#include <stdint.h>
#include <assert.h>
#include <string.h>
static uint8_t features[17],storage[32],message[32];
static uint32_t event_type,event_size,fail,allocs,sends,fallbacks,fallback_id;
uintptr_t opencfw_em9305_ll_event_allocate(uint32_t t,uint32_t n) {event_type=t;event_size=n;allocs++;return fail?0:(uintptr_t)(storage+2);}
uint32_t opencfw_em9305_ll_event_send(uintptr_t p) {assert(p==(uintptr_t)storage);sends++;return 77;}
void *opencfw_em9305_memcpy(void *d,const void *s,uint32_t n) {return memcpy(d,s,n);}
uint32_t opencfw_em9305_ll_event_fallback_30c2e0(uint32_t id) {fallbacks++;fallback_id=id;return 99;}
'''+bound+r'''
static void reset(uint32_t kind) {memset(features,0,sizeof features);memset(storage,0xcc,sizeof storage);for(unsigned i=0;i<32;i++)message[i]=i+16;message[2]=kind;event_type=event_size=allocs=sends=fallbacks=fail=0;}
static uint32_t run(void) {return opencfw_em9305_dispatch_332394((uintptr_t)message,123);}
int main(void) {
 for(unsigned kind=11;kind<=17;kind++) {reset(kind);assert(run()==0&&sends==0);assert(fallbacks==(kind==13));}
 reset(17);features[10]=128;assert(run()==1&&event_type==87&&event_size==2&&sends==1);assert(storage[2]==message[4]&&storage[3]==message[5]);
 reset(12);features[5]=128;assert(run()==1&&event_type==48&&event_size==3);assert(storage[2]==message[4]&&storage[3]==message[6]&&storage[4]==message[7]);
 reset(11);features[0]=128;assert(run()==1&&event_type==8&&event_size==4);assert(storage[2]==message[4]&&storage[3]==message[6]&&storage[4]==message[7]&&storage[5]==message[8]&&message[9]==25);
 reset(11);features[11]=2;assert(run()==1&&event_type==89&&event_size==5&&message[9]==1&&storage[6]==1);
 reset(13);features[16]=16;features[7]=32;assert(run()==1&&event_type==62&&event_size==13&&fallbacks==0);assert(storage[2]==5&&storage[3]==message[4]&&storage[4]==message[5]);assert(memcmp(storage+5,message+6,8)==0&&storage[13]==message[14]&&storage[14]==message[15]);
 for(unsigned kind=11;kind<=17;kind++) {if(kind!=11&&kind!=12&&kind!=13&&kind!=17)continue;reset(kind);features[0]=features[5]=features[10]=128;features[16]=16;features[7]=32;fail=1;assert(run()==0&&allocs==1&&sends==0&&fallbacks==(kind==13));if(kind==13)assert(fallback_id==((uint32_t)message[4]|((uint32_t)message[5]<<8)));}
 reset(13);features[16]=16;assert(run()==0&&allocs==0&&fallbacks==1);reset(13);features[7]=32;assert(run()==0&&allocs==0&&fallbacks==1);
 return 0;
}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'test.c').write_text(h)
 subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],check=True)
 subprocess.run([str(d/'test')],check=True)
r={'cases_passed':18,'scope':'Actual selected C bodies with host feature-mask address binding and controlled children; source-contract checks, not native runtime comparison','source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'body_sha256':hashlib.sha256(body.encode()).hexdigest(),'native_range':'332394..33248e','remaining_lower':'30c2e0'}
(root/'g2/analysis/c-source-completion-20261011/em9305/feature-events-receipt.json').write_text(json.dumps(r,indent=2)+'\n')
print('PASS18 controlled C contract cases')
