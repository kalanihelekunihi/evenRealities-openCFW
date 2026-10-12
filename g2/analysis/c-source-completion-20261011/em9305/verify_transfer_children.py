from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Native317ac0'):s.index('/* Native31df6c')].replace('*(volatile uint32_t *)(uintptr_t)0x805a94u','fixture_global')
h=r'''#include <stdint.h>
#include <stdio.h>
#include <assert.h>
#include <string.h>
static uint32_t fixture_global;
'''+b+r'''
static unsigned duration(unsigned phy,unsigned size,unsigned limit){unsigned value;if(phy==3){if(limit<2704)limit=2704;value=64*size+976;}else value=phy==2?4*size+60:16*size+56;return value<limit?value:limit;}
int main(void){_Alignas(4) uint8_t slot[600],input[8];unsigned cases=0;for(unsigned n=0;n<65536;n++){memset(slot,0xa5,sizeof slot);uint32_t low=n*0x1234567u,high=n*0x7654321u;*(uint32_t *)(slot+276)=low;*(uint32_t *)(slot+280)=high;assert(opencfw_em9305_radio_channels_317ac0((uintptr_t)slot)==(uint32_t)(uintptr_t)(slot+272));unsigned count=0;uint64_t bits=((uint64_t)high<<32)|low;for(unsigned i=0;i<37;i++)if((bits>>i)&1)assert(slot[284+count++]==i);assert(slot[272]==count&&slot[284+count]==0xa5);cases++;}
for(unsigned n=0;n<65536;n++){memset(slot,0xa5,sizeof slot);fixture_global=0xffff0000|n;assert(opencfw_em9305_radio_phy_tables_31b6cc((uintptr_t)slot)==(uint32_t)(uintptr_t)(slot+557));unsigned mask=(n&256?3:1)+(n&2048?12:0);for(unsigned i=0;i<4;i++)assert(slot[553+i]==127&&slot[332+i]==((mask&(1<<i))?126:127));assert(slot[331]==0xa5&&slot[336]==0xa5&&slot[552]==0xa5&&slot[557]==0xa5);cases++;}
unsigned phys[]={0,1,2,3,255};for(unsigned a=0;a<5;a++)for(unsigned c=0;c<5;c++)for(unsigned n=0;n<65536;n++){slot[76]=phys[a];slot[77]=phys[c];uint16_t values[4]={(uint16_t)n,(uint16_t)(n*17),(uint16_t)(n*31),(uint16_t)(n*7)};memcpy(input,values,8);unsigned expected=(uint16_t)(duration(phys[a],values[2],values[3])+duration(phys[c],values[0],values[1])+150);assert(opencfw_em9305_radio_limit_317b10((uintptr_t)slot,(uintptr_t)input)==expected);cases++;}printf("%u\n",cases);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('transfer-children-host-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Host actual C 37-channel compaction, capability4-entry table writes/extent and PHY min/max arithmetic/wrap. Config RAM mapped fixture; no ARC runtime/layout/hardware proof.'},indent=2)+'\n');print('PASS',n)
