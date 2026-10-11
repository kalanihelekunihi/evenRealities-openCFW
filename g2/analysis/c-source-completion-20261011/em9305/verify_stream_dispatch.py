from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path('/Users/kalani/Repo/evenRealities-openCFW');p=root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c';s=p.read_text();a=s.index('/* Native33052c..330568:');body=s[a:s.index('/* Native 0x332a78..',a)]
h=r'''
#include <stdint.h>
#include <assert.h>
#include <string.h>
static uint16_t command;static uint8_t input[80],packet[16];static uint32_t fail,allocs,sends,decodes,entries,mask,calls;
static uintptr_t controls_base,cursor;
uint32_t opencfw_em9305_ll_mask_command_30cf88(uint32_t id,uintptr_t p){assert(id==0x9876&&p==(uintptr_t)(input+2));calls=1;return 0x91;}
uintptr_t opencfw_em9305_ll_response_allocate_32e428(uint32_t n,uint32_t c){assert(n==1&&c==command&&calls==1);allocs++;return fail?0:(uintptr_t)(packet+5);}
uint32_t opencfw_em9305_ll_event_send(uintptr_t p){assert(p==(uintptr_t)packet&&packet[5]==0x91);sends++;return 0;}
uint32_t opencfw_em9305_dispatch_330440(uintptr_t r,uintptr_t i){assert(r==(uintptr_t)&command&&i==(uintptr_t)input);calls=2;return 63;}
void *opencfw_em9305_memset(void *p,uint32_t v,uint32_t n){assert(v==0&&n==36);controls_base=(uintptr_t)p;return memset(p,v,n);}
uint32_t opencfw_em9305_ll_status_event_331bf8(uintptr_t r,uint32_t s){assert(r==(uintptr_t)&command&&s==0x9c&&calls==3);calls=4;return 0;}
'''+body+r'''
uint32_t opencfw_em9305_ll_stream_control_decode_332a78(uintptr_t o,uintptr_t i){assert(o==controls_base+12*decodes&&i==cursor+4);for(unsigned k=0;k<12;k++){assert(((uint8_t*)o)[k]==0);((uint8_t*)o)[k]=0xa0+decodes;}uint32_t n=decodes%3+1;cursor+=n+4;decodes++;return n;}
uint32_t opencfw_em9305_ll_stream_command_30b7ec(uintptr_t h,uintptr_t p,uintptr_t c){uint8_t *b=(uint8_t*)h;assert(b[0]==input[0]&&b[1]==input[1]&&b[2]==input[2]&&b[8]==mask&&b[9]==255&&b[10]==255);assert(*(uint32_t*)(b+4)==(uint32_t)(uintptr_t)(input+3));assert(c==controls_base&&decodes==entries);uintptr_t at=(uintptr_t)(input+10);for(unsigned j=0;j<entries;j++){uint16_t *pair=(uint16_t*)p;assert(pair[2*j]==(uint16_t)(((uint8_t*)at)[0]|((uint32_t)((uint8_t*)at)[1]<<8)));assert(pair[2*j+1]==(uint16_t)(((uint8_t*)at)[2]|((uint32_t)((uint8_t*)at)[3]<<8)));for(unsigned k=0;k<12;k++)assert(((uint8_t*)c)[12*j+k]==0xa0+j);at+=j%3+5;}for(unsigned j=entries*12;j<36;j++)assert(((uint8_t*)c)[j]==0);calls=3;return 0x9c;}
static void reset(uint16_t c){command=c;for(unsigned i=0;i<80;i++)input[i]=i*7+3;input[0]=0x76;input[1]=0x98;fail=allocs=sends=decodes=entries=calls=0;}
static uint32_t run(void){return opencfw_em9305_dispatch_3305b0((uintptr_t)&command,(uintptr_t)input);}
int main(void){reset(0x1234);assert(run()==63&&calls==2&&allocs==0);for(unsigned f=0;f<2;f++){reset(0xfff8);fail=f;assert(run()==1&&allocs==1&&sends==!f);}
uint8_t masks[]={0,1,2,8,7,255,128,85};for(unsigned m=0;m<8;m++){reset(0x2043);mask=masks[m];input[9]=mask;for(unsigned bit=0;bit<8&&entries<3;bit++)entries+=(mask>>bit)&1;cursor=(uintptr_t)(input+10);assert(run()==1&&calls==4&&allocs==0);}return 0;}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],check=True);subprocess.run([str(d/'test')],check=True)
r={'cases_passed':11,'scope':'Actual selected C dispatch bodies isolated with controlled real lower contracts; checks exact field/cursor/selection/call logic from native reading, not native runtime equality','source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'body_sha256':hashlib.sha256(body.encode()).hexdigest(),'native_ranges':['33052c..330568','3305b0..330664'],'remaining_children':['30c414 mask count','30b7ec stream operation','330440 fallback']}
(root/'g2/analysis/c-source-completion-20261011/em9305/stream-dispatch-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS11 controlled C stream/mask dispatch cases')
