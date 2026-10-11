from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native30d378..'):s.index('/* Native308b20..')]
body=body.replace('uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;','uintptr_t config=(uintptr_t)configuration;')
h=r"""
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
static uint8_t configuration[40];static unsigned active,queries,applies,id,enabled;static uint32_t low,high;
uint32_t opencfw_em9305_ll_slot_active_30731c(uint32_t x){assert(x==id&&x<3);queries++;return active;}
uint32_t opencfw_em9305_ll_private_mask_apply_308b20(uint32_t x,uint32_t a,uint32_t b,uint32_t c){assert(x==id&&a==low&&b==high&&c==enabled);applies++;return 0xdeadbeef;}
"""+body+r"""
int main(void){unsigned cases=0;configuration[34]=3;
for(id=0;id<5;id++){for(active=0;active<2;active++){for(enabled=0;enabled<3;enabled++){for(unsigned i=0;i<67;i++){
 low=i<32?1u<<i:i==64?0x000804beu:i==65?0xffffffffu:0;
 high=i>=32&&i<64?1u<<(i-32):i==64?0xf8000000u:i==65?0xffffffffu:0;
 queries=applies=0;unsigned ok=id<3&&active;
 unsigned forbidden=(low&0xfff7fb41u)||(high&0x07ffffffu);
 assert(opencfw_em9305_ll_private_mask_30d378(id,low,high,enabled)==(!ok?2:forbidden?18:0));
 assert(queries==(id<3)&&applies==(ok&&!forbidden));cases++;
}}}}printf("%u\n",cases);return 0;}
"""
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],check=True);cases=int(subprocess.check_output([str(d/'test')],text=True))
r={'cases_passed':cases,'native_range':'30d378..30d3c0','scope':'Actual selected C with normalized RAM and controlled slot-active/apply; all64 mask-bit boundaries plus aggregate masks; native-reading contract, not native runtime equality','body_sha256':hashlib.sha256(body.encode()).hexdigest()};Path(__file__).with_name('private-mask-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(f'PASS{cases} controlled private mask cases')
