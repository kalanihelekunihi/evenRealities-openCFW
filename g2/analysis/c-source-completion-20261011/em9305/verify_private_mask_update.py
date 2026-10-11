from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native30d378..'):s.index('/* Native310230..')]
body=body.replace('uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;','uintptr_t config=(uintptr_t)configuration;').replace('__asm__ volatile("mpyuw %0,%1,912":"=r"(offset):"r"(id));','offset=id*912u;').replace('uintptr_t slots=*(volatile uint32_t *)(uintptr_t)0x805c70u;','uintptr_t slots=(uintptr_t)records;')
h=r"""
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint8_t configuration[40];static _Alignas(4) uint8_t records[5*912];static unsigned active,queries,id;
uint32_t opencfw_em9305_ll_private_mask_apply_308b20(uint32_t,uint32_t,uint32_t,uint32_t);
uint32_t opencfw_em9305_ll_slot_active_30731c(uint32_t x){assert(x==id&&x<3);queries++;return active;}
"""+body+r"""
int main(void){unsigned cases=0;configuration[34]=3;
for(id=0;id<5;id++){for(active=0;active<2;active++){for(unsigned enabled=0;enabled<3;enabled++){for(unsigned i=0;i<67;i++){
 uint32_t low=i<32?1u<<i:i==64?0x000804beu:i==65?0xffffffffu:0;
 uint32_t high=i>=32&&i<64?1u<<(i-32):i==64?0xf8000000u:i==65?0xffffffffu:0;
 uint32_t before_low=0xa59635c7u,before_high=0x7256c98au;
 *(uint32_t *)(records+id*912+4)=before_low;*(uint32_t *)(records+id*912+8)=before_high;
 queries=0;unsigned ok=id<3&&active,forbidden=(low&0xfff7fb41u)||(high&0x07ffffffu);
 assert(opencfw_em9305_ll_private_mask_30d378(id,low,high,enabled)==(!ok?2:forbidden?18:0));
 assert(queries==(id<3));
 uint32_t expected_low=ok&&!forbidden?(enabled?before_low|low:before_low&~low):before_low;
 uint32_t expected_high=ok&&!forbidden?(enabled?before_high|high:before_high&~high):before_high;
 assert(*(uint32_t *)(records+id*912+4)==expected_low&&*(uint32_t *)(records+id*912+8)==expected_high);cases++;
 /* Direct child covers every bit regardless of validator acceptance. */
 assert(opencfw_em9305_ll_private_mask_apply_308b20(id,low,high,enabled)==(enabled?expected_low|low:expected_low&~low));
 assert(*(uint32_t *)(records+id*912+8)==(enabled?expected_high|high:expected_high&~high));cases++;
}}}}printf("%u\n",cases);return 0;}
"""
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',str(d/'test.c'),'-o',str(d/'test')],check=True);cases=int(subprocess.check_output([str(d/'test')],text=True))
r={'cases_passed':cases,'native_ranges':['30d378..30d3c0','308b20..308b48'],'scope':'Actual connected selected C validator and mask update with normalized RAM/MPYUW stride; controlled slot-active; all64 mask-bit boundaries and aggregate masks; native-reading contracts, not native runtime equality','body_sha256':hashlib.sha256(body.encode()).hexdigest()};Path(__file__).with_name('private-mask-update-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(f'PASS{cases} controlled connected private mask cases')
