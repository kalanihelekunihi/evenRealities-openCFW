from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native309910..'):s.index('/* Native309aa4..')]
body=body.replace('__asm__ volatile("mpyuw %0,%1,912":"=r"(offset):"r"(id));','offset=id*912u;').replace('uintptr_t slots=*(volatile uint32_t *)(uintptr_t)0x805c70u;','uintptr_t slots=(uintptr_t)records;').replace('*(volatile uint32_t *)(uintptr_t)0x8052c8u','callback_one').replace('*(volatile uint32_t *)(uintptr_t)0x805170u','callback_two')
h=r"""
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint8_t records[3*912],expected[3*912];static uintptr_t callback_one,callback_two;
static unsigned id,old,updated,selector,mode,flag,notify,enable_one,enable_two,calls_one,calls_two,clamps,classifies,effective;
static uint32_t delta,expected_class;
uint32_t opencfw_em9305_ll_signed_clamp_310230(uint32_t x){assert(x==0x12345678);clamps++;return updated&128?updated|0xffffff00u:updated;}
uint32_t opencfw_em9305_ll_signed_classify_31b374(uint32_t x){uint32_t b=records[id*912+66];assert(x==(b&128?b|0xffffff00u:b));classifies++;return expected_class;}
static uint32_t first(uintptr_t r,uint32_t sel,uint32_t d,uint32_t v,uint32_t zero){assert(r==(uintptr_t)(records+id*912)&&sel==effective&&d==delta&&v==(updated&128?updated|0xffffff00u:updated)&&zero==0);assert(records[id*912+66]==updated);calls_one++;return 0xfafafafa;}
static uint32_t second(uintptr_t r,uint32_t a,uint32_t b,uint32_t sel,uint32_t v,uint32_t cls,uint32_t d){assert(r==(uintptr_t)(records+id*912)&&a==0&&b==0&&sel==2&&v==(updated&128?updated|0xffffff00u:updated)&&cls==expected_class&&d==delta);assert(records[id*912+331+effective]==updated);calls_two++;return 0xabcd;}
"""+body+r"""
int main(void){unsigned cases=0;expected_class=2;
for(id=0;id<3;id++){for(old=0;old<256;old+=17){for(updated=0;updated<256;updated+=17){for(selector=0;selector<5;selector++){for(mode=1;mode<3;mode++){for(flag=0;flag<2;flag++){for(notify=0;notify<2;notify++){for(enable_one=0;enable_one<2;enable_one++){for(enable_two=0;enable_two<2;enable_two++){
 memset(records,0xa5,sizeof records);uint8_t *r=records+id*912;r[66]=old;r[76]=2;r[1]=mode;r[548]=flag?4:0;r[767]=notify;
 memcpy(expected,records,sizeof records);effective=selector?selector:2;calls_one=calls_two=clamps=classifies=0;callback_one=enable_one?(uintptr_t)first:0;callback_two=enable_two?(uintptr_t)second:0;
 uint32_t difference=(updated-old)&255;delta=difference&128?difference|0xffffff00u:difference;
 unsigned changed=old!=updated;
 if(changed){if(effective==2)expected[id*912+66]=updated;expected[id*912+331+effective]=updated;}
 opencfw_em9305_ll_signed_pair_apply_309910(id,0x12345678,selector);
 assert(clamps==1&&calls_one==(changed&&effective==2&&mode==2&&flag&&enable_one)&&calls_two==(changed&&notify&&enable_two)&&classifies==calls_two);
 assert(memcmp(records,expected,sizeof records)==0);cases++;
}}}}}}}}}printf("%u\n",cases);return 0;}
"""
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],check=True);cases=int(subprocess.check_output([str(d/'test')],text=True))
r={'cases_passed':cases,'native_range':'309910..3099c8','scope':'Actual selected C with normalized slot RAM/MPYUW and callback-pointer RAM; controlled clamp/classifier; entire record comparison and callback argument/order contracts; native-reading contracts, not native runtime equality','body_sha256':hashlib.sha256(body.encode()).hexdigest()};Path(__file__).with_name('signed-pair-apply-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(f'PASS{cases} controlled signed pair update cases')
