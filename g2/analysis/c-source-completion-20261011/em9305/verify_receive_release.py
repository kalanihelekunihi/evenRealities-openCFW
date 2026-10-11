from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native331c20..'):s.index('/* Native331cdc..')]
body=body.replace('*(volatile uint32_t *)(uintptr_t)0x8058c8u','callback_pointer').replace('*(volatile uint8_t *)(uintptr_t)0x80585cu','handler_byte')
for addr,i in [('805718',0),('805719',1),('805700',2)]:body=body.replace('0x'+addr+'u','((uintptr_t)&counters['+str(i)+'])')
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
static uint8_t event_data[4],counters[3],handler_byte;static uintptr_t callback_pointer;static unsigned type,present,mutate,releases,credits,callbacks,posts;
static uint32_t replacement(uint32_t n){assert(n==1&&releases==1);callbacks++;handler_byte=77;return 99;}
static uint32_t original(uint32_t n){assert(n==1&&releases==1&&!mutate);callbacks++;handler_byte=55;return 99;}
uint32_t opencfw_em9305_wsf_event_release(uintptr_t event){assert(event==(uintptr_t)event_data&&posts==0);releases++;handler_byte=33;if(mutate)callback_pointer=(uintptr_t)&replacement;return 99;}
uint32_t opencfw_em9305_ll_primary_credit_308570(uint32_t n){assert(n==1&&releases==1);credits++;handler_byte=88;return 99;}
uint32_t opencfw_em9305_wsf_event_post(uint32_t handler,uint32_t bits){assert(bits==4&&handler==handler_byte);posts++;return 0xcafebabe;}
'''+body+r'''
int main(void){unsigned count=0;unsigned types[]={0,1,2,3,255},codes[]={0,62,255};for(unsigned ti=0;ti<5;ti++){type=types[ti];for(unsigned ci=0;ci<3;ci++){for(unsigned subtype=0;subtype<256;subtype++){for(unsigned initial=0;initial<256;initial++){for(present=0;present<2;present++){for(mutate=0;mutate<2;mutate++){
 event_data[0]=codes[ci];event_data[2]=subtype;for(unsigned i=0;i<3;i++)counters[i]=initial;handler_byte=11;callback_pointer=present?(uintptr_t)&original:0;releases=credits=callbacks=posts=0;
 assert(opencfw_em9305_dispatch_331c20(type,(uintptr_t)event_data)==0xcafebabe&&posts==1&&releases==(type==1||type==2||(type==3&&present))&&credits==(type==1)&&callbacks==(type==3&&present));
 int changed=-1;if(type==2&&codes[ci]==62){if(subtype==2||subtype==11||subtype==13||subtype==15||subtype==34||subtype==37||subtype==40)changed=0;else if(subtype==21||subtype==22)changed=1;else if(subtype==19)changed=2;}for(unsigned i=0;i<3;i++)assert(counters[i]==(uint8_t)(initial-(changed==(int)i)));count++;
}}}}}}printf("%u\n",count);}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'t.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'t.c'),'-o',str(d/'t')],check=True);n=int(subprocess.check_output([str(d/'t')],text=True))
Path(__file__).with_name('receive-release-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C receive-release dispatch normalized product counters/handler/callback. Fullsubtype/counterbytes, types0/1/2/3/255, codes0/62/255, callbackpresent/missing and release swaps callback, wrapping counters, exactrelease/credit/callback/post counts/return. Controlled children; not native runtime equality.','body_sha256':hashlib.sha256(body.encode()).hexdigest()},indent=2)+'\n');print('PASS',n)
