from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native309aa4..'):s.index('/* Native30d8fc..')]
body=body.replace('__asm__ volatile("mpyuw %0,%1,912":"=r"(offset):"r"(id));','offset=id*912u;').replace('__asm__ volatile("mpywhl %0,0x01010101,%1":"=r"(replicated):"r"(byte));','replicated=byte*0x01010101u;').replace('uintptr_t slots=*(volatile uint32_t *)(uintptr_t)0x805c70u;','uintptr_t slots=(uintptr_t)records;').replace('*(volatile uint32_t *)(uintptr_t)0x8052c8u','callback_one').replace('*(volatile uint32_t *)(uintptr_t)0x805170u','callback_two')
h=r"""
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static _Alignas(4) uint8_t records[3*912],expected[3*912];static uintptr_t callback_one,callback_two;
static unsigned id,old,updated,mode,flag,notify,enable_one,enable_two,calls_one,calls_two,clamps,classifies,stop_after_first;static uint8_t saved[4];
static uint32_t signed_updated,expected_class;
void *opencfw_em9305_memcpy(void *a,const void *b,uint32_t n){assert(n==4&&b==records+id*912+332);return memcpy(a,b,n);}
uint32_t opencfw_em9305_ll_signed_clamp_310230(uint32_t x){assert(x==0x12345678);clamps++;return signed_updated;}
uint32_t opencfw_em9305_ll_signed_classify_31b374(uint32_t x){assert(x==signed_updated);classifies++;return expected_class;}
static uint32_t sign_delta(uint32_t x){x&=255;return x&128?x|0xffffff00u:x;}
static uint32_t first(uintptr_t r,uint32_t sel,uint32_t d,uint32_t v,uint32_t zero){assert(r==(uintptr_t)(records+id*912)&&sel==2&&d==sign_delta(signed_updated-old)&&v==signed_updated&&zero==0);assert(records[id*912+66]==updated);calls_one++;return 0xfafafafa;}
static uint32_t second(uintptr_t r,uint32_t a,uint32_t b,uint32_t sel,uint32_t v,uint32_t cls,uint32_t d){assert(r==(uintptr_t)(records+id*912)&&a==0&&b==0&&sel<4&&saved[sel]!=updated&&v==signed_updated&&cls==expected_class&&d==sign_delta(signed_updated-saved[sel]));for(unsigned i=0;i<4;i++)assert(records[id*912+332+i]==updated);calls_two++;if(stop_after_first)callback_two=0;return 0xabcd;}
"""+body+r"""
int main(void){unsigned cases=0;expected_class=2;
for(id=0;id<3;id++){for(old=0;old<256;old+=17){for(updated=0;updated<256;updated+=17){for(mode=1;mode<3;mode++){for(flag=0;flag<2;flag++){for(notify=0;notify<2;notify++){for(enable_one=0;enable_one<2;enable_one++){for(enable_two=0;enable_two<2;enable_two++){for(stop_after_first=0;stop_after_first<2;stop_after_first++){
 memset(records,0xa5,sizeof records);uint8_t *r=records+id*912;r[66]=old;r[76]=2;r[1]=mode;r[548]=flag?4:0;r[767]=notify;
 for(unsigned i=0;i<4;i++){saved[i]=(uint8_t)(old+i*37);r[332+i]=saved[i];}
 memcpy(expected,records,sizeof records);calls_one=calls_two=clamps=classifies=0;callback_one=enable_one?(uintptr_t)first:0;callback_two=enable_two?(uintptr_t)second:0;signed_updated=updated&128?updated|0xffffff00u:updated;
 expected[id*912+66]=updated;unsigned changes=0;for(unsigned i=0;i<4;i++){expected[id*912+332+i]=updated;if(saved[i]!=updated)changes++;}
 opencfw_em9305_ll_signed_apply_309aa4(id,0x12345678);
 unsigned notifications=notify&&enable_two?(stop_after_first&&changes?1:changes):0;
 assert(clamps==1&&calls_one==(old!=updated&&mode==2&&flag&&enable_one)&&calls_two==notifications&&classifies==notifications);
 assert(memcmp(records,expected,sizeof records)==0);cases++;
}}}}}}}}}printf("%u\n",cases);return 0;}
"""
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],check=True);cases=int(subprocess.check_output([str(d/'test')],text=True))
r={'cases_passed':cases,'native_range':'309aa4..309b74','scope':'Actual selected C with normalized runtime RAM/MPYUW and bounded byte replication for host-only MPYWHL stand-in; controlled clamp/classifier; whole record and dynamic callback removal checked; named DSP operation remains native in target C, no native-runtime or ISA arithmetic equality inferred','body_sha256':hashlib.sha256(body.encode()).hexdigest()};Path(__file__).with_name('signed-default-apply-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(f'PASS{cases} controlled signed default update cases')
